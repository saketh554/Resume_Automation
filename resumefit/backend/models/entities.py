from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    parsed_struct: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    analyses: Mapped[list[Analysis]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_struct: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    analyses: Mapped[list[Analysis]] = relationship(back_populates="job_description", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    jd_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    alignment_pct: Mapped[float] = mapped_column(Float, nullable=False)
    matched_skills: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    tailored_docx_path: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    resume: Mapped[Resume] = relationship(back_populates="analyses")
    job_description: Mapped[JobDescription] = relationship(back_populates="analyses")
    skill_gaps: Mapped[list[SkillGap]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    project_edits: Mapped[list[ProjectEdit]] = relationship(back_populates="analysis", cascade="all, delete-orphan")
    cold_email: Mapped[ColdEmail | None] = relationship(back_populates="analysis", cascade="all, delete-orphan")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill: Mapped[str] = mapped_column(String(255), nullable=False)
    suggested_bullet: Mapped[str] = mapped_column(Text, nullable=False)
    mapped_projects: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    analysis: Mapped[Analysis] = relationship(back_populates="skill_gaps")


class ProjectEdit(Base):
    __tablename__ = "project_edits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    irrelevant_points: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    analysis: Mapped[Analysis] = relationship(back_populates="project_edits")


class ColdEmail(Base):
    __tablename__ = "cold_emails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    analysis: Mapped[Analysis] = relationship(back_populates="cold_email")
