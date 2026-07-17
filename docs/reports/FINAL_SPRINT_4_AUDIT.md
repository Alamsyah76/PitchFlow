# Final Sprint 4 Audit

Date: 2026-05-27

## Overall Status

PASS.

Sprint 4 is complete for backend retrieval preparation. It implements top-20 vector retrieval, reranking to top 3, authenticated ownership scoping, and a context-only `generate-caption` response. Sprint 5 was not started.

Production caveat: Cohere reranking and PostgreSQL pgvector execution are not live-tested in this local audit. They are implementation-complete but still require staging validation with real `COHERE_API_KEY` and Supabase/PostgreSQL.

## Files Reviewed

- `SPRINT_4_RETRIEVAL_REPORT.md`
- `RERANKING_IMPLEMENTATION_REPORT.md`
- `CONTEXT_PAYLOAD_REPORT.md`
- `ARCHITECTURE_STACK.md`
- `PRD_Content_Engine.txt`
- `backend/app/routes_content.py`
- `backend/services/retrieval_pipeline_service.py`
- `backend/services/reranker_service.py`
- `backend/services/vector_store_service.py`
- `backend/tests/test_retrieval_pipeline.py`

## Verification Results

### 1. Top-20 vector retrieval works

PASS.

`RetrievalPipelineService` sets `TOP_K_RETRIEVAL = 20` and calls `VectorStoreService.vector_similarity_search(..., top_k=20, document_id=str(document.id))`.

`test_generate_caption_retrieves_top_20_chunks` seeds 25 chunks and verifies `retrieval_count == 20`.

### 2. Top-3 reranking works

PASS.

`RetrievalPipelineService` sets `TOP_N_CONTEXT = 3`, calls the reranker with `top_n=3`, and passes only `reranked[:TOP_N_CONTEXT]` into `ContextPayloadBuilder`.

`test_generate_caption_reranks_to_top_3_chunks` verifies exactly 3 returned chunks.

### 3. User ownership is enforced

PASS.

`POST /api/v1/content/generate-caption` requires `get_current_user`, calls `ensure_user_profile`, and resolves the document through `get_owned_document` before retrieval starts.

### 4. No cross-user chunks are returned

PASS.

Retrieval is filtered by owned `document_id`. Since `vector_store` rows belong to documents, ownership is enforced through the document check before vector search.

`test_generate_caption_retrieval_is_document_owner_scoped` seeds two users and two documents, then verifies returned chunks all belong to the owner document.

### 5. No full document is sent to Gemini

PASS.

The Sprint 4 `generate-caption` endpoint does not call Gemini. It returns only a prepared context payload. The payload builder receives only the top 3 reranked chunks.

### 6. `generate-caption` returns only context payload

PASS.

The endpoint returns:

- `selected_topic`
- `top_3_context_chunks`
- `retrieval_count`
- `rerank_method`
- `ready_for_caption_generation`
- `context_payload`

It does not return `final_caption`, does not persist a `contents` row, and does not run the auditor.

### 7. `COHERE_API_KEY` behavior is correct

PASS with staging caveat.

`get_reranker()` returns `CohereReranker` only when `settings.cohere_api_key` exists. Without `COHERE_API_KEY`, it raises `RuntimeError`, which the endpoint maps to `503 RERANKER_NOT_CONFIGURED`.

This avoids fake production reranking. Live Cohere API behavior still needs staging validation.

### 8. Deterministic reranker is only used in tests

PASS.

`DeterministicTestReranker` is defined in `backend/services/reranker_service.py`, but production factory `get_reranker()` never selects it. It is injected only by `backend/tests/test_retrieval_pipeline.py` through monkeypatching.

### 9. All tests pass

PASS.

Executed from `backend/`:

```powershell
venv_py311\Scripts\python.exe -m pytest -q
```

Result: `21 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m pytest tests\test_retrieval_pipeline.py -q
```

Result: `7 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m compileall app services models -q
```

Result: passed.

## Security Review

Protected retrieval requires a valid bearer token. Anonymous requests are rejected by existing auth middleware. Cross-user document access is rejected before vector search. The vector query is document-scoped, preventing mixed-user chunk retrieval through the Sprint 4 endpoint.

## Remaining Risks

- Cohere API integration is not live-tested in this environment.
- PostgreSQL pgvector query execution is not live-tested against Supabase in this audit.
- Existing non-Sprint-4 Gemini services still exist for topic generation and older service methods, but the audited `generate-caption` endpoint does not invoke Gemini.
- Deprecation warnings remain for Pydantic/FastAPI/SQLAlchemy/PyPDF2 and are not Sprint 4 blockers.

## Final Recommendation

Sprint 4 can be accepted. The next sprint may implement Gemini caption generation only if it preserves this retrieval boundary: retrieve top 20, rerank to top 3, and send only the top 3 context chunks to Gemini.
