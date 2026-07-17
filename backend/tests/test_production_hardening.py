import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("USE_SQLITE_DEV", "1")

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config.settings import Settings
from services.vector_store_service import VectorStoreService


def test_env_example_contains_no_real_looking_secrets():
    content = (BACKEND_DIR / ".env.example").read_text(encoding="utf-8")

    forbidden_fragments = [
        "sk-proj-",
        "AIza",
        "eyJhbGci",
        "uuiarqclhsrridlfvlin",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in content

    required_names = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_JWT_SECRET",
        "SUPABASE_JWT_AUDIENCE",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
    ]
    for name in required_names:
        assert f"{name}=" in content


def test_production_settings_fail_when_required_values_are_missing(monkeypatch):
    for name in [
        "USE_SQLITE_DEV",
        "DATABASE_URL",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_JWT_SECRET",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
    ]:
        monkeypatch.delenv(name, raising=False)

    production_settings = Settings(_env_file=None)

    with pytest.raises(RuntimeError, match="Missing required production environment variables"):
        production_settings.validate_production_requirements()


def test_migrations_do_not_drop_production_tables():
    migration_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((BACKEND_DIR / "migrations").glob("*.sql"))
    ).upper()

    assert "DROP TABLE" not in migration_text
    assert "DROP SCHEMA" not in migration_text
    assert "DROP DATABASE" not in migration_text


def test_pgvector_schema_and_query_operator_are_declared():
    migration_text = (BACKEND_DIR / "migrations" / "001_init_database.sql").read_text(encoding="utf-8")
    vector_service = (BACKEND_DIR / "services" / "vector_store_service.py").read_text(encoding="utf-8")
    service_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((BACKEND_DIR / "services").glob("*.py"))
    )

    assert "CREATE EXTENSION IF NOT EXISTS vector" in migration_text
    assert "embedding_vector vector(1536)" in migration_text
    assert "vector_cosine_ops" in migration_text
    assert "<=>" in vector_service
    assert "CAST(:query_vector AS vector)" in vector_service
    assert "cosine_distance" not in service_text


def test_embedding_dimension_validation_rejects_wrong_size():
    with pytest.raises(ValueError, match="1536 dimensions"):
        VectorStoreService._validate_embedding_dimension([0.1, 0.2, 0.3])
