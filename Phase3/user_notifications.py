"""
User Email Notifications System
Sends status update emails to users when their requests change status

Triggers:
1. Pending → In Progress (when bundled)
2. In Progress → Ordered (when ALL bundles ordered)
3. Ordered → Completed (when ALL bundles completed)

Uses existing Brevo SMTP service from email_service.py
"""

import os
import logging
from datetime import datetime
from email_service import send_email_via_brevo

logger = logging.getLogger("user_notifications")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def send_user_notification(db, req_id, notification_type, bundle_data=None):
    """
    Send email notification to user about request status change
    
    Args:
        db: DatabaseConnector instance
        req_id: Request ID
        notification_type: 'in_progress', 'ordered', or 'completed'
        bundle_data: Optional dict with bundle info (for ordered/completed emails)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get request details
        request = _get_request_details(db, req_id)
        
        if not request:
            logger.warning(f"Request {req_id} not found")
            return False
        
        # Skip BoxHero requests (no user email)
        if request.get('source_type') == 'BoxHero':
            logger.info(f"Skipping notification for BoxHero request {req_id}")
            return False
        
        # Get user details
        user = _get_user_details(db, request['user_id'])
        
        if not user or not user.get('email'):
            logger.warning(f"User email not found for request {req_id}")
            return False
        
        # Check if already notified for this status
        if request.get('last_notified_status') == notification_type:
            logger.info(f"User already notified for {notification_type} status (req_id: {req_id})")
            return False
        
        # Get request items
        items = _get_request_items(db, req_id)
        
        if not items:
            logger.warning(f"No items found for request {req_id}")
            return False
        
        # Build email content based on notification type
        if notification_type == 'in_progress':
            subject, body_text, html_body = _build_in_progress_email(user, request, items)
        elif notification_type == 'ordered':
            subject, body_text, html_body = _build_ordered_email(user, request, items, bundle_data)
        elif notification_type == 'completed':
            subject, body_text, html_body = _build_completed_email(user, request, items, bundle_data)
        else:
            logger.error(f"Invalid notification type: {notification_type}")
            return False
        
        # Send email via Brevo to user's email address
        email_sent = send_email_via_brevo(subject, body_text, html_body, recipients=[user['email']])
        
        if email_sent:
            # Update last_notified_status
            _update_notification_status(db, req_id, notification_type)
            logger.info(f"✅ Email sent to {user['email']} for request {request['req_number']} ({notification_type})")
            return True
        else:
            logger.error(f"❌ Failed to send email for request {req_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending notification for request {req_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def _get_request_details(db, req_id):
    """Get request details from database"""
    query = """
    SELECT req_id, user_id, req_number, req_date, status, 
           source_type, last_notified_status
    FROM requirements_orders
    WHERE req_id = ?
    """
    results = db.execute_query(query, (req_id,))
    return results[0] if results else None


def _get_user_details(db, user_id):
    """Get user details including email"""
    query = """
    SELECT user_id, username, full_name, email, department
    FROM requirements_users
    WHERE user_id = ?
    """
    results = db.execute_query(query, (user_id,))
    return results[0] if results else None


def _get_request_items(db, req_id):
    """Get items for a request"""
    query = """
    SELECT 
        ri.quantity, ri.project_number, ri.sub_project_number, ri.date_needed,
        i.item_name, i.sku
    FROM requirements_order_items ri
    JOIN items i ON ri.item_id = i.item_id
    WHERE ri.req_id = ?
    ORDER BY i.item_name
    """
    return db.execute_query(query, (req_id,))


def _update_notification_status(db, req_id, notification_type):
    """Update last_notified_status to prevent duplicate emails"""
    query = """
    UPDATE requirements_orders
    SET last_notified_status = ?
    WHERE req_id = ?
    """
    db.execute_insert(query, (notification_type, req_id))
    db.conn.commit()


def _format_date(date_value):
    """Format date for display"""
    if not date_value:
        return "Not specified"
    
    if isinstance(date_value, str):
        return date_value
    
    try:
        return date_value.strftime('%B %d, %Y')
    except:
        return str(date_value)


def _build_in_progress_email(user, request, items):
    """Build email for 'In Progress' status"""
    
    subject = "Your Material Request is Being Processed"
    
    # Build items list
    items_text = ""
    items_html = ""
    
    for idx, item in enumerate(items, 1):
        # Plain text version
        items_text += f"\n{idx}. {item['item_name']}"
        if item.get('sku'):
            items_text += f" (SKU: {item['sku']})"
        items_text += f"\n   Quantity: {item['quantity']} pieces"
        
        if item.get('project_number'):
            items_text += f"\n   Project: {item['project_number']}"
            if item.get('sub_project_number'):
                items_text += f" - {item['sub_project_number']}"
        
        if item.get('date_needed'):
            items_text += f"\n   Needed by: {_format_date(item['date_needed'])}"
        
        items_text += "\n"
        
        # HTML version
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{idx}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                <strong>{item['item_name']}</strong>
                {f"<br><small style='color: #666;'>SKU: {item['sku']}</small>" if item.get('sku') else ""}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item['quantity']} pcs</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                {item.get('project_number', '—')}
                {f"<br><small>{item.get('sub_project_number', '')}</small>" if item.get('sub_project_number') else ""}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                {_format_date(item.get('date_needed'))}
            </td>
        </tr>
        """
    
    # Plain text body
    body_text = f"""
Hi {user['full_name']},

Your material request has been received and is now being processed.

REQUEST DETAILS:
Request Number: {request['req_number']}
Submitted: {_format_date(request['req_date'])}
Status: In Progress
Total Items: {len(items)}

ITEMS REQUESTED:
{items_text}

We'll notify you when your items are ordered.

If you have any questions, please contact the procurement team.

---
This is an automated notification from the Requirements Management System.
"""
    
    # HTML body
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c5aa0;">Your Material Request is Being Processed</h2>
            
            <p>Hi {user['full_name']},</p>
            
            <p>Your material request has been received and is now being processed.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c5aa0;">Request Details</h3>
                <p style="margin: 5px 0;"><strong>Request Number:</strong> {request['req_number']}</p>
                <p style="margin: 5px 0;"><strong>Submitted:</strong> {_format_date(request['req_date'])}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #ff9800; font-weight: bold;">In Progress</span></p>
                <p style="margin: 5px 0;"><strong>Total Items:</strong> {len(items)}</p>
            </div>
            
            <h3 style="color: #2c5aa0;">Items Requested</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #2c5aa0; color: white;">
                        <th style="padding: 10px; text-align: left;">#</th>
                        <th style="padding: 10px; text-align: left;">Item</th>
                        <th style="padding: 10px; text-align: left;">Quantity</th>
                        <th style="padding: 10px; text-align: left;">Project</th>
                        <th style="padding: 10px; text-align: left;">Needed By</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <p style="margin-top: 30px;">We'll notify you when your items are ordered.</p>
            
            <p>If you have any questions, please contact the procurement team.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 12px; color: #666;">This is an automated notification from the Requirements Management System.</p>
        </div>
    </body>
    </html>
    """
    
    return subject, body_text, html_body


def _build_ordered_email(user, request, items, bundle_data):
    """Build email for 'Ordered' status"""
    
    subject = "📦 Your Items Have Been Ordered"
    
    # Get bundles info (can be multiple bundles)
    bundles = bundle_data.get('bundles', []) if bundle_data else []
    
    # If no bundles data (backward compatibility), use old format
    if not bundles:
        po_number = bundle_data.get('po_number', 'TBD') if bundle_data else 'TBD'
        po_date = bundle_data.get('po_date') if bundle_data else None
        expected_delivery = bundle_data.get('expected_delivery_date') if bundle_data else None
        bundles = [{'po_number': po_number, 'po_date': po_date, 'expected_delivery_date': expected_delivery}]
    
    # Build items list (simpler for ordered email)
    items_text = ""
    items_html = ""
    
    for idx, item in enumerate(items, 1):
        items_text += f"\n{idx}. {item['item_name']} - {item['quantity']} pieces"
        
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{idx}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>{item['item_name']}</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item['quantity']} pcs</td>
        </tr>
        """
    
    # Build bundles info text
    bundles_text = ""
    if len(bundles) > 1:
        bundles_text = f"\n\nYour items have been ordered from {len(bundles)} vendors:\n"
        for idx, bundle in enumerate(bundles, 1):
            bundles_text += f"\nOrder {idx}:"
            bundles_text += f"\n  PO Number: {bundle.get('po_number', 'TBD')}"
            if bundle.get('expected_delivery_date'):
                bundles_text += f"\n  Expected Delivery: {_format_date(bundle['expected_delivery_date'])}"
    else:
        bundle = bundles[0] if bundles else {}
        bundles_text = f"\n\nORDER INFORMATION:"
        bundles_text += f"\nPO Number: {bundle.get('po_number', 'TBD')}"
        if bundle.get('expected_delivery_date'):
            bundles_text += f"\nExpected Delivery: {_format_date(bundle['expected_delivery_date'])}"
    
    # Plain text body
    body_text = f"""
Hi {user['full_name']},

Great news! Your material request has been ordered.

REQUEST DETAILS:
Request Number: {request['req_number']}
Status: Ordered
{bundles_text}

ITEMS ORDERED:
{items_text}

We'll notify you when your items arrive.

If you have any questions, please contact the procurement team.

---
This is an automated notification from the Requirements Management System.
"""
    
    # HTML body
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">📦 Your Items Have Been Ordered</h2>
            
            <p>Hi {user['full_name']},</p>
            
            <p>Great news! Your material request has been ordered.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #4CAF50;">Request Details</h3>
                <p style="margin: 5px 0;"><strong>Request Number:</strong> {request['req_number']}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #4CAF50; font-weight: bold;">Ordered</span></p>
            </div>
            
            {''.join([f'''
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4CAF50;">
                <h3 style="margin-top: 0; color: #2e7d32;">Order {idx if len(bundles) > 1 else ""} Information</h3>
                <p style="margin: 5px 0;"><strong>PO Number:</strong> {bundle.get('po_number', 'TBD')}</p>
                <p style="margin: 5px 0;"><strong>Expected Delivery:</strong> {_format_date(bundle.get('expected_delivery_date')) if bundle.get('expected_delivery_date') else 'TBD'}</p>
            </div>
            ''' for idx, bundle in enumerate(bundles, 1)])}
            
            <h3 style="color: #4CAF50;">Items Ordered</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #4CAF50; color: white;">
                        <th style="padding: 10px; text-align: left;">#</th>
                        <th style="padding: 10px; text-align: left;">Item</th>
                        <th style="padding: 10px; text-align: left;">Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <p style="margin-top: 30px;">We'll notify you when your items arrive.</p>
            
            <p>If you have any questions, please contact the procurement team.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 12px; color: #666;">This is an automated notification from the Requirements Management System.</p>
        </div>
    </body>
    </html>
    """
    
    return subject, body_text, html_body


def _build_completed_email(user, request, items, bundle_data):
    """Build email for 'Completed' status"""
    
    subject = "✅ Your Items Are Ready for Pickup!"
    
    # Get bundles info (can be multiple bundles)
    bundles = bundle_data.get('bundles', []) if bundle_data else []
    
    # If no bundles data (backward compatibility), use old format
    if not bundles:
        actual_delivery = bundle_data.get('actual_delivery_date') if bundle_data else None
        packing_slip = bundle_data.get('packing_slip_code', 'N/A') if bundle_data else 'N/A'
        bundles = [{'packing_slip_code': packing_slip, 'actual_delivery_date': actual_delivery}]
    
    # Build items list
    items_text = ""
    items_html = ""
    
    for idx, item in enumerate(items, 1):
        items_text += f"\n{idx}. {item['item_name']} - {item['quantity']} pieces"
        
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{idx}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>{item['item_name']}</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{item['quantity']} pcs</td>
        </tr>
        """
    
    # Build bundles info text
    bundles_text = ""
    if len(bundles) > 1:
        bundles_text = f"\n\nYour items arrived in {len(bundles)} deliveries:\n"
        for idx, bundle in enumerate(bundles, 1):
            bundles_text += f"\nDelivery {idx}:"
            if bundle.get('packing_slip_code'):
                bundles_text += f"\n  Packing Slip: {bundle['packing_slip_code']}"
            if bundle.get('actual_delivery_date'):
                bundles_text += f"\n  Delivery Date: {_format_date(bundle['actual_delivery_date'])}"
    else:
        bundle = bundles[0] if bundles else {}
        bundles_text = f"\n\nDELIVERY INFORMATION:"
        if bundle.get('packing_slip_code'):
            bundles_text += f"\nPacking Slip: {bundle['packing_slip_code']}"
        if bundle.get('actual_delivery_date'):
            bundles_text += f"\nDelivery Date: {_format_date(bundle['actual_delivery_date'])}"
    
    # Plain text body
    body_text = f"""
Hi {user['full_name']},

Excellent news! Your material request is complete and ready for pickup.

REQUEST DETAILS:
Request Number: {request['req_number']}
Status: Completed
{bundles_text}

ITEMS READY:
{items_text}

Please collect your items from the procurement team at your earliest convenience.

If you have any questions, please contact the procurement team.

---
This is an automated notification from the Requirements Management System.
"""
    
    # HTML body
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">✅ Your Items Are Ready for Pickup!</h2>
            
            <p>Hi {user['full_name']},</p>
            
            <p>Excellent news! Your material request is complete and ready for pickup.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #4CAF50;">Request Details</h3>
                <p style="margin: 5px 0;"><strong>Request Number:</strong> {request['req_number']}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #4CAF50; font-weight: bold;">Completed</span></p>
            </div>
            
            {''.join([f'''
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4CAF50;">
                <h3 style="margin-top: 0; color: #2e7d32;">Delivery {idx if len(bundles) > 1 else ""} Information</h3>
                <p style="margin: 5px 0;"><strong>Packing Slip:</strong> {bundle.get('packing_slip_code', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Delivery Date:</strong> {_format_date(bundle.get('actual_delivery_date')) if bundle.get('actual_delivery_date') else 'Today'}</p>
            </div>
            ''' for idx, bundle in enumerate(bundles, 1)])}
            
            <h3 style="color: #4CAF50;">Items Ready</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #4CAF50; color: white;">
                        <th style="padding: 10px; text-align: left;">#</th>
                        <th style="padding: 10px; text-align: left;">Item</th>
                        <th style="padding: 10px; text-align: left;">Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0;"><strong>📍 Next Step:</strong> Please collect your items from the procurement team at your earliest convenience.</p>
            </div>
            
            <p>If you have any questions, please contact the procurement team.</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 12px; color: #666;">This is an automated notification from the Requirements Management System.</p>
        </div>
    </body>
    </html>
    """
    
    return subject, body_text, html_body
