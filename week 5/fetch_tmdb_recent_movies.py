#!/usr/bin/env python3
"""Fetch the 50 most popular 2025 movies from TMDB and save to CSV.

Uses TMDB v3 /discover/movie sorted by popularity.desc, restricted to
primary_release_year=2025. Walks pages 1-3 (20 results per page) and stops
at 50 rows. Standard library only.

Reads TMDB_API_KEY from `week 5/.env`; falls back to `week 4/.env` so the
existing key works without being duplicated.

Run from anywhere:
  python3 "week 5/fetch_tmdb_recent_movies.py"

Writes:
  tmdb_popular_2025.csv — 50 rows next to this script.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

TMDB_API_BASE = "https://api.themoviedb.org/3"
REQUEST_TIMEOUT = 30
TARGET_ROWS = 50
MAX_PAGES = 3  # TMDB returns 20 per page; 3 pages comfortably covers 50.
RELEASE_YEAR = 2025

CSV_FIELDS = [
    "movie_id",
    "title",
    "release_date",
    "vote_average",
    "vote_count",
    "popularity",
    "overview",
]
OUTPUT_NAME = "tmdb_popular_2025.csv"


def load_env_file(env_path: str) -> None:
    """Copy KEY=VALUE pairs from a simple .env file into os.environ."""
    if not os.path.isfile(env_path):
        return
    with open(env_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if (len(value) >= 2) and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value


def tmdb_get_json(url: str, context: str) -> dict | None:
    """GET a TMDB URL and return parsed JSON, or None on any failure."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        print(f"  [error] TMDB returned HTTP {exc.code} for {context}: {exc.reason}")
        return None
    except urllib.error.URLError as exc:
        print(f"  [error] Could not reach TMDB for {context}: {exc.reason}")
        return None
    except TimeoutError:
        print(f"  [error] TMDB request timed out for {context}.")
        return None
    except json.JSONDecodeError:
        print(f"  [error] TMDB response for {context} was not valid JSON.")
        return None

    if isinstance(payload, dict) and payload.get("success") is False:
        print(f"  [error] TMDB: {payload.get('status_message', 'request failed')}")
        return None
    return payload if isinstance(payload, dict) else None


def discover_popular_2025_page(api_key: str, page: int) -> list[dict]:
    """Fetch one /discover/movie page of 2025 releases sorted by popularity."""
    params = {
        "api_key": api_key,
        "sort_by": "popularity.desc",
        "primary_release_year": str(RELEASE_YEAR),
        "include_adult": "false",
        "language": "en-US",
        "page": str(page),
    }
    url = f"{TMDB_API_BASE}/discover/movie?{urllib.parse.urlencode(params)}"
    payload = tmdb_get_json(url, context=f"discover page {page}")
    if payload is None:
        return []
    results = payload.get("results")
    if not isinstance(results, list):
        return []
    return [item for item in results if isinstance(item, dict)]


def extract_fields(movie: dict) -> dict:
    """Reduce a TMDB movie record to the columns we write to CSV."""
    return {
        "movie_id": movie.get("id"),
        "title": movie.get("title", "Unknown title"),
        "release_date": movie.get("release_date", "Unknown"),
        "vote_average": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "popularity": movie.get("popularity"),
        "overview": movie.get("overview", ""),
    }


def write_csv(out_path: str, rows: list[dict]) -> None:
    """Save rows to CSV using the shared TMDB column order."""
    with open(out_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
    print(f"Saved {len(rows)} rows to {out_path}")


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Prefer a key in week 5/.env; fall back to week 4/.env so the existing
    # course key keeps working without being duplicated across folders.
    load_env_file(os.path.join(script_dir, ".env"))
    week4_env = os.path.normpath(os.path.join(script_dir, os.pardir, "week 4", ".env"))
    load_env_file(week4_env)

    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print(
            "Missing TMDB_API_KEY. Add a line like `TMDB_API_KEY=your_key_here` "
            "to week 5/.env (or week 4/.env) and try again."
        )
        sys.exit(1)

    print(f"Fetching the {TARGET_ROWS} most popular movies released in {RELEASE_YEAR}.\n")

    rows: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        print(f"--- discover page {page} ---")
        items = discover_popular_2025_page(api_key, page)
        if not items:
            print("  [warn] page returned no results; stopping early.")
            break
        for item in items:
            rows.append(extract_fields(item))
            if len(rows) >= TARGET_ROWS:
                break
        if len(rows) >= TARGET_ROWS:
            break

    if not rows:
        print("No movies returned from TMDB; nothing to save.")
        sys.exit(1)

    out_path = os.path.join(script_dir, OUTPUT_NAME)
    print()
    write_csv(out_path, rows)


if __name__ == "__main__":
    main()
