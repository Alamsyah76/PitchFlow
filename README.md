# AI Marketing Semantic Content Engine — RAG to LinkedIn Carousel

Dokumentasi ini menjelaskan arsitektur dan cara kerja sistem "RAG-to-LinkedIn-Carousel" (Retrieval-Augmented Generation → Carousel) beserta panduan singkat troubleshooting dan smoke-test otomatis.

## Gambaran Umum
Sistem ini mengambil dokumen sumber (PDF), memecahnya menjadi chunk semantik, menyimpan embedding ke vector store, lalu menggunakan LLM untuk menghasilkan caption (soft-selling) yang kemudian diaudit secara otomatis (validity score + failed propositions). Setelah caption final tervalidasi, sistem membangun carousel 3–5 slide berukuran 1080×1080 px, menempelkan logo brand, dan menyimpan gambar (Supabase Storage atau file lokal untuk dev).

## Alur Kerja (ringkas)
- Ingest: Upload PDF → ekstract teks (backend/utils/pdf_extractor.py)
- Chunking: Semantic chunker (topik-aware splitter) → top-3 chunks dipakai untuk konteks
- Embedding: `EmbeddingService` menyimpan embedding ke vector-store (pgvector di prod, fallback SQLite/dev)
- Generation: `Gemini 1.5 Flash` (atau LLM terkonfigurasi) menghasilkan caption; Linguistic Sensor melakukan rewrite loop untuk menghapus cliche/banned-propositions
- Auditing: Asynchronous auditor (OpenAI GPT-4o) mengembalikan JSON schema {"validity_score": float, "failed_propositions": [{sentence, reason}]}
- Carousel: `carousel_service` mem-parse caption → 3–5 slides → render image (Pillow) → upload ke Supabase Storage (atau folder `backend/carousel_output/` pada dev)

## Teknologi & Stack
- Backend: Python 3.11, FastAPI, Uvicorn, SQLAlchemy
- Vector store: `pgvector` (production) with SQLite fallback for local dev
- LLMs: Gemini (generation) + OpenAI GPT-4o (auditing) — abstracted behind service classes
- Indexing / tooling: `llama-index` (used for text splitting / helpers)
- Storage: Supabase (Storage + Postgres) — fallback filesystem for dev
- Image: Pillow (PIL) untuk merender slide 1080×1080
- Frontend: Next.js (React), TipTap editor, TailwindCSS, jsPDF untuk export

## Penghematan Token / Arsitektur Hemat Token
- Semantic Splitter: Memecah dokumen secara semantik sehingga hanya chunk relevan yang dikirim ke LLM (mengurangi prompt size)
- pgvector + Top-K Cutoff: Hanya ambil top-K (mis. top-3) chunk teratas untuk konteks
- Gemini Context Caching: Cache konteks prompt/response untuk dokumen yang sama sehingga LLM tidak diminta ulang untuk konteks yang tidak berubah

Fokusnya: minimize token per-request → mengurangi biaya dan latency.

## File Kunci Proyek
- Backend entry: [backend/app/main.py](backend/app/main.py)
- DB models & koneksi: [backend/models/database.py](backend/models/database.py)
- Caption generator + auditor: [backend/services/gemini_service.py](backend/services/gemini_service.py) dan [backend/services/auditor_service.py](backend/services/auditor_service.py)
- Carousel generator: [backend/services/carousel_service.py](backend/services/carousel_service.py)
- Integration script (dev): [backend/scripts/integration_generate_carousel.py](backend/scripts/integration_generate_carousel.py)
- Frontend: [frontend/pages/index.tsx](frontend/pages/index.tsx) dan komponen TipTap di [frontend/components/RichEditorTiptap.tsx](frontend/components/RichEditorTiptap.tsx)

## Troubleshooting Singkat

1) Validity Score < 95%
- Dampak: caption mengandung proposisi yang gagal audit; auditor mengembalikan `failed_propositions`.
- Langkah cepat:
  - Periksa field `failed_propositions` pada record `public.contents` (atau response API) untuk kalimat yang gagal dan alasan.
  - Jika banyak kesalahan format/tautologi: jalankan lagi endpoint `POST /api/v1/content/generate-caption` dengan parameter `rewrite=true` (jika tersedia) atau tambahkan instruksi yang lebih ketat pada prompt (tonal constraint, forbid-list).
  - Untuk masalah domain-knowledge (factual error): tambahkan referensi/quote dari chunk sumber atau kurangi temperature LLM.
  - Gunakan rekaman log auditor (`backend/services/auditor_service.py`) untuk melihat prompt auditor dan respons OpenAI.

2) Logo overlap / gambar logo menabrak margin di slide Carousel
- Penyebab umum: logo ukuran input terlalu besar atau aspect ratio tidak di-handle.
- Solusi cepat:
  - Pastikan `brand_logo_url` mengarah ke image yang proporsional; jika upload manual, gunakan PNG/SVG dengan padding transparan.
  - Di `backend/services/carousel_service.py`, ada fungsi `generate_slide_image` yang menempel logo; ubah ukuran maksimal logo (`max_logo_w`, `max_logo_h`) atau tambahkan `padding` di parameter brand.
  - Untuk dev: periksa file hasil di `backend/carousel_output/contents/<content_id>/` untuk debugging visual.

## Smoke Test Otomatis (cara pakai)
- File: [smoke_test.py](smoke_test.py)
- Cara jalankan (dari root project):
```powershell
.\backend\venv_py311\Scripts\Activate.ps1
python smoke_test.py
```
- Apa yang diperiksa:
  - Endpoint health (`/health`) backend
  - Ketersambungan ke Supabase (jika env `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` tersedia)

## Cara Pengembangan Singkat
- Backend: lihat [backend/requirements.txt](backend/requirements.txt) — setup venv dan `pip install -r requirements.txt`
- Frontend: `cd frontend && npm install && npm run dev`

## Catatan Penutup
Dokumentasi ini menutup alur pengembangan Sesi 1–6. Jika Anda ingin saya commit perubahan (`.gitignore`, `requirements.txt`, `README.md`, `smoke_test.py`) dan membuat tag release, saya bisa lanjutkan.

-- Tim Pengembang AI Marketing Semantic Content Engine
