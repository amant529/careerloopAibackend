from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from database import get_session, Resume
from .screening import score_single, ScreenInput

router = APIRouter(prefix="/api/screening", tags=["screening_bulk"])

class BulkItem(BaseModel):
    resume_text: Optional[str] = None
    resume_id: Optional[int] = None

class BulkRequest(BaseModel):
    job_description: str
    items: List[BulkItem]

@router.post("/bulk")
def bulk_score(payload: BulkRequest):
    job_desc = payload.job_description
    results = []

    for it in payload.items:
        resume_text = (it.resume_text or "")[:30000]
        si = ScreenInput(resume_text=resume_text, job_description=job_desc)
        r = score_single(si)

        if it.resume_id:
            with get_session() as s:
                rec = s.get(Resume, it.resume_id)
                if rec:
                    rec.score = r.get("score")
                    rec.matched_keywords = ",".join(r.get("matched_keywords", []))
                    rec.ai_feedback = r.get("ai_feedback", "")
                    rec.status = "screened"
                    s.add(rec)
                    s.commit()

        results.append(
            {
                "resume_id": it.resume_id,
                "score": r.get("score"),
                "matched": r.get("matched_keywords"),
            }
        )

    return {"count": len(results), "results": results}
