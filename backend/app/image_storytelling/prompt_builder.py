"""Visual storytelling prompt builder — constructs the LLM prompt for visual brief generation.

This module ONLY builds the prompt string.  It does NOT call any LLM.
"""

from typing import List, Optional


def build_visual_story_prompt(
    *,
    selected_topic: str,
    caption: str,
    hashtags: Optional[List[str]] = None,
    evidence_terms: Optional[List[str]] = None,
    business_angle: Optional[str] = None,
) -> str:
    """
    Build a controlled-creativity prompt for the LLM to produce a
    JSON visual story brief.  Temperature at 0.22 for controlled creativity.
    """
    evidence_section = ""
    if evidence_terms:
        evidence_section = (
            "EVIDENCE ANCHORS (ground your visuals in these terms):\n"
            + "\n".join(f"- {term}" for term in evidence_terms)
            + "\n\n"
        )

    hashtag_section = ""
    if hashtags:
        hashtag_section = (
            "HASHTAGS (context signals):\n"
            + " ".join(hashtags[:6])
            + "\n\n"
        )

    angle_section = ""
    if business_angle:
        angle_section = f"BUSINESS ANGLE: {business_angle}\n\n"

    return (
        "You are a B2B creative director writing a visual story brief for a "
        "corporate LinkedIn post. Your output must be a short visual story — "
        "not just a description of what an image should contain, but a narrative "
        "moment that a single still frame can capture.\n\n"
        "Output JSON with the following schema — JSON only, no markdown, no commentary:\n\n"
        "{\n"
        '  "visual_headline": "...",\n'
        '  "core_visual_message": "...",\n'
        '  "scene_concept": "...",\n'
        '  "main_subject": "...",\n'
        '  "supporting_elements": ["...", "..."],\n'
        '  "visual_metaphor": "...",\n'
        '  "mood_tone": "...",\n'
        '  "negative_constraints": ["...", "..."],\n'
        '  "linkedin_image_prompt": "...",\n'
        '  "carousel_readiness_notes": "..."\n'
        "}\n\n"
        "HARD RULES:\n"
        "1. Every visual element MUST be grounded in selected_topic, caption, and evidence anchors below. "
        "Do NOT invent entities unsupported by the source material.\n"
        "2. If evidence is weak or minimal, default to a safe, concrete business metaphor "
        "tied to the topic — do NOT fall back to generic technology imagery.\n"
        "3. DO NOT invent: human faces, brand logos, device UIs, dashboards, charts, "
        "fictional locations, or product screenshots UNLESS explicitly mentioned in evidence.\n"
        "4. scene_concept MUST include: (a) narrative tension or operational contrast "
        "(e.g. before/after, problem-to-solution, hidden-to-visible), "
        "(b) one concrete business metaphor grounded in the topic domain, "
        "(c) a brief why-this-matters hook. "
        "Avoid static descriptions like 'A professional looking at a screen'.\n"
        "5. linkedin_image_prompt MUST be in English, written in professional "
        "B2B Midjourney/DALL-E style. Automatically append negative constraints "
        "at the end as '--no ...' syntax. "
        "Forbidden generic phrases: 'abstract digital network', 'flowing data streams', "
        "'interconnected nodes', 'futuristic dashboard', 'glowing blue technology background'. "
        "Do NOT use these unless explicitly supported by evidence.\n"
        "6. visual_headline MUST be in English — a short punchy line that captures "
        "the narrative tension of the scene.\n"
        "7. Each output field must be specific to this selected_topic and caption. "
        "The brief must NOT be reusable for an unrelated PDF. "
        "If you can swap the topic name and the brief still makes sense, it is too generic.\n"
        "8. negative_constraints must include: 'human faces', 'brand logos', 'detailed UI elements', "
        "'fictional data charts' plus any topic-specific constraints. "
        "These constraints must also be automatically appended to linkedin_image_prompt "
        "using standard prompt syntax like '--no human faces, brand logos, detailed UI elements'.\n"
        "9. Do NOT invent industry assumptions. "
        "If the document does not specify an industry, do not force one.\n"
        "10. core_visual_message should be one sentence explaining what the viewer "
        "should understand after seeing the image.\n"
        "11. visual_metaphor should name the concrete metaphor used (e.g. 'bridge', "
        "'radar', 'blueprint', 'compass'), or 'none' if no metaphor is used.\n"
        "12. main_subject should be a single noun phrase describing the primary "
        "visual anchor (e.g. 'broken chain link', 'radar screen with a blind spot', "
        "'stack of paper forms next to a tablet').\n\n"
        f"SELECTED TOPIC:\n{selected_topic}\n\n"
        f"CAPTION:\n{caption}\n\n"
        f"{hashtag_section}"
        f"{angle_section}"
        f"{evidence_section}"
        "Output ONLY valid JSON — no markdown fences, no commentary, no extra text."
    )
