"""RAG Engine — chunking, embedding, semantic retrieval + rerank (no database dependency)"""
import os
import json
import numpy as np
from openai import OpenAI
from typing import List, Dict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Lazy-loaded reranker — loads on first use (~80MB, 200-300ms)
_reranker = None

def _get_reranker():
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks by characters — 1000 chars for full paragraph context"""
    if not text:
        return [text]
    chunks = []
    start = 0
    text_len = len(text)
    prev_start = -1
    while start < text_len and start != prev_start:
        prev_start = start
        end = min(start + chunk_size, text_len)
        # Jangan potong di tengah kata — mundur ke spasi terdekat
        if end < text_len and end - start >= 50:
            space_pos = text.rfind(" ", start + 50, end)
            if space_pos > start:
                end = space_pos
        chunk = text[start:end].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        next_start = end - overlap if end >= overlap else end
        start = next_start if next_start > start else end
        if start >= text_len:
            break
    return chunks if chunks else [text[:1000]]


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts"""
    if not texts:
        return []
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [e.embedding for e in resp.data]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


def rerank(query: str, chunks: List[str], top_k: int = 5) -> List[str]:
    """Rerank chunks using cross-encoder — lebih akurat dari cosine similarity"""
    if not chunks:
        return []
    if len(chunks) <= top_k:
        return chunks
    reranker = _get_reranker()
    pairs = [[query, c] for c in chunks]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [r[0] for r in ranked[:top_k]]


def process_document(text: str, doc_id: str, store_dir) -> Dict:
    """Full pipeline: chunk → embed → save"""
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    data = {
        "doc_id": doc_id,
        "chunks": chunks,
        "embeddings": embeddings,
    }
    rag_path = store_dir / f"{doc_id}_rag.json"
    rag_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def load_rag(doc_id: str, store_dir) -> Dict:
    """Load pre-computed RAG data from disk"""
    rag_path = store_dir / f"{doc_id}_rag.json"
    if rag_path.exists():
        return json.loads(rag_path.read_text())
    return {"doc_id": doc_id, "chunks": [], "embeddings": []}


def retrieve(query: str, doc_id: str, store_dir, top_k: int = 5) -> List[str]:
    """Retrieve top-k relevant chunks using cosine search + rerank"""
    rag = load_rag(doc_id, store_dir)
    if not rag["chunks"]:
        return []

    # 1. Cosine similarity — fast first pass (get top-10)
    query_emb = embed_texts([query])[0]
    scores = [(cosine_similarity(query_emb, e), i) for i, e in enumerate(rag["embeddings"])]
    scores.sort(key=lambda x: -x[0])
    candidates = [rag["chunks"][i] for _, i in scores[:top_k * 2]]

    # 2. Rerank with cross-encoder
    ranked = rerank(query, candidates, top_k)
    return ranked


def retrieve_context(query: str, doc_id: str, store_dir, top_k: int = 5, max_chars: int = 5000) -> str:
    """Retrieve top-k chunks (reranked) and join into context string"""
    chunks = retrieve(query, doc_id, store_dir, top_k)
    context = "\n\n---\n\n".join(chunks)
    return context[:max_chars]


def get_overview_context(doc_id: str, store_dir, max_chunks: int = 3) -> str:
    """Get first N chunks as overview context (for topic generation)"""
    rag = load_rag(doc_id, store_dir)
    if not rag["chunks"]:
        return ""
    chunks = rag["chunks"][:max_chunks]
    return "\n\n---\n\n".join(chunks)
