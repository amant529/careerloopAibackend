from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import os, pdfplumber, mammoth, tempfile

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/api/screen", tags=["Screening"])

class SingleReq(BaseModel):
    resume_text: str
    job_description: str

def score_ai(resume, jd):
    prompt = f"""
Score resume for this job and return strict JSON:
RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=400
        )
        import json
        return json.loads(res.choices[0].message.content.strip().replace("'", '"'))
    except:
        return {"score": 0, "summary": "AI failed to parse"}

@router.post("/single")
def single(req: SingleReq):
    if not req.resume_text or not req.job_description:
        raise HTTPException(status_code=400, detail="Missing input")

    return score_ai(req.resume_text, req.job_description)

def extract(file: UploadFile) -> str:
    suffix = file.filename.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as t:
        content = file.file.read()
        t.write(content)
        t.flush()
        path = t.name

    if suffix.endswith(".pdf"):
        try:
            with pdfplumber.open(path) as pdf:
                return "\n".join([p.extract_text() or "" for p in pdf.pages])
        except:
            return ""
    if suffix.endswith(".docx"):
        try:
            with open(path, "rb") as f:
                return mammoth.extract_raw_text(f).value or ""
        except:
            return ""
    return content.decode(errors="ignore")

@router.post("/bulk")
async def bulk(jd: str = Form(...), files: List[UploadFile] = File(...)):
    results = []
    for f in files:
        text = extract(f)
        if not text:
            results.append({"file": f.filename, "score": 0, "summary": "read error"})
            continue

        score = score_ai(text[:3000], jd)
        results.append({"file": f.filename, **score})

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"results": results}
