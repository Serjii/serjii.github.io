# Debug Report: `fetch-actors.py` Execution Failure

> **Date:** 2026-10-27  
> **Script:** `/home/serjii.github.io/fetch-actors.py`  
> **Repo:** `serjii.github.io`  
> **Status:** 2 bugs + 1 latent issue found. Auth research completed.

---

## TL;DR

| # | Issue | Status | Fix effort |
|---|-------|--------|------------|
| 1 | `.env` not loaded | ✅ Fixed by `uv run --env-file .env` | Already solved |
| 2 | Basic Auth rejected by Apify | ❌ Bug | ~3 min |
| 3 | Response `data` wrapper not unwrapped | ❌ Bug | ~2 min |
| 4 | Detail endpoint enriches only `pictureUrl` | 🟡 Suboptimal | ~5 min |
| 5 | Title slug has messy hyphens | 🟡 Cosmetic | ~2 min |

**Total remaining fix time: ~12 minutes**

---

## Issue 1 — `.env` file not loaded automatically *(User-corrected)*

**Severity:** 🟢 Not a bug (local dev)  
**Status:** ✅ Resolved by using `uv run --env-file .env python fetch-actors.py`

**Clarification:** Python's standard library doesn't auto-load `.env` files, but `uv run --env-file .env` injects the variables into the environment automatically. The script uses `os.environ.get()` which picks them up correctly when invoked this way.

**For CI (T03):** The GitHub Actions workflow will inject secrets as env vars directly — no `.env` file or `--env-file` flag needed. The script will work as-is.

**Conclusion:** No code changes needed for this issue.

---

## Issue 2 — Authentication method is wrong (Basic Auth → Bearer)

**Severity:** 🔴 Critical  
**Status:** ❌ Bug — blocks all API calls  

**Error message:**

```
ERROR: Apify API returned 401 (Unauthorized).
Check your APIFY_TOKEN — it may be invalid or expired.
```

**Root cause:** The script sends credentials via HTTP Basic Auth:

```python
AUTH = (APIFY_USERNAME, APIFY_TOKEN)
requests.get(url, headers=HEADERS, params=params, auth=AUTH)
```

Apify **does not support HTTP Basic Auth**. It returns `401` and silently discards the token.

**However**, the token is valid — it works with the recommended auth methods:

| Method | Example | Works? |
|--------|---------|--------|
| `Authorization: Bearer <token>` | Recommended | ✅ |
| `?token=<token>` | Query param | ✅ |
| `Authorization: Basic <base64>` | ❌ Not supported | ❌ |

