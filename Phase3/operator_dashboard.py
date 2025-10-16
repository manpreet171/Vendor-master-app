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
        ["Bundle Overview", "Manual Bundling", "Bundle Details", "System Status", "User Management"]
    )
    
    if page == "Bundle Overview":
        display_bundle_overview(db)
    elif page == "Manual Bundling":
        display_manual_bundling(db)
    elif page == "Bundle Details":
        display_bundle_details(db)
    elif page == "System Status":
        display_system_status(db)
    elif page == "User Management":
        display_user_management(db)
    
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
            # Show rejection warning OUTSIDE expander if bundle was rejected by Operation Team
            if bundle['status'] == 'Active' and bundle.get('rejection_reason'):
                # Format rejected_at datetime
                rejected_date = bundle.get('rejected_at')
                if rejected_date and hasattr(rejected_date, 'strftime'):
                    rejected_str = rejected_date.strftime('%Y-%m-%d %H:%M')
                else:
                    rejected_str = str(rejected_date) if rejected_date else 'N/A'
                
                st.error(f"🚨 **BUNDLE REJECTED BY OPERATION TEAM** - {bundle['bundle_name']}")
                st.markdown(f"""
                <div style='background-color: #ffebee; padding: 20px; border-radius: 8px; border-left: 6px solid #f44336; margin-bottom: 15px;'>
                    <p style='margin: 0; color: #c62828; font-size: 16px;'><strong>❌ Rejected on:</strong> {rejected_str}</p>
                    <p style='margin: 10px 0; color: #c62828; font-size: 16px;'><strong>📝 Reason:</strong> {bundle.get('rejection_reason', 'No reason provided')}</p>
                    <p style='margin: 10px 0 0 0; color: #d32f2f; font-size: 14px; font-weight: 600;'>
                        ⚠️ <strong>ACTION REQUIRED:</strong> Please rectify the issues mentioned above, make necessary changes, 
                        and re-review this bundle before submitting again.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Add REJECTED indicator to expander title if rejected
            expander_title = f"📦 {bundle['bundle_name']} - {get_status_badge(bundle['status'])}"
            if bundle['status'] == 'Active' and bundle.get('rejection_reason'):
                expander_title = f"🚨 REJECTED - {bundle['bundle_name']} - {get_status_badge(bundle['status'])}"
            
            with st.expander(expander_title, expanded=False):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Format created_at datetime
                    created_date = bundle.get('created_at')
                    if created_date and hasattr(created_date, 'strftime'):
                        created_str = created_date.strftime('%Y-%m-%d %H:%M')
                    else:
                        created_str = str(created_date) if created_date else 'N/A'
                    
                    st.write(f"**Created:** {created_str}")
                    st.write(f"**Status:** {get_status_badge(bundle['status'])}")
                    st.write(f"**Total Items:** {bundle['total_items']}")
                    st.write(f"**Total Quantity:** {bundle.get('total_quantity', 0)} pcs")
                
                with col2:
                    # Show vendor info
                    vendor_id = bundle.get('recommended_vendor_id')
                    if vendor_id:
                        vendor_query = "SELECT vendor_name, vendor_email FROM Vendors WHERE vendor_id = ?"
                        vendor_result = db.execute_query(vendor_query, (vendor_id,))
                        if vendor_result:
                            st.write("**Recommended Vendor:**")
                            st.write(f"• {vendor_result[0]['vendor_name']}")
                            if vendor_result[0].get('vendor_email'):
                                st.write(f"• {vendor_result[0]['vendor_email']}")
                    else:
                        st.write("**Vendor:** Not assigned")
                
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

def display_user_management(db: DatabaseConnector):
    """Admin-only user management (create, update, activate, role, reset password)"""
    st.header("👤 User Management (Admin)")

    # Simple admin gate using requirements_users with role Operator/Admin
    if 'um_admin_auth' not in st.session_state:
        st.session_state.um_admin_auth = False
        st.session_state.um_admin_user = None

    if not st.session_state.um_admin_auth:
        st.info("Operator/Admin sign-in required to manage users.")
        with st.form("um_admin_login"):
            username = st.text_input("Admin username")
            password = st.text_input("Admin password", type="password")
            submitted = st.form_submit_button("Sign in")
        if submitted:
            try:
                u = db.authenticate_user(username, password)
                if u and str(u.get('user_role', '')).lower() in ("operator", "admin"):
                    st.session_state.um_admin_auth = True
                    st.session_state.um_admin_user = u
                    st.success(f"Welcome, {u.get('full_name') or u.get('username')}!")
                    st.rerun()
                else:
                    st.error("Not authorized. Operator/Admin only.")
            except Exception as e:
                st.error(f"Login error: {str(e)}")
        return

    # Authenticated admin UI
    colL, colR = st.columns([2, 1])
    with colR:
        if st.button("Sign out", use_container_width=True):
            st.session_state.um_admin_auth = False
            st.session_state.um_admin_user = None
            st.rerun()

    # Show success after rerun if user was created
    if st.session_state.get('um_user_created_success'):
        st.success("User created.")
        del st.session_state['um_user_created_success']

    st.subheader("All Users")
    try:
        users = db.list_users() or []
        if not users:
            st.info("No users found.")
        for u in users:
            with st.expander(f"{u['username']} — {u.get('full_name') or ''}"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    full_name = st.text_input("Full name", value=u.get('full_name') or "", key=f"name_{u['user_id']}")
                with c2:
                    email = st.text_input("Email", value=u.get('email') or "", key=f"email_{u['user_id']}")
                with c3:
                    dept = st.text_input("Department", value=u.get('department') or "", key=f"dept_{u['user_id']}")
                with c4:
                    role = st.selectbox("Role", options=["User", "Operator"], index=0 if (u.get('user_role') or "User") == "User" else 1, key=f"role_{u['user_id']}")

                c5, c6, c7 = st.columns(3)
                with c5:
                    active = st.checkbox("Active", value=bool(u.get('is_active')), key=f"active_{u['user_id']}")
                with c6:
                    new_pw = st.text_input("Reset password", type="password", key=f"pw_{u['user_id']}")
                with c7:
                    st.caption(f"Created: {u.get('created_at')}\nLast login: {u.get('last_login')}")

                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("Save Profile", key=f"save_{u['user_id']}"):
                        ok1 = db.update_user_profile(u['user_id'], full_name, email, dept)
                        ok2 = db.set_user_role(u['user_id'], role)
                        ok3 = db.set_user_active(u['user_id'], active)
                        if ok1 and ok2 and ok3:
                            st.success("Updated.")
                        else:
                            st.error("Failed to update some fields.")
                with b2:
                    if st.button("Reset Password", key=f"reset_{u['user_id']}"):
                        if (new_pw or "").strip():
                            if db.reset_user_password(u['user_id'], new_pw.strip()):
                                st.success("Password reset.")
                            else:
                                st.error("Failed to reset password.")
                        else:
                            st.warning("Enter a new password first.")
                with b3:
                    st.write("")

    except Exception as e:
        st.error(f"Error loading users: {str(e)}")

    st.markdown("---")
    st.subheader("Create New User")
    with st.form("create_user_form", clear_on_submit=True):
        cu1, cu2 = st.columns(2)
        with cu1:
            c_username = st.text_input("Username")
            c_fullname = st.text_input("Full name")
            c_department = st.text_input("Department")
        with cu2:
            c_email = st.text_input("Email")
            c_role = st.selectbox("Role", ["User", "Operator"])
            c_active = st.checkbox("Active", value=True)
        c_pw = st.text_input("Initial password", type="password")
        submit_new = st.form_submit_button("Create User", type="primary")
    if submit_new:
        if not c_username or not c_pw:
            st.warning("Username and password are required.")
        else:
            res = db.create_user(c_username.strip(), c_pw.strip(), c_fullname.strip(), c_email.strip(), c_department.strip(), c_role, 1 if c_active else 0)
            if res.get('success'):
                st.session_state['um_user_created_success'] = True
                st.rerun()
            else:
                st.error(f"Failed to create user: {res.get('error')}")

def get_all_bundles(db):
    """Get all bundles from database"""
    query = """
    SELECT bundle_id, bundle_name, status, total_items, total_quantity,
           created_at, rejection_reason, rejected_at, recommended_vendor_id
    FROM requirements_bundles
    ORDER BY created_at DESC
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
            
            # Update all related requests to Completed++++++++
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
