import pandas as pd
import os
from dotenv import load_dotenv
import pyodbc
import numpy as np

# Load environment variables
load_dotenv()

def get_connection():
    """Create a connection to the database"""
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "SQL Server")
    
    conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Connection Timeout=30;'
    return pyodbc.connect(conn_str)

def clean_data(df):
    """Clean dataframe by handling NaN values and type conversions"""
    # Replace NaN with None for string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].where(pd.notna(df[col]), None)
    
    # Handle numeric columns
    if 'Cost' in df.columns:
        df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
        df['Cost'] = df['Cost'].fillna(0)
    
    if 'Height' in df.columns:
        df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
    
    if 'Width' in df.columns:
        df['Width'] = pd.to_numeric(df['Width'], errors='coerce')
    
    if 'Thickness' in df.columns:
        df['Thickness'] = pd.to_numeric(df['Thickness'], errors='coerce')
    
    return df

def reset_tables(conn):
    """Reset tables for fresh import"""
    cursor = conn.cursor()
    
    # Ask for confirmation
    confirm = input("This will delete all existing data. Type 'YES' to confirm: ")
    if confirm != "YES":
        print("Operation cancelled.")
        return False
    
    try:
        # Disable foreign key constraints
        cursor.execute("ALTER TABLE ItemVendorMap NOCHECK CONSTRAINT ALL")
        
        # Clear tables
        cursor.execute("DELETE FROM ItemVendorMap")
        cursor.execute("DELETE FROM Items")
        cursor.execute("DELETE FROM Vendors")
        
        # Reset identity columns if they exist
        cursor.execute("DBCC CHECKIDENT ('ItemVendorMap', RESEED, 0)")
        
        # Re-enable constraints
        cursor.execute("ALTER TABLE ItemVendorMap CHECK CONSTRAINT ALL")
        
        conn.commit()
        print("Tables reset successfully.")
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error resetting tables: {e}")
        return False

def import_vendors(excel_path, conn):
    """Import vendors from Excel"""
    print("\n--- IMPORTING VENDORS ---")
    
    try:
        # Read vendor data
        vendors_df = pd.read_excel(excel_path, sheet_name='Final_Vendor_List')
        vendors_df = clean_data(vendors_df)
        
        cursor = conn.cursor()
        vendor_count = 0
        
        # Get the next available vendor_id
        cursor.execute("SELECT ISNULL(MAX(vendor_id), 0) FROM Vendors")
        next_id = cursor.fetchone()[0] + 1
        
        # Process each vendor
        for _, row in vendors_df.iterrows():
            vendor_name = row.get('Vendor')
            contact_name = row.get('Contact Name')
            vendor_email = row.get('Vendor Email')
            vendor_phone = row.get('Vendor Phone')
            
            # Skip rows with no vendor name
            if not vendor_name:
                continue
            
            # Check if vendor already exists
            cursor.execute("SELECT vendor_id FROM Vendors WHERE vendor_name = ?", vendor_name)
            existing = cursor.fetchone()
            
            if existing:
                print(f"Vendor already exists: {vendor_name}")
                continue
            
            # Add vendor
            try:
                cursor.execute("""
                    INSERT INTO Vendors (vendor_id, vendor_name, contact_name, vendor_email, vendor_phone)
                    VALUES (?, ?, ?, ?, ?)
                """, next_id, vendor_name, contact_name, vendor_email, vendor_phone)
                
                next_id += 1
                vendor_count += 1
                print(f"Added vendor: {vendor_name}")
            
            except Exception as e:
                print(f"Error adding vendor {vendor_name}: {e}")
        
        conn.commit()
        print(f"\nSuccessfully imported {vendor_count} vendors.")
        return vendor_count
    
    except Exception as e:
        conn.rollback()
        print(f"Error importing vendors: {e}")
        return 0

