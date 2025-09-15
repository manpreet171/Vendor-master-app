import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

class DatabaseConnector:
    """Database connection and operations class"""
    
    def __init__(self):
        """Initialize database connection using environment variables"""
        # Load .env for local dev; in Streamlit Cloud we'll prefer st.secrets
        load_dotenv()
        
        # Prefer Streamlit secrets if present (support both flat and nested structures)
        secrets = getattr(st, 'secrets', None)
        if secrets:
            if 'DB_SERVER' in secrets:
                # Flat structure
                self.server = secrets.get('DB_SERVER')
                self.database = secrets.get('DB_NAME')
                self.username = secrets.get('DB_USERNAME')
                self.password = secrets.get('DB_PASSWORD')
                self.driver = secrets.get('DB_DRIVER', "{ODBC Driver 17 for SQL Server}")
            elif 'azure_sql' in secrets:
                # Nested structure [azure_sql]
                azure = secrets['azure_sql']
                self.server = azure.get('AZURE_DB_SERVER')
                self.database = azure.get('AZURE_DB_NAME')
                self.username = azure.get('AZURE_DB_USERNAME')
                self.password = azure.get('AZURE_DB_PASSWORD')
                self.driver = azure.get('AZURE_DB_DRIVER', "{ODBC Driver 17 for SQL Server}")
            else:
                secrets = None
        else:
            self.server = os.getenv("DB_SERVER")
            self.database = os.getenv("DB_NAME")
            self.username = os.getenv("DB_USERNAME")
            self.password = os.getenv("DB_PASSWORD")
            self.driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
        
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establish connection to the database"""
        try:
            connection_string = f"DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            return False
    
    def close_connection(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            return False
    
    def fetch_data(self, query, params=None):
        """Execute a query and fetch all results as a list of dictionaries"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            columns = [column[0] for column in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None
    
    # Vendor operations
    def get_all_vendors(self):
        """Get all vendors from the database"""
        query = "SELECT * FROM Vendors ORDER BY vendor_name"
        return self.fetch_data(query)

    def get_incomplete_vendors(self):
        """Get vendors whose details are incomplete (missing contact, email, or phone)."""
        query = (
            "SELECT * FROM Vendors "
            "WHERE ISNULL(contact_name,'') = '' "
            "   OR ISNULL(vendor_email,'') = '' "
            "   OR ISNULL(vendor_phone,'') = '' "
            "ORDER BY vendor_name"
        )
        return self.fetch_data(query)
    
    def get_vendor_by_id(self, vendor_id):
        """Get vendor by ID"""
        query = "SELECT * FROM Vendors WHERE vendor_id = ?"
        result = self.fetch_data(query, [vendor_id])
        return result[0] if result else None
    
    def add_vendor(self, vendor_name, contact_name=None, vendor_email=None, vendor_phone=None):
        """Add a new vendor"""
        # Check if vendor already exists
        check_query = "SELECT vendor_id FROM Vendors WHERE vendor_name = ?"
        existing = self.fetch_data(check_query, [vendor_name])
        if existing:
            return False, "Vendor with this name already exists"
        
        # Insert new vendor
        query = """
            INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
            VALUES (?, ?, ?, ?)
        """
        success = self.execute_query(query, [vendor_name, contact_name, vendor_email, vendor_phone])
        return success, "Vendor added successfully" if success else "Failed to add vendor"
    
    def update_vendor(self, vendor_id, vendor_name, contact_name=None, vendor_email=None, vendor_phone=None):
        """Update an existing vendor"""
        # Check if vendor exists
        check_query = "SELECT vendor_id FROM Vendors WHERE vendor_id = ?"
        existing = self.fetch_data(check_query, [vendor_id])
        if not existing:
            return False, "Vendor not found"
        
        # Check if name is already taken by another vendor
        check_name_query = "SELECT vendor_id FROM Vendors WHERE vendor_name = ? AND vendor_id != ?"
        name_exists = self.fetch_data(check_name_query, [vendor_name, vendor_id])
        if name_exists:
            return False, "Another vendor with this name already exists"
        
        # Update vendor
        query = """
            UPDATE Vendors
            SET vendor_name = ?, contact_name = ?, vendor_email = ?, vendor_phone = ?
            WHERE vendor_id = ?
        """
        success = self.execute_query(query, [vendor_name, contact_name, vendor_email, vendor_phone, vendor_id])
        return success, "Vendor updated successfully" if success else "Failed to update vendor"
    
    def delete_vendor(self, vendor_id):
        """Delete a vendor and all associated mappings"""
        # Check if vendor exists
        check_query = "SELECT vendor_id FROM Vendors WHERE vendor_id = ?"
        existing = self.fetch_data(check_query, [vendor_id])
        if not existing:
            return False, "Vendor not found"
        
        # Check if vendor has mappings
        check_mappings_query = "SELECT COUNT(*) as count FROM ItemVendorMap WHERE vendor_id = ?"
        mappings = self.fetch_data(check_mappings_query, [vendor_id])
        mapping_count = mappings[0]['count'] if mappings else 0
        
        # Delete mappings first
        if mapping_count > 0:
            delete_mappings_query = "DELETE FROM ItemVendorMap WHERE vendor_id = ?"
            self.execute_query(delete_mappings_query, [vendor_id])
        
        # Delete vendor
        query = "DELETE FROM Vendors WHERE vendor_id = ?"
        success = self.execute_query(query, [vendor_id])
        
        message = f"Vendor and {mapping_count} mappings deleted successfully" if success else "Failed to delete vendor"
        return success, message
    
    # Item operations
    def get_all_items(self, source_filter=None, type_filter=None):
        """Get all items with optional filtering"""
        query_parts = ["SELECT * FROM Items"]
        params = []
        
        # Add filters if provided
        where_clauses = []
        if source_filter and source_filter != "All":
            where_clauses.append("source_sheet = ?")
            params.append(source_filter)
        
        if type_filter and type_filter != "All":
            where_clauses.append("item_type = ?")
            params.append(type_filter)
        
        # Combine where clauses if any
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        query_parts.append("ORDER BY item_name")
        query = " ".join(query_parts)
        
        return self.fetch_data(query, params)
    
    def get_item_by_id(self, item_id):
        """Get item by ID"""
        query = "SELECT * FROM Items WHERE item_id = ?"
        result = self.fetch_data(query, [item_id])
        return result[0] if result else None

    def get_incomplete_items(self):
        """Return items with missing required details based on source.
        - BoxHero: missing SKU or Barcode
        - Raw Materials: missing Height or Width or Thickness
        """
        boxhero_query = (
            "SELECT * FROM Items "
            "WHERE source_sheet = 'BoxHero' "
            "AND (ISNULL(sku,'') = '' OR ISNULL(barcode,'') = '') "
            "ORDER BY item_name"
        )
        raw_query = (
            "SELECT * FROM Items "
            "WHERE source_sheet = 'Raw Materials' "
            "AND (height IS NULL OR width IS NULL OR thickness IS NULL) "
            "ORDER BY item_name"
        )
        return {
            'boxhero': self.fetch_data(boxhero_query) or [],
            'raw': self.fetch_data(raw_query) or []
        }
    
    def add_item(self, item_name, item_type, source_sheet, sku=None, barcode=None, 
                 height=None, width=None, thickness=None, cost=None):
        """Add a new item"""
        # Check if item already exists with same attributes
        check_query = """
            SELECT item_id FROM Items
            WHERE item_name = ? AND item_type = ? AND source_sheet = ?
            AND ISNULL(sku, '') = ISNULL(?, '')
            AND ISNULL(barcode, '') = ISNULL(?, '')
            AND ISNULL(height, 0) = ISNULL(?, 0)
            AND ISNULL(width, 0) = ISNULL(?, 0)
            AND ISNULL(thickness, 0) = ISNULL(?, 0)
        """
        existing = self.fetch_data(check_query, [item_name, item_type, source_sheet, 
                                               sku, barcode, height, width, thickness])
        if existing:
            return False, "Item with these attributes already exists"
        
        # Insert new item
        query = """
            INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode, 
                             height, width, thickness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        success = self.execute_query(query, [item_name, item_type, source_sheet, 
                                           sku, barcode, height, width, thickness])
        
        # Get the new item_id
        if success:
            new_item_query = "SELECT @@IDENTITY AS item_id"
            new_item = self.fetch_data(new_item_query)
            item_id = new_item[0]['item_id'] if new_item else None
            return success, item_id
        else:
            return False, "Failed to add item"
    
    def update_item(self, item_id, item_name, item_type, source_sheet, sku=None, barcode=None, 
                   height=None, width=None, thickness=None, cost=None):
        """Update an existing item"""
        # Check if item exists
        check_query = "SELECT item_id FROM Items WHERE item_id = ?"
        existing = self.fetch_data(check_query, [item_id])
        if not existing:
            return False, "Item not found"
        
        # Update item
        query = """
            UPDATE Items
            SET item_name = ?, item_type = ?, source_sheet = ?, sku = ?, barcode = ?,
                height = ?, width = ?, thickness = ?
            WHERE item_id = ?
        """
        success = self.execute_query(query, [item_name, item_type, source_sheet, sku, barcode,
                                           height, width, thickness, item_id])
        return success, "Item updated successfully" if success else "Failed to update item"
    
    def delete_item(self, item_id):
        """Delete an item and all associated mappings"""
        # Check if item exists
        check_query = "SELECT item_id FROM Items WHERE item_id = ?"
        existing = self.fetch_data(check_query, [item_id])
        if not existing:
            return False, "Item not found"
        
        # Check if item has mappings
        check_mappings_query = "SELECT COUNT(*) as count FROM ItemVendorMap WHERE item_id = ?"
        mappings = self.fetch_data(check_mappings_query, [item_id])
        mapping_count = mappings[0]['count'] if mappings else 0
        
        # Delete mappings first
        if mapping_count > 0:
            delete_mappings_query = "DELETE FROM ItemVendorMap WHERE item_id = ?"
            self.execute_query(delete_mappings_query, [item_id])
        
        # Delete item
        query = "DELETE FROM Items WHERE item_id = ?"
        success = self.execute_query(query, [item_id])
        
        message = f"Item and {mapping_count} mappings deleted successfully" if success else "Failed to delete item"
        return success, message
    
    # Mapping operations
    def get_item_vendors(self, item_id):
        """Get all vendors for a specific item"""
        query = """
            SELECT v.vendor_id, v.vendor_name, v.contact_name, v.vendor_email, v.vendor_phone, m.cost, m.map_id
            FROM Vendors v
            JOIN ItemVendorMap m ON v.vendor_id = m.vendor_id
            WHERE m.item_id = ?
            ORDER BY v.vendor_name
        """
        return self.fetch_data(query, [item_id])
    
    def get_vendor_items(self, vendor_id):
        """Get all items for a specific vendor"""
        query = """
            SELECT i.item_id, i.item_name, i.item_type, i.source_sheet, i.sku, i.barcode,
                   i.height, i.width, i.thickness, m.cost as vendor_cost, m.map_id
            FROM Items i
            JOIN ItemVendorMap m ON i.item_id = m.item_id
            WHERE m.vendor_id = ?
            ORDER BY i.item_name
        """
        return self.fetch_data(query, [vendor_id])
    
    def add_mapping(self, item_id, vendor_id, cost=None):
        """Add a new item-vendor mapping"""
        # Check if mapping already exists
        check_query = "SELECT map_id FROM ItemVendorMap WHERE item_id = ? AND vendor_id = ?"
        existing = self.fetch_data(check_query, [item_id, vendor_id])
        if existing:
            return False, "This mapping already exists"
        
        # Insert new mapping
        query = "INSERT INTO ItemVendorMap (item_id, vendor_id, cost) VALUES (?, ?, ?)"
        success = self.execute_query(query, [item_id, vendor_id, cost])
        return success, "Mapping added successfully" if success else "Failed to add mapping"
    
    def update_mapping(self, map_id, cost):
        """Update an existing mapping's cost"""
        # Check if mapping exists
        check_query = "SELECT map_id FROM ItemVendorMap WHERE map_id = ?"
        existing = self.fetch_data(check_query, [map_id])
        if not existing:
            return False, "Mapping not found"
        
        # Update mapping
        query = "UPDATE ItemVendorMap SET cost = ? WHERE map_id = ?"
        success = self.execute_query(query, [cost, map_id])
        return success, "Mapping updated successfully" if success else "Failed to update mapping"
    
    def delete_mapping(self, map_id):
        """Delete an item-vendor mapping"""
        # Check if mapping exists
        check_query = "SELECT map_id FROM ItemVendorMap WHERE map_id = ?"
        existing = self.fetch_data(check_query, [map_id])
        if not existing:
            return False, "Mapping not found"
        
        # Delete mapping
        query = "DELETE FROM ItemVendorMap WHERE map_id = ?"
        success = self.execute_query(query, [map_id])
        return success, "Mapping deleted successfully" if success else "Failed to delete mapping"
    
    # Data validation operations
    def validate_item_vendor_mappings(self):
        """Validate item-vendor mappings and return statistics"""
        results = {}
        
        # Get summary counts
        summary_query = """
            SELECT 
                (SELECT COUNT(*) FROM Items) as total_items,
                (SELECT COUNT(*) FROM Vendors) as total_vendors,
                (SELECT COUNT(*) FROM ItemVendorMap) as total_mappings,
                (SELECT COUNT(DISTINCT item_id) FROM ItemVendorMap) as mapped_items,
                (SELECT COUNT(DISTINCT vendor_id) FROM ItemVendorMap) as active_vendors
        """
        summary = self.fetch_data(summary_query)
        results['summary_counts'] = summary
        
        # Get unmapped items
        unmapped_query = """
            SELECT i.item_id, i.item_name, i.item_type, i.source_sheet
            FROM Items i
            LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
            WHERE m.map_id IS NULL
            ORDER BY i.item_name
        """
        results['unmapped_items'] = self.fetch_data(unmapped_query)
        
        # Get duplicate mappings
        duplicate_query = """
            SELECT i.item_name, v.vendor_name, COUNT(*) as mapping_count
            FROM ItemVendorMap m
            JOIN Items i ON m.item_id = i.item_id
            JOIN Vendors v ON m.vendor_id = v.vendor_id
            GROUP BY i.item_name, v.vendor_name
            HAVING COUNT(*) > 1
        """
        results['duplicate_mappings'] = self.fetch_data(duplicate_query)
        
        # Get vendor counts per item
        vendor_counts_query = """
            SELECT i.item_id, i.item_name, COUNT(DISTINCT m.vendor_id) as vendor_count
            FROM Items i
            JOIN ItemVendorMap m ON i.item_id = m.item_id
            GROUP BY i.item_id, i.item_name
        """
        vendor_counts = self.fetch_data(vendor_counts_query)
        
        # Categorize items by vendor count
        single_vendor_items = [item for item in vendor_counts if item['vendor_count'] == 1]
        multi_vendor_items = [item for item in vendor_counts if item['vendor_count'] > 1]
        
        results['single_vendor_items'] = len(single_vendor_items)
        results['multi_vendor_items'] = len(multi_vendor_items)
        
        # Get examples of multi-vendor items
        if multi_vendor_items:
            multi_vendor_examples = []
            for i in range(min(5, len(multi_vendor_items))):
                item = multi_vendor_items[i]
                vendors_query = """
                    SELECT v.vendor_name, m.cost
                    FROM ItemVendorMap m
                    JOIN Vendors v ON m.vendor_id = v.vendor_id
                    WHERE m.item_id = ?
                    ORDER BY v.vendor_name
                """
                vendors = self.fetch_data(vendors_query, [item['item_id']])
                multi_vendor_examples.append({
                    'item_name': item['item_name'],
                    'vendor_count': item['vendor_count'],
                    'vendors': vendors
                })
            
            results['multi_vendor_examples'] = multi_vendor_examples
        
        return results
