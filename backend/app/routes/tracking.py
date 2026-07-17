"""Open tracking endpoint — serves 1x1 pixel and logs opens"""
from fastapi import APIRouter, Request
from fastapi.responses import Response
from modules.open_tracking import log_open, get_open_stats, reset_tracking, PIXEL_GIF
from . import get_active_template

router = APIRouter(prefix="", tags=["Tracking"])

@router.get("/track/open")
async def track_open(email: str = "", template_id: str = "", request: Request = None):
    """Tracking pixel — log open event and return 1x1 transparent GIF"""
    # Get template title for logging
    tpl_title = ""
    if template_id:
        try:
            data = __import__("json").loads(
                (__import__("pathlib").Path(__file__).resolve().parent.parent.parent.parent /
                 "email_campaign" / "templates.json").read_text()
            )
            for t in data.get("templates", []):
                if t["id"] == template_id:
                    tpl_title = t.get("title", "")
                    break
        except:
            pass

    ip = request.client.host if request else ""
    ua = request.headers.get("user-agent", "") if request else ""

    if email:
        log_open(email, template_id, tpl_title, ip, ua)

    # Return 1x1 transparent GIF
    return Response(content=PIXEL_GIF, media_type="image/gif")

@router.get("/track/open/stats")
async def tracking_stats(email: str = ""):
    """Get open tracking statistics"""
    return {"success": True, "data": get_open_stats(email)}

@router.post("/track/open/reset")
async def tracking_reset():
    """Reset all tracking data"""
    reset_tracking()
    return {"success": True, "message": "Tracking data reset"}
