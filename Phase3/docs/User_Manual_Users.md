# Phase 3 Requirements App – Complete User Manual (For Regular Users)

**Version:** 2.0 | **Last Updated:** October 14, 2025

Welcome to the Requirements Management System. This comprehensive guide explains how to submit your material needs, track them end‑to‑end, and understand all possible scenarios.

## Quick Navigation
- [Getting Started](#1-sign-in)
- [Complete Data Flow](#data-flow-journey)
- [Using the System](#2-your-home-tabs)
- [All Scenarios](#all-possible-scenarios)
- [Troubleshooting](#troubleshooting)

## 1) Sign In
- Open the app URL provided by your team.
- Enter your username and password, then click “Login”.
- After login you will see your name and role in the left sidebar.

If you ever need to leave the app, click “Logout” in the sidebar.

## 2) Your Home Tabs
You have three tabs at the top of the main area:
- “🔧 Raw Materials”
- “🛒 My Cart”
- “📋 My Requests”

Use these tabs to choose items, add them to your cart, submit a request, and check request status.

**Note:** Currently, only Raw Materials are available for requesting. BoxHero items will be enabled in the future.

---

## 3) Detailed Feature Guide

### 3.1) Raw Materials Tab - Complete Walkthrough

The Raw Materials tab uses a guided 4-step flow to help you select the exact item you need.

#### **Step 1: Select Material Type**

**What You See:**
```
┌─────────────────────────────────────┐
│ 🔧 Raw Materials                    │
│                                     │
│ Step 1: Select Material Type        │
│ ┌─────────────────────────────────┐ │
│ │ [Select material type...]       │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Available Options:**
- Acrylic
- Aluminum
- Dibond
- Foam Board
- Gatorboard
- Sintra
- And more...

**What to Do:**
1. Click the dropdown
2. Scroll to find your material type
3. Click to select

**Tips:**
- Material types are alphabetically sorted
- If you don't see your material, contact your operator

---

#### **Step 2: Select Specific Material**

**What You See (after selecting "Acrylic"):**
```
┌─────────────────────────────────────┐
│ Step 2: Select Material Name        │
│ ┌─────────────────────────────────┐ │
│ │ [Select material...]            │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Available materials:                │
│ • ACRYLITE Non-glare P99            │
│ • ACRYLITE Clear                    │
│ • ACRYLITE White                    │
└─────────────────────────────────────┘
```

**What to Do:**
1. Click the dropdown
2. Find the specific material you need
3. Click to select

**Tips:**
- Material names show full specifications
- If multiple sizes exist, you'll see them in Step 3

---

#### **Step 3: Select Size (If Multiple Options)**

**What You See:**
```
┌───────────────────────────────────────────────────┐
│ Step 3: Select Size                               │
│                                                   │
│ Available sizes for ACRYLITE Non-glare P99:       │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ 📏 48 x 96 x 0.125                            │ │
│ │ Height: 48" | Width: 96" | Thickness: 0.125"  │ │
│ │                              [Select] ────────→│ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ ┌───────────────────────────────────────────────┐ │
│ │ 📏 48 x 96 x 0.250                            │ │
│ │ Height: 48" | Width: 96" | Thickness: 0.250"  │ │
│ │                              [Select] ────────→│ │
│ └───────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

**What to Do:**
1. Review each size option carefully
2. Check dimensions (Height x Width x Thickness)
3. Click **[Select]** on the size you need

**Important:**
- ⚠️ Double-check thickness (most common mistake!)
- Dimensions are in inches
- If you select wrong size, click "🔄 Start Over"

---

#### **Step 4: Enter Quantity and Project**

**What You See:**
```
┌───────────────────────────────────────────────────┐
│ Step 4: Enter Quantity and Project                │
│                                                   │
│ Selected: ACRYLITE Non-glare P99 (48 x 96 x 0.125)│
│                                                   │
│ Quantity (pieces): *                              │
│ ┌─────────────────┐                              │
│ │ [5]             │                              │
│ └─────────────────┘                              │
│                                                   │
│ Project Number: *                                 │
│ ┌───────────────────────────────────────────────┐ │
│ │ [Select or enter project...]                  │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ Recent Projects:                                  │
│ • 23-1672                                         │
│ • 25-1559                                         │
│ • 24-1702                                         │
│                                                   │
│ Project Name (optional):                          │
│ ┌───────────────────────────────────────────────┐ │
│ │ [Office Renovation]                           │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│                      [🛒 Add to Cart] ────────────→│
└───────────────────────────────────────────────────┘
```

**What to Do:**
1. **Quantity:** Enter number of pieces needed (required)
2. **Project Number:** 
   - Select from recent projects dropdown, OR
   - Type new project number (required)
3. **Project Name:** Add descriptive name (optional)
4. Click **"🛒 Add to Cart"**

**Important Rules:**
- ✅ **Project Number is REQUIRED**
- ✅ Quantity must be at least 1
- ✅ For letter-based projects (CP-2025, BCHS 2025), you can add sub-project numbers

**Tips:**
- Recent projects show your last 10 projects
- Project numbers are validated against database
- If project doesn't exist, system will ask for confirmation

---

#### **Letter-Based Projects (Special Case)**

**What Happens:**
If your project starts with letters (e.g., CP-2025, BCHS 2025), the system detects it and shows an additional field.

**What You See:**
```
┌───────────────────────────────────────────────────┐
│ Project Number: *                                 │
│ ┌───────────────────────────────────────────────┐ │
│ │ CP-2025                                       │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ ℹ️ This is a letter-based project                 │
│                                                   │
│ Sub-Project Number (optional):                    │
│ ┌───────────────────────────────────────────────┐ │
│ │ [Enter sub-project number...]                 │ │
│ └───────────────────────────────────────────────┘ │
│                                                   │
│ Previous sub-projects for CP-2025:                │
│ • 001                                             │
│ • 002                                             │
│ • 003                                             │
└───────────────────────────────────────────────────┘
```

**What to Do:**
1. Enter main project: `CP-2025`
2. Enter sub-project: `004` (or select from previous)
3. System will track as: `CP-2025 / 004`

**Benefits:**
- ✅ Better tracking for multi-phase projects
- ✅ Separate budgets per sub-project
- ✅ Historical reference for future requests

---

#### **Start Over Feature**

**When to Use:**
- Selected wrong material type
- Selected wrong material name
- Selected wrong size
- Want to start fresh

**What to Do:**
1. Click **"🔄 Start Over"** button (appears at any step)
2. All selections cleared
3. Returns to Step 1

---

### 3.2) My Cart Tab - Complete Guide

#### **Cart Overview**

**What You See:**
```
┌─────────────────────────────────────────────────────┐
│ 🛒 My Cart                                          │
│                                                     │
│ You have 3 items in your cart                       │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Item 1: ACRYLITE Non-glare P99 (48 x 96 x 0.125)│ │
│ │ Project: 📋 23-1672 (Office Renovation)         │ │
│ │ Quantity: [5] pieces    [Update] [Remove]       │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Item 2: DURA-CAST IM-7328 3/16" 4x8 WHITE PM*   │ │
│ │ Project: 📋 23-1672 (Office Renovation)         │ │
│ │ Quantity: [2] pieces    [Update] [Remove]       │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Item 3: Painted Dibond (Red) (48 x 96 x 0.125)  │ │
│ │ Project: 📋 24-1702 (Signage Project)           │ │
│ │ Quantity: [3] pieces    [Update] [Remove]       │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ Total Items: 3 | Total Pieces: 10                   │
│                                                     │
│ [Clear Cart]                  [Submit Request] ────→│
└─────────────────────────────────────────────────────┘
```

#### **Cart Actions**

**1. Update Quantity**
- Change number in quantity box
- Click **[Update]**
- Quantity updates immediately
- Success message appears

**2. Remove Item**
- Click **[Remove]** next to item
- Item removed from cart instantly
- No confirmation needed (can re-add if mistake)

**3. Clear Cart**
- Click **[Clear Cart]** at bottom
- Confirmation dialog appears: "Are you sure you want to clear your cart?"
- Click "Yes" to remove ALL items
- Click "No" to cancel

**4. Submit Request**
- Click **[Submit Request]**
- System validates all items
- Creates request number
- Shows success message

---

#### **Submit Request - What Happens**

**Before Submit:**
```
Cart Items (in memory):
├─ Item 1: ACRYLITE (5 pcs, Project 23-1672)
├─ Item 2: DURA-CAST (2 pcs, Project 23-1672)
└─ Item 3: Dibond (3 pcs, Project 24-1702)
```

**Click "Submit Request"**

**System Validation:**
- ✅ All items have quantities
- ✅ All items have projects
- ✅ No duplicate items
- ✅ User is authenticated

**Success Message:**
```
┌─────────────────────────────────────────┐
│ ✅ Request Submitted Successfully!      │
│                                         │
│ Request Number: REQ-20251014-001        │
│ Total Items: 3                          │
│ Total Pieces: 10                        │
│ Status: Pending                         │
│                                         │
│ Your request will be bundled and        │
│ processed by the procurement team.      │
└─────────────────────────────────────────┘
```

**After Submit:**
- ✅ Cart is cleared
- ✅ Request appears in "My Requests" tab
- ✅ Status: 🟡 Pending

---

### 3.3) My Requests Tab - Complete Guide

#### **Request List View**

**What You See:**
```
┌─────────────────────────────────────────────────────┐
│ 📋 My Requests                                      │
│                                                     │
│ Filter by Status: [All Statuses ▼]                  │
│                                                     │
│ You have 5 requests                                 │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ ▼ REQ-20251014-001 | 🟡 Pending | Oct 14, 2025  │ │
│ │   3 items | 10 pieces                           │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ ▼ REQ-20251012-003 | 🔵 In Progress | Oct 12    │ │
│ │   2 items | 5 pieces                            │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ ▼ REQ-20251010-002 | ✅ Completed | Oct 10      │ │
│ │   4 items | 12 pieces | Completed: Oct 13       │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

#### **Request Status Meanings**

**🟡 Pending**
- Your request is waiting to be bundled
- Cron job runs twice a week
- You CAN still edit quantities
- No action needed from you

**🔵 In Progress**
- Your request is part of a bundle
- Operator is processing the order
- Quantities are LOCKED (cannot edit)
- Bundle ID shown for reference

**✅ Completed**
- Items have been received
- Ready for pickup/use
- Completion date shown
- Packing slip code shown

---

#### **Expanded Request View (Pending)**

**Click ▼ to expand:**
```
┌─────────────────────────────────────────────────────┐
│ ▼ REQ-20251014-001 | 🟡 Pending | Oct 14, 2025      │
│   3 items | 10 pieces                               │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Your Items:                                     │ │
│ │                                                 │ │
│ │ • ACRYLITE Non-glare P99 (48 x 96 x 0.125)     │ │
│ │   Project: 📋 23-1672 (Office Renovation)       │ │
│ │   Quantity: [5] pieces          [Update]        │ │
│ │                                                 │ │
│ │ • DURA-CAST IM-7328 3/16" 4x8 WHITE PM*        │ │
│ │   Project: 📋 23-1672 (Office Renovation)       │ │
│ │   Quantity: [2] pieces          [Update]        │ │
│ │                                                 │ │
│ │ • Painted Dibond (Red) (48 x 96 x 0.125)       │ │
│ │   Project: 📋 24-1702 (Signage Project)         │ │
│ │   Quantity: [3] pieces          [Update]        │ │
│ │                                                 │ │
│ │ ℹ️ You can update quantities until bundled      │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**What You Can Do:**
- ✅ Update quantities (change number and click Update)
- ✅ View all item details
- ✅ See project information
- ❌ Cannot remove items (submit new request instead)

---

#### **Expanded Request View (In Progress)**

**Click ▼ to expand:**
```
┌─────────────────────────────────────────────────────┐
│ ▼ REQ-20251012-003 | 🔵 In Progress | Oct 12, 2025  │
│   2 items | 5 pieces                                │
│   Bundle: BUNDLE-20251012-001 (S & F Supplies Inc.) │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Your Items:                                     │ │
│ │                                                 │ │
│ │ • ACRYLITE Non-glare P99 (48 x 96 x 0.125)     │ │
│ │   Project: 📋 25-1559                           │ │
│ │   Quantity: 3 pieces (locked)                   │ │
│ │                                                 │ │
│ │ • DURA-CAST IM-7328 3/16" 4x8 WHITE PM*        │ │
│ │   Project: 📋 23-1672                           │ │
│ │   Quantity: 2 pieces (locked)                   │ │
│ │                                                 │ │
│ │ ℹ️ Quantities are locked while being processed  │ │
│ │ 📦 Bundle Status: Approved                       │ │
│ │ 📧 Vendor: S & F Supplies Inc.                  │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**What You See:**
- ✅ Bundle ID and vendor name
- ✅ Bundle status (Reviewed/Approved/Ordered)
- ✅ All item details
- ❌ Quantities are READ-ONLY (locked)

**What This Means:**
- Your request is being actively processed
- Operator has reviewed and approved the bundle
- Order will be placed with vendor soon
- No changes can be made at this stage

---

#### **Expanded Request View (Completed)**

**Click ▼ to expand:**
```
┌─────────────────────────────────────────────────────┐
│ ▼ REQ-20251010-002 | ✅ Completed | Oct 10, 2025    │
│   4 items | 12 pieces                               │
│   Completed: Oct 13, 2025                           │
│   Bundle: BUNDLE-20251010-002 (O Reilly Auto Parts) │
│   Packing Slip: PS-2025-1013-A                      │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Your Items:                                     │ │
│ │                                                 │ │
│ │ • ACRYLITE Non-glare P99 (48 x 96 x 0.125)     │ │
│ │   Project: 📋 23-1672 - 5 pcs                   │ │
│ │                                                 │ │
│ │ • DURA-CAST IM-7328 3/16" 4x8 WHITE PM*        │ │
│ │   Project: 📋 23-1672 - 2 pcs                   │ │
│ │                                                 │ │
│ │ • Painted Dibond (Red) (48 x 96 x 0.125)       │ │
│ │   Project: 📋 24-1702 - 3 pcs                   │ │
│ │                                                 │ │
│ │ • Foam Board 3/16" (48 x 96)                   │ │
│ │   Project: 📋 24-1702 - 2 pcs                   │ │
│ │                                                 │ │
│ │ ✅ Items received and ready for pickup           │ │
│ │ 📦 Packing Slip: PS-2025-1013-A                 │ │
│ │ 📍 Location: Warehouse - Bay 3                  │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**What You See:**
- ✅ Completion date
- ✅ Packing slip code
- ✅ Vendor information
- ✅ All items delivered

**What to Do:**
- Contact warehouse/receiving to pick up items
- Reference packing slip code
- Verify all items received

---

## 4) Complete Data Flow Journey

### End-to-End Process Overview

```
YOU → SYSTEM → OPERATOR → VENDOR → COMPLETED
│       │        │           │         │
│       │        │           │         └─ Items delivered
│       │        │           └─ Order placed
│       │        └─ Bundle reviewed & approved
│       └─ Smart bundling (2x/week)
└─ Submit request
```

**Timeline:** 3-7 days from submission to completion

---

### Detailed Step-by-Step Flow

**Stage 1: YOU Submit Request**
- Browse Raw Materials tab
- Select material, size, quantity
- Enter project number
- Add to cart
- Submit request
- Status: 🟡 Pending

**Stage 2: SYSTEM Bundles Automatically**
- Cron job runs twice a week (Tuesday, Thursday)
- Groups your items with other users
- Optimizes by vendor
- Creates bundle
- Your status changes: 🔵 In Progress

**Stage 3: OPERATOR Reviews**
- Reviews all items
- Checks for duplicates
- Marks as Reviewed
- Approves bundle

**Stage 4: OPERATOR Places Order**
- Contacts vendor
- Places purchase order
- Records PO number
- Status: 📦 Ordered

**Stage 5: VENDOR Ships**
- Processes order
- Ships to warehouse
- Items arrive

**Stage 6: OPERATOR Marks Complete**
- Receives items
- Verifies packing slip
- Marks bundle complete
- Your status: ✅ Completed

**Stage 7: YOU Pick Up**
- See completion notification
- Contact warehouse
- Pick up items

---

## 5) All Possible Scenarios

### Scenario 1: Normal Flow (No Issues)

**Your Actions:**
1. Add ACRYLITE P99 to cart (5 pcs, Project 23-1672)
2. Submit request → REQ-20251014-001
3. Status: Pending
4. Wait 1-3 days for bundling
5. Status changes to: In Progress
6. Wait 3-5 days for delivery
7. Status changes to: Completed
8. Pick up items from warehouse

**Timeline:** 7 days total

---

### Scenario 2: Duplicate Detection (Same Item, Same Project)

**What happens:**
You and another user both request ACRYLITE P99 for Project 25-1559.

**System response:**
-  Both requests accepted
-  Bundled together
-  Operator sees duplicate warning
-  Operator reviews quantities
-  May contact you to confirm

**Result:** Prevents over-ordering

---

### Scenario 2: Item Already Requested (Pending)

**What happens:**
You try to add item you already requested in a Pending request.

**System response:**
```
 You already have this item for this project in a pending request!
 ACRYLITE Non-glare P99 - Project: 23-1672
Current quantity in REQ-20251014-001: 5 pieces
 Go to 'My Requests' tab to edit the quantity instead.
```

**What to do:**
- Go to My Requests tab
- Find the pending request
- Update quantity there

**Why:** Prevents duplicate requests

---

### Scenario 3: Item Already In Progress

**What happens:**
You try to add item that's already being processed.

**System response:**
```
 This item is already being processed for this project!
 ACRYLITE Non-glare P99 - Project: 23-1672
Current request: REQ-20251012-003 (In Progress)
Quantity: 5 pieces
 Cannot modify - already in bundle BUNDLE-20251012-001
 Submit a new request if you need additional quantity.
```

**What to do:**
- Wait for current request to complete, OR
- Submit new request for additional quantity

**Why:** Locked items cannot be changed

---

### Scenario 4: Vendor Change (Item Moved)

**What happens:**
Operator moves your item to different vendor for better price/availability.

**Your view:**
- Request status: Still "In Progress"
- Bundle ID changes
- Vendor name changes
- No action needed from you

**Why:** System optimizes vendor selection

---

### Scenario 5: Letter-Based Project with Sub-Projects

**What happens:**
Your project is "CP-2025" with multiple phases.

**How to enter:**
1. Project Number: `CP-2025`
2. System detects letter-based project
3. Sub-Project field appears
4. Enter sub-project: `004`
5. System tracks as: `CP-2025 / 004`

**Benefits:**
- Separate tracking per phase
- Better budget management
- Historical reference

---

### Scenario 6: Quantity Update (Pending Request)

**What happens:**
You realize you need more/less quantity.

**If Pending:**
1. Go to My Requests
2. Expand request
3. Change quantity
4. Click Update
5. ✅ Quantity updated

**If In Progress:**
- ❌ Cannot update (locked)
- Submit new request for additional items

---

### Scenario 7: Multiple Items for Same Project

**What happens:**
You need several different materials for one project.

**Your Actions:**
1. Add Item 1: ACRYLITE (5 pcs, Project 23-1672)
2. Add Item 2: DURA-CAST (2 pcs, Project 23-1672)
3. Add Item 3: Dibond (3 pcs, Project 23-1672)
4. Submit request

**Result:**
- All items in one request
- All tracked under Project 23-1672
- Operator sees complete project needs

---

### Scenario 8: Multiple Projects in One Cart

**What happens:**
You need materials for different projects.

**Your Actions:**
1. Add Item 1: ACRYLITE (5 pcs, Project 23-1672)
2. Add Item 2: Dibond (3 pcs, Project 24-1702)
3. Submit request

**Result:**
- One request with items for 2 projects
- System tracks each item to correct project
- Both projects get their materials

---

### Scenario 9: Cart Cleared by Accident

**What happens:**
You accidentally click "Clear Cart".

**What to Do:**
- ❌ Cannot undo (cart is cleared)
- ✅ Re-add items from Raw Materials tab
- ✅ Recent projects still saved for quick entry

**Prevention:**
- Confirmation dialog appears before clearing
- Always click "No" if unsure

---

### Scenario 10: Login Issues

**Problem:** Can't log in

**Possible Causes:**
1. Wrong username/password
2. Account inactive
3. Network issues

**What to Do:**
1. Verify credentials
2. Contact operator/admin
3. Check internet connection

---

## 6) Troubleshooting

### Issue: Can't Find Material

**Problem:** Material not in dropdown

**Solution:**
1. Check spelling
2. Try different material type
3. Contact operator to add material

---

### Issue: Project Number Not Accepted

**Problem:** "Project not found" error

**Solution:**
1. Verify project number format
2. Check with project manager
3. System will ask to create new project
4. Confirm creation

---

### Issue: Can't Update Quantity

**Problem:** Update button disabled

**Reason:** Request is In Progress (locked)

**Solution:**
- Wait for completion, OR
- Submit new request for additional quantity

---

### Issue: Request Stuck in Pending

**Problem:** Request pending for several days

**Reason:** Waiting for bundling cron job

**Timeline:**
- Cron runs twice a week
- Maximum wait: 3-4 days
- If longer, contact operator

---

## 7) Best Practices

### ✅ DO:
- Enter correct project numbers
- Double-check dimensions before adding (especially thickness!)
- Review cart before submitting
- Update quantities in Pending requests if needed
- Track requests regularly
- Use descriptive project names
- Contact operator if unsure

### ❌ DON'T:
- Submit duplicate requests
- Use wrong project numbers
- Try to modify In Progress requests
- Ignore duplicate warnings
- Clear cart without checking
- Skip project number entry

---

## 8) Quick Reference Guide

### Common Tasks Cheat Sheet

**Add Item to Cart:**
1. Go to Raw Materials tab
2. Select material type
3. Select material name
4. Select size
5. Enter quantity
6. Enter project number
7. Click "Add to Cart"

**Submit Request:**
1. Go to My Cart tab
2. Review all items
3. Click "Submit Request"
4. See success message
5. Note your request number

**Update Pending Quantity:**
1. Go to My Requests tab
2. Find Pending request
3. Click ▼ to expand
4. Change quantity
5. Click "Update"

**Check Request Status:**
1. Go to My Requests tab
2. See status icon (🟡/🔵/✅)
3. Click ▼ to see details

---

### Status Icons & Meanings

| Icon | Status | What It Means | Can You Edit? |
|------|--------|---------------|---------------|
| 🟡 | **Pending** | Waiting for bundling | ✅ Yes |
| 🔵 | **In Progress** | Being processed | ❌ Locked |
| ✅ | **Completed** | Ready for pickup | ❌ Final |

---

### Key Terms

- **Request:** Your submission (e.g., REQ-20251014-001)
- **Bundle:** Group of items for one vendor (created by system)
- **Cron Job:** Automatic bundling process (runs 2x/week)
- **Locked:** Cannot be modified (In Progress or Completed)
- **Pending:** Can still be edited
- **Project Number:** Required for tracking (e.g., 23-1672)
- **Letter-Based Project:** Project with letters (e.g., CP-2025)
- **Sub-Project:** Phase within letter-based project (e.g., 004)
- **Packing Slip:** Code for picking up completed items

---

### Timeline Reference

```
Day 0: You submit request (Pending)
Day 1-3: Wait for cron job (runs Tue/Thu)
Day 3: System creates bundle (In Progress)
Day 3-4: Operator reviews & approves
Day 4: Operator places order (Ordered)
Day 4-7: Vendor ships items
Day 7: Items arrive (Completed)

Total: ~7 days average
```

---

### Error Messages & What They Mean

**"You already have this item for this project in a pending request!"**
- Meaning: Duplicate in Pending request
- Action: Go to My Requests and update quantity there

**"This item is already being processed for this project!"**
- Meaning: Item is In Progress (locked)
- Action: Wait for completion OR submit new request for additional quantity

**"Project not found"**
- Meaning: New project number
- Action: Confirm creation when prompted

**"Please enter a quantity"**
- Meaning: Quantity field empty
- Action: Enter number of pieces needed

**"Please select a project"**
- Meaning: Project number required
- Action: Select or enter project number

---

### When to Contact Operator

**Contact Operator If:**
- ❌ Can't find material in dropdown
- ❌ Need to add new material
- ❌ Request stuck in Pending > 4 days
- ❌ Need urgent request processed
- ❌ Questions about project numbers
- ❌ Issues with quantities
- ❌ Need to cancel In Progress request
- ❌ Items not received after Completed status

---

### Keyboard Shortcuts & Tips

**Navigation:**
- F5 - Refresh page
- Ctrl+F - Find on page
- Tab - Move between fields

**Efficiency Tips:**
- Use recent projects dropdown (saves typing)
- Add multiple items before submitting (one request)
- Check My Requests regularly
- Note your request number for reference
- Keep project numbers handy

---

### Important Rules to Remember

1. **Project Number is REQUIRED** for all items
2. **Pending = Can Edit** | **In Progress = Locked**
3. **Cron runs 2x/week** (Tuesday, Thursday)
4. **Maximum wait: 3-4 days** for bundling
5. **Cannot remove items from cart** (only update quantity or remove completely)
6. **Cannot undo Clear Cart** (re-add items)
7. **Letter-based projects** can have sub-projects

---

### Contact Information

**For Questions:**
- Contact: Your Operator
- Email: [operator@company.com]

**For New Materials:**
- Request via operator
- Provide material specifications

**For Urgent Requests:**
- Contact operator directly
- Explain urgency

**For Technical Issues:**
- Contact: System Admin
- Email: [admin@company.com]

---

**End of Complete User Manual**

**Version:** 2.0 | **Last Updated:** October 14, 2025

---

That's it! Add items, submit, and track your requests in one place. Your procurement team will handle vendors and ordering.
