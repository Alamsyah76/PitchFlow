"""Settings endpoints"""
from fastapi import APIRouter, HTTPException
from . import logger, load_settings, save_settings

router = APIRouter()


@router.get("/settings")
async def get_settings():
    return {"success": True, "data": load_settings()}


@router.post("/settings")
async def update_settings(data: dict):
    try:
        save_settings(data)
        return {"success": True, "data": load_settings()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
