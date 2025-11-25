from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

# import Groq SDK
from groq import Groq

router = APIRouter()

# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❗ERROR: GROQ_API_KEY missing from environment variables")
    
client = Groq(api_key=GROQ_API_KEY)


class ResumeRequest(BaseModel):
    name: str
    title: str
    experience: str = ""
    skills: str = ""
    achievements: str = ""
    education: str = ""
    extras: str = ""


@router.post("/generate")
async def generate_resume(req: ResumeRequest):

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Server missing GROQ_API_KEY")

    if not req.name or not req.title:
        raise HTTPException(status_code=400, detail="Name & Job Title required")

    # PROFESSIONAL RESUME FORMAT (Plain text, clean headings)
    prompt = f"""
You are an expert Indian resume writer. 
Generate a **professional ATS-optimized resume** in clean text (no bullet symbols like '-', '*', no markdown).
Use **proper headings** and structured formatting.

Details:
Name: {req.name}
Job Title: {req.title}
Experience: {req.experience}
Skills: {req.skills}
Achievements: {req.achievements}
Education: {req.education}
Extras: {req.extras}

FORMAT EXACTLY LIKE THIS (ONLY TEXT):

==============================
        {req.name.upper()}
     {req.title}
==============================

SUMMARY:
A concise 3–4 line summary written professionally.

EXPERIENCE:
• Detailed professional experience written in resume tone.

SKILLS:
• Skill1, Skill2, Skill3, ...

EDUCATION:
• Degree – College – Year

ACHIEVEMENTS:
• Achievement1
• Achievement2

ADDITIONAL INFORMATION:
• Extra notes or preferences

Make the resume look neat and structured.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        resume_text = response.choices[0].message["content"].strip()
        return {"resume": resume_text}

    except Exception as e:
        print("Resume Generation Error:", e)
        raise HTTPException(status_code=500, detail="AI processing error")
