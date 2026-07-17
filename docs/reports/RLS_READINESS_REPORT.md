# RLS Readiness Report

Date: 2026-05-26

## Status

PARTIAL. Backend ownership checks and migration policies are aligned, but live Supabase RLS and Storage policy execution still need integration validation.

## Implemented Table Policies

RLS is enabled for:

- `public.users`
- `public.documents`
- `public.vector_store`
- `public.contents`

Policies enforce:

- Users can select, insert, and update only their own profile row through `auth.uid() = id`.
- Documents are scoped to `auth.uid() = user_id`.
- Vector chunks are scoped through the owning document.
- Generated contents are scoped to `auth.uid() = user_id`.

## Backend Ownership Logic

Backend routes and services enforce ownership before protected operations:

- JWT auth is required on protected content endpoints.
- Invalid and expired JWTs return 401.
- Cross-user document access returns 403.
- Cross-user content and carousel access returns 403.
- Upload, topics, caption, search, and carousel routes run under authenticated user context.
- Carousel asset paths are user-scoped under `users/{user_id}/contents/{content_id}/...`.

## Demo User Review

No all-zero demo user fallback remains in reviewed backend app, service, model, or test code. Local-only development placeholders are gated behind `USE_SQLITE_DEV=1`.

## Production Caveats

- The backend uses a server-side database connection. Supabase service-role access can bypass RLS, so backend ownership checks remain mandatory.
- Supabase Storage bucket RLS and object policies are not defined or tested in this sprint.
- RLS policies have not yet been exercised against a live Supabase project with real JWT claims.
- `ensure_user_profile()` creates a profile for a valid JWT subject; this is acceptable only if Supabase JWT validation and onboarding expectations remain strict.

## Readiness Before Retrieval Sprint

Backend-side isolation is ready for retrieval implementation work, provided Sprint 4 does not bypass existing auth and ownership dependencies. Production deployment still requires a live Supabase RLS and Storage integration test.
