from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import openai

router = APIRouter()

# Load OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")


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


# ----------- Main Resume Generation Route -----------
@router.post("/generate")
async def generate_resume(req: ResumeRequest):
    """
    PUBLIC ENDPOINT (NO AUTH for beta launch)
    Takes minimal user info and converts it into
    a full professional resume using OpenAI.
    """

    if not req.name or not req.title:
        raise HTTPException(status_code=400, detail="Name and Job Title are required")

    # Build a strong prompt
    prompt = f"""
You are an expert resume writer for the Indian job market. 
Create a **full professional resume** using the details below.
If some sections are short, expand them naturally with ATS-friendly language.

---------------------------
Candidate Information
---------------------------
Name: {req.name}
Target Job Title: {req.title}

Experience (raw): {req.experience}
Skills: {req.skills}
Education: {req.education}
Achievements: {req.achievements}
Extras: {req.extras}

---------------------------
Instructions
---------------------------
1. Write a **full-page resume**, not bullet inputs.
2. Expand short experience (e.g., "fresher") into a proper Experience section.
3. For freshers, generate internship-style descriptions.
4. Rewrite skills into a clean formatted Skills section.
5. Add strong ATS keywords for the job title: {req.title}
6. Structure the resume properly:
   - Header with Name + Title
   - Professional Summary (expand intelligently)
   - Skills Section
   - Experience (expanded)
   - Education
   - Achievements
7. Use professional, simple, modern English.
8. Do NOT write markdown, only pure text.
9. Do NOT include headings like ** or ###. Use plain text headings.

Final Output Format:
-------------------------
Full Resume Text Only
-------------------------
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        ai_resume = response["choices"][0]["message"]["content"].strip()

        return {"resume": ai_resume}

    except Exception as e:
        print("Resume API Error:", e)
        raise HTTPException(status_code=500, detail="OpenAI resume generation failed")
