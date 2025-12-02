"""
Example Usage - Backend ATS Resume Evaluator

This script demonstrates how to use the backend ATS resume evaluation engine.

Usage:
    python example_usage.py

Make sure to:
1. Install dependencies: pip install -r requirements.txt
2. Create .env file with GOOGLE_API_KEY (copy from env_example.txt)
3. Place a sample resume PDF in this directory
"""

import json
import sys
import os

# Add OCR directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'OCR'))

from resume_evaluator import ResumeEvaluator
from OCR.ocr_pdf_pipeline import PDFTextExtractor


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using OCR pipeline.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted plain text
    """
    print(f"📄 Extracting text from: {pdf_path}")
    
    extractor = PDFTextExtractor()
    
    # Try direct extraction first (faster)
    result = extractor.extract_text_from_pdf(pdf_path, use_ocr=False)
    
    if result['method'] == 'PyPDF2':
        # Concatenate text from all pages
        text = '\n'.join([page['text'] for page in result['pages']])
        print(f"✓ Extracted {len(text)} characters using PyPDF2")
        return text
    
    # If direct extraction failed, try OCR
    print("⚠ Direct extraction failed, trying OCR...")
    result = extractor.extract_text_from_pdf(pdf_path, use_ocr=True)
    
    if 'pages' in result:
        # Concatenate text from all detections
        text_parts = []
        for page in result['pages']:
            if 'detections' in page:
                for detection in page['detections']:
                    text_parts.append(detection['text'])
            elif 'text' in page:
                text_parts.append(page['text'])
        
        text = '\n'.join(text_parts)
        print(f"✓ Extracted {len(text)} characters using OCR")
        return text
    
    raise Exception("Failed to extract text from PDF")


def evaluate_resume_from_pdf(pdf_path: str):
    """
    Complete example: Extract text from PDF and evaluate.
    
    Args:
        pdf_path: Path to resume PDF file
    """
    print("\n" + "="*60)
    print("🚀 BACKEND ATS RESUME EVALUATOR")
    print("="*60 + "\n")
    
    # Step 1: Extract text from PDF
    try:
        resume_text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return
    
    print(f"\n📝 Resume Preview (first 200 chars):")
    print("-" * 60)
    print(resume_text[:200] + "...")
    print("-" * 60)
    
    # Step 2: Evaluate resume
    print("\n🔍 Analyzing resume...")
    print("   - Running Standard ATS Analyzer (rule-based)...")
    print("   - Running AI Semantic Analyzer (contextual)...")
    
    evaluator = ResumeEvaluator()
    result = evaluator.evaluate(resume_text)
    
    # Step 3: Display results
    print("\n" + "="*60)
    print("📊 EVALUATION RESULTS")
    print("="*60 + "\n")
    
    print(f"Standard ATS Score:  {result['standard_ats_score']}/100")
    print(f"AI ATS Score:        {result['ai_ats_score']}/100")
    print(f"Final ATS Score:     {result['final_ats_score']}/100")
    
    print("\n✅ STRENGTHS:")
    for i, strength in enumerate(result['analysis_summary']['strengths'], 1):
        print(f"   {i}. {strength}")
    
    print("\n⚠️  WEAKNESSES:")
    for i, weakness in enumerate(result['analysis_summary']['weaknesses'], 1):
        print(f"   {i}. {weakness}")
    
    print("\n💡 RECOMMENDED IMPROVEMENTS:")
    
    improvements = result['resume_improvements']
    
    if improvements['keyword_and_skills']:
        print("\n   📌 Keyword & Skills:")
        for imp in improvements['keyword_and_skills'][:2]:  # Show top 2
            print(f"      • {imp['recommended_fix']}")
    
    if improvements['content_and_bullets']:
        print("\n   📌 Content & Bullets:")
        for imp in improvements['content_and_bullets'][:2]:
            print(f"      • {imp['recommended_fix']}")
    
    if improvements['projects_and_experience']:
        print("\n   📌 Projects & Experience:")
        for imp in improvements['projects_and_experience'][:2]:
            print(f"      • {imp['recommended_fix']}")
    
    # Step 4: Save full JSON output
    output_file = 'resume_evaluation_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")
    print("\n" + "="*60)


def evaluate_resume_from_text(resume_text: str):
    """
    Simple example: Evaluate resume from plain text.
    
    Args:
        resume_text: Plain text resume content
    """
    print("\n🔍 Evaluating resume from text...")
    
    evaluator = ResumeEvaluator()
    result = evaluator.evaluate(resume_text)
    
    # Print JSON output
    print("\n📄 JSON OUTPUT:")
    print(json.dumps(result, indent=2))
    
    return result


def main():
    """Main entry point."""
    
    # Example 1: Evaluate from sample text
    print("\n" + "="*60)
    print("EXAMPLE 1: Evaluate from Sample Text")
    print("="*60)
    
    sample_resume = """
John Doe
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Software Engineer with 5+ years of experience in full-stack development.
Specialized in Python, JavaScript, and cloud technologies.

SKILLS
Python, JavaScript, React, Node.js, AWS, Docker, SQL, Git, REST APIs

WORK EXPERIENCE

Senior Software Engineer | Tech Corp | Jan 2020 - Present
• Developed microservices architecture using Python and FastAPI
• Improved system performance by 40% through optimization
• Led team of 3 developers on critical projects
• Implemented CI/CD pipeline reducing deployment time by 60%

Software Developer | StartupXYZ | Jun 2018 - Dec 2019
• Built responsive web applications using React and Node.js
• Collaborated with cross-functional teams on product features
• Reduced bug count by 30% through comprehensive testing

EDUCATION
B.S. Computer Science | University of Technology | 2018
GPA: 3.8/4.0

PROJECTS
E-commerce Platform - Built full-stack application with 10,000+ users
Machine Learning Model - Developed predictive model with 92% accuracy
"""
    
    result = evaluate_resume_from_text(sample_resume)
    print(f"\n✅ Final Score: {result['final_ats_score']}/100")
    
    # Example 2: Evaluate from PDF (if available)
    print("\n\n" + "="*60)
    print("EXAMPLE 2: Evaluate from PDF")
    print("="*60)
    
    # Look for any PDF file in current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if pdf_files:
        pdf_path = pdf_files[0]
        print(f"\n📁 Found PDF: {pdf_path}")
        evaluate_resume_from_pdf(pdf_path)
    else:
        print("\n⚠️  No PDF files found in current directory")
        print("   To test PDF evaluation:")
        print("   1. Place a resume PDF in this directory")
        print("   2. Run this script again")
    
    print("\n✨ Done!\n")


if __name__ == "__main__":
    main()
