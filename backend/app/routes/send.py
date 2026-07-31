"""Send email endpoints"""
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from . import (logger, load_env, get_all_contacts, get_all_pending, get_active_template,
               load_templates, build_email_body, send_email, append_log, load_sent_log_detailed,
               load_log)
from .models import SendResponse, SendSelectedRequest, CheckDuplicateRequest
from app.sender_settings import get_sender_config
from modules.config import load_settings as load_campaign_settings

# Test emails — always sendable regardless of log
from modules.config import TEST_EMAILS
TEST_EMAIL_LOWER = {e.strip().lower() for e in TEST_EMAILS}

router = APIRouter()


@router.post("/check-duplicates")
async def check_duplicates(payload: CheckDuplicateRequest):
    try:
        all_c = get_all_contacts()
        selected = []
        for idx in payload.indices:
            if 0 <= idx < len(all_c):
                selected.append(all_c[idx])
        sent_log = load_sent_log_detailed()
        active_tid = payload.template_id or ""
        duplicates = []
        for c in selected:
            email_lower = c["email"].strip().lower()
            if email_lower in sent_log:
                entry = sent_log[email_lower]
                if entry["template_id"] and entry["template_id"] == active_tid:
                    duplicates.append({
                        "email": c["email"], "name": c["name"],
                        "company": c.get("company", ""),
                        "last_sent": entry["timestamp"], "template_id": entry["template_id"],
                    })
        return {"success": True, "data": {"duplicates": duplicates}}
    except Exception as e:
        logger.error(f"Check duplicates error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_smtp_config() -> dict:
    """Build SMTP config from settings.json, fallback to .env"""
    settings = load_campaign_settings()
    sender = get_sender_config()
    
    host = settings.get("smtp_host") or os.environ.get("SMTP_HOST", "")
    port = settings.get("smtp_port") or int(os.environ.get("SMTP_PORT", 465))
    username = settings.get("smtp_username") or os.environ.get("SMTP_USERNAME", "")
    password = settings.get("smtp_password") or os.environ.get("SMTP_PASSWORD", "")
    sender_name = settings.get("sender_name") or sender.get("name", "")
    sender_email = settings.get("sender_email") or sender.get("email", "")
    
    # Tracking base URL — pakai env var supaya bekerja di production
    # (bukan hardcoded localhost). Default ke localhost untuk dev.
    tracking_base = (
        os.environ.get("TRACKING_BASE_URL")
        or os.environ.get("PUBLIC_API_URL")
        or f"http://localhost:{os.environ.get('API_PORT', '8030')}"
    ).rstrip("/")

    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "sender_name": sender_name,
        "sender_email": sender_email,
        "tracking_base_url": tracking_base,
    }


def _send_to_contacts(selected, smtp_config, sender):
    """Shared send logic — return (sent_count, fail_count, errors)"""
    tpl_subject, tpl_body, tpl_sections, tpl_logo, tpl_cc = get_active_template()
    data = load_templates()
    active_tid = data.get("active_template", "default")
    template_exists = bool(tpl_subject or tpl_body or any(v for v in tpl_sections.values()) or tpl_logo)

    # Collect attachment files for this template
    from modules.config import ATTACHMENTS_DIR
    tid_dir = ATTACHMENTS_DIR / active_tid
    attachments = []
    if tid_dir.exists():
        for f in sorted(tid_dir.iterdir()):
            if f.is_file():
                attachments.append(str(f))

    logo_b64 = tpl_logo or sender.get("logo_b64", "")

    sent_count, fail_count, errors = 0, 0, []
    for contact in selected:
        if template_exists:
            html = build_email_body(contact, template_body=tpl_body,
                    sender_name=smtp_config.get("sender_name", ""),
                    sender_email=smtp_config.get("sender_email", ""),
                    sender_company=sender.get("company", "PitchFlow"),
                    logo_b64=logo_b64,
                    **{f"template_{k}": v for k, v in tpl_sections.items()})
        else:
            html = build_email_body(contact, template_body="",
                    sender_name=smtp_config.get("sender_name", ""),
                    sender_email=smtp_config.get("sender_email", ""),
                    sender_company=sender.get("company", "PitchFlow"),
                    logo_b64=logo_b64)

        # Append open tracking pixel
        track_url = smtp_config.get("tracking_base_url", "http://localhost:8040")
        pixel = f'<img src="{track_url}/api/email-campaign/track/open?email={contact["email"]}&template_id={active_tid}" width="1" height="1" style="display:none" />'
        html = html.replace("</body>", f"{pixel}</body>") if "</body>" in html else html + pixel

        ok, err = send_email(smtp_config, contact["email"], contact["name"], html,
                             subject=tpl_subject, attachments=attachments or None, cc_email=tpl_cc)
        if ok:
            append_log(contact["name"], contact["email"], contact.get("company", ""), "sent", template_id=active_tid)
            sent_count += 1
        else:
            append_log(contact["name"], contact["email"], contact.get("company", ""), "failed", err, template_id=active_tid)
            fail_count += 1
            errors.append(f"{contact['email']}: {err}")
    return sent_count, fail_count, errors


@router.post("/send-selected", response_model=SendResponse)
async def send_selected(payload: SendSelectedRequest):
    try:
        load_env()
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        if not smtp_pass or smtp_pass == "your_password_here":
            return SendResponse(success=False, message="SMTP password not configured in .env")

        # Gunakan get_all_contacts() (full list, sama dengan frontend)
        all_c = get_all_contacts()
        sent_set = load_log()

        selected = []
        for idx in payload.indices:
            if 0 <= idx < len(all_c):
                contact = all_c[idx]
                email_lower = contact["email"].strip().lower()
                if email_lower not in sent_set or email_lower in TEST_EMAIL_LOWER:
                    selected.append(contact)

        if not selected:
            return SendResponse(success=False, message="No valid pending contacts selected (all may have been sent already)")

        sender = get_sender_config()
        smtp_config = _build_smtp_config()

        if not smtp_config["password"] or smtp_config["password"] == "your_password_here":
            return SendResponse(success=False, message="SMTP password not configured")

        sent_count, fail_count, errors = _send_to_contacts(selected, smtp_config, sender)
        return SendResponse(success=True, message=f"Sent {sent_count} success, {fail_count} failed",
                            sent_count=sent_count, fail_count=fail_count, errors=errors)
    except Exception as e:
        logger.error(f"Send selected error: {e}")
        return SendResponse(success=False, message=str(e))


@router.post("/send", response_model=SendResponse)
async def send_batch(background_tasks: BackgroundTasks):
    try:
        load_env()
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        if not smtp_pass or smtp_pass == "your_password_here":
            return SendResponse(success=False, message="SMTP password not configured in .env")
        pending = get_all_pending()
        daily_limit = int(os.environ.get("DAILY_LIMIT", 10))
        to_send = pending[:daily_limit]
        if not to_send:
            return SendResponse(success=True, message="All contacts have been sent. No pending emails.")
        sender = get_sender_config()
        smtp_config = _build_smtp_config()
        sent_count, fail_count, errors = _send_to_contacts(to_send, smtp_config, sender)
        return SendResponse(success=True, message=f"Batch sent: {sent_count} success, {fail_count} failed",
                            sent_count=sent_count, fail_count=fail_count, errors=errors)
    except Exception as e:
        logger.error(f"Send error: {e}")
        return SendResponse(success=False, message=str(e))
