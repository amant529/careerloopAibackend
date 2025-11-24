from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ATSRequest(BaseModel):
    resume: str
    jd: str


class BulkRequest(BaseModel):
    resumes: str
    jd: str


@router.post("/ats")
async def ats(req: ATSRequest):

    if not req.resume.strip() or not req.jd.strip():
        raise HTTPException(status_code=400, detail="Resume & JD required")

    prompt = f"""
Analyze this resume against the job description.

Resume:
{req.resume}

JD:
{req.jd}

Give:
1. ATS Score (0-100)
2. Missing Keywords
3. Strengths
4. Weaknesses
5. Improvement Tips
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3
        )
        return {"result": response.choices[0].message.content.strip()}

    except Exception as e:
        print("ATS Error:", e)
        raise HTTPException(status_code=500, detail="ATS error")


@router.post("/bulk")
async def bulk(req: BulkRequest):

    resumes_list = req.resumes.split("\n\n---\n\n")
    output = []

    for idx, res in enumerate(resumes_list, start=1):
        prompt = f"""
Resume #{idx}:
{res}

JD:
{req.jd}

Give:
- ATS %
- Missing Skills
- Summary
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                temperature=0.3
            )

            output.append({
                "candidate": idx,
                "result": response.choices[0].message.content.strip()
            })

        except:
            continue

    return {"candidates": output}
