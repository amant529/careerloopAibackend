from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_session, Resume
from sqlmodel import select
from routers.resume import router as resume_router
from routers.screening import router as screening_router

app = FastAPI(title="Careerloop API (MVP)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(resume_router)
app.include_router(screening_router)

@app.get("/api/dashboard")
def dashboard():
    with get_session() as s:
        total_resumes = s.exec(select(Resume)).all()
        return {"resumes_count": len(total_resumes), "revenue_monthly": 0}
