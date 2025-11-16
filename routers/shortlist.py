from fastapi import APIRouter
from database import get_session, Resume

router = APIRouter(prefix="/api/resume", tags=["resume_actions"])

@router.post("/{id}/shortlist")
def mark_shortlist(id: int):
    with get_session() as s:
        rec = s.get(Resume, id)
        if not rec:
            return {"error": "not found"}
        rec.status = "shortlisted"
        s.add(rec)
        s.commit()
    return {"ok": True}
