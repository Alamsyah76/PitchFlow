"""Content Writer — LinkedIn caption + max 5 hashtags, 3 paragraf grounded, dynamic persona"""
import os, json, re
from openai import OpenAI
from app.content_engine.rag import retrieve_context

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AVOID = ["pernahkah anda", "apakah anda", "tahukah anda", "seiring dengan", "era baru", "lanskap",
         "mari kita", "mari diskusikan", "game changer", "revolution", "transformasi",
         "era digital", "future of", "dunia semakin", "tidak bisa dipungkiri",
         "yang perlu anda ketahui", "yang menarik adalah", "perlu diingat",
         "kita semua tahu", "sudah bukan rahasia", "tren yang berkembang",
         "selain itu", "sementara itu", "di sisi lain",
         "tidak hanya", "tetapi juga", "hal ini", "dengan demikian",
         "pada akhirnya", "oleh karena itu", "tak hanya",
         "merupakan salah satu", "salah satu", "dengan semakin"]

_hashtag_re = re.compile(r"#[A-Za-z0-9_]+")


def _is_valid_hashtag(tag: str) -> bool:
    t = tag.strip()
    return len(t) >= 3 and sum(c.isalpha() for c in t) >= 2 and bool(re.search(r"[A-Za-z]", t))


def _detect_persona(context: str) -> str:
    """Detect industry from document and return appropriate LinkedIn persona"""
    resp = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"system","content":"Deteksi industri/bidang dari teks berikut. Return JSON: {\"industry\": \"...\", \"role\": \"...\"}. Contoh: {\"industry\": \"IT Security\", \"role\": \"profesional keamanan TI\"}, {\"industry\": \"Finance\", \"role\": \"profesional keuangan\"}, {\"industry\": \"HR\", \"role\": \"profesional HR\"}. Bahasa Indonesia."},
                  {"role":"user","content":f"Teks:\n\n{context[:2000]}"}],
        temperature=0.2,
        response_format={"type":"json_object"})
    result = json.loads(resp.choices[0].message.content)
    role = result.get("role", "profesional")
    return f"Anda adalah {role} yang aktif membagikan wawasan di LinkedIn. Tulisan Anda natural, tidak kaku, dan grounded pada fakta. Hindari frasa klise, promosi berlebihan, dan akhiran slogan."


def _post_process(caption: str) -> str:
    """Replace banned/AI-ish phrases — hanya find-and-replace, tidak potong struktur"""
    replacements = [
        # Klise pembuka
        ("pernahkah anda", "Pernah"),
        ("apakah anda", ""),
        ("tahukah anda", "Tahukah"),
        ("seiring dengan", "Bersamaan dengan"),
        ("mari kita", "Mari"),
        ("mari diskusikan", "Diskusikan"),
        ("yang perlu anda ketahui", "Perlu diketahui"),
        ("yang menarik adalah", "Menariknya"),
        ("kita semua tahu", "Seperti diketahui"),
        ("sudah bukan rahasia", "Bukan rahasia"),
        ("tren yang berkembang", "Tren"),
        ("tidak bisa dipungkiri", "Jelas"),
        ("merupakan salah satu", ""),
        ("salah satu", ""),

        # Transisi kaku
        ("selain itu", "Lebih dari itu"),
        ("sementara itu", "Di saat yang sama"),
        ("di sisi lain", "Di sisi sebaliknya"),
        (" tidak hanya ", " "),
        (" tetapi juga ", " "),
        (" tak hanya ", " "),
        ("dengan demikian", "Karena itu"),
        ("pada akhirnya", "Kesimpulannya"),
        ("oleh karena itu", "Karena itu"),
        ("hal ini ", "Ini "),
        ("hal tersebut", "Ini"),

        # Marketing bombastis
        ("game changer", "pengubah permainan"),
        ("revolution", "perubahan"),
        ("era baru", "babak baru"),
        ("era digital", "era modern"),
        ("dunia digital", "dunia modern"),
        ("lanskap bisnis", "dunia bisnis"),
        ("ekosistem digital", "lingkungan digital"),
        ("transformasi digital", "adopsi digital"),
        ("era serba digital", "zaman digital"),
        ("zaman now", "saat ini"),

        # Inggris berlebihan
        ("going forward", "ke depannya"),
        ("stay ahead", "tetap unggul"),
        ("in today's fast-paced", "Di era yang serba cepat"),
        ("revolutionize", "mengubah"),
        ("never been easier", "semakin mudah"),
        ("seamless", "mulus"),
        ("future of", "masa depan"),
        ("dunia semakin", ""),

        # Formal kaku
        ("harap diperhatikan", "Perlu dicatat"),
        ("dapat dipahami bahwa", ""),
        ("menjadi perhatian kita bersama", ""),
        ("semoga bermanfaat", ""),
        ("terima kasih atas perhatiannya", ""),
        ("perlu diingat", "Ingat"),
        ("demikian disampaikan", ""),
        ("demikian informasi ini", ""),
        ("dengan semakin", ""),

        # Promosi
        ("tunggu apalagi", ""),
        ("jangan lewatkan", ""),
        ("ayo segera", ""),
        ("buruan daftar", ""),
        ("limited time", "waktu terbatas"),
        ("jangan sampai ketinggalan", ""),

        # Pengulangan
        ("tidak hanya itu", ""),
        ("tak hanya itu", ""),
        ("selain daripada itu", ""),
    ]
    for old, new in replacements:
        if new:
            caption = caption.replace(old, new)
            caption = caption.replace(old.capitalize(), new.capitalize() if new else old.capitalize())
        else:
            caption = caption.replace(old, "")
            caption = caption.replace(old.capitalize(), "")

    # Bersihkan spasi ganda dan titik kosong
    caption = re.sub(r"\s+", " ", caption)
    caption = re.sub(r"\.\s*\.", ".", caption)
    caption = re.sub(r"\s*\.\s*$", ".", caption)
    # Hapus spasi sebelum tanda baca
    caption = re.sub(r"\s+\.", ".", caption)
    caption = re.sub(r"\s+,", ",", caption)
    caption = caption.strip()
    if caption == ".":
        caption = ""

    # Kapitalisasi awal
    if caption and not caption[0].isupper():
        caption = caption[0].upper() + caption[1:]

    return caption


