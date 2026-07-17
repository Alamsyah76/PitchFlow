# Pipeline Contract.md

# AI Content Operating System — Pipeline Contract

## Objective

This system must generate:

* grounded topics,
* grounded captions,
* document-specific business insight,

from uploaded PDFs without cross-document contamination.

The system must remain:

* domain-neutral,
* retrieval-grounded,
* deterministic enough for testing,
* resistant to stale runtime state.

The system is NOT a generic motivational copywriter.

The system is a:
Document-Grounded Semantic Content Engine.

---

# Core Pipeline

```text
PDF Upload
    ↓
Document Parsing
    ↓
Chunk Extraction
    ↓
Evidence Retrieval
    ↓
Document Isolation
    ↓
Domain Detection
    ↓
Topic Generation
    ↓
Topic Validation
    ↓
Caption Generation
    ↓
Caption Validation
    ↓
Frontend Rendering
```

---

# Pipeline Contracts

## 1. Document Parsing Contract

Input:

* uploaded PDF

Output:

* clean extracted text
* page metadata
* document_id
* normalized chunk structure

Requirements:

* every chunk MUST contain document_id
* no anonymous chunk allowed downstream
* malformed chunks MUST be discarded

Forbidden:

* downstream fallback chunks without document_id

---

# 2. Retrieval Contract

Goal:
retrieve only evidence belonging to active document_id.

Requirements:

* retrieval MUST filter by document_id before ranking
* retrieval cache MUST reset on document switch
* stale retrieval memory MUST NOT survive uploads

Forbidden:

* mixing chunks across documents
* fallback retrieval without ownership validation
* retrieval using previous upload context

Required Debug Logs:

* active_document_id
* retrieved_chunk_count
* unique_document_ids
* rejected_chunk_count

---

# 3. Domain Detection Contract

Goal:
identify dominant semantic domain from evidence.

Examples:

* ERP/business operations
* hardware/workstation
* network/security
* alerting/notification
* infrastructure monitoring

Requirements:

* domain derived from retrieved evidence
* domain confidence score required
* low-confidence domains should reduce topic count

Forbidden:

* hardcoded monitoring bias
* universal network framing
* forcing infrastructure narrative onto all PDFs

Rule:
If confidence < threshold:

* generate fewer topics
* do not hallucinate category

---

# 4. Topic Generation Contract

Topics MUST:

* originate from current evidence
* reflect dominant document domain
* express business meaning
* avoid keyword dumping

Topic quality rules:

* human-readable
* business-relevant
* concise
* grounded
* domain-aligned

Forbidden:

* stale terms from previous uploads
* unrelated categories
* generic monitoring fallback
* meaningless keyword concatenation

Examples of bad topics:

* “Monitoring traffic lebih cepat”
* “Mengurangi blind spot operasional”
  when source document is ERP or desktop hardware.

Rule:
1 strong topic is better than 2 weak topics.

---

# 5. Topic Validation Contract

Every topic must pass:

## Relevance

topic aligns with dominant evidence.

## Domain Integrity

topic does not violate domain matrix.

## Evidence Traceability

topic can map back to evidence snippets.

## Forbidden Vocabulary

topic cannot contain banned stale-domain terms.

If validation fails:

* reject topic
* regenerate
* or reduce topic count

---

# 6. Caption Generation Contract

Caption MUST:

* explain business insight naturally
* derive from evidence
* remain specific to document domain

Caption MUST NOT:

* use generic filler templates
* use keyword dump sentences
* reuse stale context
* hallucinate unrelated products/domains

Forbidden template examples:

* “Tekanan kerja tim biasanya naik...”
* “Bukti yang dipilih menunjukkan perlunya X, Y, dan Z”

These are fallback anti-patterns.

---

# 7. Caption Validation Contract

Caption validator must detect:

## Cross-document contamination

ERP terms inside Fortinet caption.

## Keyword dumping

lists of extracted tokens presented as insight.

## Weak token leakage

examples:

* built
* reduce
* they
* other
* mouse
* wired

## Template repetition

repeated paragraph structures across domains.

If failed:

* regenerate caption
* do not silently pass validation

---

# 8. Frontend Contract

Frontend must:

* render only current request state
* discard stale response payloads
* preserve request correlation IDs

Frontend is NOT responsible for:

* semantic correction
* domain classification
* retrieval filtering

---

# 9. Runtime State Contract

Caches allowed:

* embedding cache
* parsed PDF cache

Caches forbidden:

* stale topic state
* stale caption state
* previous upload semantic memory

On document switch:

* topic cache reset
* caption cache reset
* validation cache reset

---

# 10. Golden Rule

The system must prefer:

```text
less output + high grounding
```

over:

```text
more output + hallucinated semantic blending
```

Grounded accuracy is the highest priority.
