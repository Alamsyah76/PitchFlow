# Implementation Audit

Audit date: 2026-05-26

Source documents compared:

- `PRD_Content_Engine.txt`
- `ARCHITECTURE_STACK.md`
- `PROMPT_TEMPLATES.md`

Current implementation inspected:

- Frontend: `frontend/pages`, `frontend/components`, `frontend/lib/api.ts`
- Backend: `backend/app`, `backend/models`, `backend/services`, `backend/migrations`

## Completion Summary

| Document | Completion | Rationale |
| --- | ---: | --- |
| `PRD_Content_Engine.txt` | 38% | Core backend ingestion pieces exist and a static dashboard exists, but the end-to-end user workflow is not wired, SaaS auth/security is absent, reranking is absent, and 95% validation is not enforced. |
| `ARCHITECTURE_STACK.md` | 45% | FastAPI routes, ORM models, and a migration exist, but the migration does not match the required schema, RLS is not aligned with the PRD data model, duplicate caption routes exist, and pgvector is not used correctly in the SQLAlchemy model layer. |
| `PROMPT_TEMPLATES.md` | 55% | Topic, caption, and auditor prompts are partially embedded in services, but they are not centralized templates, not exact to the document, and not consistently used across duplicate caption generation paths. |

## 1. Requirements Implemented

### Product and UI

- A Next.js frontend exists under `frontend/`.
- TypeScript and TailwindCSS are configured.
- A modern dashboard shell exists:
  - `frontend/components/app-shell/Sidebar.tsx`
  - `frontend/components/app-shell/HeaderBar.tsx`
  - `frontend/components/app-shell/AppShell.tsx`
- A static Content Studio page exists at:
  - `frontend/pages/index.tsx`
  - `frontend/pages/content-studio.tsx`
- The current UI includes sidebar navigation, header, workflow stepper, upload card, keyword card, topic cards, caption preview, insights panel, and output buttons.
- A TipTap rich text editor exists in `frontend/components/RichEditorTiptap.tsx`.
- Failed proposition highlighting is implemented inside the TipTap editor via ProseMirror decorations.

### Backend and API

- FastAPI app exists in `backend/app/main.py`.
- Health endpoints exist:
  - `GET /health`
  - `GET /api/health`
- PDF upload endpoint exists:
  - `POST /api/v1/content/upload`
- Topic generation endpoint exists:
  - `GET /api/v1/content/topics`
- Caption generation endpoint exists, but duplicated:
  - `POST /api/v1/content/generate-caption` in `routes_content.py`
  - `POST /api/v1/content/generate-caption` in `routes_topics.py`
- Carousel generation endpoint exists:
  - `GET /api/v1/content/generate-carousel`
- Semantic search endpoint exists:
  - `POST /api/v1/content/search`

### RAG and Data Processing

- PDF validation and extraction exist.
- Large-file modularization exists through page grouping in `DocumentService.process_large_file`.
- LlamaIndex `SemanticSplitterNodeParser` is attempted in `DocumentService._semantic_chunk_text`.
- Fallback chunking exists if semantic splitting fails.
- OpenAI embedding provider exists for `text-embedding-3-small`.
- Ollama embedding provider exists for local embeddings.
- Document hash caching exists to prevent duplicate processing.
- Vector-store service exists for saving and retrieving chunks.

### AI Generation and Auditing

- Gemini topic generation service exists.
- Gemini caption generation service exists.
- GPT-4o auditor service exists.
- Anti-AI banned word list exists in `routes_content.py`.
- Carousel image generation exists using Pillow.
- Supabase Storage upload path exists in `carousel_service.py`.

## 2. Requirements Partially Implemented

### Dashboard Workflow

- The dashboard layout is present, but it is currently static.
- `frontend/lib/api.ts` contains API helper functions, but `ContentStudioPage.tsx` does not call them.
- Upload, topic generation, topic selection, caption generation, copy, and carousel generation are not wired into the new dashboard.
- Older components (`ColumnLeft`, `ColumnCenter`, `ColumnRight`, `ThreeColumnLayout`) contain parts of the required 3-column workflow, but they are no longer used by the current page.

### 3-Column PRD Layout

- The PRD requires a permanent 3-column workflow:
  - Input and settings
  - Topic and validation
  - Editor and output
- The current UI uses a dashboard shell with sections, not the permanent 3-column operating layout. It is visually polished but structurally different from the PRD.

### Brand Kit

- Old `ColumnLeft.tsx` includes target audience, language, colors, and logo file fields.
- The current dashboard only shows a keyword input and static tips.
- Backend `User` model includes brand colors and logo URL.
- The active frontend does not persist or send brand kit settings to backend carousel generation.

### Supabase and pgvector

- Dependencies and migration mention Supabase and pgvector.
- Runtime ORM models use SQLite-compatible fallback types:
  - `VECTOR_TYPE = Text`
  - `JSONB_TYPE = JSON`
  - `UUID_TYPE = String(36)`
