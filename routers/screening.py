from fastapi import APIRouter
from pydantic import BaseModel
from difflib import SequenceMatcher
import re
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables (for OpenAI key)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/api/screening", tags=["screening"])

class ScreenInput(BaseModel):
    resume_text: str
    job_description: str


def similarity(a: str, b: str) -> float:
    """Quick normalized similarity as baseline (0–1)."""
    matcher = SequenceMatcher(None, a.lower(), b.lower())
    return matcher.ratio()


def extract_keywords(text: str):
    """Extract simple keywords (longer than 3 chars)."""
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    unique = list(dict.fromkeys(words))
    return unique


@router.post("/match")
def match_resume(payload: ScreenInput):
    """Compare resume with job description and score similarity."""
    resume = payload.resume_text or ""
    jd = payload.job_description or ""

    # 1️⃣ Basic text similarity score
    base_score = round(similarity(resume, jd) * 100, 2)

    # 2️⃣ Extract matching keywords
    jd_keywords = extract_keywords(jd)
    matched = [kw for kw in jd_keywords if kw in resume.lower()]

    # 3️⃣ (Optional) AI feedback using GPT — makes it “smart”
    prompt = f"""
    You are an HR screening assistant.
    Compare this resume and job description. 
    Give a short feedback about the candidate’s fit (max 3 sentences).
    
    Resume:
    {resume}

    Job Description:
    {jd}
    """

    try:
        ai_feedback = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a skilled HR assistant."},
                {"role": "user", "content": prompt}
            ]
        ).choices[0].message.content.strip()
    except Exception:
        ai_feedback = "AI feedback unavailable (check OpenAI key)."

    # 4️⃣ Return combined results
    return {
        "match_score": base_score,
        "matched_keywords": matched[:20],
        "ai_feedback": ai_feedback
    }
