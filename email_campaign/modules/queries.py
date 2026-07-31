"""Campaign queries — composite data access"""
import os
from modules.config import load_env, XLS_FILE, TEST_EMAILS
from modules.validation import is_valid_email
from modules.storage import load_extra, load_merged_contacts, save_merged_contacts
from modules.xls_reader import merge_xls_into_all
from modules.log_store import load_log


def get_all_contacts():
    """Return ALL contacts with valid emails (merged + manual + test emails)"""
    load_env()
    merged = load_merged_contacts()

    # Migrasi satu kali: jika contacts_all.json kosong tapi XLS_FILE ada
    if not merged and XLS_FILE.exists():
        merge_xls_into_all(XLS_FILE)
        merged = load_merged_contacts()

    extra = load_extra()
    all_c = [c for c in merged if is_valid_email(c.get("email", ""))]
    for c in extra.get("manual", []):
        if is_valid_email(c.get("email", "")):
            all_c.append(c)

    # Always include test emails so they're never blocked
    test_contacts = []
    seen_emails = {c.get("email", "").strip().lower() for c in all_c}
    for te in TEST_EMAILS:
        if te.lower() not in seen_emails:
            test_contacts.append({"name": "Test Target", "email": te, "company": "", "job_title": ""})
    all_c.extend(test_contacts)

    return all_c


def get_all_contacts_raw():
    """Return ALL contacts including invalid emails (for stats)"""
    load_env()
    merged = load_merged_contacts()

    if not merged and XLS_FILE.exists():
        merge_xls_into_all(XLS_FILE)
        merged = load_merged_contacts()

    extra = load_extra()
    all_c = list(merged)
    for c in extra.get("manual", []):
        all_c.append(c)
    return all_c


def get_all_pending():
    """Return pending contacts (merged + manual, excluding sent, bounced AND unsubscribed)"""
    load_env()
    merged = load_merged_contacts()
    sent = load_log()
    sent_set = {e.strip().lower() for e in sent}
    from modules.log_store import load_bounced
    bounced_set = load_bounced()
    from modules.unsubscribe_store import unsubscribed_set
    unsub_set = unsubscribed_set()
    extra = load_extra()

    pending = []
    test_email_lower = {e.strip().lower() for e in TEST_EMAILS}

    def _excluded(email_lower):
        """Excluded if sent, bounced, or unsubscribed (unless test email)"""
        return (email_lower in sent_set or email_lower in bounced_set or email_lower in unsub_set) and email_lower not in test_email_lower

    for c in merged:
        if is_valid_email(c.get("email", "")):
            email_lower = c["email"].strip().lower()
            if not _excluded(email_lower):
                pending.append(c)

    for c in extra.get("manual", []):
        email_lower = c.get("email", "").strip().lower()
        if not _excluded(email_lower) and is_valid_email(c.get("email", "")):
            pending.append(c)

    return pending


def get_campaign_stats():
    """Get campaign overview statistics — total, valid, sent, pending with accurate counts"""
    try:
        load_env()
    except SystemExit:
        pass
    from modules.config import load_settings, TEST_EMAILS
    settings = load_settings()

    all_contacts_raw = get_all_contacts_raw()
    all_contacts_valid = get_all_contacts()
    sent_emails = load_log()
    from modules.log_store import load_bounced
    bounced_emails = load_bounced()

    total = len(all_contacts_raw)
    valid = len(all_contacts_valid)
    # attempted = sudah dikirim ATAU bounce (bounce adalah subset dari yang dikirim)
    attempted = sent_emails | bounced_emails
    sent = len(sent_emails)
    bounced = len(bounced_emails)

    # Pending — hitung dari kontak yang VALID & ada di list & belum di-attempt
    # (sama persis dengan logika preview, jadi angka selalu sinkron)
    test_email_lower = {e.strip().lower() for e in TEST_EMAILS}
    pending = 0
    for c in all_contacts_valid:
        e = c.get("email", "").strip().lower()
        if e not in attempted or e in test_email_lower:
            pending += 1
    test_in_attempted = attempted & test_email_lower

    return {
        "total_contacts": total,
        "valid_emails": valid,
        "already_sent": sent,
        "bounced": bounced,
        "pending": pending,
        "test_emails_available": len(test_in_attempted),
        "daily_limit": settings.get("daily_limit", int(os.environ.get("DAILY_LIMIT", 10))),
    }
