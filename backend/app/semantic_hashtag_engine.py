"""SemanticHashtagEngine — strict structured hashtag generation from raw document text.

AUTHORITATIVE PATH (primary):
    run_authoritative_hashtag_engine(chunks, filename)
    → reads RAW document text directly (no abstraction)
    → returns 5-7 LinkedIn-ready PascalCase hashtags

SIGNAL PATH (secondary/fallback):
    generate_linkedin_hashtags(semantic_identity, ..., profile=...)
    → reads semantic metadata (identity terms, domain terms, topic angles)
    → returns structured hashtag dict with identity/topic/industry groups

Replaces: BUSINESS_HASHTAG_RULES, identity_type-only inference, n-gram fallback.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Constants
_MAX_HASHTAGS = 7
_MIN_HASHTAGS = 5


# ---------------------------------------------------------------------------
# Dynamic file-name fallback (last resort when LLM is unavailable)
# ---------------------------------------------------------------------------

def generate_dynamic_fallback_tags(file_name: str) -> List[str]:
    """Generate contextual hashtags from the filename as a last-resort fallback.
    
    Converts the base filename (without extension) into PascalCase tags.
    Never returns generic ERP/Security/Risk tags.
    
    Examples:
        'otomotif.pdf' -> ['#Otomotif', '#OtomotifAnalysis', '#OtomotifData',
                           '#ContentEngineOS', '#SemanticExtraction']
        'financial_report.pdf' -> ['#FinancialReport', '#FinancialReportAnalysis',
                                    '#FinancialReportData', ...]
    """
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', file_name.split('.')[0])
    base_tag = f"#{clean_name.capitalize()}" if clean_name else "#Document"
    return [
        base_tag,
        f"{base_tag}Analysis",
        f"{base_tag}Data",
        "#ContentEngineOS",
        "#SemanticExtraction",
    ]


# ---------------------------------------------------------------------------
# PascalCase formatter
# ---------------------------------------------------------------------------

def _to_pascal_case(phrase: str) -> str:
    """Convert phrase to PascalCase: 'Internet of Things' -> '#InternetOfThings'"""
    if not phrase:
        return ""
    phrase = phrase.strip().strip(".:;!?,-")
    words = re.findall(r"[A-Za-z0-9]+", phrase)
    pascal = "".join(w[0].upper() + w[1:] if w else "" for w in words if w)
    return f"#{pascal}" if pascal else ""


def _validate_format(tag: str) -> bool:
    return bool(tag and tag.startswith("#") and " " not in tag and len(tag) >= 2)


# ---------------------------------------------------------------------------
# AUTHORITATIVE PATH — raw document text
# ---------------------------------------------------------------------------

def run_authoritative_hashtag_engine(
    chunks: List[str],
    filename: str = "",
) -> Dict[str, Any]:
    """Read RAW high-fidelity document text and generate authoritative hashtags.
    
    This is the PRIMARY path. It feeds original chunk text directly to the LLM,
    bypassing any abstraction layer.  The LLM is instructed to extract hashtags
    ONLY from what is actually in the text — no generic business cross-domain tags.
    
    Parameters
    ----------
    chunks : list of str
        Original document chunks (high-fidelity text).
    filename : str
        Original filename for reference.
    
    Returns
    -------
    dict with keys: identity_hashtags, topic_hashtags, industry_hashtags, final_hashtags
    """
    if not chunks:
        return _signals_result({}, filename)
    
    # Select representative chunks for the LLM
    valid = [re.sub(r"\s+", " ", str(c or "")).strip() for c in chunks if c]
    if not valid:
        return _signals_result({}, filename)
    
    # Take first 4 chunks (~4000 chars) as high-fidelity context
    high_fidelity = []
    total = 0
    for v in valid:
        if total + len(v) > 4000:
            remaining = 4000 - total
            if remaining > 200:
                high_fidelity.append(v[:remaining])
            break
        high_fidelity.append(v)
        total += len(v)
    
    context_text = "\n\n".join(high_fidelity)
    if not context_text.strip():
        return _signals_result({}, filename)
    
    # Call LLM with raw text
    used_llm = False
    result = None
    try:
        api_key = getattr(settings, "openai_api_key", None)
        if api_key:
            result = _call_authoritative_openai(context_text, filename)
            used_llm = True
    except Exception as exc:
        logger.warning("AUTHORITATIVE_HASHTAG_LLM_FAILED %s", str(exc))
    
    if result and result.get("final_hashtags") and len(result["final_hashtags"]) >= _MIN_HASHTAGS:
        result["used_llm"] = used_llm
        _log_authoritative(result, filename)
        return result
    
    # Fallback to signal-based path
    logger.info("AUTHORITATIVE_HASHTAG_FALLBACK_TO_SIGNALS %s", {"filename": filename})
    return _signals_result({}, filename)


_AUTHORITATIVE_SYSTEM_PROMPT = """You are a LinkedIn hashtag engine with FULL AUTHORITY over hashtag output.

