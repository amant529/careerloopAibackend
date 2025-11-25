from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


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

    if not GROQ_API_KEY:
        # This will show clearly on the frontend instead of generic "AI processing error"
        raise HTTPException(
            status_code=500,
            detail="Server missing GROQ_API_KEY. Set it in your Render environment."
        )

    prompt = f"""
You are a professional Indian resume writer.

Create a detailed, ATS-friendly resume from these details:

Name: {req.name}
Job Title: {req.title}
Experience (short notes): {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extra notes: {req.extras}

Rules:
- Expand short notes into full professional bullet points.
- Use clear section-wise structure: Summary, Skills, Experience, Education, Achievements, Projects (if relevant).
- Tailor tone for Indian job market (freshers + 1–5 YOE).
- Do NOT use markdown, *, ##, or any special formatting symbols.
- Return plain text only.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }

    try:
        resp = requests.post(GROQ_URL, json=data, headers=headers, timeout=60)

        if resp.status_code != 200:
            # Print full error to logs and send readable detail to frontend
            print("Groq API Error:", resp.status_code, resp.text)
            raise HTTPException(
                status_code=500,
                detail=f"Groq error {resp.status_code}: {resp.text}"
            )

        result = resp.json()
        resume_text = result["choices"][0]["message"]["content"].strip()

        if not resume_text:
            raise HTTPException(
                status_code=500,
                detail="Groq returned empty resume text."
            )

        return {"resume": resume_text}

    except HTTPException:
        # re-raise cleanly
        raise
    except Exception as e:
        print("Resume Error (unexpected):", str(e))
        raise HTTPException(status_code=500, detail="AI processing error")
