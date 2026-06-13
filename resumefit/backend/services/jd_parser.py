from __future__ import annotations

import re

from backend.agents.schemas import JDStruct


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
    return output


def parse_jd_fallback(jd_text: str) -> JDStruct:
    """Rule-based fallback parser for local development without API calls."""
    lines = [line.strip() for line in jd_text.splitlines() if line.strip()]

    # Lightweight skill extraction from common tokens.
    known_skills = [
        "python",
        "fastapi",
        "sql",
        "postgres",
        "docker",
        "kubernetes",
        "aws",
        "gcp",
        "azure",
        "react",
        "typescript",
        "javascript",
        "langchain",
        "langgraph",
        "machine learning",
    ]

    text_lower = jd_text.lower()
    found_skills = [skill for skill in known_skills if skill in text_lower]

    required: list[str] = []
    nice_to_have: list[str] = []
    responsibilities: list[str] = []

    for line in lines:
        line_lower = line.lower()
        if line_lower.startswith(("required", "requirements", "must have", "you have")):
            required.extend(re.split(r"[,;|]", line.replace(":", " ")))
        elif line_lower.startswith(("preferred", "nice to have", "bonus")):
            nice_to_have.extend(re.split(r"[,;|]", line.replace(":", " ")))
        elif line.startswith(("-", "*")):
            responsibilities.append(line.lstrip("-* "))

    required.extend(found_skills)

    seniority = ""
    for level in ("intern", "junior", "mid", "senior", "staff", "principal", "lead"):
        if re.search(rf"\b{level}\b", text_lower):
            seniority = level
            break

    role_title = ""
    for line in lines[:8]:
        if any(token in line.lower() for token in ("engineer", "developer", "scientist", "manager")):
            role_title = line
            break

    company = ""
    for line in lines[:8]:
        if " at " in line.lower():
            company = line.split(" at ", maxsplit=1)[-1].strip()
            break

    return JDStruct(
        required_skills=_dedupe_keep_order(required),
        nice_to_haves=_dedupe_keep_order(nice_to_have),
        responsibilities=_dedupe_keep_order(responsibilities),
        seniority=seniority,
        company=company,
        role_title=role_title,
    )
