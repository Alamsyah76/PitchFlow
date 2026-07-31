"""
Bounce Detector — scan IMAP inbox for Mail Delivery Failure notifications
==========================================================================
Single responsibility: connect to inbox, find bounce/NDR emails, extract
failed recipient addresses.
"""
import imaplib
import os
import re
from email.header import decode_header

BOUNCE_SUBJECT_KEYWORDS = [
    "mail delivery failed", "undeliverable", "undelivered mail",
    "delivery status notification", "failure notice", "returned mail",
    "delivery failure", "mail delivery subsystem", "postmaster",
    "mail failure",
]

BOUNCE_BODY_PATTERNS = [
    r"Final-Recipient:\s*rfc822;\s*([\w.+-]+@[\w.-]+)",
    r"X-Failed-Recipients:\s*([\w.+-]+@[\w.-]+)",
    r"Original-Recipient:\s*rfc822;\s*([\w.+-]+@[\w.-]+)",
]

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+")


def _decode(s):
    """Decode RFC2047 headers to plain text."""
    if not s:
        return ""
    try:
        out = ""
        for data, enc in decode_header(s):
            if isinstance(data, bytes):
                out += data.decode(enc or "utf-8", errors="replace")
            else:
                out += data
        return out
    except Exception:
        return s


def _is_bounce(msg) -> bool:
    """True if message subject looks like a delivery failure notification."""
    subj = _decode(msg.get("Subject", "")).lower()
    return any(kw in subj for kw in BOUNCE_SUBJECT_KEYWORDS)


def _extract_failed_recipients(msg):
    """Extract failed recipient email(s) from a bounce message body/headers."""
    recipients = set()

    # 1. Direct headers (X-Failed-Recipients / X-Original-To)
    for h in ("X-Failed-Recipients", "X-Original-To"):
        val = msg.get(h, "")
        m = _EMAIL_RE.search(val)
        if m:
            recipients.add(m.group(0).lower())

    # 2. Body — plain text / html
    parts = msg.walk() if msg.is_multipart() else [msg]
    body_text = ""
    for part in parts:
        ctype = part.get_content_type()
        if ctype in ("text/plain", "text/html"):
            try:
                payload = part.get_payload(decode=True)
                if payload:
                    body_text += payload.decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
            except Exception:
                continue

    for pat in BOUNCE_BODY_PATTERNS:
        for m in re.finditer(pat, body_text, re.IGNORECASE):
            recipients.add(m.group(1).lower())

    # 3. Fallback — "To:" line in plain bounce bodies
    if not recipients:
        m = re.search(r"\bTo:\s*([\w.+-]+@[\w.-]+)", body_text, re.IGNORECASE)
        if m:
            recipients.add(m.group(1).lower())

    return recipients


def scan_bounces(smtp_config: dict, max_msgs: int = 300):
    """Scan IMAP inbox for bounce notifications.

    Returns (bounces, error):
        bounces: list of {"emails": [...], "subject": str, "received_at": str}
        error:   "" if ok, else error message
    """
    host = smtp_config.get("host", "")
    port = int(smtp_config.get("imap_port") or os.environ.get("IMAP_PORT", 993))
    user = smtp_config.get("username", "")
    pw = smtp_config.get("password", "")

    if not (host and user and pw):
        return [], "IMAP credentials not configured (set IMAP_HOST/IMAP_PORT or smtp_config)"

    try:
        conn = imaplib.IMAP4_SSL(host, port)
        conn.login(user, pw)
        conn.select("INBOX")

        status, data = conn.search(None, "ALL")
        if status != "OK":
            conn.logout()
            return [], "IMAP search failed"

        ids = data[0].split()[-max_msgs:]  # most recent N messages only
        bounces = []
        for i in ids:
            try:
                status, msg_data = conn.fetch(i, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]:
                    continue
                msg = email_message_from_bytes(msg_data[0][1])
                if _is_bounce(msg):
                    recipients = _extract_failed_recipients(msg)
                    if recipients:
                        bounces.append({
                            "emails": sorted(recipients),
                            "subject": _decode(msg.get("Subject", ""))[:120],
                            "received_at": msg.get("Date", ""),
                        })
            except Exception:
                continue

        conn.logout()
        return bounces, ""
    except Exception as e:
        return [], str(e)


def email_message_from_bytes(raw: bytes):
    """Wrap email.message_from_bytes so the import stays local (lazy)."""
    import email
    return email.message_from_bytes(raw)
