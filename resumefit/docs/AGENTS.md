# ResumeFit — JD-to-Resume Tailoring Agent

## Business Requirements

A job seeker pastes a job description (JD) into a web UI alongside their base resume (a .docx
file). The system evaluates how well the resume aligns with the JD, surfaces gaps, and produces a
tailored resume that fixes those gaps WITHOUT changing the layout, format, or overall length. It
also drafts a cold email to send with the application. A human always reviews before sending or
submitting — the agent assists, it does not auto-apply.

From a normal browser, the user must be able to:

1. Upload their base resume (.docx) once and paste a JD into a text box.
2. Get an alignment analysis: an alignment percentage, a list of missing/weak skills, and for each
   missing skill a strong, professional resume bullet point.
3. See which existing project(s) in the resume each missing skill could be incorporated into.
4. See a list of irrelevant or incorrect points found in each project/experience section.
5. Click "Generate tailored resume" and download a .docx that incorporates the suggested changes —
   same fonts, styles, section order, and roughly the same page length as the original.
6. Get a cold email (subject + body) tailored to the JD and company, ready to copy or download.

## Limitations / MVP scope

- Single user, no auth for the MVP. The data model should still cleanly support multiple users
  later (every analysis row keyed by a resume_id + jd_id).
- One base resume at a time. Re-uploading replaces the active base resume.
- Input resume is .docx only for the MVP. (PDF import is a future extension.)
- The agent SUGGESTS and APPLIES edits but never invents employers, dates, degrees, or
  achievements that are not grounded in the original resume. Missing-skill bullets are phrased as
  realistic, on-theme additions the user can confirm — not fabricated history.
- Runs locally for development; optionally deployed to a public URL.

## Technical Decisions

- Language: Python 3.11+.
- Orchestration: LangGraph. A typed shared state object flows through agent nodes; the graph is
  explicit and inspectable. (LangChain is used only for model/client wrappers where convenient.)
- Backend: FastAPI + Uvicorn. Serves the API; can also serve the built frontend at `/`.
- Frontend: React + Vite + Tailwind (single-page app). Three panels: input, analysis, output.
- LLM: OpenAI gpt-4o for analysis/writing; gpt-4o-mini for cheap parsing/classification. Swappable
  via config (a single `MODEL_*` block in settings; no hard-coded model names in agent code).
- Resume parsing + editing: python-docx. Read the document's paragraphs, runs, and styles; apply
  edits in place by manipulating runs so fonts/sizes/bullets are preserved.
- Structured outputs: every LLM call that returns data uses a Pydantic schema via OpenAI
  structured outputs. Never parse free text with regex or string splitting.
- Relational DB: SQLite via SQLAlchemy, file-backed so analyses survive restarts. Tables:
  Resume, JobDescription, Analysis, SkillGap, ProjectEdit, ColdEmail.
- Config/secrets: pydantic-settings + .env. OPENAI_API_KEY read from .env.
- Package manager: uv.
- Containerization: optional Dockerfile for local run.

## Agent graph (LangGraph)

Shared state: `{ resume_struct, jd_text, jd_struct, alignment, skill_gaps, project_edits,
irrelevant_points, tailored_docx_path, cold_email }`.

Nodes (each a small, typed function; LLM nodes use schema-constrained output):

1. `parse_resume` — python-docx → structured resume (sections, projects, bullets, skills).
2. `parse_jd` — LLM → structured JD (required skills, nice-to-haves, responsibilities, seniority).
3. `analyze_alignment` — LLM → alignment % + matched skills + missing/weak skills, grounded in the
   two structured inputs. The percentage formula is defined and explained, not a vibe.
4. `write_gap_bullets` — for each missing skill → one strong, professional, quantifiable-where-
   honest bullet point.
5. `map_to_projects` — for each missing skill / new bullet → which existing project(s) it best
   fits, with a short rationale.
6. `audit_projects` — per project section → list irrelevant or incorrect/off-target points.
7. `apply_edits` — python-docx → produce the tailored .docx: insert/replace bullets in the mapped
   projects, remove/flag irrelevant points, preserve styles, keep length within tolerance.
8. `write_cold_email` — LLM → subject + body tailored to JD + company, grounded in the resume.

Edges are linear for the MVP (1→2→3→4→5→6→7→8). Keep it a straight pipeline; do not add loops or
self-reflection unless a test shows it's needed.

## Format & length preservation (the hard requirement)

- Edit runs in place. When replacing a bullet's text, reuse the existing paragraph's style and the
  first run's font properties; do not create new paragraphs with default styling.
- Insert new bullets by cloning an existing bullet paragraph in the same section (copy style +
  numbering/list formatting), then setting its text — never append a plain paragraph.
- Length budget: count the original document's paragraphs and approximate rendered lines. For every
  bullet added, the agent must propose a roughly equivalent removal/trim (typically an irrelevant
  point flagged in `audit_projects`) so net length stays within ±1 line. The plan calls this the
  "one-in-one-out" rule.
- After writing the tailored .docx, re-open it and assert: same section headings in the same order,
  same named styles present, paragraph count within tolerance. Fail loudly if layout drifted.
- Never change: fonts, font sizes, margins, section order, header/contact block.

## Coding standards

1. Latest stable libraries; idiomatic Python. Type hints everywhere; small readable functions.
2. Keep it simple. No over-engineering, no features beyond the requirements — but handle the real
   failure modes below.
3. Be concise. No emojis. The README explains the WHY behind tradeoffs, not a feature list.
4. When hitting issues, find the root cause before fixing. Prove with evidence, then fix the cause.
5. SCHEMA-CONSTRAINED OUTPUTS ONLY. Every structured LLM call uses a Pydantic schema.
6. GROUNDED, NOT FABRICATED. Missing-skill bullets and the cold email must be grounded in the
   actual resume and JD. Never invent employers, titles, dates, degrees, metrics, or certifications.
   When a metric is suggested as a placeholder, mark it clearly (e.g., `[X]%`) for the user to fill.
7. FORMAT FAITHFULNESS. The tailored .docx must preserve fonts, styles, section order, and length
   within tolerance. A layout-breaking edit is a bug, not a stylistic choice.
8. PERSISTENCE, NOT IN-MEMORY. Analyses live in SQLite on disk and survive a restart.
9. Graceful failure modes (never crash the request): corrupt/locked .docx, empty JD, a resume with
   no detectable project section, an LLM returning an unparseable response. On failure, return a
   clear message and a partial result where possible.

## Working documentation

All planning docs live in `docs/`. Review `docs/PLAN.md` before proceeding. Update `PROGRESS.md`
after each verified slice. The condensed brief is in `docs/BRIEF.md`. Cursor rules mirror the
standards above in `.cursor/rules/`.
