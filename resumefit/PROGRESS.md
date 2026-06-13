# Progress log

## Part 0 - Scaffolding

- [x] Added Python project setup (`pyproject.toml`) with Python 3.11+ and FastAPI stack.
- [x] Added backend scaffold directories and package markers.
- [x] Implemented `GET /api/health` endpoint.
- [x] Added `.cursor/rules/` baseline rule docs.
- [x] Added MIT `LICENSE`.
- [x] Confirmed `.gitignore` and `.env.example` include required items.

### Verification

- [x] Run backend and verify `GET /api/health` returns `{"status":"ok"}`.

## Part 1 - Data models and persistence

- [x] Added SQLAlchemy setup with persistent SQLite engine and request session helper.
- [x] Added settings loader for `DATABASE_URL` and `DATA_DIR` using `.env`.
- [x] Implemented relational models: Resume, JobDescription, Analysis, SkillGap, ProjectEdit, ColdEmail.
- [x] Wired DB auto-create on app startup.
- [x] Added tests for schema creation and restart persistence.

### Verification

- [x] `uv run pytest -q` passes (`2 passed`).
- [x] Analysis row persists after engine restart in test coverage.

## Part 2 - Resume + JD parsing (LangGraph nodes 1-2)

- [x] Added `ResumeStruct`, `ProjectSection`, `ResumeSection`, and `JDStruct` schemas.
- [x] Added shared `GraphState` schema for LangGraph node handoff.
- [x] Implemented `parse_resume` node using `python-docx` parser service.
- [x] Implemented `parse_jd` node with structured `JDStruct` output.
- [x] Added linear LangGraph wiring for Part 2 (`parse_resume -> parse_jd`).
- [x] Added graceful error handling for missing/corrupt/empty resume inputs.

### Verification

- [x] Sample `.docx` parses into contact block, sections, projects/bullets, skills, education.
- [x] JD text parses into required skills vs nice-to-have skills.
- [x] Corrupt `.docx` is handled gracefully (`parse_resume failed` error, no crash).
- [x] `uv run pytest -q` passes (`4 passed`).
