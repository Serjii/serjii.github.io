# T03 — `fetch-actors.py` CI — GitHub Actions Workflow

> **Status:** ⏭️ Won't Implement
> **Reason:** The task author decided to keep data updates manual (run `fetch-actors.py` locally). GitHub Actions would cost nothing, but adding a CI workflow for a manual process was deemed unnecessary overhead.
> **Est. time:** N/A
> **Depends on:** —

## Goal

Every push to `main` runs `fetch-actors.py` and commits the updated `actors.json`.

## Requirements

- [ ] Create `.github/workflows/fetch-actors.yml`
- [ ] Trigger on: `push` to `main`, and optionally a `schedule` (e.g. weekly)
- [ ] Steps:
  1. Checkout code
  2. Set up Python 3.11+ and `uv` (`actions/setup-uv`)
  3. Install dependencies (`uv sync --frozen`)
  4. Run `uv run python fetch-actors.py`
  5. Check if `actors.json` changed; if so, commit and push
- [ ] Use `secrets.APIFY_TOKEN` for authentication (never stored in repo)
- [ ] Commit message: `chore: update actors.json`
- [ ] Push with proper git config (user.name, user.email) and auth token

## Deliverable

Workflow runs successfully on push and updates `actors.json`.

## Notes

- The current `.github/workflows/fetch-actors.yml` is just a placeholder comment.
- Use `actions/checkout@v4` with `token` for the push step.
- The `APIFY_USERNAME` can be hardcoded in the workflow as it's not secret.

## Reference

See `fetch-actors.py` for the script's expected behavior and env vars.
