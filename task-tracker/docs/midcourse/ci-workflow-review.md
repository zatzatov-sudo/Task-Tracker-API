# CI Workflow Review (Module 4)

Review of `.github/workflows/ci.yml` against the Module 4 CI safety checklist. No issues found; no changes made to the workflow file.

| Check | Pass/Concern | Evidence | Minimal fix |
|---|---|---|---|
| Missing push/pull_request trigger | Pass | `on: push: / pull_request:` both present | — |
| Python version not pinned to 3.11 | Pass | `python-version: "3.11"`, exact version | — |
| Dependencies installed but pytest never run | Pass | `pytest -v` runs as its own step after install | — |
| `continue-on-error` | Pass | No occurrence in file | — |
| `\|\| true` | Pass | No occurrence in file | — |
| `--exit-zero` | Pass | No occurrence in file | — |
| pytest output piped in a way that hides exit code | Pass | `pytest -v` runs alone — no pipe, tee, or redirection | — |
| Deployment steps that don't belong in this module | Pass | Only checkout, setup-python, install, test steps present | — |
| Workflow file in the wrong folder | Pass | File lives at repo root `.github/workflows/ci.yml`, not under `app/` or `task-tracker/` | — |

Verified live via the GitHub Actions API: both the `mid-course-project` push (`1116b85`) and a throwaway branch push (`ac39acf`) completed with `conclusion: success`.
