from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import get_session, Resume
from openai import OpenAI
import os, re
import numpy as np
from numpy.linalg import norm
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

router = APIRouter(prefix="/api/screening", tags=["screening"])

def sanitize_text(s: Optional[str]) -> str:
    return (s or "").strip()

def extract_keywords(text: str):
    toks = re.findall(r"\b[a-zA-Z0-9+#\.+]{2,}\b", (text or "").lower())
    toks = [t for t in toks if len(t) > 2]
    seen = set()
    out = []
    for t in toks:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def embed_text(text: str):
    text_clip = text[:3000]
    resp = client.embeddings.create(model=EMBED_MODEL, input=text_clip)
    vec = np.array(resp.data[0].embedding, dtype=float)
    return vec

def cosine(a, b) -> float:
    if a is None or b is None:
        return 0.0
    return float(np.dot(a, b) / (norm(a) * norm(b) + 1e-9))

class ScreenInput(BaseModel):
    resume_text: str
    job_description: str

@router.post("/score")
def score_single(payload: ScreenInput):
    resume_text = sanitize_text(payload.resume_text)
    job_desc = sanitize_text(payload.job_description)
    if not resume_text or not job_desc:
        return {"error": "resume_text and job_description are required."}

    try:
        jvec = embed_text(job_desc)
        rvec = embed_text(resume_text)
        sem_sim = cosine(jvec, rvec)
    except Exception:
        sem_sim = 0.0

    jkw = set(extract_keywords(job_desc))
    rkw = set(extract_keywords(resume_text))
    matched = list(jkw.intersection(rkw))

    kw_score = 0.0
    if jkw:
        kw_score = min(1.0, len(matched) / max(1, len(jkw)))

    final = (0.75 * sem_sim) + (0.20 * kw_score)
    final_score = round(float(final * 100), 2)

    ai_feedback = ""
    try:
        prompt = (
            f"You are a concise hiring assistant.\nJob description:\n{job_desc[:1200]}\n\n"
            f"Resume:\n{resume_text[:1600]}\n\n"
            "Give 3 concise bullets to improve this resume to match the JD."
        )
        resp = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful HR assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=180,
        )
        ai_feedback = resp.choices[0].message.content.strip()
    except Exception:
        ai_feedback = ""

    return {
        "score": final_score,
        "matched_keywords": matched[:60],
        "ai_feedback": ai_feedback,
        "sem_sim": round(sem_sim, 4),
        "kw_score": round(kw_score, 4),
    }
