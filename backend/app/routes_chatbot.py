"""Chatbot — auto-detect Ollama local / DeepSeek API, paham PitchFlow"""
import os, json, httpx
from fastapi import APIRouter

from app.database import get_cached_answer, cache_answer

router = APIRouter(prefix="/api", tags=["chatbot"])

SYSTEM_PROMPT = """Kamu adalah asisten PitchFlow. Jawab pertanyaan tentang sistem ini dengan singkat dan jelas.

PITCHFLOW adalah platform Content Generation untuk Marketing & Sales. Fitur utama:

1. Content Studio — Upload PDF (produk, brosur, dokumen teknis) → otomatis jadi:
   - 2 topic angle berbeda
   - Caption LinkedIn 3 paragraf (grounded ke dokumen, RAG chunk 1000 + rerank)
   - 5 hashtag relevan
   - Image storytelling (DALL-E scene + teks, tanpa overlay)
   - Export ZIP (topic.txt + content.txt + image.jpg)

2. Email Campaign — Upload kontak (XLS/manual), template email, kirim batch, log pengiriman, download CSV.

3. Library — Auto-save hasil generate, per-user, limit sesuai tier.

4. Pricing (Harga):
   │ Fitur                │ Free    │ Basic       │ Bisnis         │ Pro            │
   │──────────────────────┼─────────┼─────────────┼────────────────┼────────────────│
   │ Harga                │ Rp 0    │ Rp 49rb/bln │ Rp 149rb/bln   │ Rp 299rb/bln   │
   │ Konten               │ 3 file  │ 20 file     │ 100 file       │ Unlimited      │
   │ Image                │ 1x trial│ 1024×1024   │ 1024×1024      │ 1024×1024      │
   │ Library              │ ❌      │ 20 konten   │ 100 konten     │ Unlimited      │
   │ Email Campaign       │ ❌      │ ❌          │ 100 kontak     │ Unlimited      │

Chatbot gratis untuk semua tier. Tidak perlu login untuk chat.

Jika ditanya harga, jawab dengan format persis seperti ini:

**Free**
Content Studio — 3 file/bulan
Image — 1x trial
Library — ❌
Email Campaign — ❌

**Basic — Rp 49rb/bulan**
Content Studio — 20 file/bulan
Image — 1024×1024
Library — 20 konten
Email Campaign — ❌

**Bisnis — Rp 149rb/bulan**
Content Studio — 100 file/bulan
Image — 1024×1024
Library — 100 konten
Email Campaign — 100 kontak

**Pro — Rp 299rb/bulan**
Content Studio — Unlimited
Image — 1024×1024
Library — Unlimited
Email Campaign — Unlimited

Gunakan format bold untuk nama tier (**Free**, **Basic**, dll) dan bullet point untuk fitur. Jawab profesional dan informatif.

Keunggulan: Upload PDF → konten jadi (tanpa prompt), grounded ke dokumen (zero hallucination), AI-ish rendah (80+ banned phrases + filter naturalisasi otomatis), dynamic persona, Indonesia native.

AVOID (Banned Phrases) adalah 80+ kata/frasa yang dilarang muncul di caption karena terlalu AI-ish. Contoh: "pernahkah anda", "apakah anda", "tahukah anda", "seiring dengan", "era baru", "lanskap", "mari kita", "mari diskusikan", "game changer", "transformasi", "era digital", "dunia digital", "lanskap bisnis", "ekosistem digital", "era serba digital", "zaman now", "going forward", "stay ahead", "in today's fast-paced", "revolutionize", "never been easier", "seamless", "era of", "harap diperhatikan", "dapat dipahami bahwa", "menjadi perhatian kita bersama", "semoga bermanfaat", "terima kasih atas perhatiannya", "perlu diingat", "demikian disampaikan", "tunggu apalagi", "jangan lewatkan".
Filter bekerja otomatis: frasa AI diganti atau dihapus dari caption setelah generate, tanpa merusak 3 paragraf, topic, atau hashtags.

Deteksi bahasa dari pertanyaan user. Jika user bertanya dalam Bahasa Indonesia, jawab dalam Bahasa Indonesia. Jika user bertanya dalam Bahasa Inggris, jawab dalam Bahasa Inggris. Singkat dan padat. Jika tidak tahu, bilang tidak tahu."""


def _try_ollama(prompt: str) -> str | None:
    """Coba panggil Ollama local (1 detik timeout total)"""
    try:
        r = httpx.post("http://127.0.0.1:11434/api/chat",
            json={"model": "llama3.1", "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ], "stream": False}, timeout=1)
        if r.status_code == 200:
            return r.json()["message"]["content"]
    except: pass
    return None


def _try_deepseek(prompt: str) -> str | None:
    """Panggil DeepSeek API"""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key: return None
    try:
        r = httpx.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ], "max_tokens": 500, "temperature": 0.3},
            timeout=15)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except: pass
    return None


from app.rate_limit import check_chat_limit, increment_chat


@router.post("/chatbot/ask")
async def chatbot_ask(payload: dict):
    prompt = (payload.get("message", "") or "").strip()
    if not prompt:
        return {"success": False, "message": "Pertanyaan tidak boleh kosong"}

    # Cek cache dulu
    cached = get_cached_answer(prompt)
    if cached:
        return {"success": True, "data": {"reply": cached, "source": "cache"}}

    # Rate limit check
    lim = check_chat_limit()
    if not lim["allowed"]:
        return {"success": False, "message": f"Batas chat hari ini sudah habis ({lim['used']}/{lim['limit']}). Upgrade tier untuk unlimited chat."}

    reply = _try_ollama(prompt)
    source = "local"
    if reply is None:
        reply = _try_deepseek(prompt)
        source = "deepseek"

    if reply is None:
        return {"success": False, "message": "Tidak bisa terhubung ke Ollama maupun DeepSeek. Pastikan Ollama berjalan atau DEEPSEEK_API_KEY terisi."}

    # Cache jawaban
    try: cache_answer(prompt, reply)
    except: pass

    increment_chat()
    return {"success": True, "data": {"reply": reply, "source": source}}
