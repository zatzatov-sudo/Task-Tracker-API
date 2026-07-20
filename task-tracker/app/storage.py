from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task.

    Generates a new UUID and sets `created_at`/`updated_at` to the
    current UTC time. A `None` `payload.description` is stored as an
    empty string.

    Args:
        payload (TaskCreate): The already-validated task data.

    Returns:
        TaskResponse: The stored task, including its generated `id`
        and timestamps.
    """
    now = datetime.now(timezone.utc)
    task_id = str(uuid4())
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered.

    Filters are applied in sequence (status, then priority, then
    tag, then search) and combined with AND logic; a task must match
    every provided filter. `tag` is matched as a single normalized
    tag against `TaskResponse.tags`. `search` matches a
    case-insensitive substring against `title` or `description`; a
    blank/whitespace-only `search` is treated as no filter.

    Args:
        status (Optional[TaskStatus]): Exact status to filter by.
        priority (Optional[TaskPriority]): Exact priority to filter
            by.
        tag (Optional[str]): Single tag to filter by (stripped and
            lowercased before comparison).
        search (Optional[str]): Substring to search for in `title`
            or `description` (case-insensitive).

    Returns:
        list[TaskResponse]: Matching tasks, in insertion (creation)
        order.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    if tag is not None:
        tasks = [t for t in tasks if tag.strip().lower() in t.tags]
    if search is not None:
        query = search.strip().lower()
        if query:
            tasks = [
                t for t in tasks
                if query in t.title.lower()
                or query in (t.description or "").lower()
            ]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by ID.

    Args:
        task_id (str): The task's UUID.

    Returns:
        Optional[TaskResponse]: The task if found, otherwise None.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Only fields explicitly set on `payload` are applied (via
    `model_dump(exclude_unset=True)`); fields left unset on
    `payload` are unchanged. If no fields were set, the task is
    returned unchanged and `updated_at` is not bumped. This function
    does not itself validate status transitions — callers (see
    `main.update_task`) are expected to call
    `business_rules.validate_status_transition` first when
    `payload.status` is set.

    Args:
        task_id (str): The task's UUID.
        payload (TaskUpdate): Fields to update.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task
        with `task_id` exists.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    updated = task.model_copy(
        update={**updates, "updated_at": datetime.now(timezone.utc)}
    )
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task by ID.

    Args:
        task_id (str): The task's UUID.

    Returns:
        bool: True if a task was found and deleted, False if no task
        with `task_id` existed.
    """
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()