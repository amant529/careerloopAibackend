from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_session

router = APIRouter(prefix="/api/admin", tags=["admin"])

class SubscribeRequest(BaseModel):
    email: str


@router.post("/subscribe")
def subscribe(payload: SubscribeRequest):
    conn, cur = get_session()

    # Ensure user exists
    cur.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (payload.email,))

    # Update subscription status
    cur.execute("UPDATE users SET subscribed=1 WHERE email=?", (payload.email,))
    conn.commit()
    conn.close()

    return {"message": "Subscribed successfully", "email": payload.email}


@router.get("/subscribers")
def subscribers():
    conn, cur = get_session()
    cur.execute("SELECT email FROM users WHERE subscribed=1")
    rows = cur.fetchall()
    conn.close()

    return {"subscribers": [r[0] for r in rows]}
