"""
LLM Enhancement Analyzer - Generates Enhancement JSON from Evaluation

This module uses LLM to analyze ATS evaluation results and generate
specific text enhancements in JSON format.

Author: Prashiskshan Backend Team
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)


class LLMEnhancementAnalyzer:
    """Analyze evaluation and generate enhancement JSON using LLM."""
    
    def __init__(self):
        """Initialize the LLM analyzer."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_enhancements(
        self,
        resume_text: str,
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate enhancement JSON from evaluation.
        
        Args:
            resume_text: Original resume text
            evaluation: ATS evaluation results
            
        Returns:
            Dictionary with enhancements in JSON format
        """
        try:
            print("🤖 Analyzing evaluation with LLM...")
            
            # Create prompt for LLM
            prompt = self._create_enhancement_prompt(resume_text, evaluation)
            
            # Generate enhancements
            response = self.model.generate_content(prompt)
            enhancement_json = response.text.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if '```json' in enhancement_json:
                enhancement_json = enhancement_json.split('```json')[1].split('```')[0].strip()
            elif '```' in enhancement_json:
                enhancement_json = enhancement_json.split('```')[1].split('```')[0].strip()
            
            enhancements = json.loads(enhancement_json)
            
            print(f"✓ Generated {len(enhancements.get('enhancements', []))} enhancements")
            
            return {
                'success': True,
                'enhancements': enhancements,
                'message': 'Enhancements generated successfully'
            }
            
        except Exception as e:
            import traceback
            print(f"❌ LLM analysis failed: {str(e)}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'enhancements': None
            }
    
    def _create_enhancement_prompt(
        self,
        resume_text: str,
        evaluation: Dict[str, Any]
    ) -> str:
        """Create prompt for LLM to generate enhancements."""
        
        # Extract key issues from evaluation
        improvements = evaluation.get('resume_improvements', {})
        weaknesses = evaluation.get('analysis_summary', {}).get('weaknesses', [])
        
        prompt = f"""You are a professional resume enhancement expert. Analyze the resume and ATS evaluation below, then generate specific text enhancements.

**CRITICAL RULES:**
1. Only enhance existing text - DO NOT add new content
2. DO NOT change dates, timelines, company names, roles, or institutions
3. DO NOT invent metrics or achievements
4. Focus on improving wording, action verbs, and clarity
5. Each enhancement must have EXACT original text and improved text

**RESUME TEXT:**
{resume_text}

**ATS EVALUATION WEAKNESSES:**
{json.dumps(weaknesses, indent=2)}

**IMPROVEMENT RECOMMENDATIONS:**
{json.dumps(improvements, indent=2)}

**YOUR TASK:**
Generate a JSON array of enhancements. Each enhancement should have:
- "original": The exact text from the resume to replace
- "enhanced": The improved version of that text
- "reason": Why this enhancement improves the resume

**OUTPUT FORMAT (JSON only, no explanations):**
{{
  "enhancements": [
    {{
      "original": "exact text from resume",
      "enhanced": "improved version",
      "reason": "why this is better"
    }}
  ]
}}

**FOCUS ON:**
- Strengthening weak action verbs
- Adding professional context to vague statements
- Improving clarity and impact
- Making descriptions more specific

Generate the JSON now:"""
        
        return prompt


def analyze_and_generate_enhancements(
    resume_text: str,
    evaluation: Dict[str, Any],
    output_path: str = None,
    save_to_file: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to generate enhancements.
    
    Args:
        resume_text: Original resume text
        evaluation: ATS evaluation results
        output_path: Optional path to save enhancement JSON (only used if save_to_file=True)
        save_to_file: If True, save to file. If False, only return data.
        
    Returns:
        Enhancement results with JSON data included
    """
    analyzer = LLMEnhancementAnalyzer()
    result = analyzer.generate_enhancements(resume_text, evaluation)
    
    # Save to file only if explicitly requested
    if result.get('success') and save_to_file and output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result['enhancements'], f, indent=2, ensure_ascii=False)
        print(f"✓ Enhancements saved to: {output_path}")
        result['enhancement_json_path'] = output_path
    
    return result


if __name__ == "__main__":
    print("LLM Enhancement Analyzer")
    print("Generates enhancement JSON from ATS evaluation")
