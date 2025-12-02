"""
Evidence-Based Rubric Analyzer (EBRA) - Human Reviewer Simulation

This module simulates a strict human resume reviewer focusing on proof,
ownership, technical depth, and hireability judgment.

NO UI, NO DATABASE - Pure backend processing.
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class EvidenceBasedRubricAnalyzer:
    """Human reviewer simulation with strict evidence-based evaluation."""
    
    def __init__(self):
        """Initialize the analyzer with Google Gemini API."""
        load_dotenv()
        # Use dedicated API key for rubric analyzer, fallback to general key
        self.api_key = os.getenv("RUBRIC_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            self.available = True
        else:
            self.available = False
    
    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """
        Evidence-based rubric analysis simulating human reviewer.
        
        Args:
            resume_text: Plain text extracted from resume (OCR output)
            
        Returns:
            Dictionary with rubric score and human reviewer feedback
        """
        if not self.available:
            return {
                'score': 0,
                'error': 'Rubric analysis unavailable - missing API key or google-generativeai package',
                'strengths': [],
                'weaknesses': ['Rubric analysis could not be performed']
            }
        
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                'score': 0,
                'strengths': [],
                'weaknesses': ['Resume text is too short for meaningful rubric analysis']
            }
        
        try:
            # Create rubric evaluation prompt
            prompt = self._create_rubric_prompt(resume_text)
            
            # Get AI response with JSON output
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON response
            result = json.loads(response.text)
            
            # Transform to standard format
            transformed = self._transform_rubric_output(result)
            
            return transformed
            
        except json.JSONDecodeError as e:
            return {
                'score': 0,
                'error': f'Rubric response parsing failed: {str(e)}',
                'strengths': [],
                'weaknesses': ['Rubric analysis encountered a JSON parsing error']
            }
        except Exception as e:
            return {
                'score': 0,
                'error': f'Rubric analysis failed: {str(e)}',
                'strengths': [],
                'weaknesses': ['Rubric analysis encountered an error']
            }
    
    def _create_rubric_prompt(self, resume_text: str) -> str:
        """Create evidence-based rubric evaluation prompt."""
        return f"""SYSTEM:
You are an Evidence-Based Rubric Analyzer (EBRA), simulating a strict human resume reviewer and hiring manager. You do not care about keyword matching or semantic similarity. You evaluate resumes only on proof, ownership, difficulty, plausibility, and honesty.

RESUME TEXT:
{resume_text}

INSTRUCTIONS:

A. CLAIM-PROOF VALIDATION
- For every skill, achievement, or impact claim, search for explicit proof inside experience or project descriptions.
- If proof is missing or vague, mark as "Unsupported Claim" and deduct points.

B. OWNERSHIP SIGNAL ANALYSIS
- Classify verbs:
   Weak: assisted, involved, helped, participated
   Strong: designed, built, implemented, optimized, debugged, led
- If majority of bullets use weak verbs → apply major deduction.

C. TECHNICAL DEPTH RUBRIC
- Evaluate each major bullet on:
   1. What was done
   2. How it was done (tools / approach)
   3. Why it was done (reason / constraint)
- Missing "why" → partial credit only.

D. DIFFICULTY & EFFORT
- Detect non-trivial effort indicators:
   performance tuning, failure handling, scalability, debugging, integration
- Pure CRUD/tutorial work framed as advanced → penalty.

E. REPEATABILITY TEST
- If bullets are generic and could apply to anyone → downgrade originality score.

F. HONESTY & SCOPE CHECK
- Penalize exaggerated titles, inflated scope, or buzzwords without evidence.

G. HUMAN SHORTLIST SIMULATION
- Decide if you would shortlist this resume for interview.
- This decision should strongly affect the final score.

H. SCORING
- Raw rubric score (0–100) using:
   Proof & ownership: 40%
   Technical depth & difficulty: 30%
   Originality & honesty: 20%
   Hireability judgment: 10%
- Apply penalties aggressively. Conservative bias required.

I. EDUCATIONAL FEEDBACK (MANDATORY)
- For each major weakness, explain:
   1. Why a human reviewer would reject it
   2. What exact change would improve trust
   3. One rewritten example bullet showing proof + ownership

J. OUTPUT FORMAT (JSON ONLY)

{{
  "rubric_ats_score": 0,
  "shortlist_decision": "Yes/No",
  "rubric_summary": {{
    "trusted_signals": [],
    "red_flags": []
  }},
  "rubric_issues": [
    {{
      "issue": "",
      "why_it_fails_human_review": "",
      "how_to_fix": "",
      "example_rewrite": ""
    }}
  ],
  "learning_takeaways": [
    "..."
  ]
}}

STRICT RULES:
- Prefer lowering scores if unsure.
- Do not assume intent; judge only text.
- No follow-up questions.
- Output JSON only."""

    def _transform_rubric_output(self, rubric_result: Dict[str, Any]) -> Dict[str, Any]:
        """Transform rubric JSON output to standard format."""
        
        # Extract score
        score = rubric_result.get('rubric_ats_score', 0)
        
        # Extract shortlist decision
        shortlist = rubric_result.get('shortlist_decision', 'No')
        
        # Extract summary
        rubric_summary = rubric_result.get('rubric_summary', {})
        trusted_signals = rubric_summary.get('trusted_signals', [])
        red_flags = rubric_summary.get('red_flags', [])
        
        # Build strengths from trusted signals
        strengths = trusted_signals.copy()
        if shortlist == 'Yes':
            strengths.insert(0, f"✓ Shortlist Decision: Would recommend for interview")
        
        # Build weaknesses from red flags
        weaknesses = red_flags.copy()
        if shortlist == 'No':
            weaknesses.insert(0, f"✗ Shortlist Decision: Would NOT recommend for interview")
        
        # Extract learning takeaways
        learning_takeaways = rubric_result.get('learning_takeaways', [])
        
        # Extract issues
        issues = rubric_result.get('rubric_issues', [])
        
        return {
            'score': score,
            'shortlist_decision': shortlist,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'learning_takeaways': learning_takeaways,
            'rubric_issues': issues,
            'trusted_signals': trusted_signals,
            'red_flags': red_flags
        }
