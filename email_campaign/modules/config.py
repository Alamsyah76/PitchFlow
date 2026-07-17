"""
Config — path constants & environment loader
=============================================
Single responsibility: load .env and define global paths.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # email_campaign/
PROJECT_ROOT = BASE_DIR.parent                     # project root
REPORT_DIR = PROJECT_ROOT / "Report"
XLS_FILE = REPORT_DIR / "Alams-Tekno database.xls"
LOG_FILE = BASE_DIR / "log.csv"
ENV_FILE = BASE_DIR / ".env"
EXTRA_FILE = BASE_DIR / "contacts_extra.json"
ALL_CONTACTS_FILE = BASE_DIR / "contacts_all.json"
SETTINGS_FILE = BASE_DIR / "settings.json"
ATTACHMENTS_DIR = BASE_DIR / "attachments"

# Test email whitelist — selalu bisa dikirim ulang tanpa terhalang log
TEST_EMAILS = {
    "alams.kombet@gmail.com",
    "alams.kombet@yahoo.com",
}


def load_settings() -> dict:
    """Load campaign settings from settings.json"""
    default = {
        "daily_limit": 10,
        "smtp_host": "",
        "smtp_port": 465,
        "smtp_username": "",
        "smtp_password": "",
        "imap_host": "",
        "imap_port": 993,
        "sender_name": "",
        "sender_email": "",
    }
    if SETTINGS_FILE.exists():
        try:
            import json
            data = json.loads(SETTINGS_FILE.read_text())
            default.update(data)
        except Exception:
            pass
    return default


def save_settings(data: dict):
    """Save campaign settings to settings.json"""
    import json
    current = load_settings()
    current.update(data)
    SETTINGS_FILE.write_text(json.dumps(current, indent=2, ensure_ascii=False))
    # Also update runtime env so send_batch picks it up
    if "daily_limit" in current:
        os.environ["DAILY_LIMIT"] = str(current["daily_limit"])


def load_env():
    """Load .env file manually into os.environ"""
    env_path = ENV_FILE
    if not env_path.exists():
        print(f"[ERROR] File .env tidak ditemukan di {env_path}")
        print("[INFO] Copy .env.example ke .env dan isi credentials SMTP kamu")
        sys.exit(1)

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")
