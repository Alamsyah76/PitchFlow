"""
Embedding Service Module
Handles text embedding using OpenAI or local Ollama models
"""

import asyncio
import hashlib
import os
import httpx
from typing import List, Optional
from abc import ABC, abstractmethod
from tenacity import RetryError
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed single text string"""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed batch of text strings"""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small model"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: text-embedding-3-small)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.timeout = 30
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed_text(self, text: str) -> List[float]:
        """
        Embed single text using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions)
            
        Raises:
            RuntimeError: If embedding fails after retries
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": text,
                        "encoding_format": "float"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                if "data" not in result or len(result["data"]) == 0:
                    raise ValueError("No embedding data in response")
                
                embedding = result["data"][0]["embedding"]
                logger.debug(f"Successfully embedded text with {len(embedding)} dimensions")
                return embedding
        
        except Exception as e:
            logger.error(f"Error embedding text with OpenAI: {e}")
            raise RuntimeError(f"Failed to embed text: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed_batch(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        """
        Embed batch of texts using OpenAI API.
        OpenAI supports up to 100 texts per request.
        
        Args:
            texts: List of texts to embed
            batch_size: Size of batch per API call (max 100)
            
        Returns:
            List of embedding vectors
            
        Raises:
            RuntimeError: If embedding fails
        """
        try:
            embeddings = []
            batch_size = min(batch_size, 100)  # OpenAI max batch size
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                logger.info(f"Embedding batch {i//batch_size + 1} of {(len(texts)-1)//batch_size + 1}")
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/embeddings",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.model,
                            "input": batch,
                            "encoding_format": "float"
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Sort by index to maintain order
                    sorted_data = sorted(result["data"], key=lambda x: x["index"])
                    batch_embeddings = [item["embedding"] for item in sorted_data]
                    embeddings.extend(batch_embeddings)
                
                # Add small delay between batches to avoid rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.5)
            
            logger.info(f"Successfully embedded {len(embeddings)} texts")
            return embeddings
        
        except Exception as e:
            logger.error(f"Error embedding batch with OpenAI: {e}")
            raise RuntimeError(f"Failed to embed batch: {e}")


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Local Ollama embedding provider for nomic-embed-text model"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        """
        Initialize Ollama embedding provider.
        
        Args:
            base_url: Ollama server base URL
            model: Model name (default: nomic-embed-text)
        """
        self.base_url = base_url
        self.model = model
        self.timeout = 60  # Ollama can be slow on first run
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Embed single text using Ollama API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            RuntimeError: If embedding fails
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                if "embedding" not in result:
                    raise ValueError("No embedding in Ollama response")
                
                embedding = result["embedding"]
                logger.debug(f"Successfully embedded text with {len(embedding)} dimensions")
                return embedding
        
        except Exception as e:
            logger.error(f"Error embedding text with Ollama: {e}")
            raise RuntimeError(f"Failed to embed text with Ollama: {e}")
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed batch of texts using Ollama API.
        Ollama processes one at a time, but this method handles multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            RuntimeError: If embedding fails
        """
        try:
            embeddings = []
            total = len(texts)
            
            for idx, text in enumerate(texts):
                logger.info(f"Embedding text {idx+1}/{total}")
                embedding = await self.embed_text(text)
                embeddings.append(embedding)
                
                # Add delay between requests to Ollama
                if idx + 1 < total:
                    await asyncio.sleep(0.1)
            
            logger.info(f"Successfully embedded {len(embeddings)} texts")
            return embeddings
        
        except Exception as e:
            logger.error(f"Error embedding batch with Ollama: {e}")
            raise RuntimeError(f"Failed to embed batch with Ollama: {e}")


class LocalDeterministicEmbeddingProvider(EmbeddingProvider):
    """Development-only deterministic embedding fallback for offline SQLite runs."""

    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    def _embed(self, text: str) -> List[float]:
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for index in range(self.dimensions):
            byte = seed[index % len(seed)]
            values.append((byte / 127.5) - 1.0)
        return values

    async def embed_text(self, text: str) -> List[float]:
        return self._embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]


