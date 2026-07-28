# Governance Retrospective

## What I shared with AI

| Item | Module | Risk Level | Reason |
|---|---|---|---|
| Task Tracker Code (`app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`) | 2-5 | Low | Learning-project source only; no secrets or real user data identified. |
| Test output and stack traces (`pytest -v`, `pydantic_core`, `starlette`, `anyio`) | 2-4 | Low | Internal paths and versions only; no sensitive application data identified. |
| Frontend code (`frontend/index.html`, `API_BASE_URL`, `fetchTasks`, `setupDragAndDrop`, `setupModal`) | 3 | Low | Localhost client code with no tokens, accounts, or private endpoints. |
| Dockerfile and CI YAML (`Dockerfile`, `.github/workflows/ci.yml`) | 4 | Low | Learning-project build configuration with no deployment secrets. |
| `CLAUDE.md`, `README.md`, `docs/midcourse/*.md` | 4-5 | Low | Architecture and decision documentation only. |
| Any real external data used by mistake | None | None | No real names, emails, passwords, or production data appeared in the reviewed prompts. |

## What I received from AI

| Generated Thing | Module | Do I understand it line by line? | Action |
|---|---|---|---|
| Backend models and validators (`TaskCreate`, `TaskUpdate`, `TaskResponse`, `_normalize_tags`) | 2 | Mostly — validators and `exclude_unset=True` are clear; `model_copy` needs a second review. | Review Pydantic `model_copy` and the null-title edge case. |
| Storage layer (`add_task`, `get_all_tasks`, `update_task`, `delete_task`, `_reset`) | 2-5 | Yes — CRUD, filter chaining, search, and test reset behavior are clear. | No action needed. |
| Business rules (`VALID_TRANSITIONS`, `validate_status_transition`) | 2 | Yes — transition lookup and HTTP 422 handling are clear. | No action needed. |
| Route handlers in `main.py` (`create_task`, `list_tasks`, `get_task`, `update_task`, `delete_task`) | 2-5 | Yes — handlers delegate to storage and business rules. | No action needed. |
| `conftest.py` fixtures and `test_tasks.py` | 2-5 | Mostly — test assertions are clear; PowerShell output piping needs practice. | Run individual tests with `pytest tests/test_tasks.py::test_name`. |
| Frontend board and drag-and-drop (`buildTaskCardMarkup`, `renderBoard`, `setupDragAndDrop`, `moveTaskStatus`) | 3 | Partially — event delegation is clear; rollback and `requestInFlight` need a second read. | Trace `moveTaskStatus` rollback in DevTools. |
| Modal logic (`openCreateModal`, `openEditModal`, `handleModalSubmit`, `originalTaskStatus`) | 3 | Mostly — create/edit state and same-status PATCH avoidance are clear. | No action needed. |
| Tag chips and live filter (`tagsHtml`, `activeFilters`, `applyFilters`) | 4-5 | Yes — chip rendering and `URLSearchParams` wiring are clear. | No action needed. |
| CI workflow (`.github/workflows/ci.yml`) | 4 | Yes — checkout, Python setup, working directory, and test execution are clear. | Verify Python 3.11 container test coverage if Docker is adopted. |
| Dockerfile (multi-stage build, non-root `app` user, `CMD`) | 4 | Mostly — the stages and non-root runtime are clear; cache behavior needs study. | Review Docker layer caching and test a local build. |
| Security findings and plans (`SEC-01` to `SEC-06`) | 5 | Mostly — I can trace evidence, distinguish Valid from Noise, and recognize course-scope limits. | Keep SEC-01 to SEC-03 as conditional production risks; treat SEC-05 as low-priority hardening; require new evidence before retaining SEC-04 or SEC-06. |
