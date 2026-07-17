-- ============================================================================
-- AI Marketing Semantic Content Engine - Safe Legacy Schema Alignment
-- Date: 2026-05-26
--
-- This migration is intentionally non-destructive:
-- - It does not DROP existing production tables.
-- - Incompatible legacy tables are renamed to timestamped backup tables.
-- - Fresh aligned tables are then created with the required architecture schema.
-- - Legacy data remains available for a controlled/manual backfill.
-- ============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

-- Rename incompatible legacy tables in dependency order. Aligned tables are left
-- untouched. Existing backup names abort the migration rather than overwriting.
DO $$
BEGIN
    IF to_regclass('public.contents') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.columns
           WHERE table_schema = 'public' AND table_name = 'contents' AND column_name = 'final_caption'
       )
    THEN
        IF to_regclass('public.legacy_contents_backup_20260526') IS NOT NULL THEN
            RAISE EXCEPTION 'Backup table public.legacy_contents_backup_20260526 already exists';
        END IF;
        ALTER TABLE public.contents RENAME TO legacy_contents_backup_20260526;
    END IF;

    IF to_regclass('public.vector_store') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.columns
           WHERE table_schema = 'public' AND table_name = 'vector_store' AND column_name = 'embedding_vector'
       )
    THEN
        IF to_regclass('public.legacy_vector_store_backup_20260526') IS NOT NULL THEN
            RAISE EXCEPTION 'Backup table public.legacy_vector_store_backup_20260526 already exists';
        END IF;
        ALTER TABLE public.vector_store RENAME TO legacy_vector_store_backup_20260526;
    END IF;

    IF to_regclass('public.documents') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.columns
           WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'file_name'
       )
    THEN
        IF to_regclass('public.legacy_documents_backup_20260526') IS NOT NULL THEN
            RAISE EXCEPTION 'Backup table public.legacy_documents_backup_20260526 already exists';
        END IF;
        ALTER TABLE public.documents RENAME TO legacy_documents_backup_20260526;
    END IF;

    IF to_regclass('public.users') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1 FROM information_schema.columns
           WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'brand_color_primary'
       )
    THEN
        IF to_regclass('public.legacy_users_backup_20260526') IS NOT NULL THEN
            RAISE EXCEPTION 'Backup table public.legacy_users_backup_20260526 already exists';
        END IF;
        ALTER TABLE public.users RENAME TO legacy_users_backup_20260526;
    END IF;
END $$;

-- 1.1 Users & Brand Kit Settings Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users NOT NULL PRIMARY KEY,
    email TEXT NOT NULL,
    brand_color_primary VARCHAR(7) DEFAULT '#000000',
    brand_color_secondary VARCHAR(7) DEFAULT '#FFFFFF',
    brand_font_family TEXT DEFAULT 'Inter',
    brand_logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 1.2 Documents Metadata Table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT,
    total_pages INT NOT NULL,
    is_cached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 1.3 Modular Document Vector Chunks Table
CREATE TABLE IF NOT EXISTS public.vector_store (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    module_chunk_id INT NOT NULL,
    chunk_content TEXT NOT NULL,
    embedding_vector vector(1536),
    metadata JSONB
);

-- 1.4 Generated Content & Audit Log Table
CREATE TABLE IF NOT EXISTS public.contents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    topic_selected TEXT NOT NULL,
    final_caption TEXT NOT NULL,
    carousel_images_urls TEXT[],
    validity_score NUMERIC(5,2) NOT NULL,
    failed_propositions JSONB,
    language_output VARCHAR(2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vector_store_embedding_vector
    ON public.vector_store USING ivfflat (embedding_vector vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_hash ON public.documents(user_id, file_hash);
CREATE INDEX IF NOT EXISTS idx_vector_store_document_id ON public.vector_store(document_id);
CREATE INDEX IF NOT EXISTS idx_contents_user_id ON public.contents(user_id);
CREATE INDEX IF NOT EXISTS idx_contents_document_id ON public.contents(document_id);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vector_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contents ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'users' AND policyname = 'users_select_own') THEN
        CREATE POLICY users_select_own ON public.users FOR SELECT USING (auth.uid() = id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'users' AND policyname = 'users_insert_own') THEN
        CREATE POLICY users_insert_own ON public.users FOR INSERT WITH CHECK (auth.uid() = id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'users' AND policyname = 'users_update_own') THEN
        CREATE POLICY users_update_own ON public.users FOR UPDATE USING (auth.uid() = id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'documents_owner_all') THEN
        CREATE POLICY documents_owner_all ON public.documents
            FOR ALL USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'vector_store' AND policyname = 'vector_store_owner_all') THEN
        CREATE POLICY vector_store_owner_all ON public.vector_store
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM public.documents d
                    WHERE d.id = vector_store.document_id
                    AND d.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM public.documents d
                    WHERE d.id = vector_store.document_id
                    AND d.user_id = auth.uid()
                )
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'contents' AND policyname = 'contents_owner_all') THEN
        CREATE POLICY contents_owner_all ON public.contents
            FOR ALL USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

COMMIT;
