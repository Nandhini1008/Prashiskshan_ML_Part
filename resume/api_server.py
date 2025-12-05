"""
Resume Processing API Server

FastAPI server that exposes resume processing functionality via REST API.
Integrates with the Node.js backend for resume upload and processing.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from process_resume import ResumeProcessor

app = FastAPI(
    title="Resume Processing API",
    description="API for processing and analyzing resumes with ATS scoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize resume processor
processor = ResumeProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Resume Processing API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "resume-processing",
        "components": {
            "ocr": "ready",
            "evaluator": "ready",
            "enhancer": "ready"
        }
    }

@app.post("/process-resume")
async def process_resume(file: UploadFile = File(...)):
    """
    Process uploaded resume PDF
    
    Args:
        file: PDF file upload
        
    Returns:
        JSON with evaluation results, ATS score, and enhancement data
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Create temporary file to store upload
    temp_dir = tempfile.mkdtemp()
    temp_pdf_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        contents = await file.read()
        with open(temp_pdf_path, 'wb') as f:
            f.write(contents)
        
        print(f"Processing resume: {file.filename}")
        
        # Process the resume
        result = processor.process_resume_pdf(
            temp_pdf_path,
            use_ocr=False,  # Try direct extraction first
            enhance=True    # Generate enhancements
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Resume processing failed')
            )
        
        # Return the complete result
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        try:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")

@app.get("/enhancement-data")
async def get_enhancement_data(path: str):
    """
    Get enhancement JSON data
    
    Args:
        path: Path to enhancement JSON file
        
    Returns:
        Enhancement data with original and recommended changes
    """
    try:
        if not os.path.exists(path):
            raise HTTPException(
                status_code=404,
                detail="Enhancement file not found"
            )
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read enhancement data: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8002"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n{'='*60}")
    print(f"🚀 Resume Processing API Server")
    print(f"{'='*60}")
    print(f"📍 Running on: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
