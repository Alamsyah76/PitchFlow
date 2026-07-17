#!/bin/bash

# ================================================================================
# Backend Startup Script for AI Marketing Content Engine
# ================================================================================

set -e

echo "======================================"
echo "AI Marketing Content Engine - Backend"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure your settings:"
    echo "  cp .env.example .env"
    exit 1
fi

echo -e "${GREEN}✓${NC} .env file found"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

if [ "$(echo \"$PYTHON_VERSION < 3.9\" | bc)" -eq 1 ]; then
    echo -e "${RED}Error: Python 3.9+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Check if Supabase is configured
if grep -q "SUPABASE_URL=https://" .env; then
    echo -e "${GREEN}✓${NC} Supabase configuration found"
else
    echo -e "${YELLOW}⚠${NC} Supabase not configured - vector storage may not work"
fi

# Check if OpenAI API key is configured
if grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${GREEN}✓${NC} OpenAI API key configured"
else
    echo -e "${YELLOW}⚠${NC} OpenAI not configured - will use Ollama if available"
fi

# Display startup info
echo ""
echo "======================================"
echo "Backend Configuration:"
echo "======================================"
grep -E "^API_|^VECTOR_|^LOG_" .env | grep -v "KEY\|SECRET" || true
echo ""

# Start the FastAPI server
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn app.main:app \
    --host $(grep "API_HOST=" .env | cut -d= -f2) \
    --port $(grep "API_PORT=" .env | cut -d= -f2) \
    --reload \
    --log-level $(grep "LOG_LEVEL=" .env | cut -d= -f2 | tr '[:upper:]' '[:lower:]')
