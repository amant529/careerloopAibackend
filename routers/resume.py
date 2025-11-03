from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/api/resume", tags=["resume"])

# Input schema for resume data
class ResumeInput(BaseModel):
    name: str
    summary: str
    skills: str
    experience: str
    template: str = "classic"  # optional template name


@router.post("/")
def create_resume(data: ResumeInput):
    # Prompt for AI
    prompt = f"""
    Create a professional, well-written resume for the following person.
    Name: {data.name}
    Summary: {data.summary}
    Skills: {data.skills}
    Experience: {data.experience}

    Format it nicely with sections like:
    - Professional Summary
    - Key Skills
    - Work Experience
    - Education
    - Achievements
    """

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract text
    ai_resume = response.choices[0].message.content.strip()

    # Convert resume text into basic HTML
    html_resume = f"""
    <div class="resume-template {data.template}">
        <h1>{data.name}</h1>
        <pre style='font-family: sans-serif; white-space: pre-wrap;'>{ai_resume}</pre>
    </div>
    """

    # Return structured response
    return {
        "name": data.name,
        "html_resume": html_resume,
        "template_used": data.template
    }
