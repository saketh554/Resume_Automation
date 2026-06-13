# Project plan checklist — ResumeFit (lean MVP)

This is the execution checklist for the JD-to-Resume Tailoring Agent. Review `docs/AGENTS.md` for
the full constitution before proceeding. Keep it lean: build the thinnest vertical slice first,
then layer capabilities. Commit per verified slice.

## Agreed constraints and decisions

- Backend: FastAPI (Python 3.11+), `uv` package manager.
- Orchestration: LangGraph — one typed shared-state graph, linear edges for the MVP.
- Frontend: React + Vite + Tailwind, single-page app; three panels (input / analysis / output).
- LLM: OpenAI gpt-4o (analysis + writing) + gpt-4o-mini (parsing/classification). Swappable config.
- Structured outputs: Pydantic schema on every structured LLM call.
- Resume parse + edit: python-docx, editing runs in place to preserve format and length.
- DB: SQLite via SQLAlchemy (relational tables, not a JSON blob). Survives restarts.
- Input: .docx resume + pasted JD text. Output: tailored .docx + cold email.

## Git workflow

- `main` is always green and runnable.
- One branch per part (e.g., `feat/part-2-langgraph`). Small PRs; review the diff; merge; delete.
- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
- Tags: `v0.1-slice` (one JD round-trips to an analysis), `v1.0-mvp` (all 6 capabilities).
- Never commit code that has not been run/verified.

---

## Part 0: Scaffolding

### Checklist
- [ ] Repo; MIT license; `.gitignore` (.env, *.db, __pycache__, node_modules, dist/, uploads/).
- [ ] Init Python project with `uv`; pin Python 3.11+.
- [ ] `docs/` (AGENTS.md, BRIEF.md, PLAN.md) + `.cursor/rules/` (standards.md, format-rules.md).
- [ ] `PROGRESS.md`, `.env.example` (OPENAI_API_KEY).
- [ ] FastAPI skeleton with `GET /api/health`.
- [ ] Layout: `backend/` (app, agents, models, services), `frontend/`, `data/`, `docs/`.

### Tests
- [ ] Server boots; `GET /api/health` returns `{"status":"ok"}`.
- [ ] `.gitignore` excludes secrets, DB, and uploads.

### Success criteria
- One command starts the backend; guardrail docs are in place.

---

## Part 1: Data models and persistence

### Checklist
- [ ] SQLAlchemy models: Resume, JobDescription, Analysis, SkillGap, ProjectEdit, ColdEmail.
- [ ] Resume: id, filename, stored_path, parsed_struct(JSON), created_at.
- [ ] JobDescription: id, raw_text, parsed_struct(JSON), created_at.
- [ ] Analysis: id, resume_id, jd_id, alignment_pct, matched_skills(JSON), created_at.
- [ ] SkillGap: id, analysis_id, skill, suggested_bullet, mapped_projects(JSON).
- [ ] ProjectEdit: id, analysis_id, project_name, irrelevant_points(JSON).
- [ ] ColdEmail: id, analysis_id, subject, body.
- [ ] DB auto-creates on startup if missing; SQLite on a persistent path.

### Tests
- [ ] Schema creates from a clean state.
- [ ] Write an Analysis row, restart the process, confirm it persists.

### Success criteria
- Relational state is persistent and survives restarts.

---

## Part 2: Resume + JD parsing (LangGraph nodes 1-2)

### Checklist
- [ ] python-docx loader → structured resume: contact block, sections (in order), projects/experience
      with their bullets, skills list, education. Preserve a handle to each source paragraph.
- [ ] Pydantic `ResumeStruct` and `ProjectSection` schemas.
- [ ] `parse_jd` node: LLM (gpt-4o-mini) → `JDStruct` (required_skills, nice_to_haves,
      responsibilities, seniority, company, role_title).
- [ ] Both nodes write into the LangGraph shared state.

### Tests
- [ ] A sample .docx parses into the expected sections/projects/bullets without crashing.
- [ ] A pasted JD parses into required vs nice-to-have skills.
- [ ] A corrupt/empty .docx is handled gracefully (clear error, no crash).

### Success criteria
- Resume and JD become validated structured objects the rest of the graph can use.

---

## Part 3: Alignment + gap analysis (LangGraph nodes 3-6)

### Checklist
- [ ] `analyze_alignment`: define the alignment formula (e.g., weighted % = covered_required*0.7 +
      covered_nice*0.3, normalized) and return alignment_pct + matched_skills + missing_skills.
      The formula is documented in code and README.
