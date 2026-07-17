# Feature: Tags/Labels

**Branch:** mid-course-project  
**Date:** 2026-07-18  
**Status:** Complete  

## What Was Built

Tags allow users to attach short, descriptive labels to tasks (e.g. `bug`,
`frontend`, `urgent`). Tags support future search and combined filter features.

## Files Changed

### `app/models.py`
- Added `_normalize_tags()` shared helper: strips whitespace, lowercases,
  drops blanks, deduplicates, enforces max 10 tags and max 32 chars each
- Added `tags: list[str] = []` to `TaskCreate` (optional, defaults to empty)
- Added `tags: Optional[list[str]] = None` to `TaskUpdate`
  (`None` = don't touch; `[]` = clear all tags)
- Added `tags: list[str]` to `TaskResponse` (always a list, never null)

### `app/storage.py`
- `add_task`: passes `payload.tags` into `TaskResponse` constructor
- `get_all_tasks`: added `tag: Optional[str] = None` filter param;
  filters using `tag.strip().lower() in t.tags` (normalized match)
- `update_task`: no change needed; `model_dump(exclude_unset=True)` +
  `model_copy` handles tags correctly already

### `app/main.py`
- `GET /tasks`: added `tag: str | None = None` query param,
  passed through to `storage.get_all_tasks`

### `frontend/index.html`
- **Modal**: added Tags input field (comma-separated free text);
  split/trim/filter on submit; pre-filled on edit from `task.tags.join(', ')`
- **Cards**: added tag chip rendering in `buildTaskCardMarkup`;
  chips appear between description and meta row
- **Header**: added live tag filter input; filters client-side on
  the in-memory `tasks` array on every keystroke; no extra network call

### `tests/test_tasks.py`
- Added 11 new tests covering: normalization, deduplication, blank tag
  dropping, max length (422), max count (422), patch replaces tags,
  patch clears tags with `[]`, patch omits tags preserves existing,
  filter by tag returns matches, case-insensitive filter, no-match returns `[]`

## Constraints Respected

| Constraint | Value |
|---|---|
| Max tags per task | 10 |
| Max tag length | 32 characters |
| Normalization | Lowercased + stripped |
| Duplicates | Silently removed after normalization |
| `tags` in `TaskUpdate` | `null` = untouched, `[]` = cleared |
| Tag filter | Single tag, exact normalized match |
| Frontend filter | Client-side only, no backend call per keystroke |
| New dependencies | None |

## Test Results

| | Count |
|---|---|
| Baseline (before feature) | 17 passed |
| After feature | 28 passed |
| Failed | 0 |
| Errors | 0 |
| New tests added | 11 |

## Deferred / Out of Scope

- Multi-tag AND filtering (only single-tag filter implemented)
- Tag autocomplete
- Tag colors or IDs
- Dedicated tag management screen
- JSON file persistence (still in-memory, same as rest of app)