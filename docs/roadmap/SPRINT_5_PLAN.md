# Sprint 5 Plan

Date: 2026-05-27

## Status

Planning only. No application code has been modified for Sprint 5.

## Inputs Reviewed

- `PRD_Content_Engine.txt`
- `ARCHITECTURE_STACK.md`
- `PROMPT_TEMPLATES.md`
- `FINAL_SPRINT_4_AUDIT.md`

## Sprint 5 Assumption

Sprint 4 completed retrieval preparation: top-20 vector retrieval, reranking to top 3, and context payload construction. Based on the PRD and architecture, Sprint 5 should implement the next backend stage for `POST /api/v1/content/generate-caption`:

1. Send only the top 3 reranked chunks to Gemini 1.5 Flash.
2. Generate the soft-selling LinkedIn draft from the prompt template.
3. Apply the anti-AI-ish banned phrase sensor and controlled rewrite loop.
4. Run the factual auditor / 95% validity rule.
5. Persist successful generated content into `contents`.
6. Return caption, score, failed propositions, and content ID.

If Sprint 5 is intended to cover Gemini generation only and defer the auditor to Sprint 6, that scope should be confirmed before implementation.

## Constraints To Preserve

- Do not modify frontend.
- Do not start carousel work.
- Do not bypass Supabase JWT auth.
- Do not bypass document ownership checks.
- Do not send all 20 retrieved chunks to Gemini.
- Do not re-embed documents during caption generation.
- Keep deterministic/mock logic limited to tests.
- Preserve Sprint 4 retrieval boundary: retrieve top 20, rerank top 3, send only top 3 to Gemini.

## Proposed Implementation Plan

### 1. Formalize Caption Generation Request/Response Schemas

Add or update Pydantic models for the caption generation endpoint:

- Request fields:
  - `document_id`
  - `topic`
  - `language`
  - `target_audience`
- Response fields:
  - `success`
  - `document_id`
  - `content_id`
  - `selected_topic`
  - `final_caption`
  - `validity_score`
  - `failed_propositions`
  - `top_3_context_chunks`
  - `retrieval_count`
  - `rerank_method`
  - `rewrite_attempts`

Keep backward-compatible payload aliases only if required by existing clients.

### 2. Build Prompt Payload From Sprint 4 Context

Use `RetrievalPipelineService.prepare_caption_context()` as the mandatory first step.

Transform `context_payload["top_3_context_chunks"]` into the `RERANKED_CONTEXT` input required by `PROMPT_TEMPLATES.md`.

The Gemini input must include:

- selected topic
- target audience
- language
- only the top 3 reranked chunks
- enough metadata for traceability

### 3. Implement Gemini Draft Generation Integration

Use the existing Gemini service if it already matches the required prompt contract. If it does not, update it to support:

- strict soft-selling prompt from `PROMPT_TEMPLATES.md`
- target language control
- top-3-only context injection
- optional rewrite instruction for banned phrase cleanup

Do not send the full document or top 20 chunks to Gemini.

### 4. Implement Anti-AI-ish Sensor

Add backend validation for the banned phrase list from `PROMPT_TEMPLATES.md` and PRD:

- Indonesian terms:
  - `lanskap`
  - `merevolusi`
  - `komprehensif`
  - `penting sekali`
  - `menakjubkan`
  - `di era digital ini`
  - `seperti yang kita ketahui`
  - `ingatlah bahwa`
- English terms:
  - `landscape`
  - `revolutionize`
  - `comprehensive`
  - `crucial`
  - `testament`
  - `delve`

If banned phrases are found, request a Gemini rewrite with a bounded retry limit.

### 5. Run 95% Auditor

Use existing auditor service if it already implements the `PROMPT_TEMPLATES.md` auditor schema. Otherwise update it to return:

- `validity_score`
- `failed_propositions`

The auditor context should be the same grounded top-3 evidence chunks unless the user approves a broader audit context. This keeps token usage aligned with the Sprint 4 retrieval boundary, but it may reduce audit coverage if the generated draft contains claims outside the top-3 context.

Implementation decision needed:

