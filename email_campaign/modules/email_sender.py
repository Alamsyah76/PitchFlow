"""
Email Sender — SMTP send + IMAP copy to Sent folder
=====================================================
Single responsibility: transmit email via SMTP and save copy to Sent.
Supports file attachments via `attachments` param (list of file paths).
"""
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from pathlib import Path


def send_email(smtp_config, to_email, to_name, html_body, subject="", attachments=None, cc_email=""):
    """Kirim email via SMTP + simpan ke folder Sent via IMAP.
    
    Args:
        smtp_config: dict with SMTP connection details
        to_email: recipient email
        to_name: recipient name
        html_body: HTML email body
        subject: email subject
        attachments: list of file paths to attach, or None
        cc_email: CC recipient email (optional)
    """
    SENDER_EMAIL = smtp_config['sender_email']

    # Outer mixed — supports both HTML body and attachments
    msg = MIMEMultipart("mixed")
    msg["From"] = f"{smtp_config['sender_name']} <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject or ""
    if cc_email:
        msg["Cc"] = cc_email
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body, "html"))
    msg.attach(alt)

    # Attachments
    if attachments:
        for filepath in attachments:
            p = Path(filepath)
            if not p.exists():
                continue
            with open(p, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{p.name}"'
            )
            msg.attach(part)

    port = smtp_config["port"]
    raw = msg.as_string()

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_config["host"], port)
        else:
            server = smtplib.SMTP(smtp_config["host"], port)
            server.starttls()

        server.login(smtp_config["username"], smtp_config["password"])
        server.sendmail(SENDER_EMAIL, [to_email], raw)
        server.quit()

        _save_to_sent(raw, smtp_config)

        return True, ""
    except Exception as e:
        return False, str(e)


def _save_to_sent(raw_email, smtp_config=None):
    """Simpan salinan email ke folder Sent via IMAP."""
    if smtp_config:
        host = os.environ.get("IMAP_HOST", smtp_config.get("host", "mail.example.com"))
        port = int(os.environ.get("IMAP_PORT", 993))
        user = smtp_config.get("username", os.environ.get("SMTP_USERNAME", ""))
        pw = smtp_config.get("password", os.environ.get("SMTP_PASSWORD", ""))
    else:
        host = os.environ.get("IMAP_HOST", "mail.sendquick.com")
        port = int(os.environ.get("IMAP_PORT", 993))
        user = os.environ.get("SMTP_USERNAME", "")
        pw = os.environ.get("SMTP_PASSWORD", "")

    if not user or not pw:
        return False
    try:
        conn = imaplib.IMAP4_SSL(host, port)
        conn.login(user, pw)
        for folder in ('INBOX.Sent', 'INBOX.mail.virtual.sent',
                       'Sent', 'Sent Items', '[Gmail]/Sent Mail'):
            try:
                conn.append(folder, '\\Seen', None, raw_email.encode('utf-8'))
                conn.logout()
                return True
            except imaplib.IMAP4.error:
                continue
        conn.logout()
        return False
    except Exception:
        return False
