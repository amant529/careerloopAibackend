from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ScreeningRequest(BaseModel):
    resume_text: str
    job_desc: str


@router.post("/check")
async def screen_resume(req: ScreeningRequest):

    if not req.resume_text or not req.job_desc:
        raise HTTPException(status_code=400, detail="Resume & Job Description required")

    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server missing GROQ_API_KEY. Set it in your Render environment."
        )

    prompt = f"""
You are an ATS engine.

Compare the following RESUME and JOB DESCRIPTION.

RESUME:
{req.resume_text}

JOB DESCRIPTION:
{req.job_desc}

Return the following:

1. ATS Match Score (0–100)
2. Top skills matched
3. Important missing skills / keywords
4. Specific suggestions to improve the resume to better match this job.

Output must be clear plain text. No markdown, no bullet symbols (*, -, •).
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    try:
        resp = requests.post(GROQ_URL, json=data, headers=headers, timeout=60)

        if resp.status_code != 200:
            print("Groq ATS Error:", resp.status_code, resp.text)
            raise HTTPException(
                status_code=500,
                detail=f"Groq error {resp.status_code}: {resp.text}"
            )

        result = resp.json()
        output_text = result["choices"][0]["message"]["content"].strip()

        return {"result": output_text}

    except HTTPException:
        raise
    except Exception as e:
        print("Screening Error:", str(e))
        raise HTTPException(status_code=500, detail="AI processing error")
