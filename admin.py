from fastapi import APIRouter, Depends, HTTPException
from utils import verify_token
from database import db

router = APIRouter()

def admin_required(token: str):
    payload = verify_token(token)
    if not payload or payload["role"] != "admin":
        raise HTTPException(403, "You are not admin")
    return payload

@router.get("/dashboard")
async def dashboard(_: dict = Depends(admin_required)):
    users = await db.users.count_documents({})
    resumes = await db.analytics.count_documents({"type": "resume_generated"})
    ats = await db.analytics.count_documents({"type": "ats_screen"})
    bulk = await db.analytics.count_documents({"type": "bulk_screen"})

    return {
        "users": users,
        "resumes": resumes,
        "ats": ats,
        "bulk": bulk
    }
