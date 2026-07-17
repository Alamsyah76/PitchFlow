"""Sender settings — name, email, logo (SQLite-based)"""
import os
from app.database import get_sender_settings as db_get, save_sender_settings as db_save


def get_sender_config() -> dict:
    """Get sender config"""
    data = db_get()
    return {
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "logo_b64": data.get("logo_b64", ""),
        "company": data.get("company", ""),
    }


def save_sender_config(name: str, email: str, company: str = "", logo_b64: str = ""):
    db_save(name, email, company, logo_b64)
