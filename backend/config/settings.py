"""
Backend Configuration Management
Loads environment variables and defines application settings
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field


SETTINGS_FILE = Path(__file__).resolve()
BACKEND_DIR = SETTINGS_FILE.parents[1]
PROJECT_ROOT = SETTINGS_FILE.parents[2]

ENV_FILE_CANDIDATES = [
    Path.cwd() / ".env",
    PROJECT_ROOT / ".env",
    BACKEND_DIR / ".env",
]
ENV_FILES_LOADED = []
LOAD_DOTENV_EXECUTED = False

for env_path in ENV_FILE_CANDIDATES:
    if env_path.exists() and env_path.is_file():
        load_dotenv(dotenv_path=env_path, override=False)
        ENV_FILES_LOADED.append(str(env_path))
        LOAD_DOTENV_EXECUTED = True


def get_environment_loading_status() -> dict:
    """Return non-secret environment loading diagnostics for startup logs."""
    return {
        "current_working_directory": os.getcwd(),
        "env_file_candidates": [str(path) for path in ENV_FILE_CANDIDATES],
        "env_files_loaded": list(ENV_FILES_LOADED),
        "load_dotenv_executed": LOAD_DOTENV_EXECUTED,
        "base_settings_used": True,
        "settings_config_dict_used": False,
        "OPENAI_API_KEY_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "GEMINI_API_KEY_loaded": bool(os.getenv("GEMINI_API_KEY")),
        "LLAMA_CLOUD_API_KEY_loaded": bool(os.getenv("LLAMA_CLOUD_API_KEY")),
    }


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === Runtime Mode ===
    use_sqlite_dev: bool = Field(default=False, alias="USE_SQLITE_DEV")

    # === Supabase Configuration ===
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_anon_key: Optional[str] = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_jwt_secret: Optional[str] = Field(default=None, alias="SUPABASE_JWT_SECRET")
    supabase_jwt_audience: str = Field(default="authenticated", alias="SUPABASE_JWT_AUDIENCE")

    # === OpenAI Configuration ===
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # === Google Gemini Configuration ===
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")

    # === LlamaCloud/LlamaParse Configuration ===
    llama_cloud_api_key: Optional[str] = Field(default=None, alias="LLAMA_CLOUD_API_KEY")

    # === Cohere Rerank Configuration ===
    cohere_api_key: Optional[str] = Field(default=None, alias="COHERE_API_KEY")
    cohere_rerank_model: str = Field(default="rerank-v3.5", alias="COHERE_RERANK_MODEL")
    
    # === FastAPI Configuration ===
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # === Vector Store Configuration ===
    vector_embedding_model: str = Field(default="text-embedding-3-small", alias="VECTOR_EMBEDDING_MODEL")
    vector_dimension: int = Field(default=1536, alias="VECTOR_DIMENSION")
    vector_similarity_top_k: int = Field(default=3, alias="VECTOR_SIMILARITY_TOP_K")
    
    # === Logging Configuration ===
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # === Database Configuration ===
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # === CORS Configuration ===
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000", 
        alias="CORS_ORIGINS"
    )
    
    # === File Processing Configuration ===
    max_file_size_mb: int = 100
    pdf_pages_per_module: int = 5  # Pages per module for large file processing
    chunk_size_tokens: int = 512
    chunk_overlap_percent: float = 0.10  # 10% overlap
    
    # === Embedding Configuration ===
    use_ollama: bool = Field(default=False, alias="USE_OLLAMA")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")
    ollama_chat_model: str = Field(default="llama3", alias="OLLAMA_CHAT_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    def is_sqlite_dev(self) -> bool:
        return bool(self.use_sqlite_dev) or os.getenv("USE_SQLITE_DEV", "").lower() in ("1", "true", "yes")

    def validate_production_requirements(self) -> None:
        """Fail fast when production-critical configuration is missing."""
        if self.is_sqlite_dev():
            return

        required = {
            "DATABASE_URL": self.database_url,
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_SERVICE_ROLE_KEY": self.supabase_service_role_key,
            "SUPABASE_ANON_KEY": self.supabase_anon_key,
            "SUPABASE_JWT_SECRET": self.supabase_jwt_secret,
            "OPENAI_API_KEY": self.openai_api_key,
            "GEMINI_API_KEY": self.gemini_api_key,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing required production environment variables: "
                + ", ".join(sorted(missing))
            )

        if not self.database_url.startswith(("postgresql://", "postgres://")):
            raise RuntimeError("DATABASE_URL must be a PostgreSQL connection string in production")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Initialize settings
settings = None
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Please ensure .env file is properly configured")
    settings = None

# If running in development mode, provide safe defaults so the app can start
# without production env vars (USE_SQLITE_DEV=1 enables this behavior).
if settings:
    if settings.is_sqlite_dev():
        if not settings.supabase_url:
            settings.supabase_url = "http://localhost:5432"
        if not settings.supabase_service_role_key:
            settings.supabase_service_role_key = "dev-service-role-key"
        if not settings.supabase_anon_key:
            settings.supabase_anon_key = "dev-anon-key"
        if not settings.supabase_jwt_secret:
            settings.supabase_jwt_secret = "dev-jwt-secret"
        if not settings.openai_api_key:
            settings.openai_api_key = "dev-openai-key"
        if not settings.gemini_api_key:
            settings.gemini_api_key = "dev-gemini-key"
        print("USE_SQLITE_DEV detected - applying development placeholder settings")