- [ ] `write_gap_bullets`: for each missing skill → one strong, professional bullet. Quantify only
      where honest; otherwise insert a marked placeholder like `[X]%`.
- [ ] `map_to_projects`: each missing skill/bullet → best-fit existing project(s) + 1-line rationale.
- [ ] `audit_projects`: per project section → irrelevant/incorrect/off-target points.
- [ ] All four use Pydantic structured outputs; all are grounded in Part 2's structured inputs.

### Tests
- [ ] Alignment % is reproducible for the same inputs and matches the documented formula.
- [ ] Every missing skill gets exactly one bullet and at least one mapped project.
- [ ] Audit never flags the contact/header block; only project/experience content.
- [ ] No bullet invents an employer, date, degree, or unmarked metric.

### Success criteria
- The analysis is specific, grounded, and explainable — not generic filler.

---

## Part 4: Format-preserving edit + cold email (LangGraph nodes 7-8)

### Checklist
- [ ] `apply_edits` (python-docx): insert new bullets by CLONING an existing bullet paragraph in the
      mapped project (copy style + numbering + run font); replace/trim flagged irrelevant points.
- [ ] Enforce the "one-in-one-out" length rule: each added bullet offset by a trim/removal.
- [ ] Post-edit assertions: same section headings in same order; same named styles present;
      paragraph count within tolerance. Fail loudly if layout drifted.
- [ ] Save tailored .docx to `data/` and record the path.
- [ ] `write_cold_email`: LLM → subject + body tailored to JD + company, grounded in the resume.

### Tests
- [ ] Open the tailored .docx: headings/order/styles match the original; length within ±1 line.
- [ ] Added bullets carry the same bullet/list formatting as their siblings (not plain paragraphs).
- [ ] Cold email references the actual role/company and real resume content; nothing fabricated.

### Success criteria
- The downloaded resume looks identical in structure to the original and reads cleanly; the email
  is ready to copy/send after a human review.

---

## Part 5: Backend API + LangGraph wiring

### Checklist
- [ ] POST /api/resume (multipart .docx upload → parse → persist → return resume_id).
- [ ] POST /api/analyze (resume_id + jd_text → run the LangGraph pipeline → persist → return the
      full analysis: alignment_pct, skill_gaps, project_edits, irrelevant_points).
- [ ] GET /api/analysis/{id} (full analysis + download link for the tailored .docx).
- [ ] GET /api/analysis/{id}/resume.docx (download the tailored file).
- [ ] GET /api/analysis/{id}/email (subject + body).
- [ ] Request/response Pydantic models; clear HTTP errors; graceful failure messages.

### Tests
- [ ] Upload → analyze → download flow works end-to-end via Swagger UI.
- [ ] Past analyses are retrievable after a restart.

### Success criteria
- All six capabilities are exercisable through the API.

---

## Part 6: Frontend UI

### Checklist
- [ ] Input panel: upload .docx + paste JD + "Analyze" button.
- [ ] Analysis panel: alignment % (prominent), missing-skills list with suggested bullets, the
      project mapping for each, and the per-project irrelevant-points audit.
- [ ] Output panel: "Generate tailored resume" → download button; cold-email box (copy + download).
- [ ] Loading + error states; empty-state guidance.

### Tests
- [ ] Click through all six capabilities in the browser end-to-end.
- [ ] Download opens a correctly formatted .docx; email copies cleanly.
- [ ] Refresh / restart → past analyses still load.

### Success criteria
- A user can do everything required from a normal browser.

---

## Part 7: README + polish (+ optional deploy)

### Checklist
- [ ] README: run locally + API keys; the LangGraph agent graph + a small diagram; the alignment
      formula; how format/length preservation works; grounding/no-fabrication policy; what's next.
- [ ] Optional Dockerfile for local run.
- [ ] Optional deploy to a public URL with a persistent disk (SQLite).
- [ ] Final review: typed, readable, schema-constrained outputs, graceful failures.

### Success criteria
- A clean clone runs from the README; the app demonstrably works end-to-end; the README explains the
  WHY behind the tradeoffs.

---

## Suggested build order (fastest path to a working slice)

1. Part 0 + Part 1 (scaffold + persistence).
2. Part 2 + a minimal Part 3 (`analyze_alignment` only) + a stub Part 5 (`/api/resume`,
   `/api/analyze`) → tag `v0.1-slice` once a pasted JD returns a real alignment %.
3. Finish Part 3, then Part 4 (edits + email).
4. Part 6 UI, then Part 7 README → tag `v1.0-mvp`.
