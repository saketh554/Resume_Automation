from __future__ import annotations

import json
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from backend.agents.graph import build_agent_graph
from backend.agents.schemas import GraphState
from backend.app.api_schemas import AnalyzeResponse, AnalysisDetailResponse, ColdEmailResponse
from backend.app.settings import settings
from backend.models.entities import Analysis, ColdEmail, JobDescription, ProjectEdit, Resume, SkillGap
from backend.services.resume_parser import parse_resume_docx, validate_resume_file


def _serialize_model(model) -> str:
    return model.model_dump_json() if model is not None else "{}"


def save_uploaded_resume(file_path: Path, filename: str, db: Session) -> Resume:
    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    stored_path = data_dir / f"resume_{filename}"
    shutil.copyfile(file_path, stored_path)

    validate_resume_file(str(stored_path))
    resume_struct = parse_resume_docx(str(stored_path))

    record = Resume(
        filename=filename,
        stored_path=str(stored_path),
        parsed_struct=_serialize_model(resume_struct),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def run_and_persist_analysis(resume: Resume, jd_text: str, db: Session) -> AnalyzeResponse:
    state = GraphState(resume_path=resume.stored_path, jd_text=jd_text)
    result = build_agent_graph().invoke(state)

    jd_struct = result.get("jd_struct")
    alignment = result.get("alignment")
    gap_bullets = result.get("gap_bullets", [])
    project_mappings = result.get("project_mappings", [])
    project_audit = result.get("project_audit", [])
    tailored_docx_path = result.get("tailored_docx_path", "")
    cold_email = result.get("cold_email")

    if alignment is None:
        raise ValueError("Analysis failed to produce alignment output.")

    jd_record = JobDescription(raw_text=jd_text, parsed_struct=_serialize_model(jd_struct))
    db.add(jd_record)
    db.flush()

    analysis_record = Analysis(
        resume_id=resume.id,
        jd_id=jd_record.id,
        alignment_pct=alignment.alignment_pct,
        matched_skills=json.dumps(alignment.matched_skills),
        tailored_docx_path=tailored_docx_path,
    )
    db.add(analysis_record)
    db.flush()

    skill_gap_rows: list[SkillGap] = []
    for gap in gap_bullets:
        mapped_projects = []
        for mapping in project_mappings:
            if mapping.skill == gap.skill:
                mapped_projects = mapping.project_names
                break

        row = SkillGap(
            analysis_id=analysis_record.id,
            skill=gap.skill,
            suggested_bullet=gap.bullet,
            mapped_projects=json.dumps(mapped_projects),
        )
        db.add(row)
        skill_gap_rows.append(row)

    project_edit_rows: list[ProjectEdit] = []
    for item in project_audit:
        row = ProjectEdit(
            analysis_id=analysis_record.id,
            project_name=item.project_name,
            irrelevant_points=json.dumps(item.irrelevant_points),
        )
        db.add(row)
        project_edit_rows.append(row)

    if cold_email is not None:
        db.add(
            ColdEmail(
                analysis_id=analysis_record.id,
                subject=cold_email.subject,
                body=cold_email.body,
            )
        )

    db.commit()

    return AnalyzeResponse(
        analysis_id=analysis_record.id,
        alignment_pct=alignment.alignment_pct,
        matched_skills=alignment.matched_skills,
        skill_gaps=[
            {
                "skill": row.skill,
                "suggested_bullet": row.suggested_bullet,
                "mapped_projects": json.loads(row.mapped_projects),
            }
            for row in skill_gap_rows
        ],
        project_edits=[
            {
                "project_name": row.project_name,
                "irrelevant_points": json.loads(row.irrelevant_points),
            }
            for row in project_edit_rows
        ],
        tailored_resume_download_url=f"/api/analysis/{analysis_record.id}/resume.docx",
    )


def fetch_analysis_detail(analysis: Analysis) -> AnalysisDetailResponse:
    return AnalysisDetailResponse(
        analysis_id=analysis.id,
        resume_id=analysis.resume_id,
        jd_id=analysis.jd_id,
        alignment_pct=analysis.alignment_pct,
        matched_skills=json.loads(analysis.matched_skills),
        skill_gaps=[
            {
                "skill": row.skill,
                "suggested_bullet": row.suggested_bullet,
                "mapped_projects": json.loads(row.mapped_projects),
            }
            for row in analysis.skill_gaps
        ],
        project_edits=[
            {
                "project_name": row.project_name,
                "irrelevant_points": json.loads(row.irrelevant_points),
            }
            for row in analysis.project_edits
        ],
        tailored_resume_download_url=f"/api/analysis/{analysis.id}/resume.docx",
    )


def fetch_cold_email(analysis_id: int, email: ColdEmail) -> ColdEmailResponse:
    return ColdEmailResponse(
        analysis_id=analysis_id,
        subject=email.subject,
        body=email.body,
    )
