"""
Gemini API Service Module
Handles Google Gemini 1.5 Flash API calls with Context Caching for token savings
"""

import asyncio
import json
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiCacheManager:
    """Manages Gemini API Context Caching for token savings"""
    
    _cache_store: Dict[str, Dict] = {}  # In-memory cache for demo (use Redis in production)
    
    @classmethod
    def get_cached_content_name(cls, document_id: str, version: str = "v1") -> str:
        """
        Generate a cache name for Gemini Context Caching.
        Gemini allows reusing cached content IDs within 30 minutes.
        
        Args:
            document_id: Document UUID
            version: Cache version identifier
            
        Returns:
            Cache content name
        """
        return f"projects/documents/{document_id}/cached_content_{version}"
    
    @classmethod
    def is_cache_valid(cls, document_id: str) -> bool:
        """
        Check if cache is still valid (within 30-minute window).
        
        Args:
            document_id: Document UUID
            
        Returns:
            True if cache is valid, False otherwise
        """
        if document_id not in cls._cache_store:
            return False
        
        cache_entry = cls._cache_store[document_id]
        created_at = cache_entry.get("created_at")
        
        if created_at is None:
            return False
        
        # Gemini keeps cache for 30 minutes
        expires_at = created_at + timedelta(minutes=30)
        is_valid = datetime.utcnow() < expires_at
        
        logger.debug(f"Cache validity check: {is_valid} for document {document_id}")
        return is_valid
    
    @classmethod
    def store_cache_metadata(cls, document_id: str, cache_name: str, metadata: Dict):
        """
        Store cache metadata for future reference.
        
        Args:
            document_id: Document UUID
            cache_name: Cache name from Gemini API
            metadata: Additional metadata (content size, etc.)
        """
        cls._cache_store[document_id] = {
            "cache_name": cache_name,
            "created_at": datetime.utcnow(),
            "metadata": metadata
        }
        logger.info(f"Stored cache metadata for document {document_id}")


