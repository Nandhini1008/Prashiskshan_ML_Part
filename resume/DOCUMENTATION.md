# Backend ATS Resume Analyzer - Complete Documentation

## Overview

A comprehensive, backend-only ATS (Applicant Tracking System) resume evaluation engine that uses **three independent analyzers** to provide detailed, actionable feedback on resumes.

---

## System Architecture

### Three-Analyzer System

1. **Standard ATS Analyzer** (Rule-Based)
   - Traditional ATS evaluation using predefined rules
   - Keyword matching and pattern recognition
   - Deterministic and consistent scoring

2. **AI Semantic Analyzer** (Pedagogical Strict Mode)
   - AI-powered contextual evaluation using Google Gemini
   - Evidence-based skill validation
   - Strict penalties for unsupported claims
   - Provides rewritten bullet examples

3. **Evidence-Based Rubric Analyzer** (Human Reviewer Simulation)
   - Simulates strict human hiring manager review
   - Focuses on proof, ownership, and technical depth
   - Provides shortlist decision (Yes/No for interview)
   - Human-centric feedback and learning takeaways

### Final Score Calculation

```
Final ATS Score = (Standard Score + AI Score + Rubric Score) / 3
```

---

## Step-by-Step Process Flow

### Step 1: PDF Upload
- User provides a PDF resume file
- File path is passed to the processing pipeline
- No file size restrictions (handled by OCR pipeline)

### Step 2: OCR Text Extraction
- **Primary Method**: PyPDF2 (fast, for text-based PDFs)
  - Extracts text directly from PDF structure
  - Works for digitally created PDFs
  - Fastest extraction method

- **Fallback Method**: OCR (for image-based PDFs)
  - Uses CRAFT + PaddleOCR for text detection
  - Handles scanned documents and images
  - Slower but more comprehensive

- **Output**: Plain text string containing all resume content

### Step 3: Standard ATS Analysis (Rule-Based)

#### 3.1 Parsability & ATS Readiness (15% weight)
- **OCR Quality Check**
  - Detects broken words (short word ratio > 15%)
  - Identifies garbled text and special characters
  - Penalty: -30 points for poor OCR quality

- **Special Character Detection**
  - Flags excessive `|`, `_`, `=`, `+`, `[`, `]`, `{`, `}`
  - Indicates tables/columns (ATS incompatible)
  - Penalty: -25 points if ratio > 5%

- **Line Length Consistency**
  - Checks for logical reading order
  - Flags if >30% lines are very short (<10 chars)
  - Penalty: -20 points for inconsistent spacing

- **Minimum Content Check**
  - Requires at least 300 characters
  - Penalty: -25 points if too short

#### 3.2 Section Detection (20% weight)
- **Critical Sections** (20 points each)
  - Contact Information
  - Skills
  - Experience OR Projects
  - Education

- **Recommended Sections** (10 points each)
  - Summary/Objective
  - Projects (for freshers)
  - Certifications

- **Penalties**
  - Missing critical section: Heavy penalty
  - Missing recommended section: Medium penalty

#### 3.3 Contact Information Validity (10% weight)
- **Email Address** (required)
  - Regex validation: `[\w\.-]+@[\w\.-]+\.\w+`
  - Penalty: -35 points if missing

- **Phone Number** (required)
  - Format: `\d{3}[-.]?\d{3}[-.]?\d{4}`
  - Penalty: -30 points if missing

- **Full Name** (should be at top)
  - First line should contain only name
  - Penalty: -10 points if first line too long

- **LinkedIn Profile** (recommended)
  - Penalty: -15 points if missing

- **Location** (recommended)
  - Penalty: -10 points if not stated

#### 3.4 Keyword & Skill Matching (25% weight)
- **Technical Skills Database** (30+ skills)
  - Python, Java, JavaScript, C++, SQL, React, Node.js
  - AWS, Azure, Docker, Kubernetes, Git
  - Machine Learning, TensorFlow, PyTorch, Pandas
  - Scoring: 100 points for 12+ skills, scales down

- **Action Verbs** (25+ verbs)
  - Developed, Created, Built, Designed, Implemented
  - Led, Managed, Optimized, Achieved, Delivered
  - Scoring: 30 points for 8+ verbs, scales down

