"""Vercel Serverless entry point for FastAPI backend"""
import os, sys

# Project root is parent of api/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from app.main import app

handler = Mangum(app)
