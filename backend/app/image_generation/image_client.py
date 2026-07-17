"""OpenAI Image Client — async image generation via OpenAI Images API.

This module is a stateless proxy.  It does NOT alter the prompt text.
It does NOT store images persistently.
"""

import base64
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from openai import OpenAI, BadRequestError, APIError, APITimeoutError, RateLimitError
from openai.types.images_response import ImagesResponse

from config import settings as app_settings
from utils.logger import get_logger

logger = get_logger(__name__)

_OPENAI_MODEL = "gpt-image-2"
_MAX_RETRIES = 2
_RETRY_DELAY_SEC = 2.0
_REQUEST_TIMEOUT_SEC = 120


def _get_client() -> OpenAI:
    """Get OpenAI client using existing OPENAI_API_KEY."""
    api_key = os.environ.get("OPENAI_API_KEY") or app_settings.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=api_key, timeout=_REQUEST_TIMEOUT_SEC)


def _build_provider_metadata(response: ImagesResponse) -> Dict[str, Any]:
    """Extract safe metadata from the OpenAI API response."""
    created_ts = datetime.fromtimestamp(response.created, tz=timezone.utc).isoformat() if response.created else ""
    data = response.data[0] if response.data else None
    return {
        "model": _OPENAI_MODEL,
        "created": created_ts,
        "revised_prompt": data.revised_prompt if data and hasattr(data, "revised_prompt") else None,
        "response_format": "url" if (data and data.url) else ("b64_json" if (data and data.b64_json) else "unknown"),
    }


def generate_image(prompt: str, image_size: str = "1024x1024") -> Dict[str, Any]:
    """
    Generate one image from the verbatim prompt using OpenAI DALL-E 3.

    Returns a dict matching ImageGenerationResponse schema.
    The prompt is passed verbatim — no modification, no prefix, no suffix.
    """
    client = _get_client()

    for attempt in range(1 + _MAX_RETRIES):
        try:
            response: ImagesResponse = client.images.generate(
                model=_OPENAI_MODEL,
                prompt=prompt,
                size=image_size,
                n=1,
            )

            image_url = response.data[0].url if response.data and response.data[0].url else ""
            if not image_url and response.data and response.data[0].b64_json:
                image_url = f"data:image/png;base64,{response.data[0].b64_json}"
            if not image_url:
                return {
                    "success": False,
                    "error_message": "OpenAI returned empty image URL",
                    "provider": "openai",
                    "image_url": "",
                    "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider_metadata": {},
                    "is_transient_url": True,
                    "expires_in_seconds": 3600,
                }

            return {
                "success": True,
                "image_url": image_url,
                "provider": "openai",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider_metadata": _build_provider_metadata(response),
                "is_transient_url": True,
                "expires_in_seconds": 3600,
                "error_message": None,
            }

        except BadRequestError as e:
            # Safety rejection or invalid prompt — do not retry
            logger.warning("IMAGE_GENERATION_SAFETY_REJECTION attempt=%d error=%s", attempt + 1, str(e))
            return {
                "success": False,
                "error_message": f"Content policy violation: {e.message or str(e)}",
                "provider": "openai",
                "image_url": "",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider_metadata": {"model": _OPENAI_MODEL},
                "is_transient_url": True,
                "expires_in_seconds": 3600,
            }

        except RateLimitError as e:
            logger.warning("IMAGE_GENERATION_RATE_LIMIT attempt=%d error=%s", attempt + 1, str(e))
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY_SEC * (attempt + 1))
                continue
            return {
                "success": False,
                "error_message": "Rate limit exceeded. Please wait and try again.",
                "provider": "openai",
                "image_url": "",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider_metadata": {"model": _OPENAI_MODEL},
                "is_transient_url": True,
                "expires_in_seconds": 3600,
            }

        except APITimeoutError as e:
            logger.warning("IMAGE_GENERATION_TIMEOUT attempt=%d error=%s", attempt + 1, str(e))
            if attempt < _MAX_RETRIES:
                continue
            return {
                "success": False,
                "error_message": "Image generation timed out. Please try again.",
                "provider": "openai",
                "image_url": "",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider_metadata": {"model": _OPENAI_MODEL},
                "is_transient_url": True,
                "expires_in_seconds": 3600,
            }

        except APIError as e:
            logger.error("IMAGE_GENERATION_API_ERROR attempt=%d error=%s", attempt + 1, str(e))
            if attempt < _MAX_RETRIES:
                continue
            return {
                "success": False,
                "error_message": f"Image generation API error: {str(e)[:200]}",
                "provider": "openai",
                "image_url": "",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider_metadata": {"model": _OPENAI_MODEL},
                "is_transient_url": True,
                "expires_in_seconds": 3600,
            }

        except Exception as e:
            logger.error("IMAGE_GENERATION_UNEXPECTED_ERROR %s", str(e))
            return {
                "success": False,
                "error_message": f"Unexpected error: {str(e)[:200]}",
                "provider": "openai",
                "image_url": "",
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "provider_metadata": {"model": _OPENAI_MODEL},
                "is_transient_url": True,
                "expires_in_seconds": 3600,
            }

    return {
        "success": False,
        "error_message": "Image generation failed after all retries",
        "provider": "openai",
        "image_url": "",
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "provider_metadata": {"model": _OPENAI_MODEL},
        "is_transient_url": True,
        "expires_in_seconds": 3600,
    }
