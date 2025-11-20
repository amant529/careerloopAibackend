from fastapi import APIRouter
from models import AnalyticsEvent
from database import db

router = APIRouter()

@router.post("/event")
async def event(ev: AnalyticsEvent):
    await db.analytics.insert_one(ev.dict())
    return {"success": True}
