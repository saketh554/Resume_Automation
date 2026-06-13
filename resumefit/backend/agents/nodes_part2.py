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
    from backend.services.jd_parser import parse_jd

    next_state = state.model_copy(deep=True)
    jd_text = next_state.jd_text.strip()
    if not jd_text:
        next_state.errors.append("parse_jd failed: JD text is empty.")
        return next_state

    try:
        jd_struct, parse_source = parse_jd(jd_text)
        next_state.jd_struct = jd_struct
        if parse_source == "fallback":
            next_state.errors.append("parse_jd warning: using fallback parser.")
    except Exception as exc:  # noqa: BLE001
        next_state.errors.append(f"parse_jd failed: {exc}")
    return next_state
