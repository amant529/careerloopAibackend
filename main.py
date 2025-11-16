from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_session, Resume
from sqlmodel import select

# Routers
from routers.upload import router as upload_router
from routers.screening import router as screening_router
from routers.screening_bulk import router as bulk_router
from routers.resume import router as resume_router
from routers.job import router as job_router
from routers.shortlist import router as shortlist_router
from routers.chat import router as chat_router

app = FastAPI(title="Careerloop AI Backend")

# CORS for Render (Backend) + Vercel (Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change later for production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
def startup():
    init_db()

# Include routes
app.include_router(upload_router)
app.include_router(screening_router)
app.include_router(bulk_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(shortlist_router)
app.include_router(chat_router)

@app.get("/api/dashboard")
def dashboard():
    with get_session() as session:
        total = len(session.exec(select(Resume)).all())
    return {"resumes": total, "message": "Dashboard data returned"}
