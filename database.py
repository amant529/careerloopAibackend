from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./careerloop.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# USERS
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    subscription_status: str = Field(default="inactive")  # inactive | active
    otp: Optional[str] = None
    otp_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# RESUMES
class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    email: Optional[str] = None
    resume_text: Optional[str] = None
    consent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ANALYTICS EVENTS
class AnalyticsEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    visitor_id: Optional[str] = Field(default=None, index=True)
    email: Optional[str] = Field(default=None, index=True)
    event_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
