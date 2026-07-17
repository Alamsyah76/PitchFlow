"""Carousel Generator — image with text overlay, no external image API needed"""
import os
import json
import textwrap
import uuid
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "carousel"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _find_font(size: int):
    """Find available font"""
    candidates = [
        r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _generate_theme(topic_title: str, caption: str) -> dict:
    """Generate color theme + visual concept from content using GPT"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "Generate a visual theme for a LinkedIn carousel. Return JSON with: primary_hex, secondary_hex, accent_hex, bg_style (gradient/solid), visual_concept (short description). Professional, clean, corporate style. Dark text on light bg preferred."
        }, {
            "role": "user",
            "content": f"Topic: {topic_title}\n\nCaption: {caption[:1000]}"
        }],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _draw_gradient(draw: ImageDraw, w: int, h: int, color1: tuple, color2: tuple):
    """Draw vertical gradient background"""
    for y in range(h):
        ratio = y / h
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_accent_shape(draw: ImageDraw, w: int, h: int, color: tuple):
    """Draw subtle accent shapes"""
    # Circle top-right
    draw.ellipse([w-200, -100, w+50, 150], fill=(*color, 30), outline=None)
    # Circle bottom-left  
    draw.ellipse([-80, h-180, 120, h+20], fill=(*color, 20), outline=None)


def _extract_slides(caption: str, max_slides: int = 3) -> list:
    """Split caption into slides"""
    paragraphs = [p.strip() for p in caption.split("\n\n") if p.strip()]
    if len(paragraphs) >= max_slides:
        return paragraphs[:max_slides]
    sentences = caption.replace("! ", ". ").replace("? ", ". ").split(". ")
    slides = []
    current = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(current) + len(s) > 300:
            if current:
                slides.append(current.rstrip("."))
            current = s + "."
        else:
            current += " " + s + "."
    if current:
        slides.append(current.rstrip("."))
    return slides[:max_slides]


def _draw_text_slide(
    draw: ImageDraw,
    w: int, h: int,
    title: str,
    body_text: str,
    accent_color: tuple,
    slide_num: int,
    total_slides: int,
):
    """Draw text on a slide"""
    title_font = _find_font(44)
    body_font = _find_font(26)
    page_font = _find_font(18)

    margin_x = 80
    y = 80

    # Title with accent line
    draw.rectangle([margin_x, y, margin_x + 60, y + 6], fill=accent_color)
    y += 20

    title_lines = textwrap.wrap(title, width=30)
    for line in title_lines:
        draw.text((margin_x, y), line, fill="white", font=title_font)
        y += 52

    y += 20

    # Body text
    para_lines = textwrap.wrap(body_text, width=55)
    for line in para_lines:
        draw.text((margin_x, y), line, fill=(220, 220, 220), font=body_font)
        y += 34
        if y > h - 80:
            break

    # Page number
    page_text = f"{slide_num + 1} / {total_slides}"
    draw.text((w - margin_x - 40, h - 50), page_text, fill=(150, 150, 150), font=page_font)


def generate_carousel(
    topic_title: str,
    caption: str,
    hashtags: list = None,
    doc_name: str = "",
) -> dict:
    """Generate carousel slides with text overlay"""
    carousel_id = str(uuid.uuid4())[:8]

    # 1. Generate theme via GPT
    theme = _generate_theme(topic_title, caption)
    primary = _hex_to_rgb(theme.get("primary_hex", "#1a73e8"))
    secondary = _hex_to_rgb(theme.get("secondary_hex", "#0d47a1"))
    accent = _hex_to_rgb(theme.get("accent_hex", "#4fc3f7"))

    # 2. Extract slides from caption
    slides = _extract_slides(caption)
    if not slides:
        slides = [caption]

    total = len(slides)
    W, H = 1200, 675  # 16:9 aspect ratio

    image_paths = []

    for i, slide_text in enumerate(slides):
        img = Image.new("RGB", (W, H), primary)
        draw = ImageDraw.Draw(img, "RGBA")

        # Gradient background
        _draw_gradient(draw, W, H, primary, secondary)

        # Accent shapes
        _draw_accent_shape(draw, W, H, accent)

        # Title on first slide, body on others
        if i == 0:
            _draw_text_slide(draw, W, H, topic_title, slide_text, accent, i, total)
        else:
            _draw_text_slide(draw, W, H, "", slide_text, accent, i, total)

        # Save
        filename = f"{carousel_id}_slide_{i+1}.jpg"
        img.save(str(STORAGE_DIR / filename), "JPEG", quality=90)
        image_paths.append(str(STORAGE_DIR / filename))

    # Save metadata
    meta = {
        "carousel_id": carousel_id,
        "slides": total,
        "theme": theme,
        "image_paths": image_paths,
        "image_urls": [f"/storage/carousel/{carousel_id}_slide_{i+1}.jpg" for i in range(total)],
    }
    (STORAGE_DIR / f"{carousel_id}.json").write_text(json.dumps(meta, indent=2))

    return meta
