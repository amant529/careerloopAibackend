from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ----------- Request Model -----------
class ResumeRequest(BaseModel):
    name: str
    title: str
    experience: str = ""
    skills: str = ""
    achievements: str = ""
    education: str = ""
    extras: str = ""
    templateId: str = "classic-pro"


# ----------- Generate Resume -----------
@router.post("/generate")
async def generate_resume(req: ResumeRequest):

    if not req.name or not req.title:
        raise HTTPException(status_code=400, detail="Name and Job Title required")

    prompt = f"""
You are an expert resume writer for Indian companies and job portals.
Create a FULL professional resume using the candidate's minimal details.

-----------------------
Candidate Info
-----------------------
Name: {req.name}
Target Job Title: {req.title}

Experience (raw): {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extras: {req.extras}

-----------------------
Instructions
-----------------------
1. Expand short inputs into full professional paragraphs.
2. Improve writing quality and make it ATS-friendly.
3. Include:
   - Header
   - Professional Summary
   - Key Skills
   - Experience (expanded)
   - Education
   - Achievements
4. Add missing but relevant skills for {req.title}.
5. Do NOT use markdown (** or ##). Use plain text headings.
6. Output ONLY the final resume.

Now generate a full-page, clean, well-structured resume:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )

        resume_text = response.choices[0].message.content.strip()

        return {"resume": resume_text}

    except Exception as e:
        print("OpenAI Resume Error:", str(e))
        raise HTTPException(status_code=500, detail="OpenAI resume generation failed")
