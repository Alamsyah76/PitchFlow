"""Unsubscribe endpoints — recipient opt-out with HMAC token verification"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from modules.unsubscribe_store import unsubscribe, verify_token, get_unsubscribers, unsubscribed_set

router = APIRouter(prefix="", tags=["Unsubscribe"])

_SUCCESS_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unsubscribed</title></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f5f7fa;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0">
<div style="background:#fff;border-radius:16px;padding:40px 48px;max-width:440px;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
<div style="font-size:48px;margin-bottom:12px">👋</div>
<h1 style="color:#1e293b;font-size:22px;margin:0 0 8px">You have been unsubscribed</h1>
<p style="color:#64748b;font-size:14px;line-height:1.6;margin:0">You will no longer receive marketing emails from this sender. If this was a mistake, no action is needed — you can re-subscribe anytime by contacting the sender.</p>
</div></body></html>"""

_INVALID_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Invalid Link</title></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f5f7fa;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0">
<div style="background:#fff;border-radius:16px;padding:40px 48px;max-width:440px;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
<div style="font-size:48px;margin-bottom:12px">⚠️</div>
<h1 style="color:#1e293b;font-size:22px;margin:0 0 8px">Invalid unsubscribe link</h1>
<p style="color:#64748b;font-size:14px;line-height:1.6;margin:0">This link is invalid or has expired. Please contact the sender if you wish to unsubscribe.</p>
</div></body></html>"""


@router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe_page(email: str = "", token: str = ""):
    """Handle unsubscribe click — verify token, mark opted out, show confirmation."""
    if not email or not verify_token(email, token):
        return HTMLResponse(_INVALID_PAGE, status_code=400)

    unsubscribe(email)
    return HTMLResponse(_SUCCESS_PAGE)


@router.get("/unsubscribe/list")
async def unsubscribe_list():
    """Get all unsubscribed emails (for stats)."""
    return {"success": True, "data": {"unsubscribers": get_unsubscribers(), "count": len(unsubscribed_set())}}
