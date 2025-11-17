from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_session, Resume
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/api/builder", tags=["Resume Builder"])

class ResumeWizardInput(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    achievements: Optional[str] = None
    skills: Optional[str] = None
    projects: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    extras: Optional[str] = None
    template: str = "template-a"
    consent: bool = False              # ✅ checkbox from frontend

@router.post("/generate")
def generate_resume(data: ResumeWizardInput):
    if not data.consent:
        raise HTTPException(status_code=400, detail="Consent is required to generate and store resume.")

    system_prompt = (
        "You are a world-class resume writer and ATS optimization expert.\n"
        "Take rough bullet notes and short phrases from the user and turn them into a polished resume.\n"
        "Rules:\n"
        "- Fix grammar and clarity.\n"
        "- Convert short phrases into impactful bullet points (4–6 per section max).\n"
        "- Use strong action verbs, but do NOT invent fake experience or numbers.\n"
        "- Structure output with clear headings: NAME & CONTACT, PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE / PROJECTS, EDUCATION, CERTIFICATIONS, ACHIEVEMENTS, EXTRAS.\n"
        "- Use simple, recruiter-friendly language.\n"
    )

    user_prompt = (
        "Generate a complete resume that looks like it was typed in Word — simple headings and bullet points.\n\n"
        f"Name: {data.name}\n"
        f"Email: {data.email}\n"
        f"Target Role: {data.target_role}\n"
        f"Experience Level: {data.experience_level}\n"
        f"Achievements (raw):\n{data.achievements}\n\n"
        f"Skills (raw):\n{data.skills}\n\n"
        f"Projects / Experience (raw):\n{data.projects}\n\n"
        f"Education (raw):\n{data.education}\n\n"
        f"Certifications (raw):\n{data.certifications}\n\n"
        f"Extras (raw):\n{data.extras}\n\n"
    )

    try:
        resp = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.45,
            max_tokens=900,
        )
        resume_text = resp.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")

    with get_session() as s:
        r = Resume(
            name=data.name,
            email=data.email,
            resume_text=resume_text,
            consent=data.consent,
        )
        s.add(r)
        s.commit()
        s.refresh(r)

    html = (
        "<div class='resume-template "
        + data.template
        + "'><pre style='white-space:pre-wrap;'>"
        + resume_text
        + "</pre></div>"
    )

    return {
        "id": r.id,
        "resume": resume_text,
        "html": html,
        "template": data.template,
    }
