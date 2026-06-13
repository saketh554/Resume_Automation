from __future__ import annotations

import re

from backend.agents.schemas import (
    AlignmentResult,
    GapBullet,
    GraphState,
    ProjectAuditItem,
    ProjectMapping,
)


# Alignment formula for Part 3:
# covered_required = matched_required / total_required
# covered_nice = matched_nice / total_nice
# weighted_score = covered_required * 0.7 + covered_nice * 0.3
# alignment_pct = round(weighted_score * 100, 2)
REQUIRED_WEIGHT = 0.7
NICE_TO_HAVE_WEIGHT = 0.3


def _norm(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def _safe_placeholder_metric(skill: str) -> str:
    return f"Improved {skill} outcomes by [X]% through measurable delivery improvements."


def analyze_alignment_node(state: GraphState) -> GraphState:
    next_state = state.model_copy(deep=True)
    if next_state.resume_struct is None or next_state.jd_struct is None:
        next_state.errors.append("analyze_alignment failed: missing parsed resume or JD.")
        return next_state

    resume_skills_raw = list(next_state.resume_struct.skills)
    resume_skills_raw.extend(project.project_name for project in next_state.resume_struct.projects)
    resume_skill_set = {_norm(item) for item in resume_skills_raw if item.strip()}

    required = [_norm(skill) for skill in next_state.jd_struct.required_skills if skill.strip()]
    nice = [_norm(skill) for skill in next_state.jd_struct.nice_to_haves if skill.strip()]

    matched_required = [skill for skill in required if skill in resume_skill_set]
    matched_nice = [skill for skill in nice if skill in resume_skill_set]

    matched_skills = list(dict.fromkeys(matched_required + matched_nice))
    missing_skills = [skill for skill in list(dict.fromkeys(required + nice)) if skill not in matched_skills]

    covered_required = len(matched_required) / len(required) if required else 1.0
    covered_nice = len(matched_nice) / len(nice) if nice else 1.0
    weighted_score = (covered_required * REQUIRED_WEIGHT) + (covered_nice * NICE_TO_HAVE_WEIGHT)
    alignment_pct = round(weighted_score * 100, 2)

    next_state.alignment = AlignmentResult(
        alignment_pct=alignment_pct,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )
    return next_state


def write_gap_bullets_node(state: GraphState) -> GraphState:
    next_state = state.model_copy(deep=True)
    if next_state.alignment is None:
        next_state.errors.append("write_gap_bullets failed: alignment is missing.")
        return next_state

    bullets: list[GapBullet] = []
    for skill in next_state.alignment.missing_skills:
        bullet_text = f"Applied {skill} in production-style deliverables. {_safe_placeholder_metric(skill)}"
        bullets.append(GapBullet(skill=skill, bullet=bullet_text))

    next_state.gap_bullets = bullets
    return next_state


def map_to_projects_node(state: GraphState) -> GraphState:
    next_state = state.model_copy(deep=True)
    if not next_state.gap_bullets:
        next_state.project_mappings = []
        return next_state
    if next_state.resume_struct is None:
        next_state.errors.append("map_to_projects failed: resume struct missing.")
        return next_state

    projects = next_state.resume_struct.projects
    section_fallback = [section.title for section in next_state.resume_struct.sections if section.title]

    mappings: list[ProjectMapping] = []
    for gap in next_state.gap_bullets:
        skill_token = _norm(gap.skill)

        ranked: list[tuple[int, str]] = []
        for project in projects:
            text_pool = " ".join([project.project_name, *project.bullets]).lower()
            score = 0
            for token in skill_token.split():
                if token and token in text_pool:
                    score += 1
            ranked.append((score, project.project_name))

        ranked.sort(key=lambda item: item[0], reverse=True)
        chosen = [name for score, name in ranked if score > 0][:2]
        if not chosen:
            if projects:
                chosen = [projects[0].project_name]
            elif section_fallback:
                chosen = [section_fallback[0]]
            else:
                chosen = ["General Experience"]

        mappings.append(
            ProjectMapping(
                skill=gap.skill,
                bullet=gap.bullet,
                project_names=chosen,
                rationale=f"Mapped to project context with strongest overlap for '{gap.skill}'.",
            )
        )

    next_state.project_mappings = mappings
    return next_state


def audit_projects_node(state: GraphState) -> GraphState:
    next_state = state.model_copy(deep=True)
    if next_state.resume_struct is None:
        next_state.errors.append("audit_projects failed: resume struct missing.")
        return next_state

    project_sections = [
        section
        for section in next_state.resume_struct.sections
        if section.title.strip().lower() in {"projects", "experience", "work experience"}
    ]

    audit_items: list[ProjectAuditItem] = []
    generic_patterns = (
        "responsible for",
        "various tasks",
        "worked on",
        "helped with",
    )

    for section in project_sections:
        flagged = [
            line
            for line in section.content
            if any(pattern in line.lower() for pattern in generic_patterns)
        ]
        audit_items.append(ProjectAuditItem(project_name=section.title, irrelevant_points=flagged))

    next_state.project_audit = audit_items
    return next_state
