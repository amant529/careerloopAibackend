from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from database import init_db, get_session, Resume
from routers.upload import router as upload_router
from routers.screening import router as screening_router
from routers.screening_bulk import router as screening_bulk_router
from routers.resume import router as resume_router
from routers.job import router as job_router
from routers.shortlist import router as shortlist_router

app = FastAPI(title="Careerloop API (MVP)")

# For first deploy keep "*" to avoid CORS headaches.
# Later: change to ["https://your-frontend.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(upload_router)
app.include_router(screening_router)
app.include_router(screening_bulk_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(shortlist_router)

@app.get("/api/dashboard")
def dashboard():
    with get_session() as s:
        total_resumes = s.exec(select(Resume)).all()
        count = len(total_resumes)
    # revenue is placeholder for now
    return {"resumes_count": count, "revenue_monthly": 0}
