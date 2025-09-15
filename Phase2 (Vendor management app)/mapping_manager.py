import streamlit as st
import pandas as pd
from utils import format_currency

class MappingManager:
    """Mapping management module for the vendor management app"""
    
    def __init__(self, db):
        """Initialize with database connector"""
        self.db = db
    
    def display_mappings_page(self):
        """Display the mappings management page"""
        st.header("Item-Vendor Mapping Management")
        
        # Create tabs for different mapping operations
        tab1, tab2, tab3, tab4 = st.tabs([
            "View Mappings", 
            "Add Mapping", 
            "Edit Mapping",
            "Find Unmapped Items"
        ])
        
        with tab1:
            self._display_mappings_view()
        
        with tab2:
            self._display_add_mapping_form()
        
        with tab3:
            self._display_edit_mapping_form()
            
        with tab4:
            self._display_unmapped_items()
    
    def _display_mappings_view(self):
        """Display the mappings view tab"""
        st.subheader("View Item-Vendor Mappings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get all unique item types for filtering
            item_types_query = "SELECT DISTINCT item_type FROM Items ORDER BY item_type"
            item_types_result = self.db.fetch_data(item_types_query)
            item_types = ["All"] + [item['item_type'] for item in item_types_result] if item_types_result else ["All"]
            type_filter = st.selectbox("Filter by item type:", item_types, key="mapping_type_filter")
        
        with col2:
            # Get all unique vendors for filtering
            vendors_query = "SELECT DISTINCT vendor_name FROM Vendors ORDER BY vendor_name"
            vendors_result = self.db.fetch_data(vendors_query)
            vendors = ["All"] + [v['vendor_name'] for v in vendors_result] if vendors_result else ["All"]
            vendor_filter = st.selectbox("Filter by vendor:", vendors)
        
        if st.button("View Item-Vendor Mappings"):
            # Build query based on filters
            query_parts = ["""
                SELECT i.item_name, i.item_type, v.vendor_name, m.cost, i.source_sheet,
                       i.height, i.width, i.thickness, m.map_id
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
            
            query_parts.append("ORDER BY i.item_name, v.vendor_name")
            query = " ".join(query_parts)
            
            # Execute query
            mappings = self.db.fetch_data(query, params)
            
            if mappings:
                # Convert to DataFrame for better display
                df = pd.DataFrame(mappings)
                
                # Format cost column
                if 'cost' in df.columns:
                    df['cost'] = df['cost'].apply(lambda x: format_currency(x))
                
                st.dataframe(df, use_container_width=True)
                st.success(f"Found {len(mappings)} item-vendor mappings")
                
                # Show mapping statistics
                st.subheader("Mapping Statistics")
                
                # Count mappings by item type
                if 'item_type' in df.columns:
                    type_counts = df.groupby('item_type').size().reset_index(name='count')
                    st.write("Mappings by Item Type:")
                    st.bar_chart(type_counts.set_index('item_type'))
            else:
                st.info("No mappings found matching the criteria.")
    
    def _display_add_mapping_form(self):
        """Display the add mapping form"""
        st.subheader("Add New Item-Vendor Mapping")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get all items for selection
            items = self.db.get_all_items()
            if not items:
                st.info("No items found in the database.")
                return
            
            # Create a dictionary for display
            item_options = {f"{item['item_name']} ({item['item_type']})": item['item_id'] for item in items}
            
            # Create a dropdown for items
            selected_item_label = st.selectbox("Select item:", list(item_options.keys()), key="add_mapping_item")
            selected_item_id = item_options[selected_item_label] if selected_item_label else None
        
        with col2:
            # Get all vendors for selection
            vendors = self.db.get_all_vendors()
            if not vendors:
                st.info("No vendors found in the database.")
                return
            
            # Create a dictionary for display
            vendor_options = {vendor['vendor_name']: vendor['vendor_id'] for vendor in vendors}
            
            # Create a dropdown for vendors
            selected_vendor = st.selectbox("Select vendor:", list(vendor_options.keys()), key="add_mapping_vendor")
            selected_vendor_id = vendor_options[selected_vendor] if selected_vendor else None
        
        # Cost input
        cost = st.number_input("Cost (optional):", min_value=0.0, step=0.01, format="%.2f")
        cost = cost if cost > 0 else None
        
        if st.button("Add Mapping"):
            if not selected_item_id or not selected_vendor_id:
                st.error("Both item and vendor must be selected.")
            else:
                # Check if mapping already exists
                check_query = "SELECT map_id FROM ItemVendorMap WHERE item_id = ? AND vendor_id = ?"
                existing = self.db.fetch_data(check_query, [selected_item_id, selected_vendor_id])
                
                if existing:
                    st.error("This mapping already exists!")
                else:
                    # Add mapping
                    success, message = self.db.add_mapping(selected_item_id, selected_vendor_id, cost)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    def _display_edit_mapping_form(self):
        """Display the edit mapping form"""
        st.subheader("Edit Item-Vendor Mapping")
        
        # First, let user select an item
        items = self.db.get_all_items()
        if not items:
            st.info("No items found in the database.")
            return
        
        # Create a dictionary for display
        item_options = {f"{item['item_name']} ({item['item_type']})": item['item_id'] for item in items}
        
        # Create a dropdown for items
        selected_item_label = st.selectbox("Select item:", list(item_options.keys()), key="edit_mapping_item")
        selected_item_id = item_options[selected_item_label] if selected_item_label else None
        
        if selected_item_id:
            # Get vendors for this item
            vendors = self.db.get_item_vendors(selected_item_id)
            
            if not vendors:
                st.warning("This item has no vendor mappings.")
                return
            
            # Create a dictionary for display
            mapping_options = {f"{v['vendor_name']}": v['map_id'] for v in vendors}
            
            # Create a dropdown for vendors
            selected_mapping_label = st.selectbox("Select vendor mapping:", list(mapping_options.keys()))
            selected_map_id = mapping_options[selected_mapping_label] if selected_mapping_label else None
            
            if selected_map_id:
                # Find the selected mapping
                selected_mapping = next((v for v in vendors if v['map_id'] == selected_map_id), None)
                
                if selected_mapping:
                    # Show current cost
                    current_cost = selected_mapping['cost']
                    st.info(f"Current cost: {format_currency(current_cost)}")
                    
                    # New cost input
                    new_cost = st.number_input("New cost:", min_value=0.0, step=0.01, format="%.2f", 
                                             value=float(current_cost) if current_cost else 0.0)
                    new_cost = new_cost if new_cost > 0 else None
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Update Cost"):
                            success, message = self.db.update_mapping(selected_map_id, new_cost)
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                    
                    with col2:
                        if st.button("Delete Mapping"):
                            success, message = self.db.delete_mapping(selected_map_id)
                            
                            if success:
                                st.success(message)
                                st.button("Back to Item Selection", on_click=lambda: st.experimental_rerun())
                            else:
                                st.error(message)
    
    def _display_unmapped_items(self):
        """Display unmapped items"""
        st.subheader("Find Unmapped Items")
        
        if st.button("Show Unmapped Items"):
            # Get unmapped items
            unmapped_query = """
                SELECT i.item_id, i.item_name, i.item_type, i.source_sheet
                FROM Items i
                LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
                WHERE m.map_id IS NULL
                ORDER BY i.item_name
            """
            unmapped_items = self.db.fetch_data(unmapped_query)
            
            if unmapped_items:
                # Convert to DataFrame for better display
                df = pd.DataFrame(unmapped_items)
                st.dataframe(df, use_container_width=True)
                st.warning(f"Found {len(unmapped_items)} items without any vendor mappings.")
                
                # Option to map items
                st.subheader("Map Unmapped Item")
                
                # Create a dictionary for display
                item_options = {f"{item['item_name']} ({item['item_type']})": item['item_id'] for item in unmapped_items}
                
                # Create a dropdown for items
                selected_item_label = st.selectbox("Select unmapped item:", list(item_options.keys()))
                selected_item_id = item_options[selected_item_label] if selected_item_label else None
                
                if selected_item_id:
                    # Get all vendors
                    vendors = self.db.get_all_vendors()
                    
                    if vendors:
                        # Create a dictionary for display
                        vendor_options = {vendor['vendor_name']: vendor['vendor_id'] for vendor in vendors}
                        
                        # Create a dropdown for vendors
                        selected_vendor = st.selectbox("Select vendor:", list(vendor_options.keys()))
                        selected_vendor_id = vendor_options[selected_vendor] if selected_vendor else None
                        
                        # Cost input
                        cost = st.number_input("Cost (optional):", min_value=0.0, step=0.01, format="%.2f")
                        cost = cost if cost > 0 else None
                        
                        if st.button("Create Mapping"):
                            if selected_item_id and selected_vendor_id:
                                success, message = self.db.add_mapping(selected_item_id, selected_vendor_id, cost)
                                
                                if success:
                                    st.success(message)
                                    st.button("Refresh Unmapped Items", on_click=lambda: st.experimental_rerun())
                                else:
                                    st.error(message)
            else:
                st.success("All items have at least one vendor mapping.")
