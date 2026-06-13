from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectSection(BaseModel):
    section_name: str
    project_name: str
    bullets: list[str] = Field(default_factory=list)
    paragraph_indices: list[int] = Field(default_factory=list)


class ResumeSection(BaseModel):
    title: str
    paragraph_indices: list[int] = Field(default_factory=list)
    content: list[str] = Field(default_factory=list)


class ResumeStruct(BaseModel):
    contact_block: list[str] = Field(default_factory=list)
    sections: list[ResumeSection] = Field(default_factory=list)
    projects: list[ProjectSection] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)


class JDStruct(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    nice_to_haves: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    seniority: str = ""
    company: str = ""
    role_title: str = ""


class AlignmentResult(BaseModel):
    alignment_pct: float = 0.0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class GapBullet(BaseModel):
    skill: str
    bullet: str


class ProjectMapping(BaseModel):
    skill: str
    bullet: str
    project_names: list[str] = Field(default_factory=list)
    rationale: str = ""


class ProjectAuditItem(BaseModel):
    project_name: str
    irrelevant_points: list[str] = Field(default_factory=list)


class GraphState(BaseModel):
    resume_path: str = ""
    jd_text: str = ""
    resume_struct: ResumeStruct | None = None
    jd_struct: JDStruct | None = None
    alignment: AlignmentResult | None = None
    gap_bullets: list[GapBullet] = Field(default_factory=list)
    project_mappings: list[ProjectMapping] = Field(default_factory=list)
    project_audit: list[ProjectAuditItem] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
