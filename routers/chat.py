from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlmodel import select
from database import get_session, ChatMessage
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter(prefix="/api", tags=["assistant"])

class AssistantRequest(BaseModel):
    message: str
    email: Optional[str] = None

class ChatItem(BaseModel):
    role: str
    content: str
    created_at: datetime

@router.post("/assistant")
def assistant(req: AssistantRequest):
    user_msg = req.message.strip()
    email = (req.email or "").strip() or None

    system_prompt = (
        "You are Careerloop AI, a resume and ATS improvement assistant."
        "Rules:\n"
        "- Fix grammar, clarity and bullet structure.\n"
        "- Use quantified results if provided.\n"
        "- Never add fake achievements.\n"
        "- Keep output ATS-optimized.\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ]

    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=400,
            temperature=0.4,
        )
        reply = response.choices[0].message.content.strip()
    except:
        reply = "I couldn't reach the AI engine. Try again."

    if email:
        with get_session() as session:
            session.add(ChatMessage(email=email, is_user=True, content=user_msg))
            session.add(ChatMessage(email=email, is_user=False, content=reply))
            session.commit()

    return {"reply": reply}

@router.get("/chat/history", response_model=List[ChatItem])
def history(email: str = Query(...)):
    with get_session() as session:
        rows = session.exec(
            select(ChatMessage).where(ChatMessage.email == email).order_by(ChatMessage.created_at.asc())
        ).all()

    return [
        ChatItem(
            role="user" if r.is_user else "assistant",
            content=r.content,
            created_at=r.created_at
        )
        for r in rows[-100:]  # limit last 100
    ]
