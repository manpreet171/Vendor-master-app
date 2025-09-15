import streamlit as st
import pandas as pd
import os
import numpy as np
from db_connector import DatabaseConnector
import time
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="SDGNY Vendor Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .info-message {
        padding: 1rem;
        background-color: #d1ecf1;
        color: #0c5460;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to clean data
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

# Function to import vendors
def import_vendors(df, db, progress_bar=None, status_text=None):
    """Import vendor data from dataframe with manual ID management"""
    # Count of successfully imported vendors
    success_count = 0
    total_count = len(df)
    
    # Get the next available vendor_id
    cursor = db.connection.cursor()
    cursor.execute("SELECT ISNULL(MAX(vendor_id), 0) FROM Vendors")
    next_id = cursor.fetchone()[0] + 1
    
    # Process each vendor row
    for i, (_, row) in enumerate(df.iterrows()):
        vendor_name = row.get('Vendor')
        contact_name = row.get('Contact Name')
        vendor_email = row.get('Vendor Email')
        vendor_phone = row.get('Vendor Phone')
        
        # Skip rows with no vendor name
        if pd.isna(vendor_name) or not vendor_name:
            continue
        
        # Check if vendor already exists
        existing = db.fetch_data("SELECT vendor_id FROM Vendors WHERE vendor_name = ?", [vendor_name])
        
        if existing:
            if progress_bar is not None:
                status_text.text(f"Vendor already exists: {vendor_name}")
            continue
        
        # Add vendor using IDENTITY column (don't specify vendor_id)
        try:
            query = """
                INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
                VALUES (?, ?, ?, ?)
            """
            db.execute_query(query, [vendor_name, contact_name, vendor_email, vendor_phone])
            
            success_count += 1
            
            if progress_bar is not None:
                status_text.text(f"Added vendor: {vendor_name}")
        
        except Exception as e:
            if progress_bar is not None:
                status_text.text(f"Error adding vendor {vendor_name}: {str(e)}")
        
        # Update progress
        if progress_bar is not None:
            progress = (i + 1) / total_count
            progress_bar.progress(progress)
            time.sleep(0.01)  # Small delay for visual feedback
    
    if progress_bar is not None:
        progress_bar.progress(1.0)
        status_text.text(f"Successfully imported {success_count} vendors out of {total_count}")
    
    return success_count

