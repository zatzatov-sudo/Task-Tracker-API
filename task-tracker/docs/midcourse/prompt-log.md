
**Feature 1: Create a Task**

# Prompt 1
- "How do I make sure the title is not just spaces but actually has text in Pydantic?"

**AI response review**:
- Accepted: The AI suggested using `@field_validator` with `strip()`.
- Edited: The AI initially gave a simple `if not value: raise ValueError`. I edited it to handle `None` safely and to strip whitespace first.
- Rejected: The AI recommended using `min_length=1` on the `str` field. I rejected this because `min_length` does not trim whitespace, so `"   "` would pass. I kept the custom validator.

# Prompt 2
- "How do I set defaults for `status` and `priority` so the user doesn't have to provide them?"

**AI response review**:
- Accepted: The AI showed me how to set `= TaskStatus.TODO` and `= TaskPriority.MEDIUM` in the model field definition.
- Edited: I changed the AI’s suggestion from using `default` in `Field()` to just using the class attribute default, which is cleaner.
- Rejected: The AI suggested making them `Optional` and handling defaults in the route. I rejected that – the schema should define defaults, not the route.

# Prompt 3
- "What should my `create_task` route return? Just the ID or the whole object?"

**AI response review**:
- Accepted: The AI explained REST conventions – returning the full resource with `201 Created` is standard practice.
- Edited: I added the `response_model=TaskResponse` and `status_code=201` based on the AI's example, but I used my own `storage.add_task` abstraction instead of writing logic directly in the route.
- Rejected: The AI initially suggested returning a `Location` header only with a 204. I rejected that – the frontend needs the data immediately.

----------------------------------------------------------------------------------------------------------------

**Feature 2: List Tasks (with filters)**

# Prompt 1
- "What is the RESTful best practice for an empty collection result set – should I return 200 OK with an empty array or 404 Not Found?"

**AI response review**:
- Accepted: The AI correctly explained that `200 OK` with `[]` is the standard and that `404` is for a specific resource that doesn't exist.
- Edited: The AI's sample code used manual `if` nesting. I edited it to a cleaner list comprehension with chained conditions.
- Rejected: The AI suggested adding a `message` field like `{"data": [], "count": 0}`. I rejected this because the spec requires a plain list `list[TaskResponse]`, not a wrapper.

# Prompt 2
- "How do I make the query parameters optional in FastAPI so the user can filter by status, priority, both, or neither?"

**AI response review**:
- Accepted: The AI showed `status: TaskStatus | None = None` and `priority: TaskPriority | None = None`. I accepted this exact type hint.
- Edited: I had to edit the import to include `Optional` (Python 3.9 compatibility) but switched to the pipe syntax per the AI.
- Rejected: The AI suggested using `Query()` with a default of `...` (required). I rejected that – filters must be optional.

# Prompt 3
- "How do I combine two filters in Python without writing a bunch of nested `if` statements?"

**AI response review**:
- Accepted: The AI proposed starting with `tasks = list(_tasks.values())` and applying filters sequentially.
- Edited: I used the AI's pattern but encapsulated it in the `storage` module, not in the route.
- Rejected: The AI suggested using `filter()` with lambdas. I rejected that for readability – list comprehensions are easier to read for my skill level.

----------------------------------------------------------------------------------------------------------------

**Feature 3: Retrieve a Single Task**

# Prompt 1
- "How do I grab the `task_id` from the URL path in FastAPI?"

**AI response review**:
- Accepted: The AI gave me the `@app.get("/tasks/{task_id}")` decorator with `task_id: str` as the function parameter. I copied this exactly.
- Edited: I added type annotation `-> TaskResponse` based on the AI's example, but specified the model explicitly.
- Rejected: The AI suggested using `int` for the ID. I rejected this – I'm using UUID strings.

# Prompt 2
- "What's the clean way to raise a 404 if my storage returns `None`?"

**AI response review**:
- Accepted: The AI showed `raise HTTPException(status_code=404, detail="...")`. I accepted this pattern.
- Edited: I edited the detail to include the specific `task_id` for better debugging (`f"Task with id {task_id} not found"`).
- Rejected: The AI suggested using `fastapi.exceptions.NotFound` or creating a custom exception class. I rejected that – keeping it simple with standard `HTTPException`.

# Prompt 3
- "If I store tasks in a dict, what's the safest way to retrieve one without causing a KeyError?"

