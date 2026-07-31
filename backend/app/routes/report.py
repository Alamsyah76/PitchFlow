"""Report API — time-series data & KPIs for charts"""
import csv
import json
from datetime import datetime, timedelta, date
from collections import defaultdict
from fastapi import APIRouter
from . import LOG_FILE, logger
from modules.log_store import load_log
from modules.open_tracking import get_open_stats
from modules.blog_monitor import get_status
from modules.daily_report import generate_today_report

router = APIRouter(prefix="", tags=["Report"])


def _parse_log_csv() -> list[dict]:
    """Parse full send log CSV into list of dicts"""
    entries = []
    if not LOG_FILE.exists():
        return entries
    try:
        with open(LOG_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 5:
                    entries.append({
                        "timestamp": row[0],
                        "email": row[1],
                        "name": row[2],
                        "company": row[3],
                        "status": row[4],
                        "error": row[5] if len(row) > 5 else "",
                        "template_id": row[6].strip() if len(row) >= 7 else "",
                    })
    except Exception as e:
        logger.error(f"Parse log CSV error: {e}")
    return entries


@router.get("/report/summary")
async def report_summary():
    """Aggregated KPIs for dashboard cards"""
    try:
        today = date.today().isoformat()[:10]
        entries = _parse_log_csv()

        # Total stats
        total_sent = len([e for e in entries if e["status"] == "sent"])
        total_failed = len([e for e in entries if e["status"] == "failed"])
        total_bounced = len([e for e in entries if e["status"] == "bounced"])

        # Today stats
        today_entries = [e for e in entries if e["timestamp"].startswith(today)]
        today_sent = len([e for e in today_entries if e["status"] == "sent"])
        today_failed = len([e for e in today_entries if e["status"] in ("failed", "bounced")])

        # Open stats
        open_stats = get_open_stats()
        total_opens = open_stats.get("total_opens", 0)
        unique_opens = open_stats.get("unique_opens", 0)
        open_rate = round((unique_opens / total_sent * 100), 1) if total_sent > 0 else 0

        # Bounce rate — bounced / (sent + bounced) * 100
        bounce_rate = round((total_bounced / (total_sent + total_bounced) * 100), 1) if (total_sent + total_bounced) > 0 else 0

        # Blog monitor
        blog = get_status()

        # Contacts
        from modules.storage import load_merged_contacts
        contacts = load_merged_contacts()
        total_contacts = len(contacts)

        # Pending = belum dikirim & tidak gagal/bounce
        delivered = total_sent + total_failed + total_bounced
        pending = max(0, total_contacts - delivered)

        return {
            "success": True,
            "data": {
                "total_sent": total_sent,
                "total_failed": total_failed,
                "total_bounced": total_bounced,
                "today_sent": today_sent,
                "today_failed": today_failed,
                "total_opens": total_opens,
                "unique_opens": unique_opens,
                "open_rate": open_rate,
                "bounce_rate": bounce_rate,
                "total_contacts": total_contacts,
                "pending": pending,
                "blog_posts_sent": blog.get("total_sent", 0),
                "last_checked": blog.get("last_checked", "never"),
            },
        }
    except Exception as e:
        logger.error(f"Report summary error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/report/timeline")
async def report_timeline(days: int = 30):
    """Time-series data for charts — daily send/open stats"""
    try:
        entries = _parse_log_csv()
        open_stats = get_open_stats()

        # Build date range
        today_dt = date.today()
        date_range = [(today_dt - timedelta(days=i)).isoformat()[:10] for i in range(days - 1, -1, -1)]

        # Aggregate by date
        daily_sent = defaultdict(int)
        daily_failed = defaultdict(int)
        for e in entries:
            d = e["timestamp"][:10]
            if e["status"] == "sent":
                daily_sent[d] += 1
            elif e["status"] in ("failed", "bounced"):
                daily_failed[d] += 1

        # Aggregate opens by date
        daily_opens = defaultdict(int)
        daily_unique_opens = defaultdict(set)
        try:
            track_file = __import__("modules.open_tracking", fromlist=[""]).TRACKING_FILE
            if track_file.exists():
                track_data = json.loads(track_file.read_text(encoding="utf-8"))
                for t in track_data:
                    d = t.get("opened_at", "")[:10]
                    daily_opens[d] += 1
                    daily_unique_opens[d].add(t.get("email", ""))
        except Exception:
            pass

        timeline = []
        for d in date_range:
            timeline.append({
                "date": d,
                "sent": daily_sent.get(d, 0),
                "failed": daily_failed.get(d, 0),
                "opens": daily_opens.get(d, 0),
                "unique_opens": len(daily_unique_opens.get(d, set())),
            })

        return {
            "success": True,
            "data": {
                "timeline": timeline,
                "total_days": days,
            },
        }
    except Exception as e:
        logger.error(f"Report timeline error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/report/campaigns")
async def report_campaigns(limit: int = 10):
    """Campaign list derived from log — group by template_id (Mailchimp-style)."""
    try:
        entries = _parse_log_csv()
        opens_data = []
        try:
            track_file = __import__("modules.open_tracking", fromlist=[""]).TRACKING_FILE
            if track_file.exists():
                opens_data = json.loads(track_file.read_text(encoding="utf-8"))
        except Exception:
            pass

        # Template title lookup
        tpl_titles = {}
        try:
            tpl_file = Path(__file__).resolve().parent.parent.parent.parent / "email_campaign" / "templates.json"
            if tpl_file.exists():
                tpl_data = json.loads(tpl_file.read_text(encoding="utf-8"))
                for t in tpl_data.get("templates", []):
                    tpl_titles[t["id"]] = t.get("title", t["id"])
        except Exception:
            pass

        from collections import defaultdict
        groups = defaultdict(lambda: {"sent": 0, "failed": 0, "bounced": 0, "first": None, "last": None})
        for e in entries:
            tid = e["template_id"] or "default"
            g = groups[tid]
            if e["status"] == "sent":
                g["sent"] += 1
            elif e["status"] == "failed":
                g["failed"] += 1
            elif e["status"] == "bounced":
                g["bounced"] += 1
            ts = e["timestamp"]
            if not g["first"] or ts < g["first"]:
                g["first"] = ts
            if not g["last"] or ts > g["last"]:
                g["last"] = ts

        # Opens per template
        opens_by_tpl = defaultdict(lambda: {"total": 0, "unique": set()})
        for o in opens_data:
            tid = o.get("template_id", "")
            opens_by_tpl[tid]["total"] += 1
            opens_by_tpl[tid]["unique"].add(o.get("email", ""))

        campaigns = []
        for tid, g in groups.items():
            delivered = g["sent"] + g["failed"] + g["bounced"]
            open_info = opens_by_tpl.get(tid, {"total": 0, "unique": set()})
            campaigns.append({
                "template_id": tid,
                "name": tpl_titles.get(tid, tid),
                "sent": g["sent"],
                "failed": g["failed"],
                "bounced": g["bounced"],
                "open_rate": round((len(open_info["unique"]) / g["sent"] * 100), 1) if g["sent"] > 0 else 0,
                "first_sent": g["first"],
                "last_sent": g["last"],
            })

        campaigns.sort(key=lambda c: c["last_sent"] or "", reverse=True)
        return {"success": True, "data": {"campaigns": campaigns[:limit]}}
    except Exception as e:
        logger.error(f"Report campaigns error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/report/recent-activity")
async def report_recent_activity(limit: int = 10):
    """Most recent send activity"""
    try:
        entries = _parse_log_csv()
        entries.reverse()
        recent = entries[:limit]
        return {"success": True, "data": recent}
    except Exception as e:
        logger.error(f"Recent activity error: {e}")
        return {"success": False, "error": str(e)}
