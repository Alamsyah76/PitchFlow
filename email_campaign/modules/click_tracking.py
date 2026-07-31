"""Click tracking — detect when recipients click links in emails"""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

CLICK_FILE = Path(__file__).resolve().parent.parent / "clicks.json"


def _load_clicks() -> list:
    if not CLICK_FILE.exists():
        return []
    try:
        return json.loads(CLICK_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_clicks(data: list):
    CLICK_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def log_click(email: str, url: str, template_id: str = "", template_title: str = "", ip: str = "", user_agent: str = ""):
    """Log a click event"""
    data = _load_clicks()
    data.append({
        "email": email,
        "url": url[:500],
        "template_id": template_id,
        "template_title": template_title,
        "clicked_at": datetime.now().isoformat(),
        "ip": ip,
        "user_agent": user_agent,
    })
    _save_clicks(data)


def get_click_stats(email: str = "") -> dict:
    """Get click statistics per email, or for all"""
    data = _load_clicks()
    if email:
        clicks = [d for d in data if d["email"] == email]
        return {"email": email, "total_clicks": len(clicks), "first_click": clicks[0]["clicked_at"] if clicks else None, "last_click": clicks[-1]["clicked_at"] if clicks else None}

    email_counts = Counter(d["email"] for d in data)
    url_counts = Counter(d["url"] for d in data)
    return {
        "total_clicks": len(data),
        "unique_clicks": len(email_counts),
        "by_url": [{"url": u, "count": c} for u, c in url_counts.most_common(20)],
    }


def reset_clicks():
    """Reset all click data"""
    _save_clicks([])
