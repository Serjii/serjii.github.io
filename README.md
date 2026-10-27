# Serjii's Apify Actor Portfolio

A polished, modern portfolio website showcasing my [Apify](https://apify.com) actors. Built as a static site with no build step, powered by a Python data pipeline that fetches actor data from the Apify API and commits it as a static JSON file.

## How It Works

1. **Data Pipeline** — `fetch-actors.py` pulls your actor list from the Apify API and writes `actors.json`.
2. **CI** — GitHub Actions runs the script on every push to `main`, keeping the data fresh.
3. **Frontend** — Vanilla HTML, CSS, and JavaScript render `actors.json` with search, category filters, and sorting.

## Structure

```
├── actors.json            ← generated data (git-tracked)
├── fetch-actors.py        ← Python data pipeline
├── index.html             ← landing page
├── styles.css             ← design system
├── app.js                 ← client-side interactivity
├── pyproject.toml         ← Python dependencies (uv-managed)
└── .github/workflows/     ← GitHub Actions CI
```

## Running Locally

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Fetch actors
uv run python fetch-actors.py
```

## License

MIT
