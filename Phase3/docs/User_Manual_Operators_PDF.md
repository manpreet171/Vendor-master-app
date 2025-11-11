# Phase 3 Operator Dashboard – Complete User Manual
## For Operators

**Version:** 3.0  
**Last Updated:** November 7, 2025

---

This comprehensive guide explains how to use the Operator Dashboard to review requests, manage vendor orders, handle all possible scenarios, and close out completed bundles.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Complete Data Flow Journey](#2-complete-data-flow-journey)
3. [Operator Tabs Overview](#3-operator-tabs-overview)
4. [User Requests Tab](#4-user-requests-tab)
5. [Active Bundles Tab - Complete Guide](#5-active-bundles-tab---complete-guide)
6. [Bundle Review Process](#6-bundle-review-process)
7. [Order Placement Process](#7-order-placement-process)
8. [Bundle Completion Process](#8-bundle-completion-process)
9. [All Possible Scenarios](#9-all-possible-scenarios)
10. [Troubleshooting Guide](#10-troubleshooting-guide)
11. [Best Practices](#11-best-practices)
12. [Quick Reference](#12-quick-reference)

---

## 1) Getting Started

### Sign In as Operator

- Log in with your operator/admin account
- You'll see your name and role in the left sidebar
- The left sidebar also shows current database connection status
- Use "🚪 Logout" in the sidebar to exit

### Your Role

You are the **bridge between user requests and vendor fulfillment**. Your responsibilities include:

- ✅ Reviewing bundles created by the system
- ✅ Verifying vendor information and item details
- ✅ Checking for duplicates and errors
- ✅ Sending bundles to Operation Team for approval
- ✅ Placing orders with vendors after approval
- ✅ Tracking deliveries and marking bundles complete

---

## 2) Complete Data Flow Journey

### End-to-End Process Overview

The system follows this flow:

```
USER → SYSTEM (Cron) → YOU (Operator) → OPERATION TEAM → VENDOR → COMPLETION
```

**Breakdown:**

1. **USER** - Submits material requests through the app
2. **SYSTEM** - Automatically groups requests into vendor bundles (2x/week)
3. **YOU (Operator)** - Review bundles and mark as reviewed
4. **OPERATION TEAM** - Final approval before ordering
5. **YOU (Operator)** - Place orders with vendors
6. **VENDOR** - Ships items
7. **YOU (Operator)** - Mark bundles complete when items arrive

---

### Detailed Flow with Your Actions

#### **Stage 1: User Submits Request**

**What Happens:**
- User adds items to cart
- Submits request (e.g., REQ-20251014-001)
- Status: 🟡 **Pending**
- User receives confirmation email

**Your Action:**
- ℹ️ None (just awareness)
- Requests appear in "User Requests" tab

**What You See:**
- Request number
- User name
- Items requested
- Project numbers
- Date needed (if specified)
- User notes (if provided)

---

#### **Stage 2: System Creates Bundles (Automatic)**

**What Happens:**
- Cron job runs **twice a week** (Tuesday & Thursday at 2 AM)
- Scans all Pending requests
- Groups items by recommended vendor
- Creates bundles (e.g., RM-2025-11-05-001)
- Merges into existing Active/Reviewed bundles if vendor already has one
- Status: 🟡 **Active** (needs your review)
- User requests change to "In Progress"
- Operator receives email notification

**Your Action:**
- ℹ️ None (automatic process)

**What You See:**
- New bundles appear in "Active Bundles" tab
- Each bundle shows:
  - Bundle ID
  - Vendor name and contact info
  - Total items and quantities
  - User breakdown
  - Date needed (if specified)
  - Merge badge (🔄 if bundle was updated)

**Email Notification:**
```
Subject: Smart Bundling Complete: 3 new bundles, 2 updated
- New Bundles: 3
- Updated Bundles: 2
- Total Items: 47
- Coverage: 100%
```

---

#### **Stage 3: YOU Review Bundles**

**What Happens:**
- You open Active Bundles tab
- See all Active bundles waiting for review
- Review each bundle carefully

**Your Actions:**

**Step 1: Open Bundle**
- Click on bundle expander
- Review all information

**Step 2: Check Vendor Information**
- ✅ Vendor name correct?
- ✅ Email address valid?
- ✅ Phone number available?
- ✅ Alternative vendors available? (if needed)

**Step 3: Review Items Table**
- ✅ All items listed correctly?
- ✅ Quantities accurate?
- ✅ User breakdown clear?
- ✅ Date needed noted? (prioritize urgent items)
- ✅ Projects identified?

**Step 4: Check for Warnings**
- ⚠️ Duplicate warnings? (same item, same project from different users)
- ⚠️ Merge badge? (🔄 bundle was updated - check merge reason)
- ⚠️ Rejection warning? (previously rejected - check reason)

**Step 5: Read User Notes**
- Check if users provided special instructions
- Note any urgency or priority requests

**Step 6: Verify Vendor Selection**
- Check if recommended vendor is best choice
- Review alternative vendors if needed
- Consider pricing, delivery time, quality

**Step 7: Mark as Reviewed**
- Click **"✅ Mark as Reviewed"** button
- Confirm checklist (4 items):
  1. ✅ Verified vendor contact information
  2. ✅ Reviewed all items and quantities
  3. ✅ Checked for duplicate warnings
  4. ✅ Ready to send to Operation Team

**Step 8: Bundle Sent to Operation Team**
- Bundle status → 🟢 **Reviewed**
- Operation Team receives notification
- You cannot edit bundle anymore (locked)

**Important Notes:**
- ⚠️ Must review ALL bundles before Operation Team can approve
- ⚠️ Once marked Reviewed, you cannot undo (contact admin if needed)
- ⚠️ Check merge badge - merged bundles need extra attention

---

#### **Stage 4: OPERATION TEAM Approves**

**What Happens:**
- Operation Team reviews all Reviewed bundles
- They check final details and budget
- They can **Approve** or **Reject**

**If APPROVED:**
- Bundle status → 🟢 **Approved**
- You receive notification
- Bundle ready for ordering

**If REJECTED:**
- Bundle status → 🔴 **Active** (back to you)
- Rejection reason displayed in bundle
- You see orange warning box with reason
- Bundle history shows rejection details

**Your Actions:**

**If Approved:**
- ℹ️ None - proceed to Stage 5 (place order)

**If Rejected:**
1. Read rejection reason carefully
2. Fix the issue (contact vendor, verify items, etc.)
3. Make necessary changes
4. Mark as Reviewed again
5. Operation Team reviews again

**Common Rejection Reasons:**
- Budget exceeded
- Wrong vendor selected
- Missing information
- Duplicate items not resolved
- Pricing too high

---

#### **Stage 5: YOU Place Orders**

**What Happens:**
- Bundles are Approved by Operation Team
- You can now place orders with vendors
- Bundles are LOCKED (no changes allowed)

**Your Actions:**

**Step 1: Contact Vendor**
- Use email/phone from bundle
- Request quote for items
- Provide item details and quantities

**Step 2: Negotiate (if needed)**
- Discuss pricing
- Confirm delivery timeline
- Clarify specifications

**Step 3: Place Purchase Order**
- Create PO in your system
- Send PO to vendor
- Get vendor confirmation

**Step 4: Record Order in System**
- Click **"📦 Mark as Ordered"** in bundle
- Enter PO number (e.g., PO-2025-1014-A)
- Enter PO date
- Enter expected delivery date (optional)
- Click Save

**Step 5: System Updates**
- Bundle status → 📦 **Ordered**
- All linked user requests → **Ordered**
- Users receive email notification
- Bundle history updated

**Email to Users:**
```
Subject: Order Placed - REQ-2025-001
Your items have been ordered from the vendor.
Status: Ordered
PO Number: PO-2025-1014-A
Expected Delivery: November 15, 2025
```

**Important Notes:**
- ⚠️ Only Approved bundles can be ordered
- ⚠️ PO number is required
- ⚠️ Cannot undo order placement (contact admin if needed)
- ⚠️ Expected delivery date helps users plan

---

#### **Stage 6: Vendor Ships Items**

**What Happens:**
- Vendor processes order
- Ships items to warehouse
- Provides tracking information
- Items arrive at receiving

**Your Actions:**
- Monitor delivery timeline
- Follow up with vendor if delayed
- Check tracking status
- Coordinate with receiving team

**What You See:**
- Bundle status: 📦 **Ordered**
- PO number displayed
- Expected delivery date (if entered)
- Days since order placed

**Tips:**
- Set reminders for expected delivery dates
- Follow up proactively if items delayed
- Keep users informed of delays

---

#### **Stage 7: YOU Mark Completed**

**What Happens:**
- Items arrive at warehouse
- Receiving team verifies shipment
- All items accounted for

**Your Actions:**

**Step 1: Verify Receipt**
- Confirm all items received
- Check quantities match PO
- Verify quality and condition

**Step 2: Check Packing Slip**
- Get packing slip code from receiving
- Verify against PO

**Step 3: Mark Complete in System**
- Click **"🏁 Mark as Completed"** in bundle
- Enter packing slip code (e.g., PS-2025-1014-A)
- Enter actual delivery date
- Click Save

**Step 4: System Updates**
- Bundle status → 🎉 **Completed**
- All linked user requests → **Completed**
- Users receive final email notification
- Bundle archived (visible in history)

**Email to Users:**
```
Subject: Order Completed - REQ-2025-001
Your items have been received and are available.
Status: Completed
You can now request these items again if needed.
```

**Important Notes:**
- ⚠️ Only Ordered bundles can be completed
- ⚠️ Packing slip code is required
- ⚠️ Cannot undo completion (contact admin if needed)
- ⚠️ Users can now reorder same items

---

### Timeline Summary

**Typical Timeline:**

| Day | Stage | Status | Your Action |
|-----|-------|--------|-------------|
| Day 0 | User submits request | 🟡 Pending | None |
| Day 1-3 | Wait for cron job | 🟡 Pending | None |
| Day 3 | Cron creates bundle | 🟡 Active | Review bundle |
| Day 3 | You review | 🟢 Reviewed | Wait for Operation |
| Day 3 | Operation approves | 🟢 Approved | Place order |
| Day 3-4 | You place order | 📦 Ordered | Monitor delivery |
| Day 4-7 | Vendor ships | 📦 Ordered | Track shipment |
| Day 7 | Items arrive | 📦 Ordered | Mark complete |
| Day 7 | You mark complete | 🎉 Completed | Done! |

**Total Time:** 7 days average (can be faster for urgent items)

---

## 3) Operator Tabs Overview

At the top of the Operator Dashboard you'll see these tabs:

### **Standard Operator Tabs:**

| Tab | Icon | Purpose | What You Do |
|-----|------|---------|-------------|
| **User Requests** | 📋 | View all user requests | Monitor pending requests |
| **Active Bundles** | 📦 | Manage vendor bundles | Review, order, complete |
| **Analytics** | 📊 | View statistics | Monitor performance |

### **Master Role Additional Tabs:**

| Tab | Icon | Purpose | What You Do |
|-----|------|---------|-------------|
| **Manual Bundling** | 🤖 | Emergency bundling | Run bundling manually |
| **System Reset** | 🧹 | Database cleanup | Clear test data |
| **User Management** | 👤 | Manage users | Add/edit/deactivate users |

**Note:** Master role has full admin privileges. Use carefully!

---

## 4) User Requests Tab

### Purpose

View all user requests in one place. See what users are requesting, track status, and understand demand patterns.

### What You See

**Request Overview:**

| Column | Description |
|--------|-------------|
| **Request #** | Unique request ID (e.g., REQ-2025-001) |
| **User** | Who submitted the request |
| **Date** | When request was submitted |
| **Items** | Number of items in request |
| **Status** | Current status (Pending, In Progress, Ordered, Completed) |
| **Projects** | Project numbers involved |

**Status Breakdown:**

- **🟡 Pending** - Waiting for bundling (not processed yet)
- **🔵 In Progress** - In a bundle, being processed
- **📦 Ordered** - Order placed with vendor
- **🎉 Completed** - Items received

### How to Use

**View Request Details:**
1. Click on any request to expand
2. See all items in request
3. View project numbers
4. Check date needed (if specified)
5. Read user notes (if provided)

**Filter Requests:**
- Filter by status
- Filter by user
- Filter by date range
- Search by request number

**Export Data:**
- Click "Export to CSV" button
- Download request data for analysis
- Use for reporting and planning

### Key Information to Note

**Date Needed:**
- Shows when user needs items
- Helps prioritize urgent requests
- Visible in bundle review

**User Notes:**
- Special instructions from user
- Urgency indicators
- Project context

**Project Numbers:**
- Track which projects need materials
- Budget allocation
- Historical reference

---

*End of Chunk 1*

---

**Next Chunks Will Cover:**
- Chunk 2: Active Bundles Tab - Detailed Guide
- Chunk 3: Bundle Review Process - Step by Step
- Chunk 4: All Possible Scenarios
- Chunk 5: Troubleshooting & Best Practices

---

## 5) Active Bundles Tab - Complete Guide

### Purpose

This is your **main workspace**. Here you review bundles, approve them, place orders, and mark them complete.

### Bundle Status Workflow

Bundles move through these statuses in order:

| Status | Icon | Description | Your Action |
|--------|------|-------------|-------------|
| **Active** | 🟡 | New bundle, needs review | Review and mark as reviewed |
| **Reviewed** | 🟢 | You've reviewed, sent to Operation Team | Wait for Operation approval |
| **Approved** | 🔵 | Operation Team approved | Place order with vendor |
| **Ordered** | 📦 | PO placed with vendor | Monitor delivery |
| **Completed** | 🎉 | Items received | Archive (done!) |

**Important:** You cannot skip statuses. Each bundle must go through all stages.

---

### Review Progress Tracking

At the top of Active Bundles tab, you'll see a progress indicator:

**While Reviewing:**
```
📊 Review Progress: 6/10 bundles reviewed • 4 remaining
```

**When Complete:**
```
✅ All bundles reviewed! Ready for Operation Team approval.
```

**Why This Matters:**
- Shows how many bundles need your attention
- Helps you track your workload
- Ensures nothing is missed

---

### Status Filter

Use the dropdown to filter bundles by status:

| Filter Option | Shows |
|---------------|-------|
| 🟡 **Active (N)** | Bundles needing your review |
| 🟢 **Reviewed (N)** | Bundles waiting for Operation approval |
| 🔵 **Approved (N)** | Bundles ready for ordering |
| 📦 **Ordered (N)** | Bundles waiting for delivery |
| 🎉 **Completed (N)** | Finished bundles (archived) |
| 📋 **All Bundles (N)** | Show everything |

**Tip:** Start with "Active" filter to focus on bundles needing review.

---

### Bundle Information Panel

Each bundle displays comprehensive information:

#### **1. Bundle Header**

**What You See:**
- Bundle ID (e.g., RM-2025-11-05-001)
- Vendor name
- Status badge
- Merge badge (🔄 if bundle was updated)
- Created date

**Example:**
```
Bundle: RM-2025-11-05-001
Vendor: ABC Plastics Inc.
Status: 🟡 Active
🔄 Updated 1x (merged with new requests)
Created: November 5, 2025
```

---

#### **2. Vendor Contact Information**

**What You See:**

| Field | Description |
|-------|-------------|
| **Vendor Name** | Full business name |
| **Email** | Primary contact email |
| **Phone** | Contact phone number |

**Example:**
```
Vendor: ABC Plastics Inc.
📧 Email: orders@abcplastics.com
📞 Phone: (555) 123-4567
```

**Your Action:**
- ✅ Verify email is valid
- ✅ Verify phone number is current
- ✅ Check if you have existing relationship with vendor

---

#### **3. Items Table (Professional View)**

**What You See:**

A detailed table showing all items in the bundle:

| Column | Description |
|--------|-------------|
| **Item** | Item name, dimensions, total quantity |
| **User** | Which user requested it |
| **Project** | Project number for tracking |
| **Date Needed** | When user needs items (if specified) |
| **Quantity** | Per-project quantity breakdown |

**Example Table:**

| Item | User | Project | Date Needed | Quantity |
|------|------|---------|-------------|----------|
| ACRYLITE Non-glare P99<br>48 x 96 x 0.125<br>**Total: 5 pcs** | Production Mgr<br>Production Mgr<br>Production Mgr2 | 📋 25-1559<br>📋 23-1672<br>📋 25-1559 | 2025-11-15<br>2025-11-20<br>2025-11-18 | 1 pc<br>2 pcs<br>2 pcs |
| DURA-CAST IM-7328<br>3/16" 4x8 WHITE PM*<br>**Total: 3 pcs** | Production Mgr | 📋 23-1672 | 2025-11-20 | 3 pcs |

**Key Features:**
- ✅ See exactly which user needs which item
- ✅ Track project numbers for each request
- ✅ Identify urgent items (date needed)
- ✅ Understand quantity breakdown per project

---

#### **4. Date Needed Column (Priority Indicator)**

**What It Shows:**
- When users need items delivered
- Helps you prioritize urgent orders
- Visible in items table

**How to Use:**
1. Look for earliest dates
2. Prioritize those bundles
3. Contact vendor about rush delivery if needed
4. Communicate timeline to users

**Example:**
```
Date Needed: 2025-11-15 (3 days from now!)
→ This is urgent - prioritize this bundle
→ Contact vendor for expedited shipping
```

**Tips:**
- ⚠️ Red flag dates within 5 days
- ⚠️ Yellow flag dates within 10 days
- ✅ Green flag dates beyond 10 days

---

#### **5. User Notes Section**

**What You See:**
- Special instructions from users
- Urgency indicators
- Project context

**Example:**
```
📝 User Notes:
"Urgent - needed for client presentation on Nov 15.
Please prioritize the acrylic sheets."
```

**Your Action:**
- ✅ Read all notes carefully
- ✅ Note any special requirements
- ✅ Communicate with vendor if needed
- ✅ Follow up with user if clarification needed

---

#### **6. Duplicate Detection (Critical)**

**What It Shows:**
- Alerts when multiple users requested same item for same project
- Only shows duplicates within THIS bundle
- Requires your review before bundle can be marked reviewed

**Example Warning:**
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

**Step 1: Investigate**
- Contact both users
- Ask: "Do you both need this item for Project 25-1559?"
- Verify quantities

**Step 2: Decide**

| Scenario | Action |
|----------|--------|
| **Both need it** | Keep both (5 pcs total) |
| **Only one needs it** | Set other to 0, click Update |
| **Need different amounts** | Adjust quantities, click Update |
| **Mistake/duplicate** | Remove one user (set to 0) |

**Step 3: Mark as Reviewed**
- Click **"✅ Mark Duplicates as Reviewed"**
- Warning disappears
- Green checkmark appears: "✅ Duplicates Reviewed"

**Important:**
- ⚠️ Cannot mark bundle as reviewed until duplicates are reviewed
- ⚠️ Duplicates are common - not always errors
- ⚠️ Always verify with users before removing

---

#### **7. Merge Badge (🔄 Updated)**

**What It Shows:**
- Bundle was updated with new requests
- Shows how many times merged
- Displays merge reason

**Example:**
```
🔄 Updated 1x

ℹ️ This bundle has been updated 1 time(s)
Last updated: November 6, 2025 at 10:30 PM

⚠️ Merge Reason:
New requests added: 2 items from 1 user(s)
- Added: ACRYLITE Clear (2 pcs) for Project 24-1702
```

**Why This Matters:**
- Bundle changed since creation
- New items added
- Need extra attention during review

**Your Actions:**
1. Read merge reason carefully
2. Review new items added
3. Check if vendor is still appropriate
4. Verify all quantities
5. Proceed with normal review

**Important:**
- ⚠️ Merged bundles need extra attention
- ⚠️ Check if new items fit with existing items
- ⚠️ Verify vendor can supply all items

---

#### **8. Rejection Warning (If Previously Rejected)**

**What It Shows:**
- Bundle was rejected by Operation Team
- Shows rejection reason
- Displays rejection date and who rejected

**Example:**
```
⚠️ REJECTION WARNING

This bundle was previously rejected by Operation Team.

Rejection Reason:
"Budget exceeded for this vendor. Please get quotes from alternative vendors."

Rejected by: Sarah Lee (Operation Team)
Rejected on: November 5, 2025 at 3:45 PM

Action Required: Address the issue above before marking as reviewed again.
```

**Your Actions:**

**Step 1: Read Rejection Reason**
- Understand what went wrong
- Note specific requirements

**Step 2: Fix the Issue**

| Rejection Reason | Your Action |
|------------------|-------------|
| Budget exceeded | Get better quotes, consider alternative vendors |
| Wrong vendor | Move items to correct vendor |
| Missing information | Add required details |
| Duplicate not resolved | Review duplicates again |
| Pricing too high | Negotiate with vendor |

**Step 3: Make Changes**
- Contact vendor for new quote
- Move items if needed
- Update information

**Step 4: Mark as Reviewed Again**
- Click **"✅ Mark as Reviewed"**
- Bundle goes back to Operation Team
- They review again

**Important:**
- ⚠️ Must fix issue before resubmitting
- ⚠️ Document what you changed
- ⚠️ Communicate with Operation Team

---

#### **9. Alternative Vendors (Single-Item Bundles)**

**What It Shows:**
- Other vendors who can supply the item
- Vendor names and contact info
- View-only (for reference)

**Example:**
```
🔄 Alternative Vendors Available:

This item can also be ordered from:
• XYZ Plastics Co. (contact@xyzplastics.com)
• Superior Materials Inc. (orders@superiormaterials.com)
```

**When to Use:**
- Current vendor too expensive
- Current vendor out of stock
- Need faster delivery
- Operation Team requests alternative

**Your Action:**
- Review alternative vendors
- Contact for quotes if needed
- Compare pricing and delivery times
- Move item to different vendor if better option

**How to Move Items:**
1. Click **"⚠️ Report Issue"** button
2. Select items to move
3. Choose new vendor
4. Click **"Move Items"**
5. Bundle updates automatically

---

#### **10. Bundle History**

**What It Shows:**
- Complete audit trail of all actions
- Who did what and when
- Status changes
- Approvals and rejections

**Example:**
```
📜 Bundle History:

✅ Completed - November 10, 2025 at 2:00 PM by John Operator
   Packing slip: PS-2025-1014-A

📦 Ordered - November 5, 2025 at 10:30 AM by John Operator
   PO Number: PO-2025-1014-A

🟢 Approved - November 5, 2025 at 9:15 AM by Sarah Lee (Operation)

🟢 Reviewed - November 5, 2025 at 8:45 AM by John Operator

🟡 Active - November 5, 2025 at 2:00 AM (Created by System)
```

**Why This Matters:**
- Track who made changes
- Understand bundle timeline
- Reference for audits
- Troubleshoot issues

---

### Bundle Actions by Status

#### **For Active Bundles (🟡)**

**Available Actions:**

| Action | Button | What It Does |
|--------|--------|--------------|
| **Mark as Reviewed** | ✅ Mark as Reviewed | Opens checklist, sends to Operation Team |
| **Report Issue** | ⚠️ Report Issue | Move items to different vendor |

**Mark as Reviewed Process:**

**Step 1: Click Button**
- Click **"✅ Mark as Reviewed"**
- Checklist modal appears

**Step 2: Review Checklist**

Confirm all 4 items:
- ☐ Verified vendor contact information (email, phone)
- ☐ Reviewed all items and quantities in table
- ☐ Checked for duplicate warnings (if any)
- ☐ Confirmed correct vendor selected

**Step 3: Confirm**
- Click **"Confirm & Mark as Reviewed"**
- Bundle status → 🟢 Reviewed
- Sent to Operation Team
- You cannot edit anymore

**Important:**
- ⚠️ Must check all 4 items
- ⚠️ Cannot undo (contact admin if needed)
- ⚠️ Duplicates must be reviewed first

---

#### **For Reviewed Bundles (🟢)**

**Status:** Waiting for Operation Team approval

**Available Actions:**

| Action | Button | What It Does |
|--------|--------|--------------|
| **Revert to Active** | ↩️ Revert | Move back to Active if you need to make changes |

**When to Revert:**
- Found an error after marking reviewed
- Need to change vendor
- Need to adjust quantities
- Operation Team asked for changes

**How to Revert:**
1. Click **"↩️ Revert"**
2. Confirm action
3. Bundle status → 🟡 Active
4. Make your changes
5. Mark as Reviewed again

**Important:**
- ⚠️ Only use if necessary
- ⚠️ Delays the process
- ⚠️ Document why you reverted

---

#### **For Approved Bundles (🔵)**

**Status:** Approved by Operation Team, ready for ordering

**Available Actions:**

| Action | Button | What It Does |
|--------|--------|--------------|
| **Mark as Ordered** | 📦 Order Placed | Record PO details after placing order |

**Order Placement Process:**

**Step 1: Contact Vendor**
- Use email/phone from bundle
- Request quote for all items
- Provide specifications and quantities

**Step 2: Negotiate**
- Discuss pricing
- Confirm delivery timeline
- Clarify any specifications
- Get written quote

**Step 3: Place Purchase Order**
- Create PO in your system
- Send PO to vendor
- Get vendor confirmation
- Save PO number

**Step 4: Record in System**
- Click **"📦 Order Placed"**
- Modal appears with fields:
  - PO Number (required)
  - PO Date (required)
  - Expected Delivery Date (optional)
- Fill in all fields
- Click **"Save"**

**Step 5: System Updates**
- Bundle status → 📦 Ordered
- All user requests → Ordered
- Users receive email notification
- Bundle history updated

**Important:**
- ⚠️ Only Approved bundles can be ordered
- ⚠️ PO number is required
- ⚠️ Cannot undo (contact admin if needed)
- ⚠️ Expected delivery helps users plan

---

#### **For Ordered Bundles (📦)**

**Status:** Order placed, waiting for delivery

**Available Actions:**

| Action | Button | What It Does |
|--------|--------|--------------|
| **Mark as Completed** | 🏁 Mark as Completed | Record delivery details when items arrive |

**Completion Process:**

**Step 1: Verify Receipt**
- Confirm all items received
- Check quantities match PO
- Verify quality and condition
- Check packing slip

**Step 2: Record in System**
- Click **"🏁 Mark as Completed"**
- Modal appears with fields:
  - Packing Slip Code (required)
  - Actual Delivery Date (required)
- Fill in all fields
- Click **"Save"**

**Step 3: System Updates**
- Bundle status → 🎉 Completed
- All user requests → Completed
- Users receive final email notification
- Bundle archived

**Important:**
- ⚠️ Only Ordered bundles can be completed
- ⚠️ Packing slip code is required
- ⚠️ Cannot undo (contact admin if needed)
- ⚠️ Users can now reorder same items

---

### Auto-Revert Safety Feature

**What It Does:**
If items are moved to a Reviewed bundle, it automatically reverts to Active status.

**Why:**
- Prevents approving bundles that have changed
- Ensures quality control
- Forces re-review of modified bundles

**Example:**
```
Bundle A: Status = Reviewed
You move Item X from Bundle B to Bundle A
→ Bundle A automatically reverts to Active
→ You must review Bundle A again
```

**Your Action:**
- Review the bundle again
- Verify new items fit
- Mark as Reviewed again

---

*End of Chunk 2*

---

---

## 9) All Possible Scenarios

### Scenario 1: Normal Flow (No Issues)

**Situation:** Bundle created with no duplicates, correct vendor, all items available.

**Timeline:** 7 days average

**Your Actions:**

| Step | Action | Result |
|------|--------|--------|
| 1 | Open Active Bundles tab | See bundle list |
| 2 | Find bundle: RM-2025-11-05-001 (ABC Plastics) | Bundle displayed |
| 3 | Review vendor contact info | ✅ Valid |
| 4 | Review items in table | ✅ All correct |
| 5 | Check for duplicate warnings | ✅ None |
| 6 | Check merge badge | ✅ None |
| 7 | Click "✅ Mark as Reviewed" | Checklist appears |
| 8 | Confirm all 4 checklist items | All checked |
| 9 | Click "Confirm & Mark as Reviewed" | Status → Reviewed |
| 10 | Wait for Operation Team approval | Status → Approved |
| 11 | Contact vendor for quote | Quote received |
| 12 | Place PO with vendor | PO confirmed |
| 13 | Click "📦 Order Placed" | Modal appears |
| 14 | Enter PO details (number, date) | Details saved |
| 15 | Click "Save" | Status → Ordered |
| 16 | Wait for delivery (3-4 days) | Items shipped |
| 17 | Items arrive at warehouse | Receiving notifies |
| 18 | Click "🏁 Mark as Completed" | Modal appears |
| 19 | Enter packing slip code | Details saved |
| 20 | Click "Save" | Status → Completed ✅ |

**Result:** Bundle completed successfully, users notified, items available.

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

**Step 1: Investigate**
- Contact Production Manager: "Do you need 3 pcs of ACRYLITE for 25-1559?"
- Contact Production Manager2: "Do you need 2 pcs of ACRYLITE for 25-1559?"

**Step 2: Get Responses**

| Response | Your Action |
|----------|-------------|
| **Both need it** (different phases) | Keep both (5 pcs total) |
| **Only one needs it** (mistake) | Set other to 0, click Update |
| **Need different amounts** | Adjust quantities, click Update |
| **Duplicate submission** | Remove one user (set to 0) |

**Step 3: Example Decision**
- Production Manager: "Yes, I need 3 pcs for Phase 1"
- Production Manager2: "Yes, I need 2 pcs for Phase 2"
- **Decision:** Keep both (5 pcs total)

**Step 4: Mark as Reviewed**
- Click **"✅ Mark Duplicates as Reviewed"**
- Warning disappears
- Green checkmark: "✅ Duplicates Reviewed - 1 item(s) were checked"

**Step 5: Continue Normal Flow**
- Click "✅ Mark as Reviewed" for bundle
- Confirm checklist
- Bundle → Reviewed

**Why This Matters:** Prevents over-ordering and waste. Ensures accurate quantities.

---

### Scenario 3: Wrong Vendor (Need to Move Item)

**Situation:** Bundle has Item A and Item B. Vendor doesn't carry Item A.

**What You See:**
```
Bundle: RM-2025-11-05-001
Vendor: S & F Supplies Inc.
Items:
- ACRYLITE Non-glare P99 (5 pcs)
- DURA-CAST IM-7328 (2 pcs)
```

**Your Actions:**

**Step 1: Discover Issue**
- Contact S & F Supplies for quote
- Vendor response: "We don't carry ACRYLITE"

**Step 2: Report Issue**
- Click **"⚠️ Report Issue"** on ACRYLITE item
- Select reason: "Alternative Vendor"

**Step 3: Choose New Vendor**
- Dropdown shows alternative vendors:
  - O Reilly Auto Parts
  - Tap Plastics
  - Industrial Plastics
- Select: **"O Reilly Auto Parts"**

**Step 4: Move Item**
- Click **"Move to Selected Vendor"**
- System creates/finds bundle for O Reilly
- ACRYLITE moved to new bundle

**Result:**

| Bundle A (S & F Supplies) | Bundle B (O Reilly Auto Parts) |
|---------------------------|--------------------------------|
| DURA-CAST IM-7328 (2 pcs) | ACRYLITE Non-glare P99 (5 pcs) |
| Status: Active (needs re-review) | Status: Active (needs review) |

**Step 5: Continue**
1. Review Bundle A (now only DURA-CAST)
2. Review Bundle B (now has ACRYLITE)
3. Mark both as Reviewed
4. Wait for Operation approval
5. Place separate POs with each vendor

**Why This Matters:** Optimizes vendor selection for best price/availability.

---

### Scenario 4: Bundle Changes After Review (Auto-Revert)

**Situation:** You reviewed Bundle A. Then you move an item TO Bundle A.

**What Happens:**

**BEFORE:**
```
Bundle A: Status = Reviewed
Items: Item X, Item Y
```

**YOU MOVE Item Z to Bundle A**

**AFTER:**
```
Bundle A: Status = Active (auto-reverted!)
Items: Item X, Item Y, Item Z
Message: "Bundle reverted to Active for re-review"
```

**Why:** Bundle changed, so you must review it again to ensure quality.

**Your Actions:**
1. See Bundle A status changed to Active
2. See message: "Bundle reverted to Active for re-review"
3. Review Bundle A again (now with Item Z)
4. Verify Item Z fits with existing items
5. Check vendor can supply all items
6. Click "✅ Mark as Reviewed"
7. Confirm checklist
8. Bundle → Reviewed

**Why This Matters:** Ensures you verify all changes before approval. Safety feature.

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
1. Review remaining Active bundles (Bundle C and others)
2. Mark them as Reviewed
3. When ALL are Reviewed:
   - Message changes: "✅ All bundles reviewed! Ready for Operation Team approval."
   - Checkboxes appear next to Reviewed bundles
   - You can now select bundles for Operation Team

**Why This Matters:** Quality control - ensures all bundles verified before sending to Operation Team.

---

### Scenario 6: Multiple Projects for Same User

**Situation:** Production Manager requested ACRYLITE for two different projects.

**What You See in Items Table:**

| Item | User | Project | Date Needed | Quantity |
|------|------|---------|-------------|----------|
| ACRYLITE Non-glare P99<br>48 x 96 x 0.125<br>**Total: 3 pcs** | Production Mgr<br>Production Mgr | 📋 25-1559<br>📋 23-1672 | 2025-11-15<br>2025-11-20 | 1 pc<br>2 pcs |

**What This Means:**
- Same user (Production Manager)
- Same item (ACRYLITE)
- **Different projects** (25-1559 and 23-1672)
- Total: 3 pcs (1 + 2)

**Your Actions:**
1. Review per-project breakdown
2. Verify quantities make sense
3. **No duplicate warning** (different projects = OK)
4. Continue normal flow

**Why This Matters:** Clear tracking of which pieces go to which project. This is NOT a duplicate.

---

### Scenario 7: Vendor Quote Too High (Need Alternative)

**Situation:** Vendor quote exceeds budget. Operation Team may reject.

**Your Actions:**

**Option 1: Before Approval (Proactive)**
1. Bundle status: Reviewed
2. Get quote from vendor
3. Quote too high
4. Click **"↩️ Revert"** to move back to Active
5. Click **"⚠️ Report Issue"** → "Alternative Vendor"
6. Select cheaper vendor
7. Move items
8. Review new bundle
9. Get new quote
10. If acceptable, mark as Reviewed

**Option 2: After Rejection (Reactive)**
1. Operation Team rejects bundle
2. Rejection reason: "Budget exceeded"
3. Bundle status → Active (with rejection warning)
4. Follow Option 1 steps above

**Why This Matters:** Cost optimization. Prevents delays from rejections.

---

### Scenario 8: Urgent Request (Need to Expedite)

**Situation:** User needs items urgently, can't wait for cron job (Tue/Thu).

**Your Actions (Master Role Only):**

**Step 1: Access Manual Bundling**
- Go to **"🤖 Manual Bundling"** tab
- Only available to Master role

**Step 2: Create Bundle Manually**
1. See list of pending requests
2. Select urgent requests
3. Click **"Create Bundle Now"**
4. System creates bundle immediately

**Step 3: Process Normally**
1. Bundle appears in Active Bundles tab
2. Review bundle
3. Mark as Reviewed
4. Wait for Operation approval
5. Place order
6. Expedite with vendor if needed

**Note:** Only Master role has access to Manual Bundling. Use sparingly.

---

### Scenario 9: Item Out of Stock (Vendor Can't Fulfill)

**Situation:** After placing PO, vendor says item out of stock.

**Your Actions:**

**If Bundle is Ordered:**
- Cannot move items (locked)
- **Options:**
  1. **Wait for restock** - Ask vendor for ETA
  2. **Cancel PO** - Contact admin to revert bundle to Approved
  3. **Find alternative** - Contact admin for help

**Best Practice:**
- **Confirm availability BEFORE placing PO**
- Ask vendor: "Do you have these items in stock?"
- Get written confirmation
- Avoid this scenario entirely

**Communication:**
- Inform users of delay
- Provide new timeline
- Keep users updated

---

### Scenario 10: Partial Delivery

**Situation:** Vendor ships only some items, rest on backorder.

**What Happens:**
- Receive 3 of 5 items
- 2 items on backorder (2-3 weeks)

**Your Actions:**

**Option 1: Wait for Complete Shipment (Recommended)**
1. Don't mark as Completed yet
2. Wait for remaining items
3. When all items arrive, mark Completed
4. Enter packing slip for complete shipment

**Option 2: Mark Completed with Note**
1. Mark bundle as Completed
2. Add note about backorder
3. Track backorder separately
4. Inform users

**Option 3: Split Bundle (Advanced)**
1. Contact admin for help
2. Split into two bundles
3. Complete first bundle
4. Keep second bundle Ordered

**Best Practice:** Wait for complete shipment before marking Completed.

---

### Scenario 11: Merge Badge - Bundle Updated

**Situation:** Bundle shows 🔄 Updated 1x badge.

**What You See:**
```
🔄 Updated 1x

ℹ️ This bundle has been updated 1 time(s)
Last updated: November 6, 2025 at 10:30 PM

⚠️ Merge Reason:
New requests added: 2 items from 1 user(s)
- Added: ACRYLITE Clear (2 pcs) for Project 24-1702
```

**Your Actions:**

**Step 1: Read Merge Reason**
- Understand what changed
- Note new items added

**Step 2: Review New Items**
- Check if new items fit with existing
- Verify vendor can supply all items
- Check quantities

**Step 3: Verify Vendor**
- Confirm vendor carries new items
- Check if pricing still reasonable

**Step 4: Proceed with Review**
- If everything OK, mark as Reviewed
- If issues, move items to different vendor

**Why This Matters:** Merged bundles need extra attention. Ensure vendor can handle all items.

---

### Scenario 12: Operation Team Rejection

**Situation:** Operation Team rejected your bundle.

**What You See:**
```
⚠️ REJECTION WARNING

This bundle was previously rejected by Operation Team.

Rejection Reason:
"Budget exceeded for this vendor. Please get quotes from alternative vendors."

Rejected by: Sarah Lee (Operation Team)
Rejected on: November 5, 2025 at 3:45 PM
```

**Your Actions:**

**Step 1: Understand Rejection**
- Read rejection reason carefully
- Note specific requirements

**Step 2: Fix the Issue**

| Rejection Reason | Your Action |
|------------------|-------------|
| Budget exceeded | Get better quotes, consider alternative vendors |
| Wrong vendor | Move items to correct vendor |
| Missing information | Add required details |
| Duplicate not resolved | Review duplicates again |
| Pricing too high | Negotiate with vendor |
| Vendor not approved | Use approved vendor list |

**Step 3: Make Changes**
- Contact vendor for new quote
- Move items if needed
- Update information
- Document changes

**Step 4: Resubmit**
- Click **"✅ Mark as Reviewed"**
- Bundle goes back to Operation Team
- They review again
- Hopefully approved this time!

**Communication:**
- Inform Operation Team of changes
- Explain what you fixed
- Provide supporting documentation

---

## 10) Troubleshooting Guide

### Issue 1: Can't See "Approve Selected" Button

**Problem:** Button not appearing even though bundles are Reviewed.

**Symptoms:**
- Bundles show Reviewed status
- No checkboxes visible
- No approve button

**Possible Causes:**
1. Not ALL bundles are Reviewed
2. Some bundles still Active
3. Page needs refresh
4. Browser cache issue

**Solution:**

**Step 1: Check Progress**
- Look at review progress indicator
- Should say: "✅ All bundles reviewed!"
- If not, some bundles still need review

**Step 2: Find Active Bundles**
- Use status filter: "Active"
- Review any remaining bundles
- Mark them as Reviewed

**Step 3: Refresh Page**
- Press F5 or Ctrl+R
- Clear browser cache if needed
- Log out and log back in

**Step 4: Contact Admin**
- If still not working after above steps
- Provide screenshot
- Mention which bundles are Reviewed

---

### Issue 2: Duplicate Warning Won't Go Away

**Problem:** Marked duplicates as reviewed, but warning still shows.

**Symptoms:**
- Clicked "Mark Duplicates as Reviewed"
- Warning still visible
- Can't mark bundle as reviewed

**Possible Causes:**
1. Didn't click the button (only adjusted quantities)
2. Page not refreshed
3. Database update failed
4. Multiple duplicate warnings (only marked one)

**Solution:**

**Step 1: Verify Button Click**
- Scroll to duplicate section
- Look for **"✅ Mark Duplicates as Reviewed"** button
- Click it (not just Update quantities)
- Wait for success message

**Step 2: Check for Multiple Duplicates**
- Scroll through entire bundle
- Look for other duplicate warnings
- Mark each one separately

**Step 3: Refresh Page**
- Press F5
- Check if warning cleared

**Step 4: Contact Admin**
- If persists after above steps
- Provide bundle ID
- Screenshot of warning

---

### Issue 3: Can't Move Item to Different Vendor

**Problem:** "Move to Selected Vendor" button disabled.

**Symptoms:**
- Button grayed out
- Can't click Move button
- No error message

**Possible Causes:**
1. Bundle is Approved (locked)
2. Bundle is Ordered (locked)
3. No alternative vendor selected
4. Item already being moved

**Solution:**

**Step 1: Check Bundle Status**

| Status | Can Move? | Solution |
|--------|-----------|----------|
| Active | ✅ Yes | Select vendor, then move |
| Reviewed | ✅ Yes | Select vendor, then move |
| Approved | ❌ No | Cannot move (locked) |
| Ordered | ❌ No | Cannot move (locked) |

**Step 2: Select Vendor First**
- Click dropdown
- Choose alternative vendor
- Then click Move button

**Step 3: If Locked**
- Contact admin to revert bundle
- Explain reason for move
- Admin can unlock if needed

---

### Issue 4: Bundle Auto-Reverted to Active

**Problem:** Bundle was Reviewed, now shows Active again.

**Symptoms:**
- Bundle status changed unexpectedly
- Was Reviewed, now Active
- Message about revert

**Reason:** Someone moved an item TO this bundle.

**Solution:**

**Step 1: Understand This is Normal**
- This is a safety feature
- Prevents approving changed bundles
- Ensures quality control

**Step 2: Review Bundle Again**
- Check what changed
- Look for new items
- Verify all items fit together

**Step 3: Mark as Reviewed Again**
- Click "✅ Mark as Reviewed"
- Confirm checklist
- Bundle → Reviewed

**Why:** Ensures you verify changes before approval. This is intentional behavior.

---

### Issue 5: HTML Table Not Showing Per-Project Breakdown

**Problem:** Table shows total only, not per-project quantities.

**Symptoms:**
- See total quantity
- Don't see project breakdown
- Missing project column

**Possible Causes:**
1. User didn't enter project numbers
2. All items for same project
3. Display issue
4. Browser compatibility

**Solution:**

**Step 1: Check Project Numbers**
- Expand request details
- Verify project numbers exist
- If missing, contact user

**Step 2: Refresh Page**
- Press F5
- Clear browser cache
- Try different browser

**Step 3: Check Data**
- If all items same project, no breakdown needed
- Breakdown only shows when multiple projects

**Step 4: Contact Admin**
- If projects exist but not showing
- Provide bundle ID
- Screenshot of table

---

### Issue 6: Cron Job Didn't Run

**Problem:** Pending requests not bundled after 3-4 days.

**Symptoms:**
- Requests stuck in Pending
- No new bundles created
- Past Tuesday/Thursday

**Possible Causes:**
1. Cron job failed
2. Schedule changed
3. System maintenance
4. Server issue

**Solution:**

**Step 1: Check with Admin**
- Report the issue
- Provide date of last successful run
- List pending request numbers

**Step 2: Manual Bundling (Master Role)**
- Go to "🤖 Manual Bundling" tab
- Select pending requests
- Click "Create Bundle Now"
- Process normally

**Step 3: Monitor Logs**
- Admin can check cron job logs
- Identify failure reason
- Fix underlying issue

---

### Issue 7: Can't Enter PO Number

**Problem:** PO number field disabled.

**Symptoms:**
- Field grayed out
- Can't type in field
- No error message

**Possible Causes:**
1. Bundle not Approved yet
2. Already entered PO (Ordered status)
3. Permission issue

**Solution:**

**Step 1: Check Bundle Status**

| Status | Can Enter PO? | Solution |
|--------|---------------|----------|
| Active | ❌ No | Must be Approved first |
| Reviewed | ❌ No | Wait for Operation approval |
| Approved | ✅ Yes | Click "Order Placed" button |
| Ordered | ❌ No | PO already recorded |

**Step 2: If Approved**
- Click **"📦 Order Placed"** button
- Modal appears with PO fields
- Enter PO number and date
- Click Save

**Step 3: If Already Ordered**
- PO already recorded
- View PO details in bundle
- Cannot change (contact admin if wrong)

---

### Issue 8: Completed Bundle Shows Wrong Items

**Problem:** Bundle shows items that weren't in original bundle.

**Symptoms:**
- Items don't match memory
- Extra items showing
- Missing items

**Possible Causes:**
1. Items were moved after review
2. Display cache issue
3. Wrong bundle selected
4. Merge occurred

**Solution:**

**Step 1: Check Bundle History**
- Scroll to Bundle History section
- Review all actions
- Look for item moves
- Check merge events

**Step 2: Refresh Page**
- Press F5
- Clear browser cache
- Log out and log back in

**Step 3: Verify Bundle ID**
- Confirm you're looking at correct bundle
- Check bundle number
- Compare with PO

**Step 4: Contact Admin**
- If discrepancy confirmed
- Provide bundle ID
- List expected vs actual items
- Screenshot of issue

---

## 11) Best Practices

### ✅ DO:

#### **Review Process:**
- ✅ Review ALL bundles before sending to Operation Team
- ✅ Check vendor contact info carefully (email, phone)
- ✅ Verify all items and quantities in table
- ✅ Always review duplicate warnings
- ✅ Read merge reasons for updated bundles
- ✅ Check date needed column for urgent items
- ✅ Confirm vendor can supply items before marking reviewed
- ✅ Read user notes for special instructions

#### **Ordering:**
- ✅ Get quotes from vendors before placing PO
- ✅ Confirm availability before ordering
- ✅ Record PO numbers accurately
- ✅ Track delivery timelines
- ✅ Enter expected delivery date
- ✅ Keep vendor contacts organized
- ✅ Document all communications

#### **Completion:**
- ✅ Verify all items received before marking Completed
- ✅ Check packing slip matches order
- ✅ Enter packing slip code accurately
- ✅ Verify quantities match PO
- ✅ Check item quality and condition
- ✅ Notify users when items ready

#### **Communication:**
- ✅ Contact users about duplicates
- ✅ Inform users of delays
- ✅ Update users on delivery status
- ✅ Respond to user questions promptly
- ✅ Keep Operation Team informed
- ✅ Document issues and resolutions

---

### ❌ DON'T:

#### **Review Process:**
- ❌ Don't mark as reviewed without checking all items
- ❌ Don't ignore duplicate warnings
- ❌ Don't skip checklist items
- ❌ Don't approve if unsure about vendor
- ❌ Don't ignore merge badges
- ❌ Don't skip reading user notes
- ❌ Don't rush through reviews

#### **Ordering:**
- ❌ Don't place PO without quote
- ❌ Don't order without confirming availability
- ❌ Don't forget to record PO details
- ❌ Don't approve bundles you can't fulfill
- ❌ Don't ignore date needed urgency
- ❌ Don't place orders without Operation approval

#### **Completion:**
- ❌ Don't mark Completed before items arrive
- ❌ Don't mark Completed with missing items
- ❌ Don't forget packing slip code
- ❌ Don't accept damaged items without documentation
- ❌ Don't skip quality checks

#### **Changes:**
- ❌ Don't move items from Approved bundles (locked)
- ❌ Don't change Ordered bundles (locked)
- ❌ Don't ignore auto-revert warnings
- ❌ Don't make changes without documenting
- ❌ Don't bypass Operation Team approval

---

### Quick Tips:

#### **Efficiency:**
- Use status filter to focus on specific stages
- Review bundles in batches
- Keep vendor contacts in separate document
- Use keyboard shortcuts (F5 to refresh)
- Process similar bundles together
- Set reminders for delivery dates

#### **Quality:**
- Always verify duplicate warnings
- Double-check project numbers
- Confirm quantities before ordering
- Review table carefully
- Check merge reasons
- Verify vendor capabilities

#### **Communication:**
- Keep users informed of status
- Document issues in notes
- Contact vendors proactively
- Escalate problems quickly
- Update Operation Team regularly
- Maintain vendor relationships

#### **Organization:**
- Use status filter effectively
- Track PO numbers systematically
- Keep delivery schedule updated
- Maintain vendor contact list
- Document special cases
- Archive completed bundles

---

## 12) Quick Reference

### Status Icons & Meanings

| Icon | Status | Your Action | Can Change? |
|------|--------|-------------|-------------|
| 🟡 | **Active** | Review bundle | ✅ Yes |
| 🟢 | **Reviewed** | Wait for Operation approval | ✅ Yes (can revert) |
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
- ✅ Wait for Operation approval
- ✅ Revert to Active (if needed)
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

**Handle Duplicate:**
1. See warning in bundle
2. Contact users to verify
3. Adjust quantities if needed (or keep both)
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
5. Enter expected delivery date (optional)
6. Click "Save"

**Mark Completed:**
1. Bundle must be Ordered
2. Items must be received
3. Click "🏁 Mark as Completed"
4. Enter packing slip code
5. Enter actual delivery date
6. Click "Save"

---

### Important Rules to Remember

1. **Must review ALL before Operation Team can approve**
2. **Approved = Locked** (no changes allowed)
3. **Moving item TO Reviewed bundle = Auto-revert to Active**
4. **Duplicates must be reviewed before bundle review**
5. **Always verify vendor availability before marking reviewed**
6. **Record PO details immediately after placing order**
7. **Don't mark Completed until ALL items received**
8. **Operation Team must approve before you can order**

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
- ❌ Need to unlock Ordered bundle
- ❌ Data discrepancies

---

### Contact Information

**For Technical Issues:**
- Contact: System Admin
- Email: admin@yourcompany.com
- Phone: (555) 123-4567

**For User Questions:**
- Direct users to User Manual
- Or contact users directly via email

**For Vendor Issues:**
- Contact vendor directly (info in bundle)
- Escalate to purchasing manager if needed

**For Operation Team:**
- Contact: Operation Team Lead
- Email: operations@yourcompany.com

---

**End of Complete Operator Manual**

**Version:** 3.0 | **Last Updated:** November 10, 2025

---

*This manual covers all aspects of the Operator Dashboard. For user-facing features, see User_Manual_Users_PDF.md*
