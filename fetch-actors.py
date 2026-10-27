#!/usr/bin/env python3
"""Fetch actor data from the Apify API and write actors.json.

Usage:
    APIFY_TOKEN=<token> APIFY_USERNAME=<username> python fetch-actors.py

Environment variables:
    APIFY_TOKEN      — Apify API token (required)
    APIFY_USERNAME   — Apify username (required, used for link URLs)
"""

import json
import os
import re
import time
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://api.apify.com/v2"
LIST_URL = f"{BASE_URL}/actors"
ITEM_URL = f"{BASE_URL}/actors/{{actor_id}}"
OUTPUT_FILE = "actors.json"

APIFY_USERNAME = os.environ.get("APIFY_USERNAME")
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")

if not APIFY_USERNAME:
    raise SystemExit(
        "ERROR: APIFY_USERNAME environment variable is required.\n"
                "Export it and re-run, or add it to a .env file."
            )
if not APIFY_TOKEN:
    raise SystemExit(
        "ERROR: APIFY_TOKEN environment variable is required.\n"
        "Get one at https://console.apify.com/account/api-tokens"
    )

HEADERS = {
    "X-Limit-Rows": "1000",
    "Authorization": f"Bearer {APIFY_TOKEN}",
}


# ---------------------------------------------------------------------------
# Category mapping
# ---------------------------------------------------------------------------

CATEGORY_LABELS = {
    "DEVELOPER_TOOLS": "Developer Tools",
    "OPEN_SOURCE": "Open Source",
    "SCIENCE_AND_EDUCATION": "Science & Education",
    "E_COMMERCE": "E-Commerce",
    "MARKETING": "Marketing",
    "SOCIAL_MEDIA": "Social Media",
    "FINANCE": "Finance",
    "HEALTH_AND_SPORTS": "Health & Sports",
    "TRAVEL": "Travel",
    "REAL_ESTATE": "Real Estate",
    "SHOPPING": "Shopping",
    "GOVERNMENT": "Government",
    "JUDICIAL": "Judicial",
    "NEWS_AND_MEDIA": "News & Media",
    "HUMAN_RESOURCES": "HR & Recruitment",
    "OTHER": "Other",
}


def map_category(raw: str) -> str:
    """Convert an Apify category slug to a human-readable label."""
    return CATEGORY_LABELS.get(raw, raw)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def fetch_json(url: str, params: dict | None = None) -> dict:
    """GET a JSON endpoint with retry + exponential backoff on 429.

    Automatically unwraps the Apify API's `data` key (e.g. {"data": {...}} → {...}).
    Appends the APIFY_TOKEN as a query parameter for authentication.
    """
    max_retries = 5
    delay = 1.0

    if params is None:
        params = {}
    params["token"] = APIFY_TOKEN

    for attempt in range(max_retries + 1):
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)

        if resp.status_code == 200:
            resp.raise_for_status()
            body = resp.json()
            return body.get("data", body)

        if resp.status_code == 401:
            raise SystemExit(
                "ERROR: Apify API returned 401 (Unauthorized).\n"
                "Check your APIFY_TOKEN — it may be invalid or expired."
            )

        if resp.status_code == 429:
            if attempt < max_retries:
                wait = delay * (2 ** attempt)
                print(f"  ⏳ Rate limited — waiting {wait:.1f}s before retry (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue
            raise SystemExit(
                f"ERROR: Rate limited by Apify API after {max_retries} retries."
            )

        resp.raise_for_status()
        # Unreachable — but keeps type-checker happy
        return {}  # pragma: no cover

    raise SystemExit("ERROR: Unexpected response from Apify API.")


def fetch_actor_detail(actor_id: str) -> dict | None:
    """Fetch a single actor's full details from the detail endpoint.

    The response is already unwrapped (data key removed) by fetch_json.
    Works without auth for public actors; requires auth for private actors.
    """
    try:
        data = fetch_json(ITEM_URL.format(actor_id=actor_id))
        return data
    except SystemExit:
        return None


# ---------------------------------------------------------------------------
# Data pipeline
# ---------------------------------------------------------------------------

def fetch_all_actors() -> list[dict]:
    """Paginate through all actors belonging to the authenticated user."""
    actors: list[dict] = []
    offset = 0
    page_size = 1000  # matches X-Limit-Rows header

    print("Fetching actors from Apify API …")

    while True:
        print(f"  Requesting offset={offset} …")
        page = fetch_json(LIST_URL, params={
            "my": "1",
            "limit": str(page_size),
            "offset": str(offset),
            "desc": "1",
        })

        items = page.get("items", [])
        if not items:
            break

        actors.extend(items)
        offset += len(items)

        if len(items) < page_size:
            break  # no more pages

        print(f"  Got {len(items)} items (total: {len(actors)})")

    return actors


def enrich_actor_details(actors: list[dict]) -> list[dict]:
    """Fetch full details from the detail endpoint for each actor.

    Best-effort — skips any actor that fails to keep the pipeline moving.
    Enriches description, isPublic, categories, pictureUrl, SEO fields,
    and enriches stats with review/bookmark counts from the detail response.
    """
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
                detail_stats = detail_data.get("stats", {})
                if "stats" not in actor:
                    actor["stats"] = {}
                actor["stats"].setdefault("actorReviewCount", detail_stats.get("actorReviewCount", 0))
                actor["stats"].setdefault("actorReviewRating", detail_stats.get("actorReviewRating", 0))
                actor["stats"].setdefault("bookmarkCount", detail_stats.get("bookmarkCount", 0))
        except Exception:
            pass  # non-critical — proceed


def transform_actors(raw: list[dict]) -> list[dict]:
    """Map raw API records to the output schema."""
    output: list[dict] = []

    for item in raw:
        categories = item.get("categories", [])
        primary_category = map_category(categories[0]) if categories else None

        title_slug = re.sub(r"[\s-]+", "-", item.get("title", "untitled")).lower().strip("-")

        actor = {
            "id": item["id"],
            "title": item.get("title") or item.get("name") or "Untitled Actor",
            "description": item.get("description", "")[:300],
            "category": primary_category,
            "isPublic": item.get("isPublic", True),
            "iconUrl": item.get("pictureUrl") or item.get("defaultWebhookAddress", ""),
            "link": f"https://apify.com/{APIFY_USERNAME}/{title_slug}",
            "stats": _extract_stats(item),
            "createdAt": item.get("createdAt", ""),
            "modifiedAt": item.get("modifiedAt", ""),
        }
        output.append(actor)

    return output


def _extract_stats(item: dict) -> dict:
    """Pull stats into a flat dict, handling Apify's nested stat objects."""
    stats_raw = item.get("stats", {})
    return {
        "totalRuns": stats_raw.get("totalRuns", 0),
        "totalUsers": stats_raw.get("totalUsers", 0),
        "totalUsers30Days": stats_raw.get("totalUsers30Days", 0),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    raw = fetch_all_actors()
    if not raw:
        print("⚠️  No actors found. Check APIFY_TOKEN / APIFY_USERNAME.")
        raw = []

    print(f"  Found {len(raw)} actor(s).")

    # Enrich with full actor details (best-effort)
    print("Enriching with actor details (best-effort) …")
    enrich_actor_details(raw)

    # Transform to output schema
    actors = transform_actors(raw)

    payload = {
        "actors": actors,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
    }

    # Write to disk
    Path(OUTPUT_FILE).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"✅ Wrote {len(actors)} actors to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
