# Task Tracker API

A minimal learning-project REST API built with **FastAPI** and **Pydantic**, using a local JSON file for data persistence (see ADR-001). This project focuses on learning REST API development, request validation, and application structure — not database technologies.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- Local JSON file (`tasks.json`) for persistence (added in a later step)
- HTML/CSS/JavaScript frontend using the Fetch API (added in a later step)

## Features

### Core CRUD
- `POST /tasks` — create a task with title, description, status, priority, assignee, and tags
- `GET /tasks` — list all tasks, with optional filters: `status`, `priority`, `tag`
- `GET /tasks/{id}` — fetch a single task by ID
- `PATCH /tasks/{id}` — partial update with status-transition validation
- `DELETE /tasks/{id}` — delete a task (returns 204, no body)

### Business Rules
- Status transitions are validated: `ToDo → InProgress → Done → InProgress`
- Same-status transitions are rejected (422)
- Skip-ahead transitions (e.g. `ToDo → Done`) are rejected (422)

### Tags/Labels
- Tasks support up to 10 tags, each max 32 characters
- Tags are normalized: lowercased, stripped, deduplicated
- Filter tasks by tag via `GET /tasks?tag=bug`
- Tag chips rendered on each card in the UI
- Live client-side tag filter in the board header

### Search + Combined Filters
- Free-text search across task title and description via `GET /tasks?search=login`
- All filters combinable in a single request with AND logic:
  `GET /tasks?status=ToDo&priority=High&tag=bug&search=login`
- Empty or whitespace-only search treated as no filter
- Invalid enum values (`status`, `priority`) return 422 automatically
- Frontend: compact four-input filter bar (search, status, priority, tag)
- Filters trigger an API call on every change — server is always source of truth
- Empty filter results show the empty state banner with columns still visible

### Frontend
- Kanban board with three columns: To Do, In Progress, Done
- Four UI states: loading, ready, empty, error (with retry)
- Drag-and-drop between columns with optimistic updates and rollback on rejection
- Create/edit modal with client-side validation and server error surfacing
- Live tag filter in the header (client-side, no extra network call)

## Current Scope

This skeleton currently includes:
- Basic FastAPI application setup
- A `GET /health` endpoint for verifying the service is running

CRUD endpoints, storage logic, authentication, and the frontend are intentionally **not** included yet — they will be added in later steps.

## Prerequisites

- Python 3.10 or higher
- `pip`

## Setup Instructions

1. Clone or download this project, then move into the project folder:
```bash
   cd task-tracker
```

2. Create a virtual environment:
```bash
   python -m venv venv
```

3. Activate the virtual environment:

   - **Linux/macOS:**
```bash
     source venv/bin/activate
```
   - **Windows (PowerShell):**
```powershell
     venv\Scripts\Activate.ps1
```

4. Install dependencies:
```bash
   pip install -r requirements.txt
```

5. Copy the example environment file and adjust if needed:
```bash
   cp .env.example .env
```
   (On Windows PowerShell: `Copy-Item .env.example .env`)

## How to Run the Project

### Prerequisites

- Python 3.10 or higher
- `pip`
- Git

### 1. Clone the repository

```bash
git clone https://github.com/zatzatov-sudo/Task-Tracker-API.git
cd Task-Tracker-API
```

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Copy the environment file

**macOS/Linux:**
```bash
cp .env.example .env
```

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

---

## Running the Backend

From the project root, with the virtual environment active:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

You should see:
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.

Keep this terminal open while using the app — press `Ctrl+C` to stop the server.

### Verify the backend is running

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-07-18T..."
}
```

### Swagger UI (interactive API docs)

With the server running, open your browser to:
http://127.0.0.1:8000/docs

All endpoints are listed and testable directly from the browser.

---

## Opening the Frontend

The frontend is a single static HTML file — no build step required.

1. Make sure the backend is running (see above)
2. Open this file directly in your browser:
task-tracker/frontend/index.html

**Windows:** navigate to the file in File Explorer and double-click it, or drag it into a browser tab.

**macOS/Linux:**
```bash
open frontend/index.html
```

The Kanban board will load and fetch tasks automatically from `http://localhost:8000`.

> **Note:** The frontend communicates with the backend via `fetch()`. CORS is enabled on the backend for local development, so opening the file via `file://` works without a local web server.

---

## Running the Tests

Tests use `pytest` with FastAPI's `TestClient` — no running server needed, the test client handles everything in-process.

From the project root, with the virtual environment active:

```bash
pytest
```

For verbose output showing each test name and result:

```bash
pytest -v
```

### Expected output
collected 28 items
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED
...
28 passed in 0.XX s

### Saving a test baseline

To run tests and save the results to a file for comparison:

**Windows PowerShell:**
```powershell
pytest -v 2>&1 | Tee-Object -FilePath "baseline_test_results.txt"
```

**macOS/Linux:**
```bash
pytest -v | tee baseline_test_results.txt
```


## Project Status

This is an early-stage skeleton (Module 1). Future modules will add task CRUD endpoints, JSON file-based storage logic, and a simple frontend.