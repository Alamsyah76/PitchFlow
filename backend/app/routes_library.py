"""Library API — per-user, tier-limited"""
import os, json, logging
from fastapi import APIRouter, HTTPException
from app.library import get_library, add_item, get_limit as get_lib_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/library", tags=["Library"])


def _get_user(payload: dict) -> str:
    """Extract user email from request"""
    email = (payload.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Email user diperlukan")
    return email


@router.post("/list")
async def library_list(payload: dict):
    email = _get_user(payload)
    items = get_library(email)
    limit = get_lib_limit(email)
    return {"success": True, "data": {"items": items, "limit": limit}}


@router.post("/add")
async def library_add(payload: dict):
    email = _get_user(payload)
    item = payload.get("item")
    if not item:
        raise HTTPException(400, "Item diperlukan")
    
    from app.library import get_library as _gl, get_limit as _gl2, save_library as _sl
    limit = _gl2(email)
    items = _gl(email)
    
    if limit == 0:
        return {"success": False, "message": "Free tier tidak bisa menyimpan ke Library. Upgrade untuk simpan konten."}
    if limit > 0 and len(items) >= limit:
        # Replace item terendah
        items.sort(key=lambda x: x.get("score", 0))
        items[0] = item
    else:
        items.append(item)
    _sl(email, items)
    
    return {"success": True, "message": f"Tersimpan ({len(items)}/{limit if limit else '∞'})"}
