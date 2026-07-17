"""SemanticDocumentReader — LLM-powered structured semantic extraction.

Responsibility:
    Extract a structured semantic profile from document chunks before topic
    generation.  This module has ONE responsibility: converting raw chunks
    into a contract of what the document is about, what must be preserved,
    and what distinct angles exist for topic generation.

    This module does NOT generate topics.
    This module does NOT generate captions.
    This module does NOT rewrite marketing copy.
    This module extracts ONLY from document evidence.

Input:
    chunks: list[str]
    filename: str

Output dict:
    {
        "document_identity": str,
        "identity_terms": list[str],
        "must_preserve_terms": list[str],
        "specific_topics": list[str],
        "topic_angles": list[str],
        "domain_terms": list[str],
        "evidence_points": list[str],
        "rejected_generic_terms": list[str],
    }

Usage:
    from app.semantic_document_reader import read_document_semantics
    semantics = read_document_semantics(chunks[:8], filename)
    if semantics.get("document_identity"):
        profile["_semantic_identity"] = semantics["document_identity"]
"""

import json
import os
import re
from typing import Any, Dict, List

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _select_context_chunks(chunks: List[str], max_chars: int = 5000) -> str:
    """Select representative chunks, preferring the first chunk (title/intro)."""
    selected: List[str] = []
    total = 0
    for chunk in chunks[:10]:
        text = _clean(chunk)
        if not text:
            continue
        if total + len(text) > max_chars:
            # Truncate the last chunk to fit
            remaining = max_chars - total
            if remaining > 200:
                selected.append(text[:remaining])
            break
        selected.append(text)
        total += len(text)
    return "\n\n".join(selected)


