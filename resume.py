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

    prompt = f"""
You are a professional Indian resume writer. Create an ATS-friendly, expanded resume based on:

Name: {req.name}
Job Title: {req.title}
Experience: {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extras: {req.extras}

Return only clean plain text. No markdown, no headings, no symbols like ** or ###.
"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        response = requests.post(GROQ_URL, json=data, headers=headers)

        if response.status_code != 200:
            print("Groq API Error:", response.text)
            raise HTTPException(status_code=500, detail="AI processing error")

        result = response.json()
        resume_text = result["choices"][0]["message"]["content"].strip()

        return {"resume": resume_text}

    except Exception as e:
        print("Resume Error:", e)
        raise HTTPException(status_code=500, detail="AI processing error")
