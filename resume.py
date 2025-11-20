from fastapi import APIRouter, Depends, HTTPException
from utils import verify_token
from openai_service import generate_resume
from models import ResumeRequest
from database import db

router = APIRouter()

def auth_required(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    return payload

@router.post("/generate")
async def generate(data: ResumeRequest, token: str = Depends(auth_required)):
    text = await generate_resume(data.dict())

    await db.analytics.insert_one({
        "type": "resume_generated",
        "user": token["email"]
    })

    return {"resume": text}
