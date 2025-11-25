from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
import os

router = APIRouter()

# Correct Groq client
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

    prompt = f"""
You are a professional Indian resume creator.
Generate a detailed ATS-friendly resume based on:

Name: {req.name}
Job Title: {req.title}
Experience: {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extras: {req.extras}

- Expand short points
- Use professional tone
- No markdown, no headings like ### or **
- Return plain clean text only
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        resume_text = response.choices[0].message["content"].strip()
        return {"resume": resume_text}

    except Exception as e:
        print("Groq Resume Error:", e)
        raise HTTPException(status_code=500, detail="AI processing error")