class GeminiService:
    """Service for Google Gemini 1.5 Flash API calls with caching"""
    
    def __init__(self):
        """Initialize Gemini service with API configuration"""
        self.api_key = settings.gemini_api_key
        self.model = "gemini-1.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.timeout = 60
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_topics(
        self,
        context_chunks: List[str],
        document_id: str,
        target_language: str = "en",
        use_cache: bool = True
    ) -> Optional[List[str]]:
        """
        Generate exactly 3 topics from context chunks using Gemini 1.5 Flash.
        Implements Context Caching for token savings on large documents.
        
        Args:
            context_chunks: List of relevant text chunks (usually top-3 from similarity search)
            document_id: Document UUID for cache management
            target_language: Target language ("en" or "id")
            use_cache: Whether to use Context Caching feature
            
        Returns:
            List of exactly 3 topics as strings, or None if generation fails
            
        Raises:
            RuntimeError: If API call fails after retries
        """
        try:
            # Combine chunks into context
            combined_context = "\n\n".join(context_chunks)
            
            # Prepare system prompt
            system_prompt = self._get_system_prompt(target_language)
            
            # Build request body
            request_body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": f"""Based on the following document context, generate exactly 3 unique, 
                                engaging topics for LinkedIn content. Return ONLY a valid JSON array with exactly 3 topic strings, 
                                no markdown, no prose, no explanations.
                                
                                Document Context:
                                {combined_context}
                                
                                Remember: Return ONLY valid JSON array like this format:
                                ["Topic 1", "Topic 2", "Topic 3"]"""
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 500,
                }
            }
            
            # Add system prompt as system instruction if supported
            request_body["systemInstruction"] = {
                "role": "user",
                "parts": [
                    {
                        "text": system_prompt
                    }
                ]
            }
            
            # Add caching configuration if enabled
            if use_cache and GeminiCacheManager.is_cache_valid(document_id):
                cache_name = GeminiCacheManager.get_cached_content_name(document_id)
                request_body["cachedContent"] = cache_name
                logger.info(f"Using cached content for document {document_id}")
            
            # Make API call
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{self.model}:generateContent",
                    params={"key": self.api_key},
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract generated text
                if "candidates" not in result or len(result["candidates"]) == 0:
                    raise ValueError("No candidates in Gemini response")
                
                candidate = result["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"]:
                    raise ValueError("No content in Gemini candidate")
                
                generated_text = candidate["content"]["parts"][0]["text"]
                
                # Extract JSON array from response
                topics = self._parse_json_topics(generated_text)
                
                # Log token usage from cache headers
                if "usageMetadata" in result:
                    usage = result["usageMetadata"]
                    logger.info(
                        f"Gemini tokens - Input: {usage.get('promptTokenCount', 0)}, "
                        f"Output: {usage.get('candidatesTokenCount', 0)}, "
                        f"Cached: {usage.get('cachedContentTokenCount', 0)}"
                    )
                
                logger.info(f"Successfully generated {len(topics)} topics for document {document_id}")
                return topics
        
        except Exception as e:
            logger.error(f"Error generating topics with Gemini: {e}")
            raise RuntimeError(f"Failed to generate topics: {e}")
    
    @staticmethod
    def _get_system_prompt(target_language: str = "en") -> str:
        """
        Get system prompt for topic generation.
        
        Args:
            target_language: Target language ("en" or "id")
            
        Returns:
            System prompt text
        """
        if target_language == "id":
            return """Anda adalah seorang Content Strategist B2B enterprise berpengalaman. 
            Tugas Anda adalah menganalisis ringkasan konteks yang diberikan dari dokumen produk 
            dan membuat tepat 3 topik konten yang unik dan menarik untuk LinkedIn.

            ATURAN KETAT:
            - Topik HARUS 100% berasal dari data faktual dalam konteks yang diberikan.
            - JANGAN hallusinasi fitur, statistik brand, atau berita eksternal industri.
            - Kembalikan HANYA array JSON dengan 3 string, tanpa markdown, tanpa prosa.
            - Format: ["Topik 1", "Topik 2", "Topik 3"]
            """
        else:
            return """You are an expert enterprise B2B Content Strategist. Your job is to analyze 
            the provided modular context summaries from a product document and create exactly 
            three (3) distinct, highly engaging content topics for LinkedIn.

            STRICT GROUND TRUTH CONSTRAINTS:
            - Topics MUST be 100% derived from the factual data provided in the context.
            - Do NOT hallucinate features, brand statistics, or industry external news.
            - Return ONLY a JSON array with exactly 3 topic strings, no markdown, no prose.
            - Format: ["Topic 1", "Topic 2", "Topic 3"]
            """
    
    @staticmethod
    def _parse_json_topics(response_text: str) -> List[str]:
        """
        Parse JSON array of topics from Gemini response.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            List of exactly 3 topics
            
        Raises:
            ValueError: If parsing fails or doesn't return 3 topics
        """
        try:
            # Try to extract JSON array from response
            response_text = response_text.strip()
            
            # Look for JSON array pattern
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]")
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError("No JSON array found in response")
            
            json_str = response_text[start_idx:end_idx + 1]
            topics = json.loads(json_str)
            
            # Validate format
            if not isinstance(topics, list):
                raise ValueError("Response is not a JSON array")
            
            if len(topics) != 3:
                logger.warning(f"Expected 3 topics, got {len(topics)}. Trimming/padding as needed.")
                topics = (topics[:3] if len(topics) > 3 else topics + [""] * (3 - len(topics)))
            
            # Validate each topic is a string
            topics = [str(t).strip() for t in topics if t]
            
            if len(topics) < 3:
                raise ValueError(f"Could not extract 3 valid topics, got {len(topics)}")
            
            return topics[:3]  # Return exactly 3
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Invalid JSON in response: {e}")
        except Exception as e:
            logger.error(f"Error parsing topics: {e}")
            raise ValueError(f"Failed to parse topics: {e}")
    
    async def generate_caption(
        self,
        topic: str,
        context_chunks: List[str],
        target_language: str = "en",
        target_audience: str = "B2B Enterprise Executives"
    ,
        extra_instruction: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate soft-selling caption using Gemini 1.5 Flash.
        
        Args:
            topic: Selected topic for caption
            context_chunks: Verified product chunks (usually top-3)
            target_language: Target language ("en" or "id")
            target_audience: Target audience persona
            
        Returns:
            Generated caption text, or None if failed
        """
        try:
            combined_context = "\n\n".join(context_chunks)
            
            system_prompt = self._get_caption_system_prompt(target_language)
            
            instruction_text = """Generate a LinkedIn caption (150-250 words) for the following:
                
Topic: {topic}
Target Audience: {target_audience}
Document Context: {combined_context}

Write in a native, casual yet authoritative tone. Follow the formula:
1. HOOK: Open with operational dilemma relatable to {target_audience}
2. DRAMA: Expand on frustration/risks if unsolved
3. SOLUTION: Introduce product as logical remedy with 2 concrete features
4. CTA: End with conversational question

Remember: NO banned words like "revolutionize", "comprehensive", "delve", etc.
""".format(topic=topic, target_audience=target_audience, combined_context=combined_context)

            if extra_instruction:
                instruction_text = f"{instruction_text}\n\nAdditional instruction: {extra_instruction}"

            request_body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": instruction_text
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 800,
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{self.model}:generateContent",
                    params={"key": self.api_key},
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "candidates" not in result or len(result["candidates"]) == 0:
                    raise ValueError("No candidates in response")
                
                caption = result["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Successfully generated caption for topic: {topic}")
                return caption
        
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise RuntimeError(f"Failed to generate caption: {e}")
    
    @staticmethod
    def _get_caption_system_prompt(target_language: str = "en") -> str:
        """Get system prompt for caption generation"""
        if target_language == "id":
            return """Anda adalah seorang copywriter B2B profesional tingkat dunia yang 
            berspesialisasi dalam copywriting pertumbuhan organik untuk LinkedIn. Gaya penulisan Anda 
            native, casual namun authoritative, dan terasa seperti praktisi industri nyata."""
        else:
            return """You are a world-class professional B2B Copywriter specializing in organic 
            growth copywriting for LinkedIn. Your writing style is native, casual yet authoritative, 
            and reads like a real human industry practitioner."""


# Initialize singleton
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
        logger.info("Gemini service initialized")
    return _gemini_service
