# Phase 3 Operation Team Dashboard – Complete User Manual
## For Operation Team Members

**Version:** 3.0  
**Last Updated:** November 11, 2025

---

This comprehensive guide explains how to use the Operation Team Dashboard to review and approve vendor bundles, understand email notifications, and make informed approval decisions.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Your Role in the Process](#2-your-role-in-the-process)
3. [Email Notifications](#3-email-notifications)
4. [Operation Team Dashboard](#4-operation-team-dashboard)
5. [Bundle Review Process](#5-bundle-review-process)
6. [Approval Decision Guide](#6-approval-decision-guide)
7. [Rejection Process](#7-rejection-process)
8. [History Tracking](#8-history-tracking)
9. [All Possible Scenarios](#9-all-possible-scenarios)
10. [Troubleshooting](#10-troubleshooting)
11. [Best Practices](#11-best-practices)
12. [Quick Reference](#12-quick-reference)

---

## 1) Getting Started

### Sign In as Operation Team Member

- Open the app URL: https://item-requirement-app-sdgny.streamlit.app/
- Enter your username and password
- Click "Login"
- You'll see your name and role in the left sidebar
- Use "🚪 Logout" in the sidebar to exit

### Your Dashboard

After login, you'll see:
- **📋 Reviewed Bundles** - Bundles awaiting your approval
- **📜 History** - Past approvals and rejections

---

## 2) Your Role in the Process

### What You Do

You are the **final approval authority** before orders are placed with vendors. Your responsibilities include:

- ✅ Reviewing bundles that operators have prepared
- ✅ Verifying vendor selection and pricing
- ✅ Checking budget and authorization
- ✅ Approving bundles for ordering
- ✅ Rejecting bundles that need changes

### Complete Process Flow

```
USER → SYSTEM (Cron) → OPERATOR → YOU (Operation Team) → VENDOR → COMPLETION
```

**Your Position in the Flow:**

1. **USER** - Submits material requests
2. **SYSTEM** - Groups requests into vendor bundles (2x/week: Tue/Thu)
3. **OPERATOR** - Reviews bundles and marks as "Reviewed"
4. **YOU** - Receive email notification
5. **YOU** - Review bundle details
6. **YOU** - Approve or Reject
7. **OPERATOR** - Places order (if approved)
8. **VENDOR** - Ships items
9. **OPERATOR** - Marks complete when items arrive

---

## 3) Email Notifications

### When You Get Emails

**Trigger:** When an operator marks a bundle as "Reviewed"

**Frequency:** Immediate notification (no delays)

**Recipients:** ALL active Operation Team members receive the same email

---

### Email Content

**Subject Line:**
```
🟢 Bundle Reviewed - Awaiting Approval: RM-2025-11-11-001
```

**What's Included:**

#### 1. Bundle Details
- Bundle ID (e.g., RM-2025-11-11-001)
- Vendor name
- Vendor email and phone
- Reviewed timestamp

#### 2. Items List
- All items with quantities
- Size specifications
- Total item count and pieces

**Example:**
```
ITEMS:
------
• ACRYLITE Non-glare P99 (48 x 96 x 0.125) - 5 pcs
• DURA-CAST IM-7328 (3/16" 4x8 WHITE PM*) - 2 pcs

Total: 2 items, 7 pieces
```

#### 3. User Requests
- Request numbers
- User names
- Number of items per request
- User notes (if provided)
- Date needed with urgency indicators

**Example:**
```
USER REQUESTS:
--------------
• REQ-2025-001 (John Smith) - 3 items
  📝 Notes: "Urgent - needed for client presentation"
  📅 Date Needed: 2025-11-15 (⚠️ 4 days!)

• REQ-2025-002 (Jane Doe) - 2 items
  📅 Date Needed: 2025-11-20
```

**Urgency Indicators:**
- ⚠️ Shows if items needed within 5 days
- Displays exact days remaining

#### 4. Bundle History (if applicable)
- Creation date
- Merge information (if bundle was updated with new items)
- Previous rejection info (if bundle was rejected before)

**Example:**
```
BUNDLE HISTORY:
---------------
✅ Created: 2025-11-08 at 10:00 AM
🔄 Updated 1 time(s) - Last: 2025-11-09 at 3:00 PM
   Merge Reason: New requests added (2 items from 1 user)

⚠️ Previously Rejected: 2025-11-09 at 2:00 PM
   Reason: "Budget exceeded - get better quotes"
   Rejected by: Sarah Lee
```

#### 5. Action Link
- Direct link to dashboard
- Click to log in and approve/reject

---

### Email Format

**Two Versions Provided:**
1. **Plain Text** - For basic email clients
2. **HTML** - Styled with colors, tables, and urgency highlights

**Both versions contain the same information.**

---

### What to Do When You Get an Email

1. **Read the email** - Review all details
2. **Check urgency** - Look for ⚠️ indicators
3. **Review history** - Check if previously rejected
4. **Click dashboard link** - Go to the system
5. **Log in** - Use your credentials
6. **Review bundle** - See full details
7. **Make decision** - Approve or Reject

---

## 4) Operation Team Dashboard

### Dashboard Overview

**Two Main Views:**

1. **📋 Reviewed Bundles** (Default)
   - Shows all bundles awaiting your approval
   - Displays count of pending bundles
   - Provides approve/reject actions

2. **📜 History**
   - Shows past 30 days of approvals and rejections
   - Displays who approved/rejected and when
   - Useful for tracking and auditing

---

### Reviewed Bundles View

**What You See:**

#### Bundle Header
- 📦 Bundle name (e.g., RM-2025-11-11-001)
- Vendor name
- Reviewed timestamp
- Status badge: 🟢 Reviewed

#### Previous Rejection Warning (if applicable)
- Red warning box
- Rejection date
- Rejection reason
- Who rejected it

**Example:**
```
⚠️ REJECTED BY OPERATION TEAM
Rejected on: 2025-11-09 14:30
Reason: Budget exceeded - get better quotes
```

#### User Requests Section
- Shows all user requests in this bundle
- User names and request numbers
- Item counts per request
- User notes (if provided)

**Example:**
```
📋 User Requests in this Bundle:

👤 REQ-2025-001 (John Smith) - 3 item(s)
📝 Urgent - needed for client presentation

👤 REQ-2025-002 (Jane Doe) - 2 item(s)
(No notes)
```

#### Bundle Items (Expandable)
- Click "📋 View Bundle Items" to expand
- Shows detailed table with:
  - Item names
  - Sizes
  - Quantities per user
  - Project numbers
  - Date needed
  - Total quantities

**Table Format:**
| Item | User | Project | Date Needed | Quantity |
|------|------|---------|-------------|----------|
| ACRYLITE Non-glare P99 (48 x 96 x 0.125) | John Smith | P-2025-001 | 2025-11-15 | 3 |
| ACRYLITE Non-glare P99 (48 x 96 x 0.125) | Jane Doe | P-2025-002 | 2025-11-20 | 2 |
| **TOTAL** | | | | **5** |

#### Action Buttons
- ✅ **Approve** (Green button)
- ❌ **Reject** (Gray button)

---

## 5) Bundle Review Process

### Step-by-Step Review

#### Step 1: Check Email Notification
- Read email summary
- Note urgency indicators
- Check bundle history

#### Step 2: Log In to Dashboard
- Click dashboard link in email
- Enter credentials
- Navigate to "📋 Reviewed Bundles"

#### Step 3: Review Bundle Details
- Read vendor information
- Check user requests and notes
- Review urgency (date needed)
- Expand bundle items table
- Check quantities and specifications

#### Step 4: Verify Information
- ✅ Is vendor correct?
- ✅ Are quantities reasonable?
- ✅ Is budget available?
- ✅ Are urgent items prioritized?
- ✅ Any duplicate items?

#### Step 5: Check History
- Was this bundle rejected before?
- If yes, were issues addressed?
- Is rejection reason still valid?

#### Step 6: Make Decision
- **Approve** - If everything looks good
- **Reject** - If changes needed

---

## 6) Approval Decision Guide

### When to APPROVE ✅

**Approve if:**
- ✅ Vendor is correct and authorized
- ✅ Quantities match user requests
- ✅ Budget is available
- ✅ No duplicate items
- ✅ Urgent items are prioritized
- ✅ Previous rejection issues resolved (if applicable)
- ✅ All information is complete

**What Happens After Approval:**
1. Bundle status changes to "Approved"
2. Bundle moves to operator's "Approved Bundles" list
3. Operator can now place order with vendor
4. Users are notified (status: In Progress → Ordered)

---

### When to REJECT ❌

**Reject if:**
- ❌ Wrong vendor selected
- ❌ Budget not available
- ❌ Quantities seem incorrect
- ❌ Duplicate items found
- ❌ Better pricing available elsewhere
- ❌ Vendor not authorized
- ❌ Missing critical information
- ❌ Previous rejection issues not resolved

**What Happens After Rejection:**
1. Bundle status changes to "Rejected"
2. Bundle moves back to operator
3. Operator sees rejection reason
4. Operator must fix issues and re-review
5. Bundle comes back to you for approval

---

## 7) Rejection Process

### How to Reject a Bundle

#### Step 1: Click "❌ Reject" Button
- Red rejection dialog appears

#### Step 2: Enter Rejection Reason
- **REQUIRED** - Must provide reason
- Be specific and clear
- Explain what needs to be fixed

**Good Rejection Reasons:**
- ✅ "Budget exceeded - get quotes from 2 other vendors"
- ✅ "Wrong vendor - use ABC Plastics instead of XYZ"
- ✅ "Quantities seem too high - verify with users"
- ✅ "Duplicate items found - consolidate before ordering"
- ✅ "Missing PO number - need authorization first"

**Bad Rejection Reasons:**
- ❌ "No" (too vague)
- ❌ "Wrong" (doesn't explain what's wrong)
- ❌ "Fix it" (doesn't say what to fix)

#### Step 3: Confirm Rejection
- Click "Confirm Rejection"
- Bundle is rejected
- Operator receives notification

---

### What Operator Sees After Rejection

**Operator Dashboard Shows:**
- 🔴 Red warning box
- Rejection date and time
- Your rejection reason
- Who rejected it (your name)

**Operator Actions:**
- Fix the issues you mentioned
- Re-review the bundle
- Mark as "Reviewed" again
- Bundle comes back to you

---

## 8) History Tracking

### Viewing History

**How to Access:**
- Click "📜 History" in sidebar
- Shows last 30 days by default

**What You See:**
- Bundle name
- Vendor name
- Action (Approved or Rejected)
- Date and time
- Who took action
- Rejection reason (if rejected)

**Use Cases:**
- Track approval patterns
- Review past decisions
- Audit trail
- Check rejection reasons

---

## 9) All Possible Scenarios

### Scenario 1: Simple Approval

**Situation:**
- Bundle looks good
- No issues found
- Budget available

**Your Action:**
1. Review bundle details
2. Click "✅ Approve"
3. Confirmation message appears
4. Bundle moves to operator

**Result:** ✅ Approved

---

### Scenario 2: Budget Exceeded

**Situation:**
- Bundle total exceeds budget
- Need better pricing

**Your Action:**
1. Click "❌ Reject"
2. Enter reason: "Budget exceeded - get quotes from 2 other vendors for comparison"
3. Confirm rejection

**Result:** ❌ Rejected

**What Happens Next:**
- Operator contacts other vendors
- Gets better quotes
- Re-reviews bundle
- Sends back to you

---

### Scenario 3: Previously Rejected Bundle

**Situation:**
- Bundle was rejected before
- Operator fixed issues
- Bundle is back for approval

**Your Action:**
1. Check rejection warning box
2. Read previous rejection reason
3. Verify issues were fixed
4. If fixed: Approve ✅
5. If not fixed: Reject again ❌

**Result:** Depends on whether issues were resolved

---

### Scenario 4: Urgent Items

**Situation:**
- Email shows ⚠️ urgency indicators
- Items needed within 5 days

**Your Action:**
1. Prioritize this bundle
2. Review quickly but thoroughly
3. If approved, operator can order immediately
4. If rejected, provide clear reason so operator can fix quickly

**Result:** Fast turnaround for urgent items

---

### Scenario 5: Duplicate Items

**Situation:**
- Same item appears multiple times
- Could be consolidated

**Your Action:**
1. Click "❌ Reject"
2. Enter reason: "Duplicate items found - consolidate ACRYLITE orders into single line"
3. Confirm rejection

**Result:** ❌ Rejected

**What Happens Next:**
- Operator consolidates items
- Re-reviews bundle
- Sends back to you

---

### Scenario 6: Wrong Vendor

**Situation:**
- System selected vendor A
- Should use vendor B

**Your Action:**
1. Click "❌ Reject"
2. Enter reason: "Wrong vendor - use ABC Plastics instead of XYZ Corp (better pricing)"
3. Confirm rejection

**Result:** ❌ Rejected

**What Happens Next:**
- Operator changes vendor
- Re-reviews bundle
- Sends back to you

---

### Scenario 7: Multiple Bundles at Once

**Situation:**
- 5 bundles awaiting approval
- All from different vendors

**Your Action:**
1. Review each bundle individually
2. Approve good ones ✅
3. Reject problematic ones ❌
4. Work through list systematically

**Result:** Mixed approvals and rejections

**Tip:** Handle urgent bundles first (check email for ⚠️)

---

### Scenario 8: Missing Information

**Situation:**
- User notes are unclear
- Quantities seem wrong
- Need clarification

**Your Action:**
1. Click "❌ Reject"
2. Enter reason: "Need clarification on quantities - verify with John Smith (REQ-2025-001)"
3. Confirm rejection

**Result:** ❌ Rejected

**What Happens Next:**
- Operator contacts user
- Gets clarification
- Updates bundle
- Re-reviews and sends back

---

## 10) Troubleshooting

### Problem: Not Receiving Emails

**Possible Causes:**
- Email not set in your user profile
- Email in spam folder
- User account not active
- Role not set to "Operation"

**Solutions:**
1. Check spam/junk folder
2. Contact Master user to verify:
   - Your email is correct
   - Your account is active
   - Your role is "Operation"
3. Add sender to safe senders list

---

### Problem: Can't See Reviewed Bundles

**Possible Causes:**
- No bundles awaiting approval
- Already approved/rejected all bundles
- Operator hasn't reviewed any bundles yet

**Solutions:**
1. Check "📜 History" to see recent actions
2. Wait for operator to review bundles
3. Contact operator to confirm status

---

### Problem: Approve Button Not Working

**Possible Causes:**
- Network issue
- Database connection problem
- Bundle already approved by another team member

**Solutions:**
1. Refresh the page (F5)
2. Log out and log back in
3. Check internet connection
4. Contact system administrator

---

### Problem: Rejection Reason Not Saving

**Possible Causes:**
- Rejection reason field is empty
- Network issue during save

**Solutions:**
1. Make sure to enter rejection reason
2. Reason must be at least 5 characters
3. Try again with clear reason
4. Refresh page if needed

---

### Problem: Bundle Keeps Coming Back

**Possible Causes:**
- Operator didn't fix the issues
- New issues found after fixing old ones
- Miscommunication about what needs fixing

**Solutions:**
1. Be very specific in rejection reason
2. List all issues at once (don't reject multiple times)
3. Contact operator directly if needed
4. Provide examples of what you want

---

## 11) Best Practices

### For Efficient Approvals

#### 1. Check Emails Regularly
- ✅ Check email 2-3 times per day
- ✅ Respond to urgent bundles (⚠️) within 2 hours
- ✅ Respond to normal bundles within 24 hours

#### 2. Review Thoroughly
- ✅ Read all user notes
- ✅ Check date needed
- ✅ Verify vendor information
- ✅ Expand bundle items table
- ✅ Check for duplicates

#### 3. Be Specific in Rejections
- ✅ Explain exactly what's wrong
- ✅ Provide clear fix instructions
- ✅ Give examples if needed
- ✅ List all issues at once

#### 4. Prioritize Urgency
- ✅ Handle ⚠️ urgent bundles first
- ✅ Check date needed
- ✅ Fast-track critical items
- ✅ Communicate delays if needed

#### 5. Track History
- ✅ Review past rejections
- ✅ Check approval patterns
- ✅ Learn from previous decisions
- ✅ Maintain consistency

---

### Communication Guidelines

#### With Operators

**DO:**
- ✅ Be clear and specific in rejection reasons
- ✅ Provide actionable feedback
- ✅ Acknowledge good work
- ✅ Communicate urgency

**DON'T:**
- ❌ Use vague rejection reasons
- ❌ Reject without explanation
- ❌ Delay urgent approvals
- ❌ Approve without reviewing

#### With Users (Indirect)

**Remember:**
- Your decisions affect user timelines
- Urgent items need fast turnaround
- Clear rejections = faster fixes = happier users
- Your approval starts the ordering process

---

### Quality Checks

**Before Approving:**
- [ ] Vendor is correct and authorized
- [ ] Quantities match user requests
- [ ] Budget is available
- [ ] No duplicate items
- [ ] Urgent items prioritized
- [ ] Previous issues resolved (if applicable)
- [ ] All information complete

**Before Rejecting:**
- [ ] Identified specific issues
- [ ] Written clear rejection reason
- [ ] Listed all problems at once
- [ ] Provided fix instructions
- [ ] Considered urgency

---

## 12) Quick Reference

### Email Notification Summary

| Element | What It Means |
|---------|---------------|
| 🟢 Bundle Reviewed | Bundle ready for your approval |
| ⚠️ X days! | Item needed within 5 days (urgent) |
| 📝 Notes | User provided special instructions |
| 🔄 Updated | Bundle was merged with new items |
| ⚠️ Previously Rejected | Bundle was rejected before |

---

### Dashboard Actions

| Button | Action | Result |
|--------|--------|--------|
| ✅ Approve | Approve bundle | Operator can place order |
| ❌ Reject | Reject bundle | Operator must fix issues |
| 📋 View Bundle Items | Expand details | See full item breakdown |
| 📜 History | View past actions | See approvals/rejections |

---

### Status Flow

```
🟡 Pending (User submitted)
    ↓
🔵 In Progress (System bundled)
    ↓
🟢 Reviewed (Operator reviewed)
    ↓
YOU APPROVE ✅ → 🟢 Approved → Operator orders
    OR
YOU REJECT ❌ → 🔴 Rejected → Operator fixes → Back to Reviewed
```

---

### Common Rejection Reasons

| Issue | Rejection Reason Example |
|-------|--------------------------|
| Budget | "Budget exceeded - get quotes from 2 other vendors" |
| Wrong Vendor | "Wrong vendor - use ABC Plastics instead" |
| Quantities | "Quantities seem high - verify with users" |
| Duplicates | "Duplicate items - consolidate before ordering" |
| Missing Info | "Need PO number for authorization" |
| Pricing | "Get better pricing - current quote too high" |

---

### Contact Information

**For Technical Issues:**
- Contact: System Administrator
- Email: [Your IT Support Email]

**For Process Questions:**
- Contact: Operations Manager
- Email: [Your Operations Email]

**For Urgent Approvals:**
- Contact: Operator Team
- Email: [Operator Team Email]

---

### Processing Schedule

**Bundling Runs:**
- Tuesday: 6:30 PM UTC (12:00 AM IST / 2:30 PM EDT)
- Thursday: 6:30 PM UTC (12:00 AM IST / 2:30 PM EDT)

**Expected Timeline:**
- Operator reviews: Within 24 hours of bundling
- Your approval: Within 24 hours of review
- Order placement: Within 24 hours of approval
- Delivery: Vendor-dependent (typically 3-7 days)

---

### Important Rules

**DO:**
- ✅ Review bundles within 24 hours
- ✅ Prioritize urgent items (⚠️)
- ✅ Be specific in rejection reasons
- ✅ Check bundle history before deciding
- ✅ Verify vendor and budget

**DON'T:**
- ❌ Approve without reviewing
- ❌ Reject without clear reason
- ❌ Ignore urgent indicators
- ❌ Delay critical approvals
- ❌ Approve duplicate items

---

## Summary

As an Operation Team member, you are the **final checkpoint** before orders are placed with vendors. Your role is critical in ensuring:

- ✅ Correct vendors are used
- ✅ Budget is managed properly
- ✅ Quantities are accurate
- ✅ Urgent items are prioritized
- ✅ Quality standards are maintained

**Your decisions directly impact:**
- User satisfaction
- Budget management
- Vendor relationships
- Delivery timelines
- Overall efficiency

**Remember:**
- Check emails regularly
- Review thoroughly
- Be specific in rejections
- Prioritize urgency
- Track your decisions

---

**Thank you for being part of the Operation Team!** 🎯

Your careful review and timely approvals keep the procurement process running smoothly and ensure users get the materials they need when they need them.

---

**Questions or Issues?**
Contact your system administrator or operations manager for assistance.

---

**End of Manual**
