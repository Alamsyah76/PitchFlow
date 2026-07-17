"""
Reranking service abstractions for Sprint 4 retrieval.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

import httpx

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class Reranker(ABC):
    """Interface for ranking retrieved chunks by relevance to a topic."""

    method_name: str

    @abstractmethod
    async def rerank(self, query: str, chunks: List[Dict], top_n: int = 3) -> List[Dict]:
        """Return the best `top_n` chunks with rerank scores."""
        raise NotImplementedError


class CohereReranker(Reranker):
    """Cohere Rerank API implementation."""

    method_name = "cohere"

    def __init__(self, api_key: str, model: str = "rerank-v3.5", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def rerank(self, query: str, chunks: List[Dict], top_n: int = 3) -> List[Dict]:
        if not chunks:
            return []

        documents = [chunk["content"] for chunk in chunks]
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.cohere.com/v2/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "query": query,
                    "documents": documents,
                    "top_n": top_n,
                },
            )
            response.raise_for_status()
            payload = response.json()

        ranked = []
        for result in payload.get("results", []):
            index = int(result["index"])
            chunk = dict(chunks[index])
            chunk["rerank_score"] = float(result.get("relevance_score", 0.0))
            ranked.append(chunk)

        logger.info(f"Cohere reranked {len(chunks)} chunks to {len(ranked)}")
        return ranked[:top_n]


class DeterministicTestReranker(Reranker):
    """Deterministic reranker for tests only."""

    method_name = "deterministic_test"

    async def rerank(self, query: str, chunks: List[Dict], top_n: int = 3) -> List[Dict]:
        ranked = sorted(
            chunks,
            key=lambda chunk: (
                float(chunk.get("similarity_score", 0.0)),
                str(chunk.get("chunk_id", "")),
            ),
            reverse=True,
        )

        output = []
        for index, chunk in enumerate(ranked[:top_n]):
            item = dict(chunk)
            item["rerank_score"] = float(item.get("similarity_score", 0.0))
            item["rerank_position"] = index + 1
            output.append(item)
        return output


def get_reranker() -> Reranker:
    """Create the configured production reranker."""
    if settings and settings.cohere_api_key:
        return CohereReranker(
            api_key=settings.cohere_api_key,
            model=settings.cohere_rerank_model,
        )

    raise RuntimeError("COHERE_API_KEY is required for production reranking")
