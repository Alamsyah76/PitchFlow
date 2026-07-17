================================================================================
                    FILE: ARCHITECTURE_STACK.md (TEXT FORMAT)
================================================================================
Target Environment: Next.js (Frontend), FastAPI (Backend), Supabase (Database)
Database Engine   : PostgreSQL with pgvector extension Enabled
================================================================================

1. SUPABASE POSTGRESQL DATABASE SCHEMA (DDL SCRIPT BLUEPRINT)
--------------------------------------------------------------------------------
Codex must execute and enforce row-level security (RLS) matching these tables:

CREATE EXTENSION IF NOT EXISTS pgvector;

-- 1.1 Users & Brand Kit Settings Table
CREATE TABLE public.users (
    id UUID REFERENCES auth.users NOT NULL PRIMARY KEY,
    email TEXT NOT NULL,
    brand_color_primary VARCHAR(7) DEFAULT '#000000',
    brand_color_secondary VARCHAR(7) DEFAULT '#FFFFFF',
    brand_font_family TEXT DEFAULT 'Inter',
    brand_logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 1.2 Documents Metadata Table (Large File Modularization Track)
CREATE TABLE public.documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    file_name TEXT NOT NULL,
    total_pages INT NOT NULL,
    is_cached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 1.3 Modular Document Vector Chunks Table
CREATE TABLE public.vector_store (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    module_chunk_id INT NOT NULL, -- Penanda urutan bab/halaman modular
    chunk_content TEXT NOT NULL,
    embedding_vector vector(1536), -- Optimized for text-embedding-3-small dimensions
    metadata JSONB
);

-- 1.4 Generated Content & Audit Log Table
CREATE TABLE public.contents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    topic_selected TEXT NOT NULL,
    final_caption TEXT NOT NULL,
    carousel_images_urls TEXT[], -- Array path storage hasil visual slide
    validity_score NUMERIC(5,2) NOT NULL,
    failed_propositions JSONB, -- Menyimpan kalimat yang dilingkari kuning/salah fakta
    language_output VARCHAR(2) NOT NULL, -- 'en' atau 'id'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);


2. FASTAPI BACKEND ENDPOINTS STRUCTURAL ROUTING
--------------------------------------------------------------------------------
Codex must build async Python routing inside the `/api/v1` namespace:

2.1 POST /api/v1/content/upload
- Payload: `file: UploadFile` (PDF), Headers: `Authorization: Bearer <Token>`
- Logic: Memicu skrip modular chunking LlamaIndex. Simpan metadata ke `documents`, 
  lalu pecah teks menjadi vektor 1536-dimensi dan simpan ke `vector_store`.

2.2 GET /api/v1/content/topics?document_id={id}&lang={en|id}
- Logic: Panggil summary module bertingkat dari database. Kirim ke Gemini 1.5 Flash 
  menggunakan Context Caching untuk mengekstrak 3 topik murni tanpa membaca ulang PDF.

2.3 POST /api/v1/content/generate-caption
- Payload: `{ document_id: UUID, topic: TEXT, language: STR, target_audience: STR }`
- Logic:
  1. Jalankan semantic search di `vector_store` -> dapatkan 20 chunks mirip.
  2. Jalankan Cohere Rerank / BGE-Reranker -> saring menjadi TOP 3 CHUNKS terbaik.
  3. Kirim TOP 3 ke Gemini 1.5 Flash dengan sistem prompt Soft-selling & Anti-AI-ish.
  4. Kirim teks draf ke GPT-4o untuk kalkulasi skor validitas matematis (95% Rule).
  5. Kembalikan: teks caption, skor, dan koordinat kalimat yang salah (jika ada).

2.4 GET /api/v1/content/generate-carousel?content_id={id}
- Logic: Ambil poin penting dari `final_caption`. Gunakan library Python `Pillow` 
  atau canvas node serverless untuk menyusun 3-5 halaman gambar berekstensi PNG 
  berisi paduan warna hex, teks terstruktur, ikon visual, dan suntikan logo user.


3. CORE MIDDLEWARE CONSTRAINTS (TOKEN-SAVING RULES)
--------------------------------------------------------------------------------
- Sebelum eksekusi LLM API komersial, backend wajib melakukan kueri ke `vector_store`. 
  Jika `document_id` sudah memiliki record, dilarang melakukan proses embedding ulang.
- Script HTTP request ke Google Gemini API WAJIB menyertakan header konfigurasi 
  `cachedContent` untuk mengaktifkan retensi memori input jangka pendek (maks 30 menit).
================================================================================