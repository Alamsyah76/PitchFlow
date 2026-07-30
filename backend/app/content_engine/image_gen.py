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


def _truncate_title(title: str, max_chars: int = 45) -> str:
    """Truncate title to fit DALL-E rendering"""
    if len(title) <= max_chars:
        return title
    # Try to break at word boundary
    truncated = title[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.6:  # Only truncate at word if we keep most of it
        return truncated[:last_space] + ".."
    return truncated + ".."


def generate_image(topic_title: str, caption: str, hashtags: list = None, doc_name: str = "") -> dict:
    img_id = str(uuid.uuid4())[:8]

    # 1. Extract 3 key points
    points = _extract_points(caption, topic_title)
    if not points:
        points = ["Secure authentication for enterprise", "MFA with FIDO2 support", "OTP via SMS email and app"]

    # 2. Shorten title for clean rendering
    short_title = _truncate_title(topic_title, 45)

    # 3. Build DALL-E prompt with exact text content
    prompt = (
        "Create a professional semi-anime style infographic image, 1024x1024. "
        "The image MUST include the following text exactly as specified. "
        "Text style: clean modern sans-serif, white colored text. "
        "Place the text on the LEFT SIDE of the image over a dark semi-transparent panel for readability. "
        f"\\n\\nTITLE (top area, large font): {short_title}"
        f"\\n\\nPOINTS (below title, medium font):\\n"
        f"• {points[0]}\\n"
        f"• {points[1]}\\n"
        f"• {points[2]}"
        "\\n\\nRIGHT SIDE: professional relevant illustration/scene supporting the topic. "
        "DO NOT add any text beyond what is specified above. "
        "Make sure all text is clearly readable and NOT cut off. "
        "Keep the overall design clean and professional."
    )

    # 4. Generate image via DALL-E
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

    # 5. Download and save
    bg_path = STORAGE_DIR / f"{img_id}_bg.png"
    urllib.request.urlretrieve(img_url, str(bg_path))
    bg = Image.open(str(bg_path)).convert("RGB")
    bg = bg.resize((1024, 1024), Image.LANCZOS)
    filename = f"{img_id}.jpg"
    bg.save(str(STORAGE_DIR / filename), "JPEG", quality=95)
    bg_path.unlink(missing_ok=True)

    return {"image_url": f"/storage/images/{filename}", "image_path": str(STORAGE_DIR / filename)}
