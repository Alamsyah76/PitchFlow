# Backend Bootability Report

Date: 2026-05-26

Scope: Sprint 1 only. The work was limited to restoring backend import/startup, router registration, dependency safety for startup smoke tests, and pytest collection.

## Result

Backend bootability is restored.

- `app.main` imports successfully.
- FastAPI registers the expected backend routers.
- Uvicorn starts successfully on a local test port.
- `/health` returns HTTP 200.
- Pytest runs successfully from the backend root.

## Fixed Files

- `backend/app/routes_topics.py`
  - Added the missing router module imported by `backend/app/main.py`.
  - Registered `GET /api/v1/content/topics`.
  - Registered `POST /api/v1/content/search`.
  - Reused existing service-layer code; no new product feature logic was added.

- `backend/services/vector_store_service.py`
  - Fixed `VectorStore(metadata=...)` usage to match the ORM field `metadata_json`.
  - Fixed metadata reads to use `metadata_json`.
  - Added local Text-backed embedding serialization/deserialization so SQLite startup/dev paths do not break on list bindings.
  - Added a SQLite-safe cosine fallback for local similarity search, avoiding pgvector SQL calls against SQLite.

- `backend/services/topic_extraction_service.py`
  - Fixed metadata reads to use `metadata_json`.
  - Routed semantic search through `VectorStoreService.vector_similarity_search` so SQLite-safe search behavior is shared.
  - Removed unused imports.

- `backend/scripts/tmp_upload_test.py`
  - Moved import-time HTTP upload side effects behind `if __name__ == "__main__"`.
  - This prevents pytest collection from trying to call a live server before tests start.

- `backend/tests/test_startup_smoke.py`
  - Added startup smoke tests for app import, route registration, FastAPI lifespan startup, and `/health`.

- `backend/requirements_dev.txt`
  - Added `pytest==8.2.2` for the required test command.

## Verification Commands

Executed from project root unless noted.

```powershell
backend\venv_py311\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); import app.main; print('import ok')"
```

Result: passed.

```powershell
venv_py311\Scripts\python.exe -m pytest -q
```

Run from `backend/`.

Result: `2 passed, 14 warnings`.

```powershell
venv_py311\Scripts\python.exe -m compileall app services models -q
```

Run from `backend/`.

Result: passed.

Startup smoke test:

```powershell
$env:USE_SQLITE_DEV='1'
venv_py311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8010/health
```

Result: HTTP 200 with:

```json
{"status":"healthy","service":"AI Marketing Content Engine Backend"}
```

## Remaining Blockers Outside Sprint 1

- Production database schema still does not match `ARCHITECTURE_STACK.md`.
- ORM still uses local-development compatible column types instead of a real pgvector SQLAlchemy type.
- Supabase Auth/user isolation is not implemented; routes still use demo identity paths.
- End-to-end upload/caption/carousel flows still require external API keys and production schema alignment.
- The 95% validity enforcement loop is not implemented.
- Cohere/BGE reranking and real Gemini Context Cache creation are not implemented.
- Deprecation warnings remain for Pydantic class-based config, SQLAlchemy `declarative_base`, FastAPI `on_event`, and PyPDF2.
