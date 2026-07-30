"""Profile API — update avatar, get profile"""
import os, json, logging
from fastapi import APIRouter, HTTPException
from app.database import save_openai_key, get_openai_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["Profile"])

USERS_FILE = None

def _load():
    global USERS_FILE
    if USERS_FILE is None:
        from pathlib import Path
        home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
        USERS_FILE = home / "pitchflow_users.json"
    if USERS_FILE.exists():
        try: return json.loads(USERS_FILE.read_text())
        except: pass
    return {}


def _save(data: dict):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(data, indent=2))


@router.post("/get")
async def get_profile(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Email diperlukan")
    users = _load()
    user = users.get(email, {})
    return {
        "success": True,
        "data": {
            "name": user.get("name", ""),
            "email": email,
            "avatar": user.get("avatar", ""),
        }
    }


@router.post("/update")
async def update_profile(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    name = (payload.get("name") or "").strip()
    avatar = (payload.get("avatar") or "").strip()

    if not email or "@" not in email:
        raise HTTPException(400, "Email diperlukan")

    users = _load()
    if email not in users:
        raise HTTPException(404, "User tidak ditemukan")

    if name:
        users[email]["name"] = name
    if avatar:
        users[email]["avatar"] = avatar
    elif "avatar" in payload and not avatar:
        # Hapus avatar jika dikirim string kosong
        users[email].pop("avatar", None)

    _save(users)
    return {"success": True, "message": "Profil tersimpan"}


@router.post("/save-api-key")
async def save_api_key(payload: dict):
    """BYOK — user save their own OpenAI API key."""
    email = (payload.get("email") or "").strip().lower()
    api_key = (payload.get("api_key") or "").strip()

    if not email or "@" not in email:
        raise HTTPException(400, "Email diperlukan")
    if not api_key:
        raise HTTPException(400, "API Key tidak boleh kosong")

    save_openai_key(email, api_key)
    return {"success": True, "message": "API Key tersimpan"}


@router.post("/get-api-key-status")
async def get_api_key_status(payload: dict):
    """Cek apakah user punya API key sendiri."""
    email = (payload.get("email") or "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Email diperlukan")
    key = get_openai_key(email)
    return {
        "success": True,
        "data": {
            "has_key": bool(key),
            "key_preview": key[:8] + "..." + key[-4:] if len(key) > 12 else "",
        }
    }
