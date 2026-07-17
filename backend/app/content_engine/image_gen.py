"""Infografis — DALL-E background + judul + 3 short point, tanpa icon, tanpa overlay"""
import os, json, textwrap, uuid, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
_api_key = ""
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            _api_key = line.split("=", 1)[1].strip()
            break
client = OpenAI(api_key=_api_key, timeout=300.0) if _api_key else OpenAI(timeout=300.0)

STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "images"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _font(size):
    for p in [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\seguisb.ttf",
              r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\arial.ttf",
              r"C:\Windows\Fonts\calibri.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _generate_prompt(topic: str, caption: str) -> str:
    resp = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"system","content":"Buat prompt DALL-E dalam Bahasa Inggris untuk background infografis dengan gaya semi-anime profesional. Scene harus mendukung topik berikut. Area kiri gambar harus cukup gelap agar teks putih terbaca. JANGAN ada teks dalam gambar. Max 100 kata."},
                  {"role":"user","content":f"Topik: {topic}\n\nKonteks: {caption[:500]}"}],
        temperature=0.4, max_tokens=200)
    return resp.choices[0].message.content.strip()


def _generate_image(prompt: str) -> str:
    resp = client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024", quality="auto", n=1)
    url = resp.data[0].url if resp.data and resp.data[0].url else ""
    if not url and resp.data and resp.data[0].b64_json:
        url = f"data:image/png;base64,{resp.data[0].b64_json}"
    return url


def _extract_points(caption: str, topic: str) -> list:
    """Extract 3 short points (5-8 words each) from caption"""
    resp = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"system","content":"Dari teks berikut, buat 3 poin pendek (masing-masing 5-8 kata) yang merupakan intisari penting. Return JSON: {\"points\":[\"...\",\"...\",\"...\"]}. Poin harus spesifik, grounded pada teks."},
                  {"role":"user","content":f"Topik: {topic}\n\nTeks:\n{caption[:2000]}"}],
        temperature=0.3, response_format={"type":"json_object"})
    result = json.loads(resp.choices[0].message.content)
    return result.get("points", [])[:3]


def generate_image(topic_title: str, caption: str, hashtags: list = None, doc_name: str = "") -> dict:
    img_id = str(uuid.uuid4())[:8]

    # 1. Generate scene background
    prompt = _generate_prompt(topic_title, caption)
    img_url = _generate_image(prompt)

    # 2. Download background
    bg_path = STORAGE_DIR / f"{img_id}_bg.png"
    urllib.request.urlretrieve(img_url, str(bg_path))

    # 3. Open and prepare
    bg = Image.open(str(bg_path)).convert("RGB")
    bg = bg.resize((1024, 1024), Image.LANCZOS)
    W, H = bg.size
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # 4. Extract 3 short points
    points = _extract_points(caption, topic_title)
    if not points:
        points = [topic_title[:60]]

    # 5. Fonts
    title_font = _font(38)
    point_font = _font(22)

    mx, my = 45, 45

    # 6. TITLE — langsung di gambar, putih polos
    draw.rectangle([mx, my, mx+45, my+3], fill=(255, 255, 255, 200))
    my += 18
    for line in textwrap.wrap(topic_title, width=28):
        draw.text((mx, my), line, fill="white", font=title_font)
        my += 44

    my += 25

    # 7. POINTS — tanpa icon, teks putih polos
    for pt in points:
        for line in textwrap.wrap(pt, width=35):
            draw.text((mx, my), line, fill="white", font=point_font)
            my += 28
        my += 6

    # Save
    filename = f"{img_id}.jpg"
    img.save(str(STORAGE_DIR / filename), "JPEG", quality=92)
    bg_path.unlink(missing_ok=True)

    return {"image_url": f"/storage/images/{filename}", "image_path": str(STORAGE_DIR / filename)}
