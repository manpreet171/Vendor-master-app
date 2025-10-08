import pyodbc
import os
import json
import streamlit as st
from dotenv import load_dotenv

class DatabaseConnector:
    def __init__(self):
        """Initialize database connection using Phase 2's proven pattern"""
        load_dotenv()
        
        # Use Phase 2's proven secrets management approach
        try:
            # For Streamlit Cloud deployment (same as Phase 2)
            self.server = st.secrets["azure_sql"]["AZURE_DB_SERVER"]
            self.database = st.secrets["azure_sql"]["AZURE_DB_NAME"]
            self.username = st.secrets["azure_sql"]["AZURE_DB_USERNAME"]
            self.password = st.secrets["azure_sql"]["AZURE_DB_PASSWORD"]
            self.driver = st.secrets["azure_sql"]["AZURE_DB_DRIVER"]
        except Exception:
            # Fallback to environment variables (same pattern as Phase 2)
            self.server = os.getenv('AZURE_DB_SERVER', 'dw-sqlsvr.database.windows.net')
            self.database = os.getenv('AZURE_DB_NAME', 'dw-sqldb')
            self.username = os.getenv('AZURE_DB_USERNAME', 'manpreet')
            self.password = os.getenv('AZURE_DB_PASSWORD', 'xxxx')
            self.driver = os.getenv('AZURE_DB_DRIVER', '{ODBC Driver 18 for SQL Server}')
        
        self.conn = None
        self.cursor = None
        self.connection_error = None
        self.connect()
    
    def connect(self):
        """Connect to Azure SQL Database"""
        try:
            # Try multiple driver versions for compatibility
            drivers_to_try = [
                self.driver,
                '{ODBC Driver 18 for SQL Server}',
                '{ODBC Driver 17 for SQL Server}',
                '{SQL Server}'
            ]
            
            for driver in drivers_to_try:
                try:
                    connection_string = f"DRIVER={driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
                    self.conn = pyodbc.connect(connection_string)
                    self.cursor = self.conn.cursor()
                    self.connection_error = None
                    return
                except Exception:
                    continue
            
            # If all drivers failed
            raise Exception("Unable to connect with available ODBC drivers")
            
        except Exception as e:
            error_msg = str(e)
            self.connection_error = error_msg
            self.conn = None
            self.cursor = None
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        if not self.conn:
            return []
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Fetch all results
            columns = [column[0] for column in self.cursor.description]
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            print(f"Query execution error: {str(e)}")
            return []
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT/UPDATE/DELETE query"""
        if not self.conn:
            raise Exception("No database connection")
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Don't commit here - let the calling function handle commits
            return True
            
        except Exception as e:
            print(f"Insert execution error: {str(e)}")
            raise
    
    def execute_non_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries"""
        if not self.conn:
            return False
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            st.error(f"Query execution error: {str(e)}")
            return False
    
    def get_last_insert_id(self):
        """Get the last inserted ID"""
        try:
            self.cursor.execute("SELECT @@IDENTITY")
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception:
            return None
    
    # Phase 3 specific methods for requirements system
    
    def authenticate_user(self, username, password):
        """Authenticate user against requirements_users table"""
        query = """
        SELECT user_id, username, full_name, email, department, user_role, is_active
        FROM requirements_users 
        WHERE username = ? AND password_hash = ? AND is_active = 1
        """
        results = self.execute_query(query, (username, password))
        return results[0] if results else None
    
    def get_all_items(self, source_filter=None):
        """Get items from Phase 2's items table (reusing proven logic)"""
        query = "SELECT * FROM items"
        if source_filter:
            query += " WHERE source_sheet = ?"
            return self.execute_query(query, (source_filter,))
        return self.execute_query(query)
    
    def get_item_vendors(self, item_id):
        """Get vendors for an item (reusing Phase 2's logic)"""
        query = """
        SELECT v.*, ivm.cost 
        FROM vendors v 
        JOIN item_vendor_mapping ivm ON v.vendor_id = ivm.vendor_id 
        WHERE ivm.item_id = ?
        """
        return self.execute_query(query, (item_id,))
    
    def get_bundle_item_project_breakdown(self, bundle_id, item_id):
        """Get project breakdown for a specific item in a bundle"""
        query = """
        SELECT roi.project_number, roi.quantity, ro.user_id
        FROM requirements_bundle_mapping rbm
        JOIN requirements_orders ro ON rbm.req_id = ro.req_id
        JOIN requirements_order_items roi ON ro.req_id = roi.req_id
        WHERE rbm.bundle_id = ? AND roi.item_id = ?
        """
        return self.execute_query(query, (bundle_id, item_id))
    
    def get_previous_sub_projects(self, parent_project):
        """
        Get previously used sub-project numbers for a parent project.
        For letter-based projects like 'CP-2025', returns list of sub-projects used before.
        
        Args:
            parent_project: Parent project ID (e.g., 'CP-2025')
        
        Returns:
            List of unique sub-project numbers (e.g., ['25-3456', '25-7890'])
        """
        try:
            query = """
            SELECT DISTINCT sub_project_number
            FROM requirements_order_items
            WHERE parent_project_id = ?
            AND sub_project_number IS NOT NULL
            ORDER BY sub_project_number DESC
            """
            results = self.execute_query(query, (parent_project,))
            
            # Extract sub-project numbers
            sub_projects = []
            for row in results:
                sub_project_number = row['sub_project_number']
                if sub_project_number:
                    sub_projects.append(sub_project_number)
            
            return sub_projects
        except Exception as e:
            print(f"Error getting previous sub-projects: {str(e)}")
            return []
    
    def detect_duplicate_projects_in_bundle(self, bundle_id):
        """
        Detect items where multiple users requested same item for same project.
        Returns list of duplicates with format:
        [{
            'item_id': int,
            'item_name': str,
            'project_number': str,
            'users': [{'user_id': int, 'quantity': int}, ...]
        }]
        """
        query = """
        SELECT 
            roi.item_id,
            i.item_name,
            roi.project_number,
            ro.user_id,
            roi.quantity
        FROM requirements_bundle_mapping rbm
        JOIN requirements_orders ro ON rbm.req_id = ro.req_id
        JOIN requirements_order_items roi ON ro.req_id = roi.req_id
        JOIN items i ON roi.item_id = i.item_id
        WHERE rbm.bundle_id = ? AND roi.project_number IS NOT NULL
        ORDER BY roi.item_id, roi.project_number
        """
        
        results = self.execute_query(query, (bundle_id,))
        
        if not results:
            return []
        
        # Group by (item_id, project_number)
        grouped = {}
        for row in results:
            key = (row['item_id'], row['project_number'])
            if key not in grouped:
                grouped[key] = {
                    'item_id': row['item_id'],
                    'item_name': row['item_name'],
                    'project_number': row['project_number'],
                    'users': []
                }
            grouped[key]['users'].append({
                'user_id': row['user_id'],
                'quantity': row['quantity']
            })
        
        # Filter to only duplicates (multiple users for same item+project)
        duplicates = [v for v in grouped.values() if len(v['users']) > 1]
        return duplicates
    
    def update_bundle_item_user_quantity(self, bundle_id, item_id, user_id, new_quantity):
        """
        Update a specific user's quantity for an item in a bundle.
        Updates the original order item and recalculates bundle totals.
        """
        try:
            import json
            
            # Step 1: Find the specific order item to update
            find_query = """
            SELECT roi.req_id, roi.quantity as current_qty
            FROM requirements_bundle_mapping rbm
            JOIN requirements_orders ro ON rbm.req_id = ro.req_id
            JOIN requirements_order_items roi ON ro.req_id = roi.req_id
            WHERE rbm.bundle_id = ? 
              AND roi.item_id = ? 
              AND ro.user_id = ?
            """
            find_result = self.execute_query(find_query, (bundle_id, item_id, user_id))
            
            if not find_result:
                return {'success': False, 'error': f'Order item not found for user {user_id}'}
            
            req_id = find_result[0]['req_id']
            old_qty = find_result[0]['current_qty']
            
            # Step 2: Update the original order item
            if new_quantity > 0:
                update_order_query = """
                UPDATE requirements_order_items
                SET quantity = ?
                WHERE req_id = ? AND item_id = ?
                """
                self.execute_insert(update_order_query, (new_quantity, req_id, item_id))
            else:
                # Remove the item if quantity is 0
                delete_order_query = """
                DELETE FROM requirements_order_items
                WHERE req_id = ? AND item_id = ?
                """
                self.execute_insert(delete_order_query, (req_id, item_id))
            
            # Step 3: Recalculate bundle item totals
            # Get all remaining quantities for this item in the bundle
            recalc_query = """
            SELECT ro.user_id, roi.quantity
            FROM requirements_bundle_mapping rbm
            JOIN requirements_orders ro ON rbm.req_id = ro.req_id
            JOIN requirements_order_items roi ON ro.req_id = roi.req_id
            WHERE rbm.bundle_id = ? AND roi.item_id = ?
            """
            recalc_result = self.execute_query(recalc_query, (bundle_id, item_id))
            
            if recalc_result:
                # Rebuild user_breakdown
                user_breakdown = {}
                for row in recalc_result:
                    uid = str(row['user_id'])
                    user_breakdown[uid] = user_breakdown.get(uid, 0) + row['quantity']
                
                new_total = sum(user_breakdown.values())
                
                # Update bundle item
                update_bundle_query = """
                UPDATE requirements_bundle_items
                SET user_breakdown = ?, total_quantity = ?
                WHERE bundle_id = ? AND item_id = ?
                """
                self.execute_insert(update_bundle_query, (json.dumps(user_breakdown), new_total, bundle_id, item_id))
            else:
                # No items left, remove from bundle
                delete_bundle_query = """
                DELETE FROM requirements_bundle_items
                WHERE bundle_id = ? AND item_id = ?
                """
                self.execute_insert(delete_bundle_query, (bundle_id, item_id))
            
            self.conn.commit()
            
            return {
                'success': True,
                'old_quantity': old_qty,
                'new_quantity': new_quantity,
                'new_total': new_total if recalc_result else 0
            }
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"ERROR in update_bundle_item_user_quantity: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def mark_bundle_duplicates_reviewed(self, bundle_id):
        """Mark bundle as having duplicates reviewed by operator"""
        try:
            query = """
            UPDATE requirements_bundles
            SET duplicates_reviewed = 1
            WHERE bundle_id = ?
            """
            self.execute_insert(query, (bundle_id,))
            self.conn.commit()
            return True
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error marking duplicates reviewed: {str(e)}")
            return False
    
    # ========== Bundle Issue Resolution Functions ==========
    
    def get_alternative_vendors_for_item(self, item_id, exclude_vendor_id):
        """Get vendors who can supply this item, excluding current vendor"""
        query = """
        SELECT v.vendor_id, v.vendor_name, v.vendor_email, v.vendor_phone
        FROM Vendors v
        JOIN ItemVendorMap ivm ON v.vendor_id = ivm.vendor_id
        WHERE ivm.item_id = ? AND v.vendor_id != ?
        ORDER BY v.vendor_name
        """
        return self.execute_query(query, (item_id, exclude_vendor_id))
    
    def get_active_bundle_for_vendor(self, vendor_id):
        """Check if vendor already has an ACTIVE or REVIEWED bundle (not Approved - those are locked)"""
        query = """
        SELECT bundle_id, bundle_name, total_items, total_quantity, status
        FROM requirements_bundles
        WHERE recommended_vendor_id = ? 
          AND status IN ('Active', 'Reviewed')
        ORDER BY bundle_id DESC
        """
        results = self.execute_query(query, (vendor_id,))
        return results[0] if results else None
    
    def get_bundles_for_request(self, req_id):
        """Get all bundles that contain items from this request"""
        query = """
        SELECT DISTINCT b.bundle_id, b.bundle_name, b.status, b.recommended_vendor_id
        FROM requirements_bundles b
        JOIN requirements_bundle_mapping rbm ON b.bundle_id = rbm.bundle_id
        WHERE rbm.req_id = ?
        ORDER BY b.bundle_id
        """
        return self.execute_query(query, (req_id,))
    
    def move_item_to_vendor(self, current_bundle_id, item_id, new_vendor_id):
        """
        Move item from current bundle to vendor's bundle.
        If vendor bundle exists, add item there. Otherwise create new bundle.
        Returns: {'success': bool, 'target_bundle_id': int, 'message': str}
        """
        try:
            import json
            from datetime import datetime
            
            # Step 1: Recalculate item data from SOURCE order items (not bundle)
            # This ensures we get the latest quantities after duplicate reviews
            recalc_query = """
            SELECT 
                roi.item_id,
                ro.user_id,
                roi.quantity
            FROM requirements_bundle_mapping rbm
            JOIN requirements_orders ro ON rbm.req_id = ro.req_id
            JOIN requirements_order_items roi ON ro.req_id = roi.req_id
            WHERE rbm.bundle_id = ? AND roi.item_id = ?
            """
            recalc_results = self.execute_query(recalc_query, (current_bundle_id, item_id))
            
            if not recalc_results:
                return {'success': False, 'error': 'Item not found in bundle'}
            
            # Build fresh user_breakdown from source data
            user_breakdown = {}
            total_quantity = 0
            for row in recalc_results:
                user_id = str(row['user_id'])
                quantity = row['quantity']
                user_breakdown[user_id] = quantity
                total_quantity += quantity
            
            item_data = {
                'item_id': item_id,
                'total_quantity': total_quantity,
                'user_breakdown': json.dumps(user_breakdown)
            }
            
            # Step 2: Check if vendor already has a bundle
            existing_bundle = self.get_active_bundle_for_vendor(new_vendor_id)
            
            if existing_bundle:
                # CASE A: Add to existing bundle
                target_bundle_id = existing_bundle['bundle_id']
                
                # Add item to existing bundle
                insert_query = """
                INSERT INTO requirements_bundle_items 
                (bundle_id, item_id, total_quantity, user_breakdown)
                VALUES (?, ?, ?, ?)
                """
                self.execute_insert(insert_query, (
                    target_bundle_id,
                    item_data['item_id'],
                    item_data['total_quantity'],
                    item_data['user_breakdown']
                ))
                
                # Update bundle totals
                update_bundle_query = """
                UPDATE requirements_bundles
                SET total_items = total_items + 1,
                    total_quantity = total_quantity + ?
                WHERE bundle_id = ?
                """
                self.execute_insert(update_bundle_query, (
                    item_data['total_quantity'],
                    target_bundle_id
                ))
                
                # AUTO-REVERT: If bundle was Reviewed, revert to Active (bundle changed)
                if existing_bundle.get('status') == 'Reviewed':
                    revert_query = """
                    UPDATE requirements_bundles
                    SET status = 'Active'
                    WHERE bundle_id = ?
                    """
                    self.execute_insert(revert_query, (target_bundle_id,))
                    message = f"Item added to existing bundle {existing_bundle['bundle_name']} (reverted to Active for re-review)"
                else:
                    message = f"Item added to existing bundle {existing_bundle['bundle_name']}"
                
            else:
                # CASE B: Create new bundle
                # Get vendor info
                vendor_query = """
                SELECT vendor_name FROM vendors WHERE vendor_id = ?
                """
                vendor_result = self.execute_query(vendor_query, (new_vendor_id,))
                
                if not vendor_result:
                    return {'success': False, 'error': 'Vendor not found'}
                
                vendor_name = vendor_result[0]['vendor_name']
                
                # Create new bundle
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                bundle_name = f"BUNDLE-{timestamp}"
                
                create_bundle_query = """
                INSERT INTO requirements_bundles 
                (bundle_name, recommended_vendor_id, total_items, total_quantity, status, duplicates_reviewed)
                VALUES (?, ?, 1, ?, 'Active', 0)
                """
                self.execute_insert(create_bundle_query, (
                    bundle_name,
                    new_vendor_id,
                    item_data['total_quantity']
                ))
                
                # Get new bundle ID
                target_bundle_id = self.execute_query(
                    "SELECT MAX(bundle_id) as bundle_id FROM requirements_bundles"
                )[0]['bundle_id']
                
                # Add item to new bundle
                insert_query = """
                INSERT INTO requirements_bundle_items 
                (bundle_id, item_id, total_quantity, user_breakdown)
                VALUES (?, ?, ?, ?)
                """
                self.execute_insert(insert_query, (
                    target_bundle_id,
                    item_data['item_id'],
                    item_data['total_quantity'],
                    item_data['user_breakdown']
                ))
                
                message = f"Created new bundle {bundle_name} for {vendor_name}"
            
            # Step 3: Link requests from current bundle to target bundle
            # Get requests from current bundle
            get_requests_query = """
            SELECT DISTINCT req_id 
            FROM requirements_bundle_mapping 
            WHERE bundle_id = ?
            """
            requests = self.execute_query(get_requests_query, (current_bundle_id,))
            
            if requests:
                for req in requests:
                    req_id = req['req_id']
                    
                    # Check if already linked
                    check_query = """
                    SELECT COUNT(*) as count 
                    FROM requirements_bundle_mapping 
                    WHERE bundle_id = ? AND req_id = ?
                    """
                    exists = self.execute_query(check_query, (target_bundle_id, req_id))[0]['count']
                    
                    if exists == 0:
                        # Link it
                        insert_mapping_query = """
                        INSERT INTO requirements_bundle_mapping (bundle_id, req_id)
                        VALUES (?, ?)
                        """
                        self.execute_insert(insert_mapping_query, (target_bundle_id, req_id))
            
            # Step 4: Remove item from current bundle
            delete_query = """
            DELETE FROM requirements_bundle_items
            WHERE bundle_id = ? AND item_id = ?
            """
            self.execute_insert(delete_query, (current_bundle_id, item_id))
            
            # Update current bundle totals
            update_current_query = """
            UPDATE requirements_bundles
            SET total_items = total_items - 1,
                total_quantity = total_quantity - ?
            WHERE bundle_id = ?
            """
            self.execute_insert(update_current_query, (
                item_data['total_quantity'],
                current_bundle_id
            ))
            
            # Step 5: Check if current bundle is now empty
            check_empty_query = """
            SELECT COUNT(*) as count 
            FROM requirements_bundle_items 
            WHERE bundle_id = ?
            """
            item_count = self.execute_query(check_empty_query, (current_bundle_id,))[0]['count']
            
            if item_count == 0:
                # Delete empty bundle
                self.execute_insert("DELETE FROM requirements_bundle_mapping WHERE bundle_id = ?", (current_bundle_id,))
                self.execute_insert("DELETE FROM requirements_bundles WHERE bundle_id = ?", (current_bundle_id,))
                message += " (Original bundle was empty and removed)"
            
            self.conn.commit()
            
            return {
                'success': True,
                'target_bundle_id': target_bundle_id,
                'message': message
            }
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"ERROR in move_item_to_vendor: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    # ========== Order Placement Functions ==========
    
    def get_bundle_item_costs(self, bundle_id):
        """Get current costs for all items in bundle from ItemVendorMap"""
        query = """
        SELECT 
            bi.item_id,
            i.item_name,
            bi.total_quantity,
            ivm.cost,
            ivm.last_cost_update,
            v.vendor_id
        FROM requirements_bundle_items bi
        JOIN Items i ON bi.item_id = i.item_id
        JOIN requirements_bundles b ON bi.bundle_id = b.bundle_id
        JOIN Vendors v ON b.recommended_vendor_id = v.vendor_id
        LEFT JOIN ItemVendorMap ivm ON bi.item_id = ivm.item_id AND v.vendor_id = ivm.vendor_id
        WHERE bi.bundle_id = ?
        ORDER BY i.item_name
        """
        return self.execute_query(query, (bundle_id,))
    
    def save_order_placement(self, bundle_id, po_number, item_costs):
        """
        Save order placement: PO number and update item costs
        item_costs: dict {item_id: cost}
        Returns: {'success': bool, 'message': str}
        """
        try:
            from datetime import datetime
            
            # Step 1: Get vendor_id from bundle
            vendor_query = """
            SELECT recommended_vendor_id 
            FROM requirements_bundles 
            WHERE bundle_id = ?
            """
            vendor_result = self.execute_query(vendor_query, (bundle_id,))
            
            if not vendor_result:
                return {'success': False, 'error': 'Bundle not found'}
            
            vendor_id = vendor_result[0]['recommended_vendor_id']
            
            # Step 2: Update bundle with PO info and status
            update_bundle_query = """
            UPDATE requirements_bundles
            SET po_number = ?,
                po_date = ?,
                status = 'Ordered'
            WHERE bundle_id = ?
            """
            self.execute_insert(update_bundle_query, (po_number, datetime.now(), bundle_id))
            
            # Step 3: Update costs in ItemVendorMap
            for item_id, cost in item_costs.items():
                # Check if mapping exists
                check_query = """
                SELECT map_id FROM ItemVendorMap 
                WHERE item_id = ? AND vendor_id = ?
                """
                existing = self.execute_query(check_query, (item_id, vendor_id))
                
                if existing:
                    # Update existing
                    update_cost_query = """
                    UPDATE ItemVendorMap
                    SET cost = ?,
                        last_cost_update = ?
                    WHERE item_id = ? AND vendor_id = ?
                    """
                    self.execute_insert(update_cost_query, (cost, datetime.now(), item_id, vendor_id))
                else:
                    # Insert new mapping
                    insert_cost_query = """
                    INSERT INTO ItemVendorMap (item_id, vendor_id, cost, last_cost_update)
                    VALUES (?, ?, ?, ?)
                    """
                    self.execute_insert(insert_cost_query, (item_id, vendor_id, cost, datetime.now()))
            
            # Step 4: Update request status if all bundles are ordered
            # Get all requests linked to this bundle
            requests_query = """
            SELECT DISTINCT req_id 
            FROM requirements_bundle_mapping 
            WHERE bundle_id = ?
            """
            requests = self.execute_query(requests_query, (bundle_id,))
            
            for req in requests:
                req_id = req['req_id']
                
                # Get all bundles for this request
                all_bundles = self.get_bundles_for_request(req_id)
                
                # Check if ALL bundles are ordered or completed
                all_ordered = all(b['status'] in ('Ordered', 'Completed') for b in all_bundles)
                
                if all_ordered:
                    # All bundles ordered - update request status
                    update_request_query = """
                    UPDATE requirements_orders
                    SET status = 'Ordered'
                    WHERE req_id = ?
                    """
                    self.execute_insert(update_request_query, (req_id,))
            
            self.conn.commit()
            
            return {
                'success': True,
                'message': f'Order placed successfully with PO# {po_number}'
            }
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"ERROR in save_order_placement: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def get_order_details(self, bundle_id):
        """Get order details (PO number, date, costs) for a bundle"""
        query = """
        SELECT 
            b.po_number,
            b.po_date,
            bi.item_id,
            i.item_name,
            bi.total_quantity,
            ivm.cost,
            ivm.last_cost_update
        FROM requirements_bundles b
        JOIN requirements_bundle_items bi ON b.bundle_id = bi.bundle_id
        JOIN Items i ON bi.item_id = i.item_id
        LEFT JOIN ItemVendorMap ivm ON bi.item_id = ivm.item_id AND b.recommended_vendor_id = ivm.vendor_id
        WHERE b.bundle_id = ?
        ORDER BY i.item_name
        """
        return self.execute_query(query, (bundle_id,))
    
    def get_all_projects(self):
        """Get all projects from ProcoreProjectData for dropdown selection"""
        query = """
        SELECT ProjectNumber, ProjectName, ProjectType, ProjectManager, Customer
        FROM ProcoreProjectData
        ORDER BY ProjectName
        """
        return self.execute_query(query)
    
    def get_request_items(self, req_id):
        """Get items for a specific request"""
        query = """
        SELECT 
            ri.item_id,
            ri.quantity, 
            ri.item_notes,
            ri.project_number,
            ri.parent_project_id,
            ri.sub_project_number,
            i.item_name, 
            i.sku,
            i.source_sheet,
            i.height,
            i.width,
            i.thickness
        FROM requirements_order_items ri
        JOIN items i ON ri.item_id = i.item_id
        WHERE ri.req_id = ?
        """
        return self.execute_query(query, (req_id,))
    
    def submit_cart_as_order(self, user_id, cart_items, notes=""):
        """Submit cart items as a new requirements order"""
        try:
            # Generate request number
            req_number = self.generate_request_number()
            
            # Calculate total items
            total_items = sum(item['quantity'] for item in cart_items)
            
            # Insert main order
            order_query = """
            INSERT INTO requirements_orders 
            (req_number, user_id, req_date, status, total_items, notes)
            VALUES (?, ?, GETDATE(), 'Pending', ?, ?)
            """
            
            self.execute_insert(order_query, (req_number, user_id, total_items, notes))
            
            # Get the inserted order ID
            req_id = self.get_last_insert_id()
            
            if not req_id:
                raise Exception("Failed to get order ID")
            
            # Insert order items
            for item in cart_items:
                item_query = """
                INSERT INTO requirements_order_items 
                (req_id, item_id, quantity, item_notes, project_number, parent_project_id, sub_project_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                item_notes = f"Category: {item.get('category', 'Unknown')}"
                self.execute_insert(item_query, (
                    req_id, 
                    item['item_id'], 
                    item['quantity'], 
                    item_notes,
                    item.get('project_number'),
                    item.get('parent_project_id'),
                    item.get('sub_project_number')
                ))
            
            # Commit the transaction
            self.conn.commit()
            return {
                'success': True,
                'req_id': req_id,
                'req_number': req_number,
                'total_items': total_items
            }
            
        except Exception as e:
            # Rollback on error
            if self.conn:
                self.conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_request_number(self):
        """Generate a unique request number"""
        import datetime
        now = datetime.datetime.now()
        
        # Format: REQ-YYYYMMDD-HHMMSS
        req_number = f"REQ-{now.strftime('%Y%m%d-%H%M%S')}"
        
        # Check if exists and add suffix if needed
        check_query = "SELECT COUNT(*) as count FROM requirements_orders WHERE req_number = ?"
        result = self.execute_query(check_query, (req_number,))
        
        if result and result[0]['count'] > 0:
            # Add random suffix if duplicate
            import random
            req_number += f"-{random.randint(100, 999)}"
        
        return req_number
    
    def get_user_requested_item_ids(self, user_id):
        """Get item IDs that user has already requested (pending or in progress)"""
        query = """
        SELECT DISTINCT roi.item_id
        FROM requirements_orders ro
        JOIN requirements_order_items roi ON ro.req_id = roi.req_id
        WHERE ro.user_id = ? AND ro.status IN ('Pending', 'In Progress')
        """
        results = self.execute_query(query, (user_id,))
        return [row['item_id'] for row in results] if results else []
    
    def update_order_item_quantity(self, req_id, item_id, new_quantity):
        """Update quantity for an existing order item"""
        try:
            print(f"Updating req_id={req_id}, item_id={item_id}, new_quantity={new_quantity}")
            
            # Update the item quantity
            update_query = """
            UPDATE requirements_order_items 
            SET quantity = ?
            WHERE req_id = ? AND item_id = ?
            """
            self.execute_insert(update_query, (new_quantity, req_id, item_id))
            print("Item quantity updated")
            
            # Update total items count in the main order
            total_query = """
            UPDATE requirements_orders 
            SET total_items = (
                SELECT SUM(quantity) 
                FROM requirements_order_items 
                WHERE req_id = ?
            )
            WHERE req_id = ?
            """
            self.execute_insert(total_query, (req_id, req_id))
            print("Total items updated")
            
            self.conn.commit()
            print("Changes committed")
            return True
            
        except Exception as e:
            print(f"Error in update_order_item_quantity: {str(e)}")
            if self.conn:
                self.conn.rollback()
            raise Exception(f"Failed to update quantity: {str(e)}")
    
    def get_all_pending_requests(self):
        """Get all pending requests for bundling"""
        query = """
        SELECT ro.req_id, ro.req_number, ro.user_id, ro.req_date, ro.total_items,
               roi.item_id, roi.quantity, roi.project_number, roi.parent_project_id, roi.sub_project_number,
               i.item_name, i.sku, i.source_sheet
        FROM requirements_orders ro
        JOIN requirements_order_items roi ON ro.req_id = roi.req_id
        JOIN items i ON roi.item_id = i.item_id
        WHERE ro.status = 'Pending'
        ORDER BY ro.req_date ASC
        """
        return self.execute_query(query)
    
    def update_requests_to_in_progress(self, req_ids):
        """Update multiple requests status to In Progress"""
        try:
            if not req_ids:
                return False
            
            # Create placeholders for the IN clause
            placeholders = ','.join(['?' for _ in req_ids])
            query = f"""
            UPDATE requirements_orders 
            SET status = 'In Progress'
            WHERE req_id IN ({placeholders})
            """
            
            self.execute_insert(query, req_ids)
            self.conn.commit()
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise Exception(f"Failed to update request status: {str(e)}")
    
    def create_bundle(self, bundle_data):
        """Create a new bundle in the database"""
        try:
            # First, let's check what columns exist in requirements_bundles table
            check_columns_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'requirements_bundles'
            """
            columns_result = self.execute_query(check_columns_query)
            available_columns = [col['COLUMN_NAME'] for col in columns_result] if columns_result else []
            print(f"Available columns in requirements_bundles: {available_columns}")
            
            # Insert main bundle record with available columns including recommended_vendor_id
            bundle_query = """
            INSERT INTO requirements_bundles 
            (bundle_name, status, total_items, total_quantity, recommended_vendor_id)
            VALUES (?, 'Active', ?, ?, ?)
            """
            
            bundle_name = f"BUNDLE-{bundle_data['timestamp']}"
            total_items = len(bundle_data['items'])
            total_quantity = sum(item['quantity'] for item in bundle_data['items'])
            
            # Get the recommended vendor ID from the bundle data
            recommended_vendor_id = None
            if bundle_data.get('vendor_recommendations') and len(bundle_data['vendor_recommendations']) > 0:
                recommended_vendor_id = bundle_data['vendor_recommendations'][0].get('vendor_id')
            
            self.execute_insert(bundle_query, (bundle_name, total_items, total_quantity, recommended_vendor_id))
            
            # Get the inserted bundle ID
            bundle_id = self.get_last_insert_id()
            
            if not bundle_id:
                raise Exception("Failed to get bundle ID")
            
            # Check bundle items table structure
            check_items_columns_query = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'requirements_bundle_items'
            """
            items_columns_result = self.execute_query(check_items_columns_query)
            available_items_columns = [col['COLUMN_NAME'] for col in items_columns_result] if items_columns_result else []
            print(f"Available columns in requirements_bundle_items: {available_items_columns}")
            
            # Insert bundle items with available columns
            for item in bundle_data['items']:
                item_query = """
                INSERT INTO requirements_bundle_items 
                (bundle_id, item_id, total_quantity, user_breakdown)
                VALUES (?, ?, ?, ?)
                """
                
                user_breakdown = json.dumps(item['user_breakdown'], ensure_ascii=True)
                self.execute_insert(item_query, (
                    bundle_id,
                    item['item_id'],
                    item['quantity'],
                    user_breakdown
                ))
            
            # Insert bundle-request mappings
            for req_id in bundle_data['request_ids']:
                mapping_query = """
                INSERT INTO requirements_bundle_mapping 
                (bundle_id, req_id)
                VALUES (?, ?)
                """
                self.execute_insert(mapping_query, (bundle_id, req_id))
            
            self.conn.commit()
            return bundle_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise Exception(f"Failed to create bundle: {str(e)}")
    
    def get_item_vendors(self, item_ids):
        """Get vendors for specific items using Phase 2's item_vendor_mapping"""
        try:
            if not item_ids:
                print("No item IDs provided to get_item_vendors")
                return []
            
            print(f"Looking up vendors for item IDs: {item_ids}")
            
            placeholders = ','.join(['?' for _ in item_ids])
            query = f"""
            SELECT ivm.item_id, ivm.vendor_id, v.vendor_name, v.vendor_email as contact_email, 
                   v.vendor_phone as contact_phone, i.item_name
            FROM ItemVendorMap ivm
            JOIN Vendors v ON ivm.vendor_id = v.vendor_id
            JOIN Items i ON ivm.item_id = i.item_id
            WHERE ivm.item_id IN ({placeholders})
            ORDER BY ivm.item_id, v.vendor_name
            """
            
            print(f"Executing vendor query: {query}")
            result = self.execute_query(query, item_ids)
            print(f"Vendor query returned {len(result) if result else 0} results")
            
            return result
            
        except Exception as e:
            print(f"Error getting item vendors: {str(e)}")
            return []
    
    def reset_system_for_testing(self):
        """Clear all Phase 3 data except users - for testing purposes"""
        try:
            print("Starting system reset for testing...")
            
            # Clear tables in proper order (foreign key dependencies)
            tables_to_clear = [
                'requirements_bundle_mapping',  # Links bundles to requests
                'requirements_bundle_items',    # Items in bundles
                'requirements_bundles',         # Bundles themselves
                'requirements_order_items',     # Items in orders
                'requirements_orders'           # Orders/requests
            ]
            
            for table in tables_to_clear:
                query = f"DELETE FROM {table}"
                self.execute_insert(query, ())
                print(f"Cleared table: {table}")
            
            # Reset identity columns if they exist
            identity_reset_queries = [
                "DBCC CHECKIDENT ('requirements_orders', RESEED, 0)",
                "DBCC CHECKIDENT ('requirements_bundles', RESEED, 0)"
            ]
            
            for reset_query in identity_reset_queries:
                try:
                    self.cursor.execute(reset_query)
                    print(f"Reset identity: {reset_query}")
                except Exception as e:
                    print(f"Identity reset warning (may not exist): {str(e)}")
            
            self.conn.commit()
            print("System reset completed successfully!")
            print("All requests, orders, bundles, and related data cleared.")
            print("Users table preserved - you can login with existing credentials.")
            
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error during system reset: {str(e)}")
            return False

    def check_db_connection(self):
        """Check database connection status (same as Phase 2)"""
        if self.conn:
            try:
                self.cursor.execute("SELECT 1")
                return True, "Connected successfully", {}, {}
            except Exception as e:
                return False, f"Connection test failed: {str(e)}", {}, {"error": str(e)}
        else:
            error_details = {
                "server": self.server,
                "database": self.database,
                "username": self.username,
                "driver": self.driver
            }
            return False, self.connection_error or "No connection", error_details, {"error": self.connection_error}
    
    def close_connection(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # ------------------------------
    # Admin: requirements_users CRUD
    # ------------------------------
    def list_users(self):
        """Return all users for admin management UI"""
        query = """
        SELECT user_id, username, full_name, email, department, user_role, is_active, created_at, last_login
        FROM requirements_users
        ORDER BY created_at DESC
        """
        return self.execute_query(query)

    def get_user_by_username(self, username: str):
        query = """
        SELECT user_id, username FROM requirements_users WHERE username = ?
        """
        res = self.execute_query(query, (username,))
        return res[0] if res else None

    def create_user(self, username: str, password: str, full_name: str, email: str = None, department: str = None, user_role: str = 'User', is_active: int = 1) -> dict:
        """Create a new user. Note: password stored as provided to match current auth behavior."""
        try:
            # Ensure unique username
            existing = self.get_user_by_username(username)
            if existing:
                return {"success": False, "error": "Username already exists"}

            query = """
            INSERT INTO requirements_users (username, password_hash, full_name, email, department, user_role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            self.execute_insert(query, (username, password, full_name, email, department, user_role, is_active))
            self.conn.commit()
            return {"success": True}
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return {"success": False, "error": str(e)}

    def update_user_profile(self, user_id: int, full_name: str, email: str, department: str) -> bool:
        try:
            query = """
            UPDATE requirements_users
            SET full_name = ?, email = ?, department = ?
            WHERE user_id = ?
            """
            self.execute_insert(query, (full_name, email, department, user_id))
            self.conn.commit()
            return True
        except Exception:
            if self.conn:
                self.conn.rollback()
            return False

    def set_user_role(self, user_id: int, role: str) -> bool:
        try:
            query = """
            UPDATE requirements_users SET user_role = ? WHERE user_id = ?
            """
            self.execute_insert(query, (role, user_id))
            self.conn.commit()
            return True
        except Exception:
            if self.conn:
                self.conn.rollback()
            return False

    def set_user_active(self, user_id: int, is_active: bool) -> bool:
        try:
            query = """
            UPDATE requirements_users SET is_active = ? WHERE user_id = ?
            """
            self.execute_insert(query, (1 if is_active else 0, user_id))
            self.conn.commit()
            return True
        except Exception:
            if self.conn:
                self.conn.rollback()
            return False

    def reset_user_password(self, user_id: int, new_password: str) -> bool:
        try:
            query = """
            UPDATE requirements_users SET password_hash = ? WHERE user_id = ?
            """
            self.execute_insert(query, (new_password, user_id))
            self.conn.commit()
            return True
        except Exception:
            if self.conn:
                self.conn.rollback()
            return False

    def delete_user(self, user_id: int) -> bool:
        """Attempt to delete a user. Will fail if foreign key constraints exist."""
        try:
            query = """
            DELETE FROM requirements_users WHERE user_id = ?
            """
            self.execute_insert(query, (user_id,))
            self.conn.commit()
            return True
        except Exception:
            if self.conn:
                self.conn.rollback()
            return False
    
    def mark_bundle_reviewed(self, bundle_id):
        """Mark bundle as reviewed (Active → Reviewed) - Individual review only"""
        try:
            update_q = """
            UPDATE requirements_bundles
            SET status = 'Reviewed'
            WHERE bundle_id = ? AND status = 'Active'
            """
            self.execute_insert(update_q, (bundle_id,))
            self.conn.commit()
            return True
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error marking bundle as reviewed: {str(e)}")
            return False
    
    def mark_bundles_approved_bulk(self, bundle_ids):
        """Approve multiple bundles at once (only if they are Reviewed)"""
        try:
            if not bundle_ids:
                return {'success': False, 'error': 'No bundles selected'}
            
            placeholders = ','.join(['?' for _ in bundle_ids])
            
            # First check if all bundles are Reviewed
            check_q = f"""
            SELECT bundle_id, status 
            FROM requirements_bundles
            WHERE bundle_id IN ({placeholders})
            """
            bundles = self.execute_query(check_q, tuple(bundle_ids))
            
            non_reviewed = [b for b in bundles if b['status'] != 'Reviewed']
            if non_reviewed:
                return {
                    'success': False, 
                    'error': f"{len(non_reviewed)} bundle(s) are not Reviewed yet"
                }
            
            # All are reviewed, proceed with approval
            update_q = f"""
            UPDATE requirements_bundles
            SET status = 'Approved'
            WHERE bundle_id IN ({placeholders})
              AND status = 'Reviewed'
            """
            self.execute_insert(update_q, tuple(bundle_ids))
            self.conn.commit()
            return {'success': True, 'approved_count': len(bundle_ids)}
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Error approving bundles: {str(e)}")
            return {'success': False, 'error': str(e)}
