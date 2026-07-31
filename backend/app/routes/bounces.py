"""Bounce scan endpoint — check inbox for delivery failures and mark contacts"""
import os
from fastapi import APIRouter
from . import logger, append_log
from modules.bounce_detector import scan_bounces
from modules.log_store import load_bounced

router = APIRouter()


@router.post("/bounces/scan")
async def scan_bounce_emails():
    """Scan IMAP inbox for bounce/NDR emails; mark matched contacts as 'bounced'."""
    try:
        from modules.config import load_env
        load_env()
        from app.routes.send import _build_smtp_config
        smtp_config = _build_smtp_config()
        # IMAP usually shares SMTP host/creds — add imap config if available
        smtp_config["imap_port"] = int(os.environ.get("IMAP_PORT", 993))

        bounces, error = scan_bounces(smtp_config)
        if error:
            return {"success": False, "message": f"Bounce scan failed: {error}"}

        already = load_bounced()
        marked = []
        for b in bounces:
            for email in b["emails"]:
                if email.lower() in already:
                    continue
                append_log("Bounce", email, "", "bounced", b.get("subject", ""))
                marked.append(email)
                already.add(email)

        return {
            "success": True,
            "message": f"Scan done: {len(bounces)} bounce email(s) found, {len(marked)} new contact(s) marked",
            "data": {
                "bounce_emails_found": len(bounces),
                "new_marked": len(marked),
                "bounced": sorted(already),
            },
        }
    except Exception as e:
        logger.error(f"Bounce scan error: {e}")
        return {"success": False, "message": str(e)}
