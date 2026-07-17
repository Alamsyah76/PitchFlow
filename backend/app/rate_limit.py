"""Rate limit & pricing tier system — SQLite-based, no JSON"""
import os
from datetime import datetime
from app.database import get_usage_konten, increment_konten as db_inc_konten, get_usage_image, increment_image as db_inc_image, get_usage_chat, increment_chat as db_inc_chat

TIERS = {
    "free": {
        "label": "Free", "price": "Rp 0",
        "konten_per_bulan": 3, "topic_per_file": 1,
        "image_quality": None, "trial_image": 1,
        "chat_per_hari": None,  # unlimited
        "library": 0, "email_kontak": 0, "email_kirim": False,
    },
    "basic": {
        "label": "Basic", "price": "Rp 49rb/bln",
        "konten_per_bulan": 20, "topic_per_file": 2,
        "image_quality": "standard", "trial_image": 0,
        "chat_per_hari": None,
        "library": 20, "email_kontak": 0, "email_kirim": False,
    },
    "bisnis": {
        "label": "Bisnis", "price": "Rp 149rb/bln",
        "konten_per_bulan": 100, "topic_per_file": 2,
        "image_quality": "hd", "trial_image": 0,
        "chat_per_hari": None,
        "library": 100, "email_kontak": 100, "email_kirim": True,
    },
    "pro": {
        "label": "Pro", "price": "Rp 299rb/bln",
        "konten_per_bulan": None, "topic_per_file": 2,
        "image_quality": "hd_plus", "trial_image": 0,
        "chat_per_hari": None,
        "library": None, "email_kontak": None, "email_kirim": True,
    },
}


def _get_month_key() -> str:
    return datetime.now().strftime("%Y-%m")


def get_tier(identifier: str = "default") -> str:
    """Get user tier — dev mode first, then user-specific"""
    if os.environ.get("PITCHFLOW_DEV", "").strip() in ("1", "true", "yes"):
        return "pro"
    try:
        from app.auth_user import get_tier_for_email
        user_tier = get_tier_for_email(identifier)
        if user_tier in TIERS:
            return user_tier
    except: pass
    env_tier = os.environ.get("PITCHFLOW_TIER", "").strip().lower()
    if env_tier in TIERS:
        return env_tier
    return "free"


def set_tier(identifier: str, tier: str):
    if tier not in TIERS: tier = "free"
    from app.database import get_db
    db = get_db()
    db.execute("UPDATE users SET tier=? WHERE email=?", (tier, identifier))
    db.commit()


def check_konten_limit(identifier: str = "default") -> dict:
    tier_name = get_tier(identifier)
    tier = TIERS[tier_name]
    limit = tier["konten_per_bulan"]
    if limit is None:
        return {"allowed": True, "used": 0, "limit": None}
    usage = get_usage_konten(identifier)
    used = usage["used"]
    return {"allowed": used < limit, "used": used, "limit": limit}


def increment_konten(identifier: str = "default"):
    db_inc_konten(identifier)


def check_image_limit(identifier: str = "default") -> dict:
    tier_name = get_tier(identifier)
    tier = TIERS[tier_name]
    if tier_name == "free":
        from app.database import get_db
        row = get_db().execute("SELECT images_used FROM usage_trial WHERE identifier=?", (identifier,)).fetchone()
        used = row["images_used"] if row else 0
        allowed = used < tier["trial_image"]
        return {"allowed": allowed, "used": used, "limit": tier["trial_image"], "quality": None if allowed else None}
    limit = tier["konten_per_bulan"]
    if limit is None:
        return {"allowed": True, "used": 0, "limit": None, "quality": tier["image_quality"]}
    usage = get_usage_image(identifier)
    used = usage["used"]
    return {"allowed": used < limit, "used": used, "limit": limit, "quality": tier["image_quality"]}


def increment_image(identifier: str = "default"):
    tier_name = get_tier(identifier)
    if tier_name == "free":
        from app.database import get_db
        db = get_db()
        db.execute("INSERT INTO usage_trial (identifier, images_used) VALUES (?, 1) "
                    "ON CONFLICT(identifier) DO UPDATE SET images_used=images_used+1", (identifier,))
        db.commit()
    else:
        db_inc_image(identifier)


def check_chat_limit(identifier: str = "default") -> dict:
    """Chat is free — no limit for any tier"""
    return {"allowed": True, "used": 0, "limit": None}


def increment_chat(identifier: str = "default"):
    pass


def get_usage_status(identifier: str = "default") -> dict:
    tier_name = get_tier(identifier)
    tier = TIERS[tier_name]
    konten_usage = get_usage_konten(identifier)
    image_usage = get_usage_image(identifier)
    return {
        "tier": tier_name,
        "tier_label": tier["label"],
        "konten": {"used": konten_usage["used"], "limit": tier["konten_per_bulan"]},
        "image": {"used": image_usage["used"], "limit": tier["konten_per_bulan"], "quality": tier["image_quality"]},
        "chat": {"used": 0, "limit": None},
        "library": tier["library"],
        "email": {"kontak": tier["email_kontak"], "can_send": tier["email_kirim"]},
    }
