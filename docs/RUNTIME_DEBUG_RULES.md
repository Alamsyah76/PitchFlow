# Runtime Debug Rules

Runtime debugging rules for Semantic Content Engine OS 2.

## Primary Objective

The system must work for:

- old uploaded PDFs
- new uploaded PDFs
- unseen future PDFs

Runtime fixes must target shared mechanisms, not specific documents.

## Mandatory Debug Sequence

1. Identify active route.
2. Identify final writer.
3. Identify validator input.
4. Identify first wrong layer.
5. Patch only that layer.
6. Browser validation required.

## Source Of Truth

- Browser runtime is source of truth.
- Do not trust local replay alone.
- Do not trust assumptions.
- Verify runtime evidence before patching.

## Forbidden Debugging Patterns

- PDF-specific fixes
- vendor-specific fixes
- product-specific fixes
- file-name-specific fixes
- topic-specific fixes
- caption-specific fixes
- dataset chasing

## Required Question Before Every Patch

"Will this fix improve behavior for unseen future PDFs?"

If the answer is no:  
Do not patch.
