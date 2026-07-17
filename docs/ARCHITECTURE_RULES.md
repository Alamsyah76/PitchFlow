# Architecture Rules

Architecture rules for Semantic Content Engine OS 2.

## Core Rules

1. One file = one responsibility.
2. Avoid giant files.
3. Avoid overlapping fallback routes.
4. Avoid multiple final writers.
5. Keep topic layer separate from caption layer.
6. Keep evidence layer separate from narrative layer.
7. Keep validators separate from writers.
8. Runtime fixes must target the first wrong layer only.
9. Fix shared runtime mechanisms, not individual PDFs.
10. Every architecture change must work for old PDFs, new PDFs, and unseen future PDFs.

## Forbidden

- dataset chasing
- PDF-specific architecture
- vendor-specific logic
- product-specific logic
- file-name-specific logic
- topic-specific logic
- caption-specific logic
