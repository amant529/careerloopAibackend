from fastapi import APIRouter, Depends
from utils import verify_token
from models import ScreeningRequest, BulkScreeningRequest
from openai_service import ats_screen, bulk_screen
from database import db

router = APIRouter()

def auth_required(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    return payload

@router.post("/ats")
async def ats(data: ScreeningRequest, token: str = Depends(auth_required)):
    result = await ats_screen(data.resume, data.jd)

    await db.analytics.insert_one({"type": "ats_screen", "user": token["email"]})
    return {"result": result}

@router.post("/bulk")
async def bulk(data: BulkScreeningRequest, token: str = Depends(auth_required)):
    results = await bulk_screen(data.resumes, data.jd)

    await db.analytics.insert_one({"type": "bulk_screen", "user": token["email"]})
    return {"candidates": results}
