-- ============================================================================
-- AI Marketing Semantic Content Engine - Initial Supabase Schema
-- Aligned with ARCHITECTURE_STACK.md
-- Date: 2026-05-26
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

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

-- 1.2 Documents Metadata Table (Large File Modularization Track)
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

-- pgvector search support
CREATE INDEX IF NOT EXISTS idx_vector_store_embedding_vector
    ON public.vector_store USING ivfflat (embedding_vector vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_hash ON public.documents(user_id, file_hash);
CREATE INDEX IF NOT EXISTS idx_vector_store_document_id ON public.vector_store(document_id);
CREATE INDEX IF NOT EXISTS idx_contents_user_id ON public.contents(user_id);
CREATE INDEX IF NOT EXISTS idx_contents_document_id ON public.contents(document_id);

-- Row-level security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vector_store ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contents ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_select_own ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY users_insert_own ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY users_update_own ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY documents_owner_all ON public.documents
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

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

CREATE POLICY contents_owner_all ON public.contents
    FOR ALL USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
