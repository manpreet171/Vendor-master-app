# SDGNY Vendor Management App – Phase 2 Documentation

This document describes the Phase 2 Streamlit application in detail: features, UI flows, database operations, and the main functions/modules added or modified.

## 1. Overview

Phase 2 provides a simple, user-friendly app for viewing and managing vendors, items, and the relationships between them. The focus is on:
- Minimal navigation with three tabs: Dashboard, Items, Vendors
- Clean presentation of item details and mapped vendors
- Inline editing of vendor costs for items
- Source-specific item fields (BoxHero vs Raw Materials)
- “Incomplete” views for quickly completing missing details for vendors and items

## 2. App Structure

- `app.py` – Entry point and tab navigation (Dashboard, Items, Vendors)
- `db_connector.py` – All database access/query helpers
- `item_manager.py` – Items page UI + logic (view, add, edit/delete, incomplete, vendor cost updates)
- `vendor_manager.py` – Vendors page UI + logic (view, add, edit/delete, incomplete)
- `utils.py` – UI helpers and small formatters (e.g., CSS, currency formatting)

The app uses the existing Azure SQL Server database from Phase 1 with the following key tables:
- `Items(item_id, item_name, item_type, source_sheet, sku, barcode, height, width, thickness)`
- `Vendors(vendor_id, vendor_name, contact_name, vendor_email, vendor_phone)`
- `ItemVendorMap(map_id, item_id, vendor_id, cost)`

Note: Cost is stored in `ItemVendorMap.cost`, not in `Items`.

## 3. Dashboard

Function: `display_dashboard()` in `app.py`

Flow:
1. User selects a source: BoxHero or Raw Materials.
2. User selects an item by `item_name` from that source.
3. The app shows a clean "Item Details" summary:
   - Always: Name, Type, Source
   - BoxHero: SKU, Barcode
   - Raw Materials: Height, Width, Thickness
4. Below, the app shows "Vendors for this Item" as expandable panels:
   - Header: Vendor Name — Cost (formatted)
   - Inside panel: Contact, Email (clickable), Phone (clickable)

Key operations:
- Items query: `db.get_all_items(source_filter=...)`
- Vendors for item: `db.get_item_vendors(item_id)`

UX design:
- Friendly labels (no technical IDs)
- Sorted by lowest cost first (NULL costs appear last)
- No JSON blocks, no technical column names

## 4. Items Tab

Module: `item_manager.py`

### 4.1 View Items
- Filters: Item Type, Source (All/BoxHero/Raw Materials)
- Loads with `db.get_all_items(source_filter, type_filter)`
- Displays a simple table (hiding technical identifiers) and a quick bar chart for item type distribution.

### 4.2 Add Item (Source-specific fields)
- Common fields: Item Name, Item Type, Source, Default Cost (applied when creating vendor mappings)
- BoxHero fields: SKU, Barcode
- Raw Materials fields: Height, Width, Thickness
- Non-applicable fields are set to `NULL` (None) automatically.
- Insert: `db.add_item(item_name, item_type, source_sheet, sku, barcode, height, width, thickness)`
- After successful add:
  - Inline vendor assignment: multiselect vendors and set a single cost applied to all mappings.
  - Mapping insert: `db.add_mapping(item_id, vendor_id, cost)`

### 4.3 Edit/Delete Item
- Edit uses the same source-specific logic:
  - BoxHero: edit SKU, Barcode (no dimensions)
  - Raw Materials: edit Height, Width, Thickness (no SKU/Barcode)
- Update: `db.update_item(item_id, item_name, item_type, source_sheet, sku, barcode, height, width, thickness)`
- Delete: `db.delete_item(item_id)` (also removes related mappings)
- Inline vendor assignment for existing items: add new vendor mappings with a single cost applied to all selected vendors.

### 4.4 View Vendors (for a Selected Item)
- Shows current vendor mappings in a table with formatted cost
- Counts and highlights how many mappings have `NULL` cost
- Inline per-vendor cost editor:
  - Number input per vendor mapping
  - Save button invokes: `db.update_mapping(map_id, cost)`

