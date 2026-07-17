# Final Sprint 1-3 Audit

Date: 2026-05-26

Scope: Audit only. No Sprint 4 work was performed.

## Overall Status: PARTIAL

Sprint 1-3 are materially improved and the local backend test/startup path passes. They are not yet production-safe.

The main blockers are migration safety, production configuration hygiene, a likely broken production pgvector similarity query, and incomplete proof that protected endpoints work end-to-end against real Supabase/PostgreSQL/Storage.

## Sprint Status

| Sprint | Status | Rationale |
| --- | --- | --- |
| Sprint 1: Backend Bootability | PASS | FastAPI imports, starts under the smoke setup, registers expected routes, and `/health` returns 200. |
| Sprint 2: Database Alignment | PARTIAL | Fresh schema matches the required tables and columns, but the legacy migration is destructive, production DB connection fallback is unsafe, and production pgvector query behavior is not proven. |
| Sprint 3: Supabase Auth & Security | PARTIAL | JWT and ownership tests pass locally, protected endpoints reject anonymous/invalid/expired tokens, but production env/config issues and storage/RLS integration remain unverified. |

## Files Reviewed

- `PRD_Content_Engine.txt`
- `ARCHITECTURE_STACK.md`
- `PROMPT_TEMPLATES.md`
- `IMPLEMENTATION_AUDIT.md`
- `BACKEND_BOOTABILITY_REPORT.md`
- `DATABASE_ALIGNMENT_REPORT.md`
- `SCHEMA_COMPARISON_REPORT.md`
- `AUTH_IMPLEMENTATION_REPORT.md`
- `SECURITY_TEST_REPORT.md`
- `backend/app/main.py`
- `backend/app/auth.py`
- `backend/app/routes_content.py`
- `backend/app/routes_topics.py`
- `backend/config/settings.py`
- `backend/models/database.py`
- `backend/models/schemas.py`
- `backend/services/document_service.py`
- `backend/services/vector_store_service.py`
- `backend/services/topic_extraction_service.py`
- `backend/services/carousel_service.py`
- `backend/migrations/001_init_database.sql`
- `backend/migrations/002_align_architecture_stack.sql`
- `backend/tests/test_startup_smoke.py`
- `backend/tests/test_auth_security.py`
- `backend/.env.example`

## Tests Executed

Executed from `backend/`.

```powershell
venv_py311\Scripts\python.exe -m pytest -q
```

Result: `9 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m pytest tests\test_auth_security.py -q
```

Result: `7 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m pytest tests\test_startup_smoke.py -q
```

Result: `2 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m compileall app services models -q
```

Result: passed.

FastAPI startup smoke test:

```powershell
$env:USE_SQLITE_DEV='1'
venv_py311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8014
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8014/health
```

Result: HTTP 200 with `{"status":"healthy","service":"AI Marketing Content Engine Backend"}`.

## Backend Bootability Verification

Status: PASS for local smoke environment.

- FastAPI imports without import errors.
- Registered routes include:
  - `/health`
  - `/api/health`
  - `/api/v1/content/upload`
  - `/api/v1/content/topics`
  - `/api/v1/content/generate-caption`
  - `/api/v1/content/generate-carousel`
  - `/api/v1/content/search`
- `/health` returns HTTP 200.
- No missing route module remains.
- `scripts/tmp_upload_test.py` no longer performs network calls during pytest collection.

Production caveat: startup is still tolerant of SQLite fallback and `create_all()`, which is useful for local bootability but should not be treated as production migration control.

## Database Verification

Status: PARTIAL.

What passes:

- `users`, `documents`, `vector_store`, and `contents` exist in ORM with the expected logical columns.
- `backend/migrations/001_init_database.sql` defines the four required architecture tables.
- `vector_store.embedding_vector` is `vector(1536)` in the migration.
- ORM maps database column `metadata` as Python `metadata_json`, avoiding SQLAlchemy's reserved `metadata` attribute.
- FK relationships exist in migration:
  - `documents.user_id -> users.id`
  - `vector_store.document_id -> documents.id`
  - `contents.user_id -> users.id`
  - `contents.document_id -> documents.id`
  - `users.id -> auth.users`
- RLS is enabled in migration for the four required tables.

Issues:

- `002_align_architecture_stack.sql` is not non-destructive. It drops `public.contents`, `public.vector_store`, `public.documents`, and `public.users` after creating backup tables. That is a high-risk migration strategy for production.
- `002_align_architecture_stack.sql` assumes legacy tables already exist. It will fail on environments where one of those tables is missing.
- `ARCHITECTURE_STACK.md` says `CREATE EXTENSION IF NOT EXISTS pgvector;`, while the migration correctly uses the real PostgreSQL extension name `vector`. This is acceptable technically, but it is a spec wording mismatch worth documenting.
- ORM only adds `auth.users` FK when `DATABASE_URL` is explicitly PostgreSQL. If a deployment relies on `SUPABASE_URL` fallback instead of `DATABASE_URL`, ORM-created tables will not include the auth FK.
- `DatabaseConnection.initialize()` derives a PostgreSQL URL from `SUPABASE_URL` using a hard-coded placeholder password. Production must use `DATABASE_URL`; the fallback is not production-safe.
- Production vector search likely needs correction. `VectorStoreService.vector_similarity_search()` uses `func.cosine_distance(...)`; pgvector normally uses the `<=>` cosine-distance operator or a library-specific comparator. This was not proven against PostgreSQL.

## Security Verification

Status: PARTIAL.

What passes in tests:

