from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Optional
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./careerloop.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    email: Optional[str] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
    resume_text: Optional[str] = None
    parsed_json: Optional[str] = None
    score: Optional[float] = None
    matched_keywords: Optional[str] = None
    ai_feedback: Optional[str] = None
    status: Optional[str] = Field(default="new")  # new, screened, shortlisted, rejected
    job_id: Optional[int] = None
    consent: bool = Field(default=False)          # ✅ user consent stored
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, index=True)
    is_user: bool = Field(default=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
