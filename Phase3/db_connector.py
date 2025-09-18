import pyodbc
import streamlit as st
from dotenv import load_dotenv
import os

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
    
    def get_request_items(self, req_id):
        """Get items for a specific request"""
        query = """
        SELECT ri.quantity, ri.item_notes, i.item_name, i.sku
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
                (req_id, item_id, quantity, item_notes)
                VALUES (?, ?, ?, ?)
                """
                
                item_notes = f"Category: {item.get('category', 'Unknown')}"
                self.execute_insert(item_query, (req_id, item['item_id'], item['quantity'], item_notes))
            
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
