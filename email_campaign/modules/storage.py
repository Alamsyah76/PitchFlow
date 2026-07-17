"""Contact data storage (JSON files)"""
import json
from modules.config import EXTRA_FILE, ALL_CONTACTS_FILE


def load_extra():
    """Load manually added contacts + edits from JSON"""
    if EXTRA_FILE.exists():
        try:
            return json.loads(EXTRA_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            pass
    return {"manual": [], "edits": {}}


def save_extra(data: dict):
    """Save extra contacts to JSON"""
    EXTRA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_merged_contacts():
    """Load all merged contacts from contacts_all.json (return [] jika kosong)"""
    if ALL_CONTACTS_FILE.exists():
        try:
            data = json.loads(ALL_CONTACTS_FILE.read_text())
            return data.get("contacts", [])
        except Exception:
            pass
    return []


def save_merged_contacts(contacts: list):
    """Save merged contacts to contacts_all.json"""
    ALL_CONTACTS_FILE.write_text(json.dumps({"contacts": contacts}, indent=2, ensure_ascii=False))
