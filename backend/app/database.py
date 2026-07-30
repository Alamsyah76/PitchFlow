"""SQLite database — replace semua JSON file, zero external dependencies"""
import os, json, sqlite3, threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
DB_PATH = HOME / "pitchflow.db"

_local = threading.local()


def _get_db() -> sqlite3.Connection:
    """Thread-safe connection — setiap thread dapat koneksi sendiri"""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")     # Concurrent reads
        _local.conn.execute("PRAGMA busy_timeout=5000")    # Wait 5s if locked
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    """Buat tabel jika belum ada — panggil sekali di startup"""
    db = _get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL DEFAULT '',
            tier TEXT NOT NULL DEFAULT 'free',
            avatar TEXT DEFAULT '',
            openai_api_key TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS otps (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS usage_monthly (
            identifier TEXT NOT NULL,
            month TEXT NOT NULL,
            konten INTEGER NOT NULL DEFAULT 0,
            images INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (identifier, month)
        );

        CREATE TABLE IF NOT EXISTS usage_daily (
            identifier TEXT NOT NULL,
            day TEXT NOT NULL,
            chat INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (identifier, day)
        );

        CREATE TABLE IF NOT EXISTS usage_trial (
            identifier TEXT PRIMARY KEY,
            images_used INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sender_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            company TEXT NOT NULL DEFAULT '',
            logo_b64 TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            subject TEXT NOT NULL DEFAULT '',
            body_html TEXT NOT NULL DEFAULT '',
            body_text TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS library_items (
            id TEXT PRIMARY KEY,
            user_email TEXT NOT NULL,
            pdf_filename TEXT NOT NULL DEFAULT '',
            selected_topic TEXT NOT NULL DEFAULT '',
            caption_text TEXT NOT NULL DEFAULT '',
            hashtags TEXT NOT NULL DEFAULT '[]',
            image_url TEXT DEFAULT '',
            industry TEXT NOT NULL DEFAULT 'Lainnya',
            score INTEGER NOT NULL DEFAULT 5,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chat_cache (
            question_hash TEXT PRIMARY KEY,
            answer TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_library_user ON library_items(user_email);
        CREATE INDEX IF NOT EXISTS idx_usage_monthly_id ON usage_monthly(identifier);
        CREATE INDEX IF NOT EXISTS idx_usage_daily_id ON usage_daily(identifier);
    """)
    db.commit()


# ── User & Auth ──

def upsert_user(email: str, name: str, tier: str = "free"):
    db = _get_db()
    db.execute("INSERT INTO users (email, name, tier) VALUES (?, ?, ?) "
               "ON CONFLICT(email) DO UPDATE SET name=excluded.name",
               (email, name, tier))
    db.commit()

def get_user(email: str) -> Optional[dict]:
    row = _get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    return dict(row) if row else None

def get_all_users() -> list:
    return [dict(r) for r in _get_db().execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()]

def update_user_tier(email: str, tier: str):
    _get_db().execute("UPDATE users SET tier=? WHERE email=?", (tier, email))
    _get_db().commit()

def update_user_avatar(email: str, avatar: str):
    _get_db().execute("UPDATE users SET avatar=? WHERE email=?", (avatar, email))
    _get_db().commit()


def save_openai_key(email: str, api_key: str):
    """Simpan OpenAI API key untuk user tertentu (BYOK)."""
    _get_db().execute("UPDATE users SET openai_api_key=? WHERE email=?", (api_key, email))
    _get_db().commit()


def get_openai_key(email: str) -> str:
    """Ambil OpenAI API key user, atau None kalau tidak set."""
    row = _get_db().execute("SELECT openai_api_key FROM users WHERE email=?", (email,)).fetchone()
    return row["openai_api_key"] if row and row["openai_api_key"] else ""


# ── OTP ──

def save_otp(email: str, code: str, name: str = ""):
    expires = (datetime.now() + timedelta(minutes=10)).isoformat()
    _get_db().execute("INSERT INTO otps (email, code, expires_at, name) VALUES (?, ?, ?, ?) "
                       "ON CONFLICT(email) DO UPDATE SET code=excluded.code, expires_at=excluded.expires_at, name=excluded.name",
                       (email, code, expires, name))
    _get_db().commit()

def verify_otp(email: str, code: str) -> Optional[dict]:
    row = _get_db().execute("SELECT * FROM otps WHERE email=? AND code=?", (email, code)).fetchone()
    if row:
        row = dict(row)
        expires = datetime.fromisoformat(row["expires_at"])
        if expires > datetime.now():
            _get_db().execute("DELETE FROM otps WHERE email=?", (email,))
            _get_db().commit()
            return get_user(email)
    return None


# ── Rate Limit (usage) ──

def _get_month_key() -> str:
    return datetime.now().strftime("%Y-%m")

def _get_day_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_usage_konten(identifier: str) -> dict:
    month = _get_month_key()
    row = _get_db().execute("SELECT konten FROM usage_monthly WHERE identifier=? AND month=?",
                             (identifier, month)).fetchone()
    used = row["konten"] if row else 0
    return {"used": used}

def increment_konten(identifier: str):
    month = _get_month_key()
    _get_db().execute("INSERT INTO usage_monthly (identifier, month, konten) VALUES (?, ?, 1) "
                       "ON CONFLICT(identifier, month) DO UPDATE SET konten=konten+1",
                       (identifier, month))
    _get_db().commit()

def get_usage_image(identifier: str) -> dict:
    month = _get_month_key()
    row = _get_db().execute("SELECT images FROM usage_monthly WHERE identifier=? AND month=?",
                             (identifier, month)).fetchone()
    used = row["images"] if row else 0
    return {"used": used}

def increment_image(identifier: str):
    month = _get_month_key()
    _get_db().execute("INSERT INTO usage_monthly (identifier, month, images) VALUES (?, ?, 1) "
                       "ON CONFLICT(identifier, month) DO UPDATE SET images=images+1",
                       (identifier, month))
    _get_db().commit()

def get_usage_chat(identifier: str) -> int:
    day = _get_day_key()
    row = _get_db().execute("SELECT chat FROM usage_daily WHERE identifier=? AND day=?",
                             (identifier, day)).fetchone()
    return row["chat"] if row else 0

def increment_chat(identifier: str):
    day = _get_day_key()
    _get_db().execute("INSERT INTO usage_daily (identifier, day, chat) VALUES (?, ?, 1) "
                       "ON CONFLICT(identifier, day) DO UPDATE SET chat=chat+1",
                       (identifier, day))
    _get_db().commit()


# ── Sender Settings ──

def get_sender_settings() -> dict:
    row = _get_db().execute("SELECT * FROM sender_settings WHERE id=1").fetchone()
    if row:
        return dict(row)
    return {"name": "", "email": "", "company": "", "logo_b64": ""}

def save_sender_settings(name: str, email: str, company: str, logo_b64: str):
    _get_db().execute("INSERT INTO sender_settings (id, name, email, company, logo_b64) VALUES (1, ?, ?, ?, ?) "
                       "ON CONFLICT(id) DO UPDATE SET name=excluded.name, email=excluded.email, "
                       "company=excluded.company, logo_b64=excluded.logo_b64",
                       (name, email, company, logo_b64))
    _get_db().commit()


# ── Library ──

def get_library(user_email: str) -> list:
    rows = _get_db().execute("SELECT * FROM library_items WHERE user_email=? ORDER BY timestamp DESC",
                              (user_email,)).fetchall()
    return [dict(r) for r in rows]

def add_library_item(user_email: str, item: dict):
    _get_db().execute(
        "INSERT INTO library_items (id, user_email, pdf_filename, selected_topic, caption_text, "
        "hashtags, image_url, industry, score, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (item["id"], user_email, item.get("pdf_filename", ""), item.get("selected_topic", ""),
         item.get("caption_text", ""), json.dumps(item.get("hashtags", [])),
         item.get("image_url", ""), item.get("industry", "Lainnya"),
         item.get("score", 5), item.get("timestamp", datetime.now().isoformat()))
    )
    _get_db().commit()

def replace_lowest_library_item(user_email: str, item: dict):
    """Ganti item dengan score terendah untuk user ini"""
    lowest = _get_db().execute(
        "SELECT id, score FROM library_items WHERE user_email=? ORDER BY score ASC LIMIT 1",
        (user_email,)).fetchone()
    if lowest:
        _get_db().execute("DELETE FROM library_items WHERE id=?", (lowest["id"],))
    add_library_item(user_email, item)

def count_library_items(user_email: str) -> int:
    row = _get_db().execute("SELECT COUNT(*) as cnt FROM library_items WHERE user_email=?",
                             (user_email,)).fetchone()
    return row["cnt"]


# ── Chat Cache ──

def get_cached_answer(question: str) -> Optional[str]:
    import hashlib
    qh = hashlib.md5(question.lower().encode()).hexdigest()
    row = _get_db().execute("SELECT answer FROM chat_cache WHERE question_hash=?", (qh,)).fetchone()
    return row["answer"] if row else None

def cache_answer(question: str, answer: str):
    import hashlib
    qh = hashlib.md5(question.lower().encode()).hexdigest()
    _get_db().execute("INSERT INTO chat_cache (question_hash, answer) VALUES (?, ?) "
                       "ON CONFLICT(question_hash) DO UPDATE SET answer=excluded.answer",
                       (qh, answer))
    _get_db().commit()
