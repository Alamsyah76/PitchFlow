# Security Test Report

Date: 2026-05-26

Scope: Sprint 3 auth and ownership isolation tests.

## Test Commands

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

```powershell
venv_py311\Scripts\python.exe -c "import app.main; print('import ok')"
```

Result: passed.

Startup smoke test:

```powershell
$env:USE_SQLITE_DEV='1'
venv_py311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8013
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8013/health
```

Result: HTTP 200.

## Covered Security Cases

- Valid token
  - A signed Supabase-style JWT reaches protected endpoint logic.

- Invalid token
  - Malformed token is rejected with HTTP 401 and `INVALID_TOKEN`.

- Expired token
  - Expired signed token is rejected with HTTP 401 and `TOKEN_EXPIRED`.

- Missing token
  - Anonymous protected request is rejected with HTTP 401 and `AUTH_REQUIRED`.

- Document ownership
  - Owner can pass ownership gate for their document.
  - Cross-user document access is rejected with HTTP 403 and `DOCUMENT_FORBIDDEN`.

- Content ownership
  - Cross-user carousel/content access is rejected with HTTP 403 and `CONTENT_FORBIDDEN`.

## Test Isolation

Auth tests use:

- in-memory SQLite
- FastAPI dependency override for `get_db`
- locally signed JWTs with the configured test `SUPABASE_JWT_SECRET`
- no external Supabase/OpenAI/Gemini calls

## Known Warnings

The passing suite still emits existing deprecation warnings:

- Pydantic class-based config
- PyPDF2 package deprecation
- SQLAlchemy `declarative_base` import path
- FastAPI `on_event` lifespan deprecation

These warnings are not Sprint 3 security failures.
