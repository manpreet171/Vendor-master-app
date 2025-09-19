"""
Smart Bundling Engine for Phase 3C
Automatically groups pending requests by optimal vendor coverage
"""

import json
from datetime import datetime
from collections import defaultdict
from db_connector import DatabaseConnector

class SmartBundlingEngine:
    def __init__(self):
        self.db = DatabaseConnector()
    
    def run_bundling_process(self):
        """Main bundling process - called by cron job"""
        try:
            print("Starting Smart Bundling Process...")
            
            # Step 1: Get all pending requests
            pending_requests = self.db.get_all_pending_requests()
            
            if not pending_requests:
                print("No pending requests found. Nothing to bundle.")
                return {"success": True, "message": "No pending requests"}
            
            print(f"Found {len(pending_requests)} pending request items")
            
            # Step 2: Aggregate items and quantities
            aggregated_items = self.aggregate_items(pending_requests)
            print(f"Aggregated into {len(aggregated_items)} unique items")
            
            # Debug: Show what items we're trying to bundle
            for item_id, item_data in aggregated_items.items():
                print(f"  Item {item_id}: {item_data['item_name']} - {item_data['total_quantity']} pieces")
            
            # Step 3: Get vendor information for all items
            vendor_data = self.get_vendor_coverage(aggregated_items)
            print(f"Found vendor data for {len(vendor_data)} items")
            
            # Debug: Show what vendor data we found
            for item_id, vendors in vendor_data.items():
                item_name = aggregated_items[item_id]['item_name']
                print(f"  Item {item_id} ({item_name}): {len(vendors)} vendors")
                for vendor in vendors:
                    print(f"    - {vendor['vendor_name']} (ID: {vendor['vendor_id']})")
            
            # Step 4: Find optimal vendor combinations with 100% coverage
            optimization_result = self.optimize_vendor_selection(aggregated_items, vendor_data)
            print(f"Generated {optimization_result['total_bundles']} bundles with {optimization_result['coverage_percentage']:.1f}% coverage")
            
            # Step 5: Update request status to "In Progress"
            request_ids = list(set([req['req_id'] for req in pending_requests]))
            self.db.update_requests_to_in_progress(request_ids)
            print(f"Updated {len(request_ids)} requests to 'In Progress'")
            
            # Step 6: Create multiple bundles in database (one per vendor)
            created_bundles = []
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            
            for i, bundle in enumerate(optimization_result['bundles'], 1):
                bundle_data = {
                    'timestamp': f"{timestamp}-{i:02d}",
                    'total_requests': len(request_ids),
                    'total_items': bundle['total_quantity'],
                    'vendor_recommendations': [bundle],  # Single vendor per bundle
                    'items': bundle['items_list'],
                    'request_ids': request_ids,
                    'bundle_number': i,
                    'vendor_name': bundle['vendor_name']
                }
                
                bundle_id = self.db.create_bundle(bundle_data)
                created_bundles.append({
                    'bundle_id': bundle_id,
                    'bundle_name': f"BUNDLE-{bundle_data['timestamp']}",
                    'vendor_name': bundle['vendor_name'],
                    'items_count': bundle['items_count'],
                    'total_quantity': bundle['total_quantity']
                })
                print(f"Created Bundle {i}: {bundle['vendor_name']} - {bundle['items_count']} items")
            
            return {
                "success": True,
                "bundles_created": created_bundles,
                "total_bundles": len(created_bundles),
                "total_requests": len(request_ids),
                "total_items": sum(item['total_quantity'] for item in aggregated_items.values()),
                "coverage_percentage": optimization_result['coverage_percentage'],
                "optimization_result": optimization_result
            }
            
        except Exception as e:
            print(f"Bundling process failed: {str(e)}")
            return {"success": False, "error": str(e)}
        
        finally:
            self.db.close_connection()
    
    def aggregate_items(self, pending_requests):
        """Aggregate items by item_id and calculate total quantities"""
        aggregated = defaultdict(lambda: {
            'item_id': None,
            'item_name': '',
            'total_quantity': 0,
            'user_breakdown': {},
            'source_sheet': '',
            'sku': ''
        })
        
        for req in pending_requests:
            item_id = req['item_id']
            user_id = req['user_id']
            quantity = req['quantity']
            
            # Initialize if first time seeing this item
            if aggregated[item_id]['item_id'] is None:
                aggregated[item_id]['item_id'] = item_id
                aggregated[item_id]['item_name'] = req['item_name']
                aggregated[item_id]['source_sheet'] = req['source_sheet']
                aggregated[item_id]['sku'] = req.get('sku', '')
            
            # Add to total quantity
            aggregated[item_id]['total_quantity'] += quantity
            
            # Track user breakdown
            if user_id not in aggregated[item_id]['user_breakdown']:
                aggregated[item_id]['user_breakdown'][user_id] = 0
            aggregated[item_id]['user_breakdown'][user_id] += quantity
        
        return dict(aggregated)
    
    def get_vendor_coverage(self, aggregated_items):
        """Get vendor information for all items with detailed analysis"""
        try:
            item_ids = list(aggregated_items.keys())
            vendor_mappings = self.db.get_item_vendors(item_ids)
            
            # Organize by item_id
            vendor_data = {}
            for mapping in vendor_mappings:
                item_id = mapping['item_id']
                if item_id not in vendor_data:
                    vendor_data[item_id] = []
                
                vendor_data[item_id].append({
                    'vendor_id': mapping['vendor_id'],
                    'vendor_name': mapping['vendor_name'],
                    'contact_email': mapping['contact_email'],
                    'contact_phone': mapping['contact_phone']
                })
            
            # Add detailed analysis for debugging
            self.debug_info = {
                'items_analysis': {},
                'vendor_coverage_analysis': {},
                'common_vendors': {},
                'coverage_strategy': []
            }
            
            # Analyze each item and its vendors
            print("\n" + "="*60)
            print("DETAILED BUNDLING ANALYSIS (DEBUG VIEW)")
            print("="*60)
            
            print("\n1. ITEMS AND THEIR VENDORS:")
            for item_id, vendors in vendor_data.items():
                item_name = aggregated_items[item_id]['item_name']
                quantity = aggregated_items[item_id]['total_quantity']
                
                print(f"\nITEM: {item_name} ({quantity} pieces)")
                print(f"   Item ID: {item_id}")
                
                vendor_list = []
                for vendor in vendors:
                    vendor_info = f"   - {vendor['vendor_name']} (ID: {vendor['vendor_id']})"
                    if vendor['contact_email']:
                        vendor_info += f" - {vendor['contact_email']}"
                    if vendor['contact_phone']:
                        vendor_info += f" - {vendor['contact_phone']}"
                    print(vendor_info)
                    vendor_list.append(vendor['vendor_name'])
                
                self.debug_info['items_analysis'][item_id] = {
                    'item_name': item_name,
                    'quantity': quantity,
                    'vendors': vendor_list,
                    'vendor_count': len(vendors)
                }
            
            # Analyze vendor coverage across all items
            print("\n2. VENDOR COVERAGE ANALYSIS:")
            all_vendors = {}
            for item_id, vendors in vendor_data.items():
                for vendor in vendors:
                    vendor_id = vendor['vendor_id']
                    vendor_name = vendor['vendor_name']
                    
                    if vendor_id not in all_vendors:
                        all_vendors[vendor_id] = {
                            'vendor_name': vendor_name,
                            'contact_email': vendor['contact_email'],
                            'contact_phone': vendor['contact_phone'],
                            'items_covered': [],
                            'total_pieces': 0
                        }
                    
                    all_vendors[vendor_id]['items_covered'].append({
                        'item_id': item_id,
                        'item_name': aggregated_items[item_id]['item_name'],
                        'quantity': aggregated_items[item_id]['total_quantity']
                    })
                    all_vendors[vendor_id]['total_pieces'] += aggregated_items[item_id]['total_quantity']
            
            # Show vendor coverage analysis
            total_items = len(aggregated_items)
            for vendor_id, vendor_info in all_vendors.items():
                coverage_percentage = (len(vendor_info['items_covered']) / total_items) * 100
                print(f"\nVENDOR: {vendor_info['vendor_name']} (ID: {vendor_id})")
                print(f"   Coverage: {len(vendor_info['items_covered'])}/{total_items} items ({coverage_percentage:.1f}%)")
                print(f"   Total Pieces: {vendor_info['total_pieces']}")
                print(f"   Contact: {vendor_info['contact_email']} | {vendor_info['contact_phone']}")
                print("   Items covered:")
                for item in vendor_info['items_covered']:
                    print(f"     - {item['item_name']} ({item['quantity']} pieces)")
                
                self.debug_info['vendor_coverage_analysis'][vendor_id] = {
                    'vendor_name': vendor_info['vendor_name'],
                    'coverage_percentage': coverage_percentage,
                    'items_count': len(vendor_info['items_covered']),
                    'total_pieces': vendor_info['total_pieces'],
                    'contact_email': vendor_info['contact_email'],
                    'contact_phone': vendor_info['contact_phone'],
                    'items_covered': vendor_info['items_covered']
                }
            
            return vendor_data
            
        except Exception as e:
            print(f"Error getting vendor coverage: {str(e)}")
            return {}
    
    def optimize_vendor_selection(self, aggregated_items, vendor_data):
        """Find optimal vendor combinations for 100% item coverage"""
        print("Starting smart vendor optimization for complete coverage...")
        
        # Step 1: Build vendor capabilities matrix
        vendor_capabilities = defaultdict(lambda: {
            'items_available': set(),
            'vendor_info': {},
            'total_quantity': 0
        })
        
        # Map which vendors can supply which items
        for item_id, item_data in aggregated_items.items():
            if item_id in vendor_data:
                for vendor in vendor_data[item_id]:
                    vendor_id = vendor['vendor_id']
                    vendor_capabilities[vendor_id]['items_available'].add(item_id)
                    vendor_capabilities[vendor_id]['vendor_info'] = {
                        'vendor_name': vendor['vendor_name'],
                        'contact_email': vendor['contact_email'],
                        'contact_phone': vendor['contact_phone']
                    }
        
        # Step 2: Smart Bundle Creation Algorithm
        bundles = []
        remaining_items = set(aggregated_items.keys())
        bundle_number = 1
        
        print(f"Need to cover {len(remaining_items)} items: {[aggregated_items[i]['item_name'] for i in remaining_items]}")
        
        print("\n3. BUNDLE CREATION STRATEGY:")
        
        while remaining_items:
            # Find vendor with maximum coverage of remaining items
            best_vendor = None
            best_coverage = 0
            best_items = set()
            
            print(f"\n   Analyzing remaining items: {len(remaining_items)}")
            for item_id in remaining_items:
                print(f"     - {aggregated_items[item_id]['item_name']}")
            
            print("   Vendor coverage analysis:")
            for vendor_id, capabilities in vendor_capabilities.items():
                # Items this vendor can cover from remaining items
                can_cover = capabilities['items_available'].intersection(remaining_items)
                coverage_count = len(can_cover)
                vendor_name = capabilities['vendor_info']['vendor_name']
                
                if coverage_count > 0:
                    print(f"     - {vendor_name}: can cover {coverage_count} items")
                    for item_id in can_cover:
                        print(f"       * {aggregated_items[item_id]['item_name']}")
                
                if coverage_count > best_coverage:
                    best_coverage = coverage_count
                    best_vendor = vendor_id
                    best_items = can_cover
            
            if best_vendor is None:
                # Handle items with no vendors (shouldn't happen in normal case)
                print(f"   WARNING: Items without vendors: {remaining_items}")
                for item_id in remaining_items:
                    print(f"     - {aggregated_items[item_id]['item_name']} (Item ID: {item_id})")
                break
            
            # Create bundle for this vendor
            bundle_items = []
            bundle_total_qty = 0
            
            for item_id in best_items:
                item_data = aggregated_items[item_id]
                bundle_items.append({
                    'item_id': item_id,
                    'item_name': item_data['item_name'],
                    'quantity': item_data['total_quantity'],
                    'user_breakdown': item_data['user_breakdown']
                })
                bundle_total_qty += item_data['total_quantity']
            
            bundle = {
                'bundle_number': bundle_number,
                'vendor_id': best_vendor,
                'vendor_name': vendor_capabilities[best_vendor]['vendor_info']['vendor_name'],
                'contact_email': vendor_capabilities[best_vendor]['vendor_info']['contact_email'],
                'contact_phone': vendor_capabilities[best_vendor]['vendor_info']['contact_phone'],
                'items_count': len(bundle_items),
                'total_quantity': bundle_total_qty,
                'items_list': bundle_items
            }
            
            bundles.append(bundle)
            
            # Remove covered items from remaining
            remaining_items -= best_items
            
            print(f"   Bundle {bundle_number}: {bundle['vendor_name']} covers {len(best_items)} items ({bundle_total_qty} pieces)")
            print(f"      Contact: {bundle['contact_email']} | {bundle['contact_phone']}")
            print("      Items in this bundle:")
            for item in bundle_items:
                print(f"        - {item['item_name']} ({item['quantity']} pieces)")
            
            # Store bundle strategy in debug info
            self.debug_info['coverage_strategy'].append({
                'bundle_number': bundle_number,
                'vendor_name': bundle['vendor_name'],
                'vendor_id': best_vendor,
                'contact_email': bundle['contact_email'],
                'contact_phone': bundle['contact_phone'],
                'items_covered': len(best_items),
                'total_pieces': bundle_total_qty,
                'items_list': [{'item_name': item['item_name'], 'quantity': item['quantity']} for item in bundle_items]
            })
            
            bundle_number += 1
        
        # Step 3: Verify 100% coverage
        total_items_covered = sum(len(bundle['items_list']) for bundle in bundles)
        total_items_needed = len(aggregated_items)
        
        coverage_percentage = (total_items_covered / total_items_needed) * 100 if total_items_needed > 0 else 0
        
        print(f"Coverage Result: {total_items_covered}/{total_items_needed} items = {coverage_percentage:.1f}%")
        
        if coverage_percentage < 100:
            print(f"Warning: Not all items covered! Missing items: {remaining_items}")
        
        print("\n" + "="*60)
        print(f"BUNDLING COMPLETED: {len(bundles)} bundles created with {coverage_percentage:.1f}% coverage")
        print("="*60)
        
        return {
            'bundles': bundles,
            'total_bundles': len(bundles),
            'coverage_percentage': coverage_percentage,
            'total_items': total_items_needed,
            'items_covered': total_items_covered,
            'debug_info': self.debug_info if hasattr(self, 'debug_info') else {}
        }

