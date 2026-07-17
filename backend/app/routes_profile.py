"""Profile API — update avatar, get profile"""
import os, json, logging
from fastapi import APIRouter, HTTPException

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