- Missing token returns HTTP 401 with `AUTH_REQUIRED`.
- Invalid token returns HTTP 401 with `INVALID_TOKEN`.
- Expired token returns HTTP 401 with `TOKEN_EXPIRED`.
- Cross-user document access returns HTTP 403 with `DOCUMENT_FORBIDDEN`.
- Cross-user content/carousel access returns HTTP 403 with `CONTENT_FORBIDDEN`.
- Upload, topics, caption, search, and carousel routes are protected by `get_current_user`.
- Demo all-zero user ID is no longer present in backend app/service/model/test code.
- Carousel asset paths are user-scoped: `users/{user_id}/contents/{content_id}/slide_{idx}.png`.

Security gaps:

- `backend/.env.example` contains real-looking Supabase, OpenAI, and Gemini secrets. This is a critical repository hygiene issue. Rotate those credentials if they were ever valid.
- `backend/.env.example` does not include `SUPABASE_JWT_SECRET`, even though production auth now requires it.
- JWT validation is local HS256 validation only. That can be valid for Supabase if `SUPABASE_JWT_SECRET` is correct, but there is no integration test against a real Supabase project token.
- `ensure_user_profile()` auto-creates a `public.users` row for any valid JWT subject. That is acceptable for bootstrap only if the database connection is server-side trusted and JWT validation is strict, but it should be reviewed against the intended onboarding model.
- RLS policies are present in migrations, but tests do not run against Supabase/PostgreSQL with RLS enabled.
- Supabase Storage bucket policies for carousel images are not tested or defined.

## Endpoint Readiness

### `POST /api/v1/content/upload`

Status: PARTIAL.

- Protected by JWT.
- Stores uploaded document under authenticated user ID.
- Local validation tests cover protected-route entry but do not perform a successful PDF ingest.
- Still depends on external embedding provider and DB behavior for end-to-end success.

### `GET /api/v1/content/topics`

Status: PARTIAL.

- Protected by JWT.
- Checks document ownership before topic generation.
- Existing topic service still uses representative chunks, not the full PRD hierarchical summary flow.
- Requires Gemini API for successful topic generation.

### `POST /api/v1/content/generate-caption`

Status: PARTIAL.

- Protected by JWT.
- Checks document ownership before embedding/retrieval/generation.
- Still uses top-3 retrieval directly, not top-20 plus rerank.
- 95% validation score is stored but not enforced.
- External OpenAI/Gemini calls are required for end-to-end success.

### `GET /api/v1/content/generate-carousel`

Status: PARTIAL.

- Protected by JWT.
- Checks content ownership before generation.
- Filters content by owner inside carousel service.
- Uses user-scoped storage paths.
- Supabase Storage bucket/policy behavior is unverified.

### `/health`

Status: PASS.

- Returns HTTP 200 in startup smoke test.
- Does not require auth, which is appropriate for a simple health check.

## Risk Review

### Fake/mock logic

- Tests use local signed JWTs and in-memory SQLite. That is appropriate for unit/integration isolation, but not a substitute for Supabase integration testing.
- `USE_SQLITE_DEV` supplies placeholder secrets in development.
- SQLite fallback remains active and can hide PostgreSQL/pgvector/RLS issues.

### Hardcoded demo user

- No hardcoded all-zero demo user remains in backend app/service/model/test code reviewed.

### Missing Supabase config / env variables

- `SUPABASE_JWT_SECRET` is required but missing from `.env.example`.
- `DATABASE_URL` is required for production-safe Postgres connection behavior.
- `SUPABASE_URL` to Postgres URL derivation is unsafe and should be removed or replaced.

### Security gaps

- Secrets appear to be committed in `.env.example`; rotate them and replace with placeholders.
- Storage authorization is not defined/tested.
- RLS has not been tested against real Supabase.
- Auth tests do not cover algorithm-confusion cases or service-role bypass scenarios.

### Broken imports

- None found in current backend import and compile checks.

### Unused or risky routes

- `/api/v1/content/search` is registered and protected, but not part of the user’s listed endpoint audit. It should remain covered by ownership tests before Sprint 4 retrieval work expands it.

### Schema mismatch

- Fresh migration and ORM mostly match `ARCHITECTURE_STACK.md`.
- Legacy migration strategy is not production-safe.
- ORM/auth FK behavior depends on `DATABASE_URL`, not just Supabase config.

### Hidden blockers before Sprint 4

- Production pgvector similarity query likely needs a real Postgres test and possibly operator-level implementation.
- End-to-end protected upload cannot be considered production-ready until run against real Postgres + Supabase Auth + embedding provider.
- `DocumentService` no longer persists document hash, so the PRD token-saving "do not re-embed same document" behavior is not implemented after schema alignment.
- `backend/models/schemas.py` still includes `chunk_index` in `ChunkMetadata`; not a boot blocker, but it is stale relative to the aligned DB schema.

## Safe To Continue Sprint 4?

Not directly.

It is safe to continue development work in the codebase, but not safe to start Sprint 4 retrieval/reranking as if Sprint 1-3 were production-complete. The next sprint should first harden the production DB/auth foundation.

## Exact Next Sprint Recommendation

Run a short hardening sprint before retrieval work:

1. Remove committed secrets from `.env.example`, replace with placeholders, and rotate any exposed credentials.
2. Add `SUPABASE_JWT_SECRET` and `SUPABASE_JWT_AUDIENCE` to `.env.example`.
3. Replace `SUPABASE_URL`-derived Postgres connection logic with an explicit required `DATABASE_URL` for production.
4. Replace destructive `002_align_architecture_stack.sql` with a safer additive/rename migration or require explicit manual backup/restore steps.
5. Add a real PostgreSQL/Supabase integration test for migrations, RLS, JWT-authenticated access, and pgvector similarity search.
6. Fix pgvector similarity search to use a verified pgvector operator/comparator.
7. Reintroduce document deduplication/caching in a schema-compatible way before implementing top-20 retrieval and reranking.
