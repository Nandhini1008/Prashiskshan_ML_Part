@echo off
echo ============================================================
echo Starting Resume Processing API Server
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
    pip install fastapi uvicorn python-multipart
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please create a .env file with GOOGLE_API_KEY
)

echo.
echo Starting API server on http://localhost:8002
echo Press Ctrl+C to stop the server
echo.

python api_server.py

pause

