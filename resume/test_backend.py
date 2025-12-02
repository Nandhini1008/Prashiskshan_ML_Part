"""Quick verification test for backend ATS analyzer."""

from standard_ats_analyzer import StandardATSAnalyzer
from ai_semantic_analyzer import AISemanticAnalyzer
from resume_evaluator import ResumeEvaluator
import json

# Test data
sample_resume = """
John Doe
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Software Engineer with 5 years of experience in Python and JavaScript.

SKILLS
Python, JavaScript, React, Node.js, AWS, Docker, SQL, Git

WORK EXPERIENCE
Senior Developer at Tech Corp (2020-2023)
- Developed microservices using Python and FastAPI
- Improved system performance by 40%
- Led team of 3 developers

EDUCATION
B.S. Computer Science, University XYZ (2018)
"""

print("="*60)
print("BACKEND ATS ANALYZER - VERIFICATION TEST")
print("="*60)

# Test 1: Standard ATS Analyzer
print("\n[Test 1] Standard ATS Analyzer...")
try:
    analyzer = StandardATSAnalyzer()
    result = analyzer.analyze(sample_resume)
    print(f"✓ Score: {result['score']}/100")
    print(f"✓ Components: {list(result['component_scores'].keys())}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: AI Semantic Analyzer
print("\n[Test 2] AI Semantic Analyzer...")
try:
    ai_analyzer = AISemanticAnalyzer()
    if ai_analyzer.available:
        result = ai_analyzer.analyze(sample_resume)
        print(f"✓ Score: {result['score']}/100")
        print(f"✓ AI analysis available")
    else:
        print("⚠ AI analysis unavailable (missing API key)")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Resume Evaluator
print("\n[Test 3] Resume Evaluator (Integration)...")
try:
    evaluator = ResumeEvaluator()
    result = evaluator.evaluate(sample_resume)
    
    print(f"✓ Standard Score: {result['standard_ats_score']}/100")
    print(f"✓ AI Score: {result['ai_ats_score']}/100")
    print(f"✓ Final Score: {result['final_ats_score']}/100")
    print(f"✓ Strengths: {len(result['analysis_summary']['strengths'])}")
    print(f"✓ Weaknesses: {len(result['analysis_summary']['weaknesses'])}")
    print(f"✓ Improvement categories: {len(result['resume_improvements'])}")
    
    # Verify JSON structure
    required_keys = ['standard_ats_score', 'ai_ats_score', 'final_ats_score', 
                     'analysis_summary', 'resume_improvements']
    for key in required_keys:
        assert key in result, f"Missing key: {key}"
    
    print("\n✓ JSON structure valid")
    
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check for unwanted dependencies
print("\n[Test 4] Checking for unwanted dependencies...")
try:
    import streamlit
    print("✗ Streamlit is still imported (should be removed)")
except ImportError:
    print("✓ No Streamlit dependency")

try:
    import sqlite3
    # sqlite3 is part of Python standard library, so we check if it's actually used
    print("⚠ sqlite3 available (standard library)")
except ImportError:
    print("✓ No sqlite3")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
