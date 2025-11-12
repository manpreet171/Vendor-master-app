"""
Operator Email Notifications
- Bundling summary emails (Tuesday/Thursday cron)
- Bundle decision notifications (approved/rejected by Operation Team)
- Provides dynamic operator email list from database
- Consistent with user_notifications.py and operation_team_notifications.py patterns
"""

import logging
from email_service import send_email_via_brevo

logger = logging.getLogger("operator_notifications")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_operator_emails(db):
    """
    Get email addresses of all active operators from database.
    
    Args:
        db: DatabaseConnector instance
    
    Returns:
        list: List of operator email addresses, or empty list if none found
    
    Example:
        >>> emails = get_operator_emails(db)
        >>> print(emails)
        ['rex@sdgny.com', 'joivel@sdgny.com', 'miguel@sdgny.com']
    """
    query = """
    SELECT 
        email,
        full_name,
        username
    FROM requirements_users
    WHERE role = 'Operator'
      AND is_active = 1
      AND email IS NOT NULL
      AND email != ''
    ORDER BY full_name
    """
    
    try:
        results = db.execute_query(query)
        
        if not results:
            logger.info("No active operators found in database")
            return []
        
        # Extract emails and log operator names for transparency
        emails = [r['email'] for r in results]
        names = [r.get('full_name') or r.get('username', 'Unknown') for r in results]
        
        logger.info(f"Found {len(results)} active operator(s): {', '.join(names)}")
        logger.info(f"Operator emails: {', '.join(emails)}")
        
        return emails
        
    except Exception as e:
        logger.error(f"Error querying operator emails from database: {str(e)}")
        return []


# ========== Bundle Decision Notifications ==========

def _get_bundle_details_for_operator(db, bundle_id):
    """Get bundle details for operator notification"""
    query = """
    SELECT 
        b.bundle_id,
        b.bundle_name,
        b.reviewed_by,
        b.approved_at,
        b.rejected_at,
        b.rejection_reason,
        b.total_items,
        b.total_quantity,
        v.vendor_name,
        v.vendor_email,
        v.vendor_phone
    FROM requirements_bundles b
    LEFT JOIN Vendors v ON b.recommended_vendor_id = v.vendor_id
    WHERE b.bundle_id = ?
    """
    try:
        results = db.execute_query(query, (bundle_id,))
        return results[0] if results else None
    except Exception as e:
        logger.error(f"Error getting bundle details: {str(e)}")
        return None


def _get_operator_email_by_name(db, full_name):
    """Get operator email from full name"""
    if not full_name or full_name == 'Operator':
        return None
    
    query = """
    SELECT email, full_name
    FROM requirements_users
    WHERE full_name = ?
      AND role = 'Operator'
      AND is_active = 1
      AND email IS NOT NULL
      AND email != ''
    """
    try:
        results = db.execute_query(query, (full_name,))
        if results:
            return results[0]['email']
        else:
            logger.warning(f"No active operator found with name: {full_name}")
            return None
    except Exception as e:
        logger.error(f"Error getting operator email: {str(e)}")
        return None


def _format_datetime(datetime_value):
    """Format datetime for display"""
    if not datetime_value:
        return "Not specified"
    if hasattr(datetime_value, 'strftime'):
        return datetime_value.strftime('%Y-%m-%d at %I:%M %p')
    return str(datetime_value)


def send_bundle_approved_notification(db, bundle_id):
    """
    Send email to operator when Operation Team approves their bundle
    
    Args:
        db: DatabaseConnector instance
        bundle_id: ID of approved bundle
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get bundle details
        bundle = _get_bundle_details_for_operator(db, bundle_id)
        if not bundle:
            logger.error(f"Bundle {bundle_id} not found")
            return False
        
        # Get operator email
        reviewed_by = bundle.get('reviewed_by')
        if not reviewed_by or reviewed_by == 'Operator':
            logger.info(f"Bundle {bundle_id} has no specific reviewer; skipping operator notification")
            return False
        
        operator_email = _get_operator_email_by_name(db, reviewed_by)
        if not operator_email:
            logger.warning(f"No email found for operator '{reviewed_by}'; skipping notification")
            return False
        
        # Build email content
        bundle_name = bundle['bundle_name']
        vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
        approved_at = _format_datetime(bundle.get('approved_at'))
        
        # Subject
        subject = f"✅ Bundle Approved: {bundle_name}"
        
        # Plain text body
        body_text = f"""Hello {reviewed_by},

Good news! Your bundle has been approved by the Operation Team.

BUNDLE DETAILS:
---------------
Bundle ID: {bundle_name}
Vendor: {vendor_name}
Items: {bundle.get('total_items', 0)} item(s), {bundle.get('total_quantity', 0)} pieces
Reviewed by: {reviewed_by} (you)
Approved at: {approved_at}

NEXT STEPS:
-----------
The bundle is now ready for vendor communication and order placement.

Dashboard: https://item-requirement-app-sdgny.streamlit.app/

