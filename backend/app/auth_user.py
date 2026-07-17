"""Auth — Register + OTP Login, user & tier management, SQLite-based"""
import os, random, time
from pathlib import Path
from datetime import datetime
from app.database import upsert_user, get_user, get_all_users, update_user_tier, update_user_avatar, save_otp, verify_otp as db_verify_otp

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
DEFAULT_TIER = "free"


# ── Users ──

def register_user(name: str, email: str) -> bool:
    """Daftar user baru. Return False jika email sudah terdaftar."""
    email_lower = email.strip().lower()
    existing = get_user(email_lower)
    if existing:
        return False
    upsert_user(email_lower, name.strip(), DEFAULT_TIER)
    return True


def get_user(email: str) -> dict | None:
    return get_user(email.strip().lower())


def set_user_tier(email: str, tier: str):
    update_user_tier(email.strip().lower(), tier)


def verify_user(email: str):
    """Tandai user sebagai verified (OTP berhasil)"""
    pass  # OTP verification already deletes the OTP


def get_users() -> list:
    """Get all users (for admin panel)"""
    return get_all_users()


def get_tier_for_email(email: str) -> str:
    """Get user's tier, fallback ke free"""
    user = get_user(email)
    if user:
        return user.get("tier", DEFAULT_TIER)
    return DEFAULT_TIER


# ── OTP ──

def generate_otp(email: str) -> str:
    """Generate 6-digit OTP, simpan dengan expiry 10 menit"""
    code = f"{random.randint(100000, 999999)}"
    # Cari nama user jika sudah register
    user = get_user(email)
    name = user.get("name", "") if user else ""
    save_otp(email.strip().lower(), code, name)
    return code


def verify_otp(email: str, code: str) -> bool:
    """Verifikasi OTP. Return True jika valid."""
    result = db_verify_otp(email.strip().lower(), code.strip())
    return result is not None
