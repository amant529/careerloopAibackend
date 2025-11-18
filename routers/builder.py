from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

from openai import OpenAI

# -------- OpenAI client (server-side only) --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Render will log this; frontend will see 500
    print("WARNING: OPENAI_API_KEY not set in environment")
client = OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter(
    prefix="/api/builder",
    tags=["builder"],
)


# -------- Request models --------
class ResumeInput(BaseModel):
    name: str
    email: EmailStr
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    achievements: Optional[str] = None
    skills: Optional[str] = None
    projects: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    extras: Optional[str] = None


class SaveResumeInput(BaseModel):
    email: EmailStr
    resume: str


# -------- Routes --------
@router.post("/generate")
async def generate_resume(body: ResumeInput):
    """
    Takes rough user input and returns a polished ATS-friendly resume.
    Called from frontend at /api/builder/generate
    """
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI key not configured on server"
        )

    try:
        # Build a structured prompt
        prompt = f"""
You are an expert resume writer for ATS systems.

Create a single-page, ATS-optimized resume in plain text using the details below.
Keep it professional, concise and strongly achievement-oriented.

Use sections:
- Name & Contact
- Professional Summary
- Skills
- Experience
- Projects (if fresher, emphasize projects & internships)
- Education
- Certifications
- Extra / Achievements

User data (rough notes, clean and expand them):
Name: {body.name}
Email: {body.email}
Target Role: {body.target_role}
Experience Level: {body.experience_level}
Achievements: {body.achievements}
Skills: {body.skills}
Projects & Experience: {body.projects}
Education: {body.education}
Certifications: {body.certifications}
Extras: {body.extras}
"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You write powerful ATS-friendly resumes."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        resume_text = resp.choices[0].message.content.strip()
        return {"resume": resume_text}

    except Exception as e:
        # Log on server; send safe error to client
        print("Resume generation backend error:", repr(e))
        raise HTTPException(status_code=500, detail="AI generation failed")


@router.post("/save")
async def save_resume(body: SaveResumeInput):
    """
    For now just acknowledge save.
    In future you can connect to database to actually persist.
    Frontend just needs 200 OK.
    """
    try:
        # TODO: integrate with database if you want to really store it.
        print(f"[SAVE RESUME] {body.email} | {len(body.resume)} chars")
        return {"ok": True}
    except Exception as e:
        print("Save resume error:", repr(e))
        raise HTTPException(status_code=500, detail="Could not save resume")
