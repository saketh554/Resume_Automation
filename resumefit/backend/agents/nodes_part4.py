from __future__ import annotations

from backend.agents.schemas import GraphState


def apply_edits_node(state: GraphState) -> GraphState:
    from backend.services.docx_editor import apply_docx_edits

    next_state = state.model_copy(deep=True)
    if not next_state.project_mappings:
        next_state.errors.append("apply_edits failed: no project mappings available.")
        return next_state

    try:
        output_path = apply_docx_edits(
            source_path=next_state.resume_path,
            mappings=next_state.project_mappings,
            audits=next_state.project_audit,
        )
        next_state.tailored_docx_path = output_path
    except Exception as exc:  # noqa: BLE001
        next_state.errors.append(f"apply_edits failed: {exc}")

    return next_state


def write_cold_email_node(state: GraphState) -> GraphState:
    from backend.services.cold_email import write_cold_email

    next_state = state.model_copy(deep=True)
    if next_state.jd_struct is None:
        next_state.errors.append("write_cold_email failed: JD struct missing.")
        return next_state

    company = next_state.jd_struct.company
    role_title = next_state.jd_struct.role_title

    try:
        email, source = write_cold_email(
            company=company,
            role_title=role_title,
            jd_text=next_state.jd_text,
            resume=next_state.resume_struct,
        )
        next_state.cold_email = email
        if source == "fallback":
            next_state.errors.append("write_cold_email warning: using fallback generator.")
    except Exception as exc:  # noqa: BLE001
        next_state.errors.append(f"write_cold_email failed: {exc}")

    return next_state
