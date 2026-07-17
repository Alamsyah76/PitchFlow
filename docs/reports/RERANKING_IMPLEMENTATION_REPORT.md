# Reranking Implementation Report

Date: 2026-05-26

## Status

PASS.

Sprint 4 added a reranker abstraction and integrated it into the retrieval pipeline.

## Implementation

New file:

- `backend/services/reranker_service.py`

Implemented classes:

- `Reranker`: abstract interface.
- `CohereReranker`: production reranker using Cohere Rerank API when `COHERE_API_KEY` exists.
- `DeterministicTestReranker`: deterministic test-only reranker used by tests through monkeypatch injection.

Production factory:

- `get_reranker()` returns `CohereReranker` only when `COHERE_API_KEY` is configured.
- If no production reranker is configured, it raises `RuntimeError`.
- There is no fake production fallback.

Configuration added:

- `COHERE_API_KEY`
- `COHERE_RERANK_MODEL`

## Reranking Flow

1. Vector search retrieves top 20 chunks.
2. Reranker receives only those 20 candidates.
3. Reranker returns top 3 chunks.
4. Only the top 3 chunks are passed into the context payload builder.

## Test Coverage

`backend/tests/test_retrieval_pipeline.py` verifies:

- Top 20 vector retrieval.
- Top 3 reranking.
- Test-only deterministic reranker method name.
- Empty vector store behavior.
- Ownership-scoped retrieval.

## Production Notes

- Cohere requests are made server-side only.
- Tests do not call Cohere or any external network.
- If `COHERE_API_KEY` is missing in a real endpoint call, the endpoint returns `503` with `RERANKER_NOT_CONFIGURED`.
