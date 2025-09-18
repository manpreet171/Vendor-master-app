# Phase 3 System Validator - Comprehensive Review and Testing
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_connector import DatabaseConnector
from bundling_engine import SmartBundlingEngine
import json

class SystemValidator:
    def __init__(self):
        self.db = DatabaseConnector()
        self.issues = []
        self.warnings = []
        
    def log_issue(self, category, message):
        """Log a critical issue"""
        self.issues.append(f"[{category}] {message}")
        print(f"ISSUE [{category}]: {message}")
    
    def log_warning(self, category, message):
        """Log a warning"""
        self.warnings.append(f"[{category}] {message}")
        print(f"WARNING [{category}]: {message}")
    
    def log_success(self, category, message):
        """Log a success"""
        print(f"SUCCESS [{category}]: {message}")
    
    def validate_database_connection(self):
        """Test database connectivity"""
        print("\nVALIDATING DATABASE CONNECTION...")
        
        if not self.db.conn:
            self.log_issue("DATABASE", f"Connection failed: {self.db.connection_error}")
            return False
        
        try:
            self.db.cursor.execute("SELECT 1")
            self.log_success("DATABASE", "Connection successful")
            return True
        except Exception as e:
            self.log_issue("DATABASE", f"Connection test failed: {str(e)}")
            return False
    
    def validate_phase2_tables(self):
        """Validate Phase 2 table structure and data"""
        print("\nVALIDATING PHASE 2 TABLES...")
        
        required_tables = ['Items', 'Vendors', 'ItemVendorMap']
        
        for table in required_tables:
            try:
                # Check if table exists
                check_query = f"""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = '{table}'
                """
                result = self.db.execute_query(check_query)
                
                if not result or result[0]['count'] == 0:
                    self.log_issue("PHASE2_TABLES", f"Table '{table}' does not exist")
                    continue
                
                # Check table has data
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                count_result = self.db.execute_query(count_query)
                count = count_result[0]['count'] if count_result else 0
                
                if count == 0:
                    self.log_warning("PHASE2_TABLES", f"Table '{table}' exists but is empty")
                else:
                    self.log_success("PHASE2_TABLES", f"Table '{table}' exists with {count} records")
                    
            except Exception as e:
                self.log_issue("PHASE2_TABLES", f"Error checking table '{table}': {str(e)}")
    
    def validate_phase3_tables(self):
        """Validate Phase 3 table structure"""
        print("\nVALIDATING PHASE 3 TABLES...")
        
        required_tables = {
            'requirements_users': ['user_id', 'username', 'password_hash'],
            'requirements_orders': ['req_id', 'user_id', 'status'],
            'requirements_order_items': ['req_id', 'item_id', 'quantity'],
            'requirements_bundles': ['bundle_id', 'bundle_name', 'status'],
            'requirements_bundle_items': ['bundle_id', 'item_id', 'total_quantity'],
            'requirements_bundle_mapping': ['bundle_id', 'req_id']
        }
        
        for table, required_columns in required_tables.items():
            try:
                # Check if table exists
                check_query = f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table}'
                """
                result = self.db.execute_query(check_query)
                
                if not result:
                    self.log_issue("PHASE3_TABLES", f"Table '{table}' does not exist")
                    continue
                
                existing_columns = [col['COLUMN_NAME'] for col in result]
                
                # Check required columns
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                if missing_columns:
                    self.log_issue("PHASE3_TABLES", f"Table '{table}' missing columns: {missing_columns}")
                else:
                    self.log_success("PHASE3_TABLES", f"Table '{table}' has all required columns")
                
                # Show all available columns
                print(f"    Available columns in {table}: {existing_columns}")
                    
            except Exception as e:
                self.log_issue("PHASE3_TABLES", f"Error checking table '{table}': {str(e)}")
    
    def validate_vendor_mapping_logic(self):
        """Test vendor mapping logic"""
        print("\nVALIDATING VENDOR MAPPING LOGIC...")
        
        try:
            # Get sample items
            items_query = "SELECT TOP 5 item_id, item_name FROM Items"
            items = self.db.execute_query(items_query)
            
            if not items:
                self.log_warning("VENDOR_MAPPING", "No items found in Items table")
                return
            
            item_ids = [item['item_id'] for item in items]
            
            # Test vendor lookup
            vendors = self.db.get_item_vendors(item_ids)
            
            if not vendors:
                self.log_warning("VENDOR_MAPPING", f"No vendors found for items: {item_ids}")
                
                # Check if ItemVendorMap has any data
                mapping_query = "SELECT COUNT(*) as count FROM ItemVendorMap"
                mapping_result = self.db.execute_query(mapping_query)
                mapping_count = mapping_result[0]['count'] if mapping_result else 0
                
                if mapping_count == 0:
                    self.log_issue("VENDOR_MAPPING", "ItemVendorMap table is empty - no vendor mappings exist")
                else:
                    self.log_warning("VENDOR_MAPPING", f"ItemVendorMap has {mapping_count} mappings but none for tested items")
            else:
                self.log_success("VENDOR_MAPPING", f"Found {len(vendors)} vendor mappings for {len(item_ids)} items")
                
                # Show sample mappings
                for vendor in vendors[:3]:  # Show first 3
                    print(f"    Item {vendor['item_id']} ({vendor['item_name']}) -> Vendor {vendor['vendor_id']} ({vendor['vendor_name']})")
                    
        except Exception as e:
            self.log_issue("VENDOR_MAPPING", f"Error testing vendor mapping: {str(e)}")
    
    def validate_bundling_engine(self):
        """Test bundling engine logic"""
        print("\nVALIDATING BUNDLING ENGINE...")
        
        try:
            # Check if there are pending requests
            pending_query = """
            SELECT COUNT(*) as count 
            FROM requirements_orders 
            WHERE status = 'Pending'
            """
            pending_result = self.db.execute_query(pending_query)
            pending_count = pending_result[0]['count'] if pending_result else 0
            
            if pending_count == 0:
                self.log_warning("BUNDLING_ENGINE", "No pending requests found - cannot test bundling")
                return
            
            self.log_success("BUNDLING_ENGINE", f"Found {pending_count} pending requests for testing")
            
            # Test bundling engine initialization
            engine = SmartBundlingEngine()
            
            # Test aggregation logic
            pending_requests = self.db.get_all_pending_requests()
            if pending_requests:
                aggregated = engine.aggregate_items(pending_requests)
                self.log_success("BUNDLING_ENGINE", f"Aggregation successful: {len(aggregated)} unique items")
                
                # Test vendor coverage
                vendor_data = engine.get_vendor_coverage(aggregated)
                if vendor_data:
                    self.log_success("BUNDLING_ENGINE", f"Vendor coverage successful: {len(vendor_data)} items have vendors")
                else:
                    self.log_warning("BUNDLING_ENGINE", "No vendor coverage found - check vendor mappings")
            
        except Exception as e:
            self.log_issue("BUNDLING_ENGINE", f"Error testing bundling engine: {str(e)}")
    
    def validate_user_authentication(self):
        """Test user authentication logic"""
        print("\nVALIDATING USER AUTHENTICATION...")
        
        try:
            # Check if users table has data
            users_query = "SELECT COUNT(*) as count FROM requirements_users"
            users_result = self.db.execute_query(users_query)
            users_count = users_result[0]['count'] if users_result else 0
            
            if users_count == 0:
                self.log_warning("USER_AUTH", "No users found in requirements_users table")
            else:
                self.log_success("USER_AUTH", f"Found {users_count} users in database")
            
            # Test admin credentials logic
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            if admin_username and admin_password:
                self.log_success("USER_AUTH", f"Admin credentials configured: {admin_username}")
            else:
                self.log_warning("USER_AUTH", "Admin credentials not properly configured")
                
        except Exception as e:
            self.log_issue("USER_AUTH", f"Error testing user authentication: {str(e)}")
    
    def validate_data_consistency(self):
        """Check data consistency across tables"""
        print("\nVALIDATING DATA CONSISTENCY...")
        
        try:
            # Check foreign key relationships
            
            # 1. requirements_order_items -> requirements_orders
            orphaned_items_query = """
            SELECT COUNT(*) as count
            FROM requirements_order_items roi
            LEFT JOIN requirements_orders ro ON roi.req_id = ro.req_id
            WHERE ro.req_id IS NULL
            """
            orphaned_items = self.db.execute_query(orphaned_items_query)
            orphaned_count = orphaned_items[0]['count'] if orphaned_items else 0
            
            if orphaned_count > 0:
                self.log_issue("DATA_CONSISTENCY", f"{orphaned_count} orphaned order items found")
            else:
                self.log_success("DATA_CONSISTENCY", "No orphaned order items")
            
            # 2. requirements_order_items -> Items (Phase 2)
            missing_items_query = """
            SELECT COUNT(*) as count
            FROM requirements_order_items roi
            LEFT JOIN Items i ON roi.item_id = i.item_id
            WHERE i.item_id IS NULL
            """
            missing_items = self.db.execute_query(missing_items_query)
            missing_count = missing_items[0]['count'] if missing_items else 0
            
            if missing_count > 0:
                self.log_issue("DATA_CONSISTENCY", f"{missing_count} order items reference non-existent items")
            else:
                self.log_success("DATA_CONSISTENCY", "All order items reference valid items")
            
        except Exception as e:
            self.log_issue("DATA_CONSISTENCY", f"Error checking data consistency: {str(e)}")
    
    def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("STARTING COMPREHENSIVE SYSTEM VALIDATION")
        print("=" * 60)
        
        # Run all validation tests
        self.validate_database_connection()
        self.validate_phase2_tables()
        self.validate_phase3_tables()
        self.validate_vendor_mapping_logic()
        self.validate_user_authentication()
        self.validate_data_consistency()
        self.validate_bundling_engine()
        
        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.issues:
            print(f"CRITICAL ISSUES FOUND: {len(self.issues)}")
            for issue in self.issues:
                print(f"   {issue}")
        
        if self.warnings:
            print(f"\nWARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if not self.issues and not self.warnings:
            print("ALL VALIDATIONS PASSED - SYSTEM IS READY!")
        elif not self.issues:
            print("NO CRITICAL ISSUES - SYSTEM SHOULD WORK WITH MINOR WARNINGS")
        else:
            print("CRITICAL ISSUES MUST BE FIXED BEFORE SYSTEM CAN WORK PROPERLY")
        
        return len(self.issues) == 0

if __name__ == "__main__":
    validator = SystemValidator()
    success = validator.run_comprehensive_validation()
    
    if success:
        print("\nSystem validation completed successfully!")
    else:
        print("\nSystem requires fixes before it can work properly.")
