# Mini-ADR: Task Tracker Design Alternatives

**Alternatives AI suggested but were rejected by me**



## ADR‑001: Data Persistence Strategy

### Decision
Store all tasks in an in‑memory Python dictionary (`_tasks`). Data is lost when the server restarts.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **JSON File** (`tasks.json`) | Simple to implement; no external dependencies; data survives restarts. | Concurrency issues (write conflicts); poor performance with many tasks; no query capabilities. |

| **SQLite** | ACID compliant; supports complex queries; no external server required. | Adds a dependency; requires schema migrations; slightly heavier setup. |

| **PostgreSQL / MongoDB** | Scalable; robust; production‑ready. | Requires external infrastructure; overkill for a learning project. |

**Current Choice:** In‑memory dictionary (deferred persistence).  
**Future Direction:** Implement JSON file storage (as hinted in the README) to persist data across restarts while keeping the project beginner‑friendly.

----------------------------------------------------------------------------------------------------------------

## ADR‑002: Status Transition Rules

### Decision
Hard‑code a fixed set of allowed transitions:
- `ToDo` → `InProgress`
- `InProgress` → `Done`
- `Done` → `InProgress`

Any other transition returns a `422 Unprocessable Content` error.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **Allow all transitions** (e.g., `ToDo` ↔ `Done`) | Maximum flexibility; simpler logic. | Risks breaking business workflow (e.g., marking "Done" without working on it). |

| **Configurable transitions** (via `.env` or database) | Adaptable to different team workflows; no code change needed. | Adds complexity to validation logic and storage. |

| **State machine library** (e.g., `transitions`) | Robust; handles side‑effects; visualizable. | Heavy dependency; overkill for only 3 states. |
| **Soft‑delete / Archive state** | Allows recovering deleted tasks. | Introduces an extra state; complicates the default list view. |

**Current Choice:** Hard‑coded transitions (simple and explicit).  
**Future Direction:** If the project grows, consider moving the transition map to a configuration file or database to make it user‑adjustable.

----------------------------------------------------------------------------------------------------------------

## ADR‑003: Task Listing & Querying (Pagination / Sorting)

### Decision
The `GET /tasks` endpoint returns **all** matching tasks in a single array. No pagination or sorting is provided.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **Offset‑based pagination** (`skip`/`limit`) | Easy to implement; familiar to most API consumers. | Performance degrades with large offsets; inconsistent if data changes between requests. |

| **Cursor‑based pagination** (e.g., `after_id`) | Stable for real‑time data; better performance. | More complex to implement; requires a sortable unique field. |

| **Sorting parameters** (`sort_by`, `order`) | Gives users control over data presentation. | Adds complexity to the filtering logic and storage query layer. |

| **Full‑text search** | Useful for large datasets. | Requires indexing; too heavy for a simple tracker. |

**Current Choice:** No pagination/sorting (keeps the learning project minimal).  
**Future Direction:** Add `skip`/`limit` and `sort_by` query parameters when the number of tasks grows beyond a practical threshold (e.g., > 100 tasks).

----------------------------------------------------------------------------------------------------------------

## ADR‑004: Task Identifier Strategy

### Decision
Use **UUID v4** (random) as the unique identifier for each task.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **Auto‑incrementing integer** | Human‑readable; easy to type; natural ordering. | Reveals volume of data; collisions in distributed systems; harder to merge data from multiple sources. |

| **ULID** | Sortable; URL‑safe; combines timestamp with randomness. | Less commonly used; fewer library defaults. |

| **Nanoid / Short UUID** | Shorter than standard UUID; good for URLs. | Less collision‑resistant than UUIDv4 (though still highly unlikely). |

**Current Choice:** UUID v4 (standard, globally unique, safe for distributed development).  
**Future Direction:** No change planned, though switching to ULID could improve sortability without sacrificing uniqueness.

----------------------------------------------------------------------------------------------------------------

## ADR‑005: Partial Updates (PATCH) Implementation

### Decision
Use Pydantic's `model_dump(exclude_unset=True)` to update only the fields provided in the request body. Missing fields are left untouched.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **PUT (full replacement)** | Simpler semantics; the request body must contain the entire resource. | Forces clients to send all fields; increases payload size; error‑prone if fields are omitted accidentally. |

| **JSON Patch (RFC 6902)** | Granular control (add/remove/replace specific fields). | Overly complex for a simple CRUD API; harder to validate. |

| **GraphQL mutations** | Client specifies exactly which fields to update. | Requires a GraphQL server; steep learning curve. |

**Current Choice:** `PATCH` with `exclude_unset` (idiomatic FastAPI, clear separation of concerns).  
**Future Direction:** No change; this is a robust and standard approach for RESTful partial updates.

----------------------------------------------------------------------------------------------------------------

## ADR‑006: Authentication & Authorization

### Decision
Currently, **no authentication** is implemented. Any client can create, read, update, or delete any task.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **API Key (static)** | Easy to add; minimal overhead. | Not user‑specific; cannot enforce per‑user permissions. |

| **JWT (Bearer Token)** | Stateless; user‑scoped; widely supported. | Adds complexity (login endpoint, token refresh, secret management). |

| **OAuth2 / SSO** | Enterprise‑grade; supports external providers. | Significant implementation overhead. |

| **Basic Auth (over HTTPS)** | Simple to test with curl. | Sends credentials with every request; less secure. |

**Current Choice:** No authentication (keeps the focus on core CRUD for learning).  
**Future Direction:** If this were to be deployed publicly, add JWT‑based authentication and associate each task with a `user_id` to enforce data isolation.

----------------------------------------------------------------------------------------------------------------

## ADR‑007: Error Handling & Status Codes

### Decision
Use FastAPI's built‑in `HTTPException` with explicit status codes (e.g., `404`, `422`). Validation errors are automatically handled by Pydantic.

### Alternatives Considered

| Alternative | Pros | Cons |
| :--- | :--- | :--- |

| **Global exception handlers** (`@app.exception_handler`) | Centralized logging; consistent error response shapes. | More boilerplate to set up. |

| **Raise custom domain exceptions** | Decouples HTTP layer from business logic. | Requires mapping exceptions to status codes in a middleware or handler. |

| **Return `None` and check in route** (current pattern for `storage`) | Simple to read. | Mixes domain logic with HTTP concerns; easy to forget checks. |

**Current Choice:** Direct `HTTPException` in route handlers (simple and clear for a small project).  
**Future Direction:** Introduce custom exceptions (e.g., `TaskNotFoundError`) and a global exception handler to standardize the error response format (e.g., `{"detail": "...", "code": "..."}`).

----------------------------------------------------------------------------------------------------------------