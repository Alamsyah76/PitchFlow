"""Topic Generator — uses RAG for grounded topic generation"""
import os
import json
from openai import OpenAI
from app.content_engine.rag import get_overview_context, retrieve_context

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_topics(text: str, filename: str, doc_id: str = None, store_dir=None) -> list:
    """Hasilkan 2 topic angle dari dokumen menggunakan RAG context"""
    # Gunakan RAG untuk mengambil konteks yang relevan
    if doc_id and store_dir:
        overview = get_overview_context(doc_id, store_dir)
        context = overview or text[:4000]
    else:
        context = text[:4000]

    prompt = f"""Analisis dokumen berikut dan hasilkan 2 TOPIC ANGLE untuk konten LinkedIn.

DOKUMEN:
{context}

Format output JSON:
{{
  "topics": [
    {{"title": "Judul Topic 1", "angle": "Penjelasan sudut pandang 1 (1 kalimat)", "key_points": ["poin spesifik 1", "poin spesifik 2", "poin spesifik 3"]}},
    {{"title": "Judul Topic 2", "angle": "Penjelasan sudut pandang 2 (1 kalimat)", "key_points": ["poin spesifik 1", "poin spesifik 2", "poin spesifik 3"]}}
  ]
}}

SYARAT:
- Topic harus grounded pada isi dokumen, bukan generik
- Kedua topic harus benar-benar berbeda sudut pandang
- Gunakan detail spesifik dari dokumen (angka, nama produk, tokoh)
- Bahasa Indonesia
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)
    return result.get("topics", [])
