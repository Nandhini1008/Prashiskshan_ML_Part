"""
Polished Feedback Formatter - Student-Friendly Resume Analysis

This module formats resume analysis results in an encouraging, constructive way
that motivates students to improve rather than discouraging them.
"""

import json
from typing import Dict, Any, List


def format_polished_feedback(result: Dict[str, Any]) -> str:
    """
    Format resume analysis results in a polished, encouraging bulletin-point format.
    
    Args:
        result: Resume evaluation result dictionary
        
    Returns:
        Formatted feedback string
    """
    if not result.get('success'):
        return "❌ Unable to process resume. Please check the file and try again."
    
    evaluation = result.get('evaluation', {})
    
    # Extract scores
    standard_score = evaluation.get('standard_ats_score', 0)
    ai_score = evaluation.get('ai_ats_score', 0)
    rubric_score = evaluation.get('rubric_ats_score', 0)
    final_score = evaluation.get('final_ats_score', 0)
    
    # Build feedback
    feedback = []
    
    # Header
    feedback.append("=" * 70)
    feedback.append("📊 YOUR RESUME ANALYSIS REPORT")
    feedback.append("=" * 70)
    feedback.append("")
    
    # Overall Score
    feedback.append("🎯 OVERALL ASSESSMENT")
    feedback.append("")
    score_interpretation = _get_score_interpretation(final_score)
    feedback.append(f"   Final ATS Score: {final_score}/100 - {score_interpretation['label']}")
    feedback.append(f"   {score_interpretation['message']}")
    feedback.append("")
    
    # Score Breakdown
    feedback.append("📈 DETAILED SCORES")
    feedback.append("")
    feedback.append(f"   • Technical ATS Check: {standard_score}/100")
    if ai_score > 0:
        feedback.append(f"   • Content Quality: {ai_score}/100")
    if rubric_score > 0:
        feedback.append(f"   • Professional Review: {rubric_score}/100")
    feedback.append("")
    
    # Strengths
    strengths = evaluation.get('analysis_summary', {}).get('strengths', [])
    if strengths:
        feedback.append("✨ WHAT'S WORKING WELL")
        feedback.append("")
        # Filter and polish strengths
        polished_strengths = _polish_strengths(strengths)
        for i, strength in enumerate(polished_strengths[:7], 1):
            feedback.append(f"   {i}. {strength}")
        feedback.append("")
    
    # Growth Opportunities (instead of "Weaknesses")
    weaknesses = evaluation.get('analysis_summary', {}).get('weaknesses', [])
    if weaknesses:
        feedback.append("🌱 OPPORTUNITIES FOR GROWTH")
        feedback.append("")
        # Filter and polish weaknesses
        polished_weaknesses = _polish_weaknesses(weaknesses)
        for i, weakness in enumerate(polished_weaknesses[:7], 1):
            feedback.append(f"   {i}. {weakness}")
        feedback.append("")
    
    # Actionable Improvements
    improvements = evaluation.get('resume_improvements', {})
    if improvements:
        feedback.append("💡 RECOMMENDED ENHANCEMENTS")
        feedback.append("")
        
        # Priority improvements
        priority_improvements = _get_priority_improvements(improvements)
        for category, items in priority_improvements.items():
            if items:
                feedback.append(f"   📌 {category}:")
                feedback.append("")
                for item in items[:2]:  # Top 2 per category
                    polished_fix = _polish_recommendation(item.get('recommended_fix', ''))
                    feedback.append(f"      • {polished_fix}")
                feedback.append("")
    
    # Encouragement
    feedback.append("🎓 FINAL THOUGHTS")
    feedback.append("")
    encouragement = _get_encouragement(final_score, standard_score, ai_score, rubric_score)
    for line in encouragement:
        feedback.append(f"   {line}")
    feedback.append("")
    
    feedback.append("=" * 70)
    feedback.append("Keep refining your resume - every improvement brings you closer to your goals!")
    feedback.append("=" * 70)
    
    return "\n".join(feedback)


def _get_score_interpretation(score: int) -> Dict[str, str]:
    """Get encouraging interpretation of score."""
    if score >= 85:
        return {
            'label': 'Excellent!',
            'message': '   Your resume is in great shape and ready for applications!'
        }
    elif score >= 75:
        return {
            'label': 'Very Good',
            'message': '   Your resume is strong with just a few areas to polish.'
        }
    elif score >= 65:
        return {
            'label': 'Good Foundation',
            'message': '   You have a solid base - focus on the improvements below to stand out.'
        }
    elif score >= 50:
        return {
            'label': 'Developing',
            'message': '   Your resume shows potential - the recommendations below will help strengthen it.'
        }
    else:
        return {
            'label': 'Needs Attention',
            'message': '   Focus on the key improvements below to make your resume more competitive.'
        }


