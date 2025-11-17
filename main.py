from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import init_db
from routers.upload import router as upload_router
from routers.resume import router as resume_router
from routers.screening import router as screening_router
from routers.screening_bulk import router as bulk_screening_router
from routers.shortlist import router as shortlist_router
from routers.chat import router as chat_router
from routers.job import router as job_router
from routers.admin import router as admin_router

app = FastAPI(title="Careerloop AI Backend")

# CORS – later restrict to your Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
def startup():
  init_db()

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # In real production write to logs/monitoring here
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error, try again.", "error": str(exc)},
    )

# Routers
app.include_router(upload_router)
app.include_router(resume_router)
app.include_router(screening_router)
app.include_router(bulk_screening_router)
app.include_router(shortlist_router)
app.include_router(chat_router)
app.include_router(job_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"status": "Careerloop backend up", "version": "phase-1"}
