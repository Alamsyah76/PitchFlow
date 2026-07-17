"""Template CRUD endpoints + file attachments"""
import time as time_module
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from . import logger, load_templates, save_templates, text_to_html, build_email_body
from app.sender_settings import get_sender_config
from .models import TemplateModel, TemplateUpdate
from modules.config import ATTACHMENTS_DIR

router = APIRouter()


@router.get("/templates")
async def list_templates():
    data = load_templates()
    data["active_template_id"] = data.get("active_template", "default")
    return {"success": True, "data": data}


@router.post("/templates")
async def create_template(tpl: TemplateModel):
    data = load_templates()
    tid = tpl.id or f"tpl_{len(data['templates'])+1}_{int(time_module.time())}"
    new_tpl = {
        "id": tid,
        "title": tpl.title,
        "subject": tpl.subject,
        "body_html": tpl.body_html or text_to_html(tpl.body_text),
        "body_text": tpl.body_text or "",
        "logo_b64": tpl.logo_b64 or "",
        "cc_email": tpl.cc_email or "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    if tpl.sections is not None:
        new_tpl["sections"] = tpl.sections.model_dump()
    data["templates"].append(new_tpl)
    save_templates(data)
    return {"success": True, "data": new_tpl}


@router.put("/templates/{tid}")
async def update_template(tid: str, tpl: TemplateUpdate):
    data = load_templates()
    for t in data["templates"]:
        if t["id"] == tid:
            if tpl.title is not None: t["title"] = tpl.title
            if tpl.subject is not None: t["subject"] = tpl.subject
            if tpl.logo_b64 is not None: t["logo_b64"] = tpl.logo_b64
            if tpl.cc_email is not None: t["cc_email"] = tpl.cc_email
            if tpl.body_text is not None:
                t["body_text"] = tpl.body_text
            if tpl.body_html is not None:
                t["body_html"] = tpl.body_html
            elif tpl.body_text is not None:
                # Regenerate body_html from body_text only if body_html not provided
                t["body_html"] = text_to_html(tpl.body_text)
            if tpl.sections is not None:
                t["sections"] = tpl.sections.model_dump()
            t["updated_at"] = datetime.now().isoformat()
            save_templates(data)
            return {"success": True, "data": t}
    raise HTTPException(status_code=404, detail="Template not found")


@router.delete("/templates/{tid}")
async def delete_template(tid: str):
    data = load_templates()
    data["templates"] = [t for t in data["templates"] if t["id"] != tid]
    save_templates(data)
    return {"success": True, "message": f"Template {tid} deleted"}


@router.post("/templates/{tid}/activate")
async def activate_template(tid: str):
    data = load_templates()
    found = any(t["id"] == tid for t in data["templates"])
    if not found:
        raise HTTPException(status_code=404, detail="Template not found")
    data["active_template"] = tid
    save_templates(data)
    return {"success": True, "message": f"Template {tid} activated"}


@router.get("/templates/{tid}/preview")
async def preview_template(tid: str):
    data = load_templates()
    for t in data["templates"]:
        if t["id"] == tid:
            sender = get_sender_config()
            tpl_sections = t.get("sections", {}) or {}
            tpl_logo = t.get("logo_b64", "") or ""
            logo_b64 = tpl_logo or sender.get("logo_b64", "")
            html = build_email_body(
                {"name": "Contoh Nama", "email": "", "company": "Contoh Perusahaan", "job_title": "CEO", "phone": ""},
                template_body=t.get("body_html", ""),
                sender_name=sender["name"],
                sender_email=sender["email"],
                sender_company=sender.get("company", "PitchFlow"),
                logo_b64=logo_b64,
                **{f"template_{k}": v for k, v in tpl_sections.items()})
            return {"success": True, "data": {"title": t["title"], "subject": t["subject"], "html": html}}
    raise HTTPException(status_code=404, detail="Template not found")


# ── Attachment Endpoints ─────────────────────────────────────────


@router.post("/templates/{tid}/attachments")
async def upload_attachment(tid: str, file: UploadFile = File(...)):
    """Upload file attachment for a template"""
    data = load_templates()
    if not any(t["id"] == tid for t in data["templates"]):
        raise HTTPException(status_code=404, detail="Template not found")

    tid_dir = ATTACHMENTS_DIR / tid
    tid_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = Path(file.filename).name
    filepath = tid_dir / safe_name

    content = await file.read()
    # Limit: 10MB per file
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    filepath.write_bytes(content)

    return {"success": True, "data": {"filename": safe_name, "size": len(content)}}


@router.get("/templates/{tid}/attachments")
async def list_attachments(tid: str):
    """List all attachments for a template"""
    tid_dir = ATTACHMENTS_DIR / tid
    if not tid_dir.exists():
        return {"success": True, "data": {"attachments": []}}

    files = []
    for f in sorted(tid_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file():
            files.append({"filename": f.name, "size": f.stat().st_size})
    return {"success": True, "data": {"attachments": files}}


@router.delete("/templates/{tid}/attachments/{filename:path}")
async def delete_attachment(tid: str, filename: str):
    """Delete a file attachment"""
    filepath = ATTACHMENTS_DIR / tid / filename
    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    filepath.unlink()
    return {"success": True, "message": f"Deleted {filename}"}
