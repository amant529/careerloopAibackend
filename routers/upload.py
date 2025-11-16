from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
from database import get_session, Resume
import uuid
import mammoth
import pdfplumber

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def extract_text_from_docx(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            res = mammoth.extract_raw_text(f)
            return res.value or ""
    except Exception:
        return ""

def extract_text_from_pdf(path: Path) -> str:
    texts = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                texts.append(p.extract_text() or "")
    except Exception:
        return ""
    return "\n".join(texts)

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    name: str = Form(None),
    email: str = Form(None),
    job_id: int = Form(None),
):
    ext = Path(file.filename).suffix.lower()
    uid = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{uid}{ext}"

    content = await file.read()
    with open(dest, "wb") as fh:
        fh.write(content)

    text = ""
    try:
        if ext == ".docx":
            text = extract_text_from_docx(dest)
        elif ext == ".pdf":
            text = extract_text_from_pdf(dest)
        else:
            try:
                text = content.decode("utf-8", errors="replace")
            except Exception:
                text = ""
    except Exception:
        text = ""

    with get_session() as s:
        r = Resume(
            name=name,
            email=email,
            filename=file.filename,
            file_path=str(dest),
            resume_text=text,
            job_id=job_id,
        )
        s.add(r)
        s.commit()
        s.refresh(r)

    return {
        "id": r.id,
        "filename": r.filename,
        "text_snippet": (r.resume_text or "")[:2000],
    }