**AI response review**:
- Accepted: The AI taught me to use `_tasks.get(task_id)` which returns `None` instead of raising `KeyError`.
- Edited: I accepted the logic but placed it inside `storage.py` to separate concerns.
- Rejected: The AI suggested using `try/except KeyError` inside the route. I rejected that – the route shouldn't know about dict internals; I used a storage function that returns `Optional[TaskResponse]`.

----------------------------------------------------------------------------------------------------------------

**Feature 4: Update a Task (including status transitions)**

# Prompt 1
- "How do I implement PATCH so the client only sends the fields they want to change?"

**AI response review**:
- Accepted: The AI pointed me to `payload.model_dump(exclude_unset=True)`. This was the key insight I needed.
- Edited: I used `model_copy(update={...})` instead of manually assigning attributes, which the AI didn't mention. I added the `updated_at` timestamp update here.
- Rejected: The AI suggested using `dict.update()` on the raw `_tasks` store. I rejected this – it bypasses the Pydantic model and breaks the response shape.

# Prompt 2
- "How do I check the status transition rules before saving the update?"

**AI response review**:
- Accepted: The AI showed me how to fetch the `existing` task first, then call a validation function before applying updates. I fully accepted this flow.
- Edited: I moved the validation logic into a separate `business_rules.py` module per the AI's suggestion, but I changed the function signature to raise an `HTTPException` instead of returning a boolean.
- Rejected: The AI suggested checking the transition *inside* the `storage.update_task` function. I rejected this because validation belongs in the business layer, not the storage layer (storage shouldn't know about workflow rules).

# Prompt 3
- "What if the payload is empty? Should I return an error or the unchanged task?"

**AI response review**:
- Accepted: The AI explained that returning the unchanged task with `200 OK` is a valid and user-friendly approach.
- Edited: I added a guard clause: `if not updates: return task` inside `storage.update_task` to avoid unnecessary writes.
- Rejected: The AI suggested returning `304 Not Modified`. I rejected this – `304` is typically for caching headers, not for application-level no-ops.

----------------------------------------------------------------------------------------------------------------

**Feature 5: Delete a Task**

# Prompt 1
- "What HTTP status code should I use when I successfully delete a task?"

**AI response review**:
- Accepted: The AI clearly explained `204 No Content` is the standard RESTful response for a successful DELETE.
- Edited: I set `status_code=status.HTTP_204_NO_CONTENT` in the decorator and made the route return `None`.
- Rejected: The AI gave an example returning `{"message": "Task deleted"}` with `200 OK`. I rejected this – 204 is more appropriate and matches the spec.

# Prompt 2
- "What if someone tries to delete a task that doesn't exist? Should I just ignore it or raise an error?"

**AI response review**:
- Accepted: The AI correctly advised that idempotency isn't an excuse to silently ignore non-existent resources – we should raise `404` to alert the client.
- Edited: I used `deleted = storage.delete_task(task_id)` and checked the boolean result.
- Rejected: The AI suggested returning `204` regardless of whether the task existed "to be idempotent". I rejected this after reading that idempotency means multiple identical requests have the same *effect*, but the response can be different (e.g., first returns 204, second returns 404). Returning 404 is standard.

# Prompt 3
- "How do I safely remove a key from a dictionary without crashing if it's not there?"

**AI response review**:
- Accepted: The AI showed me `if task_id in _tasks` or `try/except KeyError`. I accepted the `if in` pattern.
- Edited: I used `del _tasks[task_id]` and returned `True`/`False` to let the route handle the exception, keeping the storage module pure.
- Rejected: The AI suggested `_tasks.pop(task_id, None)` which silently fails. I initially accepted it, but later edited it to explicitly check `if task_id not in _tasks` for clarity, as I wanted to make the non-existence explicit to the caller via the `bool` return.

----------------------------------------------------------------------------------------------------------------

**Feature 6: Tags/Labels**

# Prompt 1
- "How do I store multiple tags on a task — as a comma-separated string or as a list?"

**AI response review**:
- Accepted: The AI recommended `list[str]` over a comma-separated string, explaining that a list serializes naturally to JSON, avoids splitting/joining on every read, and is easier to filter against.
- Edited: I kept the field as `list[str]` but set the default to `[]` (empty list) rather than `None`, so `TaskResponse.tags` is always a list and never null.
- Rejected: The AI initially suggested storing tags as `Optional[str]` with comma separation for simplicity. I rejected this because it moves parsing logic into every consumer of the field instead of keeping it clean at the model level.

# Prompt 2
- "How do I make sure tags are normalized — lowercased, stripped, and deduplicated — without repeating that logic in both `TaskCreate` and `TaskUpdate`?"

**AI response review**:
- Accepted: The AI suggested extracting the normalization into a shared helper function `_normalize_tags()` and calling it from `@field_validator("tags")` in both models. I accepted this pattern exactly.
- Edited: I added the blank-tag-drop behavior (`if not normalized: continue`) and the max-count check (`if len(result) > 10`) inside `_normalize_tags()` rather than in the validators themselves, keeping the validators as thin delegators.
- Rejected: The AI suggested using a `@model_validator` (whole-model validator) instead of a `@field_validator`. I rejected this because tags validation is self-contained to the `tags` field and doesn't depend on any other field's value — a `@field_validator` is the right tool.

# Prompt 3
- "How should `PATCH /tasks/{id}` handle tags — if the client doesn't send `tags` at all, should it clear them or leave them alone?"

**AI response review**:
- Accepted: The AI explained the distinction between "field omitted" and "field explicitly set to `[]`" using `model_dump(exclude_unset=True)`, and that `tags: Optional[list[str]] = None` in `TaskUpdate` correctly represents "not provided" as `None`.
- Edited: I confirmed that `model_copy(update={...})` in `storage.update_task` already handles this correctly without any extra code — omitting `tags` from the payload means it never appears in `exclude_unset` output, so the existing value is preserved.
- Rejected: The AI initially suggested always sending `tags` from the frontend modal on every PATCH, even if unchanged. I rejected this because it would trigger the tag validator unnecessarily and would conflict with the `originalTaskStatus` pattern we used for status — fields the user didn't touch shouldn't be included in the payload.

----------------------------------------------------------------------------------------------------------------

**Feature 7: Search + Combined Filters**

# Prompt 1
- "How do I add a free-text search to `GET /tasks` that matches against both title and description?"

**AI response review**:
- Accepted: The AI showed adding `search: str | None = None` as a query param in the route and applying it in `get_all_tasks` as a case-insensitive substring check using `query in t.title.lower()` and `query in (t.description or "").lower()`.
- Edited: I added `if query:` after `query = search.strip().lower()` so that an empty or whitespace-only search string is treated as no filter rather than matching nothing — an empty string would otherwise match every task, which is the correct behavior, but the intent is clearer with the explicit guard.
- Rejected: The AI suggested using Python's `re` module with `re.search(pattern, text, re.IGNORECASE)` for more powerful matching. I rejected this — simple `in` substring matching is sufficient, easier to read, and introduces no regex edge cases for a learning project.

# Prompt 2
- "How do I combine all four filters (`status`, `priority`, `tag`, `search`) so they all apply together without getting messy?"

**AI response review**:
- Accepted: The AI suggested the sequential filter pattern already used for `status` and `priority` — start with all tasks, then apply each active filter in order, shrinking the list at each step. I accepted this AND-logic approach and added `search` as the final step after `tag`.
- Edited: I kept `search` applied last because it is the most expensive check (two string comparisons per task) — filtering by enum fields first reduces the set before the substring scan runs.
- Rejected: The AI suggested building a single compound `filter()` call with all conditions in one expression. I rejected this for readability — four conditions in one line is harder to extend and debug than four sequential `if` blocks.

# Prompt 3
- "Should the frontend filter bar call the API on every keystroke, or should it filter the already-loaded tasks locally in JavaScript?"

**AI response review**:
- Accepted: The AI recommended always calling the API on filter change so the server remains the source of truth, and introduced the `activeFilters` state object with `applyFilters()` building `URLSearchParams` from it. I accepted this architecture fully.
- Edited: I wired each of the four inputs (`searchInput`, `statusFilter`, `priorityFilter`, `tagFilterInput`) to update `activeFilters` and call `applyFilters()` on `input`/`change` events, replacing the previous client-side `tagFilterInput` listener that operated on the in-memory `tasks` array.
- Rejected: The AI suggested adding debounce (e.g. 300ms delay) to the search input to reduce API calls while typing. I rejected this for now — the project runs locally against an in-memory store, so every keystroke completing instantly is fine. Debounce is noted as a future improvement in the feature docs.