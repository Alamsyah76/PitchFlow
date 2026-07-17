"""
Database model definitions aligned with ARCHITECTURE_STACK.md.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import JSON, TypeDecorator, UserDefinedType

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()

def is_sqlite_dev_mode() -> bool:
    """Return whether local SQLite development mode is enabled."""
    if settings and hasattr(settings, "is_sqlite_dev"):
        return settings.is_sqlite_dev()
    return os.environ.get("USE_SQLITE_DEV", "").lower() in ("1", "true", "yes")


class GUID(TypeDecorator):
    """PostgreSQL UUID with a SQLite string fallback."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class PGVector(UserDefinedType):
    """Minimal pgvector column type for vector(1536)."""

    cache_ok = True

    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    def get_col_spec(self, **_):
        return f"vector({self.dimensions})"


class VectorType(TypeDecorator):
    """pgvector in PostgreSQL, JSON-serialized text in SQLite."""

    impl = Text
    cache_ok = True

    def __init__(self, dimensions: int = 1536, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PGVector(self.dimensions))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            if isinstance(value, str):
                return value
            return "[" + ",".join(str(float(item)) for item in value) + "]"
        if isinstance(value, str):
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("[") and text.endswith("]"):
                return [float(item) for item in text.strip("[]").split(",") if item]
        return value


JSONB_TYPE = JSONB().with_variant(JSON(), "sqlite")
TEXT_ARRAY_TYPE = ARRAY(Text).with_variant(JSON(), "sqlite")


def utc_now():
    return datetime.now(timezone.utc)


def auth_user_foreign_key():
    database_url = getattr(settings, "database_url", None) if settings else None
    is_postgres = bool(database_url and database_url.startswith(("postgresql://", "postgres://")))
    if is_sqlite_dev_mode() or not is_postgres:
        return []
    return [ForeignKey("auth.users.id", link_to_name=True)]


class User(Base):
    """Users and brand kit settings table."""

    __tablename__ = "users"

    id = Column(GUID(), *auth_user_foreign_key(), primary_key=True, nullable=False)
    email = Column(Text, nullable=False)
    brand_color_primary = Column(String(7), default="#000000")
    brand_color_secondary = Column(String(7), default="#FFFFFF")
    brand_font_family = Column(Text, default="Inter")
    brand_logo_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"


class Document(Base):
    """Documents metadata table."""

    __tablename__ = "documents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(Text, nullable=False)
    file_hash = Column(String(64), nullable=True)
    total_pages = Column(Integer, nullable=False)
    is_cached = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    def __repr__(self):
        return f"<Document {self.file_name}>"


class VectorStore(Base):
    """Modular document vector chunks table."""

    __tablename__ = "vector_store"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    module_chunk_id = Column(Integer, nullable=False)
    chunk_content = Column(Text, nullable=False)
    embedding_vector = Column(VectorType(1536), nullable=True)
    metadata_json = Column(JSONB_TYPE, nullable=True)

    def __repr__(self):
        return f"<VectorStore module_{self.module_chunk_id}>"


class Content(Base):
    """Generated content and audit log table."""

    __tablename__ = "contents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    topic_selected = Column(Text, nullable=False)
    final_caption = Column(Text, nullable=False)
    carousel_images_urls = Column(TEXT_ARRAY_TYPE, nullable=True)
    validity_score = Column(Numeric(5, 2), nullable=False)
    failed_propositions = Column(JSONB_TYPE, nullable=True)
    language_output = Column(String(2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    def __repr__(self):
        return f"<Content {self.id}>"


class DatabaseConnection:
    """Database connection manager for Supabase PostgreSQL."""

    _engine = None
    _session_local = None

    @classmethod
    def initialize(cls):
        """Initialize database connection and create tables if needed."""
        try:
            if not settings:
                logger.error("Settings not configured properly")
                return False

            if is_sqlite_dev_mode():
                database_url = "sqlite:///./dev.db"
                logger.info("Using SQLite dev fallback database: ./dev.db")
            else:
                settings.validate_production_requirements()
                database_url = settings.database_url

            logger.info("Initializing database connection...")
            cls._engine = create_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
            )

            cls._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls._engine,
            )

            Base.metadata.create_all(bind=cls._engine)
            logger.info("Database connection established successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            return False

    @classmethod
    def get_session(cls):
        """Get a database session."""
        if cls._session_local is None:
            ok = cls.initialize()
            if not ok or cls._session_local is None:
                if not is_sqlite_dev_mode():
                    raise RuntimeError("Database session is unavailable in production mode")
                logger.warning("Initializing in-memory SQLite fallback session")
                engine = create_engine(
                    "sqlite:///:memory:",
                    echo=False,
                    pool_pre_ping=True,
                    connect_args={"check_same_thread": False},
                )
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                Base.metadata.create_all(bind=engine)
                cls._session_local = SessionLocal
        return cls._session_local()

    @classmethod
    def close_all(cls):
        """Close all database connections."""
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connections closed")


def get_db():
    """Dependency injection for FastAPI routes."""
    db = DatabaseConnection.get_session()
    try:
        yield db
    finally:
        db.close()
