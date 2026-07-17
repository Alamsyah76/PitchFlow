"""CLI entry point for manual campaign run"""
import os
import json
import time
import argparse
from pathlib import Path
from modules.config import load_env
from modules.xls_reader import read_namecards
from modules.validation import is_valid_email
from modules.log_store import load_log, append_log
from modules.email_builder import build_email_body
from modules.email_sender import send_email


def main():
    parser = argparse.ArgumentParser(description="PitchFlow Email Campaign")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mode uji coba: baca data & tampilkan preview tanpa kirim")
    parser.add_argument("--preview", type=int, default=0,
                        help="Jumlah preview email yang ditampilkan (dry-run, default 3)")
    args = parser.parse_args()

    print("=" * 60)
    print("  SENDQUICK EMAIL CAMPAIGN")
    if args.dry_run:
        print("  🔍 DRY RUN MODE (tidak ada email terkirim)")
    print("=" * 60)

    load_env()
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    sender_name = os.environ.get("SENDER_NAME", "Alamsyah")
    sender_email = os.environ.get("SENDER_EMAIL", "alamsyah@pitchflow.com")
    daily_limit = int(os.environ.get("DAILY_LIMIT", 10))

    if not args.dry_run:
        missing = []
        if not smtp_host: missing.append("SMTP_HOST")
        if not smtp_pass or smtp_pass == "your_password_here":
            missing.append("SMTP_PASSWORD")
        if missing:
            print(f"[ERROR] Konfigurasi belum lengkap di .env: {', '.join(missing)}")
            return

    smtp_config = {
        "host": smtp_host, "port": smtp_port, "username": smtp_user,
        "password": smtp_pass, "sender_name": sender_name, "sender_email": sender_email,
    }

    print(f"[CONFIG] SMTP: {smtp_host}:{smtp_port}")
    print(f"[CONFIG] Sender: {sender_name} <{sender_email}>")
    print(f"[CONFIG] Daily limit: {daily_limit} email")
    print()

    print("[INFO] Membaca kontak dari Namecards...")
    contacts = read_namecards()
    valid_contacts = [c for c in contacts if is_valid_email(c["email"])]
    print(f"[INFO] Kontak dengan email valid: {len(valid_contacts)}/{len(contacts)}")

    if not valid_contacts:
        print("[ERROR] Tidak ada kontak dengan email valid")
        return

    sent_emails = load_log()
    print(f"[INFO] Email sudah pernah dikirim: {len(sent_emails)} kontak")

    pending = [c for c in valid_contacts if c["email"].strip().lower() not in sent_emails]
    print(f"[INFO] Kontak siap dikirim: {len(pending)} kontak")

    if not pending:
        print("[DONE] Semua kontak sudah pernah dikirim!")
        return

    if args.dry_run:
        preview_count = args.preview if args.preview > 0 else 3
        dry_subject = ""
        try:
            tpl_path = Path(__file__).resolve().parent.parent / "templates.json"
            if tpl_path.exists():
                tpl_data = json.loads(tpl_path.read_text())
                tid = tpl_data.get("active_template", "default")
                for t in tpl_data.get("templates", []):
                    if t["id"] == tid:
                        dry_subject = t.get("subject", "")
                        break
        except Exception:
            pass
        print(f"\n[PREVIEW] Menampilkan {min(preview_count, len(pending))} preview email...\n")
        for i, contact in enumerate(pending[:preview_count], 1):
            print(f"  --- Email #{i} ---")
            print(f"  To:   {contact['name']} <{contact['email']}>")
            print(f"  Company: {contact['company']}")
            print(f"  Job:  {contact['job_title']}")
            print(f"  Subject: {dry_subject or '(kosong)'}\n")
        print(f"[DRY-RUN] Selesai. {len(pending)} kontak siap dikirim.")
        print(f"[INFO] Jalankan tanpa --dry-run untuk kirim beneran")
        return

    to_send = pending[:daily_limit]
    print(f"[INFO] Akan mengirim {len(to_send)} email hari ini...\n")

    # Load template aktif
    tpl_subject = ""
    tpl_body = None
    try:
        tpl_path = Path(__file__).resolve().parent.parent / "templates.json"
        if tpl_path.exists():
            tpl_data = json.loads(tpl_path.read_text())
            tid = tpl_data.get("active_template", "default")
            for t in tpl_data.get("templates", []):
                if t["id"] == tid:
                    tpl_subject = t.get("subject", "")
                    tpl_body = t.get("body_html", "") or None
                    break
    except Exception:
        pass

    success_count = 0
    fail_count = 0

    for i, contact in enumerate(to_send, 1):
        print(f"  [{i}/{len(to_send)}] Mengirim ke {contact['email']} ({contact['name']})...", end=" ")
        html = build_email_body(contact, template_body=tpl_body)
        ok, err = send_email(smtp_config, contact["email"], contact["name"], html, subject=tpl_subject)
        if ok:
            print("✅ BERHASIL")
            append_log(contact["name"], contact["email"], contact.get("company", ""), "sent")
            success_count += 1
        else:
            print(f"❌ GAGAL: {err[:80]}")
            append_log(contact["name"], contact["email"], contact.get("company", ""), "failed", err)
            fail_count += 1
        if i < len(to_send):
            time.sleep(3)

    print()
    print("=" * 60)
    print(f"  HASIL CAMPAIGN HARI INI")
    print(f"  ✅ Berhasil: {success_count}")
    print(f"  ❌ Gagal:    {fail_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
