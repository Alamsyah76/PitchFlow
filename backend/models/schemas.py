"""
Pydantic Schema Models
Defines request/response data structures for FastAPI endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class FileUploadResponse(BaseModel):
    """Response schema for POST /api/v1/content/upload"""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    document_id: Optional[str] = Field(None, description="UUID of uploaded document")
    file_name: Optional[str] = Field(None, description="Uploaded PDF file name")
    total_pages: Optional[int] = Field(None, description="Number of pages in uploaded PDF")
    is_cached: bool = Field(default=False, description="Whether document was already cached")
    total_modules: Optional[int] = Field(None, description="Number of modules created")
    total_chunks: Optional[int] = Field(None, description="Total semantic chunks created")
    embedding_dimension: Optional[int] = Field(None, description="Vector embedding dimension")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Document uploaded and processed successfully",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "file_name": "whitepaper.pdf",
                "total_pages": 12,
                "is_cached": False,
                "total_modules": 3,
                "total_chunks": 42,
                "embedding_dimension": 1536,
                "processing_time_seconds": 12.5,
                "error": None
            }
        }


class CachedDocumentResponse(BaseModel):
    """Response when document is already cached"""
    
    success: bool = True
    message: str = "Document already cached"
    document_id: str = Field(..., description="UUID of existing document")
    is_cached: bool = True
    total_chunks: int = Field(..., description="Number of existing chunks")
    created_at: datetime = Field(..., description="Timestamp of original upload")


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    
    success: bool = False
    error_code: str = Field(..., description="Error code for debugging")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "INVALID_PDF",
                "error_message": "Uploaded file is not a valid PDF",
                "details": "PDF header signature not found"
            }
        }


class EmbeddingInfo(BaseModel):
    """Information about an embedding"""
    
    dimension: int = Field(..., description="Embedding vector dimension")
    model: str = Field(..., description="Embedding model used")
    total_tokens: Optional[int] = Field(None, description="Total tokens used for embedding")


class ChunkMetadata(BaseModel):
    """Metadata for a text chunk"""
    
    document_id: str = Field(..., description="Parent document UUID")
    module_id: int = Field(..., description="Module sequence number")
    page_start: int = Field(..., description="Starting page number")
    page_end: int = Field(..., description="Ending page number")
    chunk_index: int = Field(..., description="Chunk sequence within module")
    token_count: int = Field(..., description="Token count of chunk")


# ===== SESSION 3: TOPIC EXTRACTION SCHEMAS =====

class TopicExtractionResponse(BaseModel):
    """Response schema for GET /api/v1/content/topics"""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    document_id: str = Field(..., description="Document UUID")
    topics: List[str] = Field(..., description="Exactly 3 topic strings")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Topics extracted successfully",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "topics": [
                    "How SendQuick Reduces Data Migration Time by 60%",
                    "Enterprise Data Security: The SendQuick Compliance Framework",
                    "Real-time Analytics: Building Scalable Data Pipelines"
                ],
                "processing_time_seconds": 8.5
            }
        }


class TopicQuery(BaseModel):
    """Query schema for topic extraction endpoint"""
    
    document_id: str = Field(..., description="Document UUID to extract topics from")
    lang: str = Field(default="en", description="Target language: 'en' or 'id'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "lang": "en"
            }
        }


class CaptionGenerationRequest(BaseModel):
    """Request schema for POST /api/v1/content/generate-caption"""
    
    document_id: str = Field(..., description="Document UUID")
    topic: str = Field(..., description="Selected topic for caption generation")
    language: str = Field(default="en", description="Target language: 'en' or 'id'")
    target_audience: str = Field(
        default="B2B Enterprise Executives",
        description="Target audience persona"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "topic": "How SendQuick Reduces Data Migration Time by 60%",
                "language": "en",
                "target_audience": "Data Engineering Leaders"
            }
        }


class CaptionGenerationResponse(BaseModel):
    """Response schema for caption generation"""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    document_id: str = Field(..., description="Document UUID")
    topic: str = Field(..., description="Topic used for generation")
    caption: str = Field(..., description="Generated caption text")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Caption generated successfully",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "topic": "How SendQuick Reduces Data Migration Time by 60%",
                "caption": "Moving petabytes of enterprise data is like... nobody's idea of fun. 📊 Three days. Four teams. Zero sleep. That was our data migration reality until SendQuick changed the game.\n\nThe problem? Traditional ETL pipelines bleed time. Every hour of downtime costs money. Every day of migration risks data integrity.\n\nSendQuick's parallel processing engine does in 6 hours what takes competitors three days. Real-time validation. Zero data loss. Built on 15 years of enterprise infrastructure battle scars.\n\nHave you found the magic bullet for zero-downtime migrations, or are you still in the two-day standoff?",
                "processing_time_seconds": 12.3
            }
        }


class SemanticSearchRequest(BaseModel):
    """Request schema for semantic search"""
    
    document_id: str = Field(..., description="Document UUID to search within")
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=3, description="Number of top results (max 10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "data migration capabilities",
                "top_k": 3
            }
        }


class SemanticSearchResult(BaseModel):
    """Single search result"""
    
    chunk_id: str = Field(..., description="Chunk UUID")
    content: str = Field(..., description="Chunk text content")
    similarity_score: float = Field(..., description="Similarity score 0-1")
    module_id: int = Field(..., description="Module identifier")
    metadata: dict = Field(..., description="Additional metadata")


class SemanticSearchResponse(BaseModel):
    """Response schema for semantic search"""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    document_id: str = Field(..., description="Document UUID")
    query: str = Field(..., description="Original query")
    results: List[SemanticSearchResult] = Field(..., description="Search results")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time")
