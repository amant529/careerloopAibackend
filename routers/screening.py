from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/api/screening", tags=["Screening"])

class ScreenRequest(BaseModel):
    resume_text: str
    job_description: str

@router.post("/score")
def score_resume(data: ScreenRequest):
    if not data.resume_text.strip() or not data.job_description.strip():
        raise HTTPException(status_code=400, detail="resume_text and job_description are required.")

    system_msg = (
        "You are an ATS + HR screening engine.\n"
        "You compare a resume to a job description and return JSON:\n"
        "{ \"score\": number(0-100), \"matched_keywords\": [..], \"ai_feedback\": \"short feedback\" }"
    )

    user_msg = f"RESUME:\n{data.resume_text}\n\nJOB DESCRIPTION:\n{data.job_description}"

    try:
        resp = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        raw = resp.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI screening failed: {e}")

    try:
        # Try parse JSON
        data_json = json.loads(raw.replace("'", '"'))
        return data_json
    except Exception:
        # fallback
        return {"score": 0, "matched_keywords": [], "ai_feedback": raw}
