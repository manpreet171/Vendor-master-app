import streamlit as st
import pandas as pd
from utils import format_currency

class ItemManager:
    """Item management module for the vendor management app"""
    
    def __init__(self, db):
        """Initialize with database connector"""
        self.db = db
    
    def display_items_page(self):
        """Display the items management page"""
        st.header("Item Management")
        
        # Create tabs for viewing and managing items
        tab1, tab2, tab3, tab4 = st.tabs(["View Items", "Add Item", "Edit/Delete Item", "Incomplete Items"])
        
        with tab1:
            self._display_items_view()
        
        with tab2:
            self._display_add_item_form()
            # Render vendor assignment UI outside the form if a new item was just created
            self._render_vendor_assignment_for_new_item()
        
        with tab3:
            self._display_edit_delete_item()
        
        with tab4:
            self._display_incomplete_items()
    
    def _display_items_view(self):
        """Display the items view tab"""
        st.subheader("View Items")
        
        # Create filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Get all unique item types for filtering
            item_types_query = "SELECT DISTINCT item_type FROM Items ORDER BY item_type"
            item_types_result = self.db.fetch_data(item_types_query)
            item_types = ["All"] + [item['item_type'] for item in item_types_result] if item_types_result else ["All"]
            type_filter = st.selectbox("Filter by item type:", item_types)
        
        with col2:
            source_options = ["All", "BoxHero", "Raw Materials"]
            source_filter = st.selectbox("Filter by source:", source_options)
        
        if st.button("View Items"):
            items = self.db.get_all_items(source_filter, type_filter)
            
            if items:
                # Convert to DataFrame for better display
                df = pd.DataFrame(items)
                
                # Format cost column
                if 'cost' in df.columns:
                    df['cost'] = df['cost'].apply(lambda x: format_currency(x))
                
                st.dataframe(df, use_container_width=True)
                st.success(f"Found {len(items)} items")
                
                # Show item type distribution
                if len(items) > 0:
                    st.subheader("Item Type Distribution")
                    type_counts = pd.DataFrame(items).groupby('item_type').size().reset_index(name='count')
                    st.bar_chart(type_counts.set_index('item_type'))
            else:
                st.info("No items found matching the criteria.")
    
    def _display_add_item_form(self):
        """Display the add item form"""
        st.subheader("Add New Item")
        # If a previous action requested a form reset, clear widget keys BEFORE instantiating widgets
        if st.session_state.get('reset_add_item_form'):
            for key in [
                'item_name_input', 'item_type_input',
                'sku_input', 'barcode_input',
                'height_input', 'width_input', 'thickness_input',
                'assign_vendors_new_item', 'add_item_source_selector'
            ]:
                if key in st.session_state:
                    st.session_state.pop(key)
            st.session_state.pop('reset_add_item_form', None)
        
        # Step 1: Choose which kind of item to add (drives the form fields)
        selected_source = st.radio("Which item do you want to add?", ["BoxHero", "Raw Materials"], horizontal=True, key="add_item_source_selector")

        # Create form for adding new item
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_name = st.text_input("Item Name*", key="item_name_input")
                item_type = st.text_input("Item Type*", key="item_type_input")
                # Source comes from selection above
                source_sheet = selected_source
            
            # Initialize fields
            sku = None
            barcode = None
            height = None
            width = None
            thickness = None
            
            with col2:
                # Default cost for vendor mappings
                cost = st.number_input("Default Cost", min_value=0.0, step=0.01, format="%.2f")
            
            # Source-specific fields
            if selected_source == "BoxHero":
                with col1:
                    sku = st.text_input("SKU", key="sku_input")
                    barcode = st.text_input("Barcode", key="barcode_input")
            else:  # Raw Materials
                with col2:
                    height = st.number_input("Height", min_value=0.0, step=0.1, format="%.2f", key="height_input")
                    width = st.number_input("Width", min_value=0.0, step=0.1, format="%.2f", key="width_input")
                    thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.2f", key="thickness_input")
            
            # Convert zero values to None (only for numeric fields present)
            if height is not None:
                height = height if height > 0 else None
            if width is not None:
                width = width if width > 0 else None
            if thickness is not None:
                thickness = thickness if thickness > 0 else None
            cost = cost if cost > 0 else None
            
            submitted = st.form_submit_button("Add Item")
            
            if submitted:
                if not item_name or not item_type or not source_sheet:
                    st.error("Item Name, Item Type, and Source are required fields.")
                else:
                    # Ensure unused fields are None based on source
                    if selected_source == "BoxHero":
                        height, width, thickness = None, None, None
                    else:
                        sku, barcode = None, None
                    success, result = self.db.add_item(
                        item_name, item_type, source_sheet, sku, barcode,
                        height, width, thickness
                    )
                    
                    if success:
                        st.success(f"Item added successfully with ID: {result}")
                        # Store in session and render assignment UI outside the form
                        st.session_state.new_item_id = result
                        st.session_state.new_item_name = item_name
                    else:
                        st.error(result)
    
    def _display_edit_delete_item(self):
        """Display the edit/delete item form"""
        st.subheader("Edit or Delete Item")
        
        # Get all items for selection
        items = self.db.get_all_items()
        if not items:
            st.info("No items found in the database.")
            return
        
        # Create a dictionary for display
        item_options = {f"{item['item_name']} ({item['item_type']})": item['item_id'] for item in items}
        
        # Create a dropdown for items
        selected_item_label = st.selectbox("Select item:", list(item_options.keys()))
        selected_item_id = item_options[selected_item_label] if selected_item_label else None
        
        if selected_item_id:
            # Get item details
            item = self.db.get_item_by_id(selected_item_id)
            
            if item:
                # Create tabs for edit and delete
                edit_tab, delete_tab, vendor_tab = st.tabs(["Edit Item", "Delete Item", "View Vendors"])
                
                with edit_tab:
                    self._display_edit_item_form(item)
                
                with delete_tab:
                    self._display_delete_item_form(item)
                
                with vendor_tab:
                    self._display_item_vendors(item)
    
    def _display_edit_item_form(self, item):
        """Display form for editing an item"""
        st.subheader(f"Edit Item: {item['item_name']}")
        
        with st.form("edit_item_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                item_name = st.text_input("Item Name*", value=item['item_name'])
                item_type = st.text_input("Item Type*", value=item['item_type'])
                source_sheet = st.selectbox("Source*", ["BoxHero", "Raw Materials"], 
                                           index=0 if item['source_sheet'] == "BoxHero" else 1)
            
            # Initialize from current item
            sku_val = item['sku'] if item['sku'] else ""
            barcode_val = item['barcode'] if item['barcode'] else ""
            height_val = float(item['height']) if item['height'] else 0.0
            width_val = float(item['width']) if item['width'] else 0.0
            thickness_val = float(item['thickness']) if item['thickness'] else 0.0
            
            # Default cost (for vendor mappings)
            with col2:
                cost = st.number_input("Default Cost", min_value=0.0, step=0.01, format="%.2f", value=0.0)
            
            # Source-specific fields
            if source_sheet == "BoxHero":
                with col1:
                    sku = st.text_input("SKU", value=sku_val)
                    barcode = st.text_input("Barcode", value=barcode_val)
                # Dimensions not applicable
                height = None
                width = None
                thickness = None
            else:
                # Raw Materials
                with col2:
                    height = st.number_input("Height", min_value=0.0, step=0.1, format="%.2f", value=height_val)
                    width = st.number_input("Width", min_value=0.0, step=0.1, format="%.2f", value=width_val)
                    thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.2f", value=thickness_val)
                # SKU/Barcode not applicable
                sku = None
                barcode = None
            
            # Convert zero values to None (guard for None)
            if height is not None:
                height = height if height > 0 else None
            if width is not None:
                width = width if width > 0 else None
            if thickness is not None:
                thickness = thickness if thickness > 0 else None
            cost = cost if (cost is not None and cost > 0) else None
            
            submitted = st.form_submit_button("Update Item")
            
            if submitted:
                if not item_name or not item_type or not source_sheet:
                    st.error("Item Name, Item Type, and Source are required fields.")
                else:
                    success, message = self.db.update_item(
                        item['item_id'], item_name, item_type, source_sheet, sku, barcode,
                        height, width, thickness
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        # Inline vendor assignment for existing item
        st.subheader("Assign Vendors to this Item")
        all_vendors = self.db.get_all_vendors() or []
        if all_vendors:
            existing = self.db.get_item_vendors(item['item_id']) or []
            existing_vendor_ids = {v['vendor_id'] for v in existing}
            vendor_options = {v['vendor_name']: v['vendor_id'] for v in all_vendors if v['vendor_id'] not in existing_vendor_ids}
            if vendor_options:
                selected_vendors = st.multiselect(
                    "Select vendors to assign",
                    list(vendor_options.keys()),
                    help="You can select multiple vendors",
                    key=f"assign_vendors_{item['item_id']}"
                )
                # Per-vendor cost inputs
                vendor_costs = {}
                if selected_vendors:
                    st.caption("Enter cost per selected vendor")
                    for vn in selected_vendors:
                        vid = vendor_options[vn]
                        cost_val = st.number_input(
                            f"Cost for {vn}", min_value=0.0, step=0.01, format="%.2f",
                            key=f"cost_input_{vid}"
                        )
                        vendor_costs[vid] = cost_val
                if st.button("Create Vendor Mappings", key=f"create_mappings_edit_{item['item_id']}"):
                    created, skipped = 0, 0
                    for vn in selected_vendors:
                        vid = vendor_options[vn]
                        this_cost = vendor_costs.get(vid, 0.0)
                        ok, msg = self.db.add_mapping(item['item_id'], vid, this_cost if this_cost > 0 else None)
                        if ok:
                            created += 1
                        else:
                            skipped += 1
                    if created:
                        st.success(f"Created {created} vendor mapping(s).")
                    if skipped:
                        st.warning(f"Skipped {skipped} mapping(s) (possibly already exist).")


    def _render_vendor_assignment_for_new_item(self):
        """Render vendor assignment UI for a newly added item outside the form.
        Allows selecting multiple vendors and entering a separate cost for each.
        Uses st.session_state.new_item_id set after a successful add.
        """
        new_item_id = st.session_state.get('new_item_id')
        if not new_item_id:
            return
        st.divider()
        st.subheader("Assign Vendors to Newly Added Item")
        st.caption(f"Item ID: {new_item_id} — {st.session_state.get('new_item_name','')}")
        all_vendors = self.db.get_all_vendors() or []
        if not all_vendors:
            st.info("No vendors available to assign.")
            return
        vendor_options = {v['vendor_name']: v['vendor_id'] for v in all_vendors}
        selected_vendors = st.multiselect(
            "Select vendors to assign",
            list(vendor_options.keys()),
            help="You can select multiple vendors",
            key="assign_vendors_new_item"
        )
        # Per-vendor cost inputs
        vendor_costs = {}
        if selected_vendors:
            st.caption("Enter cost per selected vendor")
            for vn in selected_vendors:
                vid = vendor_options[vn]
                cost_val = st.number_input(
                    f"Cost for {vn}", min_value=0.0, step=0.01, format="%.2f",
                    key=f"cost_new_item_{vid}"
                )
                vendor_costs[vid] = cost_val
        if st.button("Create Vendor Mappings", key="create_mappings_new_item"):
            created, skipped = 0, 0
            for vn in selected_vendors:
                vid = vendor_options[vn]
                this_cost = vendor_costs.get(vid, 0.0)
                ok, msg = self.db.add_mapping(new_item_id, vid, this_cost if this_cost > 0 else None)
                if ok:
                    created += 1
                else:
                    skipped += 1
            if created:
                st.success(f"Created {created} vendor mapping(s).")
            if skipped:
                st.warning(f"Skipped {skipped} mapping(s) (possibly already exist).")
            # Clear session once processed
            del st.session_state['new_item_id']
            if 'new_item_name' in st.session_state:
                del st.session_state['new_item_name']
            # Defer widget clearing to next run to avoid modifying instantiated widgets
            st.session_state['reset_add_item_form'] = True
            st.rerun()

    def _display_incomplete_items(self):
        """Show items with incomplete details based on source and allow quick completion"""
        st.subheader("Incomplete Items")
        st.caption("BoxHero requires SKU and Barcode. Raw Materials require Height, Width, and Thickness.")
        data = self.db.get_incomplete_items() or {'boxhero': [], 'raw': []}

        # BoxHero section
        with st.expander("BoxHero: Missing SKU/Barcode", expanded=True):
            bh_items = data.get('boxhero', [])
            if not bh_items:
                st.success("No incomplete BoxHero items.")
            else:
                names = [f"{i['item_name']}" for i in bh_items]
                selected_name = st.selectbox("Select item", names, key="bh_incomplete_select")
                selected = next((i for i in bh_items if i['item_name'] == selected_name), None)
                if selected:
                    current = self.db.get_item_by_id(selected['item_id']) or selected
                    with st.form(f"complete_bh_{selected['item_id']}"):
                        st.write(f"Editing: {current['item_name']}")
                        sku = st.text_input("SKU", value=current.get('sku') or "")
                        barcode = st.text_input("Barcode", value=current.get('barcode') or "")
                        submitted = st.form_submit_button("Save")
                        if submitted:
                            # Keep other fields unchanged
                            ok, msg = self.db.update_item(
                                current['item_id'], current['item_name'], current['item_type'], current['source_sheet'],
                                sku, barcode, None, None, None
                            )
                            if ok:
                                st.success("Item updated.")
                            else:
                                st.error(msg)

        # Raw Materials section
        with st.expander("Raw Materials: Missing Dimensions", expanded=True):
            raw_items = data.get('raw', [])
            if not raw_items:
                st.success("No incomplete Raw Materials items.")
            else:
                names = [f"{i['item_name']}" for i in raw_items]
                selected_name = st.selectbox("Select item", names, key="raw_incomplete_select")
                selected = next((i for i in raw_items if i['item_name'] == selected_name), None)
                if selected:
                    current = self.db.get_item_by_id(selected['item_id']) or selected
                    with st.form(f"complete_raw_{selected['item_id']}"):
                        st.write(f"Editing: {current['item_name']}")
                        height = st.number_input("Height", min_value=0.0, step=0.1, format="%.2f", value=float(current['height']) if current.get('height') else 0.0)
                        width = st.number_input("Width", min_value=0.0, step=0.1, format="%.2f", value=float(current['width']) if current.get('width') else 0.0)
                        thickness = st.number_input("Thickness", min_value=0.0, step=0.1, format="%.2f", value=float(current['thickness']) if current.get('thickness') else 0.0)
                        submitted = st.form_submit_button("Save")
                        if submitted:
                            # Convert zeros to None when not set
                            height_val = height if height > 0 else None
                            width_val = width if width > 0 else None
                            thickness_val = thickness if thickness > 0 else None
                            ok, msg = self.db.update_item(
                                current['item_id'], current['item_name'], current['item_type'], current['source_sheet'],
                                None, None, height_val, width_val, thickness_val
                            )
                            if ok:
                                st.success("Item updated.")
                            else:
                                st.error(msg)


    def _display_delete_item_form(self, item):
        """Display form for deleting an item"""
        st.subheader(f"Delete Item: {item['item_name']}")
        
        st.warning("⚠️ This will delete the item and all its vendor mappings. This action cannot be undone.")
        
        # Get vendor mappings count
        vendors = self.db.get_item_vendors(item['item_id'])
        if vendors:
            st.info(f"This item has {len(vendors)} vendor mappings that will also be deleted.")
        
        if st.button("Delete Item", key="delete_item_button"):
            success, message = self.db.delete_item(item['item_id'])
            
            if success:
                st.success(message)
                st.button("Back to Item Selection", on_click=lambda: st.experimental_rerun())
            else:
                st.error(message)
    
    def _display_item_vendors(self, item):
        """Display vendors for an item"""
        st.subheader(f"Vendors for: {item['item_name']}")
        
        vendors = self.db.get_item_vendors(item['item_id'])
        
        if vendors:
            # Convert to DataFrame for better display
            df = pd.DataFrame(vendors)
            
            # Format cost column
            if 'cost' in df.columns:
                df['cost'] = df['cost'].apply(lambda x: format_currency(x))
            
            st.dataframe(df, use_container_width=True)
            # Count missing costs
            null_costs = sum(1 for v in vendors if v.get('cost') is None)
            if null_costs:
                st.warning(f"{null_costs} vendor mapping(s) have no cost. Update them below.")
            else:
                st.info(f"This item has {len(vendors)} vendors.")

            # Inline cost editor per vendor mapping
            st.subheader("Update Vendor Costs")
            for v in vendors:
                cols = st.columns([3, 2, 2, 2])
                with cols[0]:
                    st.write(f"Vendor: {v['vendor_name']}")
                with cols[1]:
                    st.write(f"Contact: {v.get('contact_name') or '—'}")
                with cols[2]:
                    new_cost = st.number_input(
                        label=f"Cost (map #{v['map_id']})",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        value=float(v['cost']) if v.get('cost') is not None else 0.0,
                        key=f"cost_input_{v['map_id']}"
                    )
                with cols[3]:
                    if st.button("Save", key=f"save_cost_{v['map_id']}"):
                        cost_val = new_cost if new_cost > 0 else None
                        ok, msg = self.db.update_mapping(v['map_id'], cost_val)
                        if ok:
                            st.success("Saved")
                        else:
                            st.error(msg)
        else:
            st.warning("This item has no vendor mappings.")
            
            # Option to add vendor mappings
            all_vendors = self.db.get_all_vendors() or []
            if all_vendors:
                vendor_options = {v['vendor_name']: v['vendor_id'] for v in all_vendors}
                selected_vendors = st.multiselect("Select vendors to assign", list(vendor_options.keys()), key=f"add_map_{item['item_id']}")
                assign_cost = st.number_input("Cost (applied to all selected vendors)", min_value=0.0, step=0.01, format="%.2f", key=f"cost_add_map_{item['item_id']}")
                if st.button("Create Vendor Mappings", key=f"create_map_btn_{item['item_id']}"):
                    created, skipped = 0, 0
                    for vn in selected_vendors:
                        ok, msg = self.db.add_mapping(item['item_id'], vendor_options[vn], assign_cost if assign_cost > 0 else None)
                        if ok:
                            created += 1
                        else:
                            skipped += 1
                    if created:
                        st.success(f"Created {created} vendor mapping(s).")
                    if skipped:
                        st.warning(f"Skipped {skipped} mapping(s) (possibly already exist).")
