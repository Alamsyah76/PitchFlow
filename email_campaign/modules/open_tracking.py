"""Open tracking — detect when recipients open emails via pixel tracking"""
import json
import base64
from datetime import datetime
from pathlib import Path

TRACKING_FILE = Path(__file__).resolve().parent.parent / "tracking.json"

# 1x1 transparent GIF pixel (base64)
PIXEL_GIF = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)

def _load_tracking() -> list:
    if not TRACKING_FILE.exists():
        return []
    try:
        return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _save_tracking(data: list):
    TRACKING_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def log_open(email: str, template_id: str = "", template_title: str = "", ip: str = "", user_agent: str = ""):
    """Log an email open event"""
    data = _load_tracking()
    data.append({
        "email": email,
        "template_id": template_id,
        "template_title": template_title,
        "opened_at": datetime.now().isoformat(),
        "ip": ip,
        "user_agent": user_agent,
    })
    _save_tracking(data)

def get_open_stats(email: str = "") -> dict:
    """Get open statistics per email, or for all"""
    data = _load_tracking()
    if email:
        opens = [d for d in data if d["email"] == email]
        return {"email": email, "total_opens": len(opens), "first_open": opens[0]["opened_at"] if opens else None, "last_open": opens[-1]["opened_at"] if opens else None}
    
    # Per-email stats
    from collections import Counter
    email_counts = Counter(d["email"] for d in data)
    return {
        "total_opens": len(data),
        "unique_opens": len(email_counts),
        "by_email": [{"email": e, "count": c} for e, c in email_counts.most_common()],
    }

def reset_tracking():
    """Reset all tracking data"""
    _save_tracking([])
