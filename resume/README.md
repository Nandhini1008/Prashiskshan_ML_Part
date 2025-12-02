# Backend ATS Resume Evaluation Engine

A clean, backend-only ATS (Applicant Tracking System) resume evaluation engine with **NO UI** and **NO DATABASE**.

## Features

✅ **Dual Analysis System**
- **Standard ATS Analyzer**: Rule-based evaluation (keyword matching, section presence, formatting)
- **AI Semantic Analyzer**: Contextual evaluation using Google Gemini (experience depth, impact assessment)

✅ **OCR Integration**
- Extracts text from PDF resumes using CRAFT + PaddleOCR
- Fallback to PyPDF2 for text-based PDFs

✅ **Strict JSON Output**
- Structured response format with scores and categorized improvements
- Ready for API integration

✅ **No External Dependencies**
- No UI frameworks (Streamlit removed)
- No database (SQLite removed)
- Pure backend processing

## Installation

### 1. Install Dependencies

```bash
cd d:\sih_project\Prashiskshan_backend\resume
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file (copy from `env_example.txt`):

```bash
# .env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Quick Start

```python
from resume_evaluator import ResumeEvaluator

# Sample resume text (from OCR or direct input)
resume_text = """
John Doe
john.doe@email.com | (555) 123-4567

SKILLS
Python, JavaScript, React, AWS

EXPERIENCE
Software Engineer at Tech Corp (2020-2023)
- Developed microservices using Python
- Improved performance by 40%
"""

# Evaluate
evaluator = ResumeEvaluator()
result = evaluator.evaluate(resume_text)

print(f"Final Score: {result['final_ats_score']}/100")
```

### Complete Example with PDF

```python
from resume_evaluator import ResumeEvaluator
from OCR.ocr_pdf_pipeline import PDFTextExtractor

# Extract text from PDF
extractor = PDFTextExtractor()
result = extractor.extract_text_from_pdf('resume.pdf', use_ocr=False)
resume_text = '\n'.join([page['text'] for page in result['pages']])

# Evaluate
evaluator = ResumeEvaluator()
evaluation = evaluator.evaluate(resume_text)

print(evaluation)
```

### Run Example Script

```bash
python example_usage.py
```

## Output Format

```json
{
  "standard_ats_score": 75,
  "ai_ats_score": 68,
  "final_ats_score": 72,
  "analysis_summary": {
    "strengths": [
      "Complete contact information provided",
      "Good keyword density and relevance"
    ],
    "weaknesses": [
      "Missing quantifiable achievements",
      "Experience depth could be improved"
    ]
  },
  "resume_improvements": {
    "keyword_and_skills": [
      {
        "issue": "Few relevant technical keywords found",
        "recommended_fix": "Add relevant technical skills and industry keywords",
        "reason": "Improves ATS keyword matching"
      }
    ],
    "content_and_bullets": [...],
    "projects_and_experience": [...],
    "structure_and_formatting": [...],
    "ats_compatibility": [...]
  }
}
```

## Architecture

```
resume/
├── standard_ats_analyzer.py    # Rule-based ATS evaluation
├── ai_semantic_analyzer.py     # AI-powered semantic analysis
├── resume_evaluator.py         # Main orchestrator
├── example_usage.py            # Usage examples
├── requirements.txt            # Dependencies
├── env_example.txt             # Environment template
└── OCR/
    └── ocr_pdf_pipeline.py     # PDF text extraction
```

## Evaluation Criteria

### Standard ATS Analyzer (Rule-Based)
- **Contact Information** (15%): Email, phone, LinkedIn presence
- **Section Presence** (25%): Essential sections (Skills, Experience, Education)
- **Keyword Relevance** (30%): Technical keywords, action verbs, metrics
- **Formatting** (15%): Bullet points, headers, length
- **Structure** (15%): Organization, dates, logical flow

### AI Semantic Analyzer (Contextual)
- **Semantic Skill Alignment**: Depth beyond keyword matching
- **Experience Depth**: Substantive vs surface-level claims
- **Impact-Driven Content**: Quantifiable outcomes
- **Role Suitability**: Junior/Mid/Senior level signals
- **Project Relevance**: Real-world applicability
- **Career Progression**: Logical growth trajectory
- **Clarity of Intent**: Professional positioning

### Final Score
```
Final ATS Score = (Standard Score + AI Score) / 2
```

## Improvement Categories

1. **Keyword & Skills**: Technical keywords, action verbs, skill optimization
2. **Content & Bullets**: Impact statements, metrics, bullet point usage
3. **Projects & Experience**: Dates, descriptions, relevance
4. **Structure & Formatting**: Headers, spacing, organization
5. **ATS Compatibility**: Contact info, special characters, parsing issues

## Requirements

- Python 3.8+
- Google Gemini API key (for AI analysis)
- Poppler (for OCR-based PDF processing)

## Notes

- **AI Analysis**: Requires `GOOGLE_API_KEY`. Without it, only standard analysis runs.
- **OCR**: For image-based PDFs, ensure Poppler is installed and in PATH.
- **No UI**: This is a pure backend service. Integrate with your own frontend/API.
- **No Database**: All processing is stateless. Store results in your own system.

## Troubleshooting

### "AI analysis unavailable"
- Check if `GOOGLE_API_KEY` is set in `.env` file
- Verify the API key is valid

### "PDF extraction failed"
- For image-based PDFs, install Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
- Add Poppler bin directory to PATH

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## License

This is a backend module for the Prashiskshan project.
