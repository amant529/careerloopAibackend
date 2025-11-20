from pydantic import BaseModel, EmailStr
from typing import Optional, Any

class User(BaseModel):
    email: EmailStr
    role: str
    otp: Optional[int] = None

class ResumeRequest(BaseModel):
    name: str
    title: str
    experience: str
    skills: str
    achievements: str
    templateId: str

class ScreeningRequest(BaseModel):
    resume: str
    jd: str

class BulkScreeningRequest(BaseModel):
    resumes: str
    jd: str

class ChatRequest(BaseModel):
    message: str
    role: str

class AnalyticsEvent(BaseModel):
    type: str
    meta: Optional[Any] = None
