import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid

os.environ.setdefault("USE_SQLITE_DEV", "1")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from config.settings import settings
from models.database import Base, Content, Document, User, VectorStore, get_db
from services.document_service import DocumentPageLimitExceeded
from utils.pdf_extractor import PDFExtractor, PDFTextExtractionFailed

JWT_SECRET = "test-supabase-jwt-secret"
AUDIENCE = "authenticated"
DEV_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    settings.supabase_jwt_secret = JWT_SECRET
    settings.supabase_jwt_audience = AUDIENCE

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def make_token(user_id: uuid.UUID, *, expires_delta: timedelta = timedelta(minutes=30), secret: str = JWT_SECRET):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": f"{user_id}@example.test",
        "aud": AUDIENCE,
        "role": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def auth_header(user_id: uuid.UUID, **kwargs):
    return {"Authorization": f"Bearer {make_token(user_id, **kwargs)}"}


def seed_user(db_session, user_id: uuid.UUID):
    user = User(id=user_id, email=f"{user_id}@example.test")
    db_session.add(user)
    db_session.commit()
    return user


def seed_document(db_session, user_id: uuid.UUID, file_name: str = "owned.pdf"):
    seed_user(db_session, user_id)
    document = Document(
        id=uuid.uuid4(),
        user_id=user_id,
        file_name=file_name,
        total_pages=1,
        is_cached=False,
    )
    db_session.add(document)
    db_session.commit()
    return document


def seed_content(db_session, user_id: uuid.UUID):
    document = seed_document(db_session, user_id)
    content = Content(
        id=uuid.uuid4(),
        user_id=user_id,
        document_id=document.id,
        topic_selected="Owned topic",
        final_caption="Owned caption.",
        carousel_images_urls=[],
        validity_score=100,
        failed_propositions=[],
        language_output="en",
    )
    db_session.add(content)
    db_session.commit()
    return content


def test_valid_token_is_accepted_for_protected_endpoint(client):
    user_id = uuid.uuid4()
    files = {"file": ("note.txt", b"not a pdf", "text/plain")}

    response = client.post("/api/v1/content/upload", headers=auth_header(user_id), files=files)

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "INVALID_FILE_TYPE"


def test_sqlite_dev_upload_bypasses_invalid_token(client):
    files = {"file": ("note.txt", b"not a pdf", "text/plain")}

    response = client.post("/api/v1/content/upload", headers={"Authorization": "Bearer not-a-valid-token"}, files=files)

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "INVALID_FILE_TYPE"


def test_upload_rejects_pdf_over_development_page_limit(client, monkeypatch):
    async def reject_large_pdf(**kwargs):
        raise DocumentPageLimitExceeded("Dokumen melebihi batas maksimal pengembangan (Maksimal 10 Halaman).")

    monkeypatch.setattr("app.routes_content.DocumentService.process_large_file", reject_large_pdf)
    files = {"file": ("large.pdf", b"%PDF-1.4\nlarge", "application/pdf")}

    response = client.post("/api/v1/content/upload", headers={"Authorization": "Bearer not-a-valid-token"}, files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == {
        "success": False,
        "error_code": "DOCUMENT_PAGE_LIMIT_EXCEEDED",
        "error_message": "Dokumen melebihi batas maksimal pengembangan (Maksimal 10 Halaman).",
    }


def test_text_based_pdf_extraction_path_still_works(monkeypatch):
    class FakePage:
        def extract_text(self):
            return "Legal agreement obligations and payment terms."

    class FakeReader:
        def __init__(self, _file):
            self.pages = [FakePage()]

    monkeypatch.setattr("utils.pdf_extractor.PdfReader", FakeReader)
    text, total_pages = PDFExtractor.extract_all_text(b"%PDF-1.4\ntext")

    assert total_pages == 1
    assert "Legal agreement obligations" in text


def test_image_based_pdf_uses_ocr_fallback(monkeypatch):
    class EmptyPage:
        def extract_text(self):
            return ""

    class EmptyReader:
        def __init__(self, _file):
            self.pages = [EmptyPage()]

    monkeypatch.setattr("utils.pdf_extractor.PdfReader", EmptyReader)
    monkeypatch.setattr(
        "utils.pdf_extractor.PDFExtractor._extract_page_texts_with_ocr",
        staticmethod(lambda _pdf_bytes, total_pages=0: ["Digital sovereignty and resilience workflow."]),
    )

    text, total_pages = PDFExtractor.extract_all_text(b"%PDF-1.4\nimage")

    assert total_pages == 1
    assert "Digital sovereignty and resilience workflow" in text


def test_image_based_pdf_page_split_uses_ocr_fallback(monkeypatch):
    class EmptyPage:
        def extract_text(self):
            return ""

    class EmptyReader:
        def __init__(self, _file):
            self.pages = [EmptyPage()]

    monkeypatch.setattr("utils.pdf_extractor.PdfReader", EmptyReader)
    monkeypatch.setattr(
        "utils.pdf_extractor.PDFExtractor._extract_page_texts_with_ocr",
        staticmethod(lambda _pdf_bytes, total_pages=0: ["Digital sovereignty and resilience workflow."]),
    )

    modules = PDFExtractor.split_by_pages(b"%PDF-1.4\nimage", pages_per_module=5)

    assert len(modules) == 1
    assert "Digital sovereignty and resilience workflow." in modules[0]["content"]


def test_upload_returns_422_when_text_extraction_and_ocr_both_fail(client, monkeypatch):
    async def fail_extraction(**kwargs):
        raise PDFTextExtractionFailed("No text content extracted from PDF")

    monkeypatch.setattr("app.routes_content.DocumentService.process_large_file", fail_extraction)
    files = {"file": ("scan.pdf", b"%PDF-1.4\nscan", "application/pdf")}

    response = client.post("/api/v1/content/upload", headers={"Authorization": "Bearer not-a-valid-token"}, files=files)

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "success": False,
        "error_code": "PDF_TEXT_EXTRACTION_FAILED",
        "error_message": "No text content extracted from PDF",
    }


