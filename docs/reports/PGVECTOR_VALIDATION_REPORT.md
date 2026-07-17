# pgvector Validation Report

Date: 2026-05-26

## Status

PASS for code and migration validation. Live PostgreSQL execution is still required for production certification.

## Extension Validation

Migration files declare the real PostgreSQL extension name:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This matches pgvector's PostgreSQL extension name. The architecture document wording references `pgvector`, but the executable extension name is `vector`.

## Dimension Validation

The schema defines:

```sql
embedding_vector vector(1536)
```

The ORM defines `VectorType(1536)`, and `VectorStoreService` now validates embedding length before writes and similarity queries. Wrong-dimension vectors raise `ValueError`.

## Index Validation

Migrations define cosine search support:

```sql
USING ivfflat (embedding_vector vector_cosine_ops)
```

## Similarity Query Validation

The production vector query now uses the pgvector cosine-distance operator:

```sql
embedding_vector <=> CAST(:query_vector AS vector)
```

Similarity is returned as:

```sql
1 - (embedding_vector <=> CAST(:query_vector AS vector))
```

The previous invalid `func.cosine_distance(...)` path was removed from backend services. Topic search delegates through `VectorStoreService` so there is one query implementation to validate.

## Test Coverage

- Static migration validation confirms extension, `vector(1536)`, and `vector_cosine_ops`.
- Static service validation confirms `<=>` and rejects `cosine_distance`.
- Unit validation confirms incorrect embedding dimensions are rejected.
- SQLite dev fallback still performs cosine similarity in Python for local smoke tests only.

## Remaining Production Work

- Run a real PostgreSQL/Supabase integration test that inserts 1536-dimension vectors and performs a similarity search.
- Confirm ivfflat index creation succeeds after enough rows are present, or tune index settings for the expected corpus size.
- Confirm retrieval plans use this same service during Sprint 4 rather than adding another vector query path.