- **Metrics & Quantification**
  - Percentages: `\d+%`
  - Numbers: `\d+ (users|customers|projects)`
  - Money: `\$\d+`
  - Scoring: 30 points for 2+ metrics

- **Keyword Stuffing Detection**
  - Flags words repeated >10 times
  - Penalty: -15 points

#### 3.5 Experience & Project Presence (15% weight)
- **Fresher Detection**
  - No experience section OR <2 year mentions
  - Classified as fresher

- **For Freshers**
  - Requires Projects section
  - Penalty: Score capped at 40 if no projects
  - Requires 2+ projects for full credit

- **For Experienced**
  - Requires Experience section
  - Penalty: Score capped at 30 if no experience
  - Projects are bonus (not required)

#### 3.6 Bullet Point Structure (10% weight)
- **Bullet Point Presence**
  - Checks for `•`, `-`, `*`, `→`, `·`
  - Penalty: -40 points if no bullets found

- **Bullet Quality Analysis** (per bullet)
  - **Action Verb** (1 point): Starts with strong verb
  - **Method/Tool** (1 point): Mentions technology
  - **Outcome/Metric** (2 points): Shows measurable result
  - Weak bullet: <2 components present

- **Weak Bullet Threshold**
  - >5 weak bullets: -30 points
  - >2 weak bullets: -15 points

#### 3.7 Dates & Chronology (5% weight)
- **Date Presence**
  - Requires 2+ year mentions (19XX or 20XX)
  - Penalty: -40 points if <2 dates

- **Date Ranges**
  - Format: `YYYY - YYYY` or `YYYY - present`
  - Penalty: -20 points if no ranges

- **Chronological Order**
  - Should be reverse chronological (newest first)
  - Penalty: -15 points if not descending

#### 3.8 Score Caps (Applied After Calculation)
- **Parsing Issues** (parsability < 60): Max score = 55
- **No Projects** (fresher): Max score = 60
- **Weak Bullets** (bullet score < 60): Max score = 65
- **Insufficient Keywords** (keyword score < 50): Max score = 70

### Step 4: AI Semantic Analysis (Strict Pedagogical Mode)

#### 4.1 Parsing Assumption
- **OCR Noise Detection**
  - Checks if >5% lines contain unreadable tokens
  - Penalty: -10 points from maximum

#### 4.2 Evidence Rule
- **Skill Validation**
  - Every claimed skill must have supporting evidence
  - Evidence = explicit usage in Experience/Projects
  - Skills without evidence: 50% credit only

#### 4.3 Seniority Validation
- **Senior-Level Claims**
  - Keywords: senior, lead, architect, principal
  - Requires: 3+ years progressive experience
  - Requires: Leadership metrics
  - Penalty: -20 points if mismatch

#### 4.4 Metrics & Impact
- **Numeric Metrics Required**
  - Counts, percentages, time, scale
  - At least 1 metric per major role
  - Penalty: Up to -25 points if missing

#### 4.5 Template/Buzzword Detection
- **Generic Phrases**
  - "detail-oriented", "hard-working", "team player"
  - Without examples: -2 points each (stackable)

- **Repeated Bullets**
  - Identical bullets across roles
  - Penalty: -5 points per repeated block

#### 4.6 Depth & Ownership
- **Bullet Scoring** (4-point scale)
  - Action (1 point)
  - Method/Tech (1 point)
  - Outcome/Impact (2 points)
  - Missing outcome: 25% credit only

- **Outcome Threshold**
  - If >40% bullets lack outcome: -10 points

#### 4.7 Project Validation (Freshers)
- **Requirements**
  - At least 2 projects
  - Clear personal contribution
  - At least 1 measurable outcome
  - Missing: Score capped at 60

#### 4.8 Contradictions & Timelines
- **Skill-Experience Mismatch**
  - Claims expert but never used in projects
  - Penalty: -10 points

- **Overlapping Dates**
  - Conflicting full-time claims
  - Penalty: -15 points

#### 4.9 Score Normalization
- **Raw Score Weighting**
  - Evidence & depth: 40%
  - Metrics & impact: 30%
  - Seniority & role fit: 15%
  - Originality / non-template: 10%
  - Parsing cleanliness: 5%

- **Final Score**: Apply all deductions and caps

#### 4.10 Teachable Feedback
- **For Each Weakness**
  - Issue label
  - Exact snippet from resume
  - Severity (High/Medium/Low)
  - Step-by-step fix
  - Two rewritten examples (concise + expanded)

