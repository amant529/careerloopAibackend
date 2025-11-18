from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_session
import random

router = APIRouter(prefix="/auth", tags=["auth"])

class EmailRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    otp: str


@router.post("/send-otp")
def send_otp(payload: EmailRequest):
    otp = str(random.randint(111111, 999999))

    conn, cur = get_session()
    cur.execute("INSERT OR IGNORE INTO users (email, otp) VALUES (?, ?)", (payload.email, otp))
    cur.execute("UPDATE users SET otp=? WHERE email=?", (otp, payload.email))
    conn.commit()
    conn.close()

    # TODO: integrate email service later
    print("DEBUG OTP:", otp)
    return {"message": "OTP sent (debug mode)", "otp": otp}


@router.post("/verify")
def verify_user(payload: VerifyRequest):
    conn, cur = get_session()
    cur.execute("SELECT otp FROM users WHERE email=?", (payload.email,))
    row = cur.fetchone()

    if not row or row[0] != payload.otp:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Clear OTP
    cur.execute("UPDATE users SET otp=NULL WHERE email=?", (payload.email,))
    conn.commit()
    conn.close()

    return {"message": "Login successful"}
