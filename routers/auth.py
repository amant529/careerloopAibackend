from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from sqlmodel import select
from database import get_session, User
from email_utils import send_otp_email
import random

router = APIRouter(prefix="/auth", tags=["Auth"])

class EmailReq(BaseModel):
    email: EmailStr

class VerifyReq(BaseModel):
    email: EmailStr
    otp: str

@router.post("/send-otp")
def send_otp(data: EmailReq):
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=5)

    with get_session() as session:
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user:
            user = User(email=data.email)
            session.add(user)
            session.flush()

        user.otp = otp
        user.otp_expiry = expiry
        session.commit()

    send_otp_email(data.email, otp)
    return {"message": "OTP sent"}

@router.post("/verify")
def verify(data: VerifyReq):
    with get_session() as session:
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user or not user.otp:
            raise HTTPException(status_code=400, detail="OTP not requested")

        if datetime.utcnow() > user.otp_expiry:
            raise HTTPException(status_code=400, detail="OTP expired")

        if data.otp != user.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        user.otp = None
        user.otp_expiry = None
        session.commit()

    return {"message": "verified"}
