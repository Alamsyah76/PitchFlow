"""
Topic Extraction Service Module
Handles topic generation from documents using semantic retrieval and Gemini API
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import uuid

from models.database import Document, VectorStore
from services.embedding_service import EmbeddingService
from services.gemini_service import GeminiService
from services.vector_store_service import VectorStoreService
from utils.logger import get_logger

logger = get_logger(__name__)


class TopicExtractionService:
    """Service for extracting topics from documents using semantic retrieval"""
    
    @staticmethod
    async def extract_topics(
        db: Session,
        document_id: str,
        target_language: str = "en"
    ) -> Optional[List[str]]:
        """
        Extract 3 topics from a document using semantic retrieval + Gemini.
        
        Process:
        1. Validate document exists
        2. Retrieve relevant chunks using semantic similarity (no Cohere)
        3. Generate topics using Gemini 1.5 Flash with Context Caching
        
        Args:
            db: Database session
            document_id: Document UUID
            target_language: Target language ("en" or "id")
            
        Returns:
            List of exactly 3 topics, or None if failed
        """
        try:
            # Step 1: Validate document exists
            doc_id = str(uuid.UUID(document_id))
            document = db.query(Document).filter(Document.id == doc_id).first()
            
            if not document:
                logger.error(f"Document not found: {document_id}")
                raise ValueError(f"Document {document_id} not found")
            
            logger.info(f"Extracting topics for document: {document.file_name}")
            
            # Step 2: Retrieve all chunks for hierarchical summarization
            logger.info(f"Retrieving chunks for document {document_id}")
            chunks = db.query(
                VectorStore.id,
                VectorStore.document_id,
                VectorStore.module_chunk_id,
                VectorStore.chunk_content,
            ).filter(
                VectorStore.document_id == doc_id
            ).order_by(VectorStore.module_chunk_id, VectorStore.id).all()
            
            if not chunks:
                logger.error(f"No chunks found for document {document_id}")
                raise ValueError(f"No chunks found for document {document_id}")
            
            logger.info(f"Retrieved {len(chunks)} total chunks")
            
            # Step 3: Select representative chunks for topic generation
            # Strategy: Take 1-2 chunks from each module to get document overview
            selected_chunks = TopicExtractionService._select_representative_chunks(chunks)
            
            logger.info(f"Selected {len(selected_chunks)} representative chunks")
            
            # Step 4: Generate topics using Gemini with caching
            gemini_service = GeminiService()
            
            topics = await gemini_service.generate_topics(
                context_chunks=selected_chunks,
                document_id=document_id,
                target_language=target_language,
                use_cache=True
            )
            
            if not topics or len(topics) != 3:
                logger.error(f"Invalid topics response: {topics}")
                raise ValueError("Failed to generate exactly 3 topics")
            
            logger.info(f"Successfully extracted 3 topics for document {document_id}")
            return topics
        
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            raise
    
    @staticmethod
    def _select_representative_chunks(chunks: List[VectorStore], max_chunks: int = 6) -> List[str]:
        """
        Select representative chunks from different modules.
        
        Strategy: Pick 1-2 chunks from each module to get comprehensive overview
        without overwhelming Gemini with too much context.
        
        Args:
            chunks: All chunks from document
            max_chunks: Maximum chunks to select (default: 6)
            
        Returns:
            List of chunk content strings
        """
        try:
            # Group chunks by module
            modules: Dict[int, List[VectorStore]] = {}
            for chunk in chunks:
                module_id = chunk.module_chunk_id
                if module_id not in modules:
                    modules[module_id] = []
                modules[module_id].append(chunk)
            
            # Select chunks from each module
            selected = []
            chunks_per_module = max_chunks // len(modules) if modules else 1
            chunks_per_module = max(1, min(chunks_per_module, 2))  # 1-2 chunks per module
            
            for module_id in sorted(modules.keys()):
                module_chunks = modules[module_id]
                
                # Take first and middle chunk from each module for diversity
                if len(module_chunks) >= 2:
                    selected.append(module_chunks[0].chunk_content)
                    selected.append(module_chunks[len(module_chunks) // 2].chunk_content)
                else:
                    selected.append(module_chunks[0].chunk_content)
                
                if len(selected) >= max_chunks:
                    break
            
            logger.debug(f"Selected {len(selected)} chunks from {len(modules)} modules")
            return selected[:max_chunks]
        
        except Exception as e:
            logger.error(f"Error selecting representative chunks: {e}")
            # Fallback: return first chunks
            return [c.chunk_content for c in chunks[:max_chunks]]
    
    @staticmethod
    async def semantic_search_chunks(
        db: Session,
        query_text: str,
        document_id: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Perform semantic search on document chunks using pgvector.
        NO COHERE - Uses only LlamaIndex-style cosine similarity.
        
        Args:
            db: Database session
            query_text: Query text to search for
            document_id: Document UUID to search within
            top_k: Number of top results (default: 3)
            
        Returns:
            List of dicts with chunk content, similarity score, and metadata
        """
        try:
            # Step 1: Generate embedding for query
            logger.info(f"Generating embedding for search query")
            query_embedding = await EmbeddingService.embed_text(query_text)
            
            # Step 2: Perform cosine similarity search in pgvector
            results = VectorStoreService.vector_similarity_search(
                db=db,
                query_vector=query_embedding,
                top_k=top_k,
                document_id=document_id,
            )
            
            logger.info(f"Found {len(results)} similar chunks")
            return results
        
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            raise
    
    @staticmethod
    def _vector_search(
        db: Session,
        query_vector: List[float],
        document_id: uuid.UUID,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Vector similarity search using pgvector cosine distance.
        
        Args:
            db: Database session
            query_vector: Query embedding vector (1536-dim)
            document_id: Document UUID filter
            top_k: Number of top results
            
        Returns:
            List of search results
        """
        try:
            results = VectorStoreService.vector_similarity_search(
                db=db,
                query_vector=query_vector,
                top_k=top_k,
                document_id=str(document_id),
            )

            output = []
            for result in results:
                output.append({
                    "chunk_id": result["chunk_id"],
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "module_id": result.get("module_chunk_id"),
                    "similarity_score": result["similarity_score"],
                })
            
            logger.debug(f"Vector search returned {len(output)} results")
            return output
        
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            raise
    
    @staticmethod
    async def generate_caption_for_topic(
        db: Session,
        document_id: str,
        topic: str,
        target_language: str = "en",
        target_audience: str = "B2B Enterprise Executives"
    ) -> Optional[str]:
        """
        Generate a soft-selling LinkedIn caption for a specific topic.
        
        Args:
            db: Database session
            document_id: Document UUID
            topic: Selected topic
            target_language: Target language
            target_audience: Target audience persona
            
        Returns:
            Generated caption text
        """
        try:
            # Semantic search for relevant chunks
            logger.info(f"Searching for chunks relevant to topic: {topic}")
            search_results = await TopicExtractionService.semantic_search_chunks(
                db=db,
                query_text=topic,
                document_id=document_id,
                top_k=3
            )
            
            if not search_results:
                logger.error(f"No relevant chunks found for topic: {topic}")
                raise ValueError(f"No relevant chunks found for topic")
            
            context_chunks = [r["content"] for r in search_results]
            
            # Generate caption
            gemini_service = GeminiService()
            caption = await gemini_service.generate_caption(
                topic=topic,
                context_chunks=context_chunks,
                target_language=target_language,
                target_audience=target_audience
            )
            
            logger.info(f"Successfully generated caption for topic: {topic}")
            return caption
        
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise
