"""API routes for web scraper"""
import logging
import sys
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parents[3]
EMAIL_DIR = PROJECT_ROOT / "email_campaign"
MODULES_DIR = EMAIL_DIR / "modules"
if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

from scraper import (
    list_products as _list_products,
    scrape_product as _scrape_product,
    list_blog_posts as _list_blog_posts,
    scrape_blog_post as _scrape_blog_post,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["Scraper"])


class ScrapeRequest(BaseModel):
    url: str


@router.get("/products")
async def list_products():
    """List known product pages (sendquick.com)"""
    try:
        products = _list_products()
        return {"success": True, "data": {"products": products}}
    except Exception as e:
        logger.error(f"list_products failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/product")
async def scrape_product(req: ScrapeRequest):
    """Scrape a product page from sendquick.com"""
    try:
        data = _scrape_product(str(req.url))
        if not data.get("title"):
            raise HTTPException(status_code=404, detail="Could not scrape product page")
        return {"success": True, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"scrape_product failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blog")
async def list_blog():
    """List recent blog posts from sendquick.com blog"""
    try:
        posts = _list_blog_posts()
        return {"success": True, "data": {"posts": posts}}
    except Exception as e:
        logger.error(f"list_blog failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blog-post")
async def scrape_blog_post(req: ScrapeRequest):
    """Scrape a single blog post and return content"""
    try:
        data = _scrape_blog_post(str(req.url))
        if not data.get("title"):
            raise HTTPException(status_code=404, detail="Could not scrape blog post")
        return {"success": True, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"scrape_blog_post failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