# Function to import unique items (first pass)
def import_unique_items(df, db, source_sheet, progress_bar=None, status_text=None):
    """Import unique items from dataframe (first pass) with manual ID management"""
    # Dictionary to store unique items and their IDs
    unique_items = {}
    total_count = len(df)
    
    # Get the next available item_id
    cursor = db.connection.cursor()
    cursor.execute("SELECT ISNULL(MAX(item_id), 0) FROM Items")
    next_id = cursor.fetchone()[0] + 1
    
    # Process each item row
    for i, (_, row) in enumerate(df.iterrows()):
        item_name = row.get('Item Name')
        item_type = row.get('Item Type')
        
        # Skip rows with no item name
        if pd.isna(item_name) or not item_name:
            continue
        
        # Get cost for uniqueness and handle numeric conversion properly
        try:
            cost = row.get('Cost')
            cost = float(cost) if cost and not pd.isna(cost) else None
        except (ValueError, TypeError):
            cost = None
        
        # Create a unique key for this item including cost
        item_key = f"{item_name}|{item_type}|{source_sheet}|{cost}"
        
        # Only add the item if we haven't seen it before
        if item_key not in unique_items:
            # Prepare item attributes based on source sheet
            if source_sheet == 'BoxHero':
                # Handle BoxHero data properly
                try:
                    sku = row.get('SKU')
                    sku = str(sku) if sku and not pd.isna(sku) else None
                except:
                    sku = None
                    
                try:
                    barcode = row.get('Barcode')
                    barcode = str(barcode) if barcode and not pd.isna(barcode) else None
                except:
                    barcode = None
                    
                height, width, thickness = None, None, None
            else:  # Raw Materials
                sku, barcode = None, None
                # Get dimensions and handle numeric conversion properly
                try:
                    height = row.get('Height')
                    height = float(height) if height and not pd.isna(height) else None
                except (ValueError, TypeError):
                    height = None
                    
                try:
                    width = row.get('Width')
                    width = float(width) if width and not pd.isna(width) else None
                except (ValueError, TypeError):
                    width = None
                    
                try:
                    thickness = row.get('Thickness')
                    thickness = float(thickness) if thickness and not pd.isna(thickness) else None
                except (ValueError, TypeError):
                    thickness = None
            
            # Store cost in the item record for uniqueness
            # We'll add a new column to store the cost with the item
            
            # Check if item already exists using proper NULL handling
            query = """
                SELECT item_id FROM Items 
                WHERE item_name = ? AND item_type = ? AND source_sheet = ?
                AND ISNULL(sku, '') = ISNULL(?, '')
                AND ISNULL(barcode, '') = ISNULL(?, '')
                AND ISNULL(height, 0) = ISNULL(?, 0)
                AND ISNULL(width, 0) = ISNULL(?, 0)
                AND ISNULL(thickness, 0) = ISNULL(?, 0)
                AND ISNULL(cost, 0) = ISNULL(?, 0)
            """
            
            existing = db.fetch_data(query, [item_name, item_type, source_sheet, sku, barcode, height, width, thickness, cost])
            
            if existing:
                if progress_bar is not None:
                    status_text.text(f"Item already exists: {item_name}")
                unique_items[item_key] = existing[0]['item_id']
                continue
            
            # Add item with manual ID
            try:
                # Check if we're connected to the database
                if not db.connection:
                    if progress_bar is not None:
                        status_text.text("Database connection failed. Check your connection settings.")
                    return False
                
                # First, check if cost column exists and add it if needed
                try:
                    # Check if cost column exists - using a simpler query that works in all SQL Server versions
                    check_column_query = """
                        SELECT COUNT(*) as count FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = 'Items' AND COLUMN_NAME = 'cost'
                    """
                    column_exists = db.fetch_data(check_column_query)
                    
                    # Add cost column if it doesn't exist
                    if column_exists and column_exists[0]['count'] == 0:
                        alter_table_query = "ALTER TABLE Items ADD cost decimal(10,2) NULL"
                        db.execute_query(alter_table_query)
                        if progress_bar is not None:
                            status_text.text("Added cost column to Items table")
                except Exception as e:
                    if progress_bar is not None:
                        status_text.text(f"Error checking/adding cost column: {str(e)}")
                
                # Insert item with cost - using IDENTITY column (don't specify item_id)
                # First, let's check if the item already exists to avoid unique constraint violations
                # Use the full unique constraint from the database schema
                check_query = """
                    SELECT item_id FROM Items 
                    WHERE item_name = ? AND item_type = ? 
                    AND ISNULL(sku, '') = ISNULL(?, '')
                    AND ISNULL(height, 0) = ISNULL(?, 0)
                    AND ISNULL(width, 0) = ISNULL(?, 0)
                    AND ISNULL(thickness, 0) = ISNULL(?, 0)
                """
                existing_item = db.fetch_data(check_query, [item_name, item_type, sku, height, width, thickness])
                
                if existing_item:
                    # Item already exists, get its ID
                    item_id = existing_item[0]['item_id']
                    unique_items[item_key] = item_id
                    if progress_bar is not None:
                        status_text.text(f"Item already exists: {item_name} with ID {item_id}")
                else:
                    # Insert new item - handle NULL values properly
                    query = """
                        INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # Convert empty strings to None for SQL NULL
                    if pd.isna(sku) or sku == '':
                        sku = None
                    if pd.isna(barcode) or barcode == '':
                        barcode = None
                    if pd.isna(height) or height == '':
                        height = None
                    if pd.isna(width) or width == '':
                        width = None
                    if pd.isna(thickness) or thickness == '':
                        thickness = None
                        
                    # Print debug info
                    print(f"Inserting item: {item_name}, {item_type}, {source_sheet}")
                    print(f"Values: sku={sku}, barcode={barcode}, height={height}, width={width}, thickness={thickness}")
                    
                    # Try to handle barcode as string if it's a number
                    try:
                        if barcode is not None and isinstance(barcode, (int, float)):
                            barcode = str(int(barcode))
                    except:
                        pass
                    
                    success = db.execute_query(query, [item_name, item_type, source_sheet, sku, barcode, height, width, thickness])
                    
                    if not success:
                        if progress_bar is not None:
                            status_text.text(f"Error inserting item: {item_name} - Check console for details")
                            st.error(f"Error inserting item: {item_name} - Check console for details")
                        continue
                
                # Only get the newly inserted item's ID if we actually inserted a new item
                if not existing_item:
                    id_query = "SELECT SCOPE_IDENTITY() AS new_id"
                    result = db.fetch_data(id_query)
                    if result and 'new_id' in result[0] and result[0]['new_id'] is not None:
                        item_id = result[0]['new_id']
                        unique_items[item_key] = item_id
                        if progress_bar is not None:
                            status_text.text(f"Added item: {item_name} with ID {item_id}")
                    else:
                        # Try to get the item ID by querying for the item
                        query = """
                            SELECT item_id FROM Items 
                            WHERE item_name = ? AND item_type = ? AND source_sheet = ?
                        """
                        result = db.fetch_data(query, [item_name, item_type, source_sheet])
                        if result:
                            item_id = result[0]['item_id']
                            unique_items[item_key] = item_id
                            if progress_bar is not None:
                                status_text.text(f"Found existing item: {item_name} with ID {item_id}")
                
                # Status already updated above
            
            except Exception as e:
                if progress_bar is not None:
                    status_text.text(f"Error adding item {item_name}: {str(e)}")
        
        # Update progress
        if progress_bar is not None:
            progress = (i + 1) / total_count
            progress_bar.progress(progress)
            status_text.text(f"Processed {i+1}/{total_count} rows, found {len(unique_items)} unique items")
            time.sleep(0.01)  # Small delay for visual feedback
    
    if progress_bar is not None:
        progress_bar.progress(1.0)
        status_text.text(f"Successfully added {len(unique_items)} unique {source_sheet} items")
    
    return unique_items

# Function to create item-vendor mappings (second pass)
def create_item_vendor_mappings(df, db, source_sheet, items_dict, vendors_dict, progress_bar=None, status_text=None):
    """Create item-vendor mappings from dataframe (second pass)"""
    # Count of successfully created mappings
    mapping_count = 0
    total_count = len(df)
    
    # Process each row
    for i, (_, row) in enumerate(df.iterrows()):
        item_name = row.get('Item Name')
        item_type = row.get('Item Type')
        vendor_name = row.get('Vendor')
        cost = row.get('Cost')
        
        # Skip rows with missing data
        if (pd.isna(item_name) or not item_name or 
            pd.isna(vendor_name) or not vendor_name):
            continue
        
        # Get the item ID from our dictionary using cost in the key
        item_key = f"{item_name}|{item_type}|{source_sheet}|{cost}"
        item_id = items_dict.get(item_key)
        
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
                try:
                    # Insert mapping directly with SQL to avoid issues
                    query = "INSERT INTO ItemVendorMap (item_id, vendor_id, cost) VALUES (?, ?, ?)"
                    db.execute_query(query, [item_id, vendor_id, cost])
                    
                    # Ensure cost is consistent between Items and ItemVendorMap tables
                    update_cost_query = "UPDATE Items SET cost = ? WHERE item_id = ? AND (cost IS NULL OR cost != ?)"
                    db.execute_query(update_cost_query, [cost, item_id, cost])
                    
                    mapping_count += 1
                    
                    if progress_bar is not None:
                        status_text.text(f"Created mapping: {item_name} -> {vendor_name} (${cost})")
                
                except Exception as e:
                    if progress_bar is not None:
                        status_text.text(f"Error creating mapping {item_name} -> {vendor_name}: {str(e)}")
            else:
                if progress_bar is not None:
                    status_text.text(f"Mapping already exists: {item_name} -> {vendor_name}")
        else:
            if not item_id and progress_bar is not None:
                status_text.text(f"Warning: Item not found: {item_name}")
            
            if not vendor_id and progress_bar is not None:
                status_text.text(f"Warning: Vendor not found: {vendor_name}")
        
        # Update progress
        if progress_bar is not None:
            progress = (i + 1) / total_count
            progress_bar.progress(progress)
            time.sleep(0.01)  # Small delay for visual feedback
    
    if progress_bar is not None:
        progress_bar.progress(1.0)
        status_text.text(f"Successfully created {mapping_count} item-vendor mappings for {source_sheet}")
    
    return mapping_count

# Function to validate mappings
def validate_mappings(db):
    """Validate that all mappings were created correctly"""
    results = {}
    
    # Check for items without any vendor mappings
    unmapped_items = db.fetch_data("""
        SELECT i.item_id, i.item_name, i.item_type, i.source_sheet
        FROM Items i
        LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
        WHERE m.map_id IS NULL
    """)
    
    results['unmapped_items'] = len(unmapped_items) if unmapped_items else 0
    
    # Check for duplicate mappings
    duplicate_mappings = db.fetch_data("""
        SELECT item_id, vendor_id, COUNT(*) as duplicate_count
        FROM ItemVendorMap
        GROUP BY item_id, vendor_id
        HAVING COUNT(*) > 1
    """)
    
    results['duplicate_mappings'] = len(duplicate_mappings) if duplicate_mappings else 0
    
    # Show vendor counts per item
    vendor_counts = db.fetch_data("""
        SELECT i.item_name, COUNT(DISTINCT m.vendor_id) as vendor_count
        FROM Items i
        JOIN ItemVendorMap m ON i.item_id = m.item_id
        GROUP BY i.item_name
        ORDER BY vendor_count DESC
    """)
    
    if vendor_counts:
        single_vendor_items = [item for item in vendor_counts if item['vendor_count'] == 1]
        multi_vendor_items = [item for item in vendor_counts if item['vendor_count'] > 1]
        
        results['single_vendor_items'] = len(single_vendor_items)
        results['multi_vendor_items'] = len(multi_vendor_items)
        
        # Get examples of multi-vendor items
        multi_vendor_examples = []
        for item in multi_vendor_items[:5]:  # Get up to 5 examples
            item_name = item['item_name']
            vendors = db.fetch_data("""
                SELECT v.vendor_name, m.cost
                FROM ItemVendorMap m
                JOIN Vendors v ON m.vendor_id = v.vendor_id
                JOIN Items i ON m.item_id = i.item_id
                WHERE i.item_name = ?
                ORDER BY v.vendor_name
            """, [item_name])
            
            multi_vendor_examples.append({
                'item_name': item_name,
                'vendors': vendors
            })
        
        results['multi_vendor_examples'] = multi_vendor_examples
    else:
        results['single_vendor_items'] = 0
        results['multi_vendor_items'] = 0
        results['multi_vendor_examples'] = []
    
    return results

# Main app
def main():
    st.title("SDGNY Vendor Management System")
    st.markdown("### Excel Data Import Tool")
    
    # Sidebar for database connection status
    st.sidebar.title("Database Connection")
    
    # Connect to database
    db = DatabaseConnector()
    
    # Check connection status
    if db.connection:
        st.sidebar.success("✅ Connected to database")
        st.sidebar.write(f"Server: {os.getenv('DB_SERVER')}")
        st.sidebar.write(f"Database: {os.getenv('DB_NAME')}")
    else:
        st.sidebar.error("❌ Database connection failed")
        st.error("Could not connect to the database. Please check your connection settings in the .env file.")
        return
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Load Excel file
            st.info("Reading Excel file...")
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            # Check for required sheets
            required_sheets = ["Final_Vendor_List", "BoxHero_Items", "Raw_Materials_Items"]
            missing_sheets = [sheet for sheet in required_sheets if sheet not in sheet_names]
            
            if missing_sheets:
                st.error(f"Missing required sheets: {', '.join(missing_sheets)}")
                return
            
            # Show sheet preview tabs
            tab1, tab2, tab3 = st.tabs(["Vendors", "BoxHero Items", "Raw Materials Items"])
            
            # Load and display vendor data
            with tab1:
                vendors_df = pd.read_excel(excel_file, "Final_Vendor_List")
                vendors_df = clean_data(vendors_df)
                st.write("Vendor Data Preview:")
                st.dataframe(vendors_df.head(10), use_container_width=True)
                st.write(f"Total vendors: {len(vendors_df)}")
            
            # Load and display BoxHero items data
            with tab2:
                boxhero_df = pd.read_excel(excel_file, "BoxHero_Items")
                boxhero_df = clean_data(boxhero_df)
                st.write("BoxHero Items Preview:")
                st.dataframe(boxhero_df.head(10), use_container_width=True)
                st.write(f"Total BoxHero items: {len(boxhero_df)}")
            
            # Load and display Raw Materials items data
            with tab3:
                raw_materials_df = pd.read_excel(excel_file, "Raw_Materials_Items")
                raw_materials_df = clean_data(raw_materials_df)
                st.write("Raw Materials Items Preview:")
                st.dataframe(raw_materials_df.head(10), use_container_width=True)
                st.write(f"Total Raw Materials items: {len(raw_materials_df)}")
            
            # Import data button
            if st.button("Import Data to Database"):
                with st.spinner("Importing data..."):
                    # Create expander for import details
                    with st.expander("Import Details", expanded=True):
                        # Step 1: Import vendors
                        st.subheader("Step 1: Importing Vendors")
                        progress_bar_vendors = st.progress(0)
                        status_text_vendors = st.empty()
                        
                        # Import vendors
                        vendor_count = import_vendors(vendors_df, db, progress_bar_vendors, status_text_vendors)
                        
                        # Step 2: Import unique BoxHero items
                        st.subheader("Step 2: Importing BoxHero Items")
                        progress_bar_boxhero = st.progress(0)
                        status_text_boxhero = st.empty()
                        
                        # First pass: Add all unique BoxHero items
                        boxhero_items_dict = import_unique_items(boxhero_df, db, "BoxHero", progress_bar_boxhero, status_text_boxhero)
                        
                        # Step 3: Import unique Raw Materials items
                        st.subheader("Step 3: Importing Raw Materials Items")
                        progress_bar_raw = st.progress(0)
                        status_text_raw = st.empty()
                        
                        # First pass: Add all unique Raw Materials items
                        raw_items_dict = import_unique_items(raw_materials_df, db, "Raw Materials", progress_bar_raw, status_text_raw)
                        
                        # Step 4: Create all BoxHero item-vendor mappings
                        st.subheader("Step 4: Creating BoxHero Item-Vendor Mappings")
                        progress_bar_boxhero_map = st.progress(0)
                        status_text_boxhero_map = st.empty()
                        
                        # Get all vendors for mapping
                        vendors_dict = {v['vendor_name']: v['vendor_id'] for v in db.get_all_vendors()}
                        
                        # Second pass: Create all BoxHero item-vendor mappings
                        boxhero_map_count = create_item_vendor_mappings(
                            boxhero_df, db, "BoxHero", boxhero_items_dict, vendors_dict,
                            progress_bar_boxhero_map, status_text_boxhero_map
                        )
                        
                        # Step 5: Create all Raw Materials item-vendor mappings
                        st.subheader("Step 5: Creating Raw Materials Item-Vendor Mappings")
                        progress_bar_raw_map = st.progress(0)
                        status_text_raw_map = st.empty()
                        
                        # Second pass: Create all Raw Materials item-vendor mappings
                        raw_map_count = create_item_vendor_mappings(
                            raw_materials_df, db, "Raw Materials", raw_items_dict, vendors_dict,
                            progress_bar_raw_map, status_text_raw_map
                        )
                        
                        # Step 6: Validate mappings
                        st.subheader("Step 6: Validating Mappings")
                        validation_results = validate_mappings(db)
                        
                        # Print summary
                        st.markdown("### Import Summary")
                        st.markdown(f"- **Vendors imported:** {vendor_count}")
                        st.markdown(f"- **BoxHero items imported:** {len(boxhero_items_dict)}")
                        st.markdown(f"- **Raw Materials items imported:** {len(raw_items_dict)}")
                        st.markdown(f"- **BoxHero item-vendor mappings:** {boxhero_map_count}")
                        st.markdown(f"- **Raw Materials item-vendor mappings:** {raw_map_count}")
                        st.markdown(f"- **Total item-vendor mappings:** {boxhero_map_count + raw_map_count}")
                        
                        # Validation results
                        st.markdown("### Validation Results")
                        st.markdown(f"- **Items without vendor mappings:** {validation_results['unmapped_items']}")
                        st.markdown(f"- **Duplicate mappings:** {validation_results['duplicate_mappings']}")
                        st.markdown(f"- **Items with single vendor:** {validation_results['single_vendor_items']}")
                        st.markdown(f"- **Items with multiple vendors:** {validation_results['multi_vendor_items']}")
                        
                        # Show examples of multi-vendor items if available
                        if validation_results['multi_vendor_examples']:
                            st.markdown("### Examples of Items with Multiple Vendors")
                            for example in validation_results['multi_vendor_examples']:
                                with st.expander(f"{example['item_name']} ({len(example['vendors'])} vendors)"):
                                    for vendor in example['vendors']:
                                        st.write(f"- {vendor['vendor_name']}: ${vendor['cost']}")
                
                st.success("Data import completed successfully!")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Database verification section
    st.markdown("---")
    st.subheader("Database Verification")
    
    # Create tabs for different verification queries
    verify_tab1, verify_tab2, verify_tab3, verify_tab4, verify_tab5, verify_tab6 = st.tabs(["Vendors", "Items", "Item-Vendor Mappings", "Vendor Count Analysis", "Data Validation", "Item Search"])
    
    with verify_tab1:
        if st.button("View All Vendors"):
            vendors = db.get_all_vendors()
            if vendors:
                st.dataframe(pd.DataFrame(vendors), use_container_width=True)
                st.write(f"Total vendors: {len(vendors)}")
            else:
                st.info("No vendors found in the database.")
    
    with verify_tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            source_options = ["All", "BoxHero", "Raw Materials"]
            source_filter = st.selectbox("Filter by source:", source_options)
        
        with col2:
            # Get all unique item types for filtering
            item_types_query = "SELECT DISTINCT item_type FROM Items ORDER BY item_type"
            item_types_result = db.fetch_data(item_types_query)
            item_types = ["All"] + [item['item_type'] for item in item_types_result] if item_types_result else ["All"]
            type_filter = st.selectbox("Filter by item type:", item_types)
        
        if st.button("View Items"):
            # Build query based on filters
            query_parts = ["SELECT * FROM Items"]
            params = []
            where_clauses = []
            
            if source_filter != "All":
                where_clauses.append("source_sheet = ?")
                params.append(source_filter)
            
            if type_filter != "All":
                where_clauses.append("item_type = ?")
                params.append(type_filter)
            
            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))
            
            query_parts.append("ORDER BY item_type, item_name")
            query = " ".join(query_parts)
            
            items = db.fetch_data(query, params)
            
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True)
                st.write(f"Total items: {len(items)}")
                
                # Show item type distribution
                if len(items) > 0:
                    df = pd.DataFrame(items)
                    type_counts = df['item_type'].value_counts().reset_index()
                    type_counts.columns = ['Item Type', 'Count']
                    
                    fig = px.bar(type_counts, x='Item Type', y='Count', 
                                 title='Item Type Distribution',
                                 labels={'Count': 'Number of Items', 'Item Type': 'Item Type'})
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No items found in the database.")
    
    with verify_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Get all unique item types for filtering
            item_types_query = "SELECT DISTINCT item_type FROM Items ORDER BY item_type"
            item_types_result = db.fetch_data(item_types_query)
            item_types = ["All"] + [item['item_type'] for item in item_types_result] if item_types_result else ["All"]
            type_filter = st.selectbox("Filter by item type:", item_types, key="mapping_type_filter")
        
        with col2:
            # Get all unique vendors for filtering
            vendors_query = "SELECT DISTINCT vendor_name FROM Vendors ORDER BY vendor_name"
            vendors_result = db.fetch_data(vendors_query)
            vendors = ["All"] + [v['vendor_name'] for v in vendors_result] if vendors_result else ["All"]
            vendor_filter = st.selectbox("Filter by vendor:", vendors)
        
        if st.button("View Item-Vendor Mappings"):
            # Build query based on filters
            query_parts = ["""
                SELECT i.item_name, i.item_type, v.vendor_name, m.cost, i.source_sheet,
                       i.height, i.width, i.thickness
                FROM ItemVendorMap m
                JOIN Items i ON m.item_id = i.item_id
                JOIN Vendors v ON m.vendor_id = v.vendor_id
            """]
            
            params = []
            where_clauses = []
            
            if type_filter != "All":
                where_clauses.append("i.item_type = ?")
                params.append(type_filter)
            
            if vendor_filter != "All":
                where_clauses.append("v.vendor_name = ?")
                params.append(vendor_filter)
            
            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))
            
            query_parts.append("ORDER BY i.item_type, i.item_name, v.vendor_name")
            query = " ".join(query_parts)
            
            mappings = db.fetch_data(query, params)
            
            if mappings:
                # Convert to DataFrame for better display
                df = pd.DataFrame(mappings)
                st.dataframe(df, use_container_width=True)
                st.write(f"Total mappings: {len(mappings)}")
                
                # Show vendor distribution by item type
                if len(mappings) > 0:
                    # Count mappings by item type
                    type_counts = df.groupby('item_type').size().reset_index(name='count')
                    type_counts = type_counts.sort_values('count', ascending=False)
                    
                    fig = px.bar(type_counts, x='item_type', y='count', 
                                 title='Vendor Mappings by Item Type',
                                 labels={'count': 'Number of Mappings', 'item_type': 'Item Type'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show items with multiple vendors
                    multi_vendor_items = df.groupby('item_name').size()
                    multi_vendor_items = multi_vendor_items[multi_vendor_items > 1]
                    
                    if not multi_vendor_items.empty:
                        st.subheader(f"Items with Multiple Vendors: {len(multi_vendor_items)}")
                        multi_items_df = df[df['item_name'].isin(multi_vendor_items.index)]
                        st.dataframe(multi_items_df, use_container_width=True)
            else:
                st.info("No item-vendor mappings found in the database.")
    
    # Add a new tab for vendor count analysis
    with verify_tab4:
        st.subheader("Vendor Count Analysis")
        st.write("View the number of vendors for each item:")
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            # Get all unique item types for filtering
            item_types_query = "SELECT DISTINCT item_type FROM Items ORDER BY item_type"
            item_types_result = db.fetch_data(item_types_query)
            item_types = ["All"] + [item['item_type'] for item in item_types_result] if item_types_result else ["All"]
            type_filter = st.selectbox("Filter by item type:", item_types, key="vendor_count_type_filter")
        
        with col2:
            min_vendors = st.number_input("Minimum number of vendors:", min_value=1, value=1, step=1)
        
        if st.button("Analyze Vendor Counts"):
            # Build query to count vendors per item
            query = """
            SELECT i.item_id, i.item_name, i.item_type, i.source_sheet, 
                   COUNT(DISTINCT m.vendor_id) as vendor_count
            FROM Items i
            JOIN ItemVendorMap m ON i.item_id = m.item_id
            """
            
            params = []
            where_clauses = []
            
            if type_filter != "All":
                where_clauses.append("i.item_type = ?")
                params.append(type_filter)
            
            if where_clauses:
                query += "WHERE " + " AND ".join(where_clauses) + " "
            
            query += "GROUP BY i.item_id, i.item_name, i.item_type, i.source_sheet "
            query += "HAVING COUNT(DISTINCT m.vendor_id) >= ? "
            params.append(min_vendors)
            
            query += "ORDER BY vendor_count DESC, i.item_name"
            
            vendor_counts = db.fetch_data(query, params)
            
            if vendor_counts:
                # Convert to DataFrame for better display
                df = pd.DataFrame(vendor_counts)
                st.dataframe(df, use_container_width=True)
                st.write(f"Total items with {min_vendors}+ vendors: {len(vendor_counts)}")
                
                # Create histogram of vendor counts
                fig = px.histogram(df, x="vendor_count", 
                                  title="Distribution of Vendor Counts per Item",
                                  labels={"vendor_count": "Number of Vendors", "count": "Number of Items"},
                                  nbins=10)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show items with the most vendors
                st.subheader("Items with the Most Vendors")
                top_items = df.nlargest(10, 'vendor_count')
                st.dataframe(top_items, use_container_width=True)
                
                # Show vendor count by item type
                st.subheader("Average Vendors per Item Type")
                avg_by_type = df.groupby('item_type')['vendor_count'].mean().reset_index()
                avg_by_type.columns = ['Item Type', 'Average Vendor Count']
                avg_by_type = avg_by_type.sort_values('Average Vendor Count', ascending=False)
                
                fig2 = px.bar(avg_by_type, x='Item Type', y='Average Vendor Count',
                              title='Average Number of Vendors by Item Type')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info(f"No items found with {min_vendors} or more vendors.")
    
    # Move validation tab to the end
    with verify_tab5:
        tab5_col1, tab5_col2 = st.columns([1, 1])
        
        with tab5_col1:
            st.write("Run validation checks to ensure data integrity:")
            
            if st.button("Run Data Validation"):
                with st.spinner("Running validation checks..."):
                    # Get validation results
                    validation_results = db.validate_item_vendor_mappings()
                    
                    # Display summary counts
                    st.subheader("Database Summary")
                    if validation_results['summary_counts']:
                        st.dataframe(pd.DataFrame(validation_results['summary_counts']), use_container_width=True)
                    
                    # Check for unmapped items
                    st.subheader("Items Without Vendor Mappings")
                    if validation_results['unmapped_items']:
                        st.dataframe(pd.DataFrame(validation_results['unmapped_items']), use_container_width=True)
                        st.warning(f"Found {len(validation_results['unmapped_items'])} items without any vendor mappings.")
                    else:
                        st.success("All items have at least one vendor mapping.")
                    
                    # Check for duplicate mappings
                    st.subheader("Duplicate Item-Vendor Mappings")
                    if validation_results['duplicate_mappings']:
                        st.dataframe(pd.DataFrame(validation_results['duplicate_mappings']), use_container_width=True)
                        st.error(f"Found {len(validation_results['duplicate_mappings'])} duplicate item-vendor mappings.")
                    else:
                        st.success("No duplicate item-vendor mappings found.")
        
        with tab5_col2:
            st.subheader("Map Unmapped Items")
            
            # Get unmapped items
            unmapped_items = db.fetch_data("""
                SELECT i.item_id, i.item_name, i.item_type, i.source_sheet
                FROM Items i
                LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
                WHERE m.map_id IS NULL
                ORDER BY i.item_name
            """)
            
            if unmapped_items:
                # Create a dictionary for display
                unmapped_options = {f"{item['item_name']} ({item['item_type']})": item['item_id'] for item in unmapped_items}
                
                # Create a dropdown for unmapped items
                selected_item_label = st.selectbox("Select unmapped item:", list(unmapped_options.keys()))
                selected_item_id = unmapped_options[selected_item_label] if selected_item_label else None
                
                if selected_item_id:
                    # Show similar items with existing vendor mappings
                    item_name = selected_item_label.split(' (')[0]  # Extract just the name part
                    st.subheader("Similar Items with Existing Mappings")
                    
                    similar_items_query = """
                    SELECT i.item_id, i.item_name, i.item_type, v.vendor_name, m.cost
                    FROM Items i
                    JOIN ItemVendorMap m ON i.item_id = m.item_id
                    JOIN Vendors v ON m.vendor_id = v.vendor_id
                    WHERE i.item_name LIKE ?
                    ORDER BY i.item_name, v.vendor_name
                    """
                    
                    similar_items = db.fetch_data(similar_items_query, [f"%{item_name}%"])
                    
                    if similar_items:
                        st.dataframe(pd.DataFrame(similar_items), use_container_width=True)
                        st.info(f"Found {len(similar_items)} existing mappings for similar items.")
                    else:
                        st.info("No similar items with vendor mappings found.")
                    
                    st.subheader("Create New Mapping")
                    
                    # Get all vendors
                    all_vendors = db.fetch_data("SELECT vendor_id, vendor_name FROM Vendors ORDER BY vendor_name")
                    
                    if all_vendors:
                        # Create a dictionary for display
                        vendor_options = {vendor['vendor_name']: vendor['vendor_id'] for vendor in all_vendors}
                        
                        # Create multi-select for vendors
                        st.write("Select one or more vendors to map this item to:")
                        selected_vendors = st.multiselect("Select vendors:", list(vendor_options.keys()))
                        selected_vendor_ids = [vendor_options[v] for v in selected_vendors] if selected_vendors else []
                        
                        # Optional cost input
                        cost_value = st.number_input("Cost (optional):", min_value=0.0, step=0.01, value=None)
                        
                        if st.button("Create Mappings"):
                            if selected_item_id and selected_vendor_ids:
                                # Track success and failures
                                success_count = 0
                                failure_count = 0
                                already_exists_count = 0
                                
                                for vendor_name, vendor_id in [(v, vendor_options[v]) for v in selected_vendors]:
                                    # Check if mapping already exists
                                    existing = db.fetch_data(
                                        "SELECT map_id FROM ItemVendorMap WHERE item_id = ? AND vendor_id = ?",
                                        [selected_item_id, vendor_id]
                                    )
                                    
                                    if existing:
                                        already_exists_count += 1
                                        continue
                                    
                                    # Create the mapping
                                    query = "INSERT INTO ItemVendorMap (item_id, vendor_id, cost) VALUES (?, ?, ?)"
                                    success = db.execute_query(query, [selected_item_id, vendor_id, cost_value])
                                    
                                    if success:
                                        success_count += 1
                                    else:
                                        failure_count += 1
                                
                                # Show summary
                                if success_count > 0:
                                    st.success(f"Successfully created {success_count} mappings for {selected_item_label}")
                                if failure_count > 0:
                                    st.error(f"Failed to create {failure_count} mappings. Check database connection.")
                                if already_exists_count > 0:
                                    st.warning(f"Skipped {already_exists_count} mappings that already existed.")
                            else:
                                st.warning("Please select at least one vendor.")
                        
                        # Single vendor mapping option
                        st.subheader("Or Map to a Single Vendor")
                        selected_vendor = st.selectbox("Select vendor:", list(vendor_options.keys()))
                        selected_vendor_id = vendor_options[selected_vendor] if selected_vendor else None
                        
                        if st.button("Create Single Mapping"):
                            if selected_item_id and selected_vendor_id:
                                # Check if mapping already exists
                                existing = db.fetch_data(
                                    "SELECT map_id FROM ItemVendorMap WHERE item_id = ? AND vendor_id = ?",
                                    [selected_item_id, selected_vendor_id]
                                )
                                
                                if existing:
                                    st.error("This mapping already exists!")
                                else:
                                    # Create the mapping
                                    query = "INSERT INTO ItemVendorMap (item_id, vendor_id, cost) VALUES (?, ?, ?)"
                                    success = db.execute_query(query, [selected_item_id, selected_vendor_id, cost_value])
                                    
                                    if success:
                                        st.success(f"Successfully mapped {selected_item_label} to {selected_vendor}")
                                    else:
                                        st.error("Failed to create mapping. Check database connection.")
            else:
                st.info("No unmapped items found.")
                
                # Show vendor counts per item
                st.subheader("Vendor Counts Per Item")
                query = """
                SELECT i.item_name, COUNT(DISTINCT m.vendor_id) as vendor_count
                FROM Items i
                JOIN ItemVendorMap m ON i.item_id = m.item_id
                GROUP BY i.item_name
                ORDER BY vendor_count
                """
                vendor_counts = db.fetch_data(query)
                if vendor_counts:
                    fig = px.histogram(pd.DataFrame(vendor_counts), x="vendor_count", 
                                      title="Distribution of Vendors per Item",
                                      labels={"vendor_count": "Number of Vendors", "count": "Number of Items"})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show items with only one vendor
                    single_vendor_items = [item for item in vendor_counts if item['vendor_count'] == 1]
                    if single_vendor_items:
                        st.write(f"**{len(single_vendor_items)} items have only one vendor:**")
                        st.dataframe(pd.DataFrame(single_vendor_items), use_container_width=True)
                    
                    # Show items with multiple vendors
                    multi_vendor_items = [item for item in vendor_counts if item['vendor_count'] > 1]
                    if multi_vendor_items:
                        st.write(f"**{len(multi_vendor_items)} items have multiple vendors:**")
                        st.dataframe(pd.DataFrame(multi_vendor_items), use_container_width=True)
        
        # Add a search function to find vendors for a specific item
        st.subheader("Find Vendors for Item")
        item_name = st.text_input("Enter item name (or part of name)")
        if item_name:
            query = """
            SELECT i.item_name, i.item_type, v.vendor_name, v.contact_name, v.vendor_email, v.vendor_phone, m.cost
            FROM Items i
            JOIN ItemVendorMap m ON i.item_id = m.item_id
            JOIN Vendors v ON m.vendor_id = v.vendor_id
            WHERE i.item_name LIKE ?
            ORDER BY i.item_name, m.cost ASC
            """
            results = db.fetch_data(query, [f"%{item_name}%"])
            
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True)
                st.write(f"Found {len(results)} vendor mappings for items matching '{item_name}'")
            else:
                st.info(f"No items found matching '{item_name}'")
                
        # Add a search function to find items for a specific vendor
        st.subheader("Find Items for Vendor")
        vendor_name = st.text_input("Enter vendor name (or part of name)")
        if vendor_name:
            query = """
            SELECT v.vendor_name, i.item_name, i.item_type, i.source_sheet, m.cost
            FROM Vendors v
            JOIN ItemVendorMap m ON v.vendor_id = m.vendor_id
            JOIN Items i ON m.item_id = i.item_id
            WHERE v.vendor_name LIKE ?
            ORDER BY v.vendor_name, i.item_name
            """
            results = db.fetch_data(query, [f"%{vendor_name}%"])
            
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True)
                st.write(f"Found {len(results)} items supplied by vendors matching '{vendor_name}'")
            else:
                st.info(f"No vendors found matching '{vendor_name}'")
    
    with verify_tab6:
        st.subheader("Search Items and View All Vendors")
        
        # Create search options
        col1, col2 = st.columns(2)
        
        with col1:
            # Get all items for dropdown
            items_query = "SELECT DISTINCT item_name FROM Items ORDER BY item_name"
            items_result = db.fetch_data(items_query)
            
            # Create dropdown options
            item_options = ["Select an item..."] + [item['item_name'] for item in items_result] if items_result else ["No items found"]
            
            # Create a dropdown for items
            selected_item = st.selectbox("Select item:", item_options)
        
        with col2:
            source_options = ["All", "BoxHero", "Raw Materials"]
            source_filter = st.selectbox("Filter by source:", source_options)
        
        # Search button
        if st.button("Find Vendors"):
            if selected_item and selected_item != "Select an item..." and selected_item != "No items found":
                # Build query to find items and their vendors
                query = """
                SELECT 
                    i.item_id, 
                    i.item_name, 
                    i.item_type, 
                    i.source_sheet,
                    i.sku,
                    i.barcode,
                    i.height,
                    i.width,
                    i.thickness,
                    i.cost as item_cost,
                    v.vendor_name,
                    m.cost as vendor_cost
                FROM 
                    Items i
                LEFT JOIN 
                    ItemVendorMap m ON i.item_id = m.item_id
                LEFT JOIN 
                    Vendors v ON m.vendor_id = v.vendor_id
                WHERE 
                    i.item_name = ?
                """
                
                params = [selected_item]
                
                # Add source filter if selected
                if source_filter != "All":
                    query += " AND i.source_sheet = ?"
                    params.append(source_filter)
                
                query += " ORDER BY i.item_name, v.vendor_name"
                
                # Execute search
                results = db.fetch_data(query, params)
            
            if results:
                # Group results by item
                items_dict = {}
                for row in results:
                    item_id = row['item_id']
                    if item_id not in items_dict:
                        items_dict[item_id] = {
                            'item_id': item_id,
                            'item_name': row['item_name'],
                            'item_type': row['item_type'],
                            'source_sheet': row['source_sheet'],
                            'sku': row['sku'],
                            'barcode': row['barcode'],
                            'height': row['height'],
                            'width': row['width'],
                            'thickness': row['thickness'],
                            'item_cost': row['item_cost'],
                            'vendors': []
                        }
                        
                    # Add vendor if exists
                    if row['vendor_name']:
                        items_dict[item_id]['vendors'].append({
                            'vendor_name': row['vendor_name'],
                            'cost': row['vendor_cost']
                        })
                
                # Display results
                st.write(f"Found {len(items_dict)} items matching '{item_search}'")
                
                # Display each item with its vendors
                for item_id, item in items_dict.items():
                    with st.expander(f"{item['item_name']} ({item['item_type']}) - {item['source_sheet']}"):
                        # Item details
                        st.markdown("**Item Details:**")
                        details = {
                            'Item ID': item['item_id'],
                            'Item Name': item['item_name'],
                            'Item Type': item['item_type'],
                            'Source': item['source_sheet'],
                            'SKU': item['sku'] or 'N/A',
                            'Barcode': item['barcode'] or 'N/A',
                            'Height': item['height'] or 'N/A',
                            'Width': item['width'] or 'N/A',
                            'Thickness': item['thickness'] or 'N/A',
                            'Cost': item['item_cost'] or 'N/A'
                        }
                        st.json(details)
                        
                        # Vendor information
                        st.markdown("**Vendor Information:**")
                        if item['vendors']:
                            vendor_df = pd.DataFrame(item['vendors'])
                            st.dataframe(vendor_df, use_container_width=True)
                            st.write(f"Total vendors: {len(item['vendors'])}")
                        else:
                            st.warning("No vendors found for this item.")
            else:
                st.info(f"No items found matching '{item_search}'")
        else:
            st.warning("Please select an item to search.")
        
        # Show example searches
        with st.expander("Search Tips"):
            st.markdown("""
            **Tips for searching:**
            - Enter partial names like "Acrylic" or "End Mill"
            - Use the source filter to narrow down results
            - Click on an item to see all its details and vendors
            - Items without vendors will show a warning message
            
            **Example searches:**
            - "Acrylic" - Find all acrylic items
            - "HAAS" - Find all HAAS tooling items
            - "Tape" - Find all tape products
            """)

    
    # Close database connection when app is done
    db.close_connection()

if __name__ == "__main__":
    main()