### 4.5 Incomplete Items
- Quick cleanup page to complete missing details per source
- Uses `db.get_incomplete_items()` which returns:
  - `boxhero`: items missing SKU or Barcode
  - `raw`: items missing Height, Width, or Thickness
- For each selection:
  - BoxHero: update SKU and Barcode (keeps other fields unchanged)
  - Raw Materials: update Height, Width, Thickness (keeps other fields unchanged)
  - Saves via `db.update_item(...)`

## 5. Vendors Tab

Module: `vendor_manager.py`

### 5.1 View Vendors
- Loads all vendors with `db.get_all_vendors()`
- Displays a simple table (friendly column names)

### 5.2 Add Vendor
- Fields: Vendor Name, Contact Name, Email, Phone
- Insert: `db.add_vendor(...)`

### 5.3 Edit/Delete Vendor
- Edit uses `db.update_vendor(vendor_id, vendor_name, contact_name, vendor_email, vendor_phone)`
- Delete uses `db.delete_vendor(vendor_id)` (removes related mappings)
- Also shows items supplied by the selected vendor via `db.get_vendor_items(vendor_id)` with `vendor_cost`

### 5.4 Incomplete Vendors
- Tab: shows vendors missing any of Contact Name, Email, or Phone
- Query: `db.get_incomplete_vendors()`
- Quick form to complete details and save via `db.update_vendor(...)`

## 6. Database Helpers (db_connector.py)

Key methods used in Phase 2:

- Connection management: `connect()`, `close_connection()`, `fetch_data()`, `execute_query()`

- Vendors
  - `get_all_vendors()`
  - `get_vendor_by_id(vendor_id)`
  - `add_vendor(vendor_name, contact_name, vendor_email, vendor_phone)`
  - `update_vendor(vendor_id, vendor_name, contact_name, vendor_email, vendor_phone)`
  - `delete_vendor(vendor_id)`
  - `get_vendor_items(vendor_id)` – returns items for a vendor and `vendor_cost`
  - `get_incomplete_vendors()` – vendors missing contact/email/phone

- Items
  - `get_all_items(source_filter=None, type_filter=None)`
  - `get_item_by_id(item_id)`
  - `add_item(item_name, item_type, source_sheet, sku=None, barcode=None, height=None, width=None, thickness=None)`
  - `update_item(item_id, item_name, item_type, source_sheet, sku=None, barcode=None, height=None, width=None, thickness=None)`
  - `delete_item(item_id)`
  - `get_incomplete_items()` – items missing required fields per source

- Mappings (ItemVendorMap)
  - `get_item_vendors(item_id)` – vendors for an item with mapping `cost` and `map_id`
  - `add_mapping(item_id, vendor_id, cost=None)` – creates a mapping if not exists
  - `update_mapping(map_id, cost)` – updates mapping cost (NULL if cost is None)
  - `delete_mapping(map_id)`

## 7. UX and Formatting (utils.py)

- `apply_custom_css()` – Global CSS to create a clean, modern look
- `format_currency(value)` – Formats numeric values as `$0.00` or `N/A`

## 8. Running the App

```bash
py -3 -m streamlit run app.py
```

- Local URL is shown in the terminal output. The app auto-reruns on file save.

## 9. Notes & Design Decisions

- Cost is modeled at the mapping level (`ItemVendorMap.cost`) because the same item can have different costs across vendors.
- For simplicity, default cost entered on item forms is only used to seed vendor mappings; it is not stored on the item itself.
- Source-specific fields reduce cognitive load and prevent irrelevant inputs.
- Incomplete tabs help teams quickly close data gaps without hunting across pages.

## 10. Future Enhancements (Suggestions)

- Bulk update costs (Save All) for item-vendor mappings
- Role-based access (e.g., read-only viewers vs editors)
- Export views to CSV/XLSX
- Search and quick actions directly from Dashboard
- Soft delete/archival for items and vendors
