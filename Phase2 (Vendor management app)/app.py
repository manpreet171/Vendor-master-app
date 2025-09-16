import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
from db_connector import DatabaseConnector
from item_manager import ItemManager
from vendor_manager import VendorManager
from utils import apply_custom_css, format_currency

def main():
    """Main function for the vendor management app"""
    st.set_page_config(
        page_title="Vendor Management System",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load environment variables from .env in this folder (for local/dev)
    load_dotenv()

    # Login gate
    def require_login():
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if not st.session_state.logged_in:
            st.title("Login")
            st.caption("Please enter your credentials to continue.")
            with st.form("login_form"):
                user = st.text_input("Username", key="login_user")
                pwd = st.text_input("Password", type="password", key="login_pass")
                submitted = st.form_submit_button("Login")
                if submitted:
                    # Prefer Streamlit secrets, then environment variables
                    sec = getattr(st, 'secrets', None)
                    if sec and 'APP_USER' in sec and 'APP_PASSWORD' in sec:
                        env_user = str(sec.get('APP_USER'))
                        env_pass = str(sec.get('APP_PASSWORD'))
                    else:
                        env_user = os.getenv("APP_USER")
                        env_pass = os.getenv("APP_PASSWORD")
                    # Trim whitespace to handle entries like 'APP_USER= admin' in .env or secrets
                    u_ok = env_user is not None and user.strip() == str(env_user).strip()
                    p_ok = env_pass is not None and pwd == str(env_pass)
                    if u_ok and p_ok:
                        st.session_state.logged_in = True
                        st.success("Logged in successfully.")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Contact admin if you need access.")
            st.stop()

    require_login()
    
    # Apply custom CSS
    apply_custom_css()
    
    # App title
    st.title("Vendor Management System")
    
    # Initialize session state for active tab if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Dashboard"
    
    # Initialize database connection
    try:
        db = DatabaseConnector()
    except Exception as e:
        st.error(f"Failed to initialize database connector: {str(e)}")
        st.stop()
    
    # Create sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        
        # Navigation buttons
        if st.button("Dashboard", use_container_width=True):
            st.session_state.active_tab = "Dashboard"
        
        if st.button("Items", use_container_width=True):
            st.session_state.active_tab = "Items"
        
        if st.button("Vendors", use_container_width=True):
            st.session_state.active_tab = "Vendors"
        
        
        
        # Database connection status with detailed diagnostics
        st.markdown("---")
        st.subheader("Database Connection")
        
        # Check database connection with detailed error info
        is_connected, message, connection_details, error_info = db.check_db_connection()
        
        if is_connected:
            st.success("✅ Connected to database")
            if st.checkbox("Show connection details"):
                st.json(connection_details)
        else:
            st.error(f"❌ {message.split(':')[0]}")
            
            # Display helpful error information
            if error_info:
                if "firewall_issue" in error_info:
                    st.warning(f"⚠️ **Firewall Issue Detected**")
                    st.info(f"The IP address **{error_info['client_ip']}** is being blocked by the Azure SQL Database firewall.")
                    st.info("**Solution:** Add this IP to your Azure SQL Database firewall rules:")
                    st.code(f"1. Go to Azure Portal\n2. Navigate to your SQL server\n3. Go to 'Security' > 'Networking'\n4. Add rule with IP: {error_info['client_ip']}")
                
                elif "driver_issue" in error_info:
                    st.warning("⚠️ **ODBC Driver Issue Detected**")
                    st.info("The required ODBC driver is not installed or not found on the server.")
                    st.info("**Solution:** Make sure the packages.txt file includes unixodbc and unixodbc-dev.")
                
                elif "credential_issue" in error_info:
                    st.warning("⚠️ **Login Credentials Issue**")
                    st.info("The username or password provided is incorrect.")
                    st.info("**Solution:** Verify your database credentials in Streamlit secrets.")
                
                # Show full error details if needed
                if st.button("Show Full Error Details"):
                    st.error(message)
        
        # Logout
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            for k in [
                'login_user','login_pass','dashboard_mode','add_item_source_selector',
                'item_name_input','item_type_input','sku_input','barcode_input',
                'height_input','width_input','thickness_input','assign_vendors_new_item',
                'new_item_id','new_item_name','reset_add_item_form'
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    
    # Main content based on active tab
    if st.session_state.active_tab == "Dashboard":
        display_dashboard(db)
    
    elif st.session_state.active_tab == "Items":
        item_manager = ItemManager(db)
        item_manager.display_items_page()
    
    elif st.session_state.active_tab == "Vendors":
        vendor_manager = VendorManager(db)
        vendor_manager.display_vendors_page()
    
    
    
    # Close database connection when app is done
    db.close_connection()

def display_dashboard(db):
    """Display the clean, step-by-step dashboard"""
    st.header("Dashboard")
    
    # Initialize session state for dashboard flow
    if 'dashboard_step' not in st.session_state:
        st.session_state.dashboard_step = 1
    if 'selected_source' not in st.session_state:
        st.session_state.selected_source = None
    if 'selected_item_id' not in st.session_state:
        st.session_state.selected_item_id = None
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = None
    
    # Step 1: Choose view mode (Item-centric or Vendor-centric)
    if st.session_state.dashboard_step == 1:
        st.subheader("What would you like to explore?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Find Items by Source", use_container_width=True, help="Browse items from BoxHero or Raw Materials"):
                st.session_state.view_mode = "item"
                st.session_state.dashboard_step = 2
                st.rerun()
        
        with col2:
            if st.button("🏢 Browse by Vendor", use_container_width=True, help="See what items each vendor supplies"):
                st.session_state.view_mode = "vendor"
                st.session_state.dashboard_step = 2
                st.rerun()
        
        st.info("💡 Choose how you'd like to explore your inventory and vendor relationships")
        return
    
    # Back button for all subsequent steps
    if st.button("← Back", key="back_button"):
        if st.session_state.dashboard_step > 1:
            st.session_state.dashboard_step -= 1
            if st.session_state.dashboard_step == 1:
                st.session_state.view_mode = None
                st.session_state.selected_source = None
                st.session_state.selected_item_id = None
            elif st.session_state.dashboard_step == 2 and st.session_state.view_mode == "item":
                st.session_state.selected_source = None
                st.session_state.selected_item_id = None
            st.rerun()
    
    # Vendor-centric flow
    if st.session_state.view_mode == "vendor":
        display_vendor_flow(db)
        return
    
    # Item-centric flow
    if st.session_state.view_mode == "item":
        display_item_flow(db)
        return

def display_vendor_flow(db):
    """Clean vendor-centric flow"""
    st.subheader("🏢 Browse by Vendor")
    
    vendors = db.get_all_vendors() or []
    if not vendors:
        st.warning("No vendors found in the system.")
        st.info("💡 Add vendors in the 'Vendors' tab to see them here.")
        return
    
    # Step 2: Select vendor
    vendor_options = {v['vendor_name']: v['vendor_id'] for v in vendors}
    selected_vendor_name = st.selectbox(
        "Choose a vendor to see their supplied items:",
        options=[""] + sorted(vendor_options.keys()),
        key="vendor_selector"
    )
    
    if not selected_vendor_name:
        st.info("👆 Select a vendor from the dropdown above")
        return
    
    vendor_id = vendor_options[selected_vendor_name]
    items_for_vendor = db.get_vendor_items(vendor_id) or []
    
    if not items_for_vendor:
        st.info(f"📦 {selected_vendor_name} doesn't supply any items yet.")
        st.info("💡 Add item-vendor mappings in the 'Items' tab.")
        return
    
    # Display vendor's items
    display_vendor_items(selected_vendor_name, items_for_vendor)

def display_item_flow(db):
    """Clean item-centric flow"""
    st.subheader("🔍 Find Items by Source")
    
    # Step 2: Select source
    if st.session_state.dashboard_step == 2:
        st.markdown("**Step 1: Choose your data source**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📦 BoxHero Items", use_container_width=True, help="Items from BoxHero inventory system"):
                st.session_state.selected_source = "BoxHero"
                st.session_state.dashboard_step = 3
                st.rerun()
        
        with col2:
            if st.button("🔧 Raw Materials", use_container_width=True, help="Raw materials and components"):
                st.session_state.selected_source = "Raw Materials"
                st.session_state.dashboard_step = 3
                st.rerun()
        
        st.info("💡 Select the source of items you want to explore")
        return
    
    # Step 3: Select specific item
    if st.session_state.dashboard_step == 3:
        st.markdown(f"**Step 2: Choose an item from {st.session_state.selected_source}**")
        
        items = db.get_all_items(source_filter=st.session_state.selected_source)
        if not items:
            st.warning(f"No items found for source '{st.session_state.selected_source}'.")
            st.info("💡 Add items in the 'Items' tab to see them here.")
            return
        
        # Build clean item labels
        item_options = {}
        for item in items:
            if item['source_sheet'] == "BoxHero":
                sku = item.get('sku') or '—'
                bc = item.get('barcode') or '—'
                label = f"{item['item_name']} (SKU: {sku})"
            else:
                h = fmt_dim(item.get('height'))
                w = fmt_dim(item.get('width'))
                t = fmt_dim(item.get('thickness'))
                label = f"{item['item_name']} ({h}H × {w}W × {t}T)"
            item_options[label] = item['item_id']
        
        selected_label = st.selectbox(
            "Choose an item:",
            options=[""] + sorted(item_options.keys()),
            key="item_selector"
        )
        
        if not selected_label:
            st.info("👆 Select an item from the dropdown above")
            return
        
        st.session_state.selected_item_id = item_options[selected_label]
        st.session_state.dashboard_step = 4
        st.rerun()
    
    # Step 4: Display item details and vendors
    if st.session_state.dashboard_step == 4:
        display_item_details(db)

def display_item_details(db):
    """Display detailed item information and vendors"""
    items = db.get_all_items(source_filter=st.session_state.selected_source)
    item_record = next((it for it in items if it['item_id'] == st.session_state.selected_item_id), None)
    
    if not item_record:
        st.error("Item not found.")
        return
    
    # Item summary
    st.markdown("**📋 Item Details**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {item_record['item_name']}")
        st.markdown(f"**Type:** {item_record['item_type']}")
        st.markdown(f"**Source:** {item_record['source_sheet']}")
    
    with col2:
        if item_record['source_sheet'] == "BoxHero":
            st.markdown(f"**SKU:** {item_record.get('sku') or '—'}")
            st.markdown(f"**Barcode:** {item_record.get('barcode') or '—'}")
        else:
            h = fmt_dim(item_record.get('height'))
            w = fmt_dim(item_record.get('width'))
            t = fmt_dim(item_record.get('thickness'))
            st.markdown(f"**Dimensions:** {h}H × {w}W × {t}T")
    
    st.markdown("---")
    
    # Vendors section
    st.markdown("**🏢 Available Vendors**")
    vendors = db.get_item_vendors(item_record['item_id'])
    
    if vendors:
        vendors_sorted = sorted(vendors, key=lambda v: (v['cost'] is None, v['cost']))
        
        for idx, v in enumerate(vendors_sorted):
            cost_text = format_currency(v['cost']) if 'cost' in v else "N/A"
            
            with st.expander(f"{v['vendor_name']} — {cost_text}", expanded=idx == 0):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Contact:** {v.get('contact_name') or '—'}")
                    if v.get('vendor_email'):
                        st.markdown(f"**Email:** [{v['vendor_email']}](mailto:{v['vendor_email']})")
                    else:
                        st.markdown("**Email:** —")
                with col2:
                    if v.get('vendor_phone'):
                        st.markdown(f"**Phone:** [{v['vendor_phone']}](tel:{v['vendor_phone']})")
                    else:
                        st.markdown("**Phone:** —")
        
        st.success(f"✅ Found {len(vendors_sorted)} vendor(s) for this item")
    else:
        st.info("📭 No vendors mapped to this item yet.")
        st.info("💡 Add vendor mappings in the 'Items' tab.")

def display_vendor_items(vendor_name, items_for_vendor):
    """Display items supplied by a vendor"""
    st.markdown(f"**📦 Items supplied by {vendor_name}**")
    
    # Sort items by source then name
    items_sorted = sorted(items_for_vendor, key=lambda i: (i.get('source_sheet') or '', i.get('item_name') or ''))
    
    for idx, item in enumerate(items_sorted):
        cost = item.get('vendor_cost')
        cost_text = format_currency(cost) if cost is not None else "N/A"
        
        if item.get('source_sheet') == 'BoxHero':
            details = f"SKU: {item.get('sku') or '—'} • Barcode: {item.get('barcode') or '—'}"
        else:
            details = f"{fmt_dim(item.get('height'))}H × {fmt_dim(item.get('width'))}W × {fmt_dim(item.get('thickness'))}T"
        
        with st.expander(f"{item.get('item_name')} — {cost_text}", expanded=idx == 0):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Type:** {item.get('item_type') or '—'}")
                st.markdown(f"**Source:** {item.get('source_sheet') or '—'}")
            with col2:
                st.markdown(f"**Details:** {details}")
    
    st.success(f"✅ {vendor_name} supplies {len(items_sorted)} item(s)")

def fmt_dim(val):
    """Helper to format dimension values nicely"""
    if val is None:
        return '—'
    try:
        f = float(val)
        if f.is_integer():
            return str(int(f))
        s = f"{f:.3f}".rstrip('0').rstrip('.')
        return s
    except Exception:
        return str(val)

def display_validation_page(db):
    """Display the data validation page"""
    st.header("Data Validation")
    
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
                
                # Option to map these items
                if st.button("Map Unmapped Items"):
                    st.session_state.active_tab = "Mappings"
                    st.experimental_rerun()
            else:
                st.success("All items have at least one vendor mapping.")
            
            # Check for duplicate mappings
            st.subheader("Duplicate Item-Vendor Mappings")
            if validation_results['duplicate_mappings']:
                st.dataframe(pd.DataFrame(validation_results['duplicate_mappings']), use_container_width=True)
                st.error(f"Found {len(validation_results['duplicate_mappings'])} duplicate item-vendor mappings.")
            else:
                st.success("No duplicate item-vendor mappings found.")
            
            # Show vendor counts per item
            st.subheader("Vendor Distribution")
            st.write(f"Items with single vendor: {validation_results['single_vendor_items']}")
            st.write(f"Items with multiple vendors: {validation_results['multi_vendor_items']}")
            
            # Show examples of multi-vendor items
            if 'multi_vendor_examples' in validation_results and validation_results['multi_vendor_examples']:
                st.subheader("Examples of Items with Multiple Vendors")
                for example in validation_results['multi_vendor_examples']:
                    with st.expander(f"{example['item_name']} ({len(example['vendors'])} vendors)"):
                        vendors_df = pd.DataFrame(example['vendors'])
                        # Format cost column
                        if 'cost' in vendors_df.columns:
                            vendors_df['cost'] = vendors_df['cost'].apply(lambda x: f"${x:.2f}" if x else "N/A")
                        st.dataframe(vendors_df, use_container_width=True)

if __name__ == "__main__":
    main()
