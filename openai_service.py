import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_resume(data):
    prompt = f"""
You are an expert resume writer.

Write a clean ATS resume (NO markdown, NO **).

TEMPLATE: {data['templateId']}

Name: {data['name']}
Title: {data['title']}
Experience: {data['experience']}
Skills: {data['skills']}
Achievements: {data['achievements']}

Return resume ONLY.
"""

    result = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return result.choices[0].message.content


async def ats_screen(resume, jd):
    prompt = f"""
Compare RESUME vs JD.

Return:
FIT SCORE (0-100)
STRENGTHS:
GAPS:
VERDICT (Hire / Consider / Reject)

RESUME:
{resume}

JD:
{jd}
"""

    result = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return result.choices[0].message.content


async def bulk_screen(resumes, jd):
    prompt = f"""
Each resume is separated by "---".

Return JSON array:
[{{"id":1,"label":"Candidate 1","score":92,"notes":"..","resumeSnippet":".."}}, ...]

JD:
{jd}

RESUMES:
{resumes}
"""

    result = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        return json.loads(result.choices[0].message.content)
    except:
        return []


async def chat_reply(message, role):
    prompt = f"""
You are Careerloop AI assistant.

User role: {role}
User message: {message}

Give helpful, short answers.
"""

    result = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return result.choices[0].message.content
