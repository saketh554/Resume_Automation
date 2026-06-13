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


class GraphState(BaseModel):
    resume_path: str = ""
    jd_text: str = ""
    resume_struct: ResumeStruct | None = None
    jd_struct: JDStruct | None = None
    errors: list[str] = Field(default_factory=list)
