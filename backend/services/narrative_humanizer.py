from __future__ import annotations

import hashlib
import re
from typing import Optional


OPENING_VARIANTS = [
    "Yang sering terjadi di lapangan adalah:",
    "Banyak tim menghadapi situasi yang sama:",
    "Tantangannya bukan selalu pada kurangnya data:",
    "Dalam praktiknya, tantangan sering muncul ketika:",
]

IMPACT_VARIANTS = [
    "Dari sisi operasional, dampaknya mulai terasa ketika:",
    "Nilai praktisnya muncul saat:",
    "Dampaknya bukan hanya teknis:",
    "Bagi organisasi, ini mulai penting ketika:",
]

QUESTION_VARIANTS = [
    "Prioritas mana yang biasanya paling sulit terbaca lebih awal?",
    "Apakah konteks seperti ini juga terlihat di lingkungan Anda?",
    "Sinyal mana yang paling sering terlambat dipahami sebelum keputusan dibuat?",
    "Bagian mana yang paling sering luput sebelum keputusan penting diambil?",
]


def _stable_index(seed: str, size: int) -> int:
    if size <= 0:
        return 0

    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % size


def _pick(seed: str, options: list[str]) -> str:
    return options[_stable_index(seed, len(options))]


def _extract_topic_terms(topic: str) -> list[str]:
    if not topic:
        return []

    stopwords = {
        "yang",
        "dan",
        "atau",
        "untuk",
        "dalam",
        "dengan",
        "lebih",
        "menjadi",
        "membantu",
        "melalui",
        "sebagai",
        "pada",
        "dari",
        "ke",
        "di",
        "ini",
        "itu",
    }

    terms: list[str] = []

    for word in re.findall(r"[A-Za-zÀ-ÿ0-9]+", topic):
        normalized = word.lower().strip()

        if len(normalized) < 5:
            continue

        if normalized in stopwords:
            continue

        terms.append(normalized)

    return list(dict.fromkeys(terms))


def _preserve_topic_terms(
    original_caption: str,
    humanized_caption: str,
    selected_topic: str,
) -> str:
    """
    Safety guard:
    If an important topic term existed in the original caption,
    it must still exist after humanization.

    If not, return the original caption.
    """

    original_lower = original_caption.lower()
    humanized_lower = humanized_caption.lower()

    for term in _extract_topic_terms(selected_topic):
        if term in original_lower and term not in humanized_lower:
            return original_caption

    return humanized_caption


def _preserve_hashtag_block(
    original_caption: str,
    humanized_caption: str,
) -> str:
    """
    Preserve hashtags at the end if the caption contains them.
    This avoids accidental hashtag changes during polishing.
    """

    original_lines = original_caption.rstrip().splitlines()
    humanized_lines = humanized_caption.rstrip().splitlines()

    original_hashtag_lines = [
        line for line in original_lines if line.strip().startswith("#")
    ]

    if not original_hashtag_lines:
        return humanized_caption

    humanized_without_hashtags = [
        line for line in humanized_lines if not line.strip().startswith("#")
    ]

    return "\n".join(humanized_without_hashtags).rstrip() + "\n\n" + "\n".join(original_hashtag_lines)


def humanize_caption(
    caption: str,
    selected_topic: str,
    dominant_identity: Optional[str] = None,
    hashtags: Optional[list[str]] = None,
) -> str:
    """
    Post-generation Narrative Humanization Layer.

    This function is intentionally deterministic and rule-based.

    It must NOT:
    - rewrite the caption freely
    - add new facts
    - change selected topic
    - change dominant document identity
    - change hashtags
    - override semantic grounding
    - call an LLM

    It only reduces repetitive AI-ish phrasing after the caption
    has already been generated and grounded.
    """

    if not caption or not caption.strip():
        return caption

    seed = f"{selected_topic or ''}|{dominant_identity or ''}"

    opening = _pick(seed + "|opening", OPENING_VARIANTS)
    impact = _pick(seed + "|impact", IMPACT_VARIANTS)
    question = _pick(seed + "|question", QUESTION_VARIANTS)

    result = caption

    phrase_replacements = {
        "Masalah utamanya sederhana:": opening,
        "Implikasi bisnisnya cukup jelas:": impact,
        "Bagian mana yang paling perlu dibuat lebih terbaca sebelum keputusan berikutnya diambil?": question,
    }

    for old_phrase, new_phrase in phrase_replacements.items():
        result = result.replace(old_phrase, new_phrase)

    result = _preserve_hashtag_block(
        original_caption=caption,
        humanized_caption=result,
    )

    result = _preserve_topic_terms(
        original_caption=caption,
        humanized_caption=result,
        selected_topic=selected_topic,
    )

    return result