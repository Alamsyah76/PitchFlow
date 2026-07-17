import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import math
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
from models.database import Base, Document, User, VectorStore, get_db
from services.embedding_service import EmbeddingService
from services.reranker_service import DeterministicTestReranker

JWT_SECRET = "test-supabase-jwt-secret"
AUDIENCE = "authenticated"
VECTOR_DIMENSION = 1536
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
def client(db_session, monkeypatch):
    settings.supabase_jwt_secret = JWT_SECRET
    settings.supabase_jwt_audience = AUDIENCE

    async def fake_embed_text(_text):
        return [1.0] + [0.0] * (VECTOR_DIMENSION - 1)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    monkeypatch.setattr(EmbeddingService, "embed_text", staticmethod(fake_embed_text))
    monkeypatch.setattr(
        "services.retrieval_pipeline_service.get_reranker",
        lambda: DeterministicTestReranker(),
    )
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def make_token(user_id: uuid.UUID, *, expires_delta: timedelta = timedelta(minutes=30)):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": f"{user_id}@example.test",
        "aud": AUDIENCE,
        "role": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def auth_header(user_id: uuid.UUID):
    return {"Authorization": f"Bearer {make_token(user_id)}"}


def seed_user(db_session, user_id: uuid.UUID):
    user = User(id=user_id, email=f"{user_id}@example.test")
    db_session.add(user)
    db_session.commit()
    return user


def seed_document(db_session, user_id: uuid.UUID, file_name: str = "owned.pdf"):
    if db_session.query(User).filter(User.id == user_id).first() is None:
        seed_user(db_session, user_id)

    document = Document(
        id=uuid.uuid4(),
        user_id=user_id,
        file_name=file_name,
        total_pages=5,
        is_cached=True,
    )
    db_session.add(document)
    db_session.commit()
    return document


def unit_vector_with_similarity(score: float):
    score = max(0.0, min(1.0, score))
    second = math.sqrt(max(0.0, 1.0 - score * score))
    return [score, second] + [0.0] * (VECTOR_DIMENSION - 2)


def seed_chunks(db_session, document_id: uuid.UUID, count: int):
    for index in range(count):
        score = 0.99 - (index * 0.01)
        chunk = VectorStore(
            id=uuid.uuid4(),
            document_id=document_id,
            module_chunk_id=index + 1,
            chunk_content=(
                f"Acme Alert Platform module {index + 1} provides real-time incident notification workflows, "
                "encrypted alert routing, audit logs, SLA monitoring, API integration, and 99.9% delivery "
                "tracking for infrastructure operations teams."
            ),
            embedding_vector=unit_vector_with_similarity(score),
            metadata_json={
                "document_id": str(document_id),
                "module_id": index + 1,
                "chunk_index": index,
            },
        )
        db_session.add(chunk)
    db_session.commit()


def caption_payload(document_id: uuid.UUID, topic: str = "enterprise alerting reliability", language: str = "en"):
    return {
        "document_id": str(document_id),
        "topic": topic,
        "language": language,
        "target_audience": "CIO",
    }


def test_generate_caption_returns_sqlite_dev_prepared_draft(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    seed_chunks(db_session, document.id, 25)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id),
    )

    body = response.json()
    assert response.status_code == 200
    assert body["retrieval_count"] == 3
    assert body["ready_for_caption_generation"] is True
    assert body["final_caption"]
    assert body["caption"] == body["final_caption"]
    assert "Acme Alert Platform" in body["final_caption"]
    assert "#" not in body["final_caption"]
    assert body["validity_score"] == 98
    assert 3 <= len(body["hashtags"]) <= 5


def test_generate_caption_returns_top_3_dev_context_chunks(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    seed_chunks(db_session, document.id, 25)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id),
    )

    chunks = response.json()["top_3_context_chunks"]
    assert response.status_code == 200
    assert response.json()["rerank_method"] == "sqlite_dev_document_context"
    assert len(chunks) == 3
    assert [chunk["rank"] for chunk in chunks] == [1, 2, 3]
    assert [chunk["module_chunk_id"] for chunk in chunks] == [1, 2, 3]