def run_manual_bundling():
    """Manual trigger for testing"""
    engine = SmartBundlingEngine()
    result = engine.run_bundling_process()
    
    if result['success']:
        print(f"\nSmart Bundling Successful!")
        print(f"Total Bundles Created: {result.get('total_bundles', 0)}")
        print(f"Total Requests Processed: {result.get('total_requests', 0)}")
        print(f"Total Items: {result.get('total_items', 0)}")
        print(f"Coverage: {result.get('coverage_percentage', 0):.1f}%")
        print(f"\nCreated Bundles:")
        
        for i, bundle in enumerate(result.get('bundles_created', []), 1):
            print(f"{i}. {bundle['bundle_name']}")
            print(f"   Vendor: {bundle['vendor_name']}")
            print(f"   Items: {bundle['items_count']}, Quantity: {bundle['total_quantity']}")
            print(f"   Bundle ID: {bundle['bundle_id']}")
            print("")
        
        # Show detailed optimization result
        opt_result = result.get('optimization_result', {})
        if opt_result.get('bundles'):
            print("Detailed Bundle Breakdown:")
            for bundle in opt_result['bundles']:
                print(f"\nBundle {bundle['bundle_number']}: {bundle['vendor_name']}")
                print(f"   Contact: {bundle['contact_email']}")
                print(f"   Items covered:")
                for item in bundle['items_list']:
                    print(f"   - {item['item_name']} - {item['quantity']} pieces")
    else:
        print(f"Bundling Failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    run_manual_bundling()
