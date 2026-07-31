"""Contact management endpoints"""
from fastapi import APIRouter, HTTPException
from . import (logger, get_all_contacts, get_all_pending, read_namecards,
               is_valid_email, load_extra, save_extra, load_merged_contacts, save_merged_contacts)
from .models import ManualContact, ContactEdit

router = APIRouter()


@router.get("/contacts")
async def list_contacts():
    try:
        pending = get_all_pending()
        return {"success": True, "data": {"contacts": pending}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contacts/manual")
async def add_manual_contact(contact: ManualContact):
    try:
        if not is_valid_email(contact.email):
            raise HTTPException(status_code=400, detail="Invalid email address")
        extra = load_extra()
        email_lower = contact.email.strip().lower()
        for c in extra.get("manual", []):
            if c.get("email", "").strip().lower() == email_lower:
                raise HTTPException(status_code=409, detail=f"Email '{contact.email}' sudah ada!")
        try:
            xls_contacts = read_namecards()
            for c in xls_contacts:
                if c.get("email", "").strip().lower() == email_lower:
                    raise HTTPException(status_code=409, detail=f"Email '{contact.email}' sudah ada di file Excel!")
        except HTTPException:
            raise
        except Exception:
            pass
        extra.setdefault("manual", []).append(contact.model_dump())
        # Tambah added_at timestamp untuk audience growth
        try:
            from datetime import datetime
            extra["manual"][-1]["added_at"] = datetime.now().isoformat(timespec="seconds")
        except Exception:
            pass
        save_extra(extra)
        return {"success": True, "message": f"Contact {contact.name} added manually"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/contacts/edit")
async def edit_contact(edit: ContactEdit):
    try:
        all_contacts = get_all_contacts()
        if edit.index < 0 or edit.index >= len(all_contacts):
            raise HTTPException(status_code=404, detail=f"Index {edit.index} out of range (0-{len(all_contacts)-1})")
        merged = load_merged_contacts()
        extra = load_extra()
        edit_data = {}
        if edit.name is not None: edit_data["name"] = edit.name
        if edit.email is not None: edit_data["email"] = edit.email
        if edit.phone is not None: edit_data["phone"] = edit.phone
        if edit.job_title is not None: edit_data["job_title"] = edit.job_title
        if edit.company is not None: edit_data["company"] = edit.company
        xls_count = len(merged)
        if edit.index < xls_count:
            merged[edit.index].update(edit_data)
            save_merged_contacts(merged)
        else:
            manual_idx = edit.index - xls_count
            extra.setdefault("manual", [])
            if 0 <= manual_idx < len(extra["manual"]):
                extra["manual"][manual_idx].update(edit_data)
                save_extra(extra)
        return {"success": True, "message": f"Contact at index {edit.index} updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contacts/manual/{idx}")
async def delete_manual_contact(idx: int):
    try:
        extra = load_extra()
        manuals = extra.get("manual", [])
        if idx < 0 or idx >= len(manuals):
            raise HTTPException(status_code=404, detail=f"Manual contact index {idx} out of range")
        removed = manuals.pop(idx)
        extra["manual"] = manuals
        save_extra(extra)
        return {"success": True, "message": f"Removed manual contact: {removed.get('name')}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contacts/manual-lookup")
async def lookup_manual_contact(payload: dict):
    """Find manual contact index by email"""
    try:
        email = (payload.get("email", "") or "").strip().lower()
        extra = load_extra()
        manuals = extra.get("manual", [])
        for i, c in enumerate(manuals):
            if c.get("email", "").strip().lower() == email:
                return {"success": True, "data": {"manual_idx": i}}
        return {"success": False, "message": "Contact not found in manual list"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contacts/delete-by-email")
async def delete_contact_by_email(payload: dict):
    """Delete contact from either manual or merged list by email"""
    try:
        email = (payload.get("email", "") or "").strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        # Try manual list first
        extra = load_extra()
        manuals = extra.get("manual", [])
        for i, c in enumerate(manuals):
            if c.get("email", "").strip().lower() == email:
                removed = manuals.pop(i)
                extra["manual"] = manuals
                save_extra(extra)
                return {"success": True, "message": f"Removed manual contact: {removed.get('name')}"}

        # Try merged list
        from modules.storage import load_merged_contacts, save_merged_contacts
        all_c = load_merged_contacts()
        for i, c in enumerate(all_c):
            if c.get("email", "").strip().lower() == email:
                removed = all_c.pop(i)
                save_merged_contacts(all_c)
                return {"success": True, "message": f"Removed merged contact: {removed.get('name')}"}

        return {"success": False, "message": "Contact not found"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/contacts/edits")
async def clear_edits():
    extra = load_extra()
    extra["edits"] = {}
    save_extra(extra)
    return {"success": True, "message": "All edits cleared"}
