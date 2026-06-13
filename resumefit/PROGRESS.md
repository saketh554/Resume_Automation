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
