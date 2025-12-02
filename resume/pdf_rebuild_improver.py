"""
PDF Rebuild Content Improver - Structure-Preserving Enhancement

This module enhances resume content while preserving EXACT line count,
order, and structure for pixel-perfect PDF rebuilding.

Author: Prashiskshan Backend Team
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)


class PDFRebuildImprover:
    """Structure-preserving content enhancement for PDF rebuilding."""
    
    def __init__(self):
        """Initialize the LLM for content improvement."""
        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # System prompt for structure-preserving enhancement
        self.system_prompt = """You are a Resume PDF Rebuild AI.

Your task is to generate a FINAL RESUME TEXT that will be
re-inserted into an existing PDF template WITHOUT changing
its layout, structure, spacing, or formatting.

This resume will be rebuilt line-by-line at the same coordinates
in the original PDF.

Therefore, you MUST preserve line count, order, and structure
exactly as the original resume.

🔹 ABSOLUTE CONSTRAINTS (NON-NEGOTIABLE)

1. Line count MUST remain exactly the same as the ORIGINAL resume.
2. Line order MUST remain unchanged.
3. Section headings MUST remain unchanged.
4. Dates, timelines, CGPA, percentages, company names,
   institution names, roles MUST NOT be changed.
5. Do NOT add, remove, merge, or split lines.
6. Do NOT change spacing intentionally.
7. Do NOT add metrics, numbers, or achievements not present.
8. Output MUST be suitable for direct PDF text replacement.

🔹 WHAT YOU ARE ALLOWED TO DO

- Replace weak wording with stronger, professional language
- Improve clarity and ATS keyword strength
- Improve action verbs
- Add safe impact context WITHOUT adding metrics
- Align wording with the enhanced TXT content PROVIDED

🔹 OUTPUT RULES (VERY IMPORTANT)

- Return ONLY the FINAL resume text
- No explanations
- No comments
- No headers like "Enhanced Resume"
- No markdown
- No extra blank lines

The output WILL be directly injected back into the PDF."""
    
    def improve_for_pdf_rebuild(
        self,
        original_resume_text: str,
        enhanced_text: str
    ) -> str:
        """
        Improve resume while preserving exact structure for PDF rebuild.
        
        Args:
            original_resume_text: Original resume text (structure template)
            enhanced_text: Enhanced text (wording guide)
            
        Returns:
            Final resume text ready for PDF rebuilding
        """
        try:
            # Create prompt
            prompt = f"""{self.system_prompt}

🔹 YOUR TASK

Using:
- The ORIGINAL RESUME as the structural and line template
- The ENHANCED TEXT as the wording guide

Produce a FINAL RESUME TEXT that:

✅ Has EXACTLY the same line count and order as the ORIGINAL
✅ Uses improved wording inspired by the ENHANCED TEXT
✅ Is safe for pixel-perfect PDF rebuilding

------------- ORIGINAL RESUME (STRUCTURE TEMPLATE) -------------
{original_resume_text}
------------- END ORIGINAL RESUME -------------

------------- ENHANCED TEXT (WORDING GUIDE) -------------
{enhanced_text}
------------- END ENHANCED TEXT -------------

OUTPUT
Return ONLY the FINAL resume text that preserves the EXACT structure
of the ORIGINAL while using improved wording from the ENHANCED TEXT.

The output WILL be directly injected back into the PDF."""

            # Generate final text
            response = self.model.generate_content(prompt)
            final_text = response.text.strip()
            
            return final_text
            
        except Exception as e:
            print(f"Warning: PDF rebuild enhancement failed: {e}")
            # Return original text if enhancement fails
            return original_resume_text


def enhance_for_pdf_rebuild(
    original_text: str,
    enhanced_text: str
) -> str:
    """
    Convenience function to enhance for PDF rebuilding.
    
    Args:
        original_text: Original resume text
        enhanced_text: Enhanced text from LLM
        
    Returns:
        Final text ready for PDF rebuilding
    """
    improver = PDFRebuildImprover()
    return improver.improve_for_pdf_rebuild(original_text, enhanced_text)


if __name__ == "__main__":
    print("PDF Rebuild Improver - Structure-preserving enhancement")
