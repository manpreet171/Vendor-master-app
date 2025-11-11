# Phase 3 Requirements App – Complete User Manual
## For Regular Users

**Version:** 3.0  
**Last Updated:** November 7, 2025

---

Welcome to the Requirements Management System. This comprehensive guide explains how to submit your material needs, track them end-to-end, and understand all possible scenarios.

---

## Table of Contents

1. [Getting Started](#1-sign-in)
2. [Your Home Tabs](#2-your-home-tabs)
3. [Detailed Feature Guide](#3-detailed-feature-guide)
   - [Raw Materials Tab](#31-raw-materials-tab---complete-walkthrough)
   - [My Cart Tab](#32-my-cart-tab---complete-guide)
   - [My Requests Tab](#33-my-requests-tab---track-your-orders)
4. [Complete Data Flow Journey](#4-complete-data-flow-journey)
5. [All Possible Scenarios](#5-all-possible-scenarios)
6. [Troubleshooting](#6-troubleshooting)

---

## 1) Sign In

- Open the app URL provided by your team
- Enter your username and password, then click "Login"
- After login you will see your name and role in the left sidebar

If you ever need to leave the app, click "Logout" in the sidebar.

---

## 2) Your Home Tabs

You have three tabs at the top of the main area:

- **🔧 Raw Materials** - Browse and select items
- **🛒 My Cart** - Review items before submitting
- **📋 My Requests** - Track your order status

Use these tabs to choose items, add them to your cart, submit a request, and check request status.

> **Note:** Currently, only Raw Materials are available for requesting. BoxHero items will be enabled in the future.

---

## 3) Detailed Feature Guide

### 3.1) Raw Materials Tab - Complete Walkthrough

The Raw Materials tab uses a guided 4-step flow to help you select the exact item you need.

---

#### **Step 1: Select Material Type**

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

**Example (after selecting "Acrylic"):**

Available materials:
- ACRYLITE Non-glare P99
- ACRYLITE Clear
- ACRYLITE White

**What to Do:**
1. Click the dropdown
2. Find the specific material you need
3. Click to select

**Tips:**
- Material names show full specifications
- If multiple sizes exist, you'll see them in Step 3

---

#### **Step 3: Select Size (If Multiple Options)**

**Example: Available sizes for ACRYLITE Non-glare P99**

| Size | Dimensions | Action |
|------|------------|--------|
| 📏 48 x 96 x 0.125 | Height: 48" \| Width: 96" \| Thickness: 0.125" | [Select] |
| 📏 48 x 96 x 0.250 | Height: 48" \| Width: 96" \| Thickness: 0.250" | [Select] |

**What to Do:**
1. Review each size option carefully
2. Check dimensions (Height x Width x Thickness)
3. Click **[Select]** on the size you need

**Important:**
- ⚠️ Double-check thickness (most common mistake!)
- Dimensions are in inches
- If you select wrong size, click "🔄 Start Over"

---

#### **Step 4: Enter Quantity, Project, and Date**

**Fields to Fill:**

| Field | Required | Description |
|-------|----------|-------------|
| **Quantity (pieces)** | ✅ Yes | Number of pieces needed (minimum 1) |
| **Project Number** | ✅ Yes | Select from recent projects or enter new |
| **Project Name** | ❌ Optional | Descriptive name for the project |
| **📅 Date Needed** | ❌ Optional | When you need items delivered |

**What to Do:**
1. **Quantity:** Enter number of pieces needed (required)
2. **Project Number:** 
   - Select from recent projects dropdown, OR
   - Type new project number (required)
3. **Project Name:** Add descriptive name (optional)
4. **📅 Date Needed:** Select when you need items (optional)
5. Click **"🛒 Add to Cart"**

**Important Rules:**
- ✅ Project Number is REQUIRED
- ✅ Quantity must be at least 1
- ✅ Date Needed is optional but helps operators prioritize urgent orders
- ✅ For letter-based projects (CP-2025, BCHS 2025), you can add sub-project numbers

**Tips:**
- Recent projects show your last 10 projects
- Project numbers are validated against database
- If project doesn't exist, system will ask for confirmation
- **Date Needed helps operators prioritize urgent orders - use it when you have deadlines!**

---

#### **📅 Date Needed Feature**

**What It Does:**
- Lets you specify when you need items delivered
- Helps operators prioritize urgent orders
- Completely optional (leave blank if no specific deadline)

**How to Use:**
1. Click the date picker
2. Select date from calendar
3. Only future dates allowed (calendar opens at today)
4. Leave blank if no specific deadline

**Benefits:**
- ✅ Operators see your deadline in the bundle
- ✅ Urgent items get priority
- ✅ Better planning and scheduling
- ✅ Reduces follow-up questions about urgency

**Example:**
```
Date Needed: November 15, 2025
→ Operator knows this is urgent
→ Will prioritize this order
→ You get items faster!
```

---

#### **Letter-Based Projects (Special Case)**

**What Happens:**
If your project starts with letters (e.g., CP-2025, BCHS 2025), the system detects it and shows an additional field for sub-projects.

**Example:**

**Main Project:** CP-2025  
**Sub-Project:** 004  
**System Tracks As:** CP-2025 / 004

**Previous sub-projects for CP-2025:**
- 001
- 002
- 003

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

Your cart displays all items you've added, showing:
- Item name and specifications
- Project number and name
- Date needed (if specified)
- Quantity
- Options to Update or Remove

**Example Cart Items:**

**Item 1:**
- **Material:** ACRYLITE Non-glare P99 (48 x 96 x 0.125)
- **Project:** 📋 23-1672 (Office Renovation)
- **📅 Needed:** 2025-11-15
- **Quantity:** 5 pieces
- **Actions:** [Update] [Remove]

**Item 2:**
- **Material:** DURA-CAST IM-7328 3/16" 4x8 WHITE PM*
- **Project:** 📋 25-1559 (Lobby Signage)
- **📅 Needed:** 2025-11-20
- **Quantity:** 2 pieces
- **Actions:** [Update] [Remove]

---

#### **Cart Actions**

**Update Quantity:**
1. Change the number in the quantity box
2. Click **[Update]**
3. Cart updates immediately

**Remove Item:**
1. Click **[Remove]** next to the item
2. Item disappears from cart
3. No confirmation needed

**Add Notes (Optional):**
- Text box appears below cart items
- Add any special instructions or comments
- Notes will be visible to operators
- Maximum 1000 characters

**Example Notes:**
```
"Please prioritize the acrylic sheets - needed for client presentation.
The foam board can wait until next week if needed."
```

---

#### **Submit Your Request**

**Before Submitting - Review Checklist:**
- ✅ All items correct?
- ✅ Quantities accurate?
- ✅ Projects assigned correctly?
- ✅ Dates needed specified (if urgent)?
- ✅ Any special notes added?

**To Submit:**
1. Review all items in cart
2. Add notes if needed (optional)
3. Click **"📤 Submit Request"** button
4. Confirmation message appears
5. Cart clears automatically
6. Request appears in "My Requests" tab

**Success Message:**
```
✅ Request submitted successfully!
Request Number: REQ-2025-001
Status: Pending
You will receive email notifications when status changes.
```

**What Happens Next:**
1. Your request status: **Pending**
2. System processes requests twice weekly (Tuesday & Thursday, 10 AM)
3. Your items grouped with others for same vendor
4. Status changes to **In Progress**
5. You receive email notification
6. Operator reviews and places order
7. Status changes to **Ordered**
8. You receive another email notification
9. Items arrive and status changes to **Completed**

---

### 3.3) My Requests Tab - Track Your Orders

#### **Request Status Overview**

Your requests can have four different statuses:

| Status | Icon | What It Means | What You Can Do |
|--------|------|---------------|-----------------|
| **Pending** | 🟡 | Waiting to be processed | ✏️ Edit quantities or cancel |
| **In Progress** | 🔵 | Being prepared for ordering | ⏳ Wait - team is working on it |
| **Ordered** | ✅ | Order placed with supplier | 📦 Items will arrive soon |
| **Completed** | 🎉 | Items received and available | ✅ You can request this item again |

---

#### **Understanding Request Restrictions**

**🚫 Why Can't I Request the Same Item Again?**

**Rule:** You cannot request an item that's already **Pending** or **In Progress** for the same project.

**Reason:** We group requests together to save costs. If you need more of the same item:
- **If Pending:** Edit the quantity in your existing request
- **If In Progress:** Wait for completion, then submit a new request
- **If Completed:** You can freely request it again

**💡 Quick Tips:**
- **Pending requests** can be edited anytime before processing (Tue/Thu 10 AM)
- **In Progress** means processing started - no changes allowed
- **Completed items** are available - request them anytime
- Check this tab regularly to track your order progress

---

#### **Request List View**

Requests are organized into tabs by status:

- **🟡 Pending** - Awaiting processing
- **🔵 In Progress** - Currently being prepared
- **✅ Ordered** - Order placed with vendor
- **🎉 Completed** - Items received

**Each Request Shows:**
- Request number (e.g., REQ-2025-001)
- Submission date
- Total items count
- Current status
- Expand button to see details

---

#### **Request Details (Expanded View)**

**Click on any request to see:**

**Request Information:**
- Request Number: REQ-2025-001
- Submitted: November 5, 2025
- Status: In Progress
- Your Notes: "Urgent - needed for client presentation"

**Items in This Request:**

| Item | Project | Date Needed | Quantity | Status |
|------|---------|-------------|----------|--------|
| ACRYLITE Non-glare P99 (48 x 96 x 0.125) | 23-1672 (Office Renovation) | 2025-11-15 | 5 pcs | In Progress |
| DURA-CAST IM-7328 3/16" 4x8 WHITE PM* | 25-1559 (Lobby Signage) | 2025-11-20 | 2 pcs | In Progress |

**Bundle Information (if processed):**
- Bundle ID: RM-2025-11-05-001
- Vendor: ABC Plastics Inc.
- Bundle Status: Active
- Other users in this bundle: 2

---

#### **Editing Pending Requests**

**For Pending Requests Only:**

**Update Quantity:**
1. Click **[Edit Quantity]** next to item
2. Enter new quantity
3. Click **[Save]**
4. Confirmation message appears

**Cancel Request:**
1. Click **[Cancel Request]** button
2. Confirm cancellation
3. Request removed from system

**Important:**
- ⚠️ You can only edit **Pending** requests
- ⚠️ Once status changes to **In Progress**, no edits allowed
- ⚠️ Processing happens Tuesday & Thursday at 10 AM

---

## 4) Complete Data Flow Journey

### **From Your Request to Delivery**

**Stage 1: You Submit Request (Pending)**
- You add items to cart
- You submit request
- Status: **Pending**
- You receive confirmation email

**Stage 2: System Processing (In Progress)**
- Happens Tuesday & Thursday at 10 AM
- System groups requests by vendor
- Creates "bundles" for each vendor
- Your status changes to: **In Progress**
- You receive email notification

**Stage 3: Operation Team Review**
- Operation Team reviews bundles
- Checks for duplicates or issues
- Approves bundles for ordering
- Bundle status: Active → Reviewed → Approved

**Stage 4: Operator Places Order (Ordered)**
- Operator contacts vendor
- Places order with PO number
- Enters order details in system
- Your status changes to: **Ordered**
- You receive email notification

**Stage 5: Order Arrives (Completed)**
- Vendor delivers items
- Operator marks bundle as completed
- Your status changes to: **Completed**
- You receive final email notification
- You can now request these items again

---

### **Email Notifications You'll Receive**

**1. Request Submitted**
```
Subject: Request Submitted - REQ-2025-001
Your request has been submitted successfully.
Status: Pending
Next processing: Tuesday, November 7 at 10 AM
```

**2. Processing Started**
```
Subject: Request In Progress - REQ-2025-001
Your request is being processed.
Status: In Progress
Bundle: RM-2025-11-05-001
Vendor: ABC Plastics Inc.
```

**3. Order Placed**
```
Subject: Order Placed - REQ-2025-001
Your items have been ordered from the vendor.
Status: Ordered
PO Number: PO-12345
Expected Delivery: November 15, 2025
```

**4. Order Completed**
```
Subject: Order Completed - REQ-2025-001
Your items have been received and are available.
Status: Completed
You can now request these items again if needed.
```

---

## 5) All Possible Scenarios

### Scenario 1: Simple Request (First Time)

**What happens:**
You need 5 pieces of acrylic for a new project.

**Steps:**
1. Go to Raw Materials tab
2. Select: Acrylic → ACRYLITE Non-glare P99 → 48 x 96 x 0.125
3. Enter: Quantity: 5, Project: 23-1672
4. Add to cart
5. Submit request
6. Status: Pending

**Result:** ✅ Request created successfully

---

### Scenario 2: Duplicate Item (Same Project)

**What happens:**
You try to request the same item for the same project again while first request is still Pending.

**System Response:**
```
⚠️ You already have a pending request for this item!
Current quantity in REQ-2025-001: 5 pieces
💡 Go to 'My Requests' tab to edit the quantity instead of creating a duplicate.
```

**What to do:**
- Go to My Requests tab
- Find the pending request
- Click [Edit Quantity]
- Update to new quantity (e.g., 10 pieces)
- Click [Save]

**Result:** ✅ Existing request updated, no duplicate created

---

### Scenario 3: Same Item, Different Project

**What happens:**
You need the same acrylic for a different project.

**Steps:**
1. Select same item: ACRYLITE Non-glare P99 (48 x 96 x 0.125)
2. Enter different project: 25-1559
3. Add to cart
4. Submit request

**Result:** ✅ New request created (different project = allowed)

---

### Scenario 4: Item Already In Progress

**What happens:**
You try to request an item that's already being processed for the same project.

**System Response:**
```
❌ This item is already being processed for this project!
📋 ACRYLITE Non-glare P99 - Project: 23-1672
Request: REQ-2025-001 - Status: In Progress
⏳ Please wait for the current order to complete before requesting this item again.
```

**What to do:**
- Wait for current order to complete
- Check My Requests tab for status updates
- Once completed, you can request again

**Result:** ❌ Cannot add to cart (blocked)

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
1. Go to My Requests tab
2. Click on pending request
3. Click [Edit Quantity]
4. Change quantity
5. Click [Save]

**Result:** ✅ Quantity updated

**If In Progress/Ordered:**
- Cannot edit
- Contact operator directly
- Explain situation

**Result:** ⚠️ Manual intervention needed

---

### Scenario 7: Urgent Order with Date Needed

**What happens:**
You need items by a specific deadline.

**Steps:**
1. Add item to cart
2. Click date picker for "Date Needed"
3. Select deadline date (e.g., November 15, 2025)
4. Submit request

**What operator sees:**
```
⚠️ URGENT: Date Needed: November 15, 2025
User: John Smith
Item: ACRYLITE Non-glare P99
Project: 23-1672
```

**Result:** ✅ Operator prioritizes your order

---

### Scenario 8: Bundle Vendor Change

**What happens:**
System initially assigns Vendor A, but later changes to Vendor B for better pricing.

**Your view:**
- Request status: Still "In Progress"
- Bundle ID changes
- Vendor name changes
- No action needed from you

**Why:** System optimizes vendor selection

---

### Scenario 9: Request Cancellation

**What happens:**
You no longer need the items.

**If Pending:**
1. Go to My Requests tab
2. Click on pending request
3. Click [Cancel Request]
4. Confirm cancellation

**Result:** ✅ Request cancelled

**If In Progress/Ordered:**
- Cannot cancel through system
- Contact operator immediately
- Explain situation

**Result:** ⚠️ Manual intervention needed

---

### Scenario 10: Multiple Items, Same Cart

**What happens:**
You need several different items for the same project.

**Steps:**
1. Add Item 1 to cart (Acrylic, Project: 23-1672)
2. Add Item 2 to cart (Foam Board, Project: 23-1672)
3. Add Item 3 to cart (Aluminum, Project: 23-1672)
4. Review cart
5. Submit request

**Result:**
- ✅ One request created (REQ-2025-001)
- ✅ Contains all 3 items
- ✅ All for same project
- ✅ System may create multiple bundles (different vendors)

---

## 6) Troubleshooting

### Common Issues and Solutions

#### Issue 1: Can't Add Item to Cart

**Symptoms:**
- Error message appears
- Item won't add to cart

**Possible Causes:**
1. **Duplicate item for same project (Pending/In Progress)**
   - **Solution:** Edit existing request quantity instead

2. **Missing required fields**
   - **Solution:** Ensure Quantity and Project Number are filled

3. **Invalid project number**
   - **Solution:** Check project number format, confirm with team

---

#### Issue 2: Can't Edit Request

**Symptoms:**
- Edit button disabled or missing
- Changes won't save

**Possible Causes:**
1. **Request status is not Pending**
   - **Solution:** Only Pending requests can be edited. Contact operator for In Progress/Ordered requests.

2. **Processing already started**
   - **Solution:** Wait for completion, then submit new request

---

#### Issue 3: Not Receiving Email Notifications

**Symptoms:**
- No emails when status changes
- Missing confirmation emails

**Possible Causes:**
1. **Email address not in system**
   - **Solution:** Contact administrator to update your email

2. **Emails in spam folder**
   - **Solution:** Check spam, add sender to safe list

3. **Email notifications disabled**
   - **Solution:** Contact administrator to enable notifications

---

#### Issue 4: Wrong Item Added to Cart

**Symptoms:**
- Selected wrong material
- Wrong size or specifications

**Solution:**
1. Click [Remove] next to item in cart
2. Go back to Raw Materials tab
3. Click "🔄 Start Over"
4. Select correct item
5. Add to cart again

---

#### Issue 5: Project Number Not Found

**Symptoms:**
- System says project doesn't exist
- Can't submit request

**Possible Causes:**
1. **New project not in database**
   - **Solution:** System will ask for confirmation. Confirm to create new project.

2. **Typo in project number**
   - **Solution:** Double-check project number, correct typo

3. **Project from different system**
   - **Solution:** Verify project number with team

---

#### Issue 6: Request Stuck in Pending

**Symptoms:**
- Request stays Pending for days
- No status change

**Possible Causes:**
1. **Waiting for next processing cycle**
   - **Solution:** Processing happens Tue/Thu at 10 AM. Wait for next cycle.

2. **System issue**
   - **Solution:** Contact operator if still Pending after processing time

---

#### Issue 7: Can't Submit Request (Button Disabled)

**Symptoms:**
- Submit button grayed out
- Can't click submit

**Possible Causes:**
1. **Empty cart**
   - **Solution:** Add at least one item to cart

2. **Invalid quantities**
   - **Solution:** Check all quantities are valid numbers

3. **Missing project numbers**
   - **Solution:** Ensure all items have project numbers assigned

---

#### Issue 8: Date Needed Not Saving

**Symptoms:**
- Selected date disappears
- Date not showing in cart

**Possible Causes:**
1. **Past date selected**
   - **Solution:** Only future dates allowed. Select today or later.

2. **Browser issue**
   - **Solution:** Refresh page, try again

---

### Getting Help

**For Technical Issues:**
- Contact IT Support
- Email: support@yourcompany.com
- Phone: (555) 123-4567

**For Order Questions:**
- Contact Procurement Team
- Email: procurement@yourcompany.com
- Check My Requests tab for operator contact

**For Urgent Matters:**
- Call operator directly
- Reference your request number
- Explain urgency and deadline

---

## Quick Reference Card

### Key Information

**Processing Schedule:**
- Tuesday & Thursday at 10 AM
- Requests submitted before 10 AM will be processed same day
- Requests after 10 AM wait for next cycle

**Request Statuses:**
- 🟡 Pending - Can edit/cancel
- 🔵 In Progress - No edits allowed
- ✅ Ordered - Order placed
- 🎉 Completed - Can reorder

**Important Rules:**
- ✅ Project Number is required
- ✅ Cannot request same item+project if Pending/In Progress
- ✅ Can request same item for different projects
- ✅ Date Needed helps prioritize urgent orders
- ✅ Pending requests can be edited anytime
- ✅ In Progress/Ordered requests cannot be edited

**Contact Information:**
- Technical Support: support@yourcompany.com
- Procurement Team: procurement@yourcompany.com
- Emergency: (555) 123-4567

---

**End of User Manual**

*For operator manual and advanced features, see User_Manual_Operators.md*
