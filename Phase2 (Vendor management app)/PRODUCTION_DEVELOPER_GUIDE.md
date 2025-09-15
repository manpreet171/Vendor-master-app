# SDGNY Vendor Management – Production Developer Guide (Phase 2)

This guide is for engineers taking the Streamlit-based Phase 2 prototype to a production-grade system. It explains the current architecture, business rules, data model, core logic, extension points, and recommended practices for security, testing, deployment, and operations.

---

## 1. System Overview

Phase 2 is a vendor–item management tool backed by Azure SQL Database. It focuses on:
- A minimal UI with three main areas: `Dashboard`, `Items`, `Vendors`.
- Viewing items and the vendors that supply them.
- CRUD for items and vendors.
- CRUD for item–vendor mappings, including per-vendor cost.
- Data completion workflows ("Incomplete" tabs) to fill missing critical data.

The UI is implemented with Streamlit for rapid iteration. The same logic and structure can be used as the base to migrate to a production stack (e.g., a React UI + FastAPI/Flask backend) while preserving database contracts and rules.

---

## 2. Repository Layout (Phase 2)

- `app.py`: Entry point. Sidebar nav. Renders tabs and wires UI to DB.
- `db_connector.py`: Database access layer. All SQL queries and mutations live here.
- `item_manager.py`: Items UI and workflows (view/filter, add, edit/delete, vendor mapping/cost editing, incomplete items).
- `vendor_manager.py`: Vendors UI and workflows (view, add, edit/delete, incomplete vendors).
- `utils.py`: UI helper utilities (CSS, currency formatting, messages, small helpers).
- `PHASE2_APP_DOCS.md`: Feature-level documentation for the app’s business behavior.
- `PRODUCTION_DEVELOPER_GUIDE.md`: This file – production guidance.
- `.env` / `.env.template`: Environment variables for DB connectivity.
- `requirements.txt`: Python dependencies for Phase 2.

All code paths that hit the database pass through the `DatabaseConnector` class in `db_connector.py`.

---

## 3. Data Model and Constraints

Tables (from Phase 1):

- `Vendors(
    vendor_id INT PK,
    vendor_name NVARCHAR(255) UNIQUE NOT NULL,
    contact_name NVARCHAR(255) NULL,
    vendor_email NVARCHAR(255) NULL,
    vendor_phone NVARCHAR(50) NULL
  )`

- `Items(
    item_id INT PK,
    item_name NVARCHAR(500) NOT NULL,
    item_type NVARCHAR(500) NOT NULL,
    source_sheet NVARCHAR(50) NOT NULL,   -- 'BoxHero' | 'Raw Materials'
    sku NVARCHAR(500) NULL,
    barcode NVARCHAR(500) NULL,
    height DECIMAL(10,4) NULL,
    width DECIMAL(10,4) NULL,
    thickness DECIMAL(10,4) NULL,
    CONSTRAINT unique_item UNIQUE (item_name, item_type, sku, height, width, thickness)
  )`

- `ItemVendorMap(
    map_id INT IDENTITY PK,
    item_id INT FK -> Items(item_id) ON DELETE CASCADE,
    vendor_id INT FK -> Vendors(vendor_id) ON DELETE CASCADE,
    cost DECIMAL(10,2) NULL,
    CONSTRAINT unique_map UNIQUE (item_id, vendor_id)
  )`

Key business rules:
- Item cost is vendor-specific and lives in `ItemVendorMap.cost` (not in `Items`).
- An item can map to many vendors; a vendor can supply many items.
- `unique_item` prevents accidental duplicate Items based on core attributes.
- `unique_map` prevents duplicate item–vendor rows.
- Cascade deletes propagate from Items/Vendors to `ItemVendorMap`.

---

## 4. Core Logic and Flows

### 4.1 Dashboard (`display_dashboard()` in `app.py`)
- User selects a source: BoxHero | Raw Materials.
- Then selects an `item_name` within that source.
- The app shows an Item Details summary:
  - Always: Name, Type, Source
  - BoxHero: SKU, Barcode
  - Raw Materials: Height, Width, Thickness
