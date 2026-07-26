# Security Review

**Scope:** Read-only source and configuration review of the Task Tracker API.
**Date:** 2026-07-22

## Findings

| ID | Severity | Grade | Reason | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|---|---|
| SEC-01 | Medium | Valid | The absence of authentication is real and intentionally out of course scope; it becomes a meaningful production risk if the API is exposed beyond a trusted local environment. | `app/main.py:44-186`; `README.md:147` | All task data and write operations are unauthenticated and unscoped. This is documented as intentional course scope, but would expose every task to any caller if the service were network-accessible. | The API defines CRUD routes without auth dependencies; the README states that there is no authentication or authorization. | Keep the service local-only for the course. Before shared or deployed use, add authentication and per-user/task authorization. | High |
| SEC-02 | Medium | Valid | The cited input and storage bounds are absent, creating a supported availability/scalability concern outside the learning scope. | `app/models.py:52-57, 106-111`; `app/storage.py:7, 69-84` | `description`, `assignee`, and raw tag-list input have no size cap; storage is an unbounded in-memory dictionary and list responses have no pagination or maximum size. Large requests or many created tasks can consume memory and produce oversized responses. | Titles are capped at 200 characters and normalized tags at 10/32 characters, but descriptions and assignees are plain optional strings. Tag normalization processes every submitted item before applying the normalized-tag count limit. | Add server-side field and request-size limits; cap raw tag input; add pagination and bounded storage before exposing the API beyond learning use. | High |
| SEC-03 | Medium | Valid | The permissive CORS and all-interface binding are present and become a real cross-origin risk when the unauthenticated API is non-locally reachable. | `app/main.py:16-20`; `frontend/index.html:601`; `Dockerfile:20-24` | CORS permits every origin, method, and header, while the container listens on all interfaces. Together with no authentication, a non-local deployment would allow arbitrary websites to read and modify task data. | CORS uses wildcard origins, methods, and headers; the frontend assumes `http://localhost:8000`; Docker runs Uvicorn with `--host 0.0.0.0`. | Restrict CORS to explicit trusted origins and expose/bind the container only as needed before non-local deployment. | High |
| SEC-04 | Low | Noise | The observations are generic CI hardening advice, not a demonstrated repository-specific weakness or compromise. | `../.github/workflows/ci.yml:16-26`; `requirements.txt:1-27` | CI installs packages without hash verification, and GitHub Actions are referenced by movable major-version tags rather than immutable commit SHAs. | Dependencies are version-pinned, but no artifact hashes are present. The workflow uses `actions/checkout@v4` and `actions/setup-python@v5`, with no explicit `permissions` block. | Retain only if the grading rubric explicitly assesses production CI supply-chain hardening. | High |

## Course-scope context

- **SEC-01** is explicitly an intentional course-scope decision: the README states that authentication and authorization are out of scope. It becomes a vulnerability when the API is exposed beyond a trusted local learning environment.
- **SEC-03** is likely local-development convenience: wide CORS allows the static `file://` frontend to call localhost. It becomes a vulnerability when the API is reachable by untrusted clients.
- **SEC-02** is partly a consequence of the in-memory learning design. It becomes an availability risk as usage or exposure grows.
- **SEC-04** is production hardening debt, not evidence of a compromise or a demonstrated vulnerability.

## Categories with no issue found

- Enum handling and unknown request fields: status/priority enums and `extra="forbid"` are defined in `app/models.py`.
- Title and normalized-tag validation: the code rejects blank/oversized titles and oversized/too-many normalized tags; tests cover these behaviors.
- Backend error handling: no application-level broad exception catch or custom stack-trace response was found in `app/main.py` or `app/business_rules.py`.
- Frontend task content is escaped before dynamic HTML rendering in `frontend/index.html`.
- Docker runs as a non-root user and `.dockerignore` excludes `.env` files.
- No Compose configuration was found.

## Files inspected

- `agents.md`
- `README.md`
- `app/main.py`
- `app/models.py`
- `app/storage.py`
- `app/business_rules.py`
- `tests/conftest.py`
- `tests/test_tasks.py`
- `tests/verify_a.py`
- `frontend/index.html`
- `requirements.txt`
- `Dockerfile`
- `.env.example`
- `.gitignore`
- `.dockerignore`
- `../.github/workflows/ci.yml`

## Audit limits

- This was a source/configuration review only. The app, tests, dependency scanning, container build, and external vulnerability/CVE checks were not run.
- The existing `.env` file was not read; only metadata was observed, to avoid exposing potential secrets.
- No Git inspection was used, so tracking status and repository-level CI settings were not verified.
