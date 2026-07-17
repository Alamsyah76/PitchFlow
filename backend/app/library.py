"""Library per-user — SQLite-based"""
import os, json
from app.database import get_library as db_get, add_library_item as db_add, replace_lowest_library_item as db_replace, count_library_items as db_count


def get_library(user_email: str) -> list:
    """Ambil semua library item milik user — parse hashtags JSON"""
    items = db_get(user_email)
    for item in items:
        if isinstance(item.get("hashtags"), str):
            try: item["hashtags"] = json.loads(item["hashtags"])
            except: item["hashtags"] = []
    return items


def add_item(user_email: str, item: dict) -> dict:
    """Tambah satu item ke library user, enforce limit sesuai tier"""
    from app.rate_limit import get_tier
    tier = get_tier(user_email)
    limits = {"free": 0, "basic": 20, "bisnis": 100, "pro": 999999}
    max_items = limits.get(tier, 0)

    count = db_count(user_email)
    if max_items > 0 and count >= max_items:
        db_replace(user_email, item)
    else:
        db_add(user_email, item)
    return item


def get_limit(user_email: str) -> int:
    from app.rate_limit import get_tier
    tier = get_tier(user_email)
    return {"free": 0, "basic": 20, "bisnis": 100, "pro": 999999}.get(tier, 0)


def save_library(user_email: str, items: list):
    """Replace all items (for admin use) — hapus existing lalu insert ulang"""
    from app.database import get_db
    db = get_db()
    db.execute("DELETE FROM library_items WHERE user_email=?", (user_email,))
    for item in items:
        db_add(user_email, item)
    db.commit()
