"""
Brevo SMTP email service for Phase 3 cron notifications
- Reads SMTP settings from environment variables
- Sends multipart (plain + HTML) messages

Required envs (in GitHub Actions -> repository secrets):
  BREVO_SMTP_SERVER
  BREVO_SMTP_PORT           (e.g., 587)
  BREVO_SMTP_LOGIN
  BREVO_SMTP_PASSWORD
  EMAIL_SENDER              (e.g., noreply@yourdomain.com)
  EMAIL_SENDER_NAME         (optional, default: 'Procurement Bot')
  EMAIL_RECIPIENTS          (comma-separated list)
Optional envs:
  EMAIL_CC                  (comma-separated list)
  EMAIL_REPLY_TO
"""
from __future__ import annotations
import os
import smtplib
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("email_service")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.environ.get(name, default)
    return val if val is None or (isinstance(val, str) and val.strip() != "") else default


essential_envs = [
    "BREVO_SMTP_SERVER",
    "BREVO_SMTP_PORT",
    "BREVO_SMTP_LOGIN",
    "BREVO_SMTP_PASSWORD",
    "EMAIL_SENDER",
    "EMAIL_RECIPIENTS",
]


def _env_configured() -> bool:
    for key in essential_envs:
        if not _get_env(key):
            return False
    return True


def send_email_via_brevo(subject: str, body_text: str, html_body: Optional[str] = None) -> bool:
    """Send email via Brevo SMTP using environment variables. Returns True on success."""
    server = _get_env('BREVO_SMTP_SERVER')
    port_str = _get_env('BREVO_SMTP_PORT', '587')
    login = _get_env('BREVO_SMTP_LOGIN')
    password = _get_env('BREVO_SMTP_PASSWORD')
    sender = _get_env('EMAIL_SENDER')
    sender_name = _get_env('EMAIL_SENDER_NAME', 'Procurement Bot')
    recipients_str = _get_env('EMAIL_RECIPIENTS')
    cc_str = _get_env('EMAIL_CC', '')
    reply_to = _get_env('EMAIL_REPLY_TO')

    if not all([server, port_str, login, password, sender, recipients_str]):
        logger.info("Email env vars not fully configured; skipping email send.")
        return False

    try:
        port = int(port_str)
    except Exception:
        port = 587

    recipients = [r.strip() for r in (recipients_str or '').split(',') if r.strip()]
    cc_list = [c.strip() for c in (cc_str or '').split(',') if c.strip()]
    all_rcpts = recipients + cc_list
    if not recipients:
        logger.info("No recipients configured; skipping email send.")
        return False

    # Build message
    msg = MIMEMultipart('alternative')
    safe_text = (body_text or "").replace('—', '-').replace('·', '-')
    msg.attach(MIMEText(safe_text, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body.replace('·', '-'), 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(safe_text, 'plain', 'utf-8'))

    msg['Subject'] = subject
    msg['From'] = f"{sender_name} <{sender}>"
    msg['To'] = ", ".join(recipients)
    if cc_list:
        msg['Cc'] = ", ".join(cc_list)
    if reply_to:
        msg['Reply-To'] = reply_to

    try:
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(login, password)
        smtp.sendmail(sender, all_rcpts if all_rcpts else recipients, msg.as_string())
        smtp.quit()
        logger.info(f"Email sent to: {', '.join(all_rcpts if all_rcpts else recipients)}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via Brevo: {e}")
        return False
