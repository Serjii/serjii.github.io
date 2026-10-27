# Agent Guide — Apify Actor Portfolio Website

> **Repo:** `serjii.github.io`
> **Deploy:** GitHub Pages → `https://serjii.github.io`

---

## What Is This?

A polished, modern portfolio website showcasing [Apify](https://apify.com) actors. Built as a static site — no build step, no framework, just HTML + CSS + vanilla JS. Data is fetched by a Python script, committed to the repo, and served statically.

## How It Works

1. **Data Pipeline** — `fetch-actors.py` pulls actor data from the Apify API and writes `actors.json`.
2. **CI** — GitHub Actions runs the script on every push to `main`, keeping data fresh.
3. **Frontend** — Vanilla HTML/CSS/JS renders `actors.json` with search, category filters, and sorting.

## Architecture

```
serjii.github.io/
├── actors.json              ← generated data (git-tracked)
├── fetch-actors.py          ← Python data pipeline
├── index.html               ← landing page
├── styles.css               ← design system
├── app.js                   ← client-side interactivity
├── pyproject.toml           ← Python dependencies (uv-managed)
├── uv.lock                  ← lockfile (git-tracked)
├── .env.example             ← template for env vars
├── assets/
│   ├── favicon.svg
│   └── og-image.png
├── .github/workflows/       ← GitHub Actions CI
├── .tasks/                  ← task files (see backlog)
│   └── backlog.md
├── PLAN.md                  ← full project plan
├── README.md
└── AGENT.md                 ← this file
```

## Quick Start (Local Dev)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set env vars (copy .env.example → .env and fill in)
cp .env.example .env
# Edit .env: APIFY_TOKEN=..., APIFY_USERNAME=serj_henrique

# Fetch actor data
uv run python fetch-actors.py

# Serve locally
python -m http.server 8000
# Visit http://localhost:8000
```

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Vanilla JS (no framework) | Zero build step, instant load, GitHub Pages compatible |
| Static JSON (not live API) | No token exposure in browser, works offline |
| `uv` as package manager | Fast, zero-config venv, `pyproject.toml`-native |
| `requests` for Python | Standard, lightweight |
| GitHub Actions for CI | Free, integrated, automatic on push |
| CSS custom properties | Easy theming, DRY |
| Outfit font (variable weight) | Clean, modern typography |

## Important API Notes

These come from research and debugging — **critical context for any changes to `fetch-actors.py`**:

- **Auth method:** Use `Bearer <token>` in the `Authorization` header, OR `?token=<token>` as a query parameter. Basic Auth is **not** supported.
- **Response wrapper:** Every Apify API response wraps data in a `data` key: `{"data": {...}}`. The `fetch_json()` function auto-unwraps this.
- **List endpoint (`GET /v2/actors?my=1`):** **Always requires authentication**. Returns minimal fields per actor.
- **Detail endpoint (`GET /v2/actors/{id}`):** No auth needed for public actors. Returns full data including `description`, `isPublic`, `categories`, `pictureUrl`, `seoTitle`, `seoDescription`, `actorReviewCount`, `actorReviewRating`, `bookmarkCount`.
- **Rate limits:** 250K req/min global, 60 req/sec per resource. The script retries with exponential backoff on 429.
- **Pagination:** List endpoint uses `offset`/`limit` pagination. Script fetches 1000 per page until empty.

## Task Management

All work is tracked in `.tasks/`:

- **`backlog.md`** — Index of all tasks with ID, title, status, and links.
- **`Txx-*.md`** — Individual task files with full requirements, checklists, and notes.

Use `backlog.md` as your starting point. Open a task file for full details on what needs to be done.

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Done |
| ❌ | Pending |
| 🟡 | Partially done |
