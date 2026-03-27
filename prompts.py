"""
Prompt templates for AI Recruiter Copilot.
Each function returns a crafted prompt string for Gemini.
"""


def summary_prompt(context: str) -> str:
    return f"""
You are a senior technical recruiter with 10+ years of experience evaluating candidates.

RESUME CONTEXT:
{context}

Task: Summarize this candidate in exactly 5 bullet points.
Focus on:
- Total years of experience
- Core technical skills
- Most impressive achievement or project
- Industry/domain background
- Career trajectory / growth

Format each bullet with an emoji prefix. Be concise, specific, and factual.
"""


def strengths_risks_prompt(context: str, jd: str) -> str:
    return f"""
You are a senior technical recruiter evaluating candidate fit.

RESUME CONTEXT:
{context}

JOB DESCRIPTION:
{jd}

Task: Provide a structured strengths and risks analysis.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

**TOP 3 STRENGTHS:**
1. [Strength with specific evidence from resume]
2. [Strength with specific evidence from resume]
3. [Strength with specific evidence from resume]

**TOP 3 RISKS / GAPS:**
1. [Risk with explanation of impact on job performance]
2. [Risk with explanation of impact on job performance]
3. [Risk with explanation of impact on job performance]

**OVERALL ASSESSMENT:**
[2-3 sentence summary of whether this candidate is worth moving forward]
"""


def questions_prompt(context: str, jd: str) -> str:
    return f"""
You are an expert technical interviewer preparing for a candidate interview.

RESUME CONTEXT:
{context}

JOB DESCRIPTION:
{jd}

Task: Generate 5 targeted interview questions based on this specific candidate's background.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

**TECHNICAL QUESTIONS:**
1. [Specific technical question tied to their experience]
   → What to look for: [Key answer signals]

2. [Another technical question]
   → What to look for: [Key answer signals]

**BEHAVIORAL QUESTIONS:**
3. [Behavioral question using STAR method]
   → What to look for: [Key answer signals]

4. [Another behavioral question]
   → What to look for: [Key answer signals]

**DEEP-DIVE QUESTION:**
5. [A challenging, scenario-based question that tests depth]
   → What to look for: [Key answer signals]
"""


def scoring_prompt(context: str, jd: str) -> str:
    return f"""
You are a data-driven technical recruiter scoring a candidate objectively.

RESUME CONTEXT:
{context}

JOB DESCRIPTION:
{jd}

Task: Score this candidate across 4 dimensions. Be objective and strict.

Return ONLY a valid JSON object. No explanation before or after. No markdown. No code fences.
The JSON must have exactly these keys:

{{
  "Skill Match": <integer 0-5>,
  "Experience": <integer 0-5>,
  "Stability": <integer 0-5>,
  "Domain": <integer 0-5>,
  "Final Score": <integer 0-20, sum of above>,
  "Skill Match Reason": "<one sentence>",
  "Experience Reason": "<one sentence>",
  "Stability Reason": "<one sentence>",
  "Domain Reason": "<one sentence>",
  "Reason": "<2-3 sentence overall justification>",
  "Recommendation": "<exactly one of: Strong Hire, Hire, Maybe, No Hire>"
}}
"""


def compare_prompt(context1: str, context2: str, jd: str) -> str:
    return f"""
You are a senior recruiter comparing two candidates for the same role.

CANDIDATE A RESUME:
{context1}

CANDIDATE B RESUME:
{context2}

JOB DESCRIPTION:
{jd}

Task: Compare both candidates head-to-head and recommend who to move forward.

FORMAT YOUR RESPONSE LIKE THIS:

**HEAD-TO-HEAD COMPARISON:**
| Criteria          | Candidate A | Candidate B |
|-------------------|-------------|-------------|
| Technical Skills  | [rating]    | [rating]    |
| Experience        | [rating]    | [rating]    |
| Cultural Fit      | [rating]    | [rating]    |
| Growth Potential  | [rating]    | [rating]    |

**WINNER: [Candidate A / Candidate B / Tie]**

**REASONING:**
[3-4 sentences explaining the decision]
"""


def why_score_prompt(context: str, score_data: dict) -> str:
    return f"""
You are a recruiter explaining a candidate evaluation score in plain English.

CANDIDATE CONTEXT:
{context}

SCORES GIVEN:
- Skill Match: {score_data.get('Skill Match', '?')}/5
- Experience: {score_data.get('Experience', '?')}/5
- Stability: {score_data.get('Stability', '?')}/5
- Domain: {score_data.get('Domain', '?')}/5
- Final Score: {score_data.get('Final Score', '?')}/20
- Recommendation: {score_data.get('Recommendation', '?')}

Task: In 3-4 sentences, explain to the hiring manager WHY this candidate received this score.
Be specific — reference actual details from the resume context.
Write in plain, conversational English. No bullet points.
"""


def skill_match_prompt(context: str, jd_skills: str) -> str:
    return f"""
You are a technical recruiter matching a candidate's skills against job requirements.

CANDIDATE RESUME CONTEXT:
{context}

REQUIRED SKILLS FROM JOB DESCRIPTION:
{jd_skills}

Task: For each required skill, state whether the candidate has it.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS (one line per skill):
✅ [Skill] — [brief evidence from resume]
⚠️ [Skill] — [partial match or adjacent skill found]
❌ [Skill] — [not found in resume]

Be concise. One line per skill. Only list the required skills provided.
"""


def decision_prompt(context: str, score_data: dict, jd: str) -> str:
    return f"""
You are a senior recruiter making a final hiring recommendation.

CANDIDATE CONTEXT:
{context}

JOB DESCRIPTION SUMMARY:
{jd[:500]}

EVALUATION SCORES:
- Skill Match: {score_data.get('Skill Match', '?')}/5
- Experience: {score_data.get('Experience', '?')}/5
- Stability: {score_data.get('Stability', '?')}/5
- Domain: {score_data.get('Domain', '?')}/5
- Final Score: {score_data.get('Final Score', '?')}/20

Task: Give a single clear hiring decision and ONE concise sentence explaining why.

FORMAT EXACTLY LIKE THIS:
DECISION: [Strong Hire / Hire / Consider / Reject]
REASON: [One sentence, max 20 words, specific to this candidate]
"""


def extract_jd_skills_prompt(jd: str) -> str:
    return f"""
Extract the key required skills from this job description.

JOB DESCRIPTION:
{jd}

Return ONLY a comma-separated list of skills. No numbering. No explanation. No extra text.
Example: Python, Django, PostgreSQL, REST APIs, Docker, AWS

Skills:
"""
