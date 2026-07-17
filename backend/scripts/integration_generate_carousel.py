import os
import sys
import uuid
from pathlib import Path

# Ensure repo root is on sys.path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import importlib.util

# Load models.database module directly to avoid package-level imports
spec_db = importlib.util.spec_from_file_location("models.database", str(repo_root / "models" / "database.py"))
db_mod = importlib.util.module_from_spec(spec_db)
spec_db.loader.exec_module(db_mod)

Base = db_mod.Base
User = db_mod.User
Document = db_mod.Document
Content = db_mod.Content

# Load carousel_service directly to avoid importing the whole services package
spec_cs = importlib.util.spec_from_file_location("carousel_service", str(repo_root / "services" / "carousel_service.py"))
cs = importlib.util.module_from_spec(spec_cs)
spec_cs.loader.exec_module(cs)

# Create SQLite engine pointing to dev.db
db_path = repo_root / "dev.db"
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

# Create tables if needed
Base.metadata.create_all(engine)

session = Session()

# Insert or reuse test user
existing_user = session.query(User).filter(User.email == "integration_test@example.com").first()
if existing_user:
    user = existing_user
    user_id = user.id
else:
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email="integration_test@example.com", brand_color_primary="#1F2937", brand_color_secondary="#FFFFFF", brand_font_family="Arial", brand_logo_url=None)
    session.add(user)

# Insert or reuse test document
existing_doc = session.query(Document).filter(Document.file_hash == "hash_integration_test").first()
if existing_doc:
    doc = existing_doc
    doc_id = doc.id
else:
    doc_id = str(uuid.uuid4())
    doc = Document(id=doc_id, user_id=user_id, file_name="test_doc.pdf", file_hash="hash_integration_test", total_pages=1, total_modules=1, total_chunks=1)
    session.add(doc)

# Prepare a caption with multiple sentences
caption = "Introducing our new feature. It simplifies workflows and increases productivity. Try it today and see the difference!"

# Insert content
content_id = str(uuid.uuid4())
content = Content(id=content_id, user_id=user_id, document_id=doc_id, topic_selected="Integration Test Topic", final_caption=caption, carousel_images_urls=[], validity_score="1.00", failed_propositions=[], language_output="en")
session.add(content)
session.commit()

print("Inserted content_id:", content_id)

# Monkeypatch upload_image_to_supabase to save locally
output_base = repo_root / "carousel_output"

def _local_upload(image_bytes: bytes, path: str) -> str:
    dest = output_base / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(image_bytes)
    # return a file:// URL
    return f"file://{dest.resolve()}"

cs.upload_image_to_supabase = _local_upload

# Run generator locally (avoid calling generate_carousel_for_content which expects UUID types)
# Monkeypatch _wrap_text if Pillow's ImageDraw lacks `textsize`
def _compat_wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current + [w])
        try:
            width = font.getsize(test)[0]
        except Exception:
            try:
                bbox = draw.textbbox((0, 0), test, font=font)
                width = bbox[2] - bbox[0]
            except Exception:
                width = len(test) * 6
        if width <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines

# Replace if necessary
if not hasattr(cs, '_wrap_text'):
    cs._wrap_text = _compat_wrap_text
else:
    cs._wrap_text = _compat_wrap_text

slides = cs.parse_caption_to_slides(caption)
urls = []
for idx, slide in enumerate(slides, start=1):
    # Use a local generator compatible with the installed Pillow version
    def _text_size(draw_obj, text, font_obj):
        try:
            bbox = draw_obj.textbbox((0, 0), text, font=font_obj)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            # Fallback approximation
            return len(text) * 6, 14

    def generate_slide_image_local(title, body, slide_index, total_slides, brand_colors, logo_url, font_family=None):
        size = (1080, 1080)
        primary = brand_colors.get("primary") or "#0A84FF"
        secondary = brand_colors.get("secondary") or "#FFFFFF"

        img = __import__('PIL').Image.new("RGB", size, primary)
        draw = __import__('PIL').ImageDraw.Draw(img)

        # Fonts
        title_font = cs._load_font(font_family, size=56)
        body_font = cs._load_font(font_family, size=36)
        small_font = cs._load_font(font_family, size=28)

        padding = 80
        max_text_width = size[0] - padding * 2

        # Title lines
        title_lines = cs._wrap_text(draw, title, title_font, max_text_width)
        y = padding
        for line in title_lines:
            draw.text((padding, y), line, font=title_font, fill=secondary)
            _, h = _text_size(draw, line, title_font)
            y += h + 6

        # Body
        body_lines = cs._wrap_text(draw, body, body_font, max_text_width)
        y += 20
        _, line_h = _text_size(draw, "Ay", body_font)
        line_height = line_h + 6
        max_body_height = size[1] - y - 160
        max_lines = max_body_height // line_height
        body_lines = body_lines[:max_lines]
        for line in body_lines:
            draw.text((padding, y), line, font=body_font, fill=secondary)
            y += line_height

        slide_text = f"Slide {slide_index} of {total_slides}"
        w, h = _text_size(draw, slide_text, small_font)
        draw.text((size[0] - w - 20, size[1] - h - 12), slide_text, font=small_font, fill=secondary)

        out = __import__('io').BytesIO()
        img.save(out, format="PNG")
        out.seek(0)
        return out.read()

    image_bytes = generate_slide_image_local(slide.get("title", ""), slide.get("body", ""), idx, len(slides), {"primary": user.brand_color_primary, "secondary": user.brand_color_secondary}, user.brand_logo_url, user.brand_font_family)
    path = f"contents/{content_id}/slide_{idx}.png"
    url = _local_upload(image_bytes, path)
    urls.append(url)

# Update content record with generated urls
content.carousel_images_urls = urls
session.commit()
print("Generated URLs:")
for u in urls:
    print(u)

session.close()
