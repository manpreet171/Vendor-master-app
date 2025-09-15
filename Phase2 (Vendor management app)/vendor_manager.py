import streamlit as st
import pandas as pd

class VendorManager:
    """Vendor management module for the vendor management app"""
    
    def __init__(self, db):
        """Initialize with database connector"""
        self.db = db
    
    def display_vendors_page(self):
        """Display the vendors management page"""
        st.header("Vendor Management")
        
        # Create tabs for viewing and managing vendors
        tab1, tab2, tab3, tab4 = st.tabs(["View Vendors", "Add Vendor", "Edit/Delete Vendor", "Incomplete Vendors"])
        
        with tab1:
            self._display_vendors_view()
        
        with tab2:
            self._display_add_vendor_form()
        
        with tab3:
            self._display_edit_delete_vendor()

        with tab4:
            self._display_incomplete_vendors()
    
    def _display_vendors_view(self):
        """Display the vendors view tab"""
        st.subheader("View Vendors")
        
        if st.button("View All Vendors"):
            vendors = self.db.get_all_vendors()
            
            if vendors:
                # Convert to DataFrame for better display
                df = pd.DataFrame(vendors)
                st.dataframe(df, use_container_width=True)
                st.success(f"Found {len(vendors)} vendors")
            else:
                st.info("No vendors found in the database.")
    
    def _display_add_vendor_form(self):
        """Display the add vendor form"""
        st.subheader("Add New Vendor")
        
        # Create form for adding new vendor
        with st.form("add_vendor_form"):
            vendor_name = st.text_input("Vendor Name*")
            contact_name = st.text_input("Contact Name")
            vendor_email = st.text_input("Email")
            vendor_phone = st.text_input("Phone")
            
            submitted = st.form_submit_button("Add Vendor")
            
            if submitted:
                if not vendor_name:
                    st.error("Vendor Name is a required field.")
                else:
                    success, message = self.db.add_vendor(
                        vendor_name, contact_name, vendor_email, vendor_phone
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    def _display_edit_delete_vendor(self):
        """Display the edit/delete vendor form"""
        st.subheader("Edit or Delete Vendor")
        
        # Get all vendors for selection
        vendors = self.db.get_all_vendors()
        if not vendors:
            st.info("No vendors found in the database.")
            return
        
        # Create a dictionary for display
        vendor_options = {vendor['vendor_name']: vendor['vendor_id'] for vendor in vendors}
        
        # Create a dropdown for vendors
        selected_vendor = st.selectbox("Select vendor:", list(vendor_options.keys()))
        selected_vendor_id = vendor_options[selected_vendor] if selected_vendor else None
        
        if selected_vendor_id:
            # Get vendor details
            vendor = self.db.get_vendor_by_id(selected_vendor_id)
            
            if vendor:
                # Create tabs for edit and delete
                edit_tab, delete_tab, items_tab = st.tabs(["Edit Vendor", "Delete Vendor", "View Items"])
                
                with edit_tab:
                    self._display_edit_vendor_form(vendor)
                
                with delete_tab:
                    self._display_delete_vendor_form(vendor)
                
                with items_tab:
                    self._display_vendor_items(vendor)
    
    def _display_edit_vendor_form(self, vendor):
        """Display form for editing a vendor"""
        st.subheader(f"Edit Vendor: {vendor['vendor_name']}")
        
        with st.form("edit_vendor_form"):
            vendor_name = st.text_input("Vendor Name*", value=vendor['vendor_name'])
            contact_name = st.text_input("Contact Name", value=vendor['contact_name'] if vendor['contact_name'] else "")
            vendor_email = st.text_input("Email", value=vendor['vendor_email'] if vendor['vendor_email'] else "")
            vendor_phone = st.text_input("Phone", value=vendor['vendor_phone'] if vendor['vendor_phone'] else "")
            
            submitted = st.form_submit_button("Update Vendor")
            
            if submitted:
                if not vendor_name:
                    st.error("Vendor Name is a required field.")
                else:
                    success, message = self.db.update_vendor(
                        vendor['vendor_id'], vendor_name, contact_name, vendor_email, vendor_phone
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    def _display_delete_vendor_form(self, vendor):
        """Display form for deleting a vendor"""
        st.subheader(f"Delete Vendor: {vendor['vendor_name']}")
        
        st.warning("⚠️ This will delete the vendor and all its item mappings. This action cannot be undone.")
        
        # Get item mappings count
        items = self.db.get_vendor_items(vendor['vendor_id'])
        if items:
            st.info(f"This vendor has {len(items)} item mappings that will also be deleted.")
        
        if st.button("Delete Vendor", key="delete_vendor_button"):
            success, message = self.db.delete_vendor(vendor['vendor_id'])
            
            if success:
                st.success(message)
                st.button("Back to Vendor Selection", on_click=lambda: st.experimental_rerun())
            else:
                st.error(message)
    
    def _display_vendor_items(self, vendor):
        """Display items for a vendor"""
        st.subheader(f"Items supplied by: {vendor['vendor_name']}")
        
        items = self.db.get_vendor_items(vendor['vendor_id'])
        
        if items:
            # Convert to DataFrame for better display
            df = pd.DataFrame(items)
            
            # Format cost column
            if 'vendor_cost' in df.columns:
                df['vendor_cost'] = df['vendor_cost'].apply(lambda x: f"${x:.2f}" if x is not None else "N/A")
            
            st.dataframe(df, use_container_width=True)
            st.info(f"This vendor supplies {len(items)} items.")
        else:
            st.warning("This vendor has no item mappings.")
            
            # Option to add item mappings
            if st.button("Add Item Mappings"):
                st.session_state.selected_vendor_id = vendor['vendor_id']
                st.session_state.active_tab = "Mappings"
                st.experimental_rerun()

    def _display_incomplete_vendors(self):
        """Show vendors with incomplete details and allow quick update"""
        st.subheader("Vendors with Incomplete Details")
        vendors = self.db.get_incomplete_vendors() or []
        if not vendors:
            st.success("All vendors have complete details. 🎉")
            return
        
        # Simple list + select to edit
        st.caption("These vendors are missing a contact name, email, or phone.")
        names = [v['vendor_name'] for v in vendors]
        selected_name = st.selectbox("Select a vendor to complete details", names)
        selected = next((v for v in vendors if v['vendor_name'] == selected_name), None)
        
        if not selected:
            return
        
        with st.form("complete_vendor_form"):
            st.write(f"Editing: {selected['vendor_name']}")
            contact_name = st.text_input("Contact Name", value=selected.get('contact_name') or "")
            vendor_email = st.text_input("Email", value=selected.get('vendor_email') or "")
            vendor_phone = st.text_input("Phone", value=selected.get('vendor_phone') or "")
            submitted = st.form_submit_button("Save Details")
            if submitted:
                # Keep the name; update other fields
                success, msg = self.db.update_vendor(
                    selected['vendor_id'], selected['vendor_name'], contact_name, vendor_email, vendor_phone
                )
                if success:
                    st.success("Vendor details updated.")
                else:
                    st.error(msg)
