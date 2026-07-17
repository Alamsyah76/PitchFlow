# Environment Setup

Date: 2026-05-26

## Purpose

This backend now fails fast in production mode when required environment variables are missing. Local SQLite boot smoke tests remain available only when `USE_SQLITE_DEV=1`.

## Setup Steps

1. Copy `backend/.env.example` to `backend/.env`.
2. Replace every `replace-with-*` placeholder with a real local or deployment secret.
3. Keep `USE_SQLITE_DEV=0` for production and staging.
4. Use `USE_SQLITE_DEV=1` only for local smoke tests that intentionally avoid Supabase/PostgreSQL.

## Required Production Variables

- `DATABASE_URL`: PostgreSQL or Supabase Postgres connection string. Must start with `postgresql://` or `postgres://`.
- `SUPABASE_URL`: Supabase project API URL.
- `SUPABASE_SERVICE_ROLE_KEY`: Server-side service role key. Never expose this to frontend code.
- `SUPABASE_ANON_KEY`: Supabase anonymous key.
- `SUPABASE_JWT_SECRET`: JWT secret used to validate Supabase HS256 access tokens.
- `SUPABASE_JWT_AUDIENCE`: Expected JWT audience. Defaults to `authenticated`.
- `OPENAI_API_KEY`: OpenAI API key for embeddings/generation paths.
- `GEMINI_API_KEY`: Gemini API key for topic and caption generation paths.

## Optional Variables

- `API_HOST`
- `API_PORT`
- `DEBUG`
- `CORS_ORIGINS`
- `VECTOR_EMBEDDING_MODEL`
- `VECTOR_DIMENSION`
- `VECTOR_SIMILARITY_TOP_K`
- `LOG_LEVEL`
- `USE_OLLAMA`
- `OLLAMA_EMBED_MODEL`
- `OLLAMA_BASE_URL`

## Security Notes

- `backend/.env.example` contains placeholders only.
- Any credential that previously appeared in `.env.example` should be rotated if it was valid.
- Production startup does not derive a database password from `SUPABASE_URL`; `DATABASE_URL` is required explicitly.
- Do not enable `USE_SQLITE_DEV` in production, staging, CI that validates production behavior, or any environment that handles user data.
