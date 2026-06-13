from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database import Base, engine
from backend.app.database import get_db_session
from backend.app.api_schemas import AnalyzeRequest, AnalyzeResponse, AnalysisDetailResponse, ColdEmailResponse, UploadResumeResponse
from backend.app.settings import ensure_data_dir, settings
from backend import models  # noqa: F401
from backend.models.entities import Analysis, Resume
from backend.services.analysis_service import fetch_analysis_detail, fetch_cold_email, run_and_persist_analysis, save_uploaded_resume

app = FastAPI(title="ResumeFit API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    ensure_data_dir(settings)
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/resume", response_model=UploadResumeResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db_session)) -> UploadResumeResponse:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported.")

    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    temp_path = data_dir / f"upload_{file.filename}"
    with temp_path.open("wb") as out:
        out.write(file.file.read())

    try:
        record = save_uploaded_resume(temp_path, file.filename, db)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Failed to process resume: {exc}") from exc
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return UploadResumeResponse(resume_id=record.id, filename=record.filename)


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_resume(payload: AnalyzeRequest, db: Session = Depends(get_db_session)) -> AnalyzeResponse:
    if not payload.jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text cannot be empty.")

    resume = db.get(Resume, payload.resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        return run_and_persist_analysis(resume, payload.jd_text, db)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to run analysis: {exc}") from exc


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: int, db: Session = Depends(get_db_session)) -> AnalysisDetailResponse:
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return fetch_analysis_detail(analysis)


@app.get("/api/analysis/{analysis_id}/resume.docx")
def download_tailored_resume(analysis_id: int, db: Session = Depends(get_db_session)) -> FileResponse:
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if not analysis.tailored_docx_path:
        raise HTTPException(status_code=404, detail="Tailored resume not available.")

    file_path = Path(analysis.tailored_docx_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Tailored resume file missing.")

    return FileResponse(path=file_path, filename=file_path.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.get("/api/analysis/{analysis_id}/email", response_model=ColdEmailResponse)
def get_cold_email(analysis_id: int, db: Session = Depends(get_db_session)) -> ColdEmailResponse:
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if analysis.cold_email is None:
        raise HTTPException(status_code=404, detail="Cold email not found.")
    return fetch_cold_email(analysis.id, analysis.cold_email)
