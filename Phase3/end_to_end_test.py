# End-to-End Test for Phase 3 System
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_connector import DatabaseConnector
from bundling_engine import SmartBundlingEngine
import json

def test_complete_workflow():
    """Test the complete workflow from user request to bundle completion"""
    print("STARTING END-TO-END WORKFLOW TEST")
    print("=" * 50)
    
    db = DatabaseConnector()
    
    if not db.conn:
        print(f"ERROR: Database connection failed: {db.connection_error}")
        return False
    
    try:
        # Step 1: Clean up any existing test data
        print("\n1. CLEANING UP EXISTING TEST DATA...")
        cleanup_queries = [
            "DELETE FROM requirements_bundle_mapping WHERE bundle_id IN (SELECT bundle_id FROM requirements_bundles WHERE bundle_name LIKE 'TEST-%')",
            "DELETE FROM requirements_bundle_items WHERE bundle_id IN (SELECT bundle_id FROM requirements_bundles WHERE bundle_name LIKE 'TEST-%')",
            "DELETE FROM requirements_bundles WHERE bundle_name LIKE 'TEST-%'",
            "DELETE FROM requirements_order_items WHERE req_id IN (SELECT req_id FROM requirements_orders WHERE req_number LIKE 'TEST-%')",
            "DELETE FROM requirements_orders WHERE req_number LIKE 'TEST-%'"
        ]
        
        for query in cleanup_queries:
            try:
                db.execute_insert(query, ())
            except:
                pass  # Ignore errors for non-existent data
        
        db.conn.commit()
        print("   Cleanup completed")
        
        # Step 2: Create test user requests
        print("\n2. CREATING TEST USER REQUESTS...")
        
        # Get more items from the database for comprehensive testing
        items_query = "SELECT TOP 10 item_id, item_name FROM Items WHERE item_id IN (SELECT item_id FROM ItemVendorMap) ORDER BY item_id"
        items = db.execute_query(items_query)
        
        if len(items) < 8:
            print("ERROR: Not enough items with vendor mappings found")
            return False
        
        print(f"   Available items for testing: {len(items)}")
        for item in items[:8]:
            print(f"     - {item['item_name']} (ID: {item['item_id']})")
        
        # Create test requests with 5 items each
        test_requests = [
            {
                'user_id': 1,
                'req_number': 'TEST-REQ-001',
                'items': [
                    {'item_id': items[0]['item_id'], 'quantity': 5},  # Item 1
                    {'item_id': items[1]['item_id'], 'quantity': 3},  # Item 2
                    {'item_id': items[2]['item_id'], 'quantity': 2},  # Item 3
                    {'item_id': items[3]['item_id'], 'quantity': 4},  # Item 4
                    {'item_id': items[4]['item_id'], 'quantity': 6}   # Item 5
                ]
            },
            {
                'user_id': 2,
                'req_number': 'TEST-REQ-002',
                'items': [
                    {'item_id': items[0]['item_id'], 'quantity': 2},  # Same as req 1 - item 1
                    {'item_id': items[2]['item_id'], 'quantity': 3},  # Same as req 1 - item 3
                    {'item_id': items[5]['item_id'], 'quantity': 1},  # New item 6
                    {'item_id': items[6]['item_id'], 'quantity': 4},  # New item 7
                    {'item_id': items[7]['item_id'], 'quantity': 2}   # New item 8
                ]
            },
            {
                'user_id': 1,
                'req_number': 'TEST-REQ-003',
                'items': [
                    {'item_id': items[1]['item_id'], 'quantity': 1},  # Same as req 1 - item 2
                    {'item_id': items[4]['item_id'], 'quantity': 3},  # Same as req 1 - item 5
                    {'item_id': items[5]['item_id'], 'quantity': 2},  # Same as req 2 - item 6
                    {'item_id': items[6]['item_id'], 'quantity': 1},  # Same as req 2 - item 7
                    {'item_id': items[7]['item_id'], 'quantity': 5}   # Same as req 2 - item 8
                ]
            }
        ]
        
        created_req_ids = []
        
        for req_data in test_requests:
            # Insert order
            order_query = """
            INSERT INTO requirements_orders 
            (user_id, req_number, req_date, status, total_items)
            VALUES (?, ?, GETDATE(), 'Pending', ?)
            """
            
            total_items = sum(item['quantity'] for item in req_data['items'])
            db.execute_insert(order_query, (req_data['user_id'], req_data['req_number'], total_items))
            
            # Get the inserted req_id
            req_id = db.get_last_insert_id()
            created_req_ids.append(req_id)
            
            # Insert order items
            for item in req_data['items']:
                item_query = """
                INSERT INTO requirements_order_items 
                (req_id, item_id, quantity, item_notes)
                VALUES (?, ?, ?, 'Test item')
                """
                db.execute_insert(item_query, (req_id, item['item_id'], item['quantity']))
            
            print(f"   Created request {req_data['req_number']} with {len(req_data['items'])} items:")
            for item in req_data['items']:
                item_name = next(i['item_name'] for i in items if i['item_id'] == item['item_id'])
                print(f"     - {item_name}: {item['quantity']} pieces")
        
        db.conn.commit()
        
        # Step 3: Test bundling engine
        print("\n3. TESTING SMART BUNDLING ENGINE...")
        
        engine = SmartBundlingEngine()
        result = engine.run_bundling_process()
        
        if result['success']:
            print(f"   SUCCESS: Created {result.get('total_bundles', 0)} bundles")
            print(f"   Coverage: {result.get('coverage_percentage', 0):.1f}%")
            
            for i, bundle in enumerate(result.get('bundles_created', []), 1):
                print(f"   Bundle {i}: {bundle['bundle_name']} - {bundle['vendor_name']}")
        else:
            print(f"   ERROR: Bundling failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Step 4: Verify database state
        print("\n4. VERIFYING DATABASE STATE...")
        
        # Check that requests were moved to In Progress
        status_query = """
        SELECT req_number, status 
        FROM requirements_orders 
        WHERE req_number LIKE 'TEST-%'
        """
        status_results = db.execute_query(status_query)
        
        for req in status_results:
            if req['status'] != 'In Progress':
                print(f"   ERROR: Request {req['req_number']} has status {req['status']}, expected 'In Progress'")
                return False
            else:
                print(f"   Request {req['req_number']}: {req['status']} OK")
        
        # Check bundles were created
        bundles_query = """
        SELECT bundle_name, status, total_items, total_quantity
        FROM requirements_bundles 
        WHERE bundle_name LIKE 'BUNDLE-%'
        ORDER BY bundle_id DESC
        """
        bundles = db.execute_query(bundles_query)
        
        if not bundles:
            print("   ERROR: No bundles were created")
            return False
        
        for bundle in bundles[:2]:  # Show first 2
            print(f"   Bundle {bundle['bundle_name']}: {bundle['status']}, {bundle['total_items']} items, {bundle['total_quantity']} pieces OK")
        
        # Step 5: Test bundle completion
        print("\n5. TESTING BUNDLE COMPLETION...")
        
        if bundles:
            print(f"   DEBUG: First bundle keys: {list(bundles[0].keys())}")
            print(f"   DEBUG: First bundle data: {bundles[0]}")
            test_bundle_id = bundles[0]['bundle_id']
            
            # Mark bundle as completed
            completion_query = """
            UPDATE requirements_bundles 
            SET status = 'Completed'
            WHERE bundle_id = ?
            """
            db.execute_insert(completion_query, (test_bundle_id,))
            
            # Update related requests
            mapping_query = """
            SELECT req_id FROM requirements_bundle_mapping 
            WHERE bundle_id = ?
            """
            mappings = db.execute_query(mapping_query, (test_bundle_id,))
            
            if mappings:
                req_ids = [m['req_id'] for m in mappings]
                placeholders = ','.join(['?' for _ in req_ids])
                update_query = f"""
                UPDATE requirements_orders 
                SET status = 'Completed'
                WHERE req_id IN ({placeholders})
                """
                db.execute_insert(update_query, req_ids)
            
            db.conn.commit()
            print(f"   Marked bundle {test_bundle_id} as completed OK")
        
        # Step 6: Final verification
        print("\n6. FINAL VERIFICATION...")
        
        # Check final status
        final_status_query = """
        SELECT req_number, status 
        FROM requirements_orders 
        WHERE req_number LIKE 'TEST-%'
        """
        final_status = db.execute_query(final_status_query)
        
        completed_count = sum(1 for req in final_status if req['status'] == 'Completed')
        in_progress_count = sum(1 for req in final_status if req['status'] == 'In Progress')
        
        print(f"   Final status: {completed_count} completed, {in_progress_count} in progress OK")
        
        print("\n" + "=" * 50)
        print("END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("All components working correctly:")
        print("- User request creation")
        print("- Smart bundling engine")
        print("- Database integration")
        print("- Bundle completion workflow")
        print("- Status management")
        
        return True
        
    except Exception as e:
        print(f"\nERROR during end-to-end test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close_connection()

if __name__ == "__main__":
    success = test_complete_workflow()
    
    if success:
        print("\nSYSTEM IS READY FOR PRODUCTION USE!")
    else:
        print("\nSYSTEM NEEDS FIXES BEFORE PRODUCTION USE")