class EmbeddingService:
    """High-level embedding service that delegates to configured provider"""
    
    _provider: Optional[EmbeddingProvider] = None
    _provider_name: Optional[str] = None

    @classmethod
    def _expected_dimension(cls) -> int:
        return settings.vector_dimension if settings else 1536

    @staticmethod
    def _is_openai_key_usable(api_key: Optional[str]) -> bool:
        if not api_key:
            return False

        normalized = api_key.strip()
        lowered = normalized.lower()
        invalid_markers = ("placeholder", "replace", "dummy", "test", "dev-", "example")
        if any(marker in lowered for marker in invalid_markers):
            return False

        return normalized.startswith("sk-")

    @classmethod
    def _normalize_embedding(cls, embedding: List[float]) -> List[float]:
        expected = cls._expected_dimension()
        vector = [float(item) for item in embedding]

        if len(vector) == expected:
            return vector

        if len(vector) > expected:
            logger.warning(f"Truncating embedding from {len(vector)} to {expected} dimensions")
            return vector[:expected]

        logger.warning(f"Padding embedding from {len(vector)} to {expected} dimensions")
        return vector + [0.0] * (expected - len(vector))

    @classmethod
    def _normalize_batch(cls, embeddings: List[List[float]]) -> List[List[float]]:
        return [cls._normalize_embedding(embedding) for embedding in embeddings]

    @classmethod
    def _use_ollama_provider(cls):
        cls._provider = OllamaEmbeddingProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embed_model,
        )
        cls._provider_name = "ollama"
        logger.info(f"Using Ollama embedding provider: {settings.ollama_embed_model}")

    @classmethod
    def _use_dev_local_provider(cls):
        cls._provider = LocalDeterministicEmbeddingProvider(cls._expected_dimension())
        cls._provider_name = "local_deterministic"
        logger.warning("Using development-only deterministic local embedding fallback")

    @staticmethod
    def _sqlite_dev_enabled() -> bool:
        return os.getenv("USE_SQLITE_DEV", "").lower() in ("1", "true", "yes")
    
    @classmethod
    def initialize(cls):
        """Initialize embedding service with configured provider"""
        try:
            configured_openai_key = os.getenv("OPENAI_API_KEY") or settings.openai_api_key
            if settings.use_ollama or not cls._is_openai_key_usable(configured_openai_key):
                if not settings.use_ollama:
                    logger.warning("OpenAI API key is missing or invalid; falling back to Ollama embeddings")
                cls._use_ollama_provider()
            else:
                cls._provider = OpenAIEmbeddingProvider(
                    api_key=settings.openai_api_key,
                    model=settings.vector_embedding_model
                )
                cls._provider_name = "openai"
                logger.info(f"Using OpenAI embedding provider: {settings.vector_embedding_model}")
        
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise

    @classmethod
    async def _retry_with_ollama(cls, operation: str, payload):
        logger.warning(f"OpenAI embedding {operation} failed; retrying with Ollama fallback")
        cls._use_ollama_provider()
        try:
            if operation == "text":
                return await cls._provider.embed_text(payload)
            return await cls._provider.embed_batch(payload)
        except RuntimeError as exc:
            if not cls._sqlite_dev_enabled():
                raise
            logger.warning(f"Ollama embedding failed in USE_SQLITE_DEV mode; using deterministic local fallback: {exc}")
            cls._use_dev_local_provider()
            if operation == "text":
                return await cls._provider.embed_text(payload)
            return await cls._provider.embed_batch(payload)
    
    @classmethod
    async def embed_text(cls, text: str) -> List[float]:
        """
        Embed single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if cls._provider is None:
            cls.initialize()
        
        try:
            embedding = await cls._provider.embed_text(text)
        except (RetryError, RuntimeError) as exc:
            if cls._provider_name == "openai":
                embedding = await cls._retry_with_ollama("text", text)
            elif cls._provider_name == "ollama" and cls._sqlite_dev_enabled():
                logger.warning(f"Ollama embedding failed in USE_SQLITE_DEV mode; using deterministic local fallback: {exc}")
                cls._use_dev_local_provider()
                embedding = await cls._provider.embed_text(text)
            else:
                raise RuntimeError(f"Failed to embed text with {cls._provider_name}: {exc}") from exc

        return cls._normalize_embedding(embedding)
    
    @classmethod
    async def embed_batch(cls, texts: List[str]) -> List[List[float]]:
        """
        Embed batch of text strings.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if cls._provider is None:
            cls.initialize()
        
        try:
            embeddings = await cls._provider.embed_batch(texts)
        except (RetryError, RuntimeError) as exc:
            if cls._provider_name == "openai":
                embeddings = await cls._retry_with_ollama("batch", texts)
            elif cls._provider_name == "ollama" and cls._sqlite_dev_enabled():
                logger.warning(f"Ollama embedding failed in USE_SQLITE_DEV mode; using deterministic local fallback: {exc}")
                cls._use_dev_local_provider()
                embeddings = await cls._provider.embed_batch(texts)
            else:
                raise RuntimeError(f"Failed to embed batch with {cls._provider_name}: {exc}") from exc

        return cls._normalize_batch(embeddings)
