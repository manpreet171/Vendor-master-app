"""
Operation Team Dashboard for Phase 3
Simplified interface for approving/rejecting reviewed bundles
"""

import streamlit as st
from datetime import datetime
from db_connector import DatabaseConnector

def main(db=None):
    # Note: set_page_config() is already called in app.py
    # Do not call it again here to avoid conflict
    
    st.title("✅ Operation Team Dashboard")
    st.caption("Bundle Approval Management")
    
    # Use passed db connection or create new one
    if db is None:
        db = DatabaseConnector()
    
    # Sidebar info
    st.sidebar.title("👤 Operation Team")
    st.sidebar.info("You can approve or reject reviewed bundles.")
    
    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Main content - Reviewed Bundles
    display_reviewed_bundles(db)
    
    # Don't close connection if it was passed from app.py
    # db.close_connection()

def display_reviewed_bundles(db):
    """Display all reviewed bundles for approval/rejection - matches operator dashboard style"""
    st.header("📋 Reviewed Bundles")
    st.caption("Approve or reject bundles that have been reviewed by operators")
    
    try:
        # Get all reviewed bundles with vendor info (same as operator dashboard)
        bundles = db.get_reviewed_bundles_for_operation()
        
        if not bundles:
            st.info("✅ No bundles awaiting approval. All caught up!")
            return
        
        # Display count
        st.success(f"**{len(bundles)} bundle(s) awaiting your approval**")
        st.markdown("---")
        
        # Display each bundle
        for bundle in bundles:
            display_bundle_card(db, bundle)
            st.markdown("---")
    
    except Exception as e:
        st.error(f"Error loading bundles: {str(e)}")

