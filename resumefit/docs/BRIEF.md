# Project Brief (condensed) — ResumeFit: JD-to-Resume Tailoring Agent

A concise reference for what we are building and why. The full constitution and standards are in
`docs/AGENTS.md`. The execution checklist is in `docs/PLAN.md`.

## Problem

Tailoring a resume to each job posting is slow and repetitive. A job seeker wants to paste a job
description (JD), have an AI compare it against their base resume, and get back: how aligned they
are, what's missing, exactly how to fix it, and a ready-to-send cold email — without breaking the
resume's layout or blowing up its length.

## What we are given

- A base resume as a `.docx` file (uploaded once via the UI).
- A job description pasted as plain text in the UI.

## Required capabilities (from a normal browser)

1. Upload base resume (.docx) and paste a JD.
2. Alignment analysis:
   - An alignment PERCENTAGE between the JD and the base resume.
   - A list of MISSING / weak skills the JD asks for.
   - For each missing skill, a strong, professional RESUME BULLET POINT.
3. Project mapping: for each missing skill / new bullet, which existing PROJECT(S) it best fits.
4. Section audit: per project/experience section, a list of IRRELEVANT or INCORRECT points.
5. Generate + download a TAILORED .docx that incorporates the changes:
   - Same layout, fonts, styles, and section order.
   - Same length as before (within a tight tolerance — "one-in-one-out" rule).
6. A COLD EMAIL (subject + body) tailored to the JD and company.

## Hard constraints (what makes this non-trivial)

- FORMAT PRESERVATION: the output .docx must look identical in structure to the input — edit in
  place via python-docx, reusing existing paragraph styles and run formatting.
- LENGTH PRESERVATION: every added bullet is offset by a trimmed/removed irrelevant point so net
  length stays put.
- GROUNDED CONTENT: no fabricated employers, dates, degrees, or metrics. Placeholders like `[X]%`
  are explicitly marked for the user to fill in.
- HONEST ALIGNMENT: the percentage uses a defined, explainable formula (e.g., weighted coverage of
  required vs. nice-to-have skills), not an opaque guess.

## Deliverables

1. Working web app (FastAPI backend + React/Vite/Tailwind frontend) covering all six capabilities.
2. The LangGraph agent pipeline (8 nodes, linear for the MVP) with schema-constrained outputs.
3. Downloadable tailored `.docx` + a cold email.
4. README: how to run locally + required API keys; the agent graph + a short diagram; the alignment
   formula; how format/length preservation works; and what's next (PDF import, multi-resume, ATS
   keyword scoring, auto-apply with human approval).

## How to judge it's good

- Paste a real JD + a real resume → the alignment %, gaps, bullets, project mapping, and audit are
  specific and grounded (not generic filler).
- The downloaded .docx opens with the SAME look as the original and is the same length.
- Nothing in the tailored resume or cold email is fabricated.
- Re-opening the app after a restart still shows past analyses.

## Out of scope for the MVP

- PDF or Google Docs input (docx only).
- Auto-submitting applications or auto-sending email.
- Multi-user auth (data model supports it; UI does not expose it yet).
- ATS-score simulation (noted as a future extension).