_SYSTEM_PROMPT = """You are a document analyst that extracts structured semantic metadata.

Given document text, extract what the document is specifically about.
Return valid JSON only — no explanations, no markdown.

RULES:
1. Extract ONLY from the text provided. Do not invent or infer beyond the text.
2. Identity terms MUST appear verbatim in the document text.
3. Reject generic abstractions as identity unless they are explicitly the document's main subject.
4. Topic angles must be distinct perspectives supported by different evidence clusters in the text.
5. Evidence points must be actual quotes or specific factual claims from the text.
6. If unsure about any field, return an empty string or empty list — do not hallucinate.

GENERIC TERMS TO REJECT AS IDENTITY (unless document is explicitly about them):
- transformasi digital, kualitas keputusan, efektivitas operasional, visibilitas operasional
- keandalan operasional, kesiapan layanan, business continuity, operational visibility
- decision making, operational effectiveness, digital transformation
"""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def read_document_semantics(
    chunks: List[str],
    filename: str = "",
) -> Dict[str, Any]:
    """Extract structured semantic profile from document chunks.

    Parameters
    ----------
    chunks : list of str
        Up to 12 document chunks from the vector store.
    filename : str
        Original filename for reference.

    Returns
    -------
    dict with keys: document_identity, identity_terms, must_preserve_terms,
    specific_topics, topic_angles, domain_terms, evidence_points, rejected_generic_terms
    """
    if not chunks:
        return _fallback("No chunks provided", filename)

    valid = [_clean(c) for c in chunks if _clean(c)]
    if not valid:
        return _fallback("All chunks empty after cleaning", filename)

    # Prepare context
    context = _select_context_chunks(valid, max_chars=5000)
    if not context.strip():
        return _fallback("No meaningful text context", filename)

    # Call LLM
    used_llm = False
    error = None
    result = None

    try:
        api_key = getattr(settings, "openai_api_key", None)
        if api_key:
            result = _call_openai(context, filename)
            used_llm = True
        else:
            error = "No OpenAI API key available"
    except Exception as exc:
        error = str(exc)
        logger.warning("SEMANTIC_READER_LLM_FAILED %s", error)

    if result and result.get("document_identity"):
        result["used_llm"] = used_llm
        result["error"] = error
        _log_result(result, filename)
        return result

    return _fallback(error or "LLM returned empty identity", filename)


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def _call_openai(context_text: str, filename: str) -> Dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=getattr(settings, "openai_api_key", None), timeout=30.0)

    user_prompt = (
        f"Document filename: {filename}\n\n"
        f"Below is the extracted text from this document. "
        f"Analyze it and return a JSON object with these keys:\n\n"
        f"- document_identity (str): The single most specific subject (2-8 words). "
        f"This is what the document is actually about — not a generic business abstraction. "
        f"Use the exact name from the text (e.g. 'Internet of Things', 'HRIS', 'SendQuick Conversa Portal').\n"
        f"- identity_terms (list of str): 2-5 noun phrases that identify what this document "
        f"is about. Include acronym/full-form pairs if present (e.g. 'HRIS', 'Human Resource Information System'). "
        f"These MUST appear verbatim in the text.\n"
        f"- must_preserve_terms (list of str): 3-6 domain-specific noun phrases that "
        f"topic generation must preserve. These are the specific named concepts, products, "
        f"technologies, or domain terms from the document. Include acronym/full-form pairs. "
        f"These MUST appear verbatim in the text.\n"
        f"- specific_topics (list of str): 2-4 distinct specific topics or subtopics "
        f"that the document covers. These are concrete, not generic. "
        f"Examples: 'IoT architecture', 'sensor data processing', 'cloud connectivity' — not "
        f"'operational visibility' or 'decision making'.\n"
        f"- topic_angles (list of str): 2-3 distinct perspectives for topic generation, "
        f"each based on DIFFERENT evidence clusters in the text. "
        f"Each angle must be a different aspect of the document content. "
        f"Examples for an IoT doc: "
        f"['system architecture and components', 'application use cases and implementation', "
        f"'connectivity and data management'] — each drawn from a distinct section.\n"
        f"- domain_terms (list of str): 3-8 domain-specific technical/operational terms "
        f"from the document. Short, specific terms only. "
        f"Examples: 'IoT', 'sensor', 'smart building', 'SCADA', 'HRIS', 'payroll'. "
        f"Do NOT include generic terms like 'transformasi digital', 'kualitas keputusan'.\n"
        f"- evidence_points (list of str): 3-6 specific factual claims, data points, "
        f"or quotes from the document that support the document identity. "
        f"Be specific — include numbers, names, or concrete statements from the text.\n"
        f"- rejected_generic_terms (list of str): 0-4 generic terms that appear in the "
        f"text but should NOT become the document identity. "
        f"Examples: 'kualitas keputusan', 'efektivitas operasional', 'visibilitas operasional', "
        f"'transformasi digital', 'bisnis proses'.\n\n"
        f"CRITICAL: All terms listed must appear VERBATIM in the text below.\n"
        f"Focus on what makes this document UNIQUE, not on generic business abstractions.\n"
        f"topic_angles must be DISTINCT — each must describe a different section/aspect of the document.\n\n"
        f"=== DOCUMENT TEXT ===\n"
        f"{context_text}"
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=800,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content if response.choices else ""
    data = json.loads(content or "{}")

    return {
        "document_identity": str(data.get("document_identity") or ""),
        "identity_terms": list(data.get("identity_terms") or []),
        "must_preserve_terms": list(data.get("must_preserve_terms") or []),
        "specific_topics": list(data.get("specific_topics") or []),
        "topic_angles": list(data.get("topic_angles") or []),
        "domain_terms": list(data.get("domain_terms") or []),
        "evidence_points": list(data.get("evidence_points") or []),
        "rejected_generic_terms": list(data.get("rejected_generic_terms") or []),
    }


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _fallback(reason: str, filename: str) -> Dict[str, Any]:
    logger.info("SEMANTIC_READER_FALLBACK %s", {"reason": reason, "filename": filename})
    return {
        "document_identity": "",
        "identity_terms": [],
        "must_preserve_terms": [],
        "specific_topics": [],
        "topic_angles": [],
        "domain_terms": [],
        "evidence_points": [],
        "rejected_generic_terms": [],
        "used_llm": False,
        "error": reason,
    }


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log_result(result: Dict[str, Any], filename: str) -> None:
    logger.info(
        "SEMANTIC_READER_RESULT %s",
        json.dumps(
            {
                "filename": filename,
                "document_identity": result.get("document_identity"),
                "identity_terms": result.get("identity_terms"),
                "must_preserve_terms": result.get("must_preserve_terms"),
                "specific_topics": result.get("specific_topics"),
                "topic_angles": result.get("topic_angles"),
                "rejected_generic_terms": result.get("rejected_generic_terms"),
            },
            ensure_ascii=False,
        ),
    )
