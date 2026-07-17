"""
Log Store — read & write campaign log (CSV)
=============================================
Single responsibility: persist and retrieve send history.
"""
import csv
from datetime import datetime
from modules.config import LOG_FILE


def load_log():
    """Return set of email addresses that were SUCCESSFULLY sent (status='sent')"""
    sent = set()
    if LOG_FILE.exists():
        with open(LOG_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                # row: timestamp, email, name, company, status, error
                if len(row) >= 5 and row[4].strip().lower() == "sent":
                    sent.add(row[1].strip().lower())
    return sent


def load_sent_log_detailed():
    """Return dict of {email_lower: {timestamp, name, template_id}} for SENT emails"""
    sent = {}
    if LOG_FILE.exists():
        with open(LOG_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 5 and row[4].strip().lower() == "sent":
                    email = row[1].strip().lower()
                    tid = row[6].strip() if len(row) >= 7 else ""
                    sent[email] = {
                        "timestamp": row[0],
                        "name": row[2],
                        "template_id": tid,
                    }
    return sent


def append_log(name, email, company, status, error_msg="", template_id=""):
    """Append one log entry to CSV (with template_id tracking)"""
    file_exists = LOG_FILE.exists()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "email", "name", "company", "status", "error", "template_id"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            email.strip().lower(),
            name,
            company,
            status,
            error_msg,
            template_id,
        ])
