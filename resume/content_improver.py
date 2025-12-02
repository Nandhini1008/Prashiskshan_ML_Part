"""
Content Improver - LLM-Powered Resume Enhancement

This module uses LLM to enhance resume content while preserving:
- All dates, timelines, roles, company names
- Section order and structure
- Original facts and information
- No fake metrics or invented content

Author: Prashiskshan Backend Team
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)


class ContentImprover:
    """LLM-powered content enhancement for resumes."""
    
    def __init__(self):
        """Initialize the LLM for content improvement."""
        # Configure Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # System prompt for resume enhancement
        self.system_prompt = """You are a professional Resume Optimization AI specializing in ATS-friendly
enhancements for technical resumes.

Your task is to ENHANCE the wording of the resume provided by the user
WITHOUT changing its structure, section order, dates, timelines, roles,
headings, layout style, or overall format.

IMPORTANT CONSTRAINTS (NON-NEGOTIABLE):

1. DO NOT:
   - Change section names
   - Reorder sections or positions
   - Add new sections
   - Remove any existing information
   - Modify dates, timelines, CGPA, percentages, roles, company names
   - Invent metrics, numbers, users, revenue, or impact
   - Change the resume template or visual structure

2. YOU MAY ONLY:
   - Rewrite sentences to be more professional and impact-driven
   - Replace weak verbs with strong action verbs
   - Convert vague phrases into clearer, technically precise statements
   - Improve clarity, professionalism, and ATS keyword alignment
   - Add contextual "why / outcome" phrasing WITHOUT inserting fake metrics

3. FORMAT RULES:
   - Preserve the exact section order and hierarchy
   - Preserve single-column, ATS-safe formatting
   - Maintain bullet count consistency (do not add or remove bullets)
   - Do not convert paragraphs into tables or vice versa
   - Output must follow the same layout style as the original resume

4. CONTENT RULES:
   - Keep all technical stacks exactly the same (no additions)
   - Do not elevate seniority or role level
   - Do not exaggerate leadership or ownership
   - Enhance only wording, not claims

Return ONLY the enhanced resume text.
Do NOT include explanations, suggestions, comments, or metadata."""
    
    def improve_resume_content(self, resume_text: str) -> str:
        """
        Improve resume content using LLM while preserving structure.
        
        Args:
            resume_text: Original resume text
            
        Returns:
            Enhanced resume text with improved wording
        """
        try:
            # Create prompt
            prompt = f"""{self.system_prompt}

USER PROMPT
Below is my resume content.

TASK:
Enhance ONLY the wording to improve clarity, professionalism,
and ATS effectiveness.

Strictly maintain:
- Same resume template and layout
- Same section positions and order
- Same dates, timelines, and roles
- Same content coverage (nothing added or removed)

Only rewrite sentences to convey stronger impact
using professional and technical language.

Return the enhanced resume in the SAME FORMAT as the input.

------------- RESUME START -------------
{resume_text}
------------- RESUME END -------------

OUTPUT
Return ONLY the enhanced resume text.

Do NOT include:
- Explanations
- Suggestions
- Comments
- Headings like "Enhanced Version"
- Any metadata or analysis

The output should be directly usable as a resume."""

            # Generate enhanced content
            response = self.model.generate_content(prompt)
            enhanced_text = response.text.strip()
            
            return enhanced_text
            
        except Exception as e:
            print(f"Warning: LLM enhancement failed: {e}")
            # Return original text if enhancement fails
            return resume_text
    
    def improve_bullet_point(self, bullet: str, context: str = "") -> str:
        """
        Improve a single bullet point.
        
        Args:
            bullet: Original bullet point text
            context: Additional context (company, role, etc.)
            
        Returns:
            Enhanced bullet point
        """
        try:
            prompt = f"""Enhance this resume bullet point to be more professional and impact-driven.

RULES:
- Keep the same facts and information
- Do NOT add fake metrics or numbers
- Use strong action verbs
- Make it more specific and clear
- Maintain technical accuracy
- Keep it concise (1-2 lines max)

Context: {context if context else 'Technical resume'}

Original bullet:
{bullet}

Return ONLY the enhanced bullet point, nothing else."""

            response = self.model.generate_content(prompt)
            enhanced = response.text.strip()
            
            # Remove any markdown formatting or quotes
            enhanced = enhanced.replace('**', '').replace('*', '').strip('"').strip("'")
            
            return enhanced
            
        except Exception as e:
            print(f"Warning: Bullet enhancement failed: {e}")
            return bullet
    
    def improve_section(self, section_text: str, section_name: str) -> str:
        """
        Improve a specific section of the resume.
        
        Args:
            section_text: Original section text
            section_name: Name of the section (e.g., "Professional Experience")
            
        Returns:
            Enhanced section text
        """
        try:
            prompt = f"""Enhance this {section_name} section from a resume.

RULES:
- Preserve ALL dates, timelines, company names, role titles
- Keep the same structure and format
- Do NOT add or remove bullet points
- Do NOT invent metrics or numbers
- Only improve wording for clarity and professionalism
- Use strong action verbs
- Maintain technical accuracy

Original {section_name}:
{section_text}

Return ONLY the enhanced section text in the same format."""

            response = self.model.generate_content(prompt)
            enhanced = response.text.strip()
            
            return enhanced
            
        except Exception as e:
            print(f"Warning: Section enhancement failed: {e}")
            return section_text


def enhance_resume_with_llm(resume_text: str) -> str:
    """
    Convenience function to enhance resume using LLM.
    
    Args:
        resume_text: Original resume text
        
    Returns:
        Enhanced resume text
    """
    improver = ContentImprover()
    return improver.improve_resume_content(resume_text)


if __name__ == "__main__":
    print("Content Improver - LLM-powered resume enhancement")
    print("Use enhance_resume_with_llm() to improve resume content")
