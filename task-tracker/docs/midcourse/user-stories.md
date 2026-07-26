
**Feature: Create a Task**

# User Stories

1. Story 1: I want to create a new task with a title and optional details, so that I can track my work items.

2. Story 2: I want to assign a priority (Low, Medium, High) to a task when creating it, so that I can manage urgency.

3. Story 3: I want to set an initial status for a new task (defaulting to "ToDo"), so that I can reflect its current state from the beginning.

4. Story 4: I want to optionally assign the task to someone.

# Acceptance Criteria

- Criteria 1: Creating a task with a non‑empty title (max 200 characters) returns a `201 Created` response with the full task object, including a unique ID and timestamps.

- Criteria 2: The title cannot be blank; if it is empty or only whitespace, the API responds with an error.

- Criteria 3: If the title exceeds 200 characters, the API responds with a `422` error.

- Criteria 4: The `description`, `status`, `priority`, and `assignee` fields are optional; when omitted, the task uses the defaults: empty description, `ToDo` status, `Medium` priority, and `null` assignee.


# Flagged Assumption

- Assumption: Tasks are stored only in memory (`_tasks` dictionary). 

- Correction needed: The current implementation does not persist tasks across server restarts. The system should eventually use a persistent storage to retain data.



**Feature: List Tasks**

# User Stories

1. Story 1: I want to view all tasks, so that I can get an overview of my work.

2. Story 2: I want to filter tasks by status (ToDo, InProgress, Done), so that I can focus on tasks in a specific state.

3. Story 3: I want to filter tasks by priority (Low, Medium, High), so that I can see tasks of a certain urgency.

4. Story 4: I want to combine filters (status and priority) to narrow down the list further.

# Acceptance Criteria

- Criteria 1: A GET /tasks request without query parameters returns a list of all existing tasks.

- Criteria 2: Filtering by status returns only tasks that match the given status; tasks with other statuses are excluded.

- Criteria 3: Filtering by priority returns only tasks with the given priority.

- Criteria 4: If no tasks exist, the endpoint returns an empty list ([]), not an error.


# Flagged Assumption

- Assumption: The list endpoint returns all matching tasks without sorting.  

- Correction needed: As the number of tasks grows, this can lead to performance issues. The API should support sorting by priority.



**Feature: Retrieve a Single Task**

# User Stories

1. Story 1: I want to fetch the details of a specific task, so that I can view all its information.

2. Story 2: I want to receive a clear error if I request a non‑existent task, so that I know the ID is invalid.

# Acceptance Criteria

- Criteria 1: A GET /tasks/{task_id} request returns the full task object for the given ID with a `200 OK` status.

- Criteria 2: If the task does not exist, the API returns a 404 Not Found error with a message indicating the ID was not found.

- Criteria 3: The response includes all fields: id, title, description, status, priority, assignee.

# Flagged Assumption

- Assumption: The API does not include any authentication or authorization.

- Correction needed: In a real application, tasks might be user‑specific. The system should consider adding user authentication and associating tasks with users, so that only authorized users can access certain tasks.



**Feature: Update a Task**

# User Stories

1. Story 1: I want to update a task’s title, description, priority, assignee, or status, so that I can keep it accurate.

2. Story 2: I want to change only the fields I specify (partial update), without affecting other fields.

3. Story 3: I want to be prevented from changing the status to an invalid transition, so that my workflow stays consistent.


# Acceptance Criteria

- Criteria 1: A PATCH /tasks/{task_id} request with a JSON body containing one or more fields updates only those fields and returns the updated task.

- Criteria 2: If the request body is empty, the endpoint returns the existing task without changes (still `200 OK`).

- Criteria 3: Status transitions are validated:
  - `ToDo` → `InProgress` is allowed.
  - `InProgress` → `Done` is allowed.
  - `Done` → `InProgress` is allowed.
  - Any other transition (e.g., `ToDo` → `Done`, `Done` → `ToDo`, `InProgress` → `ToDo`) is rejected with a `422 Unprocessable Content` error and a list of allowed transitions.

- Criteria 4: Updating the title follows the same validation rules as creation: non‑blank and ≤200 characters.

- Criteria 5: If the task ID does not exist, the API returns `404 Not Found`.

# Flagged Assumption

- Assumption: The allowed status transitions are hard‑coded and cannot be configured by the user or administrator.

- Correction needed: The workflow may need to be configurable (e.g., allowing `ToDo` → `Done` directly, or adding custom statuses). The current rule is fixed, which might not fit all use cases.



**Feature: Delete a Task**

# User Stories

1. Story 1: I want to delete a task that is no longer needed, so that I can keep my task list clean.

2. Story 2: I want to be notified if I try to delete a task that does not exist, so that I understand the error.

# Acceptance Criteria

- Criteria 1: A DELETE /tasks/{task_id} request removes the task from storage.

- Criteria 2: If the task does not exist, the API returns a `404 Not Found` error.

- Criteria 3: After successful deletion, subsequent requests to retrieve that task return 404 Not Found.

# Flagged Assumption

- Assumption: Deletion is permanent and immediate; there is no soft‑delete or restore mechanism.  

- Correction needed: In many applications, tasks are soft‑deleted (marked as deleted) to allow recovery or audit trails.