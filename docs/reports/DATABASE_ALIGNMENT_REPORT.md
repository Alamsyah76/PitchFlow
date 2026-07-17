# Database Alignment Report

Date: 2026-05-26

Scope: Sprint 2 only. This sprint aligned database architecture with `ARCHITECTURE_STACK.md`: required tables, pgvector support, migrations, and ORM models.

## Result

Database architecture is aligned to the required four-table Supabase/PostgreSQL model:

- `public.users`
- `public.documents`
- `public.vector_store`
- `public.contents`

The old CMS-style migration has been replaced for fresh installs, and a legacy alignment migration has been added for existing databases.

## Migration Files

- `backend/migrations/001_init_database.sql`
  - Fresh schema aligned to `ARCHITECTURE_STACK.md`.
  - Enables pgvector support with `CREATE EXTENSION IF NOT EXISTS vector`.
  - Creates the required four tables.
  - Adds pgvector IVFFlat index for `vector_store.embedding_vector`.
  - Enables RLS and owner-scoped policies for required tables.

- `backend/migrations/002_align_architecture_stack.sql`
  - Backs up existing legacy tables into `legacy_*_backup` tables.
  - Recreates the four required architecture tables.
  - Preserves compatible legacy rows where they can be mapped safely.
  - Recreates indexes and RLS policies.

## ORM Changes

- `backend/models/database.py`
  - Replaced legacy ORM fields with the exact architecture entities.
  - Added `GUID` type for PostgreSQL UUID with SQLite fallback.
  - Added `VectorType`/`PGVector` support for `vector(1536)` with SQLite fallback.
  - Added PostgreSQL `TEXT[]` support for `carousel_images_urls` with SQLite fallback.
  - Mapped database column `metadata` to Python attribute `metadata_json` to avoid SQLAlchemy's reserved `metadata` name.

## Service Compatibility Updates

- `backend/services/document_service.py`
  - Removed persistence references to schema-extraneous `file_hash`, `total_modules`, and `total_chunks`.
  - Kept response-level `total_modules` and `total_chunks` because API responses already expose those operational values.

- `backend/services/vector_store_service.py`
  - Removed writes to the removed `chunk_index` column.
  - Continued accepting `chunk_index` as a method argument for call-site compatibility.
  - Uses `metadata_json` for the database `metadata` column.
  - Keeps SQLite-safe vector search for local bootability.

- `backend/services/topic_extraction_service.py`
  - Removed ordering by the deleted `chunk_index` column.
  - Uses shared vector-store search behavior.

## Verification

Executed from `backend/`:

```powershell
venv_py311\Scripts\python.exe -m pytest -q
```

Result: `2 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m compileall app services models -q
```

Result: passed.

```powershell
venv_py311\Scripts\python.exe -c "import app.main; print('import ok')"
```

Result: passed.

Startup smoke test:

```powershell
$env:USE_SQLITE_DEV='1'
venv_py311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8011
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8011/health
```

Result: HTTP 200.

## Schema Comparison

See `SCHEMA_COMPARISON_REPORT.md`.

## Remaining Blockers Outside Sprint 2

- Supabase Auth token validation is still not implemented in API routes.
- Existing demo user behavior can still violate the new production foreign keys until Sprint auth work replaces it.
- End-to-end upload/caption/carousel flows still require external API keys and real user rows.
- 95% validation enforcement, reranking, and Gemini Context Cache creation remain outside this sprint.
- Deprecation warnings remain for Pydantic config, SQLAlchemy declarative base import path, FastAPI `on_event`, and PyPDF2.
