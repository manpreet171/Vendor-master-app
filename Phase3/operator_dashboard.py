"""
Operator Dashboard for Phase 3C
Interface for procurement team to manage bundles
"""

import streamlit as st
import json
from datetime import datetime
from db_connector import DatabaseConnector
from bundling_engine import SmartBundlingEngine

def main():
    st.set_page_config(
        page_title="Operator Dashboard - Phase 3",
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("⚙️ Operator Dashboard")
    st.caption("Bundle Management for Procurement Team")
    
    # Initialize database connection
    db = DatabaseConnector()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Bundle Overview", "Manual Bundling", "Bundle Details", "System Status"]
    )
    
    if page == "Bundle Overview":
        display_bundle_overview(db)
    elif page == "Manual Bundling":
        display_manual_bundling(db)
    elif page == "Bundle Details":
        display_bundle_details(db)
    elif page == "System Status":
        display_system_status(db)
    
    db.close_connection()

def display_bundle_overview(db):
    """Display overview of all bundles"""
    st.header("📦 Bundle Overview")
    
    try:
        # Get all bundles
        bundles = get_all_bundles(db)
        
        if not bundles:
            st.info("No bundles created yet. Use 'Manual Bundling' to create the first bundle.")
            return
        
        # Display bundles in a table format
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Bundles", len(bundles))
        
        with col2:
            active_bundles = [b for b in bundles if b['status'] == 'Active']
            st.metric("Active Bundles", len(active_bundles))
        
        with col3:
            completed_bundles = [b for b in bundles if b['status'] == 'Completed']
            st.metric("Completed Bundles", len(completed_bundles))
        
        st.markdown("---")
        
        # Display each bundle
        for bundle in bundles:
            with st.expander(f"📦 {bundle['bundle_name']} - {get_status_badge(bundle['status'])}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Created:** {bundle['created_date']}")
                    st.write(f"**Status:** {get_status_badge(bundle['status'])}")
                    st.write(f"**Total Requests:** {bundle['total_requests']}")
                    st.write(f"**Total Items:** {bundle['total_items']}")
                
                with col2:
                    # Show vendor recommendations
                    if bundle.get('vendor_info'):
                        try:
                            vendor_data = eval(bundle['vendor_info'])  # Convert string back to dict
                            if vendor_data and len(vendor_data) > 0:
                                st.write("**Top Vendor Recommendation:**")
                                top_vendor = vendor_data[0]
                                st.write(f"• {top_vendor['vendor_name']} ({top_vendor['coverage_percentage']}% coverage)")
                                st.write(f"• Contact: {top_vendor['contact_email']}")
                                st.write(f"• Items: {top_vendor['items_covered']}")
                        except:
                            st.write("**Vendor Info:** Available in details")
                
                # Action buttons
                if bundle['status'] == 'Active':
                    if st.button(f"✅ Mark as Completed", key=f"complete_{bundle['bundle_id']}"):
                        mark_bundle_completed(db, bundle['bundle_id'])
                        st.success("Bundle marked as completed!")
                        st.rerun()
    
    except Exception as e:
        st.error(f"Error loading bundles: {str(e)}")

def display_manual_bundling(db):
    """Manual bundling trigger for operators"""
    st.header("🤖 Manual Bundling")
    st.write("Trigger the smart bundling process manually")
    
    # Show current pending requests
    try:
        pending_requests = db.get_all_pending_requests()
        
        if not pending_requests:
            st.info("No pending requests available for bundling.")
            return
        
        # Group by request for display
        requests_by_id = {}
        for req in pending_requests:
            req_id = req['req_id']
            if req_id not in requests_by_id:
                requests_by_id[req_id] = {
                    'req_number': req['req_number'],
                    'user_id': req['user_id'],
                    'req_date': req['req_date'],
                    'items': []
                }
            requests_by_id[req_id]['items'].append({
                'item_name': req['item_name'],
                'quantity': req['quantity'],
                'source_sheet': req['source_sheet']
            })
        
        st.write(f"**Found {len(requests_by_id)} pending requests with {len(pending_requests)} items:**")
        
        # Display pending requests
        for req_id, req_data in requests_by_id.items():
            with st.expander(f"📋 {req_data['req_number']} - User {req_data['user_id']}", expanded=False):
                for item in req_data['items']:
                    st.write(f"• {item['item_name']} - {item['quantity']} pieces ({item['source_sheet']})")
        
        st.markdown("---")
        
        # Bundling button
        if st.button("🚀 Run Smart Bundling", type="primary"):
            with st.spinner("Running smart bundling process..."):
                engine = SmartBundlingEngine()
                result = engine.run_bundling_process()
                
                if result['success']:
                    st.success("🎉 Bundling completed successfully!")
                    
                    # Display results
                    st.write(f"**Bundle Created:** {result['bundle_name']}")
                    st.write(f"**Requests Processed:** {result['total_requests']}")
                    st.write(f"**Total Items:** {result['total_items']}")
                    
                    st.write("**Top Vendor Recommendations:**")
                    for i, vendor in enumerate(result['vendor_recommendations'][:3], 1):
                        st.write(f"{i}. **{vendor['vendor_name']}** - {vendor['coverage_percentage']}% coverage")
                        st.write(f"   • Items covered: {vendor['items_covered']}")
                        st.write(f"   • Total quantity: {vendor['total_quantity']}")
                        st.write(f"   • Contact: {vendor['contact_email']}")
                        st.write("")
                    
                    st.info("All pending requests have been moved to 'In Progress' status. Users can no longer modify these requests.")
                    
                else:
                    st.error(f"❌ Bundling failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Error in manual bundling: {str(e)}")

