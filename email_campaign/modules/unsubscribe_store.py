"""Unsubscribe store — track emails that opted out"""
import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path

UNSUB_FILE = Path(__file__).resolve().parent.parent / "unsubscribed.json"
_TOKEN_SECRET = "pitchflow-unsub-2026"


def _load() -> list:
    if not UNSUB_FILE.exists():
        return []
    try:
        return json.loads(UNSUB_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save(data: list):
    UNSUB_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def unsubscribed_set() -> set:
    """Return set of unsubscribed emails (lowercase)."""
    return {u["email"].strip().lower() for u in _load() if u.get("email")}


def make_token(email: str) -> str:
    """HMAC token so only the recipient can unsubscribe themselves."""
    return hmac.new(_TOKEN_SECRET.encode(), email.strip().lower().encode(), hashlib.sha256).hexdigest()


def verify_token(email: str, token: str) -> bool:
    """Verify unsubscribe token."""
    if not token:
        return False
    return hmac.compare_digest(make_token(email), token)


def unsubscribe(email: str) -> bool:
    """Mark email as unsubscribed. Returns True if newly added."""
    data = _load()
    email_lower = email.strip().lower()
    if any(u["email"].strip().lower() == email_lower for u in data):
        return False
    data.append({
        "email": email,
        "unsubscribed_at": datetime.now().isoformat(timespec="seconds"),
    })
    _save(data)
    return True


def get_unsubscribers() -> list:
    """List all unsubscribed emails with timestamps."""
    return _load()
