from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

class JobPost(BaseModel):
    title: str
    description: str
    company: str = None

@router.post("/create")
def create_job(job: JobPost):
    # MVP: just echo back. Later: save to DB and link resumes.
    return {"job_id": 1, "status": "created", "title": job.title}
