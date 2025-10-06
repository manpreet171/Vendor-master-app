# Phase 3 Operator Dashboard – User Manual (For Operators)

This guide explains how to use the Operator Dashboard to review requests, see recommendations, manage vendor orders, and close out completed bundles. It avoids technical details and focuses on your daily workflow.

 

## 1) Sign In as Operator
- Log in with your operator/admin account.
- You’ll see your name and role in the left sidebar.
- The left sidebar also shows current database connection status.
- Use “🚪 Logout” in the sidebar to exit.

## 2) Operator Tabs
At the top of the Operator Dashboard you’ll see these tabs:
- “📋 User Requests”
- “🎯 Smart Recommendations”
- “📦 Active Bundles”
- “👤 User Management”


## 3) User Requests – See What Needs Ordering
Open `📋 User Requests` to view all pending items from users.

- The page summarizes how many requests and items are waiting.
- Expand each request to see item names, quantities, and the source (BoxHero / Raw Materials).
- Tip: This is an overview; you’ll act on recommendations in the next tab.

## 4) Smart Recommendations – See What to Order
Open `🎯 Smart Recommendations` to see the system’s suggestion of which vendors to contact.

- Click “Generate Smart Recommendations” to analyze pending requests and see proposed orders.
- You’ll see a simple breakdown per suggested order: vendor name, email, phone, and a list of items with quantities.
- Use this as your guide for emailing vendors for quotes.

Note: In production, bundling and quote emails will be sent automatically on a schedule. You remain CC’d on those emails for follow‑ups.

## 5) Active Bundles – Review, Approve, and Track Orders

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
- **Items**: each item with dimensions and quantity
- **Per-user breakdown**: Shows which users requested each item (with project info)
- **Duplicate detection**: Alerts if multiple users requested same item for same project
- **From Requests**: request numbers linked to this bundle for traceability
- **Other vendor options** (single-item bundles): View-only dropdown showing alternative vendors

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

## 8) Notes about Automation (Roadmap)
- Twice a week, the system will bundle requests automatically and email vendors for quotes, CC’ing you on each email.
- You will still close bundles by marking **Completed** once goods arrive.

If you need access or role changes, contact your admin.
