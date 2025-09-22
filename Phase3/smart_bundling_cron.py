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

# Email service (Brevo SMTP via env vars)
from email_service import send_email_via_brevo

# Ensure imports work when executed from repo root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from db_connector import DatabaseConnector
from bundling_engine import SmartBundlingEngine


def log(msg: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")


def _build_email_bodies(result: dict) -> tuple[str, str]:
    """Return (plain_text, html) summaries for operator email."""
    total_bundles = result.get("total_bundles", 0)
    total_requests = result.get("total_requests", 0)
    total_items = result.get("total_items", 0)
    coverage = result.get("coverage_percentage", 0)
    opt = result.get("optimization_result", {}) or {}
    bundles = opt.get("bundles", []) or []

    # Plain text
    lines = []
    lines.append("Smart Bundling Summary")
    lines.append("")
    lines.append(f"Bundles: {total_bundles}")
    lines.append(f"Requests Processed: {total_requests}")
    lines.append(f"Distinct Items: {total_items}")
    lines.append(f"Coverage: {coverage}%")
    lines.append("")
    for b in bundles:
        vendor = b.get('vendor_name', 'Unknown Vendor')
        items_count = b.get('items_count', len(b.get('items_list') or []))
        total_qty = b.get('total_quantity', 0)
        email = b.get('contact_email') or ''
        phone = b.get('contact_phone') or ''
        lines.append(f"- Vendor: {vendor} | Items: {items_count} | Pieces: {total_qty}")
        if email or phone:
            lines.append(f"  Contact: {email}{' | ' if email and phone else ''}{phone}")
        for it in b.get('items_list') or []:
            lines.append(f"  • {it.get('item_name', 'Item')} — {it.get('quantity', 0)} pcs")
        lines.append("")
    plain_text = "\n".join(lines)

    # HTML
    rows_html = []
    for b in bundles:
        vendor = b.get('vendor_name', 'Unknown Vendor')
        items_count = b.get('items_count', len(b.get('items_list') or []))
        total_qty = b.get('total_quantity', 0)
        email = b.get('contact_email') or ''
        phone = b.get('contact_phone') or ''
        header = f"<div style='font-weight:600;margin:8px 0 4px;'>{vendor}</div>"
        meta = f"<div style='color:#555;margin:0 0 8px;'>Items: {items_count} | Pieces: {total_qty}" + (f" | Contact: {email} {(' | '+phone) if phone else ''}" if email or phone else "") + "</div>"
        items_lines = []
        for it in b.get('items_list') or []:
            items_lines.append(f"<div>• {it.get('item_name','Item')} — {it.get('quantity',0)} pcs</div>")
        rows_html.append(header + meta + "".join(items_lines))

    html = f"""
    <div style="font-family:Segoe UI, Arial, sans-serif; font-size:14px; color:#222;">
      <h2 style="margin:0 0 8px;">Smart Bundling Summary</h2>
      <div style="margin:6px 0;">Bundles: {total_bundles}</div>
      <div style="margin:6px 0;">Requests Processed: {total_requests}</div>
      <div style="margin:6px 0;">Distinct Items: {total_items}</div>
      <div style="margin:6px 0 16px;">Coverage: {coverage}%</div>
      {''.join(rows_html) if rows_html else '<div>No bundles created.</div>'}
    </div>
    """
    return plain_text, html


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

        # 4) Send operator summary email if SMTP envs are configured
        try:
            subject = f"Smart Bundling: {total_bundles} bundles | {coverage}% coverage"
            body_text, html_body = _build_email_bodies(result)
            sent = send_email_via_brevo(subject, body_text, html_body=html_body)
            if sent:
                log("Operator summary email sent via Brevo SMTP")
            else:
                log("Email step skipped (missing SMTP envs) or failed silently")
        except Exception as e:
            log(f"Email step error: {e}")

        # 5) Optional verbose details for CI logs
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
