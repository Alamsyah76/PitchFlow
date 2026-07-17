# Production Hardening Report

Date: 2026-05-26

## Overall Status

PASS for Sprint 3.5 pre-retrieval hardening. Production deployment still requires live Supabase/PostgreSQL/Storage validation before handling real users.

Sprint 4 was not started.

## Critical Blockers Resolved

- Sanitized `backend/.env.example` and added missing production variables.
- Created `ENVIRONMENT_SETUP.md`.
- Removed unsafe production database fallback derived from `SUPABASE_URL`.
- Added production fail-fast validation for required environment variables.
- Rewrote unsafe migration `002_align_architecture_stack.sql` to avoid destructive table drops.
- Validated pgvector schema requirements, 1536-dimension vectors, and cosine operator usage.
- Removed the remaining invalid `cosine_distance` helper path from backend services.
- Documented RLS readiness and remaining Supabase Storage policy risk.

## Files Changed

- `backend/.env.example`
- `backend/app/main.py`
- `backend/config/settings.py`
- `backend/models/database.py`
- `backend/services/vector_store_service.py`
- `backend/services/topic_extraction_service.py`
- `backend/migrations/002_align_architecture_stack.sql`
- `backend/tests/test_production_hardening.py`
- `ENVIRONMENT_SETUP.md`
- `SAFE_MIGRATION_REPORT.md`
- `PGVECTOR_VALIDATION_REPORT.md`
- `RLS_READINESS_REPORT.md`
- `PRODUCTION_HARDENING_REPORT.md`

No frontend files were modified.

## Environment Hardening

`backend/.env.example` now contains placeholders only and includes:

- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_JWT_AUDIENCE`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- vector, CORS, logging, and local embedding options

Production mode now requires `DATABASE_URL` and rejects non-PostgreSQL database URLs. SQLite fallback is limited to `USE_SQLITE_DEV=1`.

## Migration Hardening

`002_align_architecture_stack.sql` is now non-destructive. Incompatible legacy tables are renamed to backup tables, aligned tables are created with `CREATE TABLE IF NOT EXISTS`, and RLS policies are guarded against duplicate creation.

Current migration tests reject `DROP TABLE`, `DROP SCHEMA`, and `DROP DATABASE`.

## pgvector Validation

- Extension installation exists via `CREATE EXTENSION IF NOT EXISTS vector`.
- `embedding_vector` is declared as `vector(1536)`.
- Cosine index uses `vector_cosine_ops`.
- Similarity query uses `<=>` with `CAST(:query_vector AS vector)`.
- Runtime vector dimension validation rejects non-1536 embeddings.

## RLS Validation

Migrations enable RLS and define owner policies for `users`, `documents`, `vector_store`, and `contents`. Backend auth tests verify invalid token, expired token, anonymous access, document ownership, content ownership, and cross-user denial behavior.

Live Supabase RLS and Storage object-policy execution remain unverified.

## Tests Executed

Executed from `backend/`.

```powershell
venv_py311\Scripts\python.exe -m pytest -q
```

Result: `14 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m pytest tests\test_auth_security.py -q
```

Result: `7 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m pytest tests\test_startup_smoke.py -q
```

Result: `2 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m pytest tests\test_production_hardening.py -q
```

Result: `5 passed, 10 warnings`.

```powershell
venv_py311\Scripts\python.exe -m compileall app services models -q
```

Result: passed.

FastAPI startup smoke test with `USE_SQLITE_DEV=1`:

- `/health` returned HTTP 200.
- Response: `{"status":"healthy","service":"AI Marketing Content Engine Backend"}`.

## Remaining Blockers

- Live Supabase/PostgreSQL migration execution has not been run in this environment.
- Live RLS tests with real Supabase JWT claims are still required.
- Supabase Storage bucket and object policies for carousel assets are not defined or verified.
- Any credential that previously existed in `.env.example` must be rotated if valid.
- Legacy data backup tables require a controlled backfill plan if existing production data must remain active.
- SQLAlchemy and FastAPI deprecation warnings remain non-blocking technical debt.

## Safe To Continue Retrieval Sprint?

Yes for development, with constraints. Sprint 4 can proceed if it uses the existing auth dependencies, ownership checks, and `VectorStoreService` query path. It is not yet safe to deploy production retrieval for real users until the live Supabase migration, RLS, Storage, and pgvector integration checks pass.
