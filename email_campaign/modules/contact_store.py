"""contact_store — migrated to validation.py + xls_reader.py + storage.py
==================================================
Import masih berfungsi untuk backward compatibility.
"""
from modules.validation import is_valid_email
from modules.xls_reader import read_namecards
from modules.storage import load_extra, save_extra, load_merged_contacts, save_merged_contacts
from modules.xls_reader import merge_xls_into_all
