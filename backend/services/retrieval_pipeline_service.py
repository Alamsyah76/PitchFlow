"""
RAG retrieval, reranking, and context payload preparation.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import Document
from services.embedding_service import EmbeddingService
from services.reranker_service import Reranker, get_reranker
from services.vector_store_service import VectorStoreService
from utils.logger import get_logger

logger = get_logger(__name__)

TOP_K_RETRIEVAL = 20
TOP_N_CONTEXT = 3


class ContextPayloadBuilder:
    """Build the Gemini-ready context payload from reranked chunks."""

    @staticmethod
    def build(
        *,
        document: Document,
        topic: str,
        language: str,
        target_audience: str,
        chunks: List[Dict],
    ) -> Dict:
        top_chunks = []
        for rank, chunk in enumerate(chunks, start=1):
            top_chunks.append(
                {
                    "rank": rank,
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "module_chunk_id": chunk.get("module_chunk_id"),
                    "content": chunk["content"],
                    "similarity_score": float(chunk.get("similarity_score", 0.0)),
                    "rerank_score": float(chunk.get("rerank_score", 0.0)),
                    "metadata": chunk.get("metadata") or {},
                }
            )

        return {
            "selected_topic": topic,
            "language": language,
            "target_audience": target_audience,
            "document": {
                "id": str(document.id),
                "file_name": document.file_name,
                "total_pages": document.total_pages,
                "is_cached": bool(document.is_cached),
                "created_at": document.created_at.isoformat() if document.created_at else None,
            },
            "top_3_context_chunks": top_chunks,
        }


class RetrievalPipelineService:
    """Coordinates top-k vector retrieval, reranking, and context construction."""

    def __init__(self, reranker: Optional[Reranker] = None):
        self._reranker = reranker

    @property
    def reranker(self) -> Reranker:
        if self._reranker is None:
            self._reranker = get_reranker()
        return self._reranker

    async def retrieve_top_k(
        self,
        *,
        db: Session,
        document: Document,
        topic: str,
        top_k: int = TOP_K_RETRIEVAL,
    ) -> List[Dict]:
        query_vector = await EmbeddingService.embed_text(topic)
        results = VectorStoreService.vector_similarity_search(
            db=db,
            query_vector=query_vector,
            top_k=top_k,
            document_id=str(document.id),
        )
        logger.info(f"Retrieved {len(results)} chunks for document {document.id}")
        return results

    async def prepare_caption_context(
        self,
        *,
        db: Session,
        document: Document,
        topic: str,
        language: str,
        target_audience: str,
    ) -> Dict:
        retrieved = await self.retrieve_top_k(
            db=db,
            document=document,
            topic=topic,
            top_k=TOP_K_RETRIEVAL,
        )

        if not retrieved:
            raise ValueError("No chunks found for document")

        reranked = await self.reranker.rerank(
            query=topic,
            chunks=retrieved,
            top_n=TOP_N_CONTEXT,
        )

        payload = ContextPayloadBuilder.build(
            document=document,
            topic=topic,
            language=language,
            target_audience=target_audience,
            chunks=reranked[:TOP_N_CONTEXT],
        )

        return {
            "retrieval_count": len(retrieved),
            "rerank_method": self.reranker.method_name,
            "context_payload": payload,
        }
