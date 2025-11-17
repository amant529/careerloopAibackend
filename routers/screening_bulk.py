from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from .screening import score_resume, ScreenRequest

router = APIRouter(prefix="/api/screening", tags=["Bulk Screening"])

class BulkItem(BaseModel):
    resume_id: Optional[int] = None
    resume_text: str

class BulkRequest(BaseModel):
    job_description: str
    items: List[BulkItem]

@router.post("/bulk")
def bulk_screening(req: BulkRequest):
    results = []
    for item in req.items:
        scored = score_resume(ScreenRequest(
            resume_text=item.resume_text,
            job_description=req.job_description
        ))
        results.append({
            "resume_id": item.resume_id,
            "score": scored.get("score", 0),
            "matched": scored.get("matched_keywords", []),
            "feedback": scored.get("ai_feedback", "")
        })
    # sort best first
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"results": results}
