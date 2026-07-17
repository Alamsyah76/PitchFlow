"""Blog Monitor — detect new blog posts on sendquick.com and auto-send newsletter"""
import json
import time as time_module
from pathlib import Path
from datetime import datetime
from modules.scraper import list_blog_posts, scrape_blog_post

SENT_FILE = Path(__file__).resolve().parent.parent / "blog_sent.json"

def _load_sent() -> set:
    """Load set of already-sent blog post URLs"""
    if not SENT_FILE.exists():
        return set()
    try:
        data = json.loads(SENT_FILE.read_text(encoding="utf-8"))
        return set(data.get("sent_urls", []))
    except (json.JSONDecodeError, KeyError):
        return set()

def _save_sent(urls: set):
    """Save sent blog post URLs"""
    data = {
        "sent_urls": sorted(urls),
        "last_checked": datetime.now().isoformat(),
        "total_sent": len(urls),
    }
    SENT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def check_for_new_posts() -> list[dict]:
    """Check blog page, return list of NEW posts not yet sent.
    Also marks newly found posts in the sent file.
    """
    current_posts = list_blog_posts()
    sent_urls = _load_sent()

    new_posts = []
    for post in current_posts:
        if post["url"] not in sent_urls:
            new_posts.append(post)

    # Only save if there are new posts — avoids unnecessary writes
    if new_posts:
        all_urls = sent_urls | {p["url"] for p in current_posts}
        _save_sent(all_urls)

    return new_posts

def get_status() -> dict:
    """Return monitor status"""
    sent_urls = _load_sent()
    SENT_FILE.touch(exist_ok=True)
    data = {}
    try:
        data = json.loads(SENT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return {
        "total_sent": len(sent_urls),
        "last_checked": data.get("last_checked", "never"),
        "sent_urls": sorted(sent_urls),
    }

def reset_sent():
    """Reset sent tracking (for testing)"""
    _save_sent(set())
