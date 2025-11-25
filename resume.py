from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
import os

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY missing — set it in Render dashboard")

client = Groq(api_key=GROQ_API_KEY)

class ResumeRequest(BaseModel):
    name: str
    title: str
    experience: str = ""
    skills: str = ""
    education: str = ""
    achievements: str = ""
    extras: str = ""


@router.post("/generate")
async def generate_resume(req: ResumeRequest):

    if not req.name or not req.title:
        raise HTTPException(status_code=400, detail="Name and Job Title required")

    prompt = f"""
Create a professional ATS-friendly resume for the Indian job market.
Return ONLY the resume. Use clear headings, bullet points and no markdown.

Name: {req.name}
Job Title: {req.title}

Experience Summary:
{req.experience}

Skills:
{req.skills}

Education:
{req.education}

Achievements:
{req.achievements}

Additional Info:
{req.extras}

FORMAT RULES:
- Use professional clean resume structure
- Use ALL CAPS for section headings (e.g., SUMMARY, WORK EXPERIENCE)
- Expand short inputs into strong resume content
- Use crisp bullet points
- Avoid generic fluff
- No markdown (**no** ###, **no** *)
- Plain text resume only
- MUST look like real resume, not paragraphs
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        resume_text = response.choices[0].message.content.strip()
        return {"resume": resume_text}

    except Exception as e:
        print("Resume Generation Error:", e)
        raise HTTPException(status_code=500, detail="AI processing error")