def display_bundle_details(db):
    """Display detailed view of a specific bundle"""
    st.header("🔍 Bundle Details")
    
    try:
        bundles = get_all_bundles(db)
        
        if not bundles:
            st.info("No bundles available.")
            return
        
        # Bundle selection
        bundle_options = [f"{b['bundle_name']} ({b['status']})" for b in bundles]
        selected_bundle_name = st.selectbox("Select a bundle:", bundle_options)
        
        if selected_bundle_name:
            # Find selected bundle
            bundle_name = selected_bundle_name.split(' (')[0]
            selected_bundle = next((b for b in bundles if b['bundle_name'] == bundle_name), None)
            
            if selected_bundle:
                # Display bundle details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Bundle ID:** {selected_bundle['bundle_id']}")
                    st.write(f"**Name:** {selected_bundle['bundle_name']}")
                    st.write(f"**Status:** {get_status_badge(selected_bundle['status'])}")
                    st.write(f"**Created:** {selected_bundle['created_date']}")
                
                with col2:
                    st.write(f"**Total Requests:** {selected_bundle['total_requests']}")
                    st.write(f"**Total Items:** {selected_bundle['total_items']}")
                
                # Show vendor recommendations
                if selected_bundle.get('vendor_info'):
                    try:
                        vendor_data = eval(selected_bundle['vendor_info'])
                        
                        st.markdown("---")
                        st.subheader("🏪 Vendor Recommendations")
                        
                        for i, vendor in enumerate(vendor_data, 1):
                            with st.expander(f"{i}. {vendor['vendor_name']} - {vendor['coverage_percentage']}% coverage"):
                                st.write(f"**Contact Email:** {vendor['contact_email']}")
                                st.write(f"**Contact Phone:** {vendor['contact_phone']}")
                                st.write(f"**Items Covered:** {vendor['items_covered']}")
                                st.write(f"**Total Quantity:** {vendor['total_quantity']}")
                                
                                st.write("**Items List:**")
                                for item in vendor['items_list']:
                                    st.write(f"• {item['item_name']} - {item['quantity']} pieces")
                    
                    except Exception as e:
                        st.write(f"Error displaying vendor info: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading bundle details: {str(e)}")

def display_system_status(db):
    """Display system status and statistics"""
    st.header("📊 System Status")
    
    try:
        # Get statistics
        pending_requests = db.get_all_pending_requests()
        bundles = get_all_bundles(db)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pending_count = len(set([req['req_id'] for req in pending_requests]))
            st.metric("Pending Requests", pending_count)
        
        with col2:
            active_bundles = [b for b in bundles if b['status'] == 'Active']
            st.metric("Active Bundles", len(active_bundles))
        
        with col3:
            completed_bundles = [b for b in bundles if b['status'] == 'Completed']
            st.metric("Completed Bundles", len(completed_bundles))
        
        with col4:
            total_items = sum(req['quantity'] for req in pending_requests)
            st.metric("Pending Items", total_items)
        
        # Database connection status
        st.markdown("---")
        st.subheader("🔗 Database Status")
        
        is_connected, message, _, _ = db.check_db_connection()
        if is_connected:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")
    
    except Exception as e:
        st.error(f"Error loading system status: {str(e)}")

def get_all_bundles(db):
    """Get all bundles from database"""
    query = """
    SELECT bundle_id, bundle_name, status, total_requests, total_items, 
           created_date, vendor_info
    FROM requirements_bundles
    ORDER BY created_date DESC
    """
    return db.execute_query(query)

def mark_bundle_completed(db, bundle_id):
    """Mark a bundle as completed and update related requests"""
    try:
        # Update bundle status
        bundle_query = """
        UPDATE requirements_bundles 
        SET status = 'Completed'
        WHERE bundle_id = ?
        """
        db.execute_insert(bundle_query, (bundle_id,))
        
        # Get all request IDs in this bundle
        mapping_query = """
        SELECT req_id FROM requirements_bundle_mapping 
        WHERE bundle_id = ?
        """
        mappings = db.execute_query(mapping_query, (bundle_id,))
        
        if mappings:
            req_ids = [mapping['req_id'] for mapping in mappings]
            
            # Update all related requests to Completed
            placeholders = ','.join(['?' for _ in req_ids])
            requests_query = f"""
            UPDATE requirements_orders 
            SET status = 'Completed'
            WHERE req_id IN ({placeholders})
            """
            db.execute_insert(requests_query, req_ids)
        
        db.conn.commit()
        return True
        
    except Exception as e:
        if db.conn:
            db.conn.rollback()
        raise Exception(f"Failed to mark bundle as completed: {str(e)}")

def get_status_badge(status):
    """Return colored status badge"""
    if status == "Active":
        return "🔵 Active"
    elif status == "Completed":
        return "🟢 Completed"
    else:
        return f"⚪ {status}"

if __name__ == "__main__":
    main()
