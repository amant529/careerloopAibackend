from fastapi import APIRouter, Header, HTTPException
from sqlmodel import select
from database import get_session, Resume

router = APIRouter(prefix="/api/admin", tags=["Admin"])

ADMIN_KEY = "SUPER_SIMPLE_ADMIN_KEY"  # change & move to env var later

def check_admin(x_admin_key: str | None):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Not authorized")

@router.get("/overview")
def overview(x_admin_key: str = Header(None)):
    check_admin(x_admin_key)

    with get_session() as s:
        resumes = s.exec(select(Resume)).all()
        total = len(resumes)
        consents = len([r for r in resumes if r.consent])
        screened = len([r for r in resumes if r.score is not None])
        shortlisted = len([r for r in resumes if r.status == "shortlisted"])

    return {
        "total_resumes": total,
        "with_consent": consents,
        "screened": screened,
        "shortlisted": shortlisted,
    }

@router.get("/resumes")
def list_resumes(x_admin_key: str = Header(None), limit: int = 50):
    check_admin(x_admin_key)

    with get_session() as s:
        rows = s.exec(select(Resume).order_by(Resume.created_at.desc())).all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "score": r.score,
            "status": r.status,
            "consent": r.consent,
            "created_at": r.created_at,
        }
        for r in rows[:limit]
    ]
