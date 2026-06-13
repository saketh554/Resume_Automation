from __future__ import annotations

from pathlib import Path

from docx import Document

from backend.agents.schemas import ProjectSection, ResumeSection, ResumeStruct

SECTION_HEADERS = {
    "experience",
    "work experience",
    "projects",
    "skills",
    "education",
    "summary",
}


def _is_section_header(text: str) -> bool:
    normalized = text.strip().lower().rstrip(":")
    return normalized in SECTION_HEADERS


def parse_resume_docx(path: str) -> ResumeStruct:
    document = Document(path)
    paragraphs = [p.text.strip() for p in document.paragraphs]

    non_empty = [(idx, text) for idx, text in enumerate(paragraphs) if text]
    if not non_empty:
        raise ValueError("Resume document is empty.")

    sections: list[ResumeSection] = []
    projects: list[ProjectSection] = []
    skills: list[str] = []
    education: list[str] = []

    current_section_title = "contact"
    current_indices: list[int] = []
    current_content: list[str] = []
    contact_block: list[str] = []

    for idx, text in non_empty:
        if _is_section_header(text):
            if current_section_title != "contact":
                sections.append(
                    ResumeSection(
                        title=current_section_title,
                        paragraph_indices=current_indices.copy(),
                        content=current_content.copy(),
                    )
                )
            current_section_title = text.strip().rstrip(":")
            current_indices = []
            current_content = []
            continue

        if current_section_title == "contact":
            contact_block.append(text)
        else:
            current_indices.append(idx)
            current_content.append(text)

            lowered = current_section_title.lower()
            if lowered == "skills":
                skills.extend([token.strip() for token in text.replace("|", ",").split(",") if token.strip()])
            if lowered == "education":
                education.append(text)
            if lowered in {"projects", "experience", "work experience"} and text.startswith(("-", "*")):
                project_name = current_content[0] if current_content else f"{current_section_title} item"
                projects.append(
                    ProjectSection(
                        section_name=current_section_title,
                        project_name=project_name,
                        bullets=[text.lstrip("-* ")],
                        paragraph_indices=[idx],
                    )
                )

    if current_section_title != "contact":
        sections.append(
            ResumeSection(
                title=current_section_title,
                paragraph_indices=current_indices.copy(),
                content=current_content.copy(),
            )
        )

    return ResumeStruct(
        contact_block=contact_block,
        sections=sections,
        projects=projects,
        skills=list(dict.fromkeys(skills)),
        education=education,
    )


def validate_resume_file(path: str) -> None:
    resume_path = Path(path)
    if not resume_path.exists():
        raise ValueError("Resume file was not found.")
    if resume_path.suffix.lower() != ".docx":
        raise ValueError("Resume must be a .docx file.")
