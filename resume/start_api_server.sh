#!/bin/bash

echo "============================================================"
echo "Starting Resume Processing API Server"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "WARNING: Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    pip install fastapi uvicorn python-multipart
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Please create a .env file with GOOGLE_API_KEY"
fi

echo ""
echo "Starting API server on http://localhost:8002"
echo "Press Ctrl+C to stop the server"
echo ""

python api_server.py

