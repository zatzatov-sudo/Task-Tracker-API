# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A learning-project REST API (FastAPI + Pydantic) for tracking tasks, with a vanilla JS/HTML frontend. No database — data lives in an in-memory dict for the lifetime of the process (`app/storage.py`'s `_tasks`). Despite the README mentioning JSON-file persistence (ADR-001), that ADR does not exist in this repo and storage is currently pure in-memory; it resets on every server restart and between every test.

## Commands

Activate the venv first (Windows PowerShell): `venv\Scripts\Activate.ps1`

- Run backend: `uvicorn app.main:app --reload --port 8000` (serves at `http://127.0.0.1:8000`, docs at `/docs`)
- Run all tests: `pytest`
- Run one test: `pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body`
- Verbose tests: `pytest -v`
- Frontend: open `frontend/index.html` directly in a browser (no build step); it talks to `http://localhost:8000` via `fetch()`, so the backend must be running

There is no lint/format tooling configured in this repo.

## Architecture

Backend is a thin 4-file layering under `app/`:

- `models.py` — Pydantic schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus`, `TaskPriority`). All validation (title length/blankness, tag normalization/limits) happens here via `field_validator`s, so invalid input never reaches storage. Both `extra="forbid"` — unknown fields 422 automatically. `TaskUpdate` fields are all `Optional`; `model_dump(exclude_unset=True)` in storage distinguishes "field omitted" from "field explicitly cleared" (important for `tags: []` vs `tags` not provided).
- `business_rules.py` — status-transition state machine (`VALID_TRANSITIONS`), enforced only on PATCH before storage is touched.
- `storage.py` — in-memory CRUD + filtering (`status`, `priority`, `tag`, `search`, all AND-combinable, search applied last). `_reset()` is used by the `conftest.py` autouse fixture to wipe state between tests.
- `main.py` — route handlers only; no business logic lives here. CORS is wide open (`allow_origins=["*"]`) since the frontend loads via `file://`.

Request flow for PATCH is the one place with cross-module coordination: `main.py` fetches the existing task, calls `business_rules.validate_status_transition` (raises 422 HTTPException directly) *before* calling `storage.update_task`.

Frontend (`frontend/index.html`, single file, ~1150 lines) is a Kanban board (To Do / In Progress / Done columns) with drag-and-drop, a create/edit modal, and a 4-input filter bar (search/status/priority/tag) that calls `GET /tasks` with combined query params on every change — the server is always the source of truth for filtering, not client-side state. Drag-and-drop does optimistic UI updates with rollback if the PATCH is rejected (e.g. invalid status transition). `API_BASE_URL` is hardcoded to `http://localhost:8000` (frontend/index.html:601).

## Testing conventions

- Tests use FastAPI's `TestClient` in-process — no server needs to be running.
- `conftest.py`'s `_reset_storage` autouse fixture clears `_tasks` before and after every test; tests never need to manage state cleanup themselves.
- Test naming: `test_<action>_<condition>_returns_<status>[_<detail>]`, e.g. `test_create_task_blank_title_returns_422`.
- `tests/verify_a.py` is a standalone ad-hoc verification script (not pytest, run with `python tests/verify_a.py`), not part of the `pytest` suite.

## Feature docs

`docs/midcourse/*.md` contain per-feature write-ups (files changed, constraints, test counts, deferred scope) for major features (tags, search/combined filters). Check these before extending those areas — they document intentional scope limits (e.g. single-tag filter only, no debounce, no OR logic between filters).
