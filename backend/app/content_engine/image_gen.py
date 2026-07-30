"""Infografis — DALL-E generates complete image with embedded text"""
import os, json, uuid, urllib.request
from pathlib import Path
from PIL import Image
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


def _extract_points(caption: str, topic: str) -> list:
    """Extract 3 very short points (max 8 words each) for clean DALL-E rendering"""
    resp = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"system","content":"Dari teks berikut, buat 3 poin SANGAT PENDEK (maksimal 6-8 kata per poin) yang merupakan intisari penting. Return JSON: {\"points\":[\"...\",\"...\",\"...\"]}. Poin harus spesifik, grounded pada teks, dan MUDAH dibaca."},
                  {"role":"user","content":f"Topik: {topic}\n\nTeks:\n{caption[:2000]}"}],
        temperature=0.3, response_format={"type":"json_object"})
    result = json.loads(resp.choices[0].message.content)
    return result.get("points", [])[:3]


def _truncate_title(title: str, max_chars: int = 70) -> str:
    """Truncate title to fit DALL-E rendering"""
    if len(title) <= max_chars:
        return title
    truncated = title[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.6:
        return truncated[:last_space] + ".."
    return truncated + ".."


def _build_image_prompt(topic_title: str, caption: str, points: list) -> str:
    """GPT generates a relevant scene, then builds full DALL-E prompt with exact text"""
    short_title = _truncate_title(topic_title, 65)

    # Step 1: GPT generates scene description relevant to the ACTUAL content (not generic)
    scene_resp = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"system","content":"Buat deskripsi scene visual dalam Bahasa Inggris (max 35 kata) untuk infografis 3D isometric style dengan glassmorphism UI. Scene harus RELEVAN dengan topik — gambar VISUAL yang spesifik mewakili topik. Contoh: untuk topik ERP, scene-nya workflow/process; untuk topik security, scene-nya lock/shield; untuk topik HR, scene-nya people/org chart. Bukan server/network generic. Hanya deskripsi scene."},
                  {"role":"user", "content":f"Topik: {topic_title}\n\nKonteks: {caption[:500]}"}],
        temperature=0.7, max_tokens=100)
    scene = scene_resp.choices[0].message.content.strip()

    # Step 2: Build full DALL-E prompt
    prompt = (
        f"Create a professional 3D isometric infographic in glassmorphism and holographic style. "
        f"Background: variatif gradient pattern. "
        f"Scene: {scene} "
        f"\\n\\nEMBEDDED TEXT (render exactly):"
        f"\\nTITLE (top-left, large white text with orange glow): {short_title}"
        f"\\nKEY POINTS (left side glass panel, white text):"
        f"\\n• {points[0]}\\n• {points[1]}\\n• {points[2]}"
        f"\\n\\nCRITICAL: Render text EXACTLY as written. White on dark background. "
        f"DO NOT add other text. Scene must be specific to the topic."
    )
    return prompt


def generate_image(topic_title: str, caption: str, hashtags: list = None, doc_name: str = "") -> dict:
    img_id = str(uuid.uuid4())[:8]

    # 1. Extract 3 key points
    points = _extract_points(caption, topic_title)
    if not points:
        points = ["Secure authentication for enterprise", "MFA with FIDO2 support", "OTP via SMS email and app"]

    # 2. Build dynamic DALL-E prompt (scene + text)
    prompt = _build_image_prompt(topic_title, caption, points)

    # 3. Generate image via DALL-E
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="auto",
        n=1,
    )
    img_url = resp.data[0].url if resp.data and resp.data[0].url else ""
    if not img_url and resp.data and resp.data[0].b64_json:
        img_url = f"data:image/png;base64,{resp.data[0].b64_json}"

    # 4. Download and save
    bg_path = STORAGE_DIR / f"{img_id}_bg.png"
    urllib.request.urlretrieve(img_url, str(bg_path))
    bg = Image.open(str(bg_path)).convert("RGB")
    bg = bg.resize((1024, 1024), Image.LANCZOS)
    filename = f"{img_id}.jpg"
    bg.save(str(STORAGE_DIR / filename), "JPEG", quality=95)
    bg_path.unlink(missing_ok=True)

    return {"image_url": f"/storage/images/{filename}", "image_path": str(STORAGE_DIR / filename)}
