"""Blog Monitor API — check & trigger auto-send newsletter"""
import re
import time as time_module
from fastapi import APIRouter, HTTPException
from modules.blog_monitor import check_for_new_posts, get_status, reset_sent
from modules.scraper import scrape_blog_post
from . import logger, load_templates, save_templates, get_all_contacts, append_log, build_email_body, text_to_html
from app.sender_settings import get_sender_config

router = APIRouter(prefix="", tags=["Blog Monitor"])

@router.get("/blog-monitor/status")
async def blog_monitor_status():
    """Get blog monitor status — total sent, last checked"""
    return {"success": True, "data": get_status()}

@router.post("/blog-monitor/check")
async def blog_monitor_check(dry_run: bool = True):
    """Check for new blog posts. Creates template + sends newsletter.
    Set dry_run=false to actually send."""
    new_posts = check_for_new_posts()

    if not new_posts:
        return {
            "success": True,
            "data": {"new_posts": 0, "message": "No new blog posts found"},
        }

    results = []
    for post in new_posts:
        try:
            detail = scrape_blog_post(post["url"])
            result = _auto_send_blog(detail, dry_run=dry_run)
            results.append({
                "title": post["title"],
                "url": post["url"],
                "sent": result["sent"],
                "count": result["count"],
                "error": result.get("error"),
            })
        except Exception as e:
            logger.error(f"Error processing blog post {post['title']}: {e}")
            results.append({
                "title": post["title"],
                "url": post["url"],
                "sent": False,
                "error": str(e),
            })

    return {
        "success": True,
        "data": {
            "new_posts": len(new_posts),
            "results": results,
        },
    }

@router.post("/blog-monitor/reset")
async def blog_monitor_reset():
    """Reset sent tracking (for testing)"""
    reset_sent()
    return {"success": True, "message": "Blog monitor tracking reset"}

def _auto_send_blog(detail: dict, dry_run: bool = True) -> dict:
    """Create a template from blog post and optionally send to all pending contacts.
    dry_run=True (default) only creates template and updates blog_sent.json without sending.
    Returns dict with sent status and count.
    """
    title = detail.get("title", "Blog Post")
    content_html = detail.get("content_html", "")
    url = detail.get("url", "")

    # 1. Create or reuse a "Newsletter" template
    data = load_templates()
    prev_active = data.get("active_template", "")
    existing = [t for t in data.get("templates", []) if t.get("title", "").startswith("📰")]
    if existing:
        tpl = existing[0]
        tpl_id = tpl["id"]
        # Update content
        tpl["title"] = f"📰 {title}"
        tpl["subject"] = f"📢 New Blog: {title}"
        tpl["body_html"] = content_html
        tpl["updated_at"] = __import__("datetime").datetime.now().isoformat()
        # Update sender config too
        sender_cfg = get_sender_config()
        if sender_cfg.get("name"):
            tpl["sender_name"] = sender_cfg["name"]
    else:
        tpl_id = f"tpl_blog_{int(time_module.time())}"
        data["templates"].append({
            "id": tpl_id,
            "title": f"📰 {title}",
            "subject": f"📢 New Blog: {title}",
            "body_html": content_html,
            "body_text": detail.get("content_text", ""),
            "logo_b64": "",
            "cc_email": "",
            "created_at": __import__("datetime").datetime.now().isoformat(),
            "updated_at": __import__("datetime").datetime.now().isoformat(),
        })

    # 2. Activate this template
    data["active_template"] = tpl_id
    save_templates(data)

    # 3. Send to all pending contacts (skip if dry_run)
    if dry_run:
        # Restore previous active template
        data["active_template"] = prev_active
        save_templates(data)
        return {"sent": True, "count": 0, "note": "Template created (dry run — previous template restored)"}

    all_contacts = get_all_contacts()
    pending = [c for c in all_contacts if c.get("status") != "sent"]

    if not pending:
        return {"sent": True, "count": 0, "note": "No pending contacts"}

    # Send via the existing send logic
    from .send import _send_to_contacts, _build_smtp_config
    from modules.config import load_env
    sender = get_sender_config()

    try:
        load_env()
        smtp_config = _build_smtp_config()
    except Exception as e:
        return {"sent": False, "count": 0, "error": f"SMTP config error: {e}"}

    if not smtp_config or not smtp_config.get("sender_email"):
        return {"sent": False, "count": 0, "error": "SMTP not configured"}

    # Use the shared send function
    sent_count, fail_count, errors = _send_to_contacts(pending, smtp_config, sender)

    return {"sent": True, "count": sent_count, "failed": fail_count}
