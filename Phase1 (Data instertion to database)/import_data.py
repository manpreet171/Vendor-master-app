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
        vendor_name = row['Vendor']
        contact_name = row['Contact Name']
        vendor_email = row['Vendor Email']
        vendor_phone = row['Vendor Phone']
        
        # Skip rows with no vendor name
        if pd.isna(vendor_name) or not vendor_name:
            continue
            
        # Add vendor to database
        if db.add_vendor(vendor_name, contact_name, vendor_email, vendor_phone):
            success_count += 1
    
    print(f"Successfully imported {success_count} vendors out of {len(vendors_df)}")
    return success_count

def import_boxhero_items(excel_path, db):
    """Import items from the BoxHero_Items sheet"""
    print("Importing BoxHero items...")
    
    # Read BoxHero items data from Excel
    items_df = pd.read_excel(excel_path, sheet_name='BoxHero_Items')
    items_df = clean_data(items_df)
    
    # Get all vendors for mapping
    vendors = {v['vendor_name']: v['vendor_id'] for v in db.get_all_vendors()}
    
    # Count of successfully imported items
    success_count = 0
    vendor_map_count = 0
    
    # Process each item row
    for _, row in items_df.iterrows():
        item_name = row['Item Name']
        item_type = row['Item Type']
        vendor_name = row['Vendor']
        cost = row['Cost']
        sku = row['SKU']
        barcode = row['Barcode']
        
        # Skip rows with no item name
        if pd.isna(item_name) or not item_name:
            continue
            
        # Add item to database
        if db.add_item(item_name, item_type, 'BoxHero', sku, barcode, None, None, None):
            success_count += 1
            
            # Get the newly added item's ID
            items = db.fetch_data(f"SELECT item_id FROM Items WHERE item_name = ? AND item_type = ? AND source_sheet = ?", 
                                [item_name, item_type, 'BoxHero'])
            
            if items and vendor_name in vendors:
                item_id = items[0]['item_id']
                vendor_id = vendors[vendor_name]
                
                # Link item to vendor with cost
                if db.link_item_to_vendor(item_id, vendor_id, cost):
                    vendor_map_count += 1
    
    print(f"Successfully imported {success_count} BoxHero items")
    print(f"Successfully mapped {vendor_map_count} items to vendors")
    return success_count, vendor_map_count

def import_raw_materials_items(excel_path, db):
    """Import items from the Raw_Materials_Items sheet"""
    print("Importing Raw Materials items...")
    
    # Read Raw Materials items data from Excel
    items_df = pd.read_excel(excel_path, sheet_name='Raw_Materials_Items')
    items_df = clean_data(items_df)
    
    # Get all vendors for mapping
    vendors = {v['vendor_name']: v['vendor_id'] for v in db.get_all_vendors()}
    
    # Count of successfully imported items
    success_count = 0
    vendor_map_count = 0
    
    # Process each item row
    for _, row in items_df.iterrows():
        item_name = row['Item Name']
        item_type = row['Item Type']
        vendor_name = row['Vendor']
        cost = row['Cost']
        height = row.get('Height')
        width = row.get('Width')
        thickness = row.get('Thickness')
        
        # Skip rows with no item name
        if pd.isna(item_name) or not item_name:
            continue
            
        # Add item to database
        if db.add_item(item_name, item_type, 'Raw Materials', None, None, height, width, thickness):
            success_count += 1
            
            # Get the newly added item's ID
            items = db.fetch_data(f"SELECT item_id FROM Items WHERE item_name = ? AND item_type = ? AND source_sheet = ?", 
                                [item_name, item_type, 'Raw Materials'])
            
            if items and vendor_name in vendors:
                item_id = items[0]['item_id']
                vendor_id = vendors[vendor_name]
                
                # Link item to vendor with cost
                if db.link_item_to_vendor(item_id, vendor_id, cost):
                    vendor_map_count += 1
    
    print(f"Successfully imported {success_count} Raw Materials items")
    print(f"Successfully mapped {vendor_map_count} items to vendors")
    return success_count, vendor_map_count

def main():
    # Connect to the database
    db = DatabaseConnector()
    
    # Check if connection was successful
    if not db.connection:
        print("Failed to connect to the database. Please check your connection settings.")
        return
    
    # Use the provided Excel file path
    excel_path = r"C:\Users\Manpreet\Downloads\Vendor_Data_Final_version_cleaned - Copy.xlsx"
    
    # Check if the file exists
    if not os.path.exists(excel_path):
        print(f"File not found: {excel_path}")
        return
    
    try:
        # Import data from each sheet
        vendor_count = import_vendors(excel_path, db)
        boxhero_count, boxhero_map_count = import_boxhero_items(excel_path, db)
        raw_materials_count, raw_materials_map_count = import_raw_materials_items(excel_path, db)
        
        # Print summary
        print("\nImport Summary:")
        print(f"- Vendors imported: {vendor_count}")
        print(f"- BoxHero items imported: {boxhero_count}")
        print(f"- Raw Materials items imported: {raw_materials_count}")
        print(f"- Total item-vendor mappings: {boxhero_map_count + raw_materials_map_count}")
        
    except Exception as e:
        print(f"An error occurred during import: {e}")
    finally:
        # Close the database connection
        db.close_connection()

if __name__ == "__main__":
    main()