def generate_caption(text: str, filename: str, topic: dict, doc_id: str = None, store_dir=None) -> dict:
    topic_title = topic.get("title", "")
    query = topic_title + " " + topic.get("angle", "")

    # RAG retrieve
    if doc_id and store_dir:
        chunks = retrieve_context(query, doc_id, store_dir, top_k=5, max_chars=5000)
    else:
        chunks = text[:3000]

    # Detect dynamic persona from document context
    persona = _detect_persona(chunks[:2000] or text[:2000])

    # Build prompt
    prompt = (
        "Anda membaca dokumen ini dalam Bahasa Indonesia. Tulislah dalam Bahasa Indonesia:\n\n"
        + topic_title + " \u2014 " + topic.get("angle", "") + "\n\n"
        + chunks + "\n\n"
        + "Tulislah **TEPAT 3 paragraf** berdasarkan bacaan di atas.\n\n"
        + "SYARAT KETAT (ikuti persis):\n"
        + "- WAJIB Bahasa Indonesia, jangan pakai bahasa Inggris\n"
        + "- TEPAT 3 paragraf, tidak lebih dan tidak kurang\n"
        + "- Setiap paragraf WAJIB mengandung minimal 1 detail spesifik dari dokumen (angka, nama produk, fitur, data)\n"
        + "- JANGAN mengulang detail yang sama di paragraf berbeda\n"
        + "- Grounded pada dokumen, jangan ngarang\n"
        + "- Natural, variatif. Campur kalimat pendek dan panjang\n"
        + "- Gunakan transisi yang variatif dan tidak kaku\n"
        + "- Jangan akhiri dengan ajakan promosi atau slogan\n\n"
        + 'Output JSON:\n{"caption": "Paragraf 1...\\n\\nParagraf 2...\\n\\nParagraf 3...", "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]}'
    )

    messages = [
        {"role": "system", "content": persona},
        {"role": "user", "content": prompt},
    ]

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    content = resp.choices[0].message.content

    # Parse JSON
    caption = content
    hashtags = []
    try:
        parsed = json.loads(content)
        caption = parsed.get("caption", parsed.get("text", content))
        hashtags = parsed.get("hashtags", [])
    except json.JSONDecodeError:
        pass

    # Post-process — AVOID filter + enforce 3 paragraf
    caption = _post_process(caption)
    
    # Enforce TEPAT 3 paragraf — ambil 3 pertama, buang sisanya
    import re
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", caption) if p.strip()]
    if len(paragraphs) > 3:
        caption = "\n\n".join(paragraphs[:3])
    elif len(paragraphs) == 1 and len(caption) > 200:
        # 1 paragraf panjang → split jadi 3 berdasarkan kalimat
        sentences = re.split(r'(?<=[.!?])\s+', caption)
        if len(sentences) >= 3:
            split_point1 = max(1, len(sentences) // 3)
            split_point2 = max(1, 2 * len(sentences) // 3)
            p1 = " ".join(sentences[:split_point1])
            p2 = " ".join(sentences[split_point1:split_point2])
            p3 = " ".join(sentences[split_point2:])
            caption = f"{p1}\n\n{p2}\n\n{p3}"

    # Fallback: extract hashtags from text
    if not hashtags:
        hashtags = _hashtag_re.findall(content)
    hashtags = [h for h in hashtags if _is_valid_hashtag(h)][:5]

    return {"caption": caption, "hashtags": hashtags}
