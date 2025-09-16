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
        # Compact navigation with a single control
        nav_choice = st.radio(
            "Go to",
            ["Dashboard", "Items", "Vendors"],
            index=["Dashboard", "Items", "Vendors"].index(st.session_state.active_tab),
            horizontal=False,
        )
        if nav_choice != st.session_state.active_tab:
            st.session_state.active_tab = nav_choice
        
        # Database connection status with detailed diagnostics (collapsed by default)
        st.markdown("---")
        with st.expander("Database connection", expanded=False):
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
                        st.warning("Firewall Issue Detected")
                        st.info(f"The IP address **{error_info['client_ip']}** is being blocked by the Azure SQL Database firewall.")
                        st.code(
                            "1. Azure Portal\n2. SQL server > Security > Networking\n3. Add rule with IP: " + str(error_info['client_ip'])
                        )
                    elif "driver_issue" in error_info:
                        st.warning("ODBC Driver Issue Detected")
                        st.info("The required ODBC driver is not installed or not found on the server.")
                        st.caption("packages.txt should include: unixodbc, unixodbc-dev")
                    elif "credential_issue" in error_info:
                        st.warning("Login Credentials Issue")
                        st.info("Verify your database credentials in Streamlit secrets.")
                
                if st.button("Show full error details"):
                    st.error(message)
        
        # Logout kept at the bottom for clarity
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
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
    """Display the simplified dashboard page"""
    st.header("Dashboard")
    st.caption("Quick overview of items and vendors. Use the navigation to manage details.")
    
    # Small KPIs for quick context
    try:
        total_boxhero = len(db.get_all_items(source_filter="BoxHero") or [])
        total_raw = len(db.get_all_items(source_filter="Raw Materials") or [])
        total_items = total_boxhero + total_raw
    except Exception:
        total_boxhero = total_raw = total_items = 0
    try:
        total_vendors = len(db.get_all_vendors() or [])
    except Exception:
        total_vendors = 0
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Items", f"{total_items}")
    kpi2.metric("BoxHero Items", f"{total_boxhero}")
    kpi3.metric("Vendors", f"{total_vendors}")
    
    # Choose dashboard mode
    mode = st.radio("View by", ["Item", "Vendor"], horizontal=True, key="dashboard_mode")
    
    if mode == "Vendor":
        # Vendor-centric view
        vendors = db.get_all_vendors() or []
        if not vendors:
            st.info("No vendors found.")
            return
        vendor_options = {v['vendor_name']: v['vendor_id'] for v in vendors}
        selected_vendor_name = st.selectbox("Select vendor", sorted(vendor_options.keys()))
        if not selected_vendor_name:
            return
        vendor_id = vendor_options[selected_vendor_name]
        items_for_vendor = db.get_vendor_items(vendor_id) or []
        if not items_for_vendor:
            st.info("This vendor does not supply any items yet.")
            return
        
        # Helper to format dimension values nicely (strip trailing zeros)
        def fmt_dim(val):
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
        
        st.subheader(f"Items supplied by {selected_vendor_name}")
        # Sort items by source then name
        items_sorted = sorted(items_for_vendor, key=lambda i: (i.get('source_sheet') or '', i.get('item_name') or ''))
        for it in items_sorted:
            # Build header with cost
            cost = it.get('vendor_cost')
            cost_text = format_currency(cost) if cost is not None else "N/A"
            if (it.get('source_sheet') == 'BoxHero'):
                sub = f"SKU: {it.get('sku') or '—'} • Barcode: {it.get('barcode') or '—'}"
            else:
                sub = f"{fmt_dim(it.get('height'))}H × {fmt_dim(it.get('width'))}W × {fmt_dim(it.get('thickness'))}T"
            header = f"{it.get('item_name')} — {cost_text}"
            with st.expander(header, expanded=False):
                left, right = st.columns(2)
                with left:
                    st.markdown(f"**Type:** {it.get('item_type') or '—'}")
                    st.markdown(f"**Source:** {it.get('source_sheet') or '—'}")
                    st.markdown(f"**Details:** {sub}")
                # We intentionally hide technical IDs in the dashboard; map_id omitted.
        st.write(f"Total items: {len(items_sorted)}")
        return
    
    # Item-centric view (existing)
    # Step 1: Select source
    source = st.radio("Select source", ["BoxHero", "Raw Materials"], horizontal=True)
    
    # Step 2: Select item by name (from chosen source)
    items = db.get_all_items(source_filter=source)
    if not items:
        st.info(f"No items found for source '{source}'.")
        return
    
    # Helper to format dimension values nicely (strip trailing zeros)
    def fmt_dim(val):
        if val is None:
            return '—'
        try:
            f = float(val)
            if f.is_integer():
                return str(int(f))
            # show up to 3 decimals, drop trailing zeros
            s = f"{f:.3f}".rstrip('0').rstrip('.')
            return s
        except Exception:
            return str(val)

    # Build disambiguated labels so items with the same name but different attributes can be selected
    def build_label(it):
        if it['source_sheet'] == "BoxHero":
            sku = it.get('sku') or '—'
            bc = it.get('barcode') or '—'
            return f"{it['item_name']}  •  SKU: {sku}  •  Barcode: {bc}"
        else:
            h = fmt_dim(it.get('height'))
            w = fmt_dim(it.get('width'))
            t = fmt_dim(it.get('thickness'))
            return f"{it['item_name']}  •  {h}H × {w}W × {t}T"

    options = {build_label(it): it['item_id'] for it in items}
    selected_label = st.selectbox("Select item by name", sorted(options.keys()))
    
    if not selected_label:
        return
    
    # Retrieve selected item by its unique ID
    selected_item_id = options[selected_label]
    item_record = next((it for it in items if it['item_id'] == selected_item_id), None)
    
    if not item_record:
        st.warning("Item not found.")
        return
    
    # Item summary (clean, not JSON)
    st.subheader("Item Details")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"**Name:** {item_record['item_name']}")
        st.markdown(f"**Type:** {item_record['item_type']}")
        st.markdown(f"**Source:** {item_record['source_sheet']}")
    with info_col2:
        if item_record['source_sheet'] == "BoxHero":
            st.markdown(f"**SKU:** {item_record.get('sku') or '—'}")
            st.markdown(f"**Barcode:** {item_record.get('barcode') or '—'}")
        else:
            h = fmt_dim(item_record.get('height'))
            w = fmt_dim(item_record.get('width'))
            t = fmt_dim(item_record.get('thickness'))
            st.markdown(f"**Height:** {h}")
            st.markdown(f"**Width:** {w}")
            st.markdown(f"**Thickness:** {t}")

    st.subheader("Vendors for this Item")
    vendors = db.get_item_vendors(item_record['item_id'])
    if vendors:
        # Sort vendors by cost (lowest first, None last)
        vendors_sorted = sorted(vendors, key=lambda v: (v['cost'] is None, v['cost']))
        st.caption("Click a vendor to view details")
        for idx, v in enumerate(vendors_sorted):
            cost_text = format_currency(v['cost']) if 'cost' in v else "N/A"
            header = f"{v['vendor_name']} — {cost_text}"
            with st.expander(header, expanded=False):
                email_link = f"mailto:{v['vendor_email']}" if v.get('vendor_email') else None
                phone_link = f"tel:{v['vendor_phone']}" if v.get('vendor_phone') else None
                
                # Left/Right columns for clean layout
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Contact**")
                    st.markdown(v.get('contact_name') or '—')
                    st.markdown("**Email**")
                    if email_link:
                        st.markdown(f"[{v['vendor_email']}]({email_link})")
                    else:
                        st.markdown("—")
                with col2:
                    st.markdown("**Phone**")
                    if phone_link:
                        st.markdown(f"[{v['vendor_phone']}]({phone_link})")
                    else:
                        st.markdown("—")
        st.write(f"Total vendors: {len(vendors_sorted)}")
    else:
        st.info("No vendors mapped to this item yet.")

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
