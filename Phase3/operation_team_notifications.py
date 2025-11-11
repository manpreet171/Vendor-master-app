"""
Operation Team Email Notifications System
Sends email notifications to Operation Team when bundles are reviewed

Trigger:
- Immediate: When operator marks bundle as Reviewed (Active → Reviewed)

Uses existing Brevo SMTP service from email_service.py
"""

import os
import logging
from datetime import datetime
from email_service import send_email_via_brevo

logger = logging.getLogger("operation_team_notifications")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_operation_team_emails(db):
    """
    Get all active Operation Team member emails
    
    Args:
        db: DatabaseConnector instance
    
    Returns:
        list: List of email addresses
    """
    try:
        query = """
        SELECT email, full_name
        FROM requirements_users
        WHERE user_role = 'Operation' 
          AND is_active = 1 
          AND email IS NOT NULL
        ORDER BY full_name
        """
        results = db.execute_query(query)
        
        if not results:
            logger.warning("No active Operation Team members found with email addresses")
            return []
        
        emails = [r['email'] for r in results if r.get('email')]
        logger.info(f"Found {len(emails)} Operation Team member(s) to notify")
        return emails
        
    except Exception as e:
        logger.error(f"Error getting Operation Team emails: {str(e)}")
        return []


def send_bundle_reviewed_notification(db, bundle_id):
    """
    Send immediate notification when bundle is marked as Reviewed
    
    Args:
        db: DatabaseConnector instance
        bundle_id: Bundle ID that was just reviewed
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Check if already notified
        check_query = """
        SELECT operation_notified_at
        FROM requirements_bundles
        WHERE bundle_id = ?
        """
        result = db.execute_query(check_query, (bundle_id,))
        
        if result and result[0].get('operation_notified_at'):
            logger.info(f"Bundle {bundle_id} already notified at {result[0]['operation_notified_at']}")
            return False
        
        # Get Operation Team emails
        recipients = get_operation_team_emails(db)
        
        if not recipients:
            logger.warning(f"No Operation Team members to notify for bundle {bundle_id}")
            return False
        
        # Get bundle details
        bundle_data = _get_bundle_details(db, bundle_id)
        
        if not bundle_data:
            logger.error(f"Bundle {bundle_id} not found")
            return False
        
        # Get bundle items
        items = _get_bundle_items(db, bundle_id)
        
        # Get user requests in bundle
        requests = _get_bundle_requests(db, bundle_id)
        
        # Build email content
        subject, body_text, html_body = _build_bundle_reviewed_email(bundle_data, items, requests)
        
        # Send email
        email_sent = send_email_via_brevo(subject, body_text, html_body, recipients=recipients)
        
        if email_sent:
            # Update operation_notified_at timestamp
            update_query = """
            UPDATE requirements_bundles
            SET operation_notified_at = GETDATE()
            WHERE bundle_id = ?
            """
            db.execute_insert(update_query, (bundle_id,))
            db.conn.commit()
            
            logger.info(f"✅ Bundle reviewed notification sent for {bundle_data['bundle_name']} to {len(recipients)} recipient(s)")
            return True
        else:
            logger.error(f"❌ Failed to send bundle reviewed notification for bundle {bundle_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending bundle reviewed notification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ========== Helper Functions ==========

def _get_bundle_details(db, bundle_id):
    """Get bundle details with vendor info"""
    query = """
    SELECT 
        b.bundle_id,
        b.bundle_name,
        b.status,
        b.total_items,
        b.total_quantity,
        b.created_at,
        b.reviewed_at,
        b.rejection_reason,
        b.rejected_at,
        b.merge_count,
        b.last_merged_at,
        b.merge_reason,
        b.operation_notified_at,
        v.vendor_name,
        v.vendor_email,
        v.vendor_phone
    FROM requirements_bundles b
    LEFT JOIN Vendors v ON b.recommended_vendor_id = v.vendor_id
    WHERE b.bundle_id = ?
    """
    results = db.execute_query(query, (bundle_id,))
    return results[0] if results else None


def _get_bundle_items(db, bundle_id):
    """Get items in bundle with details"""
    query = """
    SELECT 
        i.item_name,
        i.sku,
        bi.total_quantity,
        bi.size_details
    FROM requirements_bundle_items bi
    JOIN items i ON bi.item_id = i.item_id
    WHERE bi.bundle_id = ?
    ORDER BY i.item_name
    """
    return db.execute_query(query, (bundle_id,))


def _get_bundle_requests(db, bundle_id):
    """Get user requests in bundle with notes and urgency"""
    query = """
    SELECT DISTINCT
        ro.req_number,
        ro.user_notes,
        u.full_name,
        u.username,
        (SELECT COUNT(*) FROM requirements_order_items WHERE req_id = ro.req_id) as item_count,
        (SELECT MIN(date_needed) FROM requirements_order_items WHERE req_id = ro.req_id) as earliest_date_needed
    FROM requirements_bundle_mapping bm
    JOIN requirements_orders ro ON bm.req_id = ro.req_id
    LEFT JOIN requirements_users u ON ro.user_id = u.user_id
    WHERE bm.bundle_id = ?
    ORDER BY earliest_date_needed, ro.req_number
    """
    return db.execute_query(query, (bundle_id,))


def _format_date(date_value):
    """Format date for display"""
    if not date_value:
        return "Not specified"
    
    if hasattr(date_value, 'strftime'):
        return date_value.strftime('%Y-%m-%d')
    
    return str(date_value)


def _format_datetime(datetime_value):
    """Format datetime for display"""
    if not datetime_value:
        return "Not specified"
    
    if hasattr(datetime_value, 'strftime'):
        return datetime_value.strftime('%Y-%m-%d at %I:%M %p')
    
    return str(datetime_value)


def _calculate_urgency(date_needed):
    """Calculate days until date needed"""
    if not date_needed:
        return None
    
    try:
        if isinstance(date_needed, str):
            from datetime import datetime
            date_needed = datetime.strptime(date_needed, '%Y-%m-%d').date()
        elif hasattr(date_needed, 'date'):
            date_needed = date_needed.date()
        
        from datetime import date
        today = date.today()
        delta = (date_needed - today).days
        return delta
    except Exception:
        return None


def _build_bundle_reviewed_email(bundle_data, items, requests):
    """
    Build email content for bundle reviewed notification
    
    Returns:
        tuple: (subject, body_text, html_body)
    """
    bundle_name = bundle_data['bundle_name']
    vendor_name = bundle_data.get('vendor_name', 'Unknown Vendor')
    vendor_email = bundle_data.get('vendor_email', 'N/A')
    vendor_phone = bundle_data.get('vendor_phone', 'N/A')
    reviewed_at = _format_datetime(bundle_data.get('reviewed_at'))
    
    # Subject
    subject = f"🟢 Bundle Reviewed - Awaiting Approval: {bundle_name}"
    
    # Count urgent items
    urgent_count = 0
    for req in requests:
        if req.get('earliest_date_needed'):
            days = _calculate_urgency(req['earliest_date_needed'])
            if days is not None and days <= 5:
                urgent_count += 1
    
    # Build plain text body
    body_text = f"""Hello Operation Team,

