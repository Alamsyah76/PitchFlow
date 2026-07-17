"""Image Generation API route — generates image from linkedin_image_prompt.

This endpoint accepts a linkedin_image_prompt (from Image Storytelling Brief)
and passes it verbatim to OpenAI DALL-E 3.  No prompt modification occurs.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.image_generation.schemas import ImageGenerationRequest, ImageGenerationResponse
from app.image_generation.image_client import generate_image
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/image-generation", tags=["image-generation"])


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image_endpoint(req: ImageGenerationRequest) -> ImageGenerationResponse:
    """
    Generate an image from the linkedin_image_prompt verbatim.
    No prompt modification, no upstream regeneration.
    """
    if not req.linkedin_image_prompt or len(req.linkedin_image_prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="linkedin_image_prompt must be at least 10 characters",
        )

    result = generate_image(
        prompt=req.linkedin_image_prompt.strip(),
        image_size=req.image_size,
    )

    if not result.get("success"):
        logger.warning(
            "IMAGE_GENERATION_FAILED error=%s prompt_preview=%s",
            result.get("error_message", ""),
            req.linkedin_image_prompt[:80],
        )

    return ImageGenerationResponse(
        success=result.get("success", False),
        image_url=result.get("image_url", ""),
        provider=result.get("provider", "openai"),
        generation_timestamp=result.get("generation_timestamp", ""),
        provider_metadata=result.get("provider_metadata", {}),
        is_transient_url=result.get("is_transient_url", True),
        expires_in_seconds=result.get("expires_in_seconds", 3600),
        error_message=result.get("error_message"),
    )
