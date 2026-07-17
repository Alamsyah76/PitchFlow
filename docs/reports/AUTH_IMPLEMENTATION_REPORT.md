# Auth Implementation Report

Date: 2026-05-26

Scope: Sprint 3 only. This sprint implemented Supabase JWT authentication and user ownership isolation for protected backend endpoints. Frontend, retrieval logic, and validation-engine behavior were not modified.

## Result

Production-style Supabase authentication is now enforced on protected backend content endpoints.

- Anonymous requests are rejected.
- Invalid JWTs are rejected.
- Expired JWTs are rejected.
- Authenticated user identity is extracted from the JWT `sub` claim.
- Public `users` profile rows are created on demand for FK compatibility.
- Resource access is scoped by `user_id`.
- Demo-user assumptions were removed from protected routes.

## Implemented Files

- `backend/app/auth.py`
  - Added `CurrentUser` context.
  - Added Supabase JWT decoding and validation.
  - Added FastAPI bearer-token dependency.
  - Added profile row bootstrap helper.
  - Added document/content ownership helpers.

- `backend/config/settings.py`
  - Added `SUPABASE_JWT_SECRET`.
  - Added `SUPABASE_JWT_AUDIENCE`, defaulting to `authenticated`.
  - Added dev fallback secret only under `USE_SQLITE_DEV`.

- `backend/app/routes_content.py`
  - Protected upload, caption generation, and carousel generation endpoints.
  - Upload now stores documents under the authenticated user.
  - Caption generation checks document ownership before embedding/retrieval/generation.
  - Carousel generation checks content ownership before generating or updating assets.

- `backend/app/routes_topics.py`
  - Protected topics and semantic search endpoints.
  - Both routes check document ownership before service execution.
  - Fixed ownership `HTTPException` handling so forbidden access remains `403`.

- `backend/services/carousel_service.py`
  - Added optional user ownership filter.
  - Generated Supabase Storage paths now include the owning user id:
    `users/{user_id}/contents/{content_id}/slide_{idx}.png`.

- `backend/tests/test_auth_security.py`
  - Added auth/security integration coverage.

## Ownership Enforcement

- `documents`
  - `get_owned_document` checks `documents.user_id == current_user.id`.
  - Enforced before topics, search, and caption generation.

- `vector_store`
  - Access happens through an owned `document_id`.
  - Routes validate document ownership before vector search or chunk retrieval.

- `contents`
  - `get_owned_content` checks `contents.user_id == current_user.id`.
  - Enforced before carousel generation.

- Generated assets and carousel records
  - Carousel generation filters content by owner.
  - Asset storage path is user-scoped.
  - `contents.carousel_images_urls` is only updated after owned content is resolved.

## Organization-Ready Structure

`ARCHITECTURE_STACK.md` defines `user_id` ownership, not an organization table. The PRD allows `Organization_ID` or `User_ID`.

Sprint 3 keeps enforcement on `user_id`, matching the actual schema. `CurrentUser` also carries optional `organization_id` from JWT claims (`organization_id`, `org_id`, or `app_metadata.organization_id`) so a future organization schema can consume it without changing token parsing again.

## Configuration Required

Production deployments must set:

```env
SUPABASE_JWT_SECRET=...
SUPABASE_JWT_AUDIENCE=authenticated
```

`SUPABASE_JWT_SECRET` must match the Supabase project JWT secret used to sign access tokens.

## Remaining Blockers for Sprint 4

- Retrieval still uses the pre-existing top-3 path; top-20 retrieval and reranking are not implemented.
- Caption validation still does not enforce the 95% rejection/rewrite loop.
- Gemini Context Cache creation/reuse remains incomplete.
- Production Supabase Storage bucket policy review is still needed for generated carousel assets.
- Organization-level tables/policies are not present because Sprint 2 schema followed `ARCHITECTURE_STACK.md` user ownership.
