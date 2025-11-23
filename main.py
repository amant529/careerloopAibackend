from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from resume import router as resume_router
from screening import router as screening_router
from chat import router as chat_router
from analytics import router as analytics_router
from admin import router as admin_router

app = FastAPI(title="Careerloop AI Backend")

# 🚀 FIXED CORS — THIS IS REQUIRED FOR OTP TO WORK
origins = [
    "https://careerloopai.com",
    "https://www.careerloopai.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "https://careerloopaibackend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # <--- allows PRE-FLIGHT OPTIONS (fix)
    allow_headers=["*"],      # <--- allows JSON & custom headers
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