### Step 5: Evidence-Based Rubric Analysis (Human Reviewer Simulation)

#### 5.1 Claim-Proof Validation
- **Every Claim Requires Proof**
  - Skills, achievements, impact statements
  - Proof must be in Experience/Projects
  - Missing proof: Marked as "Unsupported Claim"
  - Points deducted aggressively

#### 5.2 Ownership Signal Analysis
- **Verb Classification**
  - **Weak**: assisted, involved, helped, participated
  - **Strong**: designed, built, implemented, optimized, led
  - Majority weak verbs: Major deduction

#### 5.3 Technical Depth Rubric
- **Three-Part Evaluation**
  1. **What** was done
  2. **How** it was done (tools/approach)
  3. **Why** it was done (reason/constraint)
  - Missing "why": Partial credit only

#### 5.4 Difficulty & Effort
- **Non-Trivial Indicators**
  - Performance tuning
  - Failure handling
  - Scalability considerations
  - Debugging complexity
  - Integration challenges

- **Tutorial Work Detection**
  - CRUD operations framed as advanced
  - Penalty applied

#### 5.5 Repeatability Test
- **Generic Bullet Detection**
  - Could apply to anyone
  - Downgrade originality score

#### 5.6 Honesty & Scope Check
- **Exaggeration Detection**
  - Inflated titles
  - Inflated scope
  - Buzzwords without evidence
  - Aggressive penalties

#### 5.7 Human Shortlist Simulation
- **Interview Decision**
  - Would you shortlist this resume?
  - Yes/No decision
  - Strongly affects final score

#### 5.8 Rubric Scoring
- **Raw Score Weighting**
  - Proof & ownership: 40%
  - Technical depth & difficulty: 30%
  - Originality & honesty: 20%
  - Hireability judgment: 10%

- **Conservative Bias**: Prefer lowering scores when unsure

#### 5.9 Educational Feedback
- **For Each Issue**
  - Why human reviewer would reject it
  - Exact change to improve trust
  - Rewritten example showing proof + ownership

### Step 6: Score Aggregation

#### 6.1 Extract Individual Scores
- Standard ATS Score (0-100)
- AI Semantic Score (0-100)
- Rubric Score (0-100)

#### 6.2 Calculate Final Score
```
Final Score = ROUND((Standard + AI + Rubric) / 3)
```

#### 6.3 Generate Analysis Summary
- **Strengths** (top 10)
  - Combined from all three analyzers
  - Deduplicated
  - Prioritized by importance

- **Weaknesses** (top 10)
  - Combined from all three analyzers
  - Deduplicated
  - Includes learning focus

### Step 7: Generate Improvements

#### 7.1 Categorization (5 categories)
1. **Keyword & Skills**
   - Missing technical skills
   - Skill usage gaps
   - Action verb improvements

2. **Content & Bullets**
   - Bullet structure fixes
   - Metric additions
   - Impact statement rewrites

3. **Projects & Experience**
   - Depth enhancements
   - Contribution clarity
   - Date additions

4. **Structure & Formatting**
   - Section ordering
   - Header improvements
   - Spacing consistency

5. **ATS Compatibility**
   - Contact information fixes
   - Table/column removal
   - Format simplification

#### 7.2 Improvement Format
Each improvement includes:
- **Issue**: What's wrong
- **Recommended Fix**: How to fix it
- **Reason**: Why it improves ATS score
- **Example** (from AI/Rubric): Rewritten bullet

### Step 8: JSON Output Generation

#### 8.1 Output Structure
```json
{
  "success": true,
  "resume_text": "extracted text...",
  "text_length": 2619,
  "evaluation": {
    "standard_ats_score": 78,
    "ai_ats_score": 90,
    "rubric_ats_score": 85,
    "final_ats_score": 84,
    "shortlist_decision": "Yes",
    "analysis_summary": {
      "strengths": [...],
      "weaknesses": [...]
    },
    "resume_improvements": {
      "keyword_and_skills": [...],
      "content_and_bullets": [...],
      "projects_and_experience": [...],
      "structure_and_formatting": [...],
      "ats_compatibility": [...]
    },
    "rubric_feedback": {
      "trusted_signals": [...],
      "red_flags": [...],
      "learning_takeaways": [...]
    }
  }
}
```