def import_items(excel_path, sheet_name, source_sheet, conn):
    """Import items from Excel"""
    print(f"\n--- IMPORTING {source_sheet} ITEMS ---")
    
    try:
        # Read item data
        items_df = pd.read_excel(excel_path, sheet_name=sheet_name)
        items_df = clean_data(items_df)
        
        cursor = conn.cursor()
        item_count = 0
        
        # Get the next available item_id
        cursor.execute("SELECT ISNULL(MAX(item_id), 0) FROM Items")
        next_id = cursor.fetchone()[0] + 1
        
        # Create a dictionary to store item IDs
        item_ids = {}
        
        # First pass: Add all unique items
        for _, row in items_df.iterrows():
            item_name = row.get('Item Name')
            item_type = row.get('Item Type')
            
            # Skip rows with no item name
            if not item_name:
                continue
            
            # Create a unique key for this item
            item_key = f"{item_name}|{item_type}|{source_sheet}"
            
            # Skip if we've already processed this item
            if item_key in item_ids:
                continue
            
            # Prepare item attributes
            if source_sheet == 'BoxHero':
                sku = row.get('SKU')
                barcode = row.get('Barcode')
                height, width, thickness = None, None, None
            else:  # Raw Materials
                sku, barcode = None, None
                height = row.get('Height')
                width = row.get('Width')
                thickness = row.get('Thickness')
            
            # Check if item already exists
            cursor.execute("""
                SELECT item_id FROM Items 
                WHERE item_name = ? AND item_type = ? AND source_sheet = ?
                AND ISNULL(sku, '') = ISNULL(?, '')
                AND ISNULL(barcode, '') = ISNULL(?, '')
                AND ISNULL(height, 0) = ISNULL(?, 0)
                AND ISNULL(width, 0) = ISNULL(?, 0)
                AND ISNULL(thickness, 0) = ISNULL(?, 0)
            """, item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
            
            existing = cursor.fetchone()
            
            if existing:
                print(f"Item already exists: {item_name}")
                item_ids[item_key] = existing[0]
                continue
            
            # Add item
            try:
                cursor.execute("""
                    INSERT INTO Items (item_id, item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, next_id, item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
                
                item_ids[item_key] = next_id
                next_id += 1
                item_count += 1
                print(f"Added item: {item_name}")
            
            except Exception as e:
                print(f"Error adding item {item_name}: {e}")
        
        conn.commit()
        print(f"\nSuccessfully imported {item_count} {source_sheet} items.")
        
        # Return the item IDs dictionary for mapping
        return item_ids
    
    except Exception as e:
        conn.rollback()
        print(f"Error importing {source_sheet} items: {e}")
        return {}

def create_vendor_mappings(excel_path, sheet_name, source_sheet, item_ids, conn):
    """Create item-vendor mappings"""
    print(f"\n--- CREATING {source_sheet} ITEM-VENDOR MAPPINGS ---")
    
    try:
        # Read item data again
        items_df = pd.read_excel(excel_path, sheet_name=sheet_name)
        items_df = clean_data(items_df)
        
        cursor = conn.cursor()
        mapping_count = 0
        
        # Get all vendors
        cursor.execute("SELECT vendor_id, vendor_name FROM Vendors")
        vendors = {row.vendor_name: row.vendor_id for row in cursor.fetchall()}
        
        # Process each row to create mappings
        for _, row in items_df.iterrows():
            item_name = row.get('Item Name')
            item_type = row.get('Item Type')
            vendor_name = row.get('Vendor')
            cost = row.get('Cost')
            
            # Skip rows with missing data
            if not item_name or not vendor_name:
                continue
            
            # Get the item ID
            item_key = f"{item_name}|{item_type}|{source_sheet}"
            item_id = item_ids.get(item_key)
            
            # Get the vendor ID
            vendor_id = vendors.get(vendor_name)
            
            # Skip if we can't find either ID
            if not item_id:
                print(f"Warning: Item not found: {item_name}")
                continue
            
            if not vendor_id:
                print(f"Warning: Vendor not found: {vendor_name}")
                continue
            
            # Check if mapping already exists
            cursor.execute("""
                SELECT map_id FROM ItemVendorMap
                WHERE item_id = ? AND vendor_id = ?
            """, item_id, vendor_id)
            
            existing = cursor.fetchone()
            
            if existing:
                print(f"Mapping already exists: {item_name} -> {vendor_name}")
                continue
            
            # Create mapping
            try:
                cursor.execute("""
                    INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
                    VALUES (?, ?, ?)
                """, item_id, vendor_id, cost)
                
                mapping_count += 1
                print(f"Created mapping: {item_name} -> {vendor_name} (${cost})")
            
            except Exception as e:
                print(f"Error creating mapping {item_name} -> {vendor_name}: {e}")
        
        conn.commit()
        print(f"\nSuccessfully created {mapping_count} {source_sheet} item-vendor mappings.")
        return mapping_count
    
    except Exception as e:
        conn.rollback()
        print(f"Error creating {source_sheet} mappings: {e}")
        return 0

def validate_data(conn):
    """Validate imported data"""
    print("\n--- VALIDATING DATA ---")
    
    cursor = conn.cursor()
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM Vendors")
    vendor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ItemVendorMap")
    mapping_count = cursor.fetchone()[0]
    
    print(f"Total vendors: {vendor_count}")
    print(f"Total items: {item_count}")
    print(f"Total mappings: {mapping_count}")
    
    # Check for items without mappings
    cursor.execute("""
        SELECT COUNT(*) FROM Items i
        LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
        WHERE m.map_id IS NULL
    """)
    unmapped_count = cursor.fetchone()[0]
    print(f"Items without vendor mappings: {unmapped_count}")
    
    # Check for multi-vendor items
    cursor.execute("""
        SELECT i.item_name, COUNT(DISTINCT m.vendor_id) as vendor_count
        FROM Items i
        JOIN ItemVendorMap m ON i.item_id = m.item_id
        GROUP BY i.item_name
        HAVING COUNT(DISTINCT m.vendor_id) > 1
        ORDER BY vendor_count DESC
    """)
    
    multi_vendor_items = cursor.fetchall()
    print(f"\nItems with multiple vendors: {len(multi_vendor_items)}")
    
    # Show some examples
    for i, row in enumerate(multi_vendor_items[:5]):
        print(f"\n{i+1}. {row.item_name} ({row.vendor_count} vendors):")
        
        cursor.execute("""
            SELECT v.vendor_name, m.cost
            FROM ItemVendorMap m
            JOIN Vendors v ON m.vendor_id = v.vendor_id
            JOIN Items i ON m.item_id = i.item_id
            WHERE i.item_name = ?
            ORDER BY v.vendor_name
        """, row.item_name)
        
        vendors = cursor.fetchall()
        for vendor in vendors:
            print(f"   - {vendor.vendor_name}: ${vendor.cost}")

def main():
    # Connect to database
    try:
        conn = get_connection()
        print("Connected to database successfully.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Get Excel file path
    excel_path = input("Enter the path to the Excel file: ")
    if not excel_path:
        excel_path = r"C:\Users\Manpreet\Downloads\Vendor_Data_Final_version_cleaned - Copy.xlsx"
        print(f"Using default path: {excel_path}")
    
    # Check if file exists
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return
    
    try:
        # Ask if user wants to reset tables
        reset = input("Do you want to reset all tables before import? (yes/no): ").lower()
        if reset == 'yes':
            if not reset_tables(conn):
                return
        
        # Import vendors
        vendor_count = import_vendors(excel_path, conn)
        
        # Import BoxHero items
        boxhero_items = import_items(excel_path, 'BoxHero_Items', 'BoxHero', conn)
        
        # Import Raw Materials items
        raw_materials_items = import_items(excel_path, 'Raw_Materials_Items', 'Raw Materials', conn)
        
        # Create BoxHero mappings
        boxhero_mappings = create_vendor_mappings(excel_path, 'BoxHero_Items', 'BoxHero', boxhero_items, conn)
        
        # Create Raw Materials mappings
        raw_materials_mappings = create_vendor_mappings(excel_path, 'Raw_Materials_Items', 'Raw Materials', raw_materials_items, conn)
        
        # Validate data
        validate_data(conn)
        
        # Print summary
        print("\n--- IMPORT SUMMARY ---")
        print(f"Vendors imported: {vendor_count}")
        print(f"BoxHero items imported: {len(boxhero_items)}")
        print(f"Raw Materials items imported: {len(raw_materials_items)}")
        print(f"BoxHero mappings created: {boxhero_mappings}")
        print(f"Raw Materials mappings created: {raw_materials_mappings}")
        print(f"Total mappings: {boxhero_mappings + raw_materials_mappings}")
    
    except Exception as e:
        print(f"Error during import: {e}")
    
    finally:
        # Close connection
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