**Why we still need auth:** The `my=1` filter (list all user's actors) requires authentication. Without it, the API can't determine who "my" is. The detail endpoint (`/v2/actors/{id}`) works unauthenticated for public actors, but we can't even get the list of actor IDs without auth.

**Research source:** See `apify-api-research.md` section 2 — both auth methods are explicitly documented in the Apify OpenAPI schema.

**Recommended fix:**

```python
# Remove this:
# AUTH = (APIFY_USERNAME, APIFY_TOKEN)

# In fetch_json, add the token as a query parameter:
if params is None:
    params = {}
params["token"] = APIFY_TOKEN

# Remove auth=AUTH from requests.get()
resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
```

---

## Issue 3 — Response doesn't unwrap `data` wrapper

**Severity:** 🔴 Critical  
**Status:** ❌ Bug — would produce zero results even after fixing Issue 2

**Current code:**

```python
page = fetch_json(LIST_URL, params={...})
items = page if isinstance(page, list) else page.get("items", [])
```

**Root cause:** The Apify API wraps every response in a `data` key:

```json
{
  "data": {
    "total": 13,
    "count": 2,
    "items": [...]
  }
}
```

`page.get("items", [])` returns `[]` because `"items"` is nested inside `data`.

**Live test:**

```bash
$ curl -s "https://api.apify.com/v2/actors?my=1&limit=2&token=apify_api_..."
{"data":{"total":13,"count":2,"items":[...]}}
```

**Recommended fix:**

```python
def fetch_json(url: str, params: dict | None = None) -> dict:
    # ... existing code ...
    resp.raise_for_status()
    return resp.json()["data"]   # unwrap the "data" key
```

Then simplify `fetch_all_actors`:

```python
page = fetch_json(LIST_URL, params={...})
items = page.get("items", [])
if not items:
    break
```

---

## Issue 4 — Enrich only copies `pictureUrl` (missing key fields)

**Severity:** 🟠 High  
**Status:** 🟡 Suboptimal — functional but incomplete

**Current behavior:** The `enrich_with_picture` function fetches the detail endpoint and only copies `pictureUrl`. But the detail endpoint returns **25+ additional fields** that are missing from the list endpoint.

**What the list endpoint returns per actor:**

| Field | Available? |
|-------|------------|
| `id` | ✅ |
| `createdAt`, `modifiedAt` | ✅ |
| `name`, `username`, `title` | ✅ |
| `stats` | ✅ |
| `description` | ❌ |
| `isPublic` | ❌ |
| `pictureUrl` | ❌ |
| `categories` | ❌ |

**What the detail endpoint returns additionally:**

| Field | Available? |
|-------|------------|
| `description` | ✅ |
| `isPublic` | ✅ |
| `pictureUrl` | ✅ |
| `categories` | ✅ |
| `seoTitle`, `seoDescription` | ✅ |
| `readmeSummary` | ✅ (AI-generated) |
| `versions` | ✅ (full history) |
| `pricingInfos` | ✅ |
| `defaultRunOptions` | ✅ |
| `exampleRunInput` | ✅ |
| `notice` | ✅ |
| `actorReviewCount`, `actorReviewRating` | ✅ |
| `bookmarkCount` | ✅ |

**Recommended fix:**

```python
def enrich_actor_details(actors: list[dict]) -> list[dict]:
    """Fetch full details from the detail endpoint."""
    for actor in actors:
        if all(actor.get(k) for k in ("pictureUrl", "description", "isPublic", "categories")):
            continue
        try:
            detail = fetch_actor_detail(actor["id"])
            if detail:
                detail_data = detail.get("data", detail)  # detail endpoint also wraps in "data"
                actor.setdefault("description", detail_data.get("description", ""))
                actor.setdefault("isPublic", detail_data.get("isPublic", True))
                actor.setdefault("categories", detail_data.get("categories", []))
                actor.setdefault("pictureUrl", detail_data.get("pictureUrl", ""))
                actor.setdefault("seoTitle", detail_data.get("seoTitle"))
                actor.setdefault("seoDescription", detail_data.get("seoDescription"))
                # Enrich stats with review/bookmark counts
                if "stats" not in actor:
                    actor["stats"] = {}
                actor["stats"].setdefault("actorReviewCount", detail_data.get("stats", {}).get("actorReviewCount", 0))
                actor["stats"].setdefault("actorReviewRating", detail_data.get("stats", {}).get("actorReviewRating", 0))
                actor["stats"].setdefault("bookmarkCount", detail_data.get("stats", {}).get("bookmarkCount", 0))
        except Exception:
            pass
```

Also unwrap the detail endpoint response the same way (it returns `{"data": {...}}`).

---

## Issue 5 — Title slug produces messy URLs

**Severity:** 🟡 Low  
**Status:** 🟡 Cosmetic — not a crash, but produces ugly URLs

**Current code:**

```python
title_slug = item.get("title", "untitled").lower().replace(" ", "-")
```

**Problem:** Apify titles contain `---` separators (e.g. `"B3 - Boletim Diário - Derivativos"`), which become `b3---boletim---diario---derivativos` after `.replace(" ", "-")`.

**Recommended fix:**

```python
import re
title_slug = re.sub(r"[\s-]+", "-", item.get("title", "untitled")).lower().strip("-")
# Produces: "b3-boletim-diario-derivativos"
```

---

## Authentication Research Summary

**Source:** `apify-api-research.md` (full details in that file)

### Key findings:

1. **List endpoint (`/v2/actors?my=1`) always requires authentication** — no way around it.
2. **Two valid auth methods:**
   - `Authorization: Bearer <token>` (recommended)
   - `?token=<token>` (query param, less secure but works)
3. **Basic Auth is not supported** — Apify returns `401 "Authentication token was not provided"`.
4. **Rate limits:** 250,000 req/min global, 60 req/sec per resource.
5. **Detail endpoint:** Returns 25+ additional fields vs list endpoint (categories, description, isPublic, pictureUrl, seoTitle, seoDescription, readmeSummary, versions, pricingInfos, etc.).

---

## Fix Priority

| # | Issue | Effort | Impact |
|---|-------|--------|--------|
| 1 | `.env` loading | ✅ Already handled by `uv run --env-file` | N/A |
| 2 | Basic Auth → Bearer/token | 3 min | Must fix to reach API |
| 3 | Response `data` unwrap | 2 min | Must fix to get any data |
| 4 | Enrich all detail fields | 5 min | Better data quality |
| 5 | Slug cleanup | 2 min | Cleaner URLs |

**Total remaining fix time: ~12 minutes**
