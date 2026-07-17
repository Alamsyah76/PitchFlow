"""Content Engine API — Upload → Topics → Content + Hashtags → Carousel"""
import os
import json
import uuid
import PyPDF2
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from openai import OpenAI

from app.content_engine.topic_generator import generate_topics
from app.content_engine.content_writer import generate_caption
from app.rate_limit import check_konten_limit, increment_konten, check_image_limit, increment_image

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/content", tags=["Content Engine"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "storage" / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _extract_pdf_text(filepath: Path) -> str:
    """Extract text from PDF — fallback OCR jika text-based gagal"""
    # Try PyPDF2 first
    text = ""
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n\n"
        text = text.strip()
    except Exception:
        text = ""

    # If too little text, try OCR
    if len(text) < 50:
        try:
            import fitz  # PyMuPDF — no external deps
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            import os
            os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

            doc = fitz.open(str(filepath))
            ocr_texts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Render page ke image (300 DPI)
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                # Simpan sementara dan OCR
                import tempfile, pathlib
                tmp = pathlib.Path(tempfile.mktemp(suffix=".png"))
                tmp.write_bytes(img_bytes)
                from PIL import Image
                t = pytesseract.image_to_string(Image.open(str(tmp)), lang="eng+ind")
                tmp.unlink()
                if t.strip():
                    ocr_texts.append(t.strip())
            doc.close()
            text = "\n\n".join(ocr_texts)
            logger.info(f"OCR used: {len(ocr_texts)} pages, {len(text)} chars extracted")
        except Exception as e:
            logger.warning(f"OCR fallback failed: {e}")
            import traceback
            logger.warning(traceback.format_exc())

    return text.strip()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF → extract text → siapkan untuk topic generation"""
    filename = (file.filename or "").lower()
    if filename and not filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    doc_id = str(uuid.uuid4())
    filepath = UPLOAD_DIR / f"{doc_id}.pdf"

    content = await file.read()
    filepath.write_bytes(content)

    text = _extract_pdf_text(filepath)

    if not text or len(text) < 50:
        raise HTTPException(400, "Could not extract sufficient text from PDF")

    # Simpan metadata
    meta = {"id": doc_id, "filename": file.filename, "text_length": len(text), "text": text}
    (UPLOAD_DIR / f"{doc_id}.json").write_text(json.dumps(meta, indent=2))

    # RAG pipeline: chunk → embed → simpan
    from app.content_engine.rag import process_document
    rag_data = process_document(text, doc_id, UPLOAD_DIR)
    chunk_count = len(rag_data["chunks"])
    logger.info(f"RAG: {chunk_count} chunks with embeddings for {doc_id}")

    return {
        "success": True,
        "data": {
            "document_id": doc_id,
            "id": doc_id,
            "filename": file.filename,
            "pages": text.count("\n\n") + 1,
            "text_length": len(text),
            "chunks": chunk_count,
        }
    }


@router.get("/topics")
async def get_topics(document_id: str, lang: str = "id"):
    """Generate 2 topic angles from document"""
    meta_path = UPLOAD_DIR / f"{document_id}.json"
    if not meta_path.exists():
        raise HTTPException(404, "Document not found")

    meta = json.loads(meta_path.read_text())
    text = meta["text"]
    filename = meta["filename"]

    try:
        topics = generate_topics(text, filename, doc_id=document_id, store_dir=UPLOAD_DIR)
        # Simpan topics ke metadata
        meta["topics"] = topics
        meta_path.write_text(json.dumps(meta, indent=2))

        return {"success": True, "data": {"topics": topics}}
    except Exception as e:
        raise HTTPException(500, f"Topic generation failed: {str(e)}")


@router.post("/generate-caption")
async def generate_caption_endpoint(payload: dict):
    """Generate LinkedIn caption + hashtags from selected topic"""
    document_id = payload.get("document_id") or payload.get("documentId")
    raw_topic = payload.get("topic") or payload.get("selected_topic") or ""

    # Topic bisa berupa string atau object (TopicCardItem)
    if isinstance(raw_topic, dict):
        topic_title = raw_topic.get("title", "")
        topic_detail = raw_topic
    else:
        topic_title = str(raw_topic)
        topic_detail = {"title": topic_title, "angle": "", "key_points": []}

    if not document_id or not topic_title:
        raise HTTPException(400, "document_id and topic are required")

    # Rate limit konten
    kc = check_konten_limit()
    if not kc["allowed"]:
        raise HTTPException(429, f"Batas konten bulan ini sudah habis ({kc['used']}/{kc['limit']}). Upgrade tier untuk lanjut.")

    meta_path = UPLOAD_DIR / f"{document_id}.json"
    if not meta_path.exists():
        raise HTTPException(404, "Document not found")

    meta = json.loads(meta_path.read_text())
    text = meta["text"]
    filename = meta["filename"]

    # Cari topic detail dari metadata jika ada
    for t in meta.get("topics", []):
        if t.get("title") == topic_title or topic_title in t.get("title", ""):
            topic_detail = t
            break

    try:
        result = generate_caption(text, filename, topic_detail, doc_id=document_id, store_dir=UPLOAD_DIR)
        increment_konten()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(500, f"Caption generation failed: {str(e)}")


@router.post("/generate-carousel")
async def generate_carousel(payload: dict):
    """Generate image with text overlay from content"""
    document_id = payload.get("document_id")
    topic = payload.get("topic") or payload.get("selected_topic", "")
    caption = payload.get("caption", "")
    hashtags = payload.get("hashtags", [])

    if not caption:
        raise HTTPException(400, "caption is required")

    # Rate limit image
    ic = check_image_limit()
    if not ic["allowed"]:
        raise HTTPException(429, f"Batas image bulan ini sudah habis. Di Free tier hanya 1x trial image.")

    from app.content_engine.image_gen import generate_carousel_storytelling, generate_image

    topic_title = topic if isinstance(topic, str) else topic.get("title", "")

    try:
        result = generate_image(topic_title, caption, hashtags)
        increment_image()
        return {"success": True, "data": {"image_url": result["image_url"]}}
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(500, detail=str(e))


@router.post("/download-zip")
async def download_zip(payload: dict):
    """Download topic, content, hashtags, and image as ZIP"""
    import tempfile, zipfile, shutil
    from pathlib import Path

    topic = payload.get("topic", "")
    caption = payload.get("caption", "")
    hashtags = payload.get("hashtags", [])
    image_path = payload.get("image_path", "")

    topic_title = topic if isinstance(topic, str) else topic.get("title", "")

    # Buat temp folder
    tmp = Path(tempfile.mkdtemp())

    # Topic
    (tmp / "topic.txt").write_text(topic_title, encoding="utf-8")

    # Content + hashtags
    content_text = caption
    if hashtags:
        content_text += "\n\n" + " ".join(hashtags)
    (tmp / "content.txt").write_text(content_text, encoding="utf-8")

    # Image
    if image_path and Path(image_path).exists():
        shutil.copy2(image_path, tmp / "image.jpg")
    elif image_path and image_path.startswith("/storage/"):
        # From URL path
        src = Path(__file__).resolve().parent.parent / image_path.lstrip("/")
        if src.exists():
            shutil.copy2(src, tmp / "image.jpg")

    # ZIP
    zip_path = tmp / "export.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in tmp.iterdir():
            if f.name != "export.zip":
                zf.write(f, f.name)

    # Baca ZIP dan return
    zip_bytes = zip_path.read_bytes()

    # Cleanup
    shutil.rmtree(tmp)

    from fastapi.responses import Response
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={topic_title[:30]}.zip"}
    )
