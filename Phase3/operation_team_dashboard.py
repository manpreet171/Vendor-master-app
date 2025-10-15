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
    """Display HTML table with per-project breakdown for bundle items"""
    try:
        # Get bundle items
        query = """
        SELECT 
            bi.item_id,
            i.item_name,
            i.height,
            i.width,
            i.thickness,
            bi.total_quantity
        FROM requirements_bundle_items bi
        LEFT JOIN Items i ON bi.item_id = i.item_id
        WHERE bi.bundle_id = ?
        ORDER BY i.item_name
        """
        items = db.execute_query(query, (bundle_id,))
        
        if not items:
            st.info("No items found in this bundle.")
            return
        
        # Display each item with project breakdown
        for item in items:
            st.markdown(f"**{item['item_name']}**")
            
            # Get dimensions
            dims = []
            if item.get('height'): dims.append(f"H: {item['height']}\"")
            if item.get('width'): dims.append(f"W: {item['width']}\"")
            if item.get('thickness'): dims.append(f"T: {item['thickness']}\"")
            if dims:
                st.caption(" | ".join(dims))
            
            # Get project breakdown
            breakdown = db.get_bundle_item_project_breakdown(bundle_id, item['item_id'])
            
            if breakdown:
                # Use Streamlit's native table instead of HTML
                import pandas as pd
                df = pd.DataFrame(breakdown)
                if not df.empty:
                    # Rename columns for display
                    display_df = df[['project_number', 'quantity', 'user_id']].copy()
                    display_df.columns = ['Project', 'Quantity', 'User']
                    display_df['Quantity'] = display_df['Quantity'].astype(str) + ' pcs'
                    display_df['User'] = 'User #' + display_df['User'].astype(str)
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.caption(f"Total: {item['total_quantity']} pieces")
            else:
                st.caption(f"Total: {item['total_quantity']} pieces")
            
            st.markdown("---")
    
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