- This helps local development but violates the production requirement for Supabase PostgreSQL with pgvector-backed vectors.

### Gemini Context Caching

- `GeminiCacheManager` exists.
- `cachedContent` is added only if an in-memory cache entry is already valid.
- There is no actual Gemini cache creation API call.
- The required behavior for large documents over 30,000 tokens is not implemented.

### 95% Truth Rule

- GPT-4o auditor service exists and asks for validity scoring.
- The `routes_content.py` caption path stores `validity_score` and `failed_propositions`.
- There is no enforced rejection/rewrite loop when score is below 95%.
- The `routes_topics.py` caption path does not run the auditor and only returns caption text.
- The active frontend does not display the required green `Validity Score: XX% Safe to Post` badge.

### Carousel Generation

- Pillow-based slide rendering exists.
- It can create 3-5 slides and upload to Supabase Storage.
- Slides are visually basic and do not yet include robust infographic layouts, dynamic graphic elements, icon systems, or reliable local fallback despite README mentioning one.
- Brand kit injection depends on `User` row data, but the active frontend does not create/update that user brand kit.

## 3. Requirements Missing

- Real Supabase Auth integration.
- Authorization token validation in backend routes.
- Organization/User isolation on every document and vector query.
- Row-level security matching the exact required SaaS model.
- Wipe Workspace Memory button and backend delete workflow.
- Cohere Rerank or BGE reranker.
- Retrieval of 20 candidate chunks before reranking to top 3.
- True Gemini Context Caching creation and reuse.
- Hierarchical summarization per module for topic generation.
- Automatic topic generation immediately after PDF processing.
- Enforced Anti-AI rewrite across every caption generation path.
- Enforced validity score threshold with rewrite/reject loop.
- Hashtag generation from AI or backend.
- Download bundle of carousel images as a cohesive output from the active UI.
- Future content polymorphism model:
  - X thread
  - Video shorts script
  - Blog article
- Production-ready Supabase Storage bucket setup/migration.
- OCR support for image-only PDFs.
- Tests for RAG correctness, prompt outputs, API contracts, and frontend workflows.

## 4. Architecture Violations

### Duplicate API Route

`POST /api/v1/content/generate-caption` is registered in both:

- `backend/app/routes_content.py`
- `backend/app/routes_topics.py`

This creates ambiguous behavior. Since `content_router` is included before `topics_router` in `backend/app/main.py`, one implementation may shadow the other depending on FastAPI route order. The two implementations have different behavior:

- `routes_content.py` performs Gemini generation, banned-word rewrite, GPT-4o audit, and persistence.
- `routes_topics.py` returns generated caption only and does not persist or audit.

### Migration Does Not Match Required DDL

`ARCHITECTURE_STACK.md` requires:

- `users.id UUID REFERENCES auth.users`
- `documents.user_id`
- `documents.file_name`
- `documents.total_pages`
- `documents.is_cached`
- `vector_store.module_chunk_id`
- `vector_store.chunk_content`
- `vector_store.embedding_vector vector(1536)`
- `contents.topic_selected`
- `contents.final_caption`
- `contents.carousel_images_urls`
- `contents.validity_score`
- `contents.failed_propositions`
- `contents.language_output`

But `backend/migrations/001_init_database.sql` defines a different CMS-like schema:

- `documents.title`, `description`, `content`, `document_type`, `created_by`
- `vector_store.chunk_text`, `embedding`
- `contents.title`, `content_type`, `content_text`, `embedding`, `relevance_score`

This migration is not compatible with the ORM models or with the required DDL.

### ORM Does Not Use pgvector Correctly

`backend/models/database.py` stores vectors as `Text`, not a pgvector column type. Similarity search calls `func.cosine_distance(VectorStore.embedding_vector, query_vector)`, but the model does not guarantee that Postgres/pgvector operators will work.

### Metadata Column Name Mismatch

The ORM model defines `metadata_json`, but services use `metadata`:

- `VectorStore(metadata=...)` in `vector_store_service.py`
- `VectorStore.metadata` in search queries

This is likely a runtime error because `metadata` is reserved by SQLAlchemy declarative models and is not the declared column name.

### SQLite Fallback Conflicts With Production Architecture

The backend silently falls back to SQLite if Supabase configuration is missing. That is useful for demos but violates the production environment requirement where Supabase PostgreSQL and pgvector are mandatory.

### Frontend and Backend Contract Drift

The old frontend expected fields like `final_caption`; `routes_topics.py` returns `caption`; `routes_content.py` returns `final_caption`. The new dashboard does not call either route, but once wired this mismatch will cause integration errors unless normalized.

### shadcn/ui Is Imitated, Not Installed

The frontend has local `Button` and `Card` primitives under `frontend/components/ui`, but it does not have a full shadcn/ui setup with Radix primitives, `components.json`, or generated shadcn components.

## 5. Missing API Integrations

### Frontend Missing Integrations

