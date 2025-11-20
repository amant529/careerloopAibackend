from jose import jwt
from datetime import datetime, timedelta
import random
import os

JWT_SECRET = os.getenv("JWT_SECRET")

def create_token(email: str, role: str):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET)

def verify_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET)
    except:
        return None

def generate_otp():
    return random.randint(100000, 999999)
