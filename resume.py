from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
import os

router = APIRouter()

# Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ResumeRequest(BaseModel):
    name: str
    title: str
    experience: str = ""
    skills: str = ""
    education: str = ""
    achievements: str = ""
    extras: str = ""
    templateId: str = "classic-pro"


@router.post("/generate")
async def generate_resume(req: ResumeRequest):

    if not req.name or not req.title:
        raise HTTPException(status_code=400, detail="Name & Job Title required")

    # --------------------
    #  MASTER PROMPT
    # --------------------
    prompt = f"""
You are a professional resume writer. 
Generate a PREMIUM, ATS-OPTIMIZED resume for the INDIAN job market.

IMPORTANT:
- Final output must be ONLY pure text.
- NO markdown, NO symbols, NO formatting marks.
- Keep clean spacing & structured headings.
- Expand minimal inputs into strong professional statements.
- Tone must be confident, crisp, and recruiter-friendly.
- Zero fluff, zero repetition.

=========================================
USER DETAILS
=========================================
Name: {req.name}
Target Job Title: {req.title}
Experience Summary: {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Additional Notes: {req.extras}

=========================================
RESUME FORMAT
=========================================

Start with:
NAME
Job Title

Then include these sections EXACTLY in this order:

PROFILE SUMMARY
- 3 to 5 powerful lines summarizing the candidate.
- Expand even minimal text into a professional summary.

KEY SKILLS
- List 6 to 12 skills as bullet points.

PROFESSIONAL EXPERIENCE
- Convert even minimal info into bullet points.
- If no experience is given, generate an excellent fresher resume.
- Each bullet should begin with an action verb.

EDUCATION
- List degrees, institutions, and years.

ACHIEVEMENTS
- Use 2 to 4 bullet points.

ADDITIONAL DETAILS
- Add relevant strengths, work preferences, remote readiness, etc.

=========================================
FINAL INSTRUCTIONS
=========================================
- DO NOT use markdown.
- DO NOT add headings not requested.
- DO NOT add fake personal details (phone, email, address).
- DO NOT add decorative lines or special characters.
- Only clean resume text with proper spacing.
=========================================

Generate the full resume now:
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1200
        )

        resume_text = response.choices[0].message["content"].strip()
        return {"resume": resume_text}

    except Exception as e:
        print("Resume Error:", e)
        raise HTTPException(status_code=500, detail="Error generating resume")
