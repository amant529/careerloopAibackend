from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import logging

router = APIRouter()

# --- OpenAI client ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger("careerloop.resume")


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
    # 1. Basic validation
    if not req.name or not req.title:
        raise HTTPException(status_code=400,
                            detail="Name & Job Title are required")

    # 2. Ensure API key exists
    if not OPENAI_API_KEY:
        # This will show clearly in frontend
        raise HTTPException(
            status_code=500,
            detail="Server missing OPENAI_API_KEY. "
                   "Set it in Render environment variables."
        )

    prompt = f"""
You are a professional resume writer for the Indian job market.

Create a complete, ATS-friendly resume in plain text (no bullets, no markdown)
using these user details:

Name: {req.name}
Target Job Title: {req.title}

Experience (short notes from user):
{req.experience}

Skills (comma separated):
{req.skills}

Education:
{req.education}

Achievements:
{req.achievements}

Any extra notes or preferences:
{req.extras}

Rules:
- Expand short notes into full professional sentences.
- Structure like a real resume: Summary, Skills, Experience, Education, Projects (if any), Achievements.
- Adapt tone for India (Bangalore, NCR, Pune, Tier 2/3 cities etc).
- DO NOT use markdown, bullets, *, or headings with ###. Plain text only.
- Optimise content for ATS systems used by Indian companies.
"""

    try:
        # 3. Use a widely-available model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        resume_text = response.choices[0].message.content.strip()
        if not resume_text:
            raise HTTPException(status_code=500,
                                detail="Empty resume generated from OpenAI")

        return {"resume": resume_text}

    except HTTPException:
        # Re-raise HTTPExceptions directly
        raise

    except Exception as e:
        # Log full error in Render logs
        logger.exception("OpenAI resume generation failed")
        # And send readable message back to frontend
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI error: {str(e)}"
        )
