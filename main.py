from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resume import router as resume_router
from screening import router as screening_router

app = FastAPI(title="Careerloop AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://careerloop-ai-frontend.vercel.app",
        "http://localhost:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(resume_router, prefix="/api/resume")
app.include_router(screening_router, prefix="/api/screening")

@app.get("/")
def home():
    return {"status": "Careerloop AI backend running (Groq Llama 3.1)"}
