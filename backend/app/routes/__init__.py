"""Email Campaign API Routes package"""
import sys
import os
import json
from pathlib import Path
from fastapi import APIRouter

# ── Project Paths ──
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # routes/ -> app/ -> backend/ -> project root
EMAIL_DIR = PROJECT_ROOT / "email_campaign"

if str(EMAIL_DIR) not in sys.path:
    sys.path.insert(0, str(EMAIL_DIR))

# ── Module Imports ──
from modules.config import load_env, REPORT_DIR, XLS_FILE, LOG_FILE, ENV_FILE, load_settings, save_settings
from modules.validation import is_valid_email
from modules.storage import load_extra, save_extra, load_merged_contacts, save_merged_contacts
from modules.xls_reader import read_namecards, merge_xls_into_all
from modules.log_store import load_log, append_log, load_sent_log_detailed
from modules.email_builder import build_email_body
from modules.email_sender import send_email
from modules.queries import get_all_pending, get_all_contacts, get_campaign_stats

TEMPLATES_FILE = EMAIL_DIR / "templates.json"

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email-campaign", tags=["Email Campaign"])


# ── Shared Helpers ──

def get_campaign_stats():
    """Get campaign statistics — delegate ke queries module"""
    try:
        load_env()
    except SystemExit:
        pass
    from modules.queries import get_campaign_stats as _stats
    return _stats()


def load_templates():
    if TEMPLATES_FILE.exists():
        try:
            return json.loads(TEMPLATES_FILE.read_text())
        except Exception:
            pass
    return {"templates": [], "active_template": "default"}


def save_templates(data: dict):
    TEMPLATES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def text_to_html(text: str) -> str:
    if not text:
        return ""
    paragraphs = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        inner = "<br>".join(escape_html(line) for line in lines if line.strip())
        if inner:
            paragraphs.append(f"<p>{inner}</p>")
    return "\n".join(paragraphs)


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_active_template():
    """Return (subject, body_html, sections, logo_b64, cc_email) of the active template"""
    data = load_templates()
    tid = data.get("active_template", "default")
    for t in data.get("templates", []):
        if t["id"] == tid:
            bh = t.get("body_html", "") or None
            sections = t.get("sections", {}) or {}
            logo = t.get("logo_b64", "") or ""
            cc = t.get("cc_email", "") or ""
            return t.get("subject", ""), bh, sections, logo, cc
    return "", None, {}, "", ""


# ── Import Sub-routers ──
from .status import router as status_router
from .templates import router as templates_router
from .contacts import router as contacts_router
from .settings import router as settings_router
from .upload import router as upload_router
from .send import router as send_router
from .scraper import router as scraper_router
from .blog_monitor import router as blog_monitor_router
from .content_library import router as content_library_router
from .tracking import router as tracking_router
from .daily_report import router as daily_report_router
from .report import router as report_router

router.include_router(status_router)
router.include_router(templates_router)
router.include_router(contacts_router)
router.include_router(settings_router)
router.include_router(upload_router)
router.include_router(send_router)
router.include_router(scraper_router)
router.include_router(blog_monitor_router)
router.include_router(content_library_router)
router.include_router(tracking_router)
router.include_router(daily_report_router)
router.include_router(report_router)