- Option A: Audit against top-3 reranked chunks only for token savings.
- Option B: Audit against a larger retrieved evidence set, such as top 20, for stronger factual validation.

The PRD says claims are checked against original PDF context, while Sprint 4 emphasizes not sending all 20 chunks to Gemini. The auditor is a separate LLM call, so this should be decided explicitly.

### 6. Enforce 95% Validity Rule

If `validity_score >= 95`, persist the caption in `contents`.

If `validity_score < 95`, either:

- reject and return failed propositions without persistence, or
- trigger a bounded Gemini rewrite/audit loop.

The PRD requires rejection and automatic rewrite if under 95. Recommended implementation:

- maximum 2 audit rewrite attempts
- persist only if final score is at least 95
- return `422 VALIDITY_SCORE_TOO_LOW` if attempts fail

### 7. Persist Successful Content

Create a `contents` row only after:

- auth succeeds
- document ownership is verified
- retrieval succeeds
- reranking succeeds
- Gemini draft succeeds
- anti-AI-ish sensor passes
- validity score passes threshold

Persist:

- `user_id`
- `document_id`
- `topic_selected`
- `final_caption`
- `carousel_images_urls=[]`
- `validity_score`
- `failed_propositions`
- `language_output`

### 8. Tests

Add focused backend tests for:

- endpoint rejects anonymous access
- endpoint rejects cross-user document access
- endpoint calls retrieval and sends only top 3 chunks to Gemini
- endpoint does not send top 20 chunks to Gemini
- successful caption generation persists `contents`
- low validity score rejects or rewrites according to approved behavior
- banned phrases trigger rewrite
- auditor failed propositions are returned
- no content is persisted when validity remains below 95
- missing Gemini config returns a clear error
- missing auditor/OpenAI config returns a clear error

Mocks should be test-only and injected with monkeypatch/dependency overrides. No fake production fallback.

## Candidate Files To Modify After Approval

Application code:

- `backend/app/routes_content.py`
- `backend/services/gemini_service.py`
- `backend/services/auditor_service.py`
- `backend/services/retrieval_pipeline_service.py`
- `backend/models/schemas.py`
- `backend/config/settings.py`
- `backend/.env.example`

New backend service files, if needed:

- `backend/services/caption_generation_service.py`
- `backend/services/anti_ai_sensor_service.py`

Tests:

- `backend/tests/test_caption_generation_pipeline.py`
- possibly `backend/tests/test_retrieval_pipeline.py` if response shape changes
- possibly `backend/tests/test_auth_security.py` if new endpoint error behavior needs explicit coverage

Reports:

- `SPRINT_5_IMPLEMENTATION_REPORT.md`
- `CAPTION_GENERATION_REPORT.md`
- `VALIDATION_ENGINE_REPORT.md`
- `SECURITY_TEST_REPORT.md` if Sprint 5 updates security test coverage

No planned frontend files.

No planned migration files unless persistence reveals a schema mismatch. Current `contents` schema appears sufficient for Sprint 5.

## Commands To Run After Implementation

From `backend/`:

```powershell
venv_py311\Scripts\python.exe -m pytest -q
venv_py311\Scripts\python.exe -m pytest tests\test_caption_generation_pipeline.py -q
venv_py311\Scripts\python.exe -m pytest tests\test_retrieval_pipeline.py -q
venv_py311\Scripts\python.exe -m pytest tests\test_auth_security.py -q
venv_py311\Scripts\python.exe -m compileall app services models -q
```

Startup smoke test:

```powershell
$env:USE_SQLITE_DEV='1'
venv_py311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8018
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8018/health
```

## Approval Needed Before Code Changes

Before implementation, confirm the Sprint 5 scope:

1. Implement Gemini generation plus anti-AI sensor only, with the 95% auditor deferred.
2. Implement Gemini generation, anti-AI sensor, 95% auditor, rewrite loop, and persistence in one sprint.

Recommended: option 2, because `ARCHITECTURE_STACK.md` defines `generate-caption` as retrieval, reranking, Gemini draft, auditor, and final response in one endpoint.
