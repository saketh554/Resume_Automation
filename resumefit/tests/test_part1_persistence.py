import tempfile
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from backend.app.database import Base
from backend.models.entities import Analysis, JobDescription, Resume


def test_schema_creates_from_clean_state() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "clean.db"
        engine = create_engine(f"sqlite:///{db_path}")
        try:
            Base.metadata.create_all(bind=engine)

            with Session(engine) as session:
                tables = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                ).scalars().all()
        finally:
            engine.dispose()

        expected_tables = {
            "analyses",
            "cold_emails",
            "job_descriptions",
            "project_edits",
            "resumes",
            "skill_gaps",
        }
        assert expected_tables.issubset(set(tables))


def test_analysis_persists_after_engine_restart() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "persist.db"
        db_url = f"sqlite:///{db_path}"

        first_engine = create_engine(db_url)
        try:
            Base.metadata.create_all(bind=first_engine)

            with Session(first_engine) as session:
                resume = Resume(filename="resume.docx", stored_path="data/resume.docx", parsed_struct="{}")
                jd = JobDescription(raw_text="Backend engineer role", parsed_struct="{}")
                session.add_all([resume, jd])
                session.flush()

                analysis = Analysis(
                    resume_id=resume.id,
                    jd_id=jd.id,
                    alignment_pct=82.5,
                    matched_skills='["python", "fastapi"]',
                )
                session.add(analysis)
                session.commit()
                analysis_id = analysis.id
        finally:
            first_engine.dispose()

        second_engine = create_engine(db_url)
        try:
            with Session(second_engine) as session:
                loaded = session.get(Analysis, analysis_id)
                assert loaded is not None
                assert loaded.alignment_pct == 82.5
                assert loaded.matched_skills == '["python", "fastapi"]'
        finally:
            second_engine.dispose()