A bundle has been reviewed by the operator and is ready for your approval.

BUNDLE DETAILS:
---------------
Bundle ID: {bundle_name}
Vendor: {vendor_name}
Email: {vendor_email}
Phone: {vendor_phone}
Reviewed: {reviewed_at}

ITEMS:
------
"""
    
    for item in items:
        size = item.get('size_details', '')
        size_str = f" ({size})" if size else ""
        body_text += f"• {item['item_name']}{size_str} - {item['total_quantity']} pcs\n"
    
    body_text += f"\nTotal: {len(items)} item(s), {bundle_data['total_quantity']} pieces\n"
    
    # User requests section
    body_text += "\nUSER REQUESTS:\n--------------\n"
    
    for req in requests:
        user_name = req.get('full_name') or req.get('username', 'Unknown User')
        body_text += f"• {req['req_number']} ({user_name}) - {req['item_count']} item(s)\n"
        
        if req.get('user_notes'):
            body_text += f"  📝 Notes: \"{req['user_notes']}\"\n"
        
        if req.get('earliest_date_needed'):
            date_str = _format_date(req['earliest_date_needed'])
            days = _calculate_urgency(req['earliest_date_needed'])
            if days is not None and days <= 5:
                body_text += f"  📅 Date Needed: {date_str} (⚠️ {days} days!)\n"
            else:
                body_text += f"  📅 Date Needed: {date_str}\n"
        
        body_text += "\n"
    
    # Bundle history section
    if bundle_data.get('merge_count') or bundle_data.get('rejection_reason'):
        body_text += "BUNDLE HISTORY:\n---------------\n"
        body_text += f"✅ Created: {_format_datetime(bundle_data.get('created_at'))}\n"
        
        if bundle_data.get('merge_count'):
            body_text += f"🔄 Updated {bundle_data['merge_count']} time(s) - Last: {_format_datetime(bundle_data.get('last_merged_at'))}\n"
            if bundle_data.get('merge_reason'):
                body_text += f"   Merge Reason: {bundle_data['merge_reason']}\n"
        
        if bundle_data.get('rejection_reason'):
            body_text += f"\n⚠️ Previously Rejected: {_format_datetime(bundle_data.get('rejected_at'))}\n"
            body_text += f"   Reason: \"{bundle_data['rejection_reason']}\"\n"
        
        body_text += "\n"
    
    # Urgency indicator
    if urgent_count > 0:
        body_text += f"URGENCY:\n--------\n⚠️ {urgent_count} item(s) needed within 5 days!\n\n"
    
    # Action required
    body_text += """ACTION REQUIRED:
