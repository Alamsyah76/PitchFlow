"""Content Library — manage PDF brochures, compro, case studies"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

LIBRARY_DIR = Path(__file__).resolve().parent.parent / "content_library"

# Default category folders
CATEGORIES = {
    "compro": "Company Profile",
    "brochures": "Product Brochures",
    "case_studies": "Case Studies",
}

def _ensure_dirs():
    """Create library folders if not exist"""
    for slug in CATEGORIES:
        (LIBRARY_DIR / slug).mkdir(parents=True, exist_ok=True)

def list_files(category: str = "") -> list[dict]:
    """List files in library, optionally filtered by category"""
    _ensure_dirs()
    results = []

    categories = [category] if category else list(CATEGORIES.keys())
    for cat in categories:
        folder = LIBRARY_DIR / cat
        if not folder.exists():
            continue
        for f in sorted(folder.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                results.append({
                    "name": f.name,
                    "category": cat,
                    "category_label": CATEGORIES.get(cat, cat),
                    "size": f.stat().st_size,
                    "size_label": _format_size(f.stat().st_size),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "path": str(f.relative_to(LIBRARY_DIR)),
                })
    return results

def delete_file(category: str, filename: str) -> bool:
    """Delete a file from library"""
    filepath = LIBRARY_DIR / category / filename
    if filepath.exists() and filepath.is_file():
        filepath.unlink()
        return True
    return False

def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size/1024:.0f} KB"
    else:
        return f"{size/(1024*1024):.1f} MB"