---
This is an automated notification from the Procurement System.
"""
        
        # HTML body
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #4CAF50;">✅ Bundle Approved</h2>
    
    <p>Hello <strong>{reviewed_by}</strong>,</p>
    
    <p>Good news! Your bundle has been approved by the Operation Team.</p>
    
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0;">Bundle Details</h3>
        <p>
            <strong>Bundle ID:</strong> {bundle_name}<br>
            <strong>Vendor:</strong> {vendor_name}<br>
            <strong>Items:</strong> {bundle.get('total_items', 0)} item(s), {bundle.get('total_quantity', 0)} pieces<br>
            <strong>Reviewed by:</strong> {reviewed_by} (you)<br>
            <strong>Approved at:</strong> {approved_at}
        </p>
    </div>
    
    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #4CAF50;">Next Steps</h3>
        <p>The bundle is now ready for vendor communication and order placement.</p>
    </div>
    
    <p><a href="https://item-requirement-app-sdgny.streamlit.app/" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
    
    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
    <p style="color: #666; font-size: 0.9em;">This is an automated notification from the Procurement System.</p>
</body>
</html>
"""
        
        # Send email
        sent = send_email_via_brevo(subject, body_text, html_body=html_body, recipients=[operator_email])
        
        if sent:
            logger.info(f"Bundle approved notification sent to {reviewed_by} ({operator_email})")
            return True
        else:
            logger.warning(f"Failed to send bundle approved notification to {operator_email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending bundle approved notification: {str(e)}")
        return False


def send_bundle_rejected_notification(db, bundle_id):
    """
    Send email to operator when Operation Team rejects their bundle
    
    Args:
        db: DatabaseConnector instance
        bundle_id: ID of rejected bundle
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get bundle details
        bundle = _get_bundle_details_for_operator(db, bundle_id)
        if not bundle:
            logger.error(f"Bundle {bundle_id} not found")
            return False
        
        # Get operator email
        reviewed_by = bundle.get('reviewed_by')
        if not reviewed_by or reviewed_by == 'Operator':
            logger.info(f"Bundle {bundle_id} has no specific reviewer; skipping operator notification")
            return False
        
        operator_email = _get_operator_email_by_name(db, reviewed_by)
        if not operator_email:
            logger.warning(f"No email found for operator '{reviewed_by}'; skipping notification")
            return False
        
        # Build email content
        bundle_name = bundle['bundle_name']
        vendor_name = bundle.get('vendor_name', 'Unknown Vendor')
        rejected_at = _format_datetime(bundle.get('rejected_at'))
        rejection_reason = bundle.get('rejection_reason', 'No reason provided')
        
        # Subject
        subject = f"❌ Bundle Rejected: {bundle_name}"
        
        # Plain text body
        body_text = f"""Hello {reviewed_by},

Your bundle has been rejected by the Operation Team and needs your attention.

BUNDLE DETAILS:
---------------
Bundle ID: {bundle_name}
Vendor: {vendor_name}
Items: {bundle.get('total_items', 0)} item(s), {bundle.get('total_quantity', 0)} pieces
Reviewed by: {reviewed_by} (you)
Rejected at: {rejected_at}

REJECTION REASON:
-----------------
{rejection_reason}

ACTION REQUIRED:
----------------
Please review the bundle, make necessary corrections, and mark it as Reviewed again.

Dashboard: https://item-requirement-app-sdgny.streamlit.app/

---
This is an automated notification from the Procurement System.
"""
        
        # HTML body
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #f44336;">❌ Bundle Rejected</h2>
    
    <p>Hello <strong>{reviewed_by}</strong>,</p>
    
    <p>Your bundle has been rejected by the Operation Team and needs your attention.</p>
    
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0;">Bundle Details</h3>
        <p>
            <strong>Bundle ID:</strong> {bundle_name}<br>
            <strong>Vendor:</strong> {vendor_name}<br>
            <strong>Items:</strong> {bundle.get('total_items', 0)} item(s), {bundle.get('total_quantity', 0)} pieces<br>
            <strong>Reviewed by:</strong> {reviewed_by} (you)<br>
            <strong>Rejected at:</strong> {rejected_at}
        </p>
    </div>
    
    <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f44336;">
        <h3 style="margin-top: 0; color: #f44336;">Rejection Reason</h3>
        <p style="margin: 0;">{rejection_reason}</p>
    </div>
    
    <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #ff9800;">Action Required</h3>
        <p>Please review the bundle, make necessary corrections, and mark it as Reviewed again.</p>
    </div>
    
    <p><a href="https://item-requirement-app-sdgny.streamlit.app/" style="display: inline-block; padding: 10px 20px; background-color: #f44336; color: white; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
    
    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
    <p style="color: #666; font-size: 0.9em;">This is an automated notification from the Procurement System.</p>
</body>
</html>
"""
        
        # Send email
        sent = send_email_via_brevo(subject, body_text, html_body=html_body, recipients=[operator_email])
        
        if sent:
            logger.info(f"Bundle rejected notification sent to {reviewed_by} ({operator_email})")
            return True
        else:
            logger.warning(f"Failed to send bundle rejected notification to {operator_email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending bundle rejected notification: {str(e)}")
        return False
