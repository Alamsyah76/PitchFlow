"""Safety guard for Image Storytelling — validates that brief does not hallucinate.

This module runs AFTER LLM generation to catch:
- unsupported visual claims
- hallucinated entities
- aggressive promotional language in the image prompt
"""

import re
from typing import List

# Phrases that should NOT appear in linkedin_image_prompt or scene_concept
_FORBIDDEN_VISUAL_CLAIMS = [
    "award-winning",
    "industry-leading",
    "revolutionary",
    "game-changing",
    "unprecedented",
    "breakthrough",
    "world-class",
    "cutting-edge",
    "next-generation",
    "patent-pending",
    "proprietary",
    "exclusive",
    "guaranteed",
    "guaranteed results",
]

# Terms that require explicit evidence to appear in a visual brief
_HIGH_RISK_VISUAL_ELEMENTS = [
    "dashboard",
    "ui",
    "user interface",
    "screenshot",
    "chart with data",
    "graph showing",
    "logo",
    "human face",
    "person smiling",
    "office interior",
    "data center",
    "server room",
]


def _check_forbidden_claims(text: str, field_name: str) -> List[str]:
    """Return list of forbidden claims found in text for the given field."""
    violations = []
    lower = text.lower()
    for phrase in _FORBIDDEN_VISUAL_CLAIMS:
        if phrase in lower:
            violations.append(f"{field_name}: forbidden claim '{phrase}'")
    return violations


def _check_high_risk_elements(text: str, evidence_terms: List[str]) -> List[str]:
    """Return list of high-risk elements that lack evidence support."""
    violations = []
    lower = text.lower()
    evidence_lower = [t.lower() for t in evidence_terms]
    for element in _HIGH_RISK_VISUAL_ELEMENTS:
        if element in lower:
            # Check if any evidence term supports this element
            supported = any(
                term in element or element in term
                for term in evidence_lower
            )
            if not supported:
                violations.append(
                    f"high-risk visual element '{element}' without evidence support"
                )
    return violations


def validate_visual_brief(
    brief: dict,
    evidence_terms: List[str],
) -> dict:
    """
    Validate a visual story brief dict for hallucination and unsupported claims.

    Returns:
        {
            "is_safe": bool,
            "warnings": List[str],
            "blocked_fields": List[str],
        }
    """
    warnings: List[str] = []
    blocked: List[str] = []

    for field in ("scene_concept", "linkedin_image_prompt", "core_visual_message"):
        text = brief.get(field, "")
        if not text:
            continue
        forbidden = _check_forbidden_claims(text, field)
        warnings.extend(forbidden)
        if forbidden:
            blocked.append(field)

    for field in ("scene_concept", "linkedin_image_prompt"):
        text = brief.get(field, "")
        if not text:
            continue
        high_risk = _check_high_risk_elements(text, evidence_terms)
        warnings.extend(high_risk)

    return {
        "is_safe": len(blocked) == 0,
        "warnings": warnings,
        "blocked_fields": blocked,
    }
