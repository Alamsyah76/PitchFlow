"""Status & Preview endpoints"""
import csv
from fastapi import APIRouter, HTTPException
from . import get_campaign_stats, get_all_contacts, get_all_pending, get_active_template, build_email_body, logger, LOG_FILE, append_log
from app.sender_settings import get_sender_config

router = APIRouter()


@router.get("/status")
async def campaign_status():
    try:
        stats = get_campaign_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview")
async def preview_contacts(limit: int = 20, q: str = ""):
    try:
        all_c = get_all_contacts()
        sent_log = {}
        try:
            from . import load_sent_log_detailed
            sent_log = load_sent_log_detailed()
        except: pass
        bounced = set()
        try:
            from modules.log_store import load_bounced
            bounced = load_bounced()
        except: pass

        def _status(c):
            e = c.get("email", "").strip().lower()
            if e in bounced:
                return "bounced"
            return "sent" if e in sent_log else "pending"

        if q.strip():
            ql = q.strip().lower()
            matched = [c for c in all_c
                       if ql in c.get("name", "").lower()
                       or ql in c.get("email", "").lower()
                       or ql in c.get("company", "").lower()]
            preview = matched[:limit]
            return {"success": True, "data": {"total_pending": len(matched), "preview": [
                {"name": c["name"], "email": c["email"], "company": c.get("company", ""), "job_title": c.get("job_title", ""),
                 "status": _status(c),
                 "last_template": sent_log.get(c.get("email","").strip().lower(), {}).get("template_id", "")}
                for c in preview]}}
        else:
            preview = all_c[:limit]
            return {"success": True, "data": {"total_pending": len(all_c), "preview": [
                {"name": c["name"], "email": c["email"], "company": c.get("company", ""), "job_title": c.get("job_title", ""),
                 "status": _status(c),
                 "last_template": sent_log.get(c.get("email","").strip().lower(), {}).get("template_id", "")}
                for c in preview]}}
    except Exception as e:
        logger.error(f"Preview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview-email/{index}")
async def preview_email_html(index: int = 0, template_id: str = None):
    try:
        # FIX #2: Fallback ke dummy contact jika tidak ada pending contacts
        pending = get_all_pending()
        if index < 0 or index >= len(pending):
            # Gunakan dummy contact untuk preview
            contact = {"name": "Nama Kontak", "email": "contoh@email.com",
                       "company": "Perusahaan", "job_title": "CEO", "phone": ""}
        else:
            contact = pending[index]
        
        if template_id:
            # Use specific template
            from . import load_templates
            tpl_data = load_templates()
            tpl = next((t for t in tpl_data["templates"] if t["id"] == template_id), None)
            if not tpl:
                raise HTTPException(status_code=404, detail="Template not found")
            tpl_subject = tpl.get("subject", "")
            tpl_body = tpl.get("body_html", "")
            tpl_sections = tpl.get("sections", {})
            tpl_logo = tpl.get("logo_b64", "")
        else:
            tpl_subject, tpl_body, tpl_sections, tpl_logo = get_active_template()
        
        sender = get_sender_config()
        # FIX #1: Priority — template logo > sender settings logo
        logo_b64 = tpl_logo or sender.get("logo_b64", "")
        
        html = build_email_body(contact, template_body=tpl_body,
            sender_name=sender["name"],
            sender_email=sender["email"],
            sender_company=sender.get("company", "PitchFlow"),
            logo_b64=logo_b64,
            **{f"template_{k}": v for k, v in tpl_sections.items()})
        return {
            "success": True,
            "data": {
                "contact": {"name": contact["name"], "email": contact["email"], "company": contact.get("company", "")},
                "subject": tpl_subject,
                "html": html,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/log")
async def get_log(limit: int = 100):
    try:
        entries = []
        if LOG_FILE.exists():
            with open(LOG_FILE, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                except StopIteration:
                    header = []
                for row in reader:
                    if len(row) >= 5:
                        entries.append({
                            "timestamp": row[0],
                            "email": row[1],
                            "name": row[2],
                            "company": row[3],
                            "status": row[4],
                            "error": row[5] if len(row) > 5 else "",
                        })
        entries.reverse()
        return {"success": True, "data": entries[:limit], "total": len(entries)}
    except Exception as e:
        logger.error(f"Log error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/log/download")
async def download_log():
    """Download log.csv as a file"""
    if not LOG_FILE.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    from fastapi.responses import FileResponse
    return FileResponse(
        path=LOG_FILE,
        filename="log_pengiriman.csv",
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=log_pengiriman.csv"}
    )


@router.post("/log/clear")
async def clear_log():
    """Clear all log entries (reset log.csv to header only)"""
    try:
        import csv
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "email", "name", "company", "status", "error", "template_id"])
        return {"success": True, "message": "Log cleared successfully"}
    except Exception as e:
        logger.error(f"Clear log error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
