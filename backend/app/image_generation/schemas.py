"""Image Generation — Pydantic schemas for image generation request/response.

This module defines request/response schemas for generating an image from
an existing linkedin_image_prompt.  It is completely independent of the
Topic Engine, Caption Engine, Hashtag Engine, and Image Storytelling Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    linkedin_image_prompt: str = Field(
        ...,
        description="The verbatim linkedin_image_prompt from the Image Storytelling brief",
        min_length=10,
    )
    image_size: str = Field(
        default="1024x1024",
        description="Desired image size (OpenAI: 1024x1024, 1024x1792, 1792x1024)",
    )


class ImageGenerationResponse(BaseModel):
    success: bool = Field(default=True)
    image_url: str = Field(default="", description="Transient URL of the generated image")
    provider: str = Field(default="openai", description="Provider used for generation")
    generation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC timestamp of generation",
    )
    provider_metadata: Dict[str, Any] = Field(default_factory=dict)
    is_transient_url: bool = Field(default=True)
    expires_in_seconds: int = Field(default=3600)
    error_message: Optional[str] = Field(default=None)
