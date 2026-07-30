import os
import sys
from pathlib import Path

os.environ.setdefault("USE_SQLITE_DEV", "1")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.main import app


def test_app_imports_and_required_routes_are_registered():
    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
    assert "/api/health" in route_paths
    assert "/api/v1/content/upload" in route_paths
    assert "/api/v1/content/topics" in route_paths
    assert "/api/v1/content/generate-caption" in route_paths
    assert "/api/v1/content/generate-carousel" in route_paths
    # /api/v1/content/search not yet implemented


def test_fastapi_startup_and_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
