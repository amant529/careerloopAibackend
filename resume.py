from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ResumeRequest(BaseModel):
    name: str
    title: str
    experience: str = ""
    skills: str = ""
    achievements: str = ""
    education: str = ""
    extras: str = ""
    templateId: str = "classic-pro"


@router.post("/generate")
async def generate_resume(req: ResumeRequest):

    if not req.name or not req.title:
        raise HTTPException(status_code=400, detail="Name & Job Title required")

    prompt = f"""
You are an expert resume writer for Indian job market.

Expand ALL short inputs into a full professional resume.

Name: {req.name}
Job Title: {req.title}
Experience: {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extras: {req.extras}

Write a fully formatted resume:
- ATS optimized
- Professional tone
- Bullet points
- Expand experience into detailed points
- DO NOT use Markdown
- Plain text only
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4
            }
        )

        data = response.json()

        resume_text = data["choices"][0]["message"]["content"]
        return {"resume": resume_text}

    except Exception as e:
        print("Resume Error:", e)
        raise HTTPException(status_code=500, detail="AI processing error")
