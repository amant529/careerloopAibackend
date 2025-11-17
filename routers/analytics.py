from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from sqlmodel import select
from database import get_session, AnalyticsEvent

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

class Visit(BaseModel):
    visitor_id: str
    page: Optional[str] = None

class Event(BaseModel):
    visitor_id: Optional[str] = None
    email: Optional[str] = None
    event_type: str  # visit, resume_generated, screen_single, screen_bulk

@router.post("/visit")
def save_visit(v: Visit):
    with get_session() as s:
        s.add(AnalyticsEvent(visitor_id=v.visitor_id, event_type="visit"))
        s.commit()
    return {"ok": True}

@router.post("/event")
def save_event(e: Event):
    with get_session() as s:
        s.add(AnalyticsEvent(visitor_id=e.visitor_id, email=e.email, event_type=e.event_type))
        s.commit()
    return {"ok": True}

@router.get("/summary")
def summary():
    with get_session() as s:
        events = s.exec(select(AnalyticsEvent)).all()

    visitors = set(e.visitor_id for e in events if e.visitor_id)
    return {
        "unique_visitors": len(visitors),
        "resume_generated": len([e for e in events if e.event_type == "resume_generated"]),
        "screen_single": len([e for e in events if e.event_type == "screen_single"]),
        "screen_bulk": len([e for e in events if e.event_type == "screen_bulk"]),
    }
