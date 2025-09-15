import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConnector:
    """
    A class to handle database connections and operations for the SDGNY Vendor Management System.
    """
    
    def __init__(self):
        """Initialize the database connection using environment variables."""
        try:
            server = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
            database = os.getenv("DB_NAME", "sdgny_vendor_management")
            username = os.getenv("DB_USER", "")
            password = os.getenv("DB_PASSWORD", "")
            driver = os.getenv("DB_DRIVER", "SQL Server")
            
            # Create connection string for Azure SQL Database
            conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Connection Timeout=30;'
            
            self.connection = pyodbc.connect(conn_str)
            self.cursor = self.connection.cursor()
            print("Successfully connected to the database")
        except pyodbc.Error as e:
            print(f"Error connecting to SQL Server database: {e}")
            self.connection = None
            self.cursor = None
    
    def close_connection(self):
        """Close the database connection."""
        if hasattr(self, 'connection') and self.connection:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            self.connection.close()
            print("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return the result."""
        try:
            if self.connection is None:
                print("Not connected to database")
                return False
            
            self.cursor.execute(query, params or [])
            self.connection.commit()
            return True
        except pyodbc.Error as e:
            error_message = f"Error executing query: {e}"
            print(error_message)
            # Print the query and parameters for debugging
            print(f"Query: {query}")
            print(f"Parameters: {params}")
            return False
    
    def fetch_data(self, query, params=None):
        """Execute a SELECT query and return the results."""
        try:
            if self.connection is None:
                print("Not connected to database")
                return None
            
            self.cursor.execute(query, params or [])
            columns = [column[0] for column in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except pyodbc.Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    # Vendor operations
    def add_vendor(self, vendor_name, contact_name=None, vendor_email=None, vendor_phone=None):
        """Add a new vendor to the database."""
        query = """
        INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (vendor_name, contact_name, vendor_email, vendor_phone))
    
    def get_all_vendors(self):
        """Get all vendors from the database."""
        query = "SELECT * FROM Vendors ORDER BY vendor_name"
        return self.fetch_data(query)
    
    def get_vendor_by_id(self, vendor_id):
        """Get a vendor by ID."""
        query = "SELECT * FROM Vendors WHERE vendor_id = ?"
        result = self.fetch_data(query, [vendor_id])
        return result[0] if result else None
    
    def update_vendor(self, vendor_id, vendor_name=None, contact_name=None, vendor_email=None, vendor_phone=None):
        """Update vendor information."""
        # Build the SET clause dynamically based on provided values
        set_clauses = []
        params = []
        
        if vendor_name is not None:
            set_clauses.append("vendor_name = ?")
            params.append(vendor_name)
        
        if contact_name is not None:
            set_clauses.append("contact_name = ?")
            params.append(contact_name)
        
        if vendor_email is not None:
            set_clauses.append("vendor_email = ?")
            params.append(vendor_email)
        
        if vendor_phone is not None:
            set_clauses.append("vendor_phone = ?")
            params.append(vendor_phone)
        
        if not set_clauses:
            print("No fields to update")
            return False
        
        query = f"UPDATE Vendors SET {', '.join(set_clauses)} WHERE vendor_id = ?"
        params.append(vendor_id)
        
        return self.execute_query(query, params)
        
    def get_vendors_for_item(self, item_name):
        """Get all vendors that supply a specific item."""
        query = """
        SELECT v.vendor_id, v.vendor_name, v.contact_name, v.vendor_email, v.vendor_phone, m.cost
        FROM Vendors v
        JOIN ItemVendorMap m ON v.vendor_id = m.vendor_id
        JOIN Items i ON m.item_id = i.item_id
        WHERE i.item_name = ?
        ORDER BY m.cost ASC
        """
        return self.fetch_data(query, [item_name])
        
    def get_cheapest_vendor_for_item(self, item_name):
        """Get the cheapest vendor for a specific item."""
        vendors = self.get_vendors_for_item(item_name)
        if vendors:
            return vendors[0]  # First vendor is the cheapest due to ORDER BY cost ASC
        return None
        
    def get_items_by_vendor(self, vendor_name):
        """Get all items supplied by a specific vendor."""
        query = """
        SELECT i.item_id, i.item_name, i.item_type, i.source_sheet, i.sku, i.barcode, m.cost
        FROM Items i
        JOIN ItemVendorMap m ON i.item_id = m.item_id
        JOIN Vendors v ON m.vendor_id = v.vendor_id
        WHERE v.vendor_name = ?
        ORDER BY i.item_type, i.item_name
        """
        return self.fetch_data(query, [vendor_name])
        
    # Data validation functions
    def validate_item_vendor_mappings(self):
        """Validate item-vendor mappings and return any issues found."""
        results = {}
        
        # Check for items without any vendor mappings
        query = """
        SELECT i.item_id, i.item_name, i.item_type
        FROM Items i
        LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
        WHERE m.map_id IS NULL
        """
        unmapped_items = self.fetch_data(query)
        results['unmapped_items'] = unmapped_items
        
        # Check for duplicate mappings
        query = """
        SELECT item_id, vendor_id, COUNT(*) as duplicate_count
        FROM ItemVendorMap
        GROUP BY item_id, vendor_id
        HAVING COUNT(*) > 1
        """
        duplicate_mappings = self.fetch_data(query)
        results['duplicate_mappings'] = duplicate_mappings
        
        # Get summary counts
        query = """
        SELECT 'Items' as table_name, COUNT(*) as record_count FROM Items
        UNION
        SELECT 'Vendors' as table_name, COUNT(*) as record_count FROM Vendors
        UNION
        SELECT 'ItemVendorMap' as table_name, COUNT(*) as record_count FROM ItemVendorMap
        """
        summary_counts = self.fetch_data(query)
        results['summary_counts'] = summary_counts
        
        return results
        
    def compare_excel_with_db(self, excel_vendors, excel_items, excel_mappings):
        """Compare Excel data with database records."""
        results = {}
        
        # Get counts from database
        db_vendors_count = len(self.get_all_vendors())
        
        query = "SELECT COUNT(*) as count FROM Items"
        db_items_count = self.fetch_data(query)[0]['count']
        
        query = "SELECT COUNT(*) as count FROM ItemVendorMap"
        db_mappings_count = self.fetch_data(query)[0]['count']
        
        # Compare counts
        results['vendors'] = {
            'excel_count': len(excel_vendors),
            'db_count': db_vendors_count,
            'match': len(excel_vendors) == db_vendors_count
        }
        
        results['items'] = {
            'excel_count': len(excel_items),
            'db_count': db_items_count,
            'match': len(excel_items) == db_items_count
        }
        
        results['mappings'] = {
            'excel_count': len(excel_mappings),
            'db_count': db_mappings_count,
            'match': len(excel_mappings) == db_mappings_count
        }
        
        return results
    
    def delete_vendor(self, vendor_id):
        """Delete a vendor by ID."""
        query = "DELETE FROM Vendors WHERE vendor_id = ?"
        return self.execute_query(query, [vendor_id])
    
    # Item operations
    def add_item(self, item_name, item_type, source_sheet, sku=None, barcode=None, 
                 height=None, width=None, thickness=None):
        """Add a new item to the database."""
        query = """
        INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, [item_name, item_type, source_sheet, sku, barcode, 
                                         height, width, thickness])
    
    def get_all_items(self):
        """Get all items from the database."""
        query = "SELECT * FROM Items ORDER BY item_name"
        return self.fetch_data(query)
    
    def get_item_by_id(self, item_id):
        """Get an item by ID."""
        query = "SELECT * FROM Items WHERE item_id = ?"
        result = self.fetch_data(query, [item_id])
        return result[0] if result else None
    
    def update_item(self, item_id, item_name=None, item_type=None, source_sheet=None, 
                   sku=None, barcode=None, height=None, width=None, thickness=None):
        """Update item information."""
        # Get current item data
        current_item = self.get_item_by_id(item_id)
        if not current_item:
            return False
        
        # Use current values if new ones aren't provided
        item_name = item_name or current_item['item_name']
        item_type = item_type or current_item['item_type']
        source_sheet = source_sheet or current_item['source_sheet']
        sku = sku if sku is not None else current_item['sku']
        barcode = barcode if barcode is not None else current_item['barcode']
        height = height if height is not None else current_item['height']
        width = width if width is not None else current_item['width']
        thickness = thickness if thickness is not None else current_item['thickness']
        
        query = """
        UPDATE Items 
        SET item_name = ?, item_type = ?, source_sheet = ?, sku = ?, 
            barcode = ?, height = ?, width = ?, thickness = ?
        WHERE item_id = ?
        """
        return self.execute_query(query, [item_name, item_type, source_sheet, sku, 
                                         barcode, height, width, thickness, item_id])
    
    def delete_item(self, item_id):
        """Delete an item by ID."""
        query = "DELETE FROM Items WHERE item_id = ?"
        return self.execute_query(query, [item_id])
    
    # ItemVendorMap operations
    def link_item_to_vendor(self, item_id, vendor_id, cost=None):
        """Link an item to a vendor with an optional cost."""
        query = """
        INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
        VALUES (?, ?, ?)
        """
        return self.execute_query(query, [item_id, vendor_id, cost])
    
    def get_vendors_for_item(self, item_id):
        """Get all vendors that supply a specific item."""
        query = """
        SELECT v.*, ivm.cost 
        FROM Vendors v
        JOIN ItemVendorMap ivm ON v.vendor_id = ivm.vendor_id
        WHERE ivm.item_id = ?
        ORDER BY v.vendor_name
        """
        return self.fetch_data(query, [item_id])
    
    def get_items_for_vendor(self, vendor_id):
        """Get all items supplied by a specific vendor."""
        query = """
        SELECT i.*, ivm.cost 
        FROM Items i
        JOIN ItemVendorMap ivm ON i.item_id = ivm.item_id
        WHERE ivm.vendor_id = ?
        ORDER BY i.item_name
        """
        return self.fetch_data(query, [vendor_id])
    
    def update_item_vendor_cost(self, item_id, vendor_id, cost):
        """Update the cost of an item from a specific vendor."""
        query = """
        UPDATE ItemVendorMap 
        SET cost = ?
        WHERE item_id = ? AND vendor_id = ?
        """
        return self.execute_query(query, [cost, item_id, vendor_id])
    
    def remove_item_vendor_link(self, item_id, vendor_id):
        """Remove the link between an item and a vendor."""
        query = """
        DELETE FROM ItemVendorMap 
        WHERE item_id = ? AND vendor_id = ?
        """
        return self.execute_query(query, [item_id, vendor_id])


# Example usage
if __name__ == "__main__":
    db = DatabaseConnector()
    
    # Example: Add a vendor
    # db.add_vendor("ABC Supplies", "John Doe", "john@abcsupplies.com", "555-1234")
    
    # Example: Get all vendors
    # vendors = db.get_all_vendors()
    # for vendor in vendors:
    #     print(vendor)
    
    db.close_connection()
