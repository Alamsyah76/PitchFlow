# BASELINE LOCK — Semantic Content Engine OS 2

**Effective Date:** Locked by Gemini Principal SaaS Product Designer Review  
**Status:** PRODUCTION-APPROVED — No regression allowed below these scores  
**Scope:** All engine, scoring, UI, and system-level benchmark scores  

---

## 1. TOPIC ENGINE

| Metric | Locked Minimum | Current (Reference) |
|--------|----------------|---------------------|
| Validity | 93/100 | 93/100 |
| Relevancy | 93/100 | 93/100 |
| Document Correlation | 92/100 | 92/100 |
| Grounded Document | 92/100 | 92/100 |
| Stability | 91/100 | 91/100 |

## 2. CAPTION ENGINE

| Metric | Locked Minimum | Current (Reference) |
|--------|----------------|---------------------|
| Softselling | 93/100 | 93/100 |
| Subtle | 94/100 | 94/100 |
| Humanize | 84/100 | 84/100 |
| Hallucination | **maximum 8/100** | 8/100 |
| AI-ish | **maximum 18/100** | 18/100 |
| Grounded Document | 89/100 | 89/100 |
| Stability | 87/100 | 87/100 |

## 3. HASHTAG ENGINE

| Metric | Locked Minimum | Current (Reference) |
|--------|----------------|---------------------|
| Validity | 95/100 | 95/100 |
| Relevancy | 94/100 | 94/100 |
| Correlation | 94/100 | 94/100 |
| Grounded Document | 94/100 | 94/100 |
| Stability | 95/100 | 95/100 |

## 4. CREATIVE DIRECTION

| Metric | Locked Minimum | Current (Reference) |
|--------|----------------|---------------------|
| Overall Quality | 94/100 | 94/100 |

## 5. IMAGE GENERATION

| Metric | Locked Minimum | Current (Reference) |
|--------|----------------|---------------------|
| Validity | 96/100 | 96/100 |
| Relevancy | 96/100 | 96/100 |
| Correlation | 95/100 | 95/100 |
| Grounded Document | 95/100 | 95/100 |
| Stability | 94/100 | 94/100 |

## 6. SYSTEM LEVEL

| Metric | Locked Minimum | Current (Reference) |
|--------|----------------|---------------------|
| Overall System Score | 93/100 | 93/100 |
| Stability Score | 92/100 | 92/100 |
| Generalization Score | 91/100 | 91/100 |
| Grounded Document Score | 92.5/100 | 92.5/100 |

---

## MANDATORY RULES

### Rule 1 — Baseline Protection

Before any future code modification:
- Compare every affected metric against this locked baseline.
- Assume the current validated scores are production-approved and stable.
- Any patch that risks regression below the locked minimum **must be rejected**.

### Rule 2 — No Regression Policy

A patch is **automatically rejected** if it causes a reduction in any of the following, even if another metric improves:

- Topic quality (any metric)
- Caption quality (any metric)
- Hashtag quality (any metric)
- Image quality (any metric)
- Grounding (any metric)
- Generalization (any metric)
- Stability (any metric)

### Rule 3 — Patch Acceptance Criteria

Future patches may only be accepted if they satisfy **one** of:

- **A.** Maintain all baseline scores (no regression on any metric).
- **B.** Improve one or more scores while preserving all others at or above baseline minimum.

Lowering any metric below locked minimum to gain improvement elsewhere is **not permitted**.

### Rule 4 — Validation Requirement

Before any patch is declared PASS:
- Browser validation required (real PDF flow, not Explore Demo).
- Runtime validation required (zero JS errors).
- Regression check against this locked baseline required.

### Rule 5 — Generalization Rule

Never optimize for:
- Specific PDF filename
- Specific vendor or product name
- Specific industry vertical
- Specific file hash or upload batch

All improvements **must generalize** to unseen future PDFs. A fix that only works for known documents is not acceptable.

### Rule 6 — Architecture Rule

Continue enforcing:
- One responsibility per file.
- No giant files (prefer extraction over bloating).
- Micro-patch only (one logical change per commit).
- One change at a time per review cycle.
- Browser validation required before next patch is applied.

---

## GOVERNANCE

### Override Process

If a patch is proposed that would intentionally reduce a locked metric (e.g., to enable a major architectural improvement), the override requires:

1. Written rationale from the proposing engineer.
2. Review and approval by Gemini Principal SaaS Product Designer.
3. Explicit update of this BASELINE_LOCK.md with new locked minimums.
4. Validation against all other metrics to confirm no unintended regressions.

### Violation

Any patch that causes an undocumented regression below these locked scores shall be:
- Immediately reverted.
- Reviewed for root cause.
- Blocked from re-application until the regression is fixed and re-validated.

---

*This document is the single source of truth for quality floor requirements. All future development references this baseline before, during, and after implementation.*
