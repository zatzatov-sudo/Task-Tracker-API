from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.models import TaskCreate, TaskStatus, TaskPriority, TaskUpdate, TaskResponse
from app.business_rules import validate_status_transition

app = FastAPI(
    title="Task Tracker API",
    description="A minimal learning-project API for tracking tasks.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check() -> dict:
    """Report basic service health.

    Liveness endpoint used to confirm the API process is up and
    responding; touches no application state.

    Returns:
        dict: A JSON-serializable mapping with:
            - status (str): Always "ok".
            - timestamp (str): Current UTC time in ISO 8601 format.

    Example:
        GET /health -> 200 {"status": "ok", "timestamp": "..."}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Delegates storage to `storage.add_task`, which assigns a new
    UUID and creation/update timestamps.

    Args:
        payload (TaskCreate): The task fields to create. `title` is
            required; `status` defaults to ToDo and `priority` to
            Medium if omitted.

    Returns:
        TaskResponse: The newly created task, including its
        generated `id`, `created_at`, and `updated_at`.

    Raises:
        HTTPException: 422 Unprocessable Content if `payload` fails
            `TaskCreate` validation (e.g. blank title, too many
            tags). Raised by FastAPI's request-body validation
            before this function body runs, not by this function
            itself.

    Example:
        POST /tasks {"title": "Write docs"} -> 201
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    tag: str | None = None,
    search: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered.

    Delegates to `storage.get_all_tasks`, which combines all
    provided filters with AND logic (a task must match every given
    filter to be included).

    Args:
        status (TaskStatus | None): Exact status to filter by.
        priority (TaskPriority | None): Exact priority to filter by.
        tag (str | None): A single tag to filter by; matched against
            a task's normalized tag list after stripping/lowercasing.
        search (str | None): Case-insensitive substring to match
            against a task's `title` or `description`.

    Returns:
        list[TaskResponse]: Matching tasks, in creation order.

    Example:
        GET /tasks?status=ToDo&tag=urgent
    """
    return storage.get_all_tasks(status=status, priority=priority, tag=tag, search=search)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by ID.

    Args:
        task_id (str): The task's UUID.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 Not Found if no task with `task_id`
            exists.

    Example:
        GET /tasks/{task_id} -> 200
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Only fields explicitly present in `payload` are applied; omitted
    fields are left unchanged (see `exclude_unset` handling in
    `storage.update_task`). If `payload.status` is set, the
    transition from the task's current status is validated against
    `business_rules.VALID_TRANSITIONS` before anything is persisted.

    Args:
        task_id (str): The task's UUID.
        payload (TaskUpdate): Fields to update; all fields optional.

    Returns:
        TaskResponse: The task after applying the update, with
        `updated_at` refreshed (unless no fields were set, in which
        case the task is returned unchanged).

    Raises:
        HTTPException: 404 Not Found if no task with `task_id`
            exists.
        HTTPException: 422 Unprocessable Content if `payload.status`
            is set and the transition from the task's current status
            is not in `VALID_TRANSITIONS` (raised by
            `validate_status_transition`).

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"}
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing.status, payload.status)
    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by ID.

    Args:
        task_id (str): The task's UUID.

    Returns:
        None: No response body; a 204 status confirms deletion.

    Raises:
        HTTPException: 404 Not Found if no task with `task_id`
            exists.

    Example:
        DELETE /tasks/{task_id} -> 204
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")