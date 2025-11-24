from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

# Create client correctly
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
You are a professional resume creator for the Indian job market.

Create a full-length ATS-friendly resume based on the following info:

Name: {req.name}
Job Title: {req.title}
Experience: {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Additional Info: {req.extras}

Instructions:
- Expand all short inputs into professional full paragraphs.
- Write a fully polished resume with all standard sections.
- No markdown, only plain text.
- No headings like ** or ##.
- Make it formal, clear, and HR-ready.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800  # ← CRITICAL FIX
        )

        text = response.choices[0].message.content.strip()
        return {"resume": text}

    except Exception as e:
        print("OPENAI ERROR:", e)  # Now you can see real errors in Render logs
        raise HTTPException(status_code=500, detail="OpenAI processing error")
