# Task Tracker API

## 1. Project Overview

A learning-project REST API built with **FastAPI** and **Pydantic**, plus a single-file vanilla JS/HTML Kanban frontend. Task data lives in an **in-memory** dictionary for the lifetime of the server process — there is no database and no file-based persistence; all data resets on every restart and before/after every test run.

Implemented functionality:
- Full task CRUD: `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`
- Status-transition validation on `PATCH` (`ToDo → InProgress → Done → InProgress`; same-status and skip-ahead transitions rejected with 422)
- Tags (up to 10 per task, 32 chars each, normalized) and free-text search across `title`/`description`
- All list filters (`status`, `priority`, `tag`, `search`) combine with AND logic
- `GET /health` liveness endpoint
- Kanban-board frontend with drag-and-drop, optimistic updates, and a combined filter bar

This project is for learning REST API development, request validation, and application structure — **not** database technologies, authentication, or deployment. See [Current Limitations](#9-project-conventions-and-current-limitations).

## 2. Prerequisites

- Python 3.11 (matches the version pinned in `Dockerfile` and `.github/workflows/ci.yml`)
- `pip`
- Git
- Docker (only needed for [Run with Docker](#6-run-with-docker))

## 3. Local Setup

All commands below are copy-pasteable in order from the **repository root** (the folder created by `git clone`).

```bash
git clone https://github.com/zatzatov-sudo/Task-Tracker-API.git
cd Task-Tracker-API/task-tracker
```

Create and activate a virtual environment:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows PowerShell:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
> If PowerShell blocks the activation script with an execution policy error, run this once first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Install dependencies:
```bash
pip install -r requirements.txt
```

`.env.example` is provided (`PORT`, `APP_ENV`), but `[VERIFY]` — no code in `app/` currently reads environment variables or calls `load_dotenv()`, so copying it to `.env` is optional for running the app today:
```bash
cp .env.example .env          # macOS/Linux
Copy-Item .env.example .env   # Windows PowerShell
```

## 4. Run the App Locally

From `task-tracker/`, with the virtual environment active:

```bash
uvicorn app.main:app --reload --port 8000
```

- API base URL: `http://127.0.0.1:8000`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `curl http://127.0.0.1:8000/health`

**Frontend** (no build step — a single static file):
- Open `frontend/index.html` directly in a browser while the backend above is running.
- It calls the API at `http://localhost:8000` via `fetch()` (hardcoded `API_BASE_URL`); CORS is wide open (`allow_origins=["*"]`) so this works from a `file://` URL.

## 5. Run Tests

From `task-tracker/`, with the virtual environment active:

```bash
pytest -v
```

Tests use FastAPI's `TestClient` in-process — no server needs to be running. An autouse fixture in `tests/conftest.py` clears in-memory storage before and after every test. At the time of writing, the suite has 41 tests, all passing.

## 6. Run with Docker

From `task-tracker/` (where the `Dockerfile` lives):

```bash
docker build -t task-tracker-api .
docker run --rm -p 8000:8000 task-tracker-api
```

Then verify:
```bash
curl http://localhost:8000/health
```

Notes on the image (`Dockerfile`):
- Multi-stage build on `python:3.11-slim`; the final image contains only installed dependencies and the `app/` package.
- Runs as a non-root user (`app`), not root.
- No `--reload` in the container's `CMD` (production-style invocation: `uvicorn app.main:app --host 0.0.0.0 --port 8000`).
- No database, authentication, or deployment step is included — this module does not deploy the image anywhere.

## 7. CI Workflow Summary

`.github/workflows/ci.yml` lives at the **repository root** (outside `task-tracker/`). It:
- Triggers on every `push` and `pull_request`
- Uses `actions/checkout@v4` and `actions/setup-python@v5` pinned to Python `3.11`
- Runs all steps with `working-directory: task-tracker`
- Installs dependencies with `python -m pip install --upgrade pip` and `pip install -r requirements.txt`
- Runs `pytest -v`
- Does **not** contain `continue-on-error`, `|| true`, `--exit-zero`, output piping that could mask a failure, or any deployment step — a failing test fails the workflow run.

## 8. Project Structure

```
Task-Tracker-API/                  (git repo root)
├── .github/workflows/ci.yml       # CI: lives at repo root, not under task-tracker/
└── task-tracker/                  # the actual project (this README's directory)
    ├── app/
    │   ├── main.py                # FastAPI app + route handlers
    │   ├── models.py              # Pydantic schemas + field validation
    │   ├── business_rules.py      # status-transition state machine
    │   └── storage.py             # in-memory CRUD + filtering
    ├── tests/
    │   ├── conftest.py            # autouse storage-reset fixture
    │   ├── test_tasks.py          # pytest suite (41 tests)
    │   └── verify_a.py            # standalone ad-hoc script, not part of pytest
    ├── frontend/
    │   └── index.html             # single-file Kanban board (fetch API, no build step)
    ├── docs/midcourse/            # per-feature technical notes (see section 10)
    ├── Dockerfile
    ├── .dockerignore
    ├── requirements.txt
    ├── .env.example
    ├── CLAUDE.md                  # guidance for AI coding assistants working in this repo
    └── README.md                  # this file
```

## 9. Project Conventions and Current Limitations

- **Storage**: purely in-memory (a module-level dict in `app/storage.py`). No database, no file persistence. All data is lost on restart. `[VERIFY]` — `.gitignore` reserves `tasks.json` for "future use," but no code currently reads or writes it.
- **No authentication or authorization.**
- **No production deployment**: this module does not add deployment steps to the CI workflow or Docker setup, and neither should be treated as production-ready.
- **Filtering**: `tag` accepts a single tag per request (no OR logic between multiple tags); all filters combine with AND only. See `docs/midcourse/search-combined-filters-feature.md` for the documented scope.
- **No lint/format tooling** is configured in this repo.
- Test naming convention: `test_<action>_<condition>_returns_<status>[_<detail>]`.

## 10. Related Technical Notes

No `docs/decisions/` ADR folder exists in this repo. `[VERIFY]` — the project's own tech-stack description previously referenced an "ADR-001" for JSON-file persistence, but that ADR does not exist and storage is in-memory only; that reference has been removed from this README as stale.

The closest existing technical notes are per-feature write-ups in `docs/midcourse/`:
- [`tags-feature.md`](docs/midcourse/tags-feature.md)
- [`search-combined-filters-feature.md`](docs/midcourse/search-combined-filters-feature.md)
- [`ci-workflow-review.md`](docs/midcourse/ci-workflow-review.md)
