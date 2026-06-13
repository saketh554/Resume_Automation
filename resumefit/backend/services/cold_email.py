from __future__ import annotations

from openai import OpenAI

from backend.agents.schemas import ColdEmailOutput, ResumeStruct
from backend.app.settings import settings


SYSTEM_PROMPT = (
    "You write concise, professional cold outreach emails for job applications. "
    "Use only provided resume/JD details. Do not fabricate companies, titles, or achievements."
)


def _resume_facts(resume: ResumeStruct | None) -> str:
    if resume is None:
        return ""

    top_skills = ", ".join(resume.skills[:6])
    project_names = ", ".join(project.project_name for project in resume.projects[:3])
    return f"Skills: {top_skills}\nProjects: {project_names}"


def write_cold_email_fallback(
    company: str,
    role_title: str,
    resume: ResumeStruct | None,
) -> ColdEmailOutput:
    role = role_title or "the role"
    org = company or "your team"
    skills = ", ".join((resume.skills[:3] if resume else [])) or "relevant backend and product skills"

    return ColdEmailOutput(
        subject=f"Application interest: {role}",
        body=(
            f"Hi {org},\n\n"
            f"I am excited to apply for {role}. My background includes {skills}, "
            "and I have delivered project work aligned with this opportunity.\n\n"
            "I would value the chance to discuss how I can contribute.\n\n"
            "Best regards,\n"
            "Candidate"
        ),
    )


def write_cold_email_with_llm(
    company: str,
    role_title: str,
    jd_text: str,
    resume: ResumeStruct | None,
) -> ColdEmailOutput:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.parse(
        model=settings.model_analysis if hasattr(settings, "model_analysis") else "gpt-4o",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Write a tailored cold email with subject and body.\n"
                    f"Company: {company}\n"
                    f"Role: {role_title}\n"
                    f"JD Summary:\n{jd_text}\n\n"
                    f"Resume Facts:\n{_resume_facts(resume)}"
                ),
            },
        ],
        text_format=ColdEmailOutput,
    )

    parsed = response.output_parsed
    if isinstance(parsed, ColdEmailOutput):
        return parsed
    if isinstance(parsed, dict):
        return ColdEmailOutput.model_validate(parsed)

    raise ValueError("Cold email parser returned unexpected response format.")


def write_cold_email(
    company: str,
    role_title: str,
    jd_text: str,
    resume: ResumeStruct | None,
) -> tuple[ColdEmailOutput, str]:
    try:
        return write_cold_email_with_llm(company, role_title, jd_text, resume), "llm"
    except Exception:
        return write_cold_email_fallback(company, role_title, resume), "fallback"
