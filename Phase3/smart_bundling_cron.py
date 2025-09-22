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


def _get_item_dimensions_map(db: DatabaseConnector, result: dict) -> dict:
    """Return {item_id: {height, width, thickness}} for all items in result bundles."""
    try:
        opt = result.get("optimization_result", {}) or {}
        bundles = opt.get("bundles", []) or []
        item_ids = set()
        for b in bundles:
            for it in (b.get('items_list') or []):
                if it.get('item_id') is not None:
                    item_ids.add(it['item_id'])
        if not item_ids:
            return {}
        placeholders = ','.join(['?' for _ in item_ids])
        q = f"SELECT item_id, height, width, thickness FROM Items WHERE item_id IN ({placeholders})"
        rows = db.execute_query(q, tuple(item_ids)) or []
        dims = {}
        for r in rows:
            dims[r['item_id']] = {
                'height': r.get('height'),
                'width': r.get('width'),
                'thickness': r.get('thickness'),
            }
        return dims
    except Exception:
        return {}


def _build_email_bodies(result: dict, dims_map: dict | None = None) -> tuple[str, str]:
    # Local formatter to match UI behavior (remove trailing zeros)
    def _fmt_dim(v):
        if v is None:
            return ''
        s = str(v).strip()
        if s == '':
            return ''
        try:
            from decimal import Decimal
            d = Decimal(s)
            s = format(d.normalize(), 'f')
        except Exception:
            pass
        if '.' in s:
            s = s.rstrip('0').rstrip('.')
        return s
    """Return (plain_text, html) summaries for operator email."""
    total_bundles = result.get("total_bundles", 0)
    total_requests = result.get("total_requests", 0)
    coverage = result.get("coverage_percentage", 0)
    opt = result.get("optimization_result", {}) or {}
    bundles = opt.get("bundles", []) or []
    # Compute distinct items and total pieces across bundles
    item_ids = []
    pieces_sum = 0
    for b in bundles:
        for it in (b.get('items_list') or []):
            if it.get('item_id') is not None:
                item_ids.append(it['item_id'])
            pieces_sum += int(it.get('quantity', 0) or 0)
    distinct_items = len(set(item_ids))

    # Plain text
    lines = []
    lines.append("Smart Bundling Summary")
    lines.append("")
    lines.append(f"Bundles: {total_bundles}")
    lines.append(f"Requests Processed: {total_requests}")
    lines.append(f"Distinct Items: {distinct_items}")
    lines.append(f"Total Pieces: {pieces_sum}")
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
            dims_txt = ""
            if dims_map and it.get('item_id') in dims_map:
                d = dims_map[it['item_id']]
                parts = [_fmt_dim(d.get('height')), _fmt_dim(d.get('width')), _fmt_dim(d.get('thickness'))]
                parts = [p for p in parts if p and p.lower() not in ('n/a', 'none', 'null')]
                if parts:
                    dims_txt = f" ({' x '.join(parts)})"
            lines.append(f"  • {it.get('item_name', 'Item')}{dims_txt} — {it.get('quantity', 0)} pcs")
        lines.append("")
    plain_text = "\n".join(lines)

    # HTML
    vendor_blocks = []
    for b in bundles:
        vendor = b.get('vendor_name', 'Unknown Vendor')
        items_count = b.get('items_count', len(b.get('items_list') or []))
        total_qty = b.get('total_quantity', 0)
        email = b.get('contact_email') or ''
        phone = b.get('contact_phone') or ''
        header = f"<div style='font-weight:600;margin:12px 0 6px;font-size:16px;'>{vendor}</div>"
        contact = ""
        if email or phone:
            sep = " | " if email and phone else ""
            contact = f"<div style='color:#555;margin:0 0 10px;'>Items: {items_count} | Pieces: {total_qty} | Contact: {email}{sep}{phone}</div>"
        else:
            contact = f"<div style='color:#555;margin:0 0 10px;'>Items: {items_count} | Pieces: {total_qty}</div>"

        # Build a table per vendor: Item | Dimensions | Quantity
        row_html = []
        for it in (b.get('items_list') or []):
            dims_txt = ''
            if dims_map and it.get('item_id') in dims_map:
                d = dims_map[it['item_id']]
                parts = [_fmt_dim(d.get('height')), _fmt_dim(d.get('width')), _fmt_dim(d.get('thickness'))]
                parts = [p for p in parts if p and p.lower() not in ('n/a','none','null')]
                if parts:
                    dims_txt = ' x '.join(parts)
            row_html.append(
                f"<tr>"
                f"<td style='padding:6px 8px;border-bottom:1px solid #eee;'>{it.get('item_name','Item')}</td>"
                f"<td style='padding:6px 8px;border-bottom:1px solid #eee;color:#555;'>{dims_txt}</td>"
                f"<td style='padding:6px 8px;border-bottom:1px solid #eee;text-align:right;'>{it.get('quantity',0)}</td>"
                f"</tr>"
            )

        table = (
            "<table style=\"border-collapse:collapse;width:100%;max-width:900px;\">"
            "<thead>\n<tr style=\"background:#f6f7f9;\">"
            "<th style=\"text-align:left;padding:6px 8px;\">Item</th>"
            "<th style=\"text-align:left;padding:6px 8px;\">Dimensions</th>"
            "<th style=\"text-align:right;padding:6px 8px;\">Qty</th>"
            "</tr>\n</thead>"
            f"<tbody>{''.join(row_html)}</tbody>"
            "</table>"
        )
        vendor_blocks.append(header + contact + table)

    html = f"""
    <div style="font-family:Segoe UI, Arial, sans-serif; font-size:14px; color:#222;">
      <h2 style="margin:0 0 8px;">Smart Bundling Summary</h2>
      <div style="margin:6px 0;">Bundles: {total_bundles}</div>
      <div style="margin:6px 0;">Requests Processed: {total_requests}</div>
      <div style="margin:6px 0;">Distinct Items: {distinct_items}</div>
      <div style="margin:6px 0;">Total Pieces: {pieces_sum}</div>
      <div style="margin:6px 0 16px;">Coverage: {coverage}%</div>
      {''.join(vendor_blocks) if vendor_blocks else '<div>No bundles created.</div>'}
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
        coverage = result.get("coverage_percentage", 0)
        # Derive distinct item count and total pieces from optimization bundles for clarity
        opt = result.get("optimization_result", {}) or {}
        bundles = opt.get("bundles", []) or []
        distinct_items = len({it.get('item_id') for b in bundles for it in (b.get('items_list') or []) if it.get('item_id') is not None})
        total_pieces = sum(int(it.get('quantity', 0) or 0) for b in bundles for it in (b.get('items_list') or []))

        log("Bundling completed successfully")
        log(f"Summary: bundles={total_bundles}, requests={total_requests}, distinct_items={distinct_items}, pieces={total_pieces}, coverage={coverage}%")

        # 4) Send operator summary email if SMTP envs are configured
        try:
            subject = f"Smart Bundling: {total_bundles} bundles | {coverage}% coverage"
            dims_map = _get_item_dimensions_map(db, result)
            body_text, html_body = _build_email_bodies(result, dims_map)
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
