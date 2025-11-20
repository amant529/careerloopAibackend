from fastapi import APIRouter
from models import ChatRequest
from openai_service import chat_reply
from database import db

router = APIRouter()

@router.post("/assist")
async def assist(data: ChatRequest):
    reply = await chat_reply(data.message, data.role)
    await db.analytics.insert_one({"type": "chat_message"})
    return {"reply": reply}
