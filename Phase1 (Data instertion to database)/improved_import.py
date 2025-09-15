import pandas as pd
import os
from dotenv import load_dotenv
from db_connector import DatabaseConnector
import numpy as np

# Load environment variables
load_dotenv()

def clean_data(df):
    """Clean dataframe by replacing NaN values with None"""
    return df.replace({np.nan: None})

def import_vendors(excel_path, db):
    """Import vendor data from the Final_Vendor_List sheet"""
    print("Importing vendors...")
    
    # Read vendor data from Excel
    vendors_df = pd.read_excel(excel_path, sheet_name='Final_Vendor_List')
    vendors_df = clean_data(vendors_df)
    
    # Count of successfully imported vendors
    success_count = 0
    
    # Process each vendor row
    for _, row in vendors_df.iterrows():
        vendor_name = row.get('Vendor')
        contact_name = row.get('Contact Name')
        vendor_email = row.get('Vendor Email')
        vendor_phone = row.get('Vendor Phone')
        
        # Skip rows with no vendor name
        if pd.isna(vendor_name) or not vendor_name:
            continue
            
        # Add vendor to database
        if db.add_vendor(vendor_name, contact_name, vendor_email, vendor_phone):
            success_count += 1
    
    print(f"Successfully imported {success_count} vendors out of {len(vendors_df)}")
    return success_count

def import_items_with_mappings(excel_path, sheet_name, source_sheet, db):
    """Import items and create vendor mappings from Excel sheet"""
    print(f"Importing {source_sheet} items...")
    
    # Read items data from Excel
    items_df = pd.read_excel(excel_path, sheet_name=sheet_name)
    items_df = clean_data(items_df)
    
    # Get all vendors for mapping
    all_vendors = db.get_all_vendors()
    vendors_dict = {v['vendor_name']: v['vendor_id'] for v in all_vendors}
    
    # First pass: Add all unique items to the database
    unique_items = {}  # Dictionary to store unique items and their IDs
    item_count = 0
    
    print("Step 1: Adding unique items...")
    for _, row in items_df.iterrows():
        item_name = row.get('Item Name')
        item_type = row.get('Item Type')
        
        # Skip rows with no item name
        if pd.isna(item_name) or not item_name:
            continue
        
        # Create a unique key for this item
        item_key = f"{item_name}|{item_type}|{source_sheet}"
        
        # Only add the item if we haven't seen it before
        if item_key not in unique_items:
            # Prepare item attributes based on source sheet
            if source_sheet == 'BoxHero':
                sku = row.get('SKU')
                barcode = row.get('Barcode')
                height, width, thickness = None, None, None
            else:  # Raw Materials
                sku, barcode = None, None
                height = row.get('Height')
                width = row.get('Width')
                thickness = row.get('Thickness')
            
            # Add item to database
            if db.add_item(item_name, item_type, source_sheet, sku, barcode, height, width, thickness):
                item_count += 1
                
                # Get the item ID and store it
                items = db.fetch_data(
                    "SELECT item_id FROM Items WHERE item_name = ? AND item_type = ? AND source_sheet = ?", 
                    [item_name, item_type, source_sheet]
                )
                
                if items:
                    unique_items[item_key] = items[0]['item_id']
    
    print(f"Successfully added {item_count} unique {source_sheet} items")
    
    # Second pass: Create all item-vendor mappings
    mapping_count = 0
    
    print("Step 2: Creating item-vendor mappings...")
    for _, row in items_df.iterrows():
        item_name = row.get('Item Name')
        item_type = row.get('Item Type')
        vendor_name = row.get('Vendor')
        cost = row.get('Cost')
        
        # Skip rows with missing data
        if (pd.isna(item_name) or not item_name or 
            pd.isna(vendor_name) or not vendor_name):
            continue
        
        # Get the item ID from our dictionary
        item_key = f"{item_name}|{item_type}|{source_sheet}"
        item_id = unique_items.get(item_key)
        
        # Get the vendor ID
        vendor_id = vendors_dict.get(vendor_name)
        
        # Create the mapping if both IDs exist
        if item_id and vendor_id:
            # Check if mapping already exists
            existing_mappings = db.fetch_data(
                "SELECT map_id FROM ItemVendorMap WHERE item_id = ? AND vendor_id = ?",
                [item_id, vendor_id]
            )
            
            if not existing_mappings:
                # Link item to vendor with cost
                if db.link_item_to_vendor(item_id, vendor_id, cost):
                    mapping_count += 1
                    print(f"  Created mapping: {item_name} -> {vendor_name} (${cost})")
            else:
                print(f"  Mapping already exists: {item_name} -> {vendor_name}")
        else:
            if not item_id:
                print(f"  Warning: Could not find item ID for {item_name}")
            if not vendor_id:
                print(f"  Warning: Could not find vendor ID for {vendor_name}")
    
    print(f"Successfully created {mapping_count} item-vendor mappings for {source_sheet}")
    return item_count, mapping_count

