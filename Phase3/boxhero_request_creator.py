"""
BoxHero Request Creator Cron (Phase 3)
- Runs Tuesday 8:00 AM (2 hours before bundling)
- Creates requests for BoxHero items needing restock
- Does NOT run bundling
- Separate from smart_bundling_cron.py

Exit codes:
- 0 on success (even if no items need reordering)
- 1 on failure (DB connection or query error)
"""

import os
import sys
from datetime import datetime

# Ensure imports work when executed from repo root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from db_connector import DatabaseConnector

# BoxHero system user ID (created in database)
BOXHERO_USER_ID = 5


def log(msg: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")


def create_boxhero_requests(db: DatabaseConnector) -> int:
    """
    Query BoxHero deficit items and create fake user requests.
    
    Returns: Number of items processed
    """
    log("Checking BoxHero inventory for items needing restock...")
    
    # Check if request already exists today (prevent duplicates)
    today_str = datetime.now().strftime('%Y%m%d')
    req_number = f"REQ-BOXHERO-{today_str}"
    
    check_query = """
    SELECT req_id FROM requirements_orders 
    WHERE req_number = ?
    """
    existing = db.execute_query(check_query, (req_number,))
    
    if existing:
        log(f"BoxHero request {req_number} already exists. Skipping creation.")
        return 0
    
    # Query BoxHero deficit items using the working query
    query = """
    WITH LatestItemSnapshot AS (
        SELECT
            sku,
            current_stock,
            reorder_threshold,
            deficit,
            snapshot_date,
            ROW_NUMBER() OVER(PARTITION BY sku ORDER BY snapshot_date DESC) AS rn
        FROM InventoryCheckHistory
    )
    SELECT
        T1.item_id,
        T1.item_name,
        T1.sku,
        T2.deficit,
        T2.current_stock,
        T2.reorder_threshold,
        T2.snapshot_date
    FROM Items AS T1
    INNER JOIN LatestItemSnapshot AS T2 ON T1.sku = T2.sku
    WHERE T1.source_sheet = 'BoxHero'
      AND T2.deficit > 0
      AND T2.rn = 1
    """
    
    try:
        boxhero_items = db.execute_query(query)
        
        if not boxhero_items or len(boxhero_items) == 0:
            log("No BoxHero items need reordering")
            return 0
        
        log(f"Found {len(boxhero_items)} BoxHero items needing restock")
        
        # Insert into requirements_orders
        insert_order = """
        INSERT INTO requirements_orders 
        (user_id, req_number, req_date, status, source_type, project_number)
        VALUES (?, ?, ?, 'Pending', 'BoxHero', NULL)
        """
        
        db.execute_insert(insert_order, (
            BOXHERO_USER_ID,
            req_number,
            datetime.now()
        ))
        db.conn.commit()
        
        # Get the req_id we just created
        req_result = db.execute_query(check_query, (req_number,))
        
        if not req_result or len(req_result) == 0:
            log(f"ERROR: Failed to retrieve req_id for {req_number}")
            return 0
        
        req_id = req_result[0]['req_id']
        log(f"Created BoxHero request: {req_number} (req_id: {req_id})")
        
        # Insert each item into requirements_order_items
        insert_item = """
        INSERT INTO requirements_order_items 
        (req_id, item_id, quantity, source_type, project_number)
        VALUES (?, ?, ?, 'BoxHero', NULL)
        """
        
        for item in boxhero_items:
            db.execute_insert(insert_item, (
                req_id,
                item['item_id'],
                item['deficit']  # Order exactly the deficit quantity
            ))
            log(f"  - Added: {item['item_name']} ({item['deficit']} pcs)")
        
        db.conn.commit()
        log(f"Successfully created BoxHero request with {len(boxhero_items)} items")
        return len(boxhero_items)
        
    except Exception as e:
        log(f"ERROR creating BoxHero requests: {e}")
        try:
            db.conn.rollback()
        except Exception:
            pass
        return 0


def main() -> int:
    log("Starting BoxHero Request Creator")
    
    # 1) Validate DB connectivity
    db = DatabaseConnector()
    if not db.conn:
        log(f"ERROR: Database connection failed: {db.connection_error}")
        return 1
    log("Database connection OK")
    
    try:
        # 2) Create BoxHero requests
        item_count = create_boxhero_requests(db)
        
        if item_count > 0:
            log(f"SUCCESS: Created BoxHero request with {item_count} items")
        else:
            log("No BoxHero requests created (no items needed or already exists)")
        
        return 0
        
    except Exception as e:
        log(f"ERROR: Exception during BoxHero request creation: {e}")
        return 1
    finally:
        try:
            db.close_connection()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
