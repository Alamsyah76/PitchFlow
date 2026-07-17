"""ImageStorytelling — Pydantic schemas for visual story brief generation.

This module defines the request/response schemas for the Image Storytelling
feature.  It is completely independent of the Topic Engine, Caption Engine,
and Hashtag Engine.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ImageStorytellingRequest(BaseModel):
    document_id: str = Field(..., description="Document UUID from parsed storage")
    selected_topic: str = Field(..., description="The chosen topic title")
    caption: str = Field(..., description="The published/validated caption text")
    hashtags: Optional[List[str]] = Field(default=None, description="Optional hashtag chips")
    evidence_terms: Optional[List[str]] = Field(default=None, description="Optional evidence anchor terms")
    business_angle: Optional[str] = Field(default=None, description="Optional business angle identifier")


class VisualStoryBrief(BaseModel):
    visual_headline: str = Field(
        ...,
        description="Short headline that captures the core visual idea in Indonesian",
    )
    core_visual_message: str = Field(
        ...,
        description="One-sentence business message the image should convey",
    )
    scene_concept: str = Field(
        ...,
        description="Paragraph describing the recommended scene/concept",
    )
    main_subject: str = Field(
        ...,
        description="The primary visual subject (abstract or concrete)",
    )
    supporting_elements: List[str] = Field(
        default_factory=list,
        description="Supporting visual elements (max 4)",
    )
    visual_metaphor: str = Field(
        ...,
        description="The visual metaphor or analogy used (if any), or 'none'",
    )
    mood_tone: str = Field(
        ...,
        description="Mood/tone descriptor e.g. 'professional', 'calm', 'forward-looking'",
    )
    negative_constraints: List[str] = Field(
        default_factory=list,
        description="Elements to avoid in image generation",
    )
    linkedin_image_prompt: str = Field(
        ...,
        description="English prompt ready for image generation API (DALL-E / Midjourney)",
    )
    carousel_readiness_notes: str = Field(
        default="",
        description="Optional notes about carousel/tile-readiness of this concept",
    )


class ImageStorytellingResponse(BaseModel):
    success: bool = Field(default=True)
    visual_brief: VisualStoryBrief
    source_topic: str
    source_document_id: str
