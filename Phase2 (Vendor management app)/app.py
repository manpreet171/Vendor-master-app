import streamlit as st
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
    
    # Apply custom CSS
    apply_custom_css()
    
    # App title
    st.title("Vendor Management System")
    
    # Initialize session state for active tab if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Dashboard"
    
    # Initialize database connection
    db = DatabaseConnector()
    
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
        
        
        
        # Display current database connection (simple status only)
        st.markdown("---")
        st.subheader("Database Connection")
        if getattr(db, 'conn', None):
            st.success("Connected")
        else:
            st.error("Not connected")
    
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
    """Simple dashboard: select source -> select item -> show item details and vendors"""
    st.header("Dashboard")
    
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
