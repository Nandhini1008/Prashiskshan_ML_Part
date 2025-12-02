# Resume Processing Pipeline - Usage Guide

## Quick Start

This file (`process_resume.py`) handles the complete flow:
**PDF Upload → OCR Extraction → ATS Analysis → JSON Results**

## Usage Methods

### Method 1: Command Line (Recommended)

```bash
# Process a resume PDF
python process_resume.py path/to/resume.pdf

# Force OCR for image-based PDFs
python process_resume.py path/to/resume.pdf --ocr

# Save to custom output file
python process_resume.py resume.pdf -o output.json
```

### Method 2: Python Function

```python
from process_resume import process_resume_file

# Process resume
result = process_resume_file('resume.pdf')

if result['success']:
    evaluation = result['evaluation']
    print(f"Final Score: {evaluation['final_ats_score']}/100")
    print(f"Strengths: {evaluation['analysis_summary']['strengths']}")
else:
    print(f"Error: {result['error']}")
```

### Method 3: Class-Based (Advanced)

```python
from process_resume import ResumeProcessor

processor = ResumeProcessor()
result = processor.process_resume_pdf('resume.pdf', use_ocr=False)
```

## Output Format

```json
{
  "success": true,
  "resume_text": "extracted text...",
  "text_length": 1234,
  "evaluation": {
    "standard_ats_score": 75,
    "ai_ats_score": 68,
    "final_ats_score": 72,
    "analysis_summary": {
      "strengths": [...],
      "weaknesses": [...]
    },
    "resume_improvements": {
      "keyword_and_skills": [...],
      "content_and_bullets": [...],
      "projects_and_experience": [...],
      "structure_and_formatting": [...],
      "ats_compatibility": [...]
    }
  }
}
```

## Examples

### Example 1: Basic Usage
```bash
python process_resume.py AMAANUDEEN.pdf
```

### Example 2: Image-based PDF
```bash
python process_resume.py scanned_resume.pdf --ocr
```

### Example 3: Save Results
```bash
python process_resume.py resume.pdf -o results.json
```

## Integration Example (FastAPI)

```python
from fastapi import FastAPI, UploadFile, File
from process_resume import process_resume_file
import tempfile
import os

app = FastAPI()

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Process resume
        result = process_resume_file(tmp_path)
        return result
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
```

## Integration Example (Flask)

```python
from flask import Flask, request, jsonify
from process_resume import process_resume_file
import tempfile
import os

app = Flask(__name__)

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Process resume
        result = process_resume_file(tmp_path)
        return jsonify(result)
    finally:
        # Clean up temp file
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(debug=True)
```

## Notes

- **OCR Flag**: Use `--ocr` only for image-based PDFs. Direct extraction is faster.
- **API Key**: Ensure `GOOGLE_API_KEY` is set in `.env` for AI analysis.
- **Output**: Results are automatically saved to `resume_evaluation_result.json`.