- Below, vendors are shown as expandable panels:
  - Header: `Vendor Name — $Cost`
  - Panel content: Contact, Email (mailto link), Phone (tel link)
- Vendors list is sorted by cost ascending (NULL last).

### 4.2 Items (`item_manager.py`)
- View + filter: by `item_type` and `source_sheet`.
- Add Item (source-specific forms):
  - Common: Item Name, Item Type, Source
  - BoxHero: SKU, Barcode (dimensions not required/applicable)
  - Raw Materials: Height, Width, Thickness (SKU/Barcode not required/applicable)
  - After a successful add, the UI prompts to assign vendors with per-vendor cost (outside the form to avoid Streamlit form limitations). Creates `ItemVendorMap` rows.
- Edit Item (source-specific):
  - BoxHero: can update SKU, Barcode
  - Raw Materials: can update Height, Width, Thickness
- Delete Item: also deletes mappings (cascade).
- View Vendors for Item:
  - Displays current mappings (with formatted costs).
  - Shows an inline per-vendor cost editor for fast cost updates.
- Incomplete Items:
  - BoxHero: missing SKU or Barcode
  - Raw: missing Height, Width, or Thickness
  - Quick forms to complete missing data.

### 4.3 Vendors (`vendor_manager.py`)
- View All Vendors: list with data table.
- Add Vendor: vendor_name (unique), contact_name, email, phone.
- Edit/Delete Vendor: CRUD with cascade delete for mappings.
- Vendor Items: show items + `vendor_cost` (from `ItemVendorMap.cost`).
- Incomplete Vendors: missing contact name, email, or phone. Simple form to complete details.

---

## 5. Database Access Layer (`db_connector.py`)

The `DatabaseConnector` centralizes DB work. Key methods:

- Connection: `connect()`, `close_connection()`, `fetch_data(query, params=None)`, `execute_query(query, params=None)`
- Vendors: `get_all_vendors()`, `get_vendor_by_id()`, `add_vendor()`, `update_vendor()`, `delete_vendor()`, `get_vendor_items(vendor_id)`, `get_incomplete_vendors()`
- Items: `get_all_items(source_filter=None, type_filter=None)`, `get_item_by_id(item_id)`, `add_item(...)`, `update_item(...)`, `delete_item(item_id)`, `get_incomplete_items()`
- Mappings: `get_item_vendors(item_id)`, `add_mapping(item_id, vendor_id, cost=None)`, `update_mapping(map_id, cost)`, `delete_mapping(map_id)`

Guidelines:
- All new SQL must be placed here to keep UI modules clean.
- Use parameterized queries exclusively.
- Keep naming consistent with existing methods for discoverability.

---

## 6. Configuration & Secrets

