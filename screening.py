from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class ScreeningRequest(BaseModel):
    resume_text: str
    job_desc: str


@router.post("/check")
async def screen_resume(req: ScreeningRequest):

    if not req.resume_text or not req.job_desc:
        raise HTTPException(status_code=400, detail="Resume & JD required")

    prompt = f"""
You are an ATS scoring engine.

Compare this RESUME and JOB DESCRIPTION:

RESUME:
{req.resume_text}

JOB DESCRIPTION:
{req.job_desc}

Give:
1. ATS Match Score (0–100)
2. Skills matched
3. Skills missing
4. Suggestions to improve resume

Output in clean plain text (NO markdown).
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
        )

        data = response.json()
        output = data["choices"][0]["message"]["content"]

        return {"result": output}

    except Exception as e:
        print("Screening Error:", e)
        raise HTTPException(status_code=500, detail="AI processing error")
