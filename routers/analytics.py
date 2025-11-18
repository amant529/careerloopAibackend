from fastapi import APIRouter
from datetime import datetime
from database import save_visit, save_event

router = APIRouter()

@router.post("/visit")
def track_visit(data: dict):
    visitor_id = data.get("visitor_id")
    page = data.get("page", "-")
    ts = datetime.utcnow().isoformat()

    save_visit(visitor_id, page, ts)
    return {"status": "ok", "tracked": True}

@router.post("/event")
def track_event(data: dict):
    visitor_id = data.get("visitor_id")
    email = data.get("email", None)
    event_type = data.get("event_type", "-")
    ts = datetime.utcnow().isoformat()

    save_event(visitor_id, email, event_type, ts)
    return {"status": "ok", "event_logged": True}
