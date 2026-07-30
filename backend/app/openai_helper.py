"""OpenAI Helper — supports BYOK (Bring Your Own Key)"""
import os
from openai import OpenAI
from app.database import get_openai_key

# Default global key (from .env)
_GLOBAL_KEY = os.getenv("OPENAI_API_KEY", "")


def get_client(email: str = None) -> OpenAI:
    """Get OpenAI client — user's key if available, otherwise global key."""
    api_key = _GLOBAL_KEY

    if email:
        user_key = get_openai_key(email)
        if user_key:
            api_key = user_key

    return OpenAI(api_key=api_key, timeout=60.0)
