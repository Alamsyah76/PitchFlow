"""Rate limit & usage status endpoint"""
from fastapi import APIRouter, HTTPException
from app.rate_limit import get_usage_status, set_tier, TIERS

router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.get("/status")
async def plan_status(identifier: str = "default"):
    return {"success": True, "data": get_usage_status(identifier)}


@router.get("/tiers")
async def list_tiers():
    """Return all tier definitions (for frontend pricing table)"""
    return {"success": True, "data": {
        name: {k: v for k, v in tier.items() if k != "trial_image"}
        for name, tier in TIERS.items()
    }}


@router.post("/set-tier")
async def update_tier(payload: dict):
    identifier = payload.get("identifier", "default")
    tier = payload.get("tier", "free")
    if tier not in TIERS:
        raise HTTPException(status_code=400, detail=f"Tier '{tier}' not found")
    set_tier(identifier, tier)
    return {"success": True, "message": f"Tier {identifier} → {tier}"}
