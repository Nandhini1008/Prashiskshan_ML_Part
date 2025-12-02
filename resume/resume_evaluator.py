"""
Resume Evaluator - Main ATS Evaluation Engine with Triple Analysis

This module orchestrates three analyzers:
1. Standard (rule-based)
2. AI Semantic (pedagogical strict mode)
3. Evidence-Based Rubric (human reviewer simulation)

NO UI, NO DATABASE - Pure backend processing.
Input: Plain text (OCR output)
Output: Strict JSON format
"""

from typing import Dict, Any, List
from standard_ats_analyzer import StandardATSAnalyzer
from ai_semantic_analyzer import AISemanticAnalyzer
from rubric_analyzer import EvidenceBasedRubricAnalyzer


class ResumeEvaluator:
    """Main resume evaluation engine combining three analyzers."""
    
    def __init__(self):
        """Initialize all three analyzers."""
        self.standard_analyzer = StandardATSAnalyzer()
        self.ai_analyzer = AISemanticAnalyzer()
        self.rubric_analyzer = EvidenceBasedRubricAnalyzer()
    
    def evaluate(self, resume_text: str) -> Dict[str, Any]:
        """
        Evaluate resume using all three analyzers.
        
        Args:
            resume_text: Plain text extracted from resume (OCR output)
            
        Returns:
            Dictionary in strict JSON format with scores and improvements
        """
        # Run all three analyzers
        standard_result = self.standard_analyzer.analyze(resume_text)
        ai_result = self.ai_analyzer.analyze(resume_text)
        rubric_result = self.rubric_analyzer.analyze(resume_text)
        
        # Extract scores
        standard_score = standard_result.get('score', 0)
        ai_score = ai_result.get('score', 0)
        rubric_score = rubric_result.get('score', 0)
        
        # Calculate final score (average of all three)
        final_score = round((standard_score + ai_score + rubric_score) / 3)
        
        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(
            standard_result, ai_result, rubric_result
        )
        
        # Generate categorized improvements
        improvements = self._generate_improvements(
            resume_text, standard_result, ai_result, rubric_result
        )
        
        # Return in strict JSON format
        return {
            "standard_ats_score": standard_score,
            "ai_ats_score": ai_score,
            "rubric_ats_score": rubric_score,
            "final_ats_score": final_score,
            "shortlist_decision": rubric_result.get('shortlist_decision', 'Unknown'),
            "analysis_summary": analysis_summary,
            "resume_improvements": improvements,
            "rubric_feedback": {
                "trusted_signals": rubric_result.get('trusted_signals', []),
                "red_flags": rubric_result.get('red_flags', []),
                "learning_takeaways": rubric_result.get('learning_takeaways', [])
            }
        }
    
    def _generate_analysis_summary(
        self, 
        standard_result: Dict[str, Any], 
        ai_result: Dict[str, Any],
        rubric_result: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate combined strengths and weaknesses summary from all three analyzers."""
        strengths = []
        weaknesses = []
        
        # Combine strengths from all analyzers
        strengths.extend(standard_result.get('strengths', []))
        strengths.extend(ai_result.get('strengths', []))
        strengths.extend(rubric_result.get('strengths', []))
        
        # Add AI-specific insights as strengths if available
        if ai_result.get('semantic_insights'):
            strengths.append(f"AI Insight: {ai_result['semantic_insights']}")
        
        # Combine weaknesses from all analyzers
        weaknesses.extend(standard_result.get('weaknesses', []))
        weaknesses.extend(ai_result.get('weaknesses', []))
        weaknesses.extend(rubric_result.get('weaknesses', []))
        
        # Deduplicate while preserving order
        strengths = list(dict.fromkeys(strengths))
        weaknesses = list(dict.fromkeys(weaknesses))
        
        return {
            "strengths": strengths[:10],  # Limit to top 10
            "weaknesses": weaknesses[:10]  # Limit to top 10
        }
    
    def _generate_improvements(
        self,
        resume_text: str,
        standard_result: Dict[str, Any],
        ai_result: Dict[str, Any],
        rubric_result: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Generate categorized, actionable improvements from all three analyzers."""
        
        improvements = {
            "keyword_and_skills": [],
            "content_and_bullets": [],
            "projects_and_experience": [],
            "structure_and_formatting": [],
            "ats_compatibility": []
        }
        
        # Extract issues from all analyzers
        standard_issues = standard_result.get('issues', [])
        ai_weaknesses = ai_result.get('weaknesses', [])
        rubric_issues = rubric_result.get('rubric_issues', [])
        
        # Categorize standard issues
        for issue in standard_issues:
            improvement = self._categorize_and_format_issue(issue, standard_result)
            if improvement:
                category = improvement['category']
                del improvement['category']
                improvements[category].append(improvement)
        
        # Add AI-driven improvements
        ai_improvements = self._generate_ai_improvements(ai_result, resume_text)
        for category, items in ai_improvements.items():
            improvements[category].extend(items)
        
        # Add rubric-driven improvements
        rubric_improvements = self._generate_rubric_improvements(rubric_result)
        for category, items in rubric_improvements.items():
            improvements[category].extend(items)
        
        # Ensure each category has at least some content
        improvements = self._ensure_minimum_improvements(improvements)
        
        return improvements
    
    def _categorize_and_format_issue(
        self, 
        issue: str, 
        standard_result: Dict[str, Any]
    ) -> Dict[str, str]:
        """Categorize an issue and format as improvement."""
        issue_lower = issue.lower()
        
        # Keyword and Skills
        if any(keyword in issue_lower for keyword in ['keyword', 'skill', 'action verb', 'quantifiable']):
            return {
                'category': 'keyword_and_skills',
                'issue': issue,
                'recommended_fix': self._get_keyword_fix(issue),
                'reason': 'Improves ATS keyword matching and demonstrates relevant expertise'
            }
        
        # Content and Bullets
        elif any(keyword in issue_lower for keyword in ['bullet', 'achievement', 'metric', 'number']):
            return {
                'category': 'content_and_bullets',
                'issue': issue,
                'recommended_fix': self._get_content_fix(issue),
                'reason': 'Makes accomplishments more impactful and measurable'
            }
        
        # Projects and Experience
        elif any(keyword in issue_lower for keyword in ['experience', 'project', 'date', 'role']):
            return {
                'category': 'projects_and_experience',
                'issue': issue,
                'recommended_fix': self._get_experience_fix(issue),
                'reason': 'Provides better context for your professional background'
            }
        
        # Structure and Formatting
        elif any(keyword in issue_lower for keyword in ['format', 'header', 'spacing', 'line', 'structure']):
            return {
                'category': 'structure_and_formatting',
                'issue': issue,
                'recommended_fix': self._get_formatting_fix(issue),
                'reason': 'Improves readability and professional appearance'
            }
        
        # ATS Compatibility
        elif any(keyword in issue_lower for keyword in ['ats', 'special character', 'table', 'graphic', 'contact']):
            return {
                'category': 'ats_compatibility',
                'issue': issue,
                'recommended_fix': self._get_ats_fix(issue),
                'reason': 'Ensures ATS systems can properly parse your resume'
            }
        
        # Default to ATS compatibility
        else:
            return {
                'category': 'ats_compatibility',
                'issue': issue,
                'recommended_fix': 'Review and address this issue to improve ATS compatibility',
                'reason': 'Helps ATS systems better understand your qualifications'
            }
    
    def _get_keyword_fix(self, issue: str) -> str:
        """Generate fix for keyword-related issues."""
        if 'action verb' in issue.lower():
            return "Start bullet points with strong action verbs like: Developed, Implemented, Led, Designed, Optimized, Achieved, Managed"
        elif 'quantifiable' in issue.lower():
            return "Add specific metrics: percentages, dollar amounts, user counts, or time savings (e.g., 'Improved performance by 40%')"
        elif 'keyword' in issue.lower() or 'skill' in issue.lower():
            return "Add relevant technical skills and industry keywords that match your target role"
        return "Enhance keyword density with role-specific terminology"
    
    def _get_content_fix(self, issue: str) -> str:
        """Generate fix for content-related issues."""
        if 'bullet' in issue.lower():
            return "Use bullet points (•, -, or *) to list responsibilities and achievements for better scannability"
        elif 'metric' in issue.lower() or 'number' in issue.lower():
            return "Quantify achievements with specific numbers, percentages, or measurable outcomes"
        return "Rewrite content to be more concise and impact-focused"
    
    def _get_experience_fix(self, issue: str) -> str:
        """Generate fix for experience-related issues."""
        if 'date' in issue.lower():
            return "Include dates in MM/YYYY format for all positions and education (e.g., '01/2020 - 12/2023')"
        elif 'section' in issue.lower() and 'experience' in issue.lower():
            return "Add a dedicated Work Experience section with job titles, companies, dates, and key achievements"
        return "Provide more detailed information about your professional experience"
    
    def _get_formatting_fix(self, issue: str) -> str:
        """Generate fix for formatting issues."""
        if 'header' in issue.lower():
            return "Use clear section headers in UPPERCASE or Title Case (e.g., 'WORK EXPERIENCE', 'EDUCATION')"
        elif 'spacing' in issue.lower():
            return "Use consistent spacing: one blank line between sections, no excessive empty lines"
        elif 'short' in issue.lower():
            return "Expand resume content to at least one full page with detailed descriptions of your experience"
        return "Review formatting for consistency and professional appearance"
    
    def _get_ats_fix(self, issue: str) -> str:
        """Generate fix for ATS compatibility issues."""
        if 'contact' in issue.lower() or 'email' in issue.lower():
            return "Add complete contact information at the top: Full Name, Email, Phone, LinkedIn URL"
        elif 'special character' in issue.lower() or 'table' in issue.lower():
            return "Avoid tables, text boxes, and excessive special characters - use simple text formatting"
        elif 'linkedin' in issue.lower():
            return "Add your LinkedIn profile URL in the format: linkedin.com/in/yourprofile"
        return "Simplify formatting to ensure ATS systems can parse your resume correctly"
    
    def _generate_ai_improvements(
        self, 
        ai_result: Dict[str, Any],
        resume_text: str
    ) -> Dict[str, List[Dict[str, str]]]:
        """Generate improvements based on AI analysis."""
        improvements = {
            "keyword_and_skills": [],
            "content_and_bullets": [],
            "projects_and_experience": [],
            "structure_and_formatting": [],
            "ats_compatibility": []
        }
        
        # Check if AI analysis was successful
        if ai_result.get('error') or ai_result.get('score', 0) == 0:
            return improvements
        
        # Add improvements based on AI insights
        
        # Experience depth
        if ai_result.get('experience_depth'):
            improvements['projects_and_experience'].append({
                'issue': 'Experience depth could be improved',
                'recommended_fix': ai_result['experience_depth'],
                'reason': 'Demonstrates substantive experience rather than surface-level claims'
            })
        
        # Impact assessment
        if ai_result.get('impact_assessment'):
            improvements['content_and_bullets'].append({
                'issue': 'Impact-driven content needs enhancement',
                'recommended_fix': ai_result['impact_assessment'],
                'reason': 'Highlights business value and measurable outcomes'
            })
        
        # Role level alignment
        role_level = ai_result.get('role_level', '').lower()
        if role_level in ['junior', 'mid-level', 'senior']:
            improvements['keyword_and_skills'].append({
                'issue': f'Resume appears to target {role_level} positions',
                'recommended_fix': f'Ensure your skills and experience align with {role_level} role expectations. Add relevant certifications or advanced skills if targeting higher levels.',
                'reason': 'Aligns resume presentation with career level and target roles'
            })
        
        return improvements
    
    def _generate_rubric_improvements(
        self,
        rubric_result: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Generate improvements based on rubric analysis."""
        improvements = {
            "keyword_and_skills": [],
            "content_and_bullets": [],
            "projects_and_experience": [],
            "structure_and_formatting": [],
            "ats_compatibility": []
        }
        
        # Check if rubric analysis was successful
        if rubric_result.get('error') or rubric_result.get('score', 0) == 0:
            return improvements
        
        # Extract rubric issues
        rubric_issues = rubric_result.get('rubric_issues', [])
        
        for issue_obj in rubric_issues[:5]:  # Limit to top 5 issues
            issue_text = issue_obj.get('issue', '')
            how_to_fix = issue_obj.get('how_to_fix', '')
            why_fails = issue_obj.get('why_it_fails_human_review', '')
            example_rewrite = issue_obj.get('example_rewrite', '')
            
            # Categorize based on issue content
            issue_lower = issue_text.lower()
            
            recommended_fix = how_to_fix
            if example_rewrite:
                recommended_fix += f" | Example: {example_rewrite}"
            
            if any(keyword in issue_lower for keyword in ['skill', 'keyword', 'proof', 'claim']):
                improvements['keyword_and_skills'].append({
                    'issue': issue_text,
                    'recommended_fix': recommended_fix,
                    'reason': f"Human Reviewer: {why_fails}"
                })
            elif any(keyword in issue_lower for keyword in ['bullet', 'verb', 'ownership', 'depth']):
                improvements['content_and_bullets'].append({
                    'issue': issue_text,
                    'recommended_fix': recommended_fix,
                    'reason': f"Human Reviewer: {why_fails}"
                })
            elif any(keyword in issue_lower for keyword in ['project', 'experience', 'difficulty']):
                improvements['projects_and_experience'].append({
                    'issue': issue_text,
                    'recommended_fix': recommended_fix,
                    'reason': f"Human Reviewer: {why_fails}"
                })
            else:
                improvements['ats_compatibility'].append({
                    'issue': issue_text,
                    'recommended_fix': recommended_fix,
                    'reason': f"Human Reviewer: {why_fails}"
                })
        
        return improvements
    
    def _ensure_minimum_improvements(
        self, 
        improvements: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Ensure each category has at least one improvement."""
        
        defaults = {
            "keyword_and_skills": {
                'issue': 'Keyword optimization opportunity',
                'recommended_fix': 'Review job descriptions for target roles and incorporate relevant technical keywords and skills',
                'reason': 'Increases match rate with ATS keyword filters'
            },
            "content_and_bullets": {
                'issue': 'Content could be more impactful',
                'recommended_fix': 'Use the STAR method (Situation, Task, Action, Result) to describe achievements',
                'reason': 'Makes accomplishments more compelling and memorable'
            },
            "projects_and_experience": {
                'issue': 'Experience presentation could be enhanced',
                'recommended_fix': 'Highlight projects that demonstrate relevant skills and real-world problem-solving',
                'reason': 'Shows practical application of skills and technical depth'
            },
            "structure_and_formatting": {
                'issue': 'Structure could be optimized',
                'recommended_fix': 'Use a clear hierarchy: Contact → Summary → Skills → Experience → Education → Projects',
                'reason': 'Follows standard resume format expected by recruiters and ATS'
            },
            "ats_compatibility": {
                'issue': 'ATS compatibility check',
                'recommended_fix': 'Use standard section headers, avoid images/graphics, and save as .docx or .pdf',
                'reason': 'Ensures maximum compatibility with all ATS systems'
            }
        }
        
        for category, default_improvement in defaults.items():
            if not improvements[category]:
                improvements[category].append(default_improvement)
        
        return improvements
