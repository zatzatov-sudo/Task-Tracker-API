# Feature: Search + Combined Filters

**Branch:** mid-course-project  
**Date:** 2026-07-18  
**Status:** Complete  

## What Was Built

Extended `GET /tasks` to support free-text search across title and description,
and combined filtering — all filters (status, priority, tag, search) can be used
together in a single request with AND logic. The frontend filter bar was replaced
with a compact four-input bar wired to the backend on every change.

## Files Changed

### `app/storage.py`
- `get_all_tasks`: added `search: Optional[str] = None` parameter
- Search applied last, after all other filters (AND logic)
- Case-insensitive substring match against `title` and `description`
- Empty or whitespace-only search is treated as no filter (returns unfiltered set)

### `app/main.py`
- `GET /tasks`: added `search: str | None = None` query param
- Passed through to `storage.get_all_tasks`
- All five params (`status`, `priority`, `tag`, `search`) now combinable freely

### `frontend/index.html`
- Replaced single tag filter input with a four-input compact filter bar:
  - Text search input (`search`) — matches title and description
  - Status dropdown (`status`) — All statuses / ToDo / InProgress / Done
  - Priority dropdown (`priority`) — All priorities / High / Medium / Low
  - Tag input (`tag`) — carries over from Tags feature
- Added `activeFilters` state object tracking all four filter values
- Added `applyFilters()` function — builds query params from active filters,
  fetches from `GET /tasks` with combined params, re-renders board
- Each filter input wired to `applyFilters()` on `input`/`change` event
- Columns remain visible in all states including empty filter results
- Responsive: filter bar wraps on narrow screens (≤900px)

### `tests/test_tasks.py`
- Added 13 new tests covering:
  - Search matches title
  - Search matches description
  - Search is case-insensitive
  - Search no match returns 200 + `[]`
  - Empty search string returns all tasks
  - Whitespace-only search returns all tasks
  - Combined status + priority
  - Combined status + search
  - Combined priority + tag
  - Combined all four filters
  - Invalid status value returns 422
  - Invalid priority value returns 422
  - Combined filters no match returns 200 + `[]`

## Constraints Respected

| Constraint | Value |
|---|---|
| Search fields | `title` and `description` only |
| Search match type | Case-insensitive substring |
| Filter logic | AND across all active filters |
| Empty/whitespace search | Treated as no filter |
| Empty result | 200 + `[]`, columns stay visible |
| Invalid enum | 422, auto-handled by FastAPI/Pydantic |
| New dependencies | None |
| Debounce | Not implemented (deferred) |

## Test Results

| | Count |
|---|---|
| Baseline (before feature) | 28 passed |
| After feature | 41 passed |
| Failed | 0 |
| Errors | 0 |
| New tests added | 13 |

## Deferred / Out of Scope

- Due date filter
- OR logic between filters
- Saved/pinned filter combinations
- Debounce on search input
- Assignee search