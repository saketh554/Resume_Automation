from __future__ import annotations

from backend.agents.schemas import GraphState


def parse_resume_node(state: GraphState) -> GraphState:
    from backend.services.resume_parser import parse_resume_docx, validate_resume_file

    next_state = state.model_copy(deep=True)
    try:
        validate_resume_file(next_state.resume_path)
        next_state.resume_struct = parse_resume_docx(next_state.resume_path)
    except Exception as exc:  # noqa: BLE001
        next_state.errors.append(f"parse_resume failed: {exc}")
    return next_state


def parse_jd_node(state: GraphState) -> GraphState:
    from backend.services.jd_parser import parse_jd_fallback

    next_state = state.model_copy(deep=True)
    jd_text = next_state.jd_text.strip()
    if not jd_text:
        next_state.errors.append("parse_jd failed: JD text is empty.")
        return next_state

    try:
        next_state.jd_struct = parse_jd_fallback(jd_text)
    except Exception as exc:  # noqa: BLE001
        next_state.errors.append(f"parse_jd failed: {exc}")
    return next_state
