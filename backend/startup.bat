@echo off
REM ================================================================================
REM Backend Startup Script for AI Marketing Content Engine (Windows)
REM ================================================================================

SETLOCAL ENABLEDELAYEDEXPANSION

echo.
echo ======================================
echo AI Marketing Content Engine - Backend
echo ======================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found
    echo Please copy .env.example to .env and configure your settings:
    echo   copy .env.example .env
    pause
    exit /b 1
)

echo [OK] .env file found

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python version: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q --upgrade pip setuptools wheel >nul 2>&1
REM Use dev requirements when USE_SQLITE_DEV=1 is set to avoid psycopg2 build
for /f "tokens=2 delims==" %%G in ('findstr /C:"USE_SQLITE_DEV=" .env 2^>nul') do set USE_SQLITE=%%G
if "%USE_SQLITE%"=="1" (
    echo Using sqlite dev requirements
    pip install -q -r requirements_dev.txt >nul 2>&1
) else (
    pip install -q -r requirements.txt >nul 2>&1
)
echo [OK] Dependencies installed

REM Check Supabase configuration
findstr /C:"SUPABASE_URL=https://" .env >nul
if errorlevel 1 (
    echo [WARNING] Supabase not configured - vector storage may not work
) else (
    echo [OK] Supabase configuration found
)

REM Check OpenAI configuration
findstr /C:"OPENAI_API_KEY=sk-" .env >nul
if errorlevel 1 (
    echo [WARNING] OpenAI not configured - will use Ollama if available
) else (
    echo [OK] OpenAI API key configured
)

echo.
echo ======================================
echo Backend Configuration:
echo ======================================
for /f "tokens=1 delims==" %%a in ('findstr /C:"API_" .env') do (
    if not "%%a"=="" (
        for /f "tokens=1,2 delims==" %%x in ('findstr "%%a" .env') do (
            if not "%%x"=="" echo %%x=***
        )
    )
)
echo.

REM Start the FastAPI server
echo [INFO] Starting FastAPI server...
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --reload

pause
