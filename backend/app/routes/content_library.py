"""Content Library API — upload, list, delete files"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from modules.content_library import list_files, delete_file, CATEGORIES, LIBRARY_DIR

router = APIRouter(prefix="", tags=["Content Library"])

ALLOWED_EXT = {".pdf", ".docx", ".pptx", ".xlsx", ".jpg", ".jpeg", ".png", ".mp4"}

@router.get("/content-library")
async def get_content_library(category: str = ""):
    """List files in content library, optionally filtered by category"""
    return {"success": True, "data": {
        "categories": CATEGORIES,
        "files": list_files(category),
    }}

@router.post("/content-library/upload")
async def upload_content_file(file: UploadFile = File(...), category: str = "brochures"):
    """Upload a file to content library"""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXT)}")
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Category '{category}' not found. Available: {', '.join(CATEGORIES.keys())}")

    content = await file.read()
    save_path = LIBRARY_DIR / category / file.filename
    save_path.write_bytes(content)

    return {
        "success": True,
        "data": {
            "name": file.filename,
            "category": category,
            "size": len(content),
            "path": str(save_path.relative_to(LIBRARY_DIR)),
        },
    }

@router.delete("/content-library/{category}/{filename}")
async def delete_content_file(category: str, filename: str):
    """Delete a file from content library"""
    ok = delete_file(category, filename)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True, "message": f"Deleted {filename}"}