The current `ContentStudioPage.tsx` does not call:

- `uploadPdf`
- `fetchTopics`
- `generateCaption`
- `generateCarousel`

The following UI actions are static:

- Choose File
- Generate Topics
- Select topic
- Copy Caption
- Generate Image

### Backend Missing/Incomplete External Integrations

- Supabase Auth token verification.
- Supabase user identity extraction from `Authorization: Bearer <Token>`.
- Supabase Storage bucket lifecycle and local fallback.
- Cohere Rerank API.
- BGE reranker or local reranker through Ollama.
- Gemini Context Cache creation endpoint.
- OpenAI/Gemini response schema hardening for JSON-only outputs.
- Real organization/user-scoped query filtering.

## 6. Missing Database Models

Required but missing or not correctly modeled:

- `auth.users` reference in `public.users`.
- `organization_id` ownership model that is consistently enforced.
- Exact `documents` table from `ARCHITECTURE_STACK.md`.
- Exact `vector_store` table with `embedding_vector vector(1536)` and `metadata JSONB`.
- Exact `contents` table with `NUMERIC(5,2)` validity score.
- Storage metadata table for uploaded PDFs and carousel assets.
- Prompt template/version table.
- Audit run table for claim-level scoring history.
- Rerank trace table for top-20 candidate chunks and top-3 selected chunks.
- Workspace memory/deletion log table.
- Content format polymorphism table for future outputs.

## 7. Missing AI Workflows

- Full pipeline orchestration from upload to topics to caption to audit to carousel.
- Hierarchical summarization:
  - module summaries
  - combined topic synthesis from summaries
- Target retrieval:
  - retrieve 20 chunks
  - rerank to top 3
  - pass only top 3 to Gemini
- Enforced 95% validity loop:
  - split draft into atomic propositions
  - audit each proposition
  - reject/rewrite when score is below 95
  - return failed propositions to UI
- AI hashtag generation.
- AI slide outline generation before rendering images.
- Human-approved caption state before carousel generation.
- Cost/token tracking.
- Context-cache lifecycle management.

## 8. Missing Prompt Templates

The prompts from `PROMPT_TEMPLATES.md` are partially represented in code, but missing as reusable templates:

- No `backend/prompts/` module.
- No versioned prompt registry.
- No exact reusable primary topic prompt.
- No exact reusable soft-selling prompt.
- No exact reusable auditor prompt.
- No separate rewrite prompt for banned words.
- No prompt for hierarchical module summaries.
- No prompt for carousel slide outline generation.
- No prompt tests or prompt snapshot tests.

Implementation notes:

- `GeminiService._get_system_prompt` approximates the topic prompt.
- `GeminiService.generate_caption` includes the caption formula but does not pass `systemInstruction`.
- `AuditorService.audit` approximates the auditor prompt.
- `routes_content.py` has an inline banned-word rewrite instruction.

## 9. Missing Pages

Routes in the sidebar are mostly not implemented:

- `/dashboard`
- `/image-studio`
- `/history`
- `/saved`
- `/templates`
- `/settings`

Workflow or SaaS pages missing:

- Login/signup/auth callback.
- User/team settings.
- Brand kit management.
- Document history.
- Saved generated content.
- Carousel preview/download page.
- Template library.
- Workspace memory/wipe page or settings panel.
- Billing/credits page.

## 10. Missing Components

Active dashboard components missing:

- Real upload dropzone with file input and drag/drop behavior.
- Target audience dropdown.
- Language toggle.
- Brand color inputs.
- Logo upload component.
- Topic selection state component wired to backend.
- Loading/skeleton states for upload/topics/caption/carousel.
- Error and retry states.
- Validity score badge.
- Failed proposition review panel.
- Rich editor integration in the active dashboard.
- Hashtag component backed by generated output.
- Carousel preview component.
- Carousel download component.
- Wipe Workspace Memory control.
- Mobile sidebar sheet/drawer.
- shadcn components beyond local `Button` and `Card`:
  - `Input`
  - `Label`
  - `Badge`
  - `Progress`
  - `Avatar`
  - `Tooltip`
  - `Sheet`
  - `ScrollArea`
  - `DropdownMenu`

## Highest-Priority Remediation Order

1. Resolve backend route duplication for `POST /api/v1/content/generate-caption`.
2. Replace migration with the exact `ARCHITECTURE_STACK.md` schema and align ORM models to it.
3. Fix `VectorStore.metadata` vs `metadata_json` and use real pgvector column support.
4. Wire the new dashboard to `frontend/lib/api.ts` or a typed workflow hook.
5. Add auth/user identity and stop using the demo all-zero user ID.
6. Implement top-20 retrieval plus Cohere/BGE reranking to top 3.
7. Implement actual Gemini context-cache creation/reuse.
8. Centralize prompt templates and make services consume exact prompt versions.
9. Enforce the 95% validation loop before persisting/posting output.
10. Add carousel preview/download flow and brand kit persistence.
