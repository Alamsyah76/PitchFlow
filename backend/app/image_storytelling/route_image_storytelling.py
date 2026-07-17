"""Image Storytelling API route — add-only endpoint for visual brief generation.

This endpoint does NOT modify any existing topic/caption routes.
It only reads from the Caption Studio state.
"""

import json
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.image_storytelling.schemas import (
    ImageStorytellingRequest,
    ImageStorytellingResponse,
    VisualStoryBrief,
)
from app.image_storytelling.visual_story_generator import generate_visual_story_brief
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/image-storytelling", tags=["image-storytelling"])


@router.post("/generate", response_model=ImageStorytellingResponse)
async def generate_image_storytelling(req: ImageStorytellingRequest) -> Any:
    """
    Generate a visual story brief from the selected topic and caption.
    This is a pure text generator — no image API is called.
    """
    if not req.selected_topic or not req.caption:
        raise HTTPException(
            status_code=400,
            detail="Both selected_topic and caption are required",
        )

    result = generate_visual_story_brief(
        selected_topic=req.selected_topic,
        caption=req.caption,
        hashtags=req.hashtags,
        evidence_terms=req.evidence_terms,
        business_angle=req.business_angle,
    )

    if not result.get("success"):
        error = result.get("error", "Unknown error")
        logger.error("IMAGE_STORYTELLING_GENERATION_FAILED error=%s", error)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": error},
        )

    brief_data: Dict[str, Any] = result["visual_brief"]
    visual_brief = VisualStoryBrief(
        visual_headline=brief_data.get("visual_headline", ""),
        core_visual_message=brief_data.get("core_visual_message", ""),
        scene_concept=brief_data.get("scene_concept", ""),
        main_subject=brief_data.get("main_subject", ""),
        supporting_elements=brief_data.get("supporting_elements", []),
        visual_metaphor=brief_data.get("visual_metaphor", "none"),
        mood_tone=brief_data.get("mood_tone", "professional"),
        negative_constraints=brief_data.get("negative_constraints", []),
        linkedin_image_prompt=brief_data.get("linkedin_image_prompt", ""),
        carousel_readiness_notes=brief_data.get("carousel_readiness_notes", ""),
    )

    logger.info(
        "IMAGE_STORYTELLING_GENERATED doc=%s topic=%s",
        req.document_id,
        req.selected_topic[:60],
    )

    return ImageStorytellingResponse(
        success=True,
        visual_brief=visual_brief,
        source_topic=req.selected_topic,
        source_document_id=req.document_id,
    )
