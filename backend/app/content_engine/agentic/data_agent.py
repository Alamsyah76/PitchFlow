"""Data Agent — retrieves relevant chunks and extracts structured facts with source citations"""
import os
import json
from openai import OpenAI
from .schemas import Fact, DataContext

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieve_facts(query: str, chunks: list, top_k: int = 5) -> DataContext:
    """
    Given a query and document chunks, retrieve relevant chunks and extract structured facts.
    Each fact includes the source chunk number for verification.
    """
    if not chunks:
        return DataContext(topic_title="", facts=[])

    # Use existing RAG's retrieve_context or do simple embedding similarity
    # For now, use LLM to select relevant chunks + extract facts
    chunks_text = "\n\n---\n\n".join(
        [f"CHUNK {i}:\n{c[:500]}" for i, c in enumerate(chunks)]
    )

    prompt = f"""You are a research data specialist. Given a research query and document chunks:

RESEARCH QUERY: {query}

DOCUMENT CHUNKS:
{chunks_text[:6000]}

TASK:
1. Identify which chunks are relevant to the query
2. Extract specific FACTS, FIGURES, and QUOTES from those chunks
3. For EACH fact, cite the source chunk number

Output JSON:
{{
  "topic_title": "Brief topic label",
  "facts": [
    {{"statement": "Specific fact from document", "source_chunk": 0, "context": "Brief surrounding context"}},
    {{"statement": "Another specific fact", "source_chunk": 2, "context": "Brief surrounding context"}}
  ]
}}

RULES:
- Only include facts DIRECTLY stated in the chunks — no inference
- Each fact must have a source_chunk number
- Prefer specific numbers, dates, names over general statements
- Extract 3-5 most relevant facts
- Bahasa Indonesia
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)

    facts = [Fact(**f) for f in data.get("facts", [])]
    return DataContext(
        topic_title=data.get("topic_title", ""),
        facts=facts,
        raw_chunks=chunks
    )
