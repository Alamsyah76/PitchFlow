from __future__ import annotations

from typing import Iterable, List


RAW_KEYWORD_DUMP_PHRASES = (
    "bukti yang dipilih menunjukkan perlunya",
    "materi ini menekankan pentingnya",
)

LOW_QUALITY_BUSINESS_TOKENS = {
    "built",
    "reduce",
    "they",
    "other",
    "normaliz",
    "large",
    "mouse",
}


def join_text(parts: Iterable[str]) -> str:
    return " ".join(str(part or "") for part in parts).lower()


def forbidden_terms_for_domain(domain: str) -> List[str]:
    if domain == "erp":
        return ["sensor monitoring", "monitoringit", "infrastrukturit", "network sensor", "device traffic"]
    if domain == "hardware":
        return ["monitoring platform", "alert monitoring", "sensor monitoring", "traffic monitoring"]
    if domain == "fortinet":
        return ["erp one", "klipboard", "dell", "optiplex"]
    return []


def assert_absent_terms(text: str, forbidden: Iterable[str]) -> None:
    lowered = str(text or "").lower()
    for term in forbidden:
        assert term.lower() not in lowered, f"Unexpected forbidden term found: {term}"


def assert_contains_any(text: str, allowed: Iterable[str]) -> None:
    lowered = str(text or "").lower()
    assert any(term.lower() in lowered for term in allowed), f"Expected one of {list(allowed)} in output"


def assert_no_keyword_dump(caption: str) -> None:
    lowered = str(caption or "").lower()
    for phrase in RAW_KEYWORD_DUMP_PHRASES:
        assert phrase not in lowered, f"Keyword dump phrase found: {phrase}"
    for token in LOW_QUALITY_BUSINESS_TOKENS:
        assert token not in lowered, f"Low-quality business token leaked: {token}"
