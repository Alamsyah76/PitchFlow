# Sprint 4 Readiness Report

Date: 2026-05-26

## Decision

READY

Sprint 4 can start without schema changes, provided it is treated as retrieval implementation work and not as a production deployment gate. The remaining live Supabase/PostgreSQL/RLS checks are production-certification blockers, not blockers for beginning top-20 retrieval, reranking, or Gemini context-injection implementation.

## Files Reviewed

- `PRODUCTION_HARDENING_REPORT.md`
- `SAFE_MIGRATION_REPORT.md`
- `PGVECTOR_VALIDATION_REPORT.md`
- `RLS_READINESS_REPORT.md`
- `backend/migrations/001_init_database.sql`
- `backend/migrations/002_align_architecture_stack.sql`
- `backend/services/vector_store_service.py`
- `backend/services/topic_extraction_service.py`
- `backend/services/embedding_service.py`
- `backend/app/routes_content.py`
- `backend/app/routes_topics.py`

## Verification

### 1. Is pgvector fully usable for retrieval?

Status: READY FOR SPRINT 4 DEVELOPMENT.

The schema declares `CREATE EXTENSION IF NOT EXISTS vector`, `embedding_vector vector(1536)`, and a cosine ivfflat index. The production query path uses pgvector's `<=>` cosine-distance operator through `VectorStoreService`.

Production caveat: a live Supabase/PostgreSQL insert-and-search test has not been run, so pgvector is not yet production-certified.

### 2. Is `vector_store` ready for top-k search?

Status: YES.

`VectorStoreService.vector_similarity_search()` accepts `top_k` as a parameter and applies it as `LIMIT :limit`. It also supports document-scoped search through `document_id`, which is required for ownership-safe retrieval.

Current application routes still use `top_k=3` in some places. Changing retrieval depth to top-20 is an implementation change, not a schema change.

### 3. Are embeddings stored correctly?

Status: YES AT SCHEMA AND SERVICE LEVEL.

Embeddings are stored in `vector_store.embedding_vector`, declared as `vector(1536)` in migrations and `VectorType(1536)` in the ORM. `VectorStoreService` validates embedding dimensions before save and search.

Production caveat: OpenAI `text-embedding-3-small` matches 1536 dimensions. Any alternate embedding provider must return 1536 dimensions or writes/searches will correctly fail.

### 4. Are retrieval indexes present?

Status: YES.

Migrations define:

- `idx_vector_store_embedding_vector` using `ivfflat (embedding_vector vector_cosine_ops)`
- `idx_vector_store_document_id`
- `idx_documents_user_id`

These support cosine vector ordering and document/user scoping.

Production caveat: index creation should still be verified on the target Supabase database, and ivfflat tuning may need adjustment after corpus size is known.

### 5. Can Sprint 4 start without schema changes?

Status: YES.

The required retrieval substrate exists:

- `documents`
- `vector_store`
- `contents`
- `embedding_vector vector(1536)`
- chunk content
- module chunk IDs
- JSONB metadata
- ownership foreign keys
- retrieval indexes

Top-20 retrieval, reranking, and Gemini context injection can be implemented against the current schema.

### 6. Hidden Blockers

#### Top-20 Retrieval

No schema blocker found.

Implementation work required:

- Change retrieval depth from current route defaults of 3 to 20 where specified by Sprint 4.
- Keep document ownership checks before retrieval.
- Ensure all retrieval code uses `VectorStoreService.vector_similarity_search()` rather than creating a second SQL path.

#### Reranking

No schema blocker found.

Implementation work required:

- Add reranking logic after top-20 vector retrieval.
- Preserve chunk IDs, similarity scores, and metadata through reranking.
- Decide whether rerank score is transient only or must be stored. Current schema supports transient reranking without changes.

#### Gemini Context Injection

No schema blocker found.

Implementation work required:

- Inject selected/reranked chunk content into Gemini prompts.
- Add token budgeting and truncation around top-20 context.
- Preserve citation/provenance metadata if Sprint 4 requires traceability.

## Remaining Non-Blocking Risks

- Live Supabase/PostgreSQL migration execution is still required before production deployment.
- Live pgvector insert/search validation is still required before production deployment.
- Live Supabase RLS and Storage policies are still unverified.
- Current SQLite fallback validates behavior locally but cannot prove pgvector query execution.
- Existing FastAPI and SQLAlchemy deprecation warnings remain technical debt but do not block Sprint 4.

## Final Recommendation

Start Sprint 4 with one constraint: retrieval implementation must use the existing authenticated, ownership-scoped route dependencies and the shared `VectorStoreService` pgvector query path. Do not add new retrieval storage tables unless Sprint 4 explicitly introduces persistent rerank audit requirements.
