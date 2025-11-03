from sqlmodel import SQLModel, create_engine, Session, Field, select
from typing import Optional
from datetime import datetime

DATABASE_URL = "sqlite:///./careerloop.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    skills: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
