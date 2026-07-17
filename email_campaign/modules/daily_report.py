"""Daily Report — generate sales report for the day"""
from datetime import datetime, date
from pathlib import Path
from modules.storage import load_merged_contacts
from .open_tracking import get_open_stats

LOG_FILE = Path(__file__).resolve().parent.parent / "send_log.json"

def _load_log() -> list:
    if not LOG_FILE.exists():
        return []
    import json
    try:
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def generate_today_report() -> dict:
    """Generate report for today"""
    today = date.today().isoformat()[:10]
    log = _load_log()

    # Filter today's entries
    today_log = [e for e in log if e.get("timestamp", "").startswith(today)]

    total_sent = len([e for e in today_log if e.get("status") == "sent"])
    total_failed = len([e for e in today_log if e.get("status") == "failed"])

    # Open stats from tracking
    open_stats = get_open_stats()
    total_opens = open_stats.get("total_opens", 0)
    unique_opens = open_stats.get("unique_opens", 0)

    # Contacts overview
    contacts = load_merged_contacts()
    total_contacts = len(contacts)
    sent_contacts = len([c for c in contacts if c.get("status") == "sent"])
    pending = total_contacts - sent_contacts

    # Top recent sends (last 5)
    recent = []
    for e in today_log[:5]:
        recent.append({
            "email": e.get("email", ""),
            "name": e.get("name", ""),
            "status": e.get("status", ""),
            "time": e.get("timestamp", "")[11:16],
        })

    return {
        "date": today,
        "total_sent": total_sent,
        "total_failed": total_failed,
        "total_opens": total_opens,
        "unique_opens": unique_opens,
        "open_rate": round((unique_opens / total_sent * 100), 1) if total_sent > 0 else 0,
        "total_contacts": total_contacts,
        "pending": pending,
        "recent": recent,
    }

def format_report_text(report: dict) -> str:
    """Format report as plain text (for Telegram / console)"""
    lines = [
        f"📊 EMAIL CAMPAIGN REPORT",
        f"📅 {report['date']}",
        f"─────────────────────",
        f"✅ Sent:    {report['total_sent']}",
        f"❌ Failed:  {report['total_failed']}",
        f"👁️ Opens:   {report['total_opens']} ({report['open_rate']}%)",
        f"👤 Unique:  {report['unique_opens']}",
        f"─────────────────────",
        f"📋 Contacts: {report['total_contacts']} total, {report['pending']} pending",
        f"─────────────────────",
    ]

    if report['recent']:
        lines.append(f"📨 Recent:")
        for r in report['recent']:
            icon = "✅" if r['status'] == 'sent' else "❌"
            lines.append(f"  {icon} {r['time']} {r['email']}")

    return "\n".join(lines)
