"""
Retrieval pipeline tests — adapted for current file-based content engine.
"""
import os
import sys
from pathlib import Path
import json
import uuid

os.environ.setdefault("USE_SQLITE_DEV", "1")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes_content import UPLOAD_DIR


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def _seed_doc(document_id: str, text: str = "Acme Alert Platform provides real-time incident notification workflows, encrypted alert routing, audit logs, SLA monitoring, API integration, and 99.9% delivery tracking for infrastructure operations teams."):
    """Seed a document in file-based storage."""
    doc_dir = UPLOAD_DIR
    doc_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": document_id,
        "filename": "owned.pdf",
        "text_length": len(text),
        "text": text,
        "topics": [
            {"title": "enterprise alerting reliability", "angle": "How Acme ensures uptime", "key_points": ["SLA monitoring", "99.9% delivery"]},
            {"title": "Automating Critical Notification Workflows", "angle": "Streamline ops", "key_points": ["alert routing", "audit logs"]},
            {"title": "Operational Compliance Guide", "angle": "Meeting compliance", "key_points": ["audit logs", "encrypted routing"]},
        ]
    }
    (doc_dir / f"{document_id}.json").write_text(json.dumps(meta, indent=2))
    return meta


def test_generate_caption_returns_prepared_draft(client):
    """Test caption generation returns caption and hashtags."""
    doc_id = str(uuid.uuid4())
    _seed_doc(doc_id)

    response = client.post(
        "/api/v1/content/generate-caption",
        json={"document_id": doc_id, "topic": "enterprise alerting reliability"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "caption" in body["data"]
    assert "hashtags" in body["data"]
    assert body["data"]["caption"]
    assert len(body["data"]["hashtags"]) > 0


def test_generate_caption_document_not_found_returns_404(client):
    """Test caption generation with non-existent document returns 404."""
    response = client.post(
        "/api/v1/content/generate-caption",
        json={"document_id": str(uuid.uuid4()), "topic": "test"},
    )

    assert response.status_code == 404
    body = response.json()
    detail = body.get("detail", body)
    assert detail["error_code"] == "DOCUMENT_NOT_FOUND"


def test_generate_caption_missing_fields_returns_400(client):
    """Test caption generation with missing fields returns 400."""
    response = client.post(
        "/api/v1/content/generate-caption",
        json={"document_id": str(uuid.uuid4())},
    )

    assert response.status_code == 400
    body = response.json()
    detail = body.get("detail", body)
    assert detail["error_code"] == "MISSING_FIELDS"


def test_generate_caption_returns_cleaned_caption(client):
    """Test that caption generation removes RAG noise markers."""
    doc_id = str(uuid.uuid4())
    text = (
        "[Page 1] Acme Security Gateway includes Router, Intelligent Switch, Firewall, and IPS controls. "
        "Contact info@sendquick.com or visit https://example.test for unrelated details."
    )
    _seed_doc(doc_id, text=text)

    response = client.post(
        "/api/v1/content/generate-caption",
        json={"document_id": doc_id, "topic": "Operational Compliance Guide", "language": "en"},
    )

    assert response.status_code == 200
    body = response.json()
    caption = body["data"]["caption"]

    # Should not contain RAG noise markers like page indicators
    assert "[Page 1]" not in caption

    # Hashtags should be present (current implementation returns hashtags)
    assert body["data"]["hashtags"]
