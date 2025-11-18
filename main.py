from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Validate OpenAI key exists (for debugging only, removed in production)
OPENAI_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")

print("🔍 DEBUG: OpenAI key loaded ->", "YES" if OPENAI_KEY else "❌ MISSING")

from routers.auth import router as auth_router
from routers.builder import router as builder_router
from routers.screen import router as screen_router
from routers.admin import router as admin_router
from routers.analytics import router as analytics_router

# Init DB if needed
from database import init_db

app = FastAPI(
    title="Careerloop AI Backend",
    version="1.2",
    description="Resume Builder, Screening, Analytics, Admin API"
)

# ------------------- CORS (keep open for MVP) -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- STARTUP LOGIC -------------------
@app.on_event("startup")
def startup_event():
    print("🚀 Careerloop backend starting...")
    try:
        init_db()
        print("📦 Database initialized")
    except Exception as e:
        print("❌ Database init failed:", str(e))

    if not OPENAI_KEY:
        print("❌ ERROR: Missing OpenAI API key — Resume generation will fail!")
    else:
        print("✅ OpenAI key detected")

# ------------------- ROUT
