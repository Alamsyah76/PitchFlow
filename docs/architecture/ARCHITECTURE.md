# ARCHITECTURE.md

# Current Architecture

PDF
→ OCR
→ Chunking
→ Embedding
→ Vector Storage
→ Retrieval
→ Topic Generation
→ Caption Generation

Current Status:

- PDF Upload Works
- OCR Works
- Embeddings Work
- Retrieval Partially Works
- Unknown Domain Detection Improved
- Topic Generation Functional
- Caption Generation Functional

Main Bottleneck:

Semantic Interpretation

---

# SCI Target Architecture

PDF
→ Retrieval
→ Semantic Document Profile
→ Business Angle Extraction
→ Narrative Planning
→ Caption Generation

---

# SCI Step 1

buildSemanticDocumentProfile()

Output:

- coreMeaning
- operationalProblems
- businessConsequences
- strategicBenefits
- targetAudience
- urgencySignals
- transformationGoals

---

# SCI Step 2

extractBusinessAngles()

Output:

Prioritized business angles.

---

# SCI Step 3

buildNarrativePlan()

Output:

- Hook
- Problem
- Insight
- Implication
- Soft Solution

---

# SCI Step 4

generateCaption()

Output:

- LinkedIn Caption
- Human-Natural Narrative
- Business-Oriented Content

---

# Future Architecture

PDF
→ Audit
→ OCR
→ Markdown
→ Clean Corpus
→ Metadata
→ Knowledge Layer
→ RAG
→ SCI
→ Agentic AI
→ Content Output

---

# Long-Term Vision

LLM
+
Corpus RAG
+
SCI
+
Agentic AI
+
MCP-like Integration Layer