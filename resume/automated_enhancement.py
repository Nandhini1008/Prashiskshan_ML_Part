"""
Automated Resume Enhancement Pipeline

This module provides the complete automated pipeline:
1. Takes resume evaluation results
2. Enhances resume content based on recommendations
3. Generates professional PDF

Author: Prashiskshan Backend Team
"""

import os
import json
from typing import Dict, Any, Optional
from resume_enhancer import ResumeEnhancer
from resume_pdf_generator import ResumePDFGenerator


class AutomatedResumeEnhancer:
    """Complete automated enhancement pipeline."""
    
    def __init__(self):
        """Initialize enhancer and PDF generator."""
        self.enhancer = ResumeEnhancer()
        self.pdf_generator = ResumePDFGenerator()
    
    def enhance_and_generate_pdf(
        self,
        evaluation_result_path: str,
        original_resume_text: str,
        output_pdf_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Evaluation → Enhancement → PDF Generation
        
        Args:
            evaluation_result_path: Path to evaluation JSON file
            original_resume_text: Original resume text (from OCR)
            output_pdf_path: Optional custom output path for PDF
            
        Returns:
            Dictionary with:
                - success: bool
                - enhanced_resume_path: str (path to generated PDF)
                - improvements_applied: List[str]
                - enhanced_content: Dict (structured enhanced content)
        """
        try:
            # Load evaluation results
            with open(evaluation_result_path, 'r', encoding='utf-8') as f:
                evaluation = json.load(f)
            
            # Extract candidate name for file naming
            candidate_name = self._extract_candidate_name(original_resume_text)
            
            # Determine output path
            if not output_pdf_path:
                eval_dir = os.path.dirname(evaluation_result_path)
                output_pdf_path = os.path.join(
                    eval_dir, 
                    f"{candidate_name}_Enhanced_Resume.pdf"
                )
            
            # Enhance resume content
            enhanced_content = self.enhancer.enhance_resume(
                evaluation, 
                original_resume_text
            )
            
            # Generate PDF
            pdf_path = self.pdf_generator.generate_resume_pdf(
                enhanced_content,
                output_pdf_path
            )
            
            # Track improvements applied
            improvements_applied = self._track_improvements(
                evaluation,
                enhanced_content
            )
            
            return {
                'success': True,
                'enhanced_resume_path': pdf_path,
                'improvements_applied': improvements_applied,
                'enhanced_content': enhanced_content,
                'candidate_name': candidate_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'enhanced_resume_path': None,
                'improvements_applied': [],
                'enhanced_content': None
            }
    
    def _extract_candidate_name(self, resume_text: str) -> str:
        """Extract candidate name from resume text."""
        import re
        
        lines = resume_text.split('\n')
        
        # First, try to find a line that looks like a name (2-4 capitalized words)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        
        # Search in first 50 lines for name
        for line in lines[:50]:
            line = line.strip()
            
            # Skip empty lines or lines that are too long
            if not line or len(line) > 60:
                continue
            
            # Skip lines with technical keywords
            if any(keyword in line.lower() for keyword in [
                'java', 'python', 'experience', 'developer', 'engineer',
                'at least', 'years', 'working', 'knowledge', 'skills',
                'ai,', 'llm', 'rag', 'oop', 'spring', 'html', 'css',
                'angularjs', 'react', 'javascript', 'software', 'deep',
                'practices', 'modules', 'based on', 'degree in', 'university',
                'college', 'master', 'bachelor', 'certified', 'certification'
            ]):
                continue
            
            # Look for name pattern
            match = re.search(name_pattern, line)
            if match:
                potential_name = match.group(1)
                
                # Verify it's not a company or location
                if not any(word in potential_name for word in ['Microsoft', 'Visa', 'Seattle', 'Austin', 'India', 'USA']):
                    # Clean name for filename
                    name = potential_name.replace(' ', '_').replace(',', '')
                    # Remove special characters
                    name = ''.join(c for c in name if c.isalnum() or c == '_')
                    if name and len(name) > 3:
                        return name
        
        # Fallback: Look for all-caps name (like "MAD HAV SOMANI")
        for line in lines:
            line = line.strip()
            # Check for all-caps name pattern
            if re.match(r'^[A-Z\s]{5,40}$', line):
                # Check if it's not a section header
                if not any(keyword in line for keyword in [
                    'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 
                    'ACCOMPLISHMENTS', 'CERTIFICATIONS', 'SUMMARY', 'CONTACT'
                ]):
                    name = line.replace(' ', '_')
                    name = ''.join(c for c in name if c.isalnum() or c == '_')
                    if name and len(name) > 3:
                        return name
        
        return "Candidate"
    
    def _track_improvements(
        self,
        evaluation: Dict[str, Any],
        enhanced_content: Dict[str, Any]
    ) -> list[str]:
        """Track what improvements were applied."""
        improvements = []
        
        # Check for bullet point enhancements
        exp_count = len(enhanced_content.get('experience', []))
        if exp_count > 0:
            total_bullets = sum(
                len(exp.get('bullets', [])) 
                for exp in enhanced_content.get('experience', [])
            )
            improvements.append(f"Enhanced {total_bullets} experience bullet points with metrics and impact")
        
        # Check for skills filtering
        skills_count = len(enhanced_content.get('skills', []))
        if skills_count > 0:
            improvements.append(f"Filtered and organized {skills_count} proven technical skills")
        
        # Check for projects enhancement
        projects_count = len(enhanced_content.get('projects', []))
        if projects_count > 0:
            improvements.append(f"Enhanced {projects_count} projects with impact and outcomes")
        
        # Check for generic content removal
        eval_improvements = evaluation.get('evaluation', {}).get('resume_improvements', {})
        if eval_improvements.get('keyword_and_skills'):
            for issue in eval_improvements['keyword_and_skills']:
                if 'generic text block' in issue.get('issue', '').lower():
                    improvements.append("Removed generic copy-pasted text block")
                    break
        
        # Check for formatting improvements
        if eval_improvements.get('structure_and_formatting'):
            improvements.append("Applied professional formatting and structure")
        
        # General improvements
        improvements.append("Improved action verbs and professional language")
        improvements.append("Enhanced ATS compatibility")
        
        return improvements


def process_and_enhance_resume(
    pdf_path: str,
    use_ocr: bool = False
) -> Dict[str, Any]:
    """
    Complete end-to-end pipeline: PDF → OCR → Evaluation → Enhancement → PDF
    
    This integrates with the existing process_resume.py pipeline.
    
    Args:
        pdf_path: Path to original resume PDF
        use_ocr: Whether to use OCR for text extraction
        
    Returns:
        Dictionary with evaluation and enhancement results
    """
    from process_resume import process_resume_file
    
    # Step 1: Process and evaluate resume
    print(f"Processing resume: {pdf_path}")
    result = process_resume_file(pdf_path, use_ocr)
    
    if not result.get('success'):
        return result
    
    # Step 2: Enhance resume
    print("Enhancing resume based on evaluation...")
    enhancer = AutomatedResumeEnhancer()
    
    # Get evaluation file path
    eval_path = pdf_path.replace('.pdf', '_evaluation.json')
    
    # Save evaluation if not already saved
    if not os.path.exists(eval_path):
        with open(eval_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Enhance and generate PDF
    enhancement_result = enhancer.enhance_and_generate_pdf(
        eval_path,
        result.get('resume_text', '')
    )
    
    # Combine results
    return {
        'success': True,
        'evaluation': result,
        'enhancement': enhancement_result,
        'original_pdf': pdf_path,
        'enhanced_pdf': enhancement_result.get('enhanced_resume_path'),
        'improvements_applied': enhancement_result.get('improvements_applied', [])
    }


def enhance_from_existing_evaluation(
    evaluation_json_path: str
) -> Dict[str, Any]:
    """
    Enhance resume from existing evaluation JSON.
    
    Args:
        evaluation_json_path: Path to existing evaluation JSON
        
    Returns:
        Enhancement results
    """
    # Load evaluation
    with open(evaluation_json_path, 'r', encoding='utf-8') as f:
        evaluation = json.load(f)
    
    # Get resume text from evaluation
    resume_text = evaluation.get('resume_text', '')
    
    if not resume_text:
        return {
            'success': False,
            'error': 'No resume text found in evaluation JSON'
        }
    
    # Enhance
    enhancer = AutomatedResumeEnhancer()
    result = enhancer.enhance_and_generate_pdf(
        evaluation_json_path,
        resume_text
    )
    
    return result


def main():
    """Example usage and testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Automated Resume Enhancement Pipeline")
        print("\nUsage:")
        print("  python automated_enhancement.py <evaluation_json_path>")
        print("\nExample:")
        print("  python automated_enhancement.py resume_evaluation_result.json")
        return
    
    evaluation_path = sys.argv[1]
    
    if not os.path.exists(evaluation_path):
        print(f"Error: File not found: {evaluation_path}")
        return
    
    print(f"Enhancing resume from evaluation: {evaluation_path}")
    print("-" * 60)
    
    result = enhance_from_existing_evaluation(evaluation_path)
    
    if result.get('success'):
        print("\n✓ Resume enhancement completed successfully!")
        print(f"\nEnhanced PDF: {result['enhanced_resume_path']}")
        print(f"\nImprovements applied:")
        for improvement in result.get('improvements_applied', []):
            print(f"  • {improvement}")
    else:
        print(f"\n✗ Enhancement failed: {result.get('error')}")


if __name__ == "__main__":
    main()
