# DO_NOT_IMPLEMENT.md

# Never Implement

The system must never prioritize:

- dominant_terms generation
- keyword overlap scoring
- keyword density logic
- noun stitching
- token assembly
- keyword-first caption generation
- deterministic phrase merging

---

# Never Regress To

Bad Example:

Retrieved Chunks
→ Keyword Extraction
→ Topic
→ Caption

Reason:

Produces artificial content.

Produces shallow reasoning.

Produces repetitive outputs.

---

# Never Replace SCI With

- Keyword ranking
- TF-IDF style captioning
- Tag aggregation
- Frequency-based narrative generation

---

# Core Principle

Retrieval is evidence.

Retrieval is not understanding.

Understanding must happen before generation.

---

# Future Expansion Restriction

Do not implement:

- Corpus RAG
- Agentic AI
- MCP Layer

before SCI reaches browser-validated quality >= 85%.

SCI comes first.