def validate_mappings(db):
    """Validate that all mappings were created correctly"""
    print("\nValidating item-vendor mappings...")
    
    # Check for items without any vendor mappings
    unmapped_items = db.fetch_data("""
        SELECT i.item_id, i.item_name, i.item_type, i.source_sheet
        FROM Items i
        LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
        WHERE m.map_id IS NULL
    """)
    
    if unmapped_items:
        print(f"Warning: Found {len(unmapped_items)} items without any vendor mappings:")
        for item in unmapped_items:
            print(f"  - {item['item_name']} ({item['item_type']})")
    else:
        print("All items have at least one vendor mapping.")
    
    # Check for duplicate mappings
    duplicate_mappings = db.fetch_data("""
        SELECT item_id, vendor_id, COUNT(*) as duplicate_count
        FROM ItemVendorMap
        GROUP BY item_id, vendor_id
        HAVING COUNT(*) > 1
    """)
    
    if duplicate_mappings:
        print(f"Warning: Found {len(duplicate_mappings)} duplicate item-vendor mappings.")
    else:
        print("No duplicate item-vendor mappings found.")
    
    # Show vendor counts per item
    vendor_counts = db.fetch_data("""
        SELECT i.item_name, COUNT(DISTINCT m.vendor_id) as vendor_count
        FROM Items i
        JOIN ItemVendorMap m ON i.item_id = m.item_id
        GROUP BY i.item_name
        ORDER BY vendor_count
    """)
    
    if vendor_counts:
        single_vendor_items = [item for item in vendor_counts if item['vendor_count'] == 1]
        multi_vendor_items = [item for item in vendor_counts if item['vendor_count'] > 1]
        
        print(f"Items with only one vendor: {len(single_vendor_items)}")
        print(f"Items with multiple vendors: {len(multi_vendor_items)}")
        
        # Show a few examples of multi-vendor items
        if multi_vendor_items:
            print("\nExamples of items with multiple vendors:")
            for item in multi_vendor_items[:5]:  # Show up to 5 examples
                item_name = item['item_name']
                vendors = db.fetch_data("""
                    SELECT v.vendor_name, m.cost
                    FROM ItemVendorMap m
                    JOIN Vendors v ON m.vendor_id = v.vendor_id
                    JOIN Items i ON m.item_id = i.item_id
                    WHERE i.item_name = ?
                    ORDER BY v.vendor_name
                """, [item_name])
                
                print(f"  - {item_name} ({item['vendor_count']} vendors):")
                for vendor in vendors:
                    print(f"    * {vendor['vendor_name']} (${vendor['cost']})")
    
    # Return summary statistics
    return {
        'unmapped_items': len(unmapped_items) if unmapped_items else 0,
        'duplicate_mappings': len(duplicate_mappings) if duplicate_mappings else 0,
        'single_vendor_items': len(single_vendor_items) if 'single_vendor_items' in locals() else 0,
        'multi_vendor_items': len(multi_vendor_items) if 'multi_vendor_items' in locals() else 0
    }

def main():
    # Connect to the database
    db = DatabaseConnector()
    
    # Check if connection was successful
    if not db.connection:
        print("Failed to connect to the database. Please check your connection settings.")
        return
    
    # Get Excel file path from user
    excel_path = input("Enter the path to the Excel file: ")
    
    # Use default path if none provided
    if not excel_path:
        excel_path = r"C:\Users\Manpreet\Downloads\Vendor_Data_Final_version_cleaned - Copy.xlsx"
        print(f"Using default path: {excel_path}")
    
    # Check if the file exists
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return
    
    try:
        # Import data from each sheet
        vendor_count = import_vendors(excel_path, db)
        
        boxhero_count, boxhero_map_count = import_items_with_mappings(
            excel_path, 'BoxHero_Items', 'BoxHero', db
        )
        
        raw_materials_count, raw_materials_map_count = import_items_with_mappings(
            excel_path, 'Raw_Materials_Items', 'Raw Materials', db
        )
        
        # Validate the mappings
        validation_results = validate_mappings(db)
        
        # Print summary
        print("\nImport Summary:")
        print(f"- Vendors imported: {vendor_count}")
        print(f"- BoxHero items imported: {boxhero_count}")
        print(f"- Raw Materials items imported: {raw_materials_count}")
        print(f"- Total item-vendor mappings: {boxhero_map_count + raw_materials_map_count}")
        print("\nValidation Results:")
        print(f"- Items without vendor mappings: {validation_results['unmapped_items']}")
        print(f"- Duplicate mappings: {validation_results['duplicate_mappings']}")
        print(f"- Items with single vendor: {validation_results['single_vendor_items']}")
        print(f"- Items with multiple vendors: {validation_results['multi_vendor_items']}")
        
    except Exception as e:
        print(f"An error occurred during import: {e}")
    finally:
        # Close the database connection
        db.close_connection()

if __name__ == "__main__":
    main()
