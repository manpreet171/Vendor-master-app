# Email Configuration Guide - Phase 3

## 📧 Two Email Systems Explained

### **System 1: Operator Notifications (Existing)**
**Purpose:** Notify operators/admins about bundling cron results

**Recipients:** Fixed list from secrets (`EMAIL_RECIPIENTS`)

**Example:**
```
To: operator@company.com, admin@company.com
Subject: Smart Bundling: 2 new, 3 updated | 100% coverage
```

---

### **System 2: User Notifications (NEW)**
**Purpose:** Notify individual users about their request status

**Recipients:** Dynamic - from database (`requirements_users.email`)

**Example:**
```
To: john.doe@company.com
Subject: Your Material Request is Being Processed
```

---

## 🔑 Streamlit Cloud Secrets Configuration

### **What to Add:**

Go to: **Your App** → **Settings** → **Secrets**

```toml
[email]
# SMTP Credentials (Required for BOTH systems)
BREVO_SMTP_SERVER = "smtp-relay.brevo.com"
BREVO_SMTP_PORT = "587"
BREVO_SMTP_LOGIN = "your_brevo_email@example.com"
BREVO_SMTP_PASSWORD = "xkeysib-xxxxxxxxxxxxxxxxxxxxx"
EMAIL_SENDER = "noreply@yourdomain.com"
EMAIL_SENDER_NAME = "Procurement Bot"

# For OPERATOR notifications only (bundling cron emails)
EMAIL_RECIPIENTS = "operator@company.com,admin@company.com"

# Optional
EMAIL_CC = ""
EMAIL_REPLY_TO = "procurement@company.com"
```

---

## 📋 What Each Setting Does:

| Setting | Purpose | Used By | Required? |
|---------|---------|---------|-----------|
| **BREVO_SMTP_SERVER** | Brevo SMTP server address | Both systems | ✅ YES |
| **BREVO_SMTP_PORT** | SMTP port (587 for TLS) | Both systems | ✅ YES |
| **BREVO_SMTP_LOGIN** | Your Brevo account email | Both systems | ✅ YES |
| **BREVO_SMTP_PASSWORD** | Brevo SMTP key (NOT account password) | Both systems | ✅ YES |
| **EMAIL_SENDER** | "From" email address | Both systems | ✅ YES |
| **EMAIL_SENDER_NAME** | Display name in "From" field | Both systems | ⚠️ Optional |
| **EMAIL_RECIPIENTS** | Operators/admins email list | Operator notifications ONLY | ⚠️ Optional* |
| **EMAIL_CC** | CC recipients for operator emails | Operator notifications ONLY | ❌ Optional |
| **EMAIL_REPLY_TO** | Reply-to address | Both systems | ❌ Optional |

**Note:** `EMAIL_RECIPIENTS` is optional for user notifications (uses database), but required for operator notifications (bundling cron).

---

## 🎯 Key Differences:

### **Operator Emails:**
```python
# In smart_bundling_cron.py
send_email_via_brevo(
    subject="Smart Bundling Results",
    body_text="...",
    html_body="..."
    # No recipients parameter = uses EMAIL_RECIPIENTS from secrets
)
```

### **User Emails:**
```python
# In user_notifications.py
send_email_via_brevo(
    subject="Your Items Are Ready",
    body_text="...",
    html_body="...",
    recipients=[user['email']]  # ← Dynamic from database!
)
```

---

## 🔍 How User Emails Work:

### **Step 1: Get Request**
```sql
SELECT user_id FROM requirements_orders WHERE req_id = 123
-- Result: user_id = 10
```

### **Step 2: Get User Email**
```sql
SELECT email FROM requirements_users WHERE user_id = 10
-- Result: email = 'john.doe@company.com'
```

### **Step 3: Send Email**
```python
send_email_via_brevo(
    subject="Your Items Are Ready",
    body_text="...",
    html_body="...",
    recipients=['john.doe@company.com']  # ← From database!
)
```

---

## 📝 How to Get Brevo Credentials:

