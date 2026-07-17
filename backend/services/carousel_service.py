"""
Carousel Service
Generates LinkedIn carousel images from a final caption using Pillow and uploads to Supabase Storage.
"""
import io
import re
import math
import httpx
from typing import List, Dict, Optional

from PIL import Image, ImageDraw, ImageFont, ImageOps

from supabase import create_client
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

BUCKET_NAME = "carousel"


def _split_into_sentences(text: str) -> List[str]:
    # Simple sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def parse_caption_to_slides(caption: str, min_slides: int = 3, max_slides: int = 5) -> List[Dict]:
    sentences = _split_into_sentences(caption)

    # If very short, split by commas
    if len(sentences) < min_slides:
        parts = [p.strip() for p in re.split(r',|;|\n', caption) if p.strip()]
        sentences = parts if parts else sentences

    # Determine number of slides
    total_sentences = len(sentences)
    target_slides = min(max_slides, max(min_slides, math.ceil(total_sentences / 2)))

    # Distribute sentences across slides
    slides = []
    if total_sentences == 0:
        # Fallback single slide
        slides = [{"title": "", "body": caption}]
    else:
        per_slide = math.ceil(total_sentences / target_slides)
        for i in range(0, total_sentences, per_slide):
            chunk = sentences[i:i+per_slide]
            title = chunk[0] if chunk else ""
            body = " ".join(chunk)
            slides.append({"title": title, "body": body})

    # Ensure between min and max slides
    if len(slides) < min_slides:
        # pad by repeating last
        while len(slides) < min_slides:
            slides.append(slides[-1])

    if len(slides) > max_slides:
        slides = slides[:max_slides]

    return slides


def _load_font(preferred: Optional[str], size: int):
    # Try to load a TTF font from common locations
    candidates = []
    if preferred:
        candidates.append(preferred)

    # Common fonts
    candidates.extend([
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ])

    for path in candidates:
        try:
            font = ImageFont.truetype(path, size=size)
            return font
        except Exception:
            continue

    # Fallback default font
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current + [w])
        width, _ = draw.textsize(test, font=font)
        if width <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def generate_slide_image(
    title: str,
    body: str,
    slide_index: int,
    total_slides: int,
    brand_colors: Dict[str, str],
    logo_url: Optional[str],
    font_family: Optional[str] = None
) -> bytes:
    # Canvas
    size = (1080, 1080)
    primary = brand_colors.get("primary") or "#0A84FF"
    secondary = brand_colors.get("secondary") or "#FFFFFF"

    # Simple background: solid primary
    img = Image.new("RGB", size, primary)
    draw = ImageDraw.Draw(img)

    # Download logo if provided
    if logo_url:
        try:
            r = httpx.get(logo_url, timeout=15.0)
            r.raise_for_status()
            logo_img = Image.open(io.BytesIO(r.content)).convert("RGBA")
            # Resize logo to fit
            max_logo = 160
            ratio = min(max_logo / logo_img.width, max_logo / logo_img.height, 1.0)
            logo_new = logo_img.resize((int(logo_img.width * ratio), int(logo_img.height * ratio)), Image.LANCZOS)
            # Paste logo to top-right with margin
            margin = 36
            pos = (size[0] - logo_new.width - margin, margin)
            img.paste(logo_new, pos, logo_new)
        except Exception as e:
            logger.warning(f"Failed to download or paste logo: {e}")

    # Fonts
    title_font = _load_font(font_family, size=56)
    body_font = _load_font(font_family, size=36)
    small_font = _load_font(font_family, size=28)

    # Title area
    padding = 80
    max_text_width = size[0] - padding * 2

    # Draw title (may be short)
    title_lines = _wrap_text(draw, title, title_font, max_text_width)
    y = padding
    for line in title_lines:
        draw.text((padding, y), line, font=title_font, fill=secondary)
        y += title_font.getsize(line)[1] + 6

    # Draw body
    body_lines = _wrap_text(draw, body, body_font, max_text_width)
    y += 20
    max_body_height = size[1] - y - 160
    line_height = body_font.getsize("Ay")[1] + 6
    max_lines = max_body_height // line_height
    body_lines = body_lines[:max_lines]
    for line in body_lines:
        draw.text((padding, y), line, font=body_font, fill=secondary)
        y += line_height

    # Slide numbering
    slide_text = f"Slide {slide_index} of {total_slides}"
    w, h = draw.textsize(slide_text, font=small_font)
    draw.text((size[0] - w - 20, size[1] - h - 12), slide_text, font=small_font, fill=secondary)

    # Export to PNG bytes
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out.read()


def _get_supabase_client():
    if not settings:
        raise RuntimeError("Settings not initialized")
    url = settings.supabase_url
    key = settings.supabase_service_role_key
    return create_client(url, key)


def upload_image_to_supabase(image_bytes: bytes, path: str) -> str:
    client = _get_supabase_client()
    try:
        res = client.storage.from_(BUCKET_NAME).upload(path, image_bytes)
        # get public url
        public = client.storage.from_(BUCKET_NAME).get_public_url(path)
        url = public.get("publicURL") or public.get("url") or public
        return url
    except Exception as e:
        logger.error(f"Failed to upload to Supabase: {e}")
        raise


def generate_carousel_for_content(db, content_id: str, user_id: Optional[str] = None) -> List[str]:
    from models.database import Content, User
    import uuid

    # Load content (convert id to UUID)
    try:
        content_uuid = uuid.UUID(content_id)
    except Exception:
        raise ValueError("Invalid content_id format")

    query = db.query(Content).filter(Content.id == content_uuid)
    if user_id:
        query = query.filter(Content.user_id == uuid.UUID(user_id))

    content = query.first()
    if not content:
        raise ValueError("Content not found")

    user = db.query(User).filter(User.id == content.user_id).first()
    if not user:
        raise ValueError("User not found for content")

    caption = content.final_caption or ""
    brand_colors = {"primary": user.brand_color_primary or "#0A84FF", "secondary": user.brand_color_secondary or "#FFFFFF"}
    font_family = user.brand_font_family
    logo_url = user.brand_logo_url

    slides = parse_caption_to_slides(caption)
    total = len(slides)

    urls = []
    for idx, slide in enumerate(slides, start=1):
        image_bytes = generate_slide_image(slide.get("title", ""), slide.get("body", ""), idx, total, brand_colors, logo_url, font_family)
        # Path: contents/{content_id}/slide_{idx}.png
        path = f"users/{content.user_id}/contents/{content_id}/slide_{idx}.png"
        url = upload_image_to_supabase(image_bytes, path)
        urls.append(url)

    # Update content record
    content.carousel_images_urls = urls
    db.commit()

    return urls
