@echo off

REM Development script for AI Communication Assistant (Windows)

REM Check if uv is installed
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo uv could not be found. Please install uv first: https://docs.astral.sh/uv/
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
uv sync

REM Start backend in background
echo Starting backend server...
start "Backend" /D "%cd%" uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

REM Start frontend
echo Starting frontend...
cd frontend/dashboard
npm install
npm run dev