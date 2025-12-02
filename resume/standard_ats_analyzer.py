"""
Standard ATS Resume Analyzer - Enhanced Rule-Based Evaluation

This module provides comprehensive traditional ATS evaluation with strict criteria
for parsability, section detection, keyword matching, and structure validation.

NO UI, NO DATABASE - Pure backend processing.
"""

import re
from typing import Dict, List, Any, Tuple


class StandardATSAnalyzer:
    """Enhanced rule-based ATS analyzer with comprehensive evaluation criteria."""
    
    def __init__(self):
        """Initialize the analyzer with detailed evaluation criteria."""
        self.essential_sections = {
            'contact': ['email', 'phone', 'address', 'linkedin', 'contact', 'mobile'],
            'summary': ['summary', 'objective', 'profile', 'about'],
            'skills': ['skills', 'technologies', 'tools', 'proficiencies', 'expertise', 'competencies'],
            'experience': ['experience', 'work', 'employment', 'job', 'internship', 'career'],
            'education': ['education', 'university', 'college', 'degree', 'academic', 'qualification'],
            'projects': ['projects', 'portfolio', 'work samples'],
            'certifications': ['certifications', 'certificates', 'certified', 'training']
        }
        
        # Action verbs for bullet point analysis
        self.action_verbs = [
            'developed', 'created', 'built', 'designed', 'implemented', 'led', 'managed',
            'improved', 'optimized', 'achieved', 'delivered', 'launched', 'established',
            'increased', 'reduced', 'streamlined', 'automated', 'coordinated', 'executed',
            'analyzed', 'researched', 'collaborated', 'initiated', 'spearheaded'
        ]
        
        # Common technical skills
        self.technical_skills = [
            'python', 'java', 'javascript', 'c++', 'sql', 'react', 'node.js', 'angular',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'agile', 'scrum',
            'machine learning', 'data analysis', 'tensorflow', 'pytorch', 'pandas',
            'rest api', 'microservices', 'ci/cd', 'devops', 'linux', 'mongodb', 'postgresql'
        ]
    
    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """
        Comprehensive ATS analysis with strict evaluation criteria.
        
        Args:
            resume_text: Plain text extracted from resume (OCR output)
            
        Returns:
            Dictionary with score and detailed analysis
        """
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                'score': 0,
                'issues': ['Resume text is too short or empty'],
                'strengths': [],
                'weaknesses': ['Insufficient content for analysis'],
                'component_scores': {}
            }
        
        text_lower = resume_text.lower()
        
        # PART 1: Parsability & ATS Readiness
        parsability_score, parsability_issues = self._evaluate_parsability(resume_text)
        
        # PART 2: Section Detection
        section_score, section_issues, detected_sections = self._evaluate_sections(text_lower)
        
        # PART 3: Contact Information Validity
        contact_score, contact_issues = self._evaluate_contact_info(resume_text)
        
        # PART 4: Keyword & Skill Matching
        keyword_score, keyword_issues = self._evaluate_keywords(text_lower, resume_text)
        
        # PART 5: Experience & Project Presence
        exp_project_score, exp_project_issues, is_fresher = self._evaluate_experience_projects(
            text_lower, detected_sections
        )
        
        # PART 6: Bullet Point Structure
        bullet_score, bullet_issues = self._evaluate_bullet_points(resume_text)
        
        # PART 7: Dates & Chronology
        date_score, date_issues = self._evaluate_dates(resume_text)
        
        # Calculate weighted score BEFORE caps
        raw_score = int(
            parsability_score * 0.15 +    # 15% - Parsability
            section_score * 0.20 +        # 20% - Sections
            contact_score * 0.10 +        # 10% - Contact
            keyword_score * 0.25 +        # 25% - Keywords
            exp_project_score * 0.15 +    # 15% - Experience/Projects
            bullet_score * 0.10 +         # 10% - Bullets
            date_score * 0.05             # 5% - Dates
        )
        
        # APPLY SCORE CAPS
        final_score, cap_reason = self._apply_score_caps(
            raw_score, parsability_score, is_fresher, bullet_score,
            keyword_score, detected_sections
        )
        
        # Collect all issues
        all_issues = []
        all_issues.extend(parsability_issues)
        all_issues.extend(section_issues)
        all_issues.extend(contact_issues)
        all_issues.extend(keyword_issues)
        all_issues.extend(exp_project_issues)
        all_issues.extend(bullet_issues)
        all_issues.extend(date_issues)
        
        # Generate strengths and weaknesses
        strengths, weaknesses = self._generate_strengths_weaknesses(
            parsability_score, section_score, contact_score, keyword_score,
            exp_project_score, bullet_score, date_score, cap_reason
        )
        
        return {
            'score': final_score,
            'raw_score': raw_score,
            'cap_applied': cap_reason,
            'component_scores': {
                'parsability': parsability_score,
                'section_detection': section_score,
                'contact_information': contact_score,
                'keyword_matching': keyword_score,
                'experience_projects': exp_project_score,
                'bullet_structure': bullet_score,
                'dates_chronology': date_score
            },
            'issues': all_issues,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'detected_sections': detected_sections
        }
    
    def _evaluate_parsability(self, text: str) -> Tuple[int, List[str]]:
        """Evaluate OCR readability and ATS parsability."""
        score = 100
        issues = []
        
        # Check for broken words (excessive short words)
        words = text.split()
        short_words = [w for w in words if len(w) <= 2 and w.isalpha()]
        if len(short_words) / max(len(words), 1) > 0.15:
            score -= 30
            issues.append("High ratio of broken/garbled words detected (OCR quality issue)")
        
        # Check for excessive special characters (tables/columns indicator)
        special_chars = len(re.findall(r'[|_=+\[\]{}]', text))
        if special_chars / max(len(text), 1) > 0.05:
            score -= 25
            issues.append("Excessive special characters detected - may indicate tables/columns")
        
        # Check line length consistency (logical reading order)
        lines = text.split('\n')
        very_short_lines = [l for l in lines if 0 < len(l.strip()) < 10]
        if len(very_short_lines) / max(len(lines), 1) > 0.3:
            score -= 20
            issues.append("Inconsistent line lengths - reading order may be disrupted")
        
        # Check for minimum content
        if len(text) < 300:
            score -= 25
            issues.append("Resume is too short (minimum 300 characters recommended)")
        
        return max(0, score), issues
    
    def _evaluate_sections(self, text_lower: str) -> Tuple[int, List[str], Dict[str, bool]]:
        """Evaluate section presence and placement."""
        score = 0
        issues = []
        detected = {}
        
        # Check each essential section
        for section_name, keywords in self.essential_sections.items():
            found = any(keyword in text_lower for keyword in keywords)
            detected[section_name] = found
            
            if found:
                if section_name in ['contact', 'skills', 'experience', 'education']:
                    score += 20  # Critical sections
                else:
                    score += 10  # Nice-to-have sections
            else:
                if section_name in ['contact', 'skills', 'experience', 'education']:
                    issues.append(f"CRITICAL: Missing {section_name.title()} section")
                elif section_name == 'projects':
                    issues.append(f"Missing {section_name.title()} section (important for freshers)")
        
        # Cap at 100
        score = min(100, score)
        
        return score, issues, detected
    
    def _evaluate_contact_info(self, text: str) -> Tuple[int, List[str]]:
        """Validate contact information completeness."""
        score = 100
        issues = []
        
        # Email (CRITICAL)
        if not re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text):
            score -= 35
            issues.append("CRITICAL: Missing email address")
        
        # Phone (CRITICAL)
        if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            score -= 30
            issues.append("CRITICAL: Missing or improperly formatted phone number")
        
        # Name (should be at top)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines and len(lines[0].split()) > 5:
            score -= 10
            issues.append("First line should be your full name only")
        
        # LinkedIn
        if 'linkedin' not in text.lower():
            score -= 15
            issues.append("Missing LinkedIn profile URL")
        
        # Location
        if not re.search(r'\b(city|state|country|location)\b', text.lower()):
            score -= 10
            issues.append("Location information not clearly stated")
        
        return max(0, score), issues
    
    def _evaluate_keywords(self, text_lower: str, text: str) -> Tuple[int, List[str]]:
        """Evaluate keyword density and skill matching."""
        score = 0
        issues = []
        
        # Count technical skills
        found_skills = [skill for skill in self.technical_skills if skill in text_lower]
        skill_count = len(found_skills)
        
        if skill_count >= 12:
            score += 40
        elif skill_count >= 8:
            score += 30
        elif skill_count >= 5:
            score += 20
        elif skill_count >= 3:
            score += 10
        else:
            issues.append("Very few relevant technical keywords found")
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.action_verbs if verb in text_lower)
        if action_verb_count >= 8:
            score += 30
        elif action_verb_count >= 5:
            score += 20
        elif action_verb_count >= 3:
            score += 10
        else:
            issues.append("Insufficient action verbs in experience descriptions")
        
        # Check for metrics/quantification
        has_percentages = bool(re.search(r'\d+%', text))
        has_numbers = bool(re.search(r'\d+\s*(users|customers|projects|team|members)', text_lower))
        has_money = bool(re.search(r'\$\d+', text))
        
        metrics_count = sum([has_percentages, has_numbers, has_money])
        if metrics_count >= 2:
            score += 30
        elif metrics_count == 1:
            score += 15
        else:
            issues.append("Missing quantifiable achievements (add metrics, percentages, numbers)")
        
        # Check for keyword stuffing
        words = text_lower.split()
        word_freq = {}
        for word in words:
            if len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        stuffed_words = [w for w, count in word_freq.items() if count > 10]
        if stuffed_words:
            score -= 15
            issues.append(f"Possible keyword stuffing detected: {', '.join(stuffed_words[:3])}")
        
        return min(100, score), issues
    
    def _evaluate_experience_projects(
        self, text_lower: str, detected_sections: Dict[str, bool]
    ) -> Tuple[int, List[str], bool]:
        """Evaluate experience and project presence."""
        score = 100
        issues = []
        
        has_experience = detected_sections.get('experience', False)
        has_projects = detected_sections.get('projects', False)
        
        # Determine if fresher (no experience section or very short experience)
        exp_keywords = ['years', 'year', 'months', 'month', 'present', 'current']
        exp_mentions = sum(1 for kw in exp_keywords if kw in text_lower)
        is_fresher = not has_experience or exp_mentions < 2
        
        if is_fresher:
            # Fresher: Projects are critical
            if not has_projects:
                score = 40  # Heavy penalty
                issues.append("CRITICAL: No projects section found (essential for freshers)")
            elif has_projects:
                # Check project depth
                project_count = text_lower.count('project')
                if project_count < 2:
                    score = 60
                    issues.append("Only one project listed - add at least 2-3 substantial projects")
        else:
            # Experienced: Experience section is critical
            if not has_experience:
                score = 30  # Very heavy penalty
                issues.append("CRITICAL: No experience section found (essential for experienced candidates)")
            
            # Projects are bonus for experienced
            if not has_projects:
                score -= 20
                issues.append("Consider adding a projects section to showcase additional work")
        
        return max(0, score), issues, is_fresher
    
    def _evaluate_bullet_points(self, text: str) -> Tuple[int, List[str]]:
        """Evaluate bullet point structure and quality."""
        score = 100
        issues = []
        
        lines = text.split('\n')
        
        # Check for bullet point presence
        bullet_lines = [l for l in lines if l.strip().startswith(('•', '-', '*', '→', '·'))]
        if not bullet_lines:
            score -= 40
            issues.append("CRITICAL: No bullet points found - use bullets for achievements")
            return max(0, score), issues
        
        # Analyze bullet structure
        weak_bullets = 0
        for bullet in bullet_lines[:10]:  # Check first 10 bullets
            bullet_text = bullet.strip().lstrip('•-*→·').strip().lower()
            
            # Check for action verb
            has_action_verb = any(bullet_text.startswith(verb) for verb in self.action_verbs)
            
            # Check for method/tool mention
            has_tool = any(skill in bullet_text for skill in self.technical_skills)
            
            # Check for outcome/metric
            has_outcome = bool(re.search(r'\d+%|\d+x|improved|increased|reduced|achieved', bullet_text))
            
            # Weak bullet: missing 2 or more components
            components = sum([has_action_verb, has_tool, has_outcome])
            if components < 2:
                weak_bullets += 1
        
        if weak_bullets > 5:
            score -= 30
            issues.append("Many weak bullet points - use format: Action Verb + Task + Method + Outcome")
        elif weak_bullets > 2:
            score -= 15
            issues.append("Some bullet points lack structure - add action verbs and outcomes")
        
        return max(0, score), issues
    
    def _evaluate_dates(self, text: str) -> Tuple[int, List[str]]:
        """Evaluate date presence and chronology."""
        score = 100
        issues = []
        
        # Find all dates
        dates = re.findall(r'\b(19|20)\d{2}\b', text)
        
        if len(dates) < 2:
            score -= 40
            issues.append("Missing dates for experience/education - add MM/YYYY format dates")
            return max(0, score), issues
        
        # Check for date ranges
        date_ranges = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|present|current)', text.lower())
        if not date_ranges:
            score -= 20
            issues.append("Use date ranges (e.g., '2020 - 2023') for positions")
        
        # Check chronological order (rough check)
        date_years = [int(d) for d in dates if d.isdigit()]
        if len(date_years) >= 3:
            # Check if mostly descending (reverse chronological)
            descending_pairs = sum(1 for i in range(len(date_years)-1) if date_years[i] >= date_years[i+1])
            if descending_pairs / max(len(date_years)-1, 1) < 0.5:
                score -= 15
                issues.append("Dates should be in reverse chronological order (most recent first)")
        
        return max(0, score), issues
    
    def _apply_score_caps(
        self, raw_score: int, parsability: int, is_fresher: bool,
        bullet_score: int, keyword_score: int, detected_sections: Dict[str, bool]
    ) -> Tuple[int, str]:
        """Apply score caps based on critical issues."""
        caps = []
        
        # Parsing issues
        if parsability < 60:
            caps.append((55, "Parsability issues"))
        
        # No projects for fresher
        if is_fresher and not detected_sections.get('projects', False):
            caps.append((60, "No projects (fresher)"))
        
        # Weak bullets
        if bullet_score < 60:
            caps.append((65, "Weak bullet points"))
        
        # Skill-context mismatch (low keywords)
        if keyword_score < 50:
            caps.append((70, "Insufficient keywords"))
        
        # Apply lowest cap
        if caps:
            min_cap = min(caps, key=lambda x: x[0])
            if raw_score > min_cap[0]:
                return min_cap[0], min_cap[1]
        
        return raw_score, "No cap applied"
    
    def _generate_strengths_weaknesses(
        self, parsability: int, section: int, contact: int, keyword: int,
        exp_project: int, bullet: int, date: int, cap_reason: str
    ) -> Tuple[List[str], List[str]]:
        """Generate strengths and weaknesses based on scores."""
        strengths = []
        weaknesses = []
        
        # Strengths
        if parsability >= 80:
            strengths.append("Clean, ATS-parsable format")
        if section >= 80:
            strengths.append("All essential sections present")
        if contact >= 80:
            strengths.append("Complete contact information")
        if keyword >= 70:
            strengths.append("Good keyword density and relevance")
        if bullet >= 80:
            strengths.append("Well-structured bullet points with outcomes")
        if date >= 80:
            strengths.append("Proper chronological organization")
        
        # Weaknesses
        if parsability < 60:
            weaknesses.append("OCR quality issues affecting parsability")
        if section < 60:
            weaknesses.append("Missing critical resume sections")
        if contact < 60:
            weaknesses.append("Incomplete contact information")
        if keyword < 50:
            weaknesses.append("Insufficient relevant keywords and skills")
        if exp_project < 60:
            weaknesses.append("Weak experience/project presentation")
        if bullet < 60:
            weaknesses.append("Bullet points lack structure and impact")
        if date < 60:
            weaknesses.append("Missing or inconsistent dates")
        
        if cap_reason != "No cap applied":
            weaknesses.append(f"Score capped due to: {cap_reason}")
        
        return strengths, weaknesses
