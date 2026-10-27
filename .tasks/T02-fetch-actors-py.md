# T02 — `fetch-actors.py` — Apify API Data Pipeline

> **Status:** ✅ Done
> **Est. time:** 45 min
> **Depends on:** —

## Goal

Python script fetches all user's actors from the Apify API and writes `actors.json`.

## Requirements

- [x] Read `APIFY_TOKEN` and `APIFY_USERNAME` from environment variables
- [x] Declare `requests` as a project dependency in `pyproject.toml`
- [x] Use `Bearer` auth header (NOT Basic Auth — Apify doesn't support it)
- [x] Handle pagination: loop through `offset` values until all items fetched
- [x] Handle rate limiting: retry with exponential backoff on 429 responses
- [x] Handle authentication errors (clear error message if token missing/invalid)
- [x] Unwrap Apify API's `data` key from all responses
- [x] Map Apify categories to human-readable labels (16 categories)
- [x] Fetch detail endpoint for enriching missing fields (description, isPublic, categories, pictureUrl, SEO fields, review/bookmark counts)
- [x] Output JSON format with `actors` array and `generatedAt` timestamp
- [x] Clean title slugs for URLs (collapse whitespace/hyphens)

### Output Schema

```json
{
  "actors": [
    {
      "id": "abc123",
      "title": "Actor Name",
      "description": "Short description",
      "category": "Real Estate",
      "isPublic": true,
      "iconUrl": "https://...",
      "link": "https://apify.com/username/actor-name",
      "stats": { "totalRuns": 150, "totalUsers": 42, "totalUsers30Days": 12 },
      "createdAt": "2025-01-15T10:00:00.000Z",
      "modifiedAt": "2026-09-01T14:30:00.000Z"
    }
  ],
  "generatedAt": "2026-10-27T12:00:00.000Z"
}
```

## Deliverable

`fetch-actors.py` produces valid `actors.json`. Test with a sample token.

## Important Notes

- **Auth:** Use `Bearer <token>` header or `?token=` query param. Basic Auth returns 401.
- **Response wrapper:** All Apify API responses have `{"data": {...}}`. `fetch_json()` unwraps automatically.
- **Detail endpoint:** `GET /v2/actors/{id}` returns 25+ additional fields. Script enriches actors with missing data (best-effort, skips failures).
- **Rate limits:** 60 req/sec per resource. Script retries with exponential backoff.

## How to Run

```bash
# With .env file:
uv run --env-file .env python fetch-actors.py

# Or with exported env vars:
APIFY_TOKEN=apify_api_xxx APIFY_USERNAME=serj_henrique uv run python fetch-actors.py
```