Environment variables (see `.env.template`):
- `DB_SERVER`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_DRIVER` (e.g., `{ODBC Driver 17 for SQL Server}`)

Recommendations for production:
- Do not commit `.env` to version control.
- Use Azure Key Vault or a secret manager. Inject secrets into the environment at runtime.
- Prefer managed identity (Azure) for DB auth where possible; otherwise rotate SQL users regularly.

---

## 7. Logging, Telemetry, and Error Handling

- Add structured logging (e.g., `structlog` or Python `logging` with JSON formatter).
- Log at the data-access layer for all write operations (info level) and catch/propagate errors with context (warning/error levels).
- In Streamlit, surface user-friendly messages and log stack traces server-side.
- For production APIs (see migration plan), integrate Application Insights (Azure) or OpenTelemetry for traces and metrics.

---

## 8. Validation and Business Rules

- Items:
  - Reject duplicates per `unique_item` before insert (we already check in SQL; optionally check in code).
  - BoxHero requires SKU/Barcode (enforced through the Incomplete Items workflow; could be enforced at create/update if desired).
  - Raw requires height/width/thickness (same as above).
- Vendors:
  - `vendor_name` must be unique; basic contact info should be provided; Incomplete Vendors workflow identifies gaps.
- Mappings:
  - Enforce uniqueness (item_id, vendor_id) at DB level.
  - Cost can be NULL but UI encourages setting it.

---

## 9. Testing Strategy

- Unit tests:
  - Mock the `DatabaseConnector` for UI tests.
  - Test each DB method with a disposable test database (use transactions rolled back per test).
- Integration tests:
  - E2E tests that create a vendor, item, mapping, set costs, and clean up.
- Data validation tests:
  - Verify Incomplete Items/Vendors lists detect expected rows.
- Performance tests:
  - Load-test queries for Items/Vendors list, and mapping editors.

Suggested tools:
- `pytest`, `pytest-cov`
- `tox` for multi-env testing
- `locust`/`k6` for performance (optional)

---

## 10. Security, Roles, and Access Control

- Streamlit prototype has no auth. For production:
  - Put behind Azure AD (App Registration) or corporate SSO.
  - Add role-based access (viewer vs editor). Editors can change data; viewers cannot.
- Validate and sanitize all user inputs.
- Enforce least privilege SQL credentials (separate read vs write roles if needed).

---

## 11. Deployment (Recommended)

Short-term (pilot):
- Containerize the app (Docker) and run on Azure App Service / Azure Container Apps.
- Streamlit is stateful per session; configure health checks and limited scaling.

Long-term (production):
- Migrate to a service split:
  - Backend API (FastAPI/Flask) that exposes endpoints for CRUD and reports; containerized and deployed on App Service / AKS.
  - Frontend (React/Next.js) consuming those APIs.
  - Background jobs (Azure Functions) for periodic validation/reporting (optional).

Infra notes:
- Use Azure Pipelines or GitHub Actions for CI/CD.
- Use deployment slots for safe cutovers.
- Run DB migrations through a controlled process (see below).

---

## 12. Database Migration Workflow

- Version SQL changes (DDL/DML) in a migrations folder.
- Use a tool (Alembic for SQLAlchemy, Flyway, or custom SQL runner) to apply migrations.
- Enforce forward-only migrations and backups before critical changes.
- Add a seed script for minimal local/dev data.

---

## 13. Performance and UX Considerations

- Indexing:
  - Ensure indexes on `Items(source_sheet)`, `Items(item_type)`, `ItemVendorMap(item_id)`, `ItemVendorMap(vendor_id)`.
- Pagination:
  - For large datasets, apply `TOP`/`OFFSET FETCH` or server-side pagination.
- Caching:
  - Cache reference lists (e.g., item types) where appropriate.
- UI polish:
  - Use card-like expanders (already implemented on Dashboard) and hide technical IDs.

---

## 14. Extensibility Points

- Add search endpoints (API) with server-side filtering/sorting.
- Add bulk editing for costs (Save All) with optimistic concurrency control.
- Add audit trail tables: `ChangeLog` to track edits (who/what/when).
- Add file export (CSV/XLSX) endpoints for lists.

---

## 15. Local Development

- Requirements:
  ```bash
  pip install -r requirements.txt
  ```
- Run (prototype):
  ```bash
  py -3 -m streamlit run app.py
  ```
- Environment:
  - Copy `.env.template` to `.env` and set values.
  - Prefer `{ODBC Driver 17 for SQL Server}` or `{ODBC Driver 18 for SQL Server}` in Windows.

---

## 16. Known Gaps / Next Steps to Production

- Authentication & RBAC: integrate Azure AD and define roles.
- Centralized configuration and secret rotation via Key Vault.
- Structured logging and distributed tracing.
- API layer abstraction (FastAPI) with typed schemas (Pydantic) and validation.
- Test coverage and CI pipeline.
- Observability: dashboards on errors, latencies, throughput (App Insights).

---

## 17. Contact and Handover Notes

- Business logic reference: `PHASE2_APP_DOCS.md` and inline docstrings.
- All DB writes go through `db_connector.py` – extend there for new features.
- Keep source-specific rules consistent:
  - BoxHero → expects SKU/Barcode (dimensions N/A)
  - Raw Materials → expects Height/Width/Thickness (SKU/Barcode N/A)
- Mapping cost is authoritative at `ItemVendorMap.cost`.

This guide should enable engineers to stabilize the prototype and incrementally evolve it into a production-ready service with clean separation of concerns, strong validation, and automated delivery.
