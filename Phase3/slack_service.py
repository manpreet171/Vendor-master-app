"""
Slack Notification Service via Zapier Webhook
Sends notifications to Slack channel for Operation Team

Usage:
    from slack_service import send_slack_notification
    send_slack_notification("Bundle Ready", "Master NY bundle needs review")
"""

import os
import requests
import logging

logger = logging.getLogger("slack_service")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _get_webhook_url():
    """Get Zapier webhook URL from environment or Streamlit secrets"""
    # Try Streamlit secrets first
    try:
        import streamlit as st
        url = st.secrets.get("slack", {}).get("ZAPIER_WEBHOOK_URL")
        if url and isinstance(url, str) and url.strip():
            return url.strip()
    except Exception:
        pass
    
    # Fall back to environment variable
    url = os.environ.get("ZAPIER_WEBHOOK_URL")
    return url.strip() if url and isinstance(url, str) and url.strip() else None


def send_slack_notification(title, message):
    """
    Send notification to Slack via Zapier webhook
    
    Args:
        title: Notification title
        message: Notification message body
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    webhook_url = _get_webhook_url()
    
    if not webhook_url:
        logger.info("Zapier webhook URL not configured; skipping Slack notification")
        return False
    
    try:
        payload = {
            "title": title,
            "message": message
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Slack notification sent: {title}")
            return True
        else:
            logger.warning(f"⚠️ Slack webhook returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Slack webhook timeout (10s)")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send Slack notification: {e}")
        return False