### **1. Create Brevo Account**
- Go to: https://www.brevo.com
- Sign up (free tier available)
- Verify your email

### **2. Get SMTP Credentials**
- Login to Brevo
- Go to: **Settings** → **SMTP & API**
- Find section: **SMTP**

### **3. Copy Credentials**
- **SMTP Server:** `smtp-relay.brevo.com` (always this)
- **SMTP Port:** `587` (always this)
- **SMTP Login:** Your Brevo account email
- **SMTP Password:** Click "Generate a new SMTP key" and copy it

⚠️ **Important:** The SMTP password is NOT your Brevo account password! It's a special key.

### **4. Verify Sender Email**
- Go to: **Senders & IP** → **Senders**
- Add your sender email (e.g., `noreply@yourdomain.com`)
- Verify it (Brevo will send verification email)

---

## ✅ Testing Your Configuration:

### **Test 1: Check Secrets**
```python
# In Streamlit app
import streamlit as st

# Should show your values (not errors)
st.write(st.secrets["email"]["BREVO_SMTP_SERVER"])
st.write(st.secrets["email"]["EMAIL_SENDER"])
```

### **Test 2: Test Operator Email**
```python
# Run bundling cron manually
# Should send email to EMAIL_RECIPIENTS
```

### **Test 3: Test User Email**
```python
# Submit a request as a user
# Wait for bundling cron to run
# User should receive "In Progress" email
```

---

## 🚨 Common Issues:

### **Issue 1: "Email env vars not fully configured"**
**Cause:** Missing SMTP credentials in secrets

**Fix:** Add all required secrets to Streamlit Cloud

---

### **Issue 2: "Authentication failed"**
**Cause:** Wrong SMTP password

**Fix:** Generate new SMTP key in Brevo and update `BREVO_SMTP_PASSWORD`

---

### **Issue 3: "Sender not verified"**
**Cause:** Email sender not verified in Brevo

**Fix:** Go to Brevo → Senders → Add and verify your sender email

---

### **Issue 4: User not receiving emails**
**Cause:** User has no email in database

**Fix:** Check `requirements_users` table - ensure user has valid email address

```sql
SELECT user_id, username, email FROM requirements_users WHERE user_id = 10
```

---

### **Issue 5: Operator emails work but user emails don't**
**Cause:** User email might be NULL or invalid in database

**Fix:** 
```sql
-- Check user email
SELECT email FROM requirements_users WHERE user_id = ?

-- Update if needed
UPDATE requirements_users SET email = 'user@company.com' WHERE user_id = ?
```

---

## 📊 Email Flow Summary:

### **Operator Notifications:**
```
Bundling Cron Runs
    ↓
Reads EMAIL_RECIPIENTS from secrets
    ↓
Sends to: operator@company.com, admin@company.com
```

### **User Notifications:**
```
Request Status Changes
    ↓
Gets user_id from request
    ↓
Queries database for user email
    ↓
Sends to: john.doe@company.com (from database)
```

---

## 🎯 Quick Checklist:

**For Streamlit Cloud:**
- [ ] Add `[email]` section to secrets
- [ ] Add BREVO_SMTP_SERVER
- [ ] Add BREVO_SMTP_PORT
- [ ] Add BREVO_SMTP_LOGIN
- [ ] Add BREVO_SMTP_PASSWORD
- [ ] Add EMAIL_SENDER
- [ ] Add EMAIL_SENDER_NAME
- [ ] Add EMAIL_RECIPIENTS (for operator emails)

**For Brevo:**
- [ ] Create Brevo account
- [ ] Generate SMTP key
- [ ] Verify sender email
- [ ] Test sending email

**For Database:**
- [ ] Ensure users have email addresses in `requirements_users` table
- [ ] Verify emails are valid

---

## 📞 Support:

If emails still don't work:
1. Check Streamlit Cloud logs for errors
2. Check Brevo dashboard for failed sends
3. Verify database has user emails
4. Test SMTP credentials manually

---

**End of Email Configuration Guide**
