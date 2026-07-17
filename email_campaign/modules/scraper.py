"""Scrape sendquick.com for product info and blog posts"""
import re
import requests
from bs4 import BeautifulSoup

SENDQUICK_BASE = "https://www.sendquick.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

_HEADERS = {"User-Agent": USER_AGENT}

# ── Known product page slugs ──
PRODUCT_PAGES_LIST = [
    ("sendquick-alert-plus", "SendQuick Alert Plus"),
    ("sendquick-ai", "SendQuick AI-in-a-Box"),
    ("sendquick-entera", "SendQuick Entera"),
    ("sendquick-conexa", "SendQuick Conexa (MFA/FIDO2)"),
    ("sendquick-asp", "SendQuick ASP"),
    ("sendquick-cloud", "SendQuick Cloud"),
    ("sendquick-assure", "SendQuick Assure"),
    ("sendquick-avera", "SendQuick Avera"),
    ("sendquick-enterprise", "SendQuick Enterprise"),
    ("sendquick-alert", "SendQuick Alert"),
    ("sendquick-alerter", "SendQuick Alerter"),
    ("sendquick-io", "SendQuick IO"),
    ("sqoope", "SQoope"),
]

PRODUCT_PAGES = {slug: f"{SENDQUICK_BASE}/products/{slug}/" for slug, _ in PRODUCT_PAGES_LIST}


def _soup(url: str) -> BeautifulSoup | None:
    """Fetch URL and return BeautifulSoup object."""
    try:
        r = requests.get(url, headers=_HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException:
        return None


# ── Product Scraping ──


def list_products() -> list[dict]:
    """Return list of known product pages with titles."""
    results = []
    for slug, display_name in PRODUCT_PAGES_LIST:
        url = PRODUCT_PAGES[slug]
        soup = _soup(url)
        if soup is None:
            results.append({"slug": slug, "url": url, "title": display_name, "available": False})
            continue
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else display_name
        h1 = soup.find("h1")
        heading = h1.text.strip() if h1 else display_name
        results.append({"slug": slug, "url": url, "title": heading, "available": True})
    return results


def scrape_product(url: str) -> dict:
    """Scrape a product page and return structured content."""
    soup = _soup(url)
    if soup is None:
        return {"title": "", "description": "", "body_html": "", "sections": {}}

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else ""

    # Try to get meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc.get("content", "") if meta_desc else ""

    # Extract text content from the page body
    body = soup.find("body")
    body_text = body.get_text(separator="\n", strip=True) if body else ""

    # Try to find the main content area (Elementor pages)
    main_content = soup.find("div", class_=re.compile(r"entry-content|elementor"))
    page_html = ""
    if main_content:
        # Remove script, style, nav, footer elements
        for tag in main_content.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        page_html = str(main_content)

    # Build sections for template
    sections = {
        "header": "",
        "intro": f"<p>{description}</p>" if description else "",
        "body": page_html or f"<pre>{body_text[:2000]}</pre>",
        "closing": "",
    }

    return {
        "title": title,
        "description": description,
        "body_html": page_html,
        "body_text": body_text[:3000],
        "sections": sections,
        "url": url,
    }


# ── Blog Scraping ──


def list_blog_posts() -> list[dict]:
    """Return list of recent blog posts from /resources/blog/"""
    soup = _soup(f"{SENDQUICK_BASE}/resources/blog/")
    if soup is None:
        return []

    posts = []
    # Elementor blog posts — look for post cards
    for article in soup.find_all("article"):
        title_el = article.find("h3") or article.find("h2") or article.find(class_=re.compile(r"title|heading"))
        link_el = article.find("a") if title_el else None
        link = link_el.get("href") if link_el else None

        title = ""
        if title_el:
            title = title_el.get_text(strip=True)
        elif link_el:
            title = link_el.get_text(strip=True)

        if not title or not link:
            continue

        # Date
        date_el = article.find("time") or article.find(class_=re.compile(r"date|meta"))
        date = date_el.get_text(strip=True) if date_el else ""

        posts.append({
            "title": title,
            "url": link if link.startswith("http") else f"{SENDQUICK_BASE}{link}",
            "date": date,
        })

    # Fallback: look for elementor post widget items
    if not posts:
        for item in soup.find_all(class_=re.compile(r"elementor-post")):
            title_el = item.find(class_=re.compile(r"elementor-post__title"))
            link_el = title_el.find("a") if title_el else None
            if link_el:
                title = link_el.get_text(strip=True)
                link = link_el.get("href", "")
                date_el = item.find(class_=re.compile(r"elementor-post__date"))
                date = date_el.get_text(strip=True) if date_el else ""
                if title and link:
                    posts.append({
                        "title": title,
                        "url": link if link.startswith("http") else f"{SENDQUICK_BASE}{link}",
                        "date": date,
                    })

    return posts[:20]


def scrape_blog_post(url: str) -> dict:
    """Scrape a single blog post page."""
    soup = _soup(url)
    if soup is None:
        return {"title": "", "content_html": "", "content_text": "", "url": url}

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else ""

    # Find article content
    article = soup.find("article") or soup.find(class_=re.compile(r"entry-content|post-content"))
    content_html = ""
    content_text = ""
    if article:
        for tag in article.find_all(["script", "style"]):
            tag.decompose()
        content_html = str(article)
        content_text = article.get_text(separator="\n", strip=True)

    # Build body_html suitable for email template
    body_html = f"<h2>{title}</h2>\n{content_html}<p><a href='{url}'>Read more →</a></p>"

    return {
        "title": title,
        "content_html": body_html,
        "content_text": content_text[:3000],
        "url": url,
    }
