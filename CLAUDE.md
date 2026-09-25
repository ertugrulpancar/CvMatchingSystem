# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

CV ↔ job-posting matching web app (FastAPI + React/TS, Gemini, Supabase, Vercel). **`docs/PLAN.md` is the source of truth**: architecture, data model, API contract, and the phase-by-phase build order (Faz 0–7). Read it before starting work, check which phase is current, and don't jump ahead. Once the code diverges from the plan, update this file and PLAN.md.

## Working with this user

- The user is a junior developer and this is a learning project. For every non-trivial design decision, briefly explain **why** it was made. When there are several reasonable options, name them and the reason for the pick. Don't explain trivial lines.
- When a product requirement is ambiguous, ask instead of assuming.
- **Never run mutating git/GitHub commands** (init, add, commit, branch, switch, merge, push, pull, remote, gh, PRs). Give the user the commands in order with a one-sentence explanation of each, a Conventional Commits message with its rationale, and a way to verify the result. Read-only `git status/diff/log` is fine. The full rules are in PLAN.md §12a. Workflow: one branch per phase (`feat/phase-N-...`), PR into `main`.
- ⚠️ The user's home directory (`~`) is itself a git repo. Until the user runs `git init` inside this folder, `git` commands here operate on `~`.
- The user speaks Turkish. Answer in Turkish.

## Commands (planned; verify once Faz 0 scaffolding exists)

Backend (`backend/`, managed with `uv`):
```
uv run uvicorn app.main:app --reload          # dev server :8000
uv run pytest                                  # all tests
uv run pytest tests/test_scoring.py::test_x    # single test
uv run ruff check . && uv run ruff format .
uv run alembic upgrade head                    # uses MIGRATION_DATABASE_URL (session pooler :5432)
uv run alembic revision --autogenerate -m "..."
```

Frontend (`frontend/`):
```
npm run dev          # :5173, proxies /api → :8000
npm run gen:types    # regenerates src/api/schema.d.ts from backend /openapi.json (backend must be running)
npm run build
```

## Architecture invariants (easy to break without reading PLAN.md)

- **Pipeline:** parse → LLM extract requirements → LLM match against CV → `verify_evidence` (code) → `scoring` (pure function, code) → save. **The LLM never produces the score.** Weights: must_have=2, nice_to_have=1. Points: met=1, partial=0.5, missing=0.
- **Evidence verification:** Each `evidence` must be a verbatim quote from the CV. It is checked with `normalize_for_match()` (NFKC → casefold → strip U+0307 → `ı`→`i`) plus a rapidfuzz `partial_ratio >= 90` threshold. If verification fails, `met` is downgraded to `partial`. Plain `.lower()` breaks Turkish `İ`.
- **Bilingual:** CVs and job postings may be in TR or EN in any combination. `requirement_text` and `evidence` stay in their original language. Only `explanation` follows `output_language`.
- **Strategy/Repository seams:** `Matcher` (`llm` | `keyword`, selected with the `MATCHER` env var) and `AnalysisRepository` (SQL | InMemory). Tests use KeywordMatcher/mocks and the InMemory repo, and must never call real Gemini or a real DB. Auth in tests: `app.dependency_overrides[get_current_user]`.
- **Schema layers kept separate:** `schemas/` (API contract), `services/llm/schemas.py` (Gemini `response_schema`, which supports only a subset of JSON Schema), `models/` (SQLAlchemy). `category_scores` are derived on read and not stored. `overall_score` is stored.
- **Frontend types are generated.** Never hand-edit `frontend/src/api/schema.d.ts`.
- **Frontend reaches Supabase only for Google auth.** All data goes through FastAPI with a `Bearer` Supabase JWT, which the backend verifies via JWKS (`aud=authenticated`, `sub` = user_id).
- **Supabase specifics:** RLS is enabled on every table with **no policies** (deny-all), because the anon key is public. The backend connects through the Supavisor transaction pooler (:6543) with `NullPool` and `prepare_threshold=None`. Alembic owns the `public` schema. Don't create tables from the dashboard.
- **Another user's analysis returns 404, not 403.** Every query filters by `user_id`.
- **Vercel limits:** upload cap is 4 MB (the platform body limit is 4.5 MB), `maxDuration: 60` is set on `app/main.py`, and heavy dependencies (torch, sentence-transformers) are not allowed. Rate limiting is a per-user daily count in the DB, because in-memory counters don't work on serverless. PDF parsing uses `pdfplumber`. Don't use PyMuPDF (AGPL).
- Never store full CV text or files, and never log CV content.
