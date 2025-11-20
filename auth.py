from fastapi import APIRouter, HTTPException
from database import db
from utils import create_token, generate_otp
from email_service import send_otp_email

router = APIRouter()

@router.post("/send-otp")
async def send_otp(data: dict):
    email = data["email"]
    role = data["role"]

    otp = generate_otp()

    await db.users.update_one(
        {"email": email},
        {"$set": {"email": email, "role": role, "otp": otp}},
        upsert=True,
    )

    await send_otp_email(email, otp)

    return {"message": "OTP sent"}

@router.post("/verify-otp")
async def verify_otp(data: dict):
    email = data["email"]
    otp = data["otp"]

    user = await db.users.find_one({"email": email})
    if not user or str(user["otp"]) != str(otp):
        raise HTTPException(400, "Invalid OTP")

    token = create_token(email, user["role"])

    await db.users.update_one({"email": email}, {"$set": {"otp": None}})

    return {"token": token}
