from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from resume import router as resume_router
from screening import router as screening_router
from chat import router as chat_router
from analytics import router as analytics_router
from admin import router as admin_router

app = FastAPI(title="Careerloop AI Backend")

# TEMPORARY LAUNCH FIX — ALLOW ALL ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth_router, prefix="/auth")
app.include_router(resume_router, prefix="/api/resume")
app.include_router(screening_router, prefix="/api/screening")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(analytics_router, prefix="/api/analytics")
app.include_router(admin_router, prefix="/admin")

@app.get("/")
def home():
    return {"status": "Careerloop AI backend running"}
