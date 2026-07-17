# Schema Comparison Report

Date: 2026-05-26

Reference: `ARCHITECTURE_STACK.md`

## Summary

The backend database schema has been aligned to the four required tables:

- `public.users`
- `public.documents`
- `public.vector_store`
- `public.contents`

Fresh installs are covered by `backend/migrations/001_init_database.sql`.
Legacy databases are covered by `backend/migrations/002_align_architecture_stack.sql`.

## Table Comparison

### public.users

| Required column | Required type / constraint | Implemented |
| --- | --- | --- |
| `id` | `UUID REFERENCES auth.users NOT NULL PRIMARY KEY` | Yes in migration; ORM uses UUID with SQLite fallback |
| `email` | `TEXT NOT NULL` | Yes |
| `brand_color_primary` | `VARCHAR(7) DEFAULT '#000000'` | Yes |
| `brand_color_secondary` | `VARCHAR(7) DEFAULT '#FFFFFF'` | Yes |
| `brand_font_family` | `TEXT DEFAULT 'Inter'` | Yes |
| `brand_logo_url` | `TEXT` | Yes |
| `created_at` | `TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL` | Yes |

Removed legacy columns from fresh schema: `username`, `full_name`, `avatar_url`, `organization_id`, `role`, `is_active`, `updated_at`, `deleted_at`.

### public.documents

| Required column | Required type / constraint | Implemented |
| --- | --- | --- |
| `id` | `UUID DEFAULT gen_random_uuid() PRIMARY KEY` | Yes |
| `user_id` | `UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL` | Yes |
| `file_name` | `TEXT NOT NULL` | Yes |
| `total_pages` | `INT NOT NULL` | Yes |
| `is_cached` | `BOOLEAN DEFAULT FALSE` | Yes |
| `created_at` | `TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL` | Yes |

Removed legacy columns from fresh schema: `title`, `description`, `content`, `document_type`, `source_url`, `created_by`, `organization_id`, `status`, `word_count`, `language`, `metadata`, `updated_at`, `deleted_at`.

### public.vector_store

| Required column | Required type / constraint | Implemented |
| --- | --- | --- |
| `id` | `UUID DEFAULT gen_random_uuid() PRIMARY KEY` | Yes |
| `document_id` | `UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL` | Yes |
| `module_chunk_id` | `INT NOT NULL` | Yes |
| `chunk_content` | `TEXT NOT NULL` | Yes |
| `embedding_vector` | `vector(1536)` | Yes in migration; ORM uses pgvector type with SQLite fallback |
| `metadata` | `JSONB` | Yes; ORM attribute is `metadata_json` because `metadata` is reserved by SQLAlchemy |

Removed legacy columns from fresh schema: `chunk_index`, `chunk_text`, `embedding`, `created_at`, `updated_at`.

### public.contents

| Required column | Required type / constraint | Implemented |
| --- | --- | --- |
| `id` | `UUID DEFAULT gen_random_uuid() PRIMARY KEY` | Yes |
| `user_id` | `UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL` | Yes |
| `document_id` | `UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL` | Yes |
| `topic_selected` | `TEXT NOT NULL` | Yes |
| `final_caption` | `TEXT NOT NULL` | Yes |
| `carousel_images_urls` | `TEXT[]` | Yes in migration; ORM uses PostgreSQL `ARRAY(Text)` with SQLite fallback |
| `validity_score` | `NUMERIC(5,2) NOT NULL` | Yes |
| `failed_propositions` | `JSONB` | Yes |
| `language_output` | `VARCHAR(2) NOT NULL` | Yes |
| `created_at` | `TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL` | Yes |

Removed legacy columns from fresh schema: `title`, `content_type`, `content_text`, `embedding`, `relevance_score`, `source_chunk_ids`, `created_by`, `metadata`, `is_published`, `updated_at`, `deleted_at`.

## pgvector

`ARCHITECTURE_STACK.md` refers to the pgvector extension. The migration enables PostgreSQL/Supabase pgvector support using the actual extension identifier:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The required `embedding_vector vector(1536)` column is implemented.

## RLS

RLS is enabled on the four required tables. Owner-scoped policies are included for:

- user profile rows
- documents by `user_id`
- vector chunks through owning document
- contents by `user_id`

## ORM Notes

The ORM aligns with the required logical schema. It includes SQLite-compatible type fallbacks so local startup smoke tests remain runnable without Supabase.

The `public.vector_store.metadata` column is mapped as `VectorStore.metadata_json` in Python because `metadata` is a reserved SQLAlchemy declarative attribute.
