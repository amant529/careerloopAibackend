from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

client = OpenAI(api_key=os.getenv("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"))


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
You are a professional resume creator for Indian job market.

Create a full resume with these details:
Name: {req.name}
Job Title: {req.title}
Experience: {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extras: {req.extras}

Instructions:
- Expand short info into detailed resume text
- ATS friendly
- No markdown
- Only plain text resume
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        resume_text = response.choices[0].message.content.strip()
        return {"resume": resume_text}

    except Exception as e:
        print("Resume Error:", e)
        raise HTTPException(status_code=500, detail="OpenAI error")
