from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from sqlmodel import select
from database import get_session, User, Resume

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class SubReq(BaseModel):
    email: EmailStr

@router.post("/subscribe")
def sub(data: SubReq):
    with get_session() as s:
        user = s.exec(select(User).where(User.email == data.email)).first()
        if not user:
            user = User(email=data.email, subscription_status="active")
            s.add(user)
        else:
            user.subscription_status = "active"
        s.commit()
    return {"message": "active"}

@router.get("/overview")
def stats():
    with get_session() as s:
        users = s.exec(select(User)).all()
        resumes = s.exec(select(Resume)).all()

    return {
        "users": len(users),
        "active_subs": len([u for u in users if u.subscription_status == "active"]),
        "resumes": len(resumes),
    }