def _polish_strengths(strengths: List[str]) -> List[str]:
    """Polish and filter strengths to be more encouraging."""
    polished = []
    
    for strength in strengths:
        # Skip overly technical or negative-sounding strengths
        if any(skip in strength.lower() for skip in ['shortlist decision: would not', 'learning focus:', '✗']):
            continue
        
        # Clean up and make more positive
        cleaned = strength.strip()
        
        # Remove redundant prefixes
        cleaned = cleaned.replace('AI Insight: ', '')
        cleaned = cleaned.replace('Semantic Analysis: ', '')
        
        polished.append(cleaned)
    
    return polished


def _polish_weaknesses(weaknesses: List[str]) -> List[str]:
    """Polish weaknesses to be constructive rather than harsh."""
    polished = []
    
    for weakness in weaknesses:
        # Skip overly harsh statements
        if any(skip in weakness.lower() for skip in [
            'would not recommend',
            'shortlist decision: would not',
            'severely undermining',
            'critical honesty concern'
        ]):
            continue
        
        # Reframe negative language
        cleaned = weakness.strip()
        
        # Remove harsh prefixes
        cleaned = cleaned.replace('✗ ', '')
        cleaned = cleaned.replace('Learning Focus: ', '')
        
        # Soften language
        cleaned = cleaned.replace('Significant lack of', 'Consider adding more')
        cleaned = cleaned.replace('Insufficient evidence', 'Strengthen by adding evidence')
        cleaned = cleaned.replace('Over-reliance on', 'Reduce use of')
        cleaned = cleaned.replace('severely undermining', 'affecting')
        cleaned = cleaned.replace('Critical', 'Important')
        
        polished.append(cleaned)
    
    return polished


def _polish_recommendation(recommendation: str) -> str:
    """Polish recommendations to be more actionable and less harsh."""
    # Remove harsh language
    polished = recommendation.replace('Human Reviewer: ', '')
    polished = polished.replace('severely', 'significantly')
    polished = polished.replace('must', 'should')
    polished = polished.replace('critical', 'important')
    
    # Truncate if too long (keep first sentence + example if present)
    if '|' in polished:
        parts = polished.split('|')
        if len(parts[0]) > 150:
            polished = parts[0][:150] + '...'
        else:
            polished = parts[0].strip()
            if len(parts) > 1 and 'Example:' in parts[1]:
                polished += ' ' + parts[1][:100].strip()
    elif len(polished) > 200:
        polished = polished[:200] + '...'
    
    return polished


def _get_priority_improvements(improvements: Dict[str, List]) -> Dict[str, List]:
    """Get priority improvements in a student-friendly order."""
    return {
        'Quick Wins (Easy to Fix)': improvements.get('ats_compatibility', []),
        'Content Enhancements': improvements.get('content_and_bullets', []),
        'Skills & Keywords': improvements.get('keyword_and_skills', []),
        'Experience Details': improvements.get('projects_and_experience', []),
        'Formatting': improvements.get('structure_and_formatting', [])
    }


def _get_encouragement(final_score: int, standard: int, ai: int, rubric: int) -> List[str]:
    """Generate encouraging final message based on scores."""
    messages = []
    
    if final_score >= 75:
        messages.append("You're on the right track! Your resume demonstrates strong potential.")
        messages.append("Focus on the recommended enhancements to make it even more competitive.")
    elif final_score >= 60:
        messages.append("You have a solid foundation to build upon.")
        messages.append("Implementing the suggestions above will significantly strengthen your application.")
    else:
        messages.append("Every great resume starts somewhere - you're taking the right steps!")
        messages.append("Focus on the quick wins first, then work through the other improvements.")
    
    # Add specific encouragement
    if standard >= 75:
        messages.append("Your resume is technically well-formatted for ATS systems.")
    
    if ai > 0 and ai >= 70:
        messages.append("Your content shows good depth and relevance.")
    
    messages.append("")
    messages.append("Remember: This analysis is meant to help you improve, not discourage you.")
    messages.append("Many successful professionals have refined their resumes multiple times.")
    
    return messages


def save_polished_feedback(result: Dict[str, Any], output_file: str = 'resume_feedback.txt'):
    """Save polished feedback to a text file."""
    feedback = format_polished_feedback(result)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(feedback)
    return output_file


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'resume_evaluation_result.json'
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        feedback = format_polished_feedback(result)
        print(feedback)
        
        # Save to file
        output_file = save_polished_feedback(result)
        print(f"\n📄 Feedback also saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find {json_file}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file}")
