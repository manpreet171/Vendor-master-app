# Phase 3 Requirements System - Complete Guide

**Version:** 2.0 | **Last Updated:** October 14, 2025

---

## Complete Data Flow Architecture

### End-to-End Journey

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐     ┌──────────────┐
│   USER      │────→│   SYSTEM     │────→│  OPERATOR   │────→│   VENDOR   │────→│  COMPLETED   │
│             │     │              │     │             │     │            │     │              │
│ Submit      │     │ Auto Bundle  │     │ Review &    │     │ Ship       │     │ Receive &    │
│ Request     │     │ (Cron 2x/wk) │     │ Approve     │     │ Items      │     │ Deliver      │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘     └──────────────┘
```

---

## Database Tables & Relationships

### Core Tables

**1. requirements_users**
```sql
- user_id (PK)
- username
- password_hash
- full_name
- email
- department
- user_role (User/Operator/Admin/Master)
- is_active
```

**2. requirements_orders** (User Requests)
```sql
- req_id (PK)
- req_number (REQ-YYYYMMDD-NNN)
- user_id (FK → requirements_users)
- status (Pending/In Progress/Completed)
- total_items
- total_quantity
- created_at
- completed_at
```

**3. requirements_order_items** (Items in Each Request)
```sql
- order_item_id (PK)
- req_id (FK → requirements_orders)
- item_id (FK → items)
- quantity
- project_number
- parent_project_id (FK → projects)
- sub_project_number
- project_name
```

**4. requirements_bundles** (Vendor Bundles)
```sql
- bundle_id (PK)
- bundle_name (BUNDLE-YYYYMMDD-HHMMSS-NN)
- vendor_id (FK → vendors)
- status (Active/Reviewed/Approved/Ordered/Completed)
- total_items
- total_quantity
- duplicates_reviewed (0/1)
- created_at
- reviewed_at
- approved_at
- ordered_at
- completed_at
- po_number
- po_date
- packing_slip_code
```

**5. requirements_bundle_items** (Items in Each Bundle)
```sql
- bundle_item_id (PK)
- bundle_id (FK → requirements_bundles)
- item_id (FK → items)
- total_quantity
- user_breakdown (JSON: {"user_id": quantity})
```

**6. requirements_bundle_mapping** (Links Requests to Bundles)
```sql
- mapping_id (PK)
- bundle_id (FK → requirements_bundles)
- req_id (FK → requirements_orders)
```

---

## Status Workflow

### User Request Status

```
Pending ──→ In Progress ──→ Completed
   ↑            ↓
   └────────────┘
   (Can revert if bundle changes)
```

**Pending:**
- User submitted request
- Waiting for bundling
- User can edit quantities
- Not yet in any bundle

**In Progress:**
- Request is part of a bundle
- Bundle status: Active/Reviewed/Approved/Ordered
- User CANNOT edit quantities (locked)
- Operator processing

**Completed:**
- Bundle marked as Completed
- Items received and delivered
- Final status (no changes)

---

### Bundle Status Workflow

```
Active ←→ Reviewed → Approved → Ordered → Completed
  ↑         ↑           ↓
  └─────────┘         LOCKED
```

**Active:**
- Bundle created by cron job
- Needs operator review
- Operator can move items between bundles
- Can revert from Reviewed

**Reviewed:**
- Operator has reviewed bundle
- Verified vendor, items, duplicates
- Ready for approval
- Can revert to Active
- Auto-reverts if items moved to this bundle

**Approved:**
- Operator approved for ordering
- **LOCKED** - no changes allowed
- Cannot move items
- Cannot change status back
- Ready to place PO

**Ordered:**
- PO placed with vendor
- Waiting for delivery
- PO number and date recorded

**Completed:**
- Items received
- Packing slip recorded
- All linked user requests marked Completed
- Final status

---

## Key Business Rules

### Duplicate Detection

**What is a Duplicate?**
- Same item
- Same project number
- Same sub-project number (if applicable)
- Multiple users

**Example:**
```
User A: ACRYLITE P99, Project 25-1559, 3 pcs
User B: ACRYLITE P99, Project 25-1559, 2 pcs
→ DUPLICATE DETECTED (same item, same project)
```

**How System Handles:**
1. ✅ Both requests accepted
2. ✅ Bundled together (total: 5 pcs)
3. ⚠️ Operator sees warning
4. ✅ Operator reviews and confirms quantities
5. ✅ Marks duplicates as reviewed
6. ✅ Continues normal flow

**Important:** Duplicate detection only checks items **actually in the bundle** (not all items from linked requests)

---

### Item Movement Rules

**When Can Items Be Moved?**
- ✅ Source bundle: Active or Reviewed
- ✅ Target bundle: Active or Reviewed
- ❌ Cannot move from/to Approved bundles (locked)

**Auto-Revert Logic:**
```
IF target_bundle.status == 'Reviewed':
    target_bundle.status = 'Active'
    message = "Bundle reverted to Active for re-review"
