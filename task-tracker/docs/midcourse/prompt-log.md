
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