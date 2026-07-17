"""Visual Story Generator — LLM call layer for Image Storytelling.

This module calls the LLM with the visual story prompt and parses the JSON
response.  Temperature is locked to 0.15 for controlled creativity.

It does NOT modify any Topic Engine, Caption Engine, or Hashtag Engine code.
"""

import json
import os
from typing import Any, Dict, List, Optional
from openai import OpenAI

from app.image_storytelling.prompt_builder import build_visual_story_prompt
from app.image_storytelling.safety_guard import validate_visual_brief
from config import settings as app_settings
from utils.logger import get_logger

logger = get_logger(__name__)


def _llm_call(prompt: str) -> Optional[str]:
    """Call OpenAI with temperature=0.22 for controlled creative metaphors."""
    api_key = os.environ.get("OPENAI_API_KEY") or app_settings.openai_api_key
    model = os.environ.get("OPENAI_CHAT_MODEL") or app_settings.openai_chat_model or "gpt-4o"
    if not api_key:
        logger.warning("OPENAI_API_KEY not configured for visual story generator")
        return None
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.22,
            max_tokens=1200,
        )
        raw = response.choices[0].message.content.strip() if response.choices else ""
        return raw
    except Exception as e:
        logger.error("VISUAL_STORY_LLM_ERROR %s", str(e))
        return None


def generate_visual_story_brief(
    *,
    selected_topic: str,
    caption: str,
    hashtags: Optional[List[str]] = None,
    evidence_terms: Optional[List[str]] = None,
    business_angle: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a VisualStoryBrief from the given topic + caption.
    Returns dict with {success, visual_brief, warnings, error} keys.
    """
    prompt = build_visual_story_prompt(
        selected_topic=selected_topic,
        caption=caption,
        hashtags=hashtags,
        evidence_terms=evidence_terms,
        business_angle=business_angle,
    )

    raw = _llm_call(prompt)
    if not raw:
        return {
            "success": False,
            "error": "LLM returned empty response",
        }

    # Parse JSON — strip markdown fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Remove markdown code fences
        cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
        cleaned = cleaned.rsplit("```", 1)[0] if "```" in cleaned else cleaned
        cleaned = cleaned.strip()

    try:
        brief = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("VISUAL_STORY_JSON_PARSE_ERROR pos=%s raw=%s", e.pos, raw[:500])
        return {
            "success": False,
            "error": f"JSON parse error: {e}",
            "raw_response": raw[:1000],
        }

    # Safety guard
    ev = evidence_terms or []
    guard_result = validate_visual_brief(brief, ev)

    if not guard_result["is_safe"]:
        logger.warning(
            "VISUAL_STORY_SAFETY_WARNINGS %s",
            json.dumps(guard_result["warnings"], ensure_ascii=False),
        )

    return {
        "success": True,
        "visual_brief": brief,
        "warnings": guard_result["warnings"],
    }