```

**Why?** Ensures operator reviews bundles that have changed

---

### Approval Gate System

**Rule:** Must review ALL bundles before approving ANY bundle

**Workflow:**
```
1. Operator reviews Bundle A → Status: Reviewed
2. Operator reviews Bundle B → Status: Reviewed
3. Operator reviews Bundle C → Status: Reviewed
4. ✅ ALL REVIEWED → Approval unlocked
5. Operator selects bundles to approve
6. Click "Approve Selected"
7. Selected bundles → Status: Approved
```

**Why?** Quality control - ensures all bundles are verified before ordering

---

## Cron Job (Automatic Bundling)

### Schedule
- **Frequency:** Twice per week
- **Days:** Tuesday, Thursday (configurable)
- **Time:** 2:00 AM (configurable)

### What It Does

**1. Scan Pending Requests**
```sql
SELECT * FROM requirements_orders 
WHERE status = 'Pending'
ORDER BY created_at ASC
```

**2. Group Items by Vendor**
```
Algorithm:
├─ For each pending request:
│  ├─ For each item in request:
│  │  ├─ Find vendor from item_vendor_mapping
│  │  ├─ Group by vendor_id
│  │  └─ Aggregate quantities
│  └─ Create user_breakdown JSON
└─ Create bundles per vendor
```

**3. Create Bundles**
```sql
INSERT INTO requirements_bundles (
    bundle_name,
    vendor_id,
    status,
    total_items,
    total_quantity
) VALUES (
    'BUNDLE-20251014-020000-01',
    5,
    'Active',
    3,
    10
)
```

**4. Create Bundle Items**
```sql
INSERT INTO requirements_bundle_items (
    bundle_id,
    item_id,
    total_quantity,
    user_breakdown
) VALUES (
    1,
    150,
    5,
    '{"3": 3, "5": 2}'  -- User 3: 3 pcs, User 5: 2 pcs
)
```

**5. Link Requests to Bundles**
```sql
INSERT INTO requirements_bundle_mapping (
    bundle_id,
    req_id
) VALUES (1, 10), (1, 12)
```

**6. Update Request Status**
```sql
UPDATE requirements_orders
SET status = 'In Progress'
WHERE req_id IN (10, 12)
```

---

## HTML Table Display (Operators)

### Table Structure

```
┌──────────────────────┬────────────────┬──────────────┬──────────┐
│ Item                 │ User           │ Project      │ Quantity │
├──────────────────────┼────────────────┼──────────────┼──────────┤
│ ACRYLITE Non-glare   │ 👤 Prod Mgr    │ 📋 25-1559   │    1 pc  │
│ 48 x 96 x 0.125      │                │ 📋 23-1672   │    2 pcs │
│ Total: 5 pcs         │ 👤 Prod Mgr2   │ 📋 25-1559   │    2 pcs │
├──────────────────────┼────────────────┼──────────────┼──────────┤
│ DURA-CAST IM-7328    │ 👤 M. Singh    │ 📋 23-1472   │    1 pc  │
│ 48 x 96 x 0.1875     │                │ 📋 23-1672   │    1 pc  │
│ Total: 2 pcs         │                │              │          │
└──────────────────────┴────────────────┴──────────────┴──────────┘
```

### Features
- ✅ Item cell spans multiple rows (rowspan)
- ✅ User cell spans multiple projects (rowspan)
- ✅ Per-project quantity breakdown
- ✅ Alternating row colors
- ✅ Hover effects
- ✅ Professional styling

---

## All Possible Scenarios

### Scenario 1: Normal Flow (No Issues)
```
1. User submits request → Pending
2. Cron job runs → Bundle created (Active)
3. Operator reviews → Reviewed
4. Operator approves → Approved
5. Operator places PO → Ordered
6. Items arrive → Completed
```

### Scenario 2: Duplicate Detection
```
1. User A & B request same item, same project
2. Cron job creates bundle
3. System detects duplicate
4. Operator sees warning
5. Operator reviews quantities
6. Marks duplicates as reviewed
7. Continues normal flow
```

### Scenario 3: Item Movement (Vendor Change)
```
1. Bundle A (Vendor X): Item A, Item B
2. Operator discovers Vendor X doesn't have Item A
3. Operator clicks "Report Issue" on Item A
4. Selects "Alternative Vendor" (Vendor Y)
5. System moves Item A to Bundle B (Vendor Y)
6. Bundle B reverts to Active (needs re-review)
7. Operator reviews both bundles
8. Continues normal flow
```

### Scenario 4: Bundle Changes After Review
```
1. Bundle A status: Reviewed
2. Operator moves Item X to Bundle A
3. System auto-reverts Bundle A to Active
4. Operator must review Bundle A again
5. Marks as Reviewed
6. Continues normal flow
```

### Scenario 5: User Updates Pending Request
```
1. User submits request (5 pcs)
2. Status: Pending
3. User realizes needs 7 pcs
4. Goes to My Requests
5. Updates quantity to 7
6. Cron job runs
7. Bundle created with 7 pcs
```

### Scenario 6: User Tries to Update In Progress Request
```
1. User submits request
2. Cron job bundles it → In Progress
3. User tries to update quantity
4. System blocks: "Locked - already in bundle"
5. User must submit new request for additional items
```

---

## Error Handling & Edge Cases

### Edge Case 1: Empty Bundle After Item Movement
```
Scenario:
- Bundle A has only 1 item
- Operator moves that item to Bundle B
- Bundle A is now empty

