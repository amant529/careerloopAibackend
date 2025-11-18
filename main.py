from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db

from routers.auth import router as auth_router
from routers.builder import router as builder_router
from routers.screen import router as screen_router
from routers.admin import router as admin_router
from routers.analytics import router as analytics_router

app = FastAPI(title="Careerloop Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def start():
    init_db()

# Correct prefixes that match frontend calls
app.include_router(auth_router,     prefix="/auth")
app.include_router(builder_router,  prefix="/api/builder")
app.include_router(screen_router,   prefix="/api/screen")
app.include_router(admin_router,    prefix="/api/admin")
app.include_router(analytics_router,prefix="/api/analytics")

@app.get("/")
def root():
    return {"status": "ok", "service": "careerloop-ai"}
