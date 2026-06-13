# ResumeFit - JD-to-Resume Tailoring Agent

A multi-agent (LangGraph) app: paste a job description, compare it against your base resume, get an
alignment score + gap analysis, and download a format-preserving tailored resume plus a cold email.

## Status

Part 3 analysis foundation is in place. The full plan lives in `docs/`:

- `docs/AGENTS.md` - constitution: tech decisions, the 8-node agent graph, format/length rules, standards.
- `docs/BRIEF.md` - condensed problem statement, capabilities, deliverables.
- `docs/PLAN.md` - lean part-by-part execution checklist with tests and success criteria.

## Getting started

1. Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.
2. Install dependencies with `uv sync`.
3. Start the API with `uv run uvicorn backend.app.main:app --reload`.
4. Verify health with `GET /api/health`.
5. Run tests with `uv run pytest -q`.

## Stack (current)

Python 3.11+, FastAPI, SQLAlchemy, SQLite, LangGraph (planned), python-docx (planned), OpenAI
(gpt-4o / gpt-4o-mini planned), React + Vite + Tailwind (planned).

## Alignment formula (Part 3)

`alignment_pct = round(((covered_required * 0.7) + (covered_nice * 0.3)) * 100, 2)`

Where:

- `covered_required = matched_required / total_required`
- `covered_nice = matched_nice / total_nice`
