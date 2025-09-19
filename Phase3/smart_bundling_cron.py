"""
Smart Bundling Cron Runner (Phase 3)
- Headless script to run the smart bundling engine on a schedule or manual trigger
- No UI, no email (email can be integrated later)

Exit codes:
- 0 on success (even if there are no pending requests)
- 1 on failure (DB connection or algorithm error)
"""

import os
import sys
import json
from datetime import datetime

# Ensure imports work when executed from repo root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from db_connector import DatabaseConnector
from bundling_engine import SmartBundlingEngine


def log(msg: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")


def main() -> int:
    log("Starting Smart Bundling cron run")

    # 1) Validate DB connectivity (env-based in CI)
    db = DatabaseConnector()
    if not db.conn:
        log(f"ERROR: Database connection failed: {db.connection_error}")
        return 1
    log("Database connection OK")

    try:
        # 2) Run the bundling engine
        engine = SmartBundlingEngine()
        result = engine.run_bundling_process()

        if not isinstance(result, dict):
            log("ERROR: Unexpected result type from bundling engine")
            return 1

        if not result.get("success"):
            log(f"ERROR: Bundling process failed: {result.get('error', 'Unknown error')}")
            return 1

        # 3) Summarize outcome
        total_bundles = result.get("total_bundles", 0)
        total_requests = result.get("total_requests", 0)
        total_items = result.get("total_items", 0)
        coverage = result.get("coverage_percentage", 0)

        log("Bundling completed successfully")
        log(f"Summary: bundles={total_bundles}, requests={total_requests}, items={total_items}, coverage={coverage}%")

        # 4) Optional verbose details for CI logs
        debug_info = result.get("debug_info") or {}
        if debug_info:
            try:
                sample_keys = list(debug_info.keys())[:5]
                log(f"Debug keys: {sample_keys}")
            except Exception:
                pass

        return 0

    except Exception as e:
        log(f"ERROR: Exception during bundling: {e}")
        return 1
    finally:
        try:
            db.close_connection()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