def test_sqlite_dev_topics_bypasses_invalid_token(client):
    response = client.get(
        f"/api/v1/content/topics?document_id={uuid.uuid4()}",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "DOCUMENT_NOT_FOUND"


def test_invalid_token_is_rejected(client):
    response = client.get(
        f"/api/v1/content/generate-carousel?content_id={uuid.uuid4()}",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["error_code"] == "INVALID_TOKEN"


def test_missing_token_is_rejected(client):
    response = client.get(f"/api/v1/content/generate-carousel?content_id={uuid.uuid4()}")

    assert response.status_code == 401
    assert response.json()["detail"]["error_code"] == "AUTH_REQUIRED"


def test_expired_token_is_rejected(client):
    user_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/content/generate-carousel?content_id={uuid.uuid4()}",
        headers=auth_header(user_id, expires_delta=timedelta(minutes=-1)),
    )

    assert response.status_code == 401
    assert response.json()["detail"]["error_code"] == "TOKEN_EXPIRED"


def seed_chunk(db_session, document_id: uuid.UUID):
    chunk = VectorStore(
        id=uuid.uuid4(),
        document_id=document_id,
        module_chunk_id=1,
        chunk_content="SendQuick-Conversa provides encrypted operational messaging for audit-ready B2B teams.",
        embedding_vector=[0.0] * 1536,
        metadata_json={"source": "test"},
    )
    db_session.add(chunk)
    db_session.commit()
    return chunk


def test_sqlite_dev_document_owner_receives_dynamic_topics(client, db_session, monkeypatch):
    owner_id = DEV_USER_ID
    document = seed_document(db_session, owner_id)
    seed_chunk(db_session, document.id)

    class FakeOllamaResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "response": (
                    '[{"topic":"Encrypted messaging for audit-ready B2B teams","audience":"Compliance Officer"},'
                    '{"topic":"Reducing operational communication risk with SendQuick-Conversa","audience":"IT Manager"},'
                    '{"topic":"Centralized message governance for compliance officers","audience":"Compliance Officer"}]'
                )
            }

    async def fake_post(self, url, json):
        assert url.endswith("/api/generate")
        assert "SendQuick-Conversa" in json["prompt"]
        return FakeOllamaResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    response = client.get(f"/api/v1/content/topics?document_id={document.id}", headers=auth_header(owner_id))

    body = response.json()
    assert response.status_code == 200
    assert len(body["topics"]) == 3
    assert body["topics"][0] == {
        "topic": "Encrypted messaging for audit-ready B2B teams",
        "audience": "Compliance Officer",
    }


def test_sqlite_dev_topics_fallback_uses_document_context_when_ollama_fails(client, db_session, monkeypatch):
    owner_id = DEV_USER_ID
    document = seed_document(db_session, owner_id, file_name="SendQuick-Alert-Plus.pdf")
    seed_chunk(db_session, document.id)

    async def fake_post(self, url, json):
        raise RuntimeError("model 'llama3' not found")

    monkeypatch.setattr("httpx.AsyncClient.post", fake_post)

    response = client.get(f"/api/v1/content/topics?document_id={document.id}&lang=id", headers=auth_header(owner_id))

    body = response.json()
    assert response.status_code == 200
    assert len(body["topics"]) == 3
    for topic in body["topics"]:
        assert set(topic) == {"topic", "audience"}
        assert topic["topic"]
        assert topic["audience"]
        assert "Panduan Kepatuhan Operasional" not in topic["topic"]
        assert "Infrastruktur Bebas Gangguan" not in topic["topic"]


def test_cross_user_document_access_is_rejected(client, db_session):
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    document = seed_document(db_session, owner_id)

    response = client.get(f"/api/v1/content/topics?document_id={document.id}", headers=auth_header(attacker_id))

    assert response.status_code == 403
    assert response.json()["detail"]["error_code"] == "DOCUMENT_FORBIDDEN"


def test_cross_user_content_access_is_rejected(client, db_session):
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    content = seed_content(db_session, owner_id)

    response = client.get(f"/api/v1/content/generate-carousel?content_id={content.id}", headers=auth_header(attacker_id))

    assert response.status_code == 403
    assert response.json()["detail"]["error_code"] == "CONTENT_FORBIDDEN"