def display_bundle_card(db, bundle):
    """Display a single bundle card - matches operator dashboard style"""
    
    # Format dates
    reviewed_date = bundle.get('reviewed_at')
    if reviewed_date and hasattr(reviewed_date, 'strftime'):
        reviewed_date = reviewed_date.strftime('%Y-%m-%d %H:%M')
    
    # Bundle header - simple and clean
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"📦 {bundle['bundle_name']}")
        st.caption(f"Vendor: {bundle.get('vendor_name', 'N/A')} | Reviewed: {reviewed_date or 'N/A'}")
    
    with col2:
        st.metric("Status", "🟢 Reviewed")
    
    # Show previous rejection warning if exists
    if bundle.get('rejection_reason'):
        rejected_date = bundle.get('rejected_at')
        if rejected_date and hasattr(rejected_date, 'strftime'):
            rejected_date = rejected_date.strftime('%Y-%m-%d %H:%M')
        
        st.error(f"⚠️ **REJECTED BY OPERATION TEAM**")
        st.markdown(f"""
        <div style='background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336;'>
            <p style='margin: 0; color: #c62828;'><strong>Rejected on:</strong> {rejected_date or 'N/A'}</p>
            <p style='margin: 5px 0 0 0; color: #c62828;'><strong>Reason:</strong> {bundle.get('rejection_reason', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Expandable section for detailed items (same as operator dashboard)
    with st.expander("📋 View Bundle Items", expanded=False):
        display_bundle_items_table(db, bundle['bundle_id'])
    
    # Action buttons
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button(f"✅ Approve", key=f"approve_{bundle['bundle_id']}", type="primary", use_container_width=True):
            handle_approve(db, bundle)
    
    with col2:
        if st.button(f"❌ Reject", key=f"reject_{bundle['bundle_id']}", type="secondary", use_container_width=True):
            st.session_state[f'show_reject_dialog_{bundle["bundle_id"]}'] = True
    
    # Rejection dialog
    if st.session_state.get(f'show_reject_dialog_{bundle["bundle_id"]}', False):
        show_rejection_dialog(db, bundle)

def display_bundle_items_table(db, bundle_id):
    """Display HTML table with per-project breakdown - EXACT copy from operator dashboard"""
    try:
        import json
        
        # Get bundle items with user breakdown
        query = """
        SELECT 
            bi.item_id,
            i.item_name,
            i.height,
            i.width,
            i.thickness,
            bi.total_quantity,
            bi.user_breakdown
        FROM requirements_bundle_items bi
        LEFT JOIN Items i ON bi.item_id = i.item_id
        WHERE bi.bundle_id = ?
        ORDER BY i.item_name
        """
        items = db.execute_query(query, (bundle_id,))
        
        if not items:
            st.info("No items found in this bundle.")
            return
        
        # Get user names for display
        user_ids_set = set()
        for it in items:
            try:
                breakdown = json.loads(it.get('user_breakdown') or '{}') if isinstance(it.get('user_breakdown'), str) else it.get('user_breakdown') or {}
            except Exception:
                breakdown = {}
            for uid in breakdown.keys():
                if str(uid).isdigit():
                    user_ids_set.add(int(uid))
        
        user_name_map = {}
        if user_ids_set:
            user_ids_list = list(user_ids_set)
            placeholders = ','.join(['?' for _ in user_ids_list])
            user_query = f"SELECT user_id, full_name FROM requirements_users WHERE user_id IN ({placeholders})"
            user_results = db.execute_query(user_query, user_ids_list)
            for u in user_results or []:
                user_name_map[u['user_id']] = u.get('full_name') or f"User {u['user_id']}"
        
        # Build HTML table (EXACT copy from operator dashboard)
        html_table = """
        <style>
            .bundle-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 14px;
            }
            .bundle-table thead {
                background-color: #f0f2f6;
            }
            .bundle-table th {
                padding: 12px 10px;
                text-align: left;
                border-bottom: 2px solid #ddd;
                font-weight: 600;
            }
            .bundle-table td {
                padding: 10px;
                border-bottom: 1px solid #eee;
                vertical-align: top;
            }
            .bundle-table tbody tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .bundle-table tbody tr:hover {
                background-color: #f0f0f0;
            }
            .item-name {
                font-weight: 600;
                color: #1f1f1f;
            }
            .item-dims {
                font-size: 12px;
                color: #666;
            }
            .item-total {
                font-size: 12px;
                color: #0066cc;
            }
            .user-name {
                font-weight: 500;
                color: #333;
            }
            .project-icon {
                margin-right: 4px;
            }
            .qty-cell {
                text-align: right;
                font-weight: 500;
            }
        </style>
        <table class="bundle-table">
            <thead>
                <tr>
                    <th style="width: 35%;">Item</th>
                    <th style="width: 25%;">User</th>
                    <th style="width: 25%;">Project</th>
                    <th style="width: 15%; text-align: right;">Quantity</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for it in items:
            # Build dimension text
            dims = []
            for key in ('height', 'width', 'thickness'):
                val = it.get(key)
                if val:
                    dims.append(str(val))
            dim_txt = f"{' x '.join(dims)}" if dims else ""
            
            # Get user breakdown
            try:
                breakdown = json.loads(it.get('user_breakdown') or '{}') if isinstance(it.get('user_breakdown'), str) else it.get('user_breakdown') or {}
            except Exception:
                breakdown = {}
            
            if breakdown:
                # Get project breakdown for this item
                project_breakdown = db.get_bundle_item_project_breakdown(bundle_id, it['item_id'])
                project_map = {}
                for pb in project_breakdown or []:
                    key = (pb['user_id'], pb.get('project_number'))
                    project_map[key] = project_map.get(key, 0) + pb['quantity']
                
                # Count total rows for this item (for rowspan)
                total_rows = sum(len([(k[1], v) for k, v in project_map.items() if k[0] == int(uid) and k[1]]) or 1 
                               for uid in breakdown.keys())
                
                # First row flag
                first_row = True
                
                for uid, qty in breakdown.items():
                    uname = user_name_map.get(int(uid), f"User {uid}") if str(uid).isdigit() else f"User {uid}"
                    user_project_breakdown = [(k[1], v) for k, v in project_map.items() if k[0] == int(uid) and k[1]]
                    
                    if user_project_breakdown:
                        # Multiple projects for this user
                        user_rows = len(user_project_breakdown)
                        for idx, (project_num, project_qty) in enumerate(user_project_breakdown):
                            html_table += "<tr>"
                            
                            # Item cell (only on first row)
                            if first_row:
                                html_table += f"""
                                <td rowspan="{total_rows}">
                                    <div class="item-name">{it['item_name']}</div>
                                    <div class="item-dims">{dim_txt}</div>
                                    <div class="item-total">Total: {it['total_quantity']} pcs</div>
                                </td>
                                """
                                first_row = False
                            
                            # User cell (rowspan if multiple projects)
                            if idx == 0:
                                html_table += f'<td rowspan="{user_rows}"><span class="user-name">👤 {uname}</span></td>'
                            
                            # Project and quantity
                            html_table += f"""
                            <td><span class="project-icon">📋</span>{project_num}</td>
                            <td class="qty-cell">{project_qty} pcs</td>
                            """
                            html_table += "</tr>"
                    else:
                        # No project info
                        html_table += "<tr>"
                        if first_row:
                            html_table += f"""
                            <td rowspan="{total_rows}">
                                <div class="item-name">{it['item_name']}</div>
                                <div class="item-dims">{dim_txt}</div>
                                <div class="item-total">Total: {it['total_quantity']} pcs</div>
                            </td>
                            """
                            first_row = False
                        html_table += f"""
                        <td><span class="user-name">👤 {uname}</span></td>
                        <td>—</td>
                        <td class="qty-cell">{qty} pcs</td>
                        </tr>
                        """
            else:
                # No breakdown
                html_table += f"""
                <tr>
                    <td>
                        <div class="item-name">{it['item_name']}</div>
                        <div class="item-dims">{dim_txt}</div>
                        <div class="item-total">Total: {it['total_quantity']} pcs</div>
                    </td>
                    <td>—</td>
                    <td>—</td>
                    <td class="qty-cell">{it['total_quantity']} pcs</td>
                </tr>
                """
        
        html_table += """
            </tbody>
        </table>
        """
        
        st.markdown(html_table, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading bundle items: {str(e)}")

def show_rejection_dialog(db, bundle):
    """Show dialog for entering rejection reason"""
    st.markdown("---")
    st.subheader(f"❌ Reject Bundle: {bundle['bundle_name']}")
    
    # Text area for rejection reason
    rejection_reason = st.text_area(
        "Rejection Reason: * (Required)",
        placeholder="Enter the reason for rejecting this bundle...\n\nExamples:\n- Vendor pricing too high, check alternatives\n- Incorrect vendor selected\n- Items need verification\n- Budget constraints",
        max_chars=500,
        height=150,
        key=f"rejection_reason_{bundle['bundle_id']}"
    )
    
    # Character count
    char_count = len(rejection_reason) if rejection_reason else 0
    st.caption(f"Characters: {char_count} / 500")
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel", key=f"cancel_reject_{bundle['bundle_id']}", use_container_width=True):
            st.session_state[f'show_reject_dialog_{bundle["bundle_id"]}'] = False
            st.rerun()
    
    with col2:
        if st.button("Reject Bundle", key=f"confirm_reject_{bundle['bundle_id']}", type="primary", use_container_width=True):
            if not rejection_reason or not rejection_reason.strip():
                st.error("❌ Rejection reason is required!")
            else:
                handle_reject(db, bundle, rejection_reason.strip())

def handle_approve(db, bundle):
    """Handle bundle approval"""
    try:
        result = db.approve_bundle_by_operation(bundle['bundle_id'])
        
        if result.get('success'):
            st.success(f"✅ Bundle {bundle['bundle_name']} approved successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ Failed to approve bundle: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Error approving bundle: {str(e)}")

def handle_reject(db, bundle, rejection_reason):
    """Handle bundle rejection"""
    try:
        result = db.reject_bundle_by_operation(bundle['bundle_id'], rejection_reason)
        
        if result.get('success'):
            st.success(f"✅ Bundle {bundle['bundle_name']} rejected successfully!")
            st.info("The operator will see your rejection reason and can fix the issues.")
            # Clear the dialog state
            st.session_state[f'show_reject_dialog_{bundle["bundle_id"]}'] = False
            st.rerun()
        else:
            st.error(f"❌ Failed to reject bundle: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Error rejecting bundle: {str(e)}")

if __name__ == "__main__":
    main()
