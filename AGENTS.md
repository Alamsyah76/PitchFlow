## Generalization Rule

This system must not be tuned only for already uploaded PDFs.

Every fix must improve the shared runtime mechanism so it works for:
- old uploaded PDFs
- new uploaded PDFs
- unseen future PDFs

Forbidden:
- dataset chasing
- PDF-specific fixes
- vendor-specific fixes
- product-specific fixes
- file-name-specific fixes
- topic-specific fixes
- caption-specific fixes

Codex must always ask:
"Does this fix generalize to unseen future PDFs?"

If the answer is no, do not patch.
