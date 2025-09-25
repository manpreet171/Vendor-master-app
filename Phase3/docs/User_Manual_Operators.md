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
- The recommendations list vendors with contact details and the exact items to order from each vendor.
- You’ll see a simple breakdown per suggested order: vendor name, email, phone, and a list of items with quantities.
- Use this as your guide for emailing vendors for quotes.

Note: In production, bundling and quote emails will be sent automatically on a schedule. You remain CC’d on those emails for follow‑ups.

## 5) Active Bundles – Track Orders and Close Out
Open `📦 Active Bundles` to manage orders and status.

What you’ll see in each bundle panel:
- **Vendor block**: name, email, phone.
- **Items**: each item with dimensions and quantity. If multiple users requested the same item, you’ll see a per‑user breakdown on the next line.
- **From Requests**: request numbers linked to this bundle for easy traceability.

Helpful visibility (single‑item bundles only):
- **Other vendor options (view‑only)**: For single‑item bundles, you’ll see a dropdown listing other vendors that can provide that same item, including contact info. This is for manual RFQs; it does not change the bundle.

Actions:
- **Approve Bundle**: Confirms the order plan inside the app. (This may be hidden in the fully automated setup.)
- **🏁 Mark as Completed**: Click when the goods have arrived at your stores; this closes the bundle and marks the linked requests as Completed.

## 6) User Management – Admin-Only
Open `👤 User Management` to manage user accounts (admin/operator only).

- **View users**: See status, role, contact details.
- **Edit**: Click “Edit” on a user to open the form.
  - “Full Name”, “Email”, “Department”
  - “Role”: User / Operator
  - “Active” checkbox
  - “New Password (optional)”
  - Buttons: “💾 Save Changes”, “❌ Cancel”
- **Reset Password**: Use the “Reset Password” button (enter a new password first).
- **Delete**: Click “Delete” to remove a user (only when appropriate).
- **Create User**: Fill out the form and click “Create User”.

## 7) Your Day-to-Day Flow
- Check `📋 User Requests` to understand demand.
- Review `🎯 Smart Recommendations` to see which vendors to contact.
- In `📦 Active Bundles`, use vendor details to send RFQs and manage status.
  - For single‑item bundles with multiple suppliers, use the view‑only vendor options as a quick reference when emailing quotes.
- When orders arrive at stores, mark each bundle as **Completed** in `📦 Active Bundles`.

## 8) Notes about Automation (Roadmap)
- Twice a week, the system will bundle requests automatically and email vendors for quotes, CC’ing you on each email.
- You will still close bundles by marking **Completed** once goods arrive.

If you need access or role changes, contact your admin.
