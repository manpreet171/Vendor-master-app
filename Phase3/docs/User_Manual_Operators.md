# Phase 3 Operator Dashboard – Complete User Manual (For Operators)

**Version:** 3.0 | **Last Updated:** November 7, 2025

This comprehensive guide explains how to use the Operator Dashboard to review requests, manage vendor orders, handle all possible scenarios, and close out completed bundles.

## Table of Contents
1. [Getting Started](#1-sign-in-as-operator)
2. [Complete Data Flow Journey](#complete-data-flow-journey)
3. [Operator Tabs Overview](#2-operator-tabs)
4. [User Requests Tab](#3-user-requests--see-what-needs-ordering)
5. [Active Bundles Tab - Complete Guide](#4-active-bundles--review-approve-and-track-orders)
6. [All Possible Scenarios](#all-possible-scenarios)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Best Practices](#best-practices)

---

## 1) Sign In as Operator
- Log in with your operator/admin account.
- You’ll see your name and role in the left sidebar.
- The left sidebar also shows current database connection status.
- Use “🚪 Logout” in the sidebar to exit.

## 2) Operator Tabs
At the top of the Operator Dashboard you'll see these tabs:
- "📋 User Requests"
- "📦 Active Bundles"
- "📊 Analytics"

**Note:** Master role has additional tabs:
- "🤖 Manual Bundling" (for emergency/special cases)
- "🧹 System Reset" (database cleanup)
- "👤 User Management" (user account management)

---

## Complete Data Flow Journey

### End-to-End Process Overview

```
USER → SYSTEM (Cron) → YOU (Operator) → OPERATION → VENDOR → COMPLETION
│       │               │                │           │         │
│       │               │                │           │         └─ Items delivered
│       │               │                │           └─ Order placed & shipped
│       │               │                └─ Final approval
│       │               └─ Review bundles
│       └─ Auto-bundle (2x/week)
└─ Submit request (with notes & dates)
```

**Your Role:** You are the bridge between user requests and vendor fulfillment. You review bundles and send them to Operation Team for final approval.

---

### Detailed Flow with Your Actions

#### Stage 1: User Submits Request
**What Happens:**
- User adds items to cart
- Submits request (e.g., REQ-20251014-001)
- Status: 🟡 Pending

**Your Action:** None (just awareness)

---

#### Stage 2: System Creates Bundles (Automatic)
**What Happens:**
- Cron job runs twice a week (Tuesday, Thursday at 2 AM)
- Scans all Pending requests
- Groups items by vendor
- Creates bundles (e.g., BUNDLE-20251014-001)
- Status: 🟡 Active (needs your review)

**Your Action:** None (automatic)

**What You See:**
- New bundles appear in "Active Bundles" tab
- Each bundle shows vendor, items, quantities
- User requests change to "In Progress"

---

#### Stage 3: YOU Review Bundles
**What Happens:**
- You open Active Bundles tab
- See all Active bundles
- Review each bundle

**Your Actions:**
1. **Check vendor contact info** (email, phone)
2. **Review all items and quantities** (use HTML table with Date Needed column)
3. **Read user notes** (if provided)
4. **Check for duplicate warnings** (same item, same project)
5. **Check merge badge** (🔄 if bundle was updated)
6. **Verify correct vendor** (check alternative vendors if needed)
7. **Click "✅ Mark as Reviewed"**
8. **Confirm checklist** (4 items)
9. Bundle status → 🟢 Reviewed
10. **Bundle sent to Operation Team**

**Important:** Must review ALL bundles before Operation Team can approve them

---

#### Stage 4: OPERATION TEAM Approves
**What Happens:**
- Operation Team reviews all Reviewed bundles
- They can approve or reject
- If rejected, bundle returns to Active status with rejection reason

**Your Actions:**
- None (Operation Team handles this)
- If rejected, you'll see rejection warning in bundle
- Fix issues and mark as Reviewed again

---

#### Stage 5: YOU Place Orders
**What Happens:**
- Bundles are Approved by Operation Team
- You can now place orders with vendors

**Your Actions:**
1. **Contact vendor** (email/phone from bundle)
2. **Place purchase order**
3. **Record PO number** in system
4. **Click "📦 Mark as Ordered"**
5. Bundle status → 📦 Ordered
6. ✉️ **Users receive email notification**

**Note:** Approved bundles are LOCKED (no changes allowed)

---

#### Stage 5: YOU Place Orders
**What Happens:**
- Approved bundles ready for ordering
- You contact vendors for quotes

**Your Actions:**
1. **Contact vendor** (email/phone from bundle)
2. **Request quote** for items in bundle
3. **Negotiate pricing** if needed
4. **Place purchase order** with vendor
5. **Click "📦 Order Placed"** in bundle
6. **Enter PO number** (e.g., PO-2025-1014-A)
7. **Enter PO date**
8. Bundle status → 📦 Ordered

---

#### Stage 6: Vendor Ships Items
**What Happens:**
- Vendor processes order
- Ships items to warehouse
- Items arrive at receiving

**Your Action:** Monitor delivery timeline

---

#### Stage 7: YOU Mark Completed
**What Happens:**
- Items arrive at warehouse
- Receiving verifies shipment

**Your Actions:**
1. **Verify all items received**
2. **Check packing slip**
3. **Click "🏁 Mark as Completed"** in bundle
4. **Enter packing slip code** (e.g., PS-2025-1014-A)
5. Bundle status → 🎉 Completed
6. **All linked user requests** → ✅ Completed

---

### Timeline Summary

```
Day 0: User submits request (Pending)
Day 1-3: Wait for cron job
Day 3: Cron creates bundle (Active)
Day 3: YOU review bundle (Reviewed)
Day 3: YOU approve bundle (Approved)
Day 3-4: YOU place order (Ordered)
Day 4-7: Vendor ships
Day 7: YOU mark completed (Completed)

Total: 7 days average
```

---

## 3) User Requests – See What Needs Ordering
Open `📋 User Requests` to view all pending items from users.

**What You See:**
- Total pending requests count
- Total items waiting
- List of all pending requests

**Request Details:**
- Request number (REQ-20251014-001)
- User name
- Submission date
- Total items
- Total pieces
- Status (Pending/In Progress/Completed)

**How to Use:**
1. **Expand request** to see items
2. **Review item details** (name, dimensions, quantity, project)
3. **Check project numbers** for tracking
4. **Monitor for urgent requests**

**Note:** Bundles are created automatically by the system (cron job runs twice a week). You don't need to manually trigger bundling.

**Your Action:** This is informational only. Actual work happens in Active Bundles tab.

---

## 4) Active Bundles – Review, Approve, and Track Orders

Open `📦 Active Bundles` to manage the complete bundle lifecycle.

### **Bundle Status Workflow:**

Bundles move through these statuses:
1. **🟡 Active** - New bundle, needs your review
2. **🟢 Reviewed** - You've reviewed it, ready for approval
3. **🔵 Approved** - Approved for ordering
4. **📦 Ordered** - PO placed with vendor
5. **🎉 Completed** - Items received and delivered

### **Review Progress Tracking:**

At the top of Active Bundles, you'll see a simple progress indicator:
- **While reviewing**: "📊 Review Progress: 6/10 bundles reviewed • 4 remaining"
- **When complete**: "✅ All bundles reviewed! Select bundles below to approve."

### **Bulk Approval (NEW):**

**When ALL bundles are reviewed:**
- Checkboxes appear next to Reviewed bundles
- "Select All" checkbox to select all at once
- **"🎯 Approve Selected (N)"** button to approve selected bundles

**Important Rule:** You must review ALL bundles individually before you can approve ANY bundle. This ensures quality control.

### **Individual Bundle Actions:**

**For Active Bundles (🟡):**
- **"✅ Mark as Reviewed"** - Opens checklist to verify vendor, items, and duplicates
- **"⚠️ Report Issue"** - Move items to different vendors if needed

**For Reviewed Bundles (🟢):**
- **Status**: "✅ Reviewed - ready for approval"
- **"↩️ Revert"** - Revert to Active if you need to make changes

**For Approved Bundles (🔵):**
- **"📦 Order Placed"** - Record PO details when order is placed with vendor
- **"🏁 Mark as Completed"** - Disabled until order is placed

**For Ordered Bundles (📦):**
- **"🏁 Mark as Completed"** - Click when goods arrive; enter packing slip details

### **Bundle Information:**

What you'll see in each bundle panel:
- **Vendor block**: name, email, phone
- **Items table** (NEW): Professional table showing:
  - **Item column**: Item name, dimensions, total quantity
  - **User column**: Which user requested it
  - **Project column**: Project number for each request
  - **Quantity column**: Per-project quantity breakdown
- **Per-project quantities** (NEW): See exactly how many pieces each user needs for each project
- **Duplicate detection**: Alerts if multiple users requested same item for same project (only for items IN this bundle)
- **From Requests**: request numbers linked to this bundle for traceability
- **Other vendor options** (single-item bundles): View-only dropdown showing alternative vendors

**Example Table Display:**
```
| Item                    | User              | Project    | Quantity |
|-------------------------|-------------------|------------|----------|
| ACRYLITE Non-glare P99  | Production Mgr    | 📋 25-1559 | 1 pc     |
| 48 x 96 x 0.125         |                   | 📋 23-1672 | 2 pcs    |
| Total: 5 pcs            | Production Mgr2   | 📋 25-1559 | 2 pcs    |
```

### **Auto-Revert Safety Feature:**

If you move an item to a Reviewed bundle:
- The bundle automatically reverts to Active status
- You must review it again before it can be approved
- This prevents approving bundles that have changed

### **Status Filter:**

Use the dropdown to filter bundles by status:
- 🟡 Active (N) - Need review
- 🟢 Reviewed (N) - Ready to approve
- 🔵 Approved (N) - Ready to order
- 📦 Ordered (N) - Waiting delivery
- 🎉 Completed (N) - Finished
- 📋 All Bundles (N) - Show everything

## 5) Analytics Tab
Open `📊 Analytics` to view system statistics and performance metrics.

- **Bundle statistics**: Total bundles by status
- **Request statistics**: Total requests and items
- **Vendor performance**: Which vendors are used most
- **Timeline charts**: Visual representation of workflow

## 6) User Management – Admin-Only
Open `👤 User Management` to manage user accounts (admin/operator only).

- **View users**: See status, role, contact details.
  - “Full Name”, “Email”, “Department”
  - “Role”: User / Operator
  - “Active” checkbox
  - “New Password (optional)”
  - Buttons: “💾 Save Changes”, “❌ Cancel”
- **Reset Password**: Use the “Reset Password” button (enter a new password first).
- **Delete**: Click “Delete” to remove a user (only when appropriate).
- **Create User**: Fill out the form and click “Create User”.

## 7) Your Day-to-Day Flow (Updated with Review Workflow)

**Step 1: Check Requests**
- Open `📋 User Requests` to understand what users need

**Step 2: Review Bundles (NEW)**
- Open `📦 Active Bundles`
- See progress: "📊 Review Progress: X/Y bundles reviewed • Z remaining"
- For each Active bundle:
  - Click "✅ Mark as Reviewed"
  - Checklist appears - verify all 4 items:
    - ☐ Vendor contact verified
    - ☐ All items and quantities reviewed
    - ☐ Duplicates reviewed (if any)
    - ☐ Correct vendor selected
  - Click "Confirm & Mark as Reviewed"
- Repeat for all bundles

**Step 3: Approve Bundles (NEW)**
- Once ALL bundles are reviewed
- Message appears: "✅ All bundles reviewed! Select bundles below to approve."
- Checkboxes appear next to Reviewed bundles
- Select bundles you want to approve (or click "Select All")
- Click "🎯 Approve Selected (N)"
- Bundles move to Approved status

**Step 4: Place Orders**
- For Approved bundles, contact vendors for quotes
- When ready to order, click "📦 Order Placed"
- Enter PO number and date
- Bundle moves to Ordered status

**Step 5: Complete Orders**
- When goods arrive at stores
- Click "🏁 Mark as Completed"
- Enter packing slip code
- Bundle moves to Completed status
- All linked user requests automatically marked as Completed

**Important Notes:**
- If a bundle changes after review (item moved), it auto-reverts to Active - you must review again
- You can approve bundles in batches - no need to approve all at once
- Status filter helps you focus on specific stages

---

## All Possible Scenarios

### Scenario 1: Normal Flow (No Issues)

**Situation:** Bundle created with no duplicates, correct vendor, all items available.

**Your Actions:**
1. Open Active Bundles tab
2. See bundle: BUNDLE-20251014-001 (S & F Supplies Inc.)
3. Review vendor contact info ✅
4. Review items in HTML table ✅
5. No duplicate warnings ✅
6. Click "✅ Mark as Reviewed"
7. Confirm checklist (all 4 items)
8. Bundle → Reviewed
9. When all reviewed, select bundle
10. Click "Approve Selected"
11. Bundle → Approved
12. Contact vendor for quote
13. Place PO
14. Click "📦 Order Placed"
15. Enter PO details
16. Bundle → Ordered
17. Wait for delivery
18. Items arrive
19. Click "🏁 Mark as Completed"
20. Enter packing slip code
21. Bundle → Completed ✅

**Timeline:** 7 days average

---

### Scenario 2: Duplicate Detection (Same Item, Same Project)

**Situation:** Two users requested ACRYLITE P99 for Project 25-1559.

**What You See:**
```
⚠️ 1 DUPLICATE PROJECT(S) DETECTED - REVIEW REQUIRED

🔍 Duplicate 1: ACRYLITE Non-glare P99 - Project 25-1559
Multiple users requested this item for the same project

User Contributions:
👤 Production Manager: 3 pcs    [Quantity: 3] [Update]
👤 Production Manager2: 2 pcs   [Quantity: 2] [Update]

💡 Options: Adjust quantities, remove a user (set to 0), or keep both as-is.

[✅ Mark Duplicates as Reviewed]
```

**Your Actions:**
1. **Review the duplicate**
   - Check if both users really need it
   - Verify project number is correct
   - Check quantities

2. **Options:**
   - **Keep both** (5 pcs total) - if both users need it
   - **Adjust quantities** - change numbers and click Update
   - **Remove one user** - set quantity to 0 and click Update

3. **Example Decision:**
   - Contact Production Manager: "Do you both need ACRYLITE for 25-1559?"
   - Response: "Yes, different phases of same project"
   - Action: Keep both (5 pcs total)

4. **Mark as Reviewed:**
   - Click "✅ Mark Duplicates as Reviewed"
   - Duplicate warning disappears
   - Green checkmark shows: "✅ Duplicates Reviewed - 1 item(s) were checked"

5. **Continue normal flow:**
   - Click "✅ Mark as Reviewed" for bundle
   - Confirm checklist
   - Bundle → Reviewed

**Why This Matters:** Prevents over-ordering and waste

---

### Scenario 3: Wrong Vendor (Need to Move Item)

**Situation:** Bundle has Item A and Item B. Vendor doesn't carry Item A.

**What You See:**
```
Bundle: BUNDLE-20251014-001
Vendor: S & F Supplies Inc.
Items:
- ACRYLITE Non-glare P99 (5 pcs)
- DURA-CAST IM-7328 (2 pcs)
```

**Your Actions:**
1. **Discover issue:**
   - Contact S & F Supplies
   - They say: "We don't carry ACRYLITE"

2. **Report issue:**
   - Click "⚠️ Report Issue" on ACRYLITE item
   - Select reason: "Alternative Vendor"

3. **Choose new vendor:**
   - Dropdown shows alternative vendors:
     - O Reilly Auto Parts
     - Tap Plastics
     - Industrial Plastics
   - Select: "O Reilly Auto Parts"

4. **Move item:**
   - Click "Move to Selected Vendor"
   - System creates/finds bundle for O Reilly
   - ACRYLITE moved to new bundle

**Result:**
```
Bundle A (S & F Supplies)          Bundle B (O Reilly Auto Parts)
- DURA-CAST IM-7328 (2 pcs)        - ACRYLITE Non-glare P99 (5 pcs)
Status: Active (needs re-review)   Status: Active (needs review)
```

**Continue:**
1. Review Bundle A (now only DURA-CAST)
2. Review Bundle B (now has ACRYLITE)
3. Mark both as Reviewed
4. Approve both
5. Place separate POs with each vendor

**Why This Matters:** Optimizes vendor selection for best price/availability

---

### Scenario 4: Bundle Changes After Review (Auto-Revert)

**Situation:** You reviewed Bundle A. Then you move an item TO Bundle A.

**What Happens:**
```
BEFORE:
Bundle A: Status = Reviewed
Items: Item X, Item Y

YOU MOVE Item Z to Bundle A

AFTER:
Bundle A: Status = Active (auto-reverted!)
Items: Item X, Item Y, Item Z
```

**Why:** Bundle changed, so you must review it again

**Your Actions:**
1. See Bundle A status changed to Active
2. See message: "Bundle reverted to Active for re-review"
3. Review Bundle A again (now with Item Z)
4. Click "✅ Mark as Reviewed"
5. Confirm checklist
6. Bundle → Reviewed

**Why This Matters:** Ensures you verify all changes before approval

---

### Scenario 5: Trying to Approve Before All Reviewed

**Situation:** You try to approve bundles, but some are still Active.

**What You See:**
```
📊 Review Progress: 6/10 bundles reviewed • 4 remaining

Bundle A: Reviewed ✅
Bundle B: Reviewed ✅
Bundle C: Active ⚠️ (not reviewed yet)
Bundle D: Reviewed ✅
```

**What Happens:**
- No checkboxes appear
- No "Approve Selected" button
- Message: "📊 Review Progress: 6/10 bundles reviewed • 4 remaining"

**Your Actions:**
1. Review remaining Active bundles (Bundle C)
2. Mark them as Reviewed
3. When ALL are Reviewed:
   - Message changes: "✅ All bundles reviewed! Select bundles below to approve."
   - Checkboxes appear
   - "Approve Selected" button enabled

**Why This Matters:** Quality control - ensures all bundles verified before ordering

---

### Scenario 6: Multiple Projects for Same User

**Situation:** Production Manager requested ACRYLITE for two different projects.

**What You See in HTML Table:**
```
┌──────────────────────┬────────────────┬──────────────┬──────────┐
│ Item                 │ User           │ Project      │ Quantity │
├──────────────────────┼────────────────┼──────────────┼──────────┤
│ ACRYLITE Non-glare   │ 👤 Prod Mgr    │ 📋 25-1559   │    1 pc  │
│ 48 x 96 x 0.125      │                │ 📋 23-1672   │    2 pcs │
│ Total: 3 pcs         │                │              │          │
└──────────────────────┴────────────────┴──────────────┴──────────┘
```

**What This Means:**
- Same user (Production Manager)
- Same item (ACRYLITE)
- Different projects (25-1559 and 23-1672)
- Total: 3 pcs (1 + 2)

**Your Actions:**
1. Review per-project breakdown
2. Verify quantities make sense
3. No duplicate warning (different projects)
4. Continue normal flow

**Why This Matters:** Clear tracking of which pieces go to which project

---

### Scenario 7: Vendor Quote Too High (Need Alternative)

**Situation:** Vendor quote exceeds budget.

**Your Actions:**
1. **Before approving:**
   - Bundle status: Reviewed
   - You can still make changes

2. **Check alternative vendors:**
   - Look at "Other Vendor Options" dropdown (for single-item bundles)
   - Or click "Report Issue" → "Alternative Vendor"

3. **Move items to cheaper vendor:**
   - Select alternative vendor
   - Move items
   - Bundle auto-reverts to Active

4. **Review new bundle:**
   - Mark as Reviewed
   - Get new quote
   - If acceptable, approve

**Why This Matters:** Cost optimization

---

### Scenario 8: Urgent Request (Need to Expedite)

**Situation:** User needs items urgently, can't wait for cron job.

**Your Actions (Master Role Only):**
1. Go to "🤖 Manual Bundling" tab
2. Select pending requests
3. Click "Create Bundle Now"
4. System creates bundle immediately
5. Review and approve as normal

**Note:** Only Master role has access to Manual Bundling

---

### Scenario 9: Item Out of Stock (Vendor Can't Fulfill)

**Situation:** After placing PO, vendor says item out of stock.

**Your Actions:**
1. **If bundle is Ordered:**
   - Cannot move items (locked)
   - Options:
     - Wait for restock
     - Cancel PO and revert bundle to Approved
     - Contact admin for help

2. **Best Practice:**
   - Confirm availability BEFORE placing PO
   - Ask vendor: "Do you have these items in stock?"

---

### Scenario 10: Partial Delivery

**Situation:** Vendor ships only some items, rest on backorder.

**Your Actions:**
1. **Receive partial shipment**
2. **Options:**
   - Wait for complete shipment, then mark Completed
   - Mark Completed with note about backorder
   - Split bundle (contact admin)

**Best Practice:** Wait for complete shipment before marking Completed

---

## Troubleshooting Guide

### Issue 1: Can't See "Approve Selected" Button

**Problem:** Button not appearing even though bundles are Reviewed.

**Possible Causes:**
1. Not ALL bundles are Reviewed
2. Some bundles still Active
3. Page needs refresh

**Solution:**
1. Check review progress indicator
2. Look for any Active bundles
3. Review remaining bundles
4. Refresh page (F5)
5. If still not working, contact admin

---

### Issue 2: Duplicate Warning Won't Go Away

**Problem:** Marked duplicates as reviewed, but warning still shows.

**Possible Causes:**
1. Didn't click "Mark Duplicates as Reviewed" button
2. Page not refreshed
3. Database update failed

**Solution:**
1. Scroll to duplicate section
2. Click "✅ Mark Duplicates as Reviewed"
3. Wait for success message
4. Refresh page
5. If persists, contact admin

---

### Issue 3: Can't Move Item to Different Vendor

**Problem:** "Move to Selected Vendor" button disabled.

**Possible Causes:**
1. Bundle is Approved (locked)
2. Bundle is Ordered (locked)
3. No alternative vendor selected

**Solution:**
1. Check bundle status
2. If Approved/Ordered: Cannot move (locked)
3. If Active/Reviewed: Select vendor from dropdown first
4. Then click Move button

---

### Issue 4: Bundle Auto-Reverted to Active

**Problem:** Bundle was Reviewed, now shows Active again.

**Reason:** Someone moved an item TO this bundle.

**Solution:**
1. This is normal behavior (safety feature)
2. Review bundle again (check new items)
3. Mark as Reviewed
4. Continue normal flow

**Why:** Ensures you verify changes before approval

---

### Issue 5: HTML Table Not Showing Per-Project Breakdown

**Problem:** Table shows total only, not per-project quantities.

**Possible Causes:**
1. User didn't enter project numbers
2. All items for same project
3. Display issue

**Solution:**
1. Check if project numbers exist
2. If missing, contact user
3. If exists but not showing, refresh page
4. If persists, contact admin

---

### Issue 6: Cron Job Didn't Run

**Problem:** Pending requests not bundled after 3-4 days.

**Possible Causes:**
1. Cron job failed
2. Schedule changed
3. System maintenance

**Solution:**
1. Check with admin
2. Master role can use Manual Bundling
3. Monitor cron job logs

---

### Issue 7: Can't Enter PO Number

**Problem:** PO number field disabled.

**Possible Causes:**
1. Bundle not Approved yet
2. Already entered PO (Ordered status)

**Solution:**
1. Check bundle status
2. Must be Approved to enter PO
3. If Ordered, PO already recorded

---

### Issue 8: Completed Bundle Shows Wrong Items

**Problem:** Bundle shows items that weren't in original bundle.

**Possible Causes:**
1. Items were moved after review
2. Display cache issue

**Solution:**
1. Check bundle history
2. Refresh page
3. Contact admin if discrepancy

---

## Best Practices

### ✅ DO:

**Review Process:**
- ✅ Review ALL bundles before approving ANY
- ✅ Check vendor contact info carefully
- ✅ Verify all items and quantities in HTML table
- ✅ Always review duplicate warnings
- ✅ Confirm vendor can supply items before approving

**Ordering:**
- ✅ Get quotes from vendors before placing PO
- ✅ Confirm availability before ordering
- ✅ Record PO numbers accurately
- ✅ Track delivery timelines

**Completion:**
- ✅ Verify all items received before marking Completed
- ✅ Check packing slip matches order
- ✅ Enter packing slip code accurately
- ✅ Notify users when items ready

**Communication:**
- ✅ Contact users about duplicates
- ✅ Inform users of delays
- ✅ Update users on delivery status

---

### ❌ DON'T:

**Review Process:**
- ❌ Don't approve bundles without reviewing
- ❌ Don't ignore duplicate warnings
- ❌ Don't skip checklist items
- ❌ Don't approve if unsure about vendor

**Ordering:**
- ❌ Don't place PO without quote
- ❌ Don't order without confirming availability
- ❌ Don't forget to record PO details
- ❌ Don't approve bundles you can't fulfill

**Completion:**
- ❌ Don't mark Completed before items arrive
- ❌ Don't mark Completed with missing items
- ❌ Don't forget packing slip code

**Changes:**
- ❌ Don't move items from Approved bundles (locked)
- ❌ Don't change Ordered bundles (locked)
- ❌ Don't ignore auto-revert warnings

---

### Quick Tips:

**Efficiency:**
- Use status filter to focus on specific stages
- Review bundles in batches
- Use "Select All" for bulk approval
- Keep vendor contacts handy

**Quality:**
- Always verify duplicate warnings
- Double-check project numbers
- Confirm quantities before ordering
- Review HTML table carefully

**Communication:**
- Keep users informed
- Document issues in notes
- Contact vendors proactively
- Escalate problems quickly

---

## 8) Recent Updates (October 2025)

**What's New:**
- ✅ **Smart Recommendations tab removed** - Bundles are now created automatically by cron job (twice a week)
- ✅ **HTML table display** - Bundle items now shown in professional table format with clear columns
- ✅ **Per-project quantity breakdown** - See exactly how many pieces for each project
- ✅ **Improved duplicate detection** - Only shows duplicates for items actually in the bundle
- ✅ **BoxHero items hidden** - Users can only request Raw Materials currently

**Automation:**
- Twice a week, the system automatically bundles requests and emails vendors for quotes
- You are CC'd on all vendor emails for follow-ups
- You still manage the review/approval/ordering workflow
- You still mark bundles as **Completed** when goods arrive

---

## Quick Reference Guide

### Status Icons & Meanings

| Icon | Status | Your Action | Can Change? |
|------|--------|-------------|-------------|
| 🟡 | **Active** | Review bundle | ✅ Yes |
| 🟢 | **Reviewed** | Ready to approve | ✅ Yes (can revert) |
| 🔵 | **Approved** | Place order | ❌ Locked |
| 📦 | **Ordered** | Wait for delivery | ❌ Locked |
| 🎉 | **Completed** | Done! | ❌ Final |

---

### Key Actions by Status

**Active Bundle:**
- ✅ Review items
- ✅ Check duplicates
- ✅ Move items
- ✅ Mark as Reviewed

**Reviewed Bundle:**
- ✅ Approve (when all reviewed)
- ✅ Revert to Active
- ✅ Still can move items

**Approved Bundle:**
- ✅ Place order
- ❌ Cannot move items (locked)
- ❌ Cannot change status back

**Ordered Bundle:**
- ✅ Mark as Completed
- ❌ Cannot move items (locked)

**Completed Bundle:**
- ✅ View only
- ❌ No changes allowed

---

### Common Tasks Cheat Sheet

**Review a Bundle:**
1. Open Active Bundles tab
2. Find Active bundle
3. Click "✅ Mark as Reviewed"
4. Check all 4 items in checklist
5. Click "Confirm & Mark as Reviewed"

**Approve Bundles:**
1. Wait until ALL bundles Reviewed
2. Select bundles (or "Select All")
3. Click "🎯 Approve Selected (N)"

**Handle Duplicate:**
1. See warning in bundle
2. Review user quantities
3. Adjust if needed (or keep both)
4. Click "✅ Mark Duplicates as Reviewed"

**Move Item to Different Vendor:**
1. Click "⚠️ Report Issue" on item
2. Select "Alternative Vendor"
3. Choose vendor from dropdown
4. Click "Move to Selected Vendor"

**Place Order:**
1. Bundle must be Approved
2. Click "📦 Order Placed"
3. Enter PO number
4. Enter PO date
5. Click "Record Order"

**Mark Completed:**
1. Bundle must be Ordered
2. Items must be received
3. Click "🏁 Mark as Completed"
4. Enter packing slip code
5. Click "Mark as Completed"

---

### Keyboard Shortcuts & Tips

**Navigation:**
- F5 - Refresh page
- Ctrl+F - Find on page
- Expand/collapse bundles with ▼/▶

**Efficiency Tips:**
- Use status filter dropdown
- Review bundles in batches
- Keep vendor contacts in separate tab
- Use "Select All" for bulk approval

---

### When to Contact Admin

**Contact Admin If:**
- ❌ Cron job didn't run (>4 days)
- ❌ Can't move items (should be able to)
- ❌ Duplicate warning won't clear
- ❌ Database connection errors
- ❌ Need to revert Approved bundle
- ❌ Need to split bundle
- ❌ System behaving unexpectedly

---

### Important Rules to Remember

1. **Must review ALL before approving ANY**
2. **Approved = Locked** (no changes)
3. **Moving item TO Reviewed bundle = Auto-revert to Active**
4. **Duplicates must be reviewed before bundle review**
5. **Always verify vendor availability before approving**
6. **Record PO details immediately after placing order**
7. **Don't mark Completed until ALL items received**

---

### Contact Information

**For Technical Issues:**
- Contact: System Admin
- Email: [admin@company.com]

**For User Questions:**
- Direct users to User Manual
- Or contact users directly

**For Vendor Issues:**
- Contact vendor directly (info in bundle)
- Escalate to purchasing manager if needed

---

If you need access or role changes, contact your admin.

---

**End of Complete Operator Manual**

**Version:** 2.0 | **Last Updated:** October 14, 2025
