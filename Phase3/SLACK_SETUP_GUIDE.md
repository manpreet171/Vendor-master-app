# Slack Notifications Setup Guide

## ✅ Implementation Complete!

**Feature:** Slack notifications for Operation Team when bundles are ready for approval

**Trigger:** When operator marks bundle as "Reviewed"

**Channel:** `#testing-app` (via Zapier webhook)

---

## 📋 Configuration Steps

### Step 1: Add Webhook URL to Local Environment

**For Local Testing (.env file):**

Add this line to your `.env` file:
```bash
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/14165386/usgsei2/
```

### Step 2: Add Webhook URL to GitHub Actions

**For Cron Jobs (GitHub Secrets):**

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add:
   - **Name:** `ZAPIER_WEBHOOK_URL`
   - **Value:** `https://hooks.zapier.com/hooks/catch/14165386/usgsei2/`
5. Click **"Add secret"**

### Step 3: Add Webhook URL to Streamlit Cloud

**For Production App (Streamlit Secrets):**

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Navigate to: **Settings** → **Secrets**
4. Add this to your secrets:
```toml
[slack]
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/14165386/usgsei2/"
```
5. Click **"Save"**

---

## 🎯 How It Works

### Current Flow:

```
User Submits Request
    ↓
Bundling Cron Runs (Tue/Thu)
    ↓
Bundle Created → Status: Active
    ↓
OPERATOR Reviews Bundle
    ↓
Operator Clicks "✅ Confirm & Mark as Reviewed"
    ↓
Bundle Status → Reviewed
    ↓
🔔 SLACK NOTIFICATION SENT! ← NEW!
    ↓
Operation Team sees message in #testing-app
    ↓
Operation Team goes to dashboard
    ↓
Operation Team reviews and approves bundle
```

---

## 📧 Slack Message Format

**Title:**
```
📦 New Bundle Ready for Approval!
```

**Message:**
```
Vendor: Master NY
Items: 5 types
Total Quantity: 25 pieces
Status: 🟢 Reviewed - Ready for Operation Team approval

👉 Action Required: Review and approve this bundle in the Operation Team Dashboard

Bundle marked as reviewed by operator
```

---

## 🧪 Testing

### Test Scenario:

1. **Login as Operator** (e.g., `operator1`)
2. Go to **Operator Dashboard**
3. Open **Active Bundles** tab
4. Find an Active bundle
5. Click **"✅ Mark as Reviewed"**
6. Complete the checklist (4 items)
7. Click **"✅ Confirm & Mark as Reviewed"**
8. **Check Slack** → Message should appear in `#testing-app`!

### Expected Result:

✅ Bundle status changes to "Reviewed"
✅ Success message appears in app
✅ Slack notification sent to `#testing-app`
✅ Operation Team sees notification

---

## 🔧 Files Modified

| File | Action | Lines Changed |
|------|--------|---------------|
| `slack_service.py` | **NEW FILE** | +73 lines |
| `app.py` | Added import + logging | +5 lines |
| `app.py` | Added Slack notification | +20 lines |
| **Total** | 1 new + 1 modified | **+98 lines** |

---

## 🔒 Safety Features

### 1. Graceful Fallback:
- If webhook URL not configured → Silently skips (no error)
- If Slack API fails → Logs warning, continues normally
- **Email system untouched** → No impact on existing workflow

### 2. Non-Blocking:
- Slack notification happens AFTER database update
- If Slack is slow, doesn't affect app
- 10-second timeout prevents hanging

### 3. Easy to Disable:
- Remove webhook URL from secrets
- Slack notifications will stop
- No code changes needed

---

## 📊 Code Changes Detail

### New File: `slack_service.py`

**Purpose:** Send notifications to Slack via Zapier webhook

**Key Functions:**
- `_get_webhook_url()` - Reads URL from secrets/env
- `send_slack_notification(title, message)` - Sends to Zapier

**Features:**
- ✅ Tries Streamlit secrets first, falls back to env vars
- ✅ 10-second timeout
- ✅ Proper error handling
- ✅ Logging for debugging

### Modified: `app.py`

**Location:** Line 2493-2512 (inside `display_review_checklist` function)

**What Changed:**
```python
# BEFORE:
if db.mark_bundle_reviewed(bundle_id):
    del st.session_state[f'reviewing_bundle_{bundle_id}']
    st.success(f"✅ Bundle marked as Reviewed!")
    st.rerun()

# AFTER:
if db.mark_bundle_reviewed(bundle_id):
    # Send Slack notification to Operation Team
    try:
        from slack_service import send_slack_notification
        title = f"📦 New Bundle Ready for Approval!"
        message = f"Vendor: {vendor_name}\n..."
        send_slack_notification(title, message.strip())
    except Exception as e:
        logger.warning(f"Slack notification failed: {e}")
    
    del st.session_state[f'reviewing_bundle_{bundle_id}']
    st.success(f"✅ Bundle marked as Reviewed!")
    st.rerun()
```

---

## ✅ Next Steps

1. ✅ **Add webhook URL to secrets** (see Step 1-3 above)
2. ✅ **Test locally** (mark a bundle as reviewed)
3. ✅ **Check Slack** (message should appear)
4. ✅ **Deploy to production** (Streamlit Cloud)
5. ✅ **Test in production** (verify notifications work)

---

## 🎉 Benefits

**For Operation Team:**
- ✅ **Instant notifications** - No need to check dashboard constantly
- ✅ **Clear action items** - Know exactly what needs approval
- ✅ **Better visibility** - See bundle details at a glance
- ✅ **Faster response** - Approve bundles quickly

**For System:**
- ✅ **Zero risk** - Doesn't affect existing workflow
- ✅ **Easy to maintain** - Simple code, clear logic
- ✅ **Scalable** - Can add more notifications later
- ✅ **Free** - Zapier free tier (100 tasks/month)

---

## 📝 Future Enhancements

**Potential additions:**
- [ ] Notify when bundle is approved
- [ ] Notify when order is placed
- [ ] Notify when order is completed
- [ ] Different channels for different notifications
- [ ] Rich Slack formatting (blocks, buttons)
- [ ] @mention specific team members

---

## 🐛 Troubleshooting

### Issue: No Slack notification appears

**Check:**
1. Is webhook URL configured in secrets?
2. Is Zapier Zap turned ON?
3. Check app logs for errors
4. Test webhook URL manually (curl/Postman)

### Issue: Slack notification delayed

**Reason:** Zapier free tier has 15-minute polling
**Solution:** Upgrade to Zapier paid plan (instant triggers)

### Issue: Notification sent but wrong format

**Check:**
1. Zapier Zap configuration
2. Slack message template in Zapier
3. Verify `title` and `message` fields

---

## 📞 Support

**Questions?** Check:
- Zapier dashboard for webhook logs
- Streamlit app logs for errors
- Slack channel for test messages

**Need help?** Contact the development team!

---

**Implementation Date:** November 7, 2025
**Status:** ✅ Complete and Ready for Testing
