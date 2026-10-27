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
}
AUTH = (APIFY_USERNAME, APIFY_TOKEN)


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
    """GET a JSON endpoint with retry + exponential backoff on 429."""
    max_retries = 5
    delay = 1.0

    for attempt in range(max_retries + 1):
        resp = requests.get(url, headers=HEADERS, params=params, auth=AUTH, timeout=30)

        if resp.status_code == 200:
            resp.raise_for_status()
            return resp.json()

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
    """Fetch a single actor's details (may include pictureUrl)."""
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

        items = page if isinstance(page, list) else page.get("items", [])
        if not items:
            break

        actors.extend(items)
        offset += len(items)

        if len(items) < page_size:
            break  # no more pages

        print(f"  Got {len(items)} items (total: {len(actors)})")

    return actors


def enrich_with_picture(actors: list[dict]) -> list[dict]:
    """Try to fetch pictureUrl for actors that lack one.

    Best-effort — we skip any actor_id that fails to keep the pipeline moving.
    """
    for actor in actors:
        if actor.get("pictureUrl"):
            continue
        try:
            detail = fetch_actor_detail(actor["id"])
            if detail and detail.get("pictureUrl"):
                actor["pictureUrl"] = detail["pictureUrl"]
        except Exception:
            pass  # non-critical — proceed


def transform_actors(raw: list[dict]) -> list[dict]:
    """Map raw API records to the output schema."""
    output: list[dict] = []

    for item in raw:
        categories = item.get("categories", [])
        primary_category = map_category(categories[0]) if categories else None

        title_slug = item.get("title", "untitled").lower().replace(" ", "-")

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

    # Enrich with pictureUrl (best-effort)
    print("Enriching with picture URLs (best-effort) …")
    enrich_with_picture(raw)

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