Your job: generate professional LinkedIn hashtags that are EXACTLY grounded in the document text below.
Do NOT invent tags for concepts that are not explicitly mentioned in the text.

Rules:
1. Extract ONLY from the document text provided below.
2. All hashtags must use PascalCase (e.g. #YamahaR25, #InternetOfThings, not #internet_of_things).
3. Total combined hashtags: minimum 5, maximum 7.
4. identity_hashtags: minimum 2 — from core entities, products, brands, subjects in the text.
5. topic_hashtags: minimum 2 — from specific technical topics or discussion angles in the text.
6. industry_hashtags: minimum 1 — from the domain/industry context.

ABSOLUTELY FORBIDDEN hashtags (do NOT generate these unless the text explicitly discusses them):
#ERP, #ERPWorkflow, #BusinessOperations, #SecurityOperations, #IncidentResponse,
#BusinessContinuity, #DigitalTransformation, #ITInfrastructure, #ITSecurity,
#NetworkSecurity, #RiskManagement, #OperationalExcellence

Return valid JSON only — no explanations, no markdown."""


def _call_authoritative_openai(context_text: str, filename: str) -> Dict[str, Any]:
    from openai import OpenAI
    
    client = OpenAI(api_key=getattr(settings, "openai_api_key", None), timeout=20.0)
    
    user_prompt = (
        f"Document: {filename}\n\n"
        f"=== RAW DOCUMENT TEXT (HIGH-FIDELITY) ===\n"
        f"{context_text}\n\n"
        f"=== TASK ===\n"
        f"Generate LinkedIn hashtags from the text above.\n"
        f"Return JSON with keys:\n"
        f"- identity_hashtags (list of str): min 2, from entities/subjects in the text\n"
        f"- topic_hashtags (list of str): min 2, from specific technical topics\n"
        f"- industry_hashtags (list of str): min 1, from domain/industry\n\n"
        f"Total combined: exactly 5-7 hashtags. PascalCase format. "
        f"NO generic tags. Grounded ONLY in the text above."
    )
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=500,
        messages=[
            {"role": "system", "content": _AUTHORITATIVE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    content = response.choices[0].message.content if response.choices else ""
    data = json.loads(content or "{}")
    
    return _compose_hashtags(data)


def _compose_hashtags(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON response and compose validated hashtags."""
    identity_tags = data.get("identity_hashtags") or []
    topic_tags = data.get("topic_hashtags") or []
    industry_tags = data.get("industry_hashtags") or []
    
    all_tags = []
    for tag in identity_tags + topic_tags + industry_tags:
        pascal = _to_pascal_case(tag.replace("#", ""))
        if pascal and pascal not in all_tags:
            all_tags.append(pascal)
    
    all_tags = all_tags[:_MAX_HASHTAGS]
    return {
        "identity_hashtags": [t for t in all_tags[:3] if _validate_format(t)],
        "topic_hashtags": [t for t in all_tags[3:5] if _validate_format(t)],
        "industry_hashtags": [t for t in all_tags[5:7] if _validate_format(t)],
        "final_hashtags": all_tags[:_MAX_HASHTAGS],
    }


def _log_authoritative(result: Dict[str, Any], filename: str) -> None:
    logger.info(
        "AUTHORITATIVE_HASHTAG_RESULT %s",
        json.dumps({"filename": filename, "hashtags": result.get("final_hashtags", [])},
                   ensure_ascii=False),
    )


# ---------------------------------------------------------------------------
# SIGNAL PATH — semantic metadata (secondary/fallback)
# ---------------------------------------------------------------------------

def generate_linkedin_hashtags(
    *,
    semantic_identity: str = "",
    identity_terms: Optional[List[str]] = None,
    must_preserve_terms: Optional[List[str]] = None,
    domain_terms: Optional[List[str]] = None,
    topic_angles: Optional[List[str]] = None,
    macro_topics: Optional[List[str]] = None,
    micro_topics: Optional[List[str]] = None,
    selected_topic: str = "",
    profile: Optional[Dict[str, Any]] = None,
    filename: str = "",
    chunks: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate LinkedIn hashtags from semantic metadata.
    
    If raw chunks are provided, uses the AUTHORITATIVE path (preferred).
    Otherwise uses semantic metadata signals.
    """
    # Prefer authoritative path when chunks are available
    if chunks:
        return run_authoritative_hashtag_engine(chunks, filename)
    
    signals = _collect_signals(
        semantic_identity=semantic_identity,
        identity_terms=identity_terms,
        must_preserve_terms=must_preserve_terms,
        domain_terms=domain_terms,
        topic_angles=topic_angles,
        macro_topics=macro_topics,
        micro_topics=micro_topics,
        selected_topic=selected_topic,
        profile=profile,
        filename=filename,
    )
    
    used_llm = False
    result = None
    try:
        api_key = getattr(settings, "openai_api_key", None)
        if api_key:
            result = _call_signals_openai(signals, filename)
            used_llm = True
    except Exception as exc:
        logger.warning("HASHTAG_SIGNAL_LLM_FAILED %s", str(exc))
    
    if result and result.get("final_hashtags"):
        result["used_llm"] = used_llm
        _log_result(result, filename, signals)
        return result
    
    return _signals_result(signals, filename)


def _collect_signals(
    semantic_identity: str = "",
    identity_terms: Optional[List[str]] = None,
    must_preserve_terms: Optional[List[str]] = None,
    domain_terms: Optional[List[str]] = None,
    topic_angles: Optional[List[str]] = None,
    macro_topics: Optional[List[str]] = None,
    micro_topics: Optional[List[str]] = None,
    selected_topic: str = "",
    profile: Optional[Dict[str, Any]] = None,
    filename: str = "",
) -> Dict[str, Any]:
    profile = profile or {}
    return {
        "filename": filename,
        "semantic_identity": semantic_identity or profile.get("_semantic_identity", ""),
        "identity_terms": identity_terms or profile.get("_semantic_identity_terms", []),
        "must_preserve_terms": must_preserve_terms or profile.get("_semantic_must_preserve", []),
        "domain_terms": domain_terms or profile.get("_semantic_domain_terms", []),
        "topic_angles": topic_angles or profile.get("_semantic_topic_angles", []) or profile.get("_diversity_topic_angles", []),
        "macro_topics": macro_topics or profile.get("_diversity_macro_topics", []),
        "micro_topics": micro_topics or profile.get("_diversity_micro_topics", []),
        "selected_topic": selected_topic or "",
        "document_about": profile.get("document_about", ""),
        "solution_capability": profile.get("solution_capability", ""),
        "business_outcome": profile.get("business_outcome", ""),
    }


def _call_signals_openai(signals: Dict[str, Any], filename: str) -> Dict[str, Any]:
    from openai import OpenAI
    client = OpenAI(api_key=getattr(settings, "openai_api_key", None), timeout=15.0)
    
    context_parts = []
    if signals.get("semantic_identity"):
        context_parts.append(f"Document Identity: {signals['semantic_identity']}")
    if signals.get("identity_terms"):
        context_parts.append(f"Identity Terms: {', '.join(signals['identity_terms'][:6])}")
    if signals.get("must_preserve_terms"):
        context_parts.append(f"Key Concepts: {', '.join(signals['must_preserve_terms'][:6])}")
    if signals.get("domain_terms"):
        context_parts.append(f"Domain Terms: {', '.join(signals['domain_terms'][:8])}")
    if signals.get("topic_angles"):
        context_parts.append(f"Topic Angles: {', '.join(signals['topic_angles'][:4])}")
    if signals.get("selected_topic"):
        context_parts.append(f"Selected Topic: {signals['selected_topic']}")
    context_text = "\n".join(context_parts)
    
    user_prompt = (
        f"Document: {filename}\n\n{context_text}\n\n"
        f"Return JSON — identity_hashtags (min 2), topic_hashtags (min 2), "
        f"industry_hashtags (min 1). PascalCase. Total 5-7. "
        f"NO generic tags. Grounded only in signals above."
    )
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        response_format={"type": "json_object"},
        temperature=0, max_tokens=400,
        messages=[{"role": "user", "content": user_prompt}],
    )
    content = response.choices[0].message.content if response.choices else ""
    return _compose_hashtags(json.loads(content or "{}"))


def _signals_result(signals: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Rule-based fallback from semantic signals when LLM unavailable."""
    seen = set()
    hashtags = []
    for key in ["semantic_identity", "document_about", "solution_capability"]:
        text = signals.get(key, "")
        if text:
            tag = _to_pascal_case(text)
            if tag and tag not in seen:
                seen.add(tag); hashtags.append(tag)
    for term in (signals.get("identity_terms") or [])[:3]:
        tag = _to_pascal_case(term)
        if tag and tag not in seen:
            seen.add(tag); hashtags.append(tag)
    for term in (signals.get("domain_terms") or [])[:3]:
        tag = _to_pascal_case(term)
        if tag and tag not in seen and len(hashtags) < 5:
            seen.add(tag); hashtags.append(tag)
    hashtags = hashtags[:_MAX_HASHTAGS]
    return {
        "identity_hashtags": [t for t in hashtags[:3] if _validate_format(t)],
        "topic_hashtags": [t for t in hashtags[3:5] if _validate_format(t)],
        "industry_hashtags": [t for t in hashtags[5:7] if _validate_format(t)],
        "final_hashtags": hashtags[:_MAX_HASHTAGS],
    }


def _log_result(result: Dict[str, Any], filename: str, signals: Dict[str, Any]) -> None:
    logger.info(
        "HASHTAG_ENGINE_RESULT %s",
        json.dumps({"filename": filename, "hashtags": result.get("final_hashtags", [])},
                   ensure_ascii=False),
    )