----------------
Please log in to the system to approve or reject this bundle.

Dashboard: https://your-app-url.com

---
This is an automated notification from the Procurement System.
"""
    
    # Build HTML body (simple styled version)
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #4CAF50;">🟢 Bundle Reviewed - Awaiting Approval</h2>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Bundle Details</h3>
            <p><strong>Bundle ID:</strong> {bundle_name}<br>
            <strong>Vendor:</strong> {vendor_name}<br>
            <strong>Email:</strong> {vendor_email}<br>
            <strong>Phone:</strong> {vendor_phone}<br>
            <strong>Reviewed:</strong> {reviewed_at}</p>
        </div>
        
        <h3>Items ({len(items)} items, {bundle_data['total_quantity']} pieces)</h3>
        <ul>
    """
    
    for item in items:
        size = item.get('size_details', '')
        size_str = f" ({size})" if size else ""
        html_body += f"<li>{item['item_name']}{size_str} - <strong>{item['total_quantity']} pcs</strong></li>"
    
    html_body += "</ul><h3>User Requests</h3>"
    
    for req in requests:
        user_name = req.get('full_name') or req.get('username', 'Unknown User')
        html_body += f"<div style='margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border-left: 3px solid #2196F3;'>"
        html_body += f"<strong>{req['req_number']}</strong> ({user_name}) - {req['item_count']} item(s)<br>"
        
        if req.get('user_notes'):
            html_body += f"<em>📝 {req['user_notes']}</em><br>"
        
        if req.get('earliest_date_needed'):
            date_str = _format_date(req['earliest_date_needed'])
            days = _calculate_urgency(req['earliest_date_needed'])
            if days is not None and days <= 5:
                html_body += f"<span style='color: #f44336;'>📅 Date Needed: {date_str} (⚠️ {days} days!)</span>"
            else:
                html_body += f"📅 Date Needed: {date_str}"
        
        html_body += "</div>"
    
    # Bundle history
    if bundle_data.get('merge_count') or bundle_data.get('rejection_reason'):
        html_body += "<h3>Bundle History</h3><ul>"
        html_body += f"<li>✅ Created: {_format_datetime(bundle_data.get('created_at'))}</li>"
        
        if bundle_data.get('merge_count'):
            html_body += f"<li>🔄 Updated {bundle_data['merge_count']} time(s) - Last: {_format_datetime(bundle_data.get('last_merged_at'))}</li>"
        
        if bundle_data.get('rejection_reason'):
            html_body += f"<li style='color: #f44336;'>⚠️ Previously Rejected: {_format_datetime(bundle_data.get('rejected_at'))}<br>"
            html_body += f"Reason: \"{bundle_data['rejection_reason']}\"</li>"
        
        html_body += "</ul>"
    
    # Urgency
    if urgent_count > 0:
        html_body += f"<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800; margin: 20px 0;'>"
        html_body += f"<strong>⚠️ URGENCY:</strong> {urgent_count} item(s) needed within 5 days!"
        html_body += "</div>"
    
    html_body += """
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Action Required</h3>
            <p>Please log in to the system to approve or reject this bundle.</p>
            <p><a href="https://your-app-url.com" style="background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Go to Dashboard</a></p>
        </div>
        
        <p style="color: #999; font-size: 12px; margin-top: 30px;">This is an automated notification from the Procurement System.</p>
    </body>
    </html>
    """
    
    return subject, body_text, html_body
