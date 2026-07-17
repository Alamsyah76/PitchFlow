"""
Main FastAPI Application
Entry point for the backend service
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import sys

from config.settings import get_environment_loading_status, settings
from models.database import DatabaseConnection
from services.embedding_service import EmbeddingService
from utils.logger import get_logger
from app.routes_content import router as content_router
from app.routes_chatbot import router as chatbot_router
from app.routes_plan import router as plan_router
from app.routes_auth import router as auth_router
from app.routes_library import router as library_router
from app.routes_profile import router as profile_router

# Email Campaign routes (merged from Email Campaign project)
from app.routes import router as email_campaign_router

# Init database
from app.database import init_db
init_db()

# Migrasi data dari JSON ke SQLite (satu kali)
try:
    from app.database import get_db, upsert_user
    import json
    from pathlib import Path
    home_dir = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    
    # Migrasi users
    users_file = home_dir / "pitchflow_users.json"
    if users_file.exists():
        users_data = json.loads(users_file.read_text())
        for email, data in users_data.items():
            if isinstance(data, dict):
                upsert_user(email, data.get("name", ""), data.get("tier", "free"))
                # Migrasi avatar
                if data.get("avatar"):
                    db = get_db()
                    db.execute("UPDATE users SET avatar=? WHERE email=?", (data["avatar"], email))
                    db.commit()
        print(f"[DB] Migrated {len(users_data)} users from JSON")
    
    # Migrasi sender settings
    sender_file = home_dir / "pitchflow_sender.json"
    if sender_file.exists():
        sd = json.loads(sender_file.read_text())
        if sd:
            from app.database import save_sender_settings
            save_sender_settings(sd.get("name", ""), sd.get("email", ""), sd.get("company", ""), sd.get("logo_b64", ""))
            print("[DB] Migrated sender settings")
except Exception as e:
    print(f"[DB] Migration note: {e}")
from app.image_storytelling.route_image_storytelling import router as image_storytelling_router
from app.image_generation.route_image_generation import router as image_generation_router

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Marketing Content Engine - Backend API",
    description="FastAPI backend for PDF ingestion, semantic chunking, and vector embedding",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# === Middleware Setup ===

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3060",
        "http://localhost:3070",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "https://pitchflow.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
        return response
    except Exception as e:
        import traceback
        logger.error(f"Request error: {e}\n{traceback.format_exc()}")
        # Ensure CORS headers are present on error responses so browser clients
        # receive the Access-Control-Allow-Origin header during failures.
        headers = {}
        try:
            if settings and getattr(settings, "cors_origins", None):
                origins = settings.cors_origins.split(",")
                headers["Access-Control-Allow-Origin"] = origins[0].strip() if origins else "*"
                headers["Access-Control-Allow-Credentials"] = "true"
        except Exception:
            headers["Access-Control-Allow-Origin"] = "*"

        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
            headers=headers,
        )


# === Event Handlers ===

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up backend service...")
    env_status = get_environment_loading_status()
    print("ENV current working directory:", env_status["current_working_directory"])
    print("ENV file path being used:", env_status["env_files_loaded"])
    print("load_dotenv() executed =", str(env_status["load_dotenv_executed"]).lower())
    print("BaseSettings used =", str(env_status["base_settings_used"]).lower())
    print("SettingsConfigDict used =", str(env_status["settings_config_dict_used"]).lower())
    print("OPENAI_API_KEY loaded =", str(env_status["OPENAI_API_KEY_loaded"]).lower())
    print("GEMINI_API_KEY loaded =", str(env_status["GEMINI_API_KEY_loaded"]).lower())
    print("LLAMA_CLOUD_API_KEY loaded =", str(env_status["LLAMA_CLOUD_API_KEY_loaded"]).lower())
    sqlite_dev = bool(settings and settings.is_sqlite_dev()) or os.getenv("USE_SQLITE_DEV", "").lower() in ("1", "true", "yes")
    
    try:
        # Initialize database connection
        if settings and not sqlite_dev:
            settings.validate_production_requirements()

        db_initialized = DatabaseConnection.initialize()
        if not db_initialized:
            if sqlite_dev:
                logger.warning("Database initialization failed in USE_SQLITE_DEV mode; continuing with SQLite fallback")
            else:
                raise RuntimeError("Database connection initialization failed")
        else:
            logger.info("Database connection established")
        
        # Initialize embedding service
        EmbeddingService.initialize()
        logger.info("Embedding service initialized")
        
        logger.info("Backend service startup complete")
    
    except Exception as e:
        logger.error(f"Startup error: {e}")
        if sqlite_dev:
            logger.warning("USE_SQLITE_DEV mode is active; startup error did not terminate FastAPI")
            return
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down backend service...")
    
    try:
        DatabaseConnection.close_all()
        logger.info("Database connections closed")
    
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# === Static Files ===
from fastapi.staticfiles import StaticFiles
from pathlib import Path
storage_path = Path(__file__).resolve().parent.parent / "storage"
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# === API Routes ===

# Register content routes
app.include_router(content_router)
app.include_router(chatbot_router)
app.include_router(plan_router)
app.include_router(auth_router)
app.include_router(library_router)
app.include_router(profile_router)
# Register image storytelling route
app.include_router(image_storytelling_router)
# Register image generation route (stateless proxy, no prompt modification)
app.include_router(image_generation_router)
# Register email campaign routes
app.include_router(email_campaign_router)


# === Health Check Endpoints ===

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "AI Marketing Content Engine Backend"}


@app.get("/api/health")
async def api_health_check():
    """API health check with version info"""
    return {
        "status": "healthy",
        "service": "AI Marketing Content Engine",
        "version": "1.0.0",
        "embedding_model": settings.vector_embedding_model if settings else "unknown",
        "vector_dimension": settings.vector_dimension if settings else 0
    }


# === Root Endpoint ===

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": "AI Marketing Content Engine - Backend API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_health": "/api/health",
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "upload": "POST /api/v1/content/upload"
        }
    }


# === Error Handlers ===

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "error_message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    if settings:
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower()
        )
    else:
        logger.error("Cannot start application - settings not configured")
        sys.exit(1)
