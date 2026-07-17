import os
import sys
import asyncio
from pathlib import Path

import pytest

os.environ.setdefault("USE_SQLITE_DEV", "1")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config.settings import settings
from services.embedding_service import EmbeddingService, EmbeddingProvider


class ShortVectorProvider(EmbeddingProvider):
    async def embed_text(self, text: str):
        return [1.0, 2.0, 3.0]

    async def embed_batch(self, texts):
        return [[1.0, 2.0, 3.0] for _ in texts]


class FailingProvider(EmbeddingProvider):
    async def embed_text(self, text: str):
        raise RuntimeError("OpenAI retry failed")

    async def embed_batch(self, texts):
        raise RuntimeError("OpenAI retry failed")


@pytest.fixture(autouse=True)
def reset_embedding_service(monkeypatch):
    EmbeddingService._provider = None
    EmbeddingService._provider_name = None
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings.use_ollama = False
    settings.openai_api_key = "sk-test-valid-key"
    settings.vector_dimension = 1536
    yield
    EmbeddingService._provider = None
    EmbeddingService._provider_name = None


def test_placeholder_openai_key_initializes_ollama(monkeypatch):
    settings.openai_api_key = "replace-with-openai-api-key"
    monkeypatch.setattr(EmbeddingService, "_use_ollama_provider", classmethod(lambda cls: setattr(cls, "_provider_name", "ollama")))

    EmbeddingService.initialize()

    assert EmbeddingService._provider_name == "ollama"


def test_embedding_is_padded_to_required_1536_dimensions():
    EmbeddingService._provider = ShortVectorProvider()
    EmbeddingService._provider_name = "ollama"

    embedding = asyncio.run(EmbeddingService.embed_text("local embedding"))

    assert len(embedding) == 1536
    assert embedding[:3] == [1.0, 2.0, 3.0]
    assert embedding[-1] == 0.0


def test_openai_runtime_failure_retries_with_ollama(monkeypatch):
    EmbeddingService._provider = FailingProvider()
    EmbeddingService._provider_name = "openai"

    monkeypatch.setattr(
        EmbeddingService,
        "_use_ollama_provider",
        classmethod(lambda cls: (setattr(cls, "_provider", ShortVectorProvider()), setattr(cls, "_provider_name", "ollama"))),
    )

    embeddings = asyncio.run(EmbeddingService.embed_batch(["chunk"]))

    assert len(embeddings) == 1
    assert len(embeddings[0]) == 1536
    assert EmbeddingService._provider_name == "ollama"


def test_sqlite_dev_ollama_failure_uses_deterministic_local_embedding():
    EmbeddingService._provider = FailingProvider()
    EmbeddingService._provider_name = "ollama"

    embedding = asyncio.run(EmbeddingService.embed_text("offline local chunk"))

    assert len(embedding) == 1536
    assert EmbeddingService._provider_name == "local_deterministic"