def test_generate_caption_dev_user_is_document_owner_scoped(client, db_session):
    owner_id = DEV_USER_ID
    other_id = uuid.uuid4()
    owner_document = seed_document(db_session, owner_id, "owner.pdf")
    other_document = seed_document(db_session, other_id, "other.pdf")
    seed_chunks(db_session, owner_document.id, 25)
    seed_chunks(db_session, other_document.id, 25)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(owner_id),
        json=caption_payload(owner_document.id),
    )

    body = response.json()
    assert response.status_code == 200
    assert {chunk["document_id"] for chunk in body["top_3_context_chunks"]} == {str(owner_document.id)}


def test_generate_caption_empty_vector_store_returns_dev_draft(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id),
    )

    assert response.status_code == 200
    assert response.json()["final_caption"]


def test_generate_caption_document_not_found_returns_404(client):
    user_id = uuid.uuid4()

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(uuid.uuid4()),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "DOCUMENT_NOT_FOUND"


def test_generate_caption_sqlite_dev_bypasses_authorization(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)

    response = client.post(
        "/api/v1/content/generate-caption",
        json=caption_payload(document.id),
    )

    assert response.status_code == 200
    assert response.json()["rerank_method"] == "sqlite_dev_document_context"


def test_context_payload_shape(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    seed_chunks(db_session, document.id, 25)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id),
    )

    body = response.json()
    payload = body["context_payload"]
    first_chunk = payload["top_3_context_chunks"][0]

    assert payload["selected_topic"] == "enterprise alerting reliability"
    assert payload["language"] == "en"
    assert payload["target_audience"] == "IT Manager"
    assert payload["document"]["id"] == str(document.id)
    assert payload["document"]["file_name"] == "owned.pdf"
    assert body["final_caption"]
    assert body["hashtags"]
    assert set(first_chunk) == {
        "rank",
        "chunk_id",
        "document_id",
        "module_chunk_id",
        "content",
        "similarity_score",
        "rerank_score",
        "metadata",
    }


def test_generate_caption_topic_1_uses_notification_workflow_draft(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    seed_chunks(db_session, document.id, 3)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id, "Automating Critical Notification Workflows", language="id"),
    )

    caption = response.json()["final_caption"]
    assert response.status_code == 200
    assert not caption.startswith("Bagi ")
    assert "Acme Alert Platform" in caption
    assert "Seberapa besar risiko operasional" not in caption
    assert response.json()["target_audience"] == "IT Manager"


def test_generate_caption_topic_2_uses_operational_compliance_draft(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    seed_chunks(db_session, document.id, 3)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id, "Operational Compliance Guide", language="id"),
    )

    caption = response.json()["final_caption"]
    assert response.status_code == 200
    assert not caption.startswith("Bagi ")
    assert "Acme Alert Platform" in caption
    assert response.json()["target_audience"] == "Compliance Officer"


def test_generate_caption_topic_3_uses_resilient_infrastructure_draft(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    seed_chunks(db_session, document.id, 3)

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id, "Resilient Infrastructure & Reducing Downtime"),
    )

    caption = response.json()["final_caption"]
    assert response.status_code == 200
    assert not caption.startswith("For CIO")
    assert "Acme Alert Platform" in caption
    assert "What operational risk emerges" not in caption
    assert response.json()["target_audience"] == "CIO"


def test_generate_caption_cleans_rag_noise_from_caption_body(client, db_session):
    user_id = DEV_USER_ID
    document = seed_document(db_session, user_id)
    chunk = VectorStore(
        id=uuid.uuid4(),
        document_id=document.id,
        module_chunk_id=1,
        chunk_content=(
            "[Page 1] Acme Security Gateway includes Router, Intelligent Switch, Firewall, and IPS controls. "
            "Contact info@sendquick.com or visit https://example.test for unrelated details."
        ),
        embedding_vector=unit_vector_with_similarity(0.98),
        metadata_json={"chunk_index": 0},
    )
    db_session.add(chunk)
    db_session.commit()

    response = client.post(
        "/api/v1/content/generate-caption",
        headers=auth_header(user_id),
        json=caption_payload(document.id, "Operational Compliance Guide", language="en"),
    )

    body = response.json()
    caption = body["final_caption"]
    assert response.status_code == 200
    assert "info@sendquick.com" not in caption
    assert "https://example.test" not in caption
    assert "[Page 1]" not in caption
    assert "Router" in caption
    assert "Firewall" in caption
    assert "#" not in caption
    assert body["hashtags"]
