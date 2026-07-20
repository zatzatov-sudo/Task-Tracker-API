# Technical Decision Note: Dockerfile Design

**Project:** Task Tracker API — Module 4  
**Branch:** mid-course-project  
**Status:** DRAFT  
**Date:** 2026-07-20  

---

## 1. Context

The Task Tracker API is a learning-project FastAPI backend with a single-file
vanilla JS frontend. It has no database, no authentication, and no production
deployment target — data lives in an in-memory dict that resets on every
process restart. The backend is a thin 4-file Python package (`app/`) served
by Uvicorn.

Up to this module the app was run exclusively via a local virtual environment
(`uvicorn app.main:app --reload --port 8000`). Module 4 introduced a
`Dockerfile` to package the backend into a container image, and a
`.dockerignore` to control what gets copied into the build context. A CI
workflow (`.github/workflows/ci.yml`) was also added to run the pytest suite
automatically on every push and pull request.

The motivations for adding Docker at this stage:

- Practice containerization as a skill, independent of whether the image is
  ever deployed anywhere.
- Establish a repeatable, environment-independent way to run the API without
  needing to manage a local Python version or venv manually.
- Pair with the CI workflow, which uses a clean Ubuntu runner rather than any
  contributor's local machine.

---

## 2. Decision

The project uses a **multi-stage Docker build** on `python:3.11-slim`. The
builder stage installs dependencies from `requirements.txt` into a dedicated
layer; the final stage copies only the installed packages and the `app/`
package — not the full source tree, test files, or documentation. The
container runs as a **non-root user** (`app`). Uvicorn is started without
`--reload` (`CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port",
"8000"]`), which is appropriate for a containerized invocation even though
this project does not deploy the image.

The CI workflow runs on `ubuntu-latest`, sets `working-directory: task-tracker`
for all steps, and runs `pytest -v` directly — no Docker build step is
included in CI. Tests run against the local Python environment in the runner,
not inside the container.

---

## 3. Alternatives Considered

**Single-stage build on `python:3.11`**  
Simpler to write, but produces a larger image because it includes the full
CPython toolchain and build utilities that are not needed at runtime. The
multi-stage approach keeps the final image smaller by starting from
`python:3.11-slim` and discarding build-time artifacts. [VERIFY — actual
image size difference was not measured.]

**Running as root inside the container**  
Docker containers run as root by default unless told otherwise. Running as a
non-root user (`app`) is a standard security practice even for non-production
images, and it costs nothing to implement at this scale.

**Including `--reload` in the container CMD**  
`--reload` watches the filesystem for changes and restarts Uvicorn
automatically — useful during local development but not inside a container
where the source files are baked in at build time and do not change while the
container is running. It was excluded from the container's `CMD` for this
reason.

**Running the Docker build in CI**  
The CI workflow installs dependencies and runs pytest directly on the runner
rather than building the Docker image and running tests inside it. This keeps
CI fast and simple for a learning project. [VERIFY — a separate workflow job
that builds and smoke-tests the image was considered but not implemented.]

---

## 4. Trade-offs

DRAFT - REWRITE IN MY OWN WORDS

- The multi-stage build adds a small amount of `Dockerfile` complexity
  (two `FROM` statements, explicit `COPY --from=builder`) in exchange for a
  leaner final image. For a project this size the size saving is not
  practically meaningful, but the pattern is worth learning.
- Running tests in CI outside the container means the test environment (Ubuntu
  runner + Python 3.11 venv) is not identical to the container environment.
  In practice both use Python 3.11 on Linux, so divergence is unlikely — but
  it is not zero. [VERIFY]
- The frontend (`frontend/index.html`) is excluded from the Docker image
  entirely. The container serves only the API; the frontend must still be
  opened as a local `file://` page pointing at `http://localhost:8000`. This
  is intentional given the module's scope, but it means `docker run` alone
  does not give you a usable full-stack experience without also opening the
  HTML file separately.
- Pinning to Python `3.11` in the `Dockerfile` and `ci.yml` while the local
  venv runs Python `3.14.6` means there is a version gap between local
  development and CI/container environments. [VERIFY — all 41 tests pass
  locally on 3.14.6; whether they pass on 3.11 inside the container has not
  been verified in this session.]

I would do this differently by running at least one CI job that builds the
Docker image and hits `/health` to confirm the container starts correctly,
so the image is actually validated and not just theoretically correct.

---

## 5. Consequences

**Positive:**
- Anyone with Docker installed can run the API backend with two commands
  (`docker build` + `docker run`) without installing Python, creating a venv,
  or managing dependencies manually.
- The non-root user and slim base image establish correct habits for
  containerization, even though this image is not deployed anywhere.
- CI gives automatic feedback on every push — if a code change breaks any of
  the 41 tests, the workflow fails visibly before the branch is merged.

**Negative:**
- The Docker image is never actually deployed or smoke-tested in CI, so a
  broken `Dockerfile` (e.g. a missing `COPY` line) would not be caught
  automatically. [VERIFY]
- The frontend is not served by the container, so the Docker setup only covers
  half the application.
- Maintaining a Python version pin across `Dockerfile`, `ci.yml`, and the
  local venv is a new source of potential inconsistency that did not exist
  before this module.

---

## 6. Open Questions

DRAFT - REWRITE IN MY OWN WORDS

- **Should the Docker image be smoke-tested in CI?** Adding a step that runs
  `docker build` and `curl http://localhost:8000/health` would confirm the
  image actually works, not just that the Python tests pass. [VERIFY — assess
  whether this is in scope for this module or a later one.]
- **Should the frontend be served by the container?** Copying
  `frontend/index.html` into the image and serving it as a static file (via
  Uvicorn's `StaticFiles` mount or a separate Nginx stage) would make
  `docker run` give a complete working app. Out of scope for this module but
  worth noting.
- **Does the test suite pass on Python 3.11 inside the container?** Local
  development uses Python 3.14.6; CI and the container use 3.11. All 41 tests
  are expected to pass on both, but this has not been explicitly confirmed.
  [VERIFY]
- **What happens to in-memory data when the container restarts?** The same as
  with the local venv — all task data is lost. This is documented and
  intentional, but worth flagging if the Dockerfile is ever reused as a
  starting point for a version of the app that adds persistence.