System Response:
- Deletes Bundle A automatically
- Removes bundle_mapping entries
- Message: "Original bundle was empty and removed"
```

### Edge Case 2: Duplicate Warning After Item Movement
```
Scenario:
- Bundle A: Item X (duplicate reviewed)
- Operator moves Item Y to Bundle B
- Bundle B should NOT show Item X duplicate warning

Fix Applied:
- Duplicate detection only checks items IN the bundle
- Uses subquery to filter by requirements_bundle_items
```

### Edge Case 3: Multiple Users, Multiple Projects
```
Scenario:
- User A: Item X, Project 1 (2 pcs)
- User A: Item X, Project 2 (3 pcs)
- User B: Item X, Project 1 (1 pc)

Display:
┌──────────┬─────────┬───────────┬──────────┐
│ Item X   │ User A  │ Project 1 │   2 pcs  │
│          │         │ Project 2 │   3 pcs  │
│          │ User B  │ Project 1 │   1 pc   │
└──────────┴─────────┴───────────┴──────────┘

Duplicate Detection:
- Item X, Project 1: User A (2) + User B (1) = DUPLICATE ⚠️
- Item X, Project 2: User A only = NO DUPLICATE ✅
```

---

## API / Function Reference

### Key Functions (db_connector.py)

**User Functions:**
- `authenticate_user(username, password)` - Login
- `get_all_items(source_filter)` - Get items
- `create_user_request(user_id, items)` - Submit request
- `get_user_requests(user_id)` - Get user's requests
- `update_order_item_quantity(order_item_id, new_quantity)` - Update pending request

**Bundling Functions:**
- `get_pending_requests()` - Get all pending requests
- `create_bundle(vendor_id, items, user_breakdown)` - Create bundle
- `get_active_bundles()` - Get all bundles
- `detect_duplicate_projects_in_bundle(bundle_id)` - Find duplicates

**Operator Functions:**
- `mark_bundle_reviewed(bundle_id)` - Mark as reviewed
- `mark_bundles_approved_bulk(bundle_ids)` - Approve multiple
- `move_item_to_vendor(current_bundle_id, item_id, new_vendor_id)` - Move item
- `mark_bundle_duplicates_reviewed(bundle_id)` - Mark duplicates reviewed
- `update_bundle_item_user_quantity(bundle_id, item_id, user_id, new_qty)` - Update duplicate quantity

**Order Functions:**
- `record_order_details(bundle_id, po_number, po_date)` - Record PO
- `mark_bundle_completed(bundle_id, packing_slip_code)` - Mark completed

---

## Security & Permissions

### Role-Based Access

**User:**
- ✅ Browse items
- ✅ Add to cart
- ✅ Submit requests
- ✅ View own requests
- ✅ Update pending requests
- ❌ Cannot see other users' requests
- ❌ Cannot access operator dashboard

**Operator:**
- ✅ View all user requests
- ✅ View all bundles
- ✅ Review bundles
- ✅ Approve bundles
- ✅ Move items between bundles
- ✅ Place orders
- ✅ Mark completed
- ❌ Cannot access system reset
- ❌ Cannot access manual bundling

**Admin:**
- ✅ All Operator permissions
- ✅ User management
- ✅ View analytics
- ❌ Cannot access system reset
- ❌ Cannot access manual bundling

**Master:**
- ✅ All Admin permissions
- ✅ Manual bundling
- ✅ System reset
- ✅ Full system access

---

## Performance Optimization

### Caching Strategy
- Item lists cached for 60 seconds
- User name map cached per page load
- Bundle items batched (single query)

### Database Indexes
- `requirements_orders.user_id`
- `requirements_orders.status`
- `requirements_order_items.req_id`
- `requirements_order_items.item_id`
- `requirements_bundles.vendor_id`
- `requirements_bundles.status`
- `requirements_bundle_items.bundle_id`
- `requirements_bundle_mapping.bundle_id`
- `requirements_bundle_mapping.req_id`

---

## Monitoring & Alerts

### Key Metrics to Monitor
- Pending requests count
- Average bundling time
- Duplicate detection rate
- Bundle approval rate
- Order completion time
- User request volume

### Alert Conditions
- ⚠️ Pending requests > 50
- ⚠️ Bundle stuck in Active > 7 days
- ⚠️ Cron job failed
- ⚠️ Database connection errors
- ⚠️ Duplicate rate > 20%

---

## Future Enhancements

### Phase 3B (Planned)
- ✅ Automatic RFQ emails to vendors
- ✅ Vendor quote comparison
- ✅ Automated PO generation
- ✅ Real-time inventory tracking
- ✅ Mobile app support

### Phase 3C (Future)
- ✅ Machine learning for vendor selection
- ✅ Predictive ordering
- ✅ Integration with accounting system
- ✅ Advanced analytics dashboard

---

**End of Complete System Guide**
