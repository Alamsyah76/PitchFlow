"""
PitchFlow Email Test
=========================================================
Gunakan SMTP credentials dari email_campaign/.env
"""
import sys
import os
from pathlib import Path

BASE = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE))

from modules.config import load_env
from modules.email_builder import build_email_body
from modules.email_sender import send_email

load_env()

SMTP_HOST = os.environ.get("SMTP_HOST", "mail.sendquick.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
SMTP_USER = os.environ.get("SMTP_USERNAME", "")
SMTP_PASS = os.environ.get("SMTP_PASSWORD", "")
SENDER_NAME = os.environ.get("SENDER_NAME", "Alamsyah")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "alamsyah@sendquick.com")

TO_NAME = "Alamsyah"
TO_EMAIL = "alamsyah@sendquick.com"

if SMTP_PASS == "your_password_here" or not SMTP_PASS:
    print("❌ SMTP_PASSWORD masih placeholder. Isi dulu di .env")
    sys.exit(1)

contact = {
    "name": TO_NAME,
    "email": TO_EMAIL,
    "company": "",
    "job_title": "Indonesia Region",
}
html = build_email_body(contact)

smtp_config = {
    "host": SMTP_HOST, "port": SMTP_PORT,
    "username": SMTP_USER, "password": SMTP_PASS,
    "sender_name": SENDER_NAME, "sender_email": SENDER_EMAIL,
}

print(f"Mengirim test email ke {TO_EMAIL}...")
print(f"  Server: {SMTP_HOST}:{SMTP_PORT}")
print(f"  Template: AI-in-a-Box ✅")

ok, err = send_email(smtp_config, TO_EMAIL, TO_NAME, html)
if ok:
    print(f"  ✅ BERHASIL TERKIRIM ke {TO_EMAIL}")
    print(f"  📧 Cek inbox alamsyah@sendquick.com")
else:
    print(f"  ❌ GAGAL: {err}")
