"""
Python Package Initializer for services module
"""

from services.document_service import DocumentService
from services.embedding_service import EmbeddingService, EmbeddingProvider, OpenAIEmbeddingProvider, OllamaEmbeddingProvider
from services.vector_store_service import VectorStoreService
from services.gemini_service import GeminiService, get_gemini_service
from services.topic_extraction_service import TopicExtractionService

__all__ = [
    "DocumentService",
    "EmbeddingService",
    "EmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "VectorStoreService"
]
__all__ += [
    "GeminiService",
    "get_gemini_service",
    "TopicExtractionService",
]
