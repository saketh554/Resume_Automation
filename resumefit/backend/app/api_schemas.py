from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    resume_id: int
    jd_text: str


class UploadResumeResponse(BaseModel):
    resume_id: int
    filename: str


class SkillGapResponse(BaseModel):
    skill: str
    suggested_bullet: str
    mapped_projects: list[str] = Field(default_factory=list)


class ProjectEditResponse(BaseModel):
    project_name: str
    irrelevant_points: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    analysis_id: int
    alignment_pct: float
    matched_skills: list[str] = Field(default_factory=list)
    skill_gaps: list[SkillGapResponse] = Field(default_factory=list)
    project_edits: list[ProjectEditResponse] = Field(default_factory=list)
    tailored_resume_download_url: str


class AnalysisDetailResponse(AnalyzeResponse):
    resume_id: int
    jd_id: int


class ColdEmailResponse(BaseModel):
    analysis_id: int
    subject: str
    body: str
