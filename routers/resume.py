from fastapi import APIRouter
from pydantic import BaseModel
from database import get_session, Resume

router = APIRouter(prefix="/api/builder", tags=["builder"])

class ResumeInput(BaseModel):
    name: str
    email: str = None
    summary: str = None
    skills: str = None
    experience: str = None
    template: str = "template-a"

@router.post("/generate")
def generate_resume(data: ResumeInput):
    lines = []
    lines.append(data.name or "")
    if data.email:
        lines.append(data.email)
    if data.summary:
        lines.append("\nProfessional Summary\n" + data.summary)
    if data.experience:
        lines.append("\nExperience\n" + data.experience)
    if data.skills:
        lines.append("\nSkills\n" + data.skills)

    ai_resume = "\n".join(lines)

    with get_session() as s:
        r = Resume(name=data.name, email=data.email, resume_text=ai_resume)
        s.add(r)
        s.commit()
        s.refresh(r)

    html_resume = (
        f"<div class='resume-template {data.template}'>"
        f"<h1>{data.name}</h1>"
        f"<pre style='white-space:pre-wrap'>{ai_resume}</pre>"
        f"</div>"
    )

    return {
        "id": r.id,
        "name": data.name,
        "html_resume": html_resume,
        "template_used": data.template,
    }
