#!/usr/bin/env python3
"""Compare movies using the TMDB API across three lookup modes.

The script loads `TMDB_API_KEY` from a local `.env` file next to this script
(format: `TMDB_API_KEY=your_key_here`) and never hardcodes the secret.

Lookup modes (set LOOKUP_MODE below):
  "search"                — look up three specific titles (video-game adaptations).
  "discover_popular_2025" — most popular movies RELEASED in 2025 (any genre).
  "discover_game_2025"    — most popular 2025 movies tagged as video-game
                            adaptations (TMDB keyword 9717 = "video game").

Run from anywhere:
  python3 "week 4/tmdb_game_movies.py"
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# TMDB's v3 REST base. We use three endpoints in this script:
#   GET /3/search/movie?query=...&year=...   — find a movie by title/attributes
#   GET /3/discover/movie?<filters>          — list movies matching filters
#   GET /3/movie/{movie_id}                  — full record for one movie
TMDB_API_BASE = "https://api.themoviedb.org/3"

# --- Mode selector ------------------------------------------------------------
# Change this string to switch what the script looks up. Valid options:
#   "search", "discover_popular_2025", "discover_game_2025"
LOOKUP_MODE = "discover_popular_2025"

# How many movies to compare when using a discover preset.
DISCOVER_LIMIT = 5

# --- discover filters -------------------------------------------
# Each preset is a dict of TMDB /discover/movie query params. Useful knobs:
#   primary_release_year  — only movies whose primary release year matches
#   sort_by               — e.g. "popularity.desc", "vote_average.desc"
#   with_keywords         — comma-separated TMDB keyword IDs (282 = "video game")
#   vote_count.gte        — ignore niche films with too few votes
DISCOVER_PRESETS: dict[str, dict] = {
    "discover_popular_2025": {
        # Most popular movies released in 2025, regardless of genre.
        "primary_release_year": 2025,
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "language": "en-US",
    },
    "discover_game_2025": {
        # Most popular 2025 movies tagged as video-game adaptations.
        "primary_release_year": 2025,
        "sort_by": "popularity.desc",
        "with_keywords": 282,
        "include_adult": "false",
        "language": "en-US",
    },
}

# --- Shared runtime knobs -----------------------------------------------------
# Network timeout in seconds — TMDB is usually fast, but we cap it so a hung
# connection can't freeze the script forever.
REQUEST_TIMEOUT = 30

# How many characters of the `overview` to show before truncating with "…".
OVERVIEW_PREVIEW_CHARS = 220

# Columns written to the output CSV. The filename itself is derived from the
# active LOOKUP_MODE so different runs don't overwrite each other.
CSV_FIELDS = ["movie_id", "title", "release_date", "vote_average", "popularity", "overview"]


def load_env_file(env_path: str) -> None:
    """Read a simple `.env` file and copy KEY=VALUE pairs into os.environ.

    We do this with the standard library instead of python-dotenv to keep the
    project dependency-free. Lines that are blank or start with `#` are
    ignored; surrounding single or double quotes around the value are stripped
    so entries like `TMDB_API_KEY='abc123'` work as expected.
    """
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
    """Shared HTTP helper: GET a TMDB URL and return parsed JSON (or None).

    Handles every failure mode we care about — bad HTTP status, network
    problems, timeouts, and malformed JSON — and prints a clear message that
    includes `context` (so the caller knows which request the error belongs to).
    """
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        # HTTP-level failure (e.g. 401 bad key, 404 unknown movie, 429 rate-limited).
        print(f"  [error] TMDB returned HTTP {exc.code} for {context}: {exc.reason}")
        return None
    except urllib.error.URLError as exc:
        # Lower-level network failure (DNS, connection refused, TLS, etc.).
        print(f"  [error] Could not reach TMDB for {context}: {exc.reason}")
        return None
    except TimeoutError:
        print(f"  [error] TMDB request timed out for {context}.")
        return None
    except json.JSONDecodeError:
        print(f"  [error] TMDB response for {context} was not valid JSON.")
        return None

    # TMDB sometimes returns 200 OK with {"success": false, ...} on auth issues.
    if isinstance(payload, dict) and payload.get("success") is False:
        print(f"  [error] TMDB: {payload.get('status_message', 'request failed')}")
        return None
    return payload if isinstance(payload, dict) else None


def search_tmdb_movie(query: str, api_key: str, year: int | None = None) -> dict | None:
    """Find a movie by title (and optional release year) using TMDB search.

    URL shape:
      https://api.themoviedb.org/3/search/movie?api_key=<key>&query=<title>&year=<YYYY>
    TMDB returns {"results": [...]} with short movie summaries. We pick the
    best match using the conditions below.
    """
    params: dict[str, str] = {"api_key": api_key, "query": query, "include_adult": "false"}
    if year is not None:
        # Narrow to a specific release year so sequels/remakes with the same
        # title don't win the match.
        params["year"] = str(year)
    url = f"{TMDB_API_BASE}/search/movie?{urllib.parse.urlencode(params)}"

    payload = tmdb_get_json(url, context=f'search "{query}"')
    if payload is None:
        return None
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        print(f"  [not found] No TMDB match for '{query}'" + (f" ({year})" if year else ""))
        return None

    # Selection conditions in order of confidence:
    # 1) exact title + exact year match; 2) exact title; 3) top-ranked result.
    q_lower = query.strip().lower()

    def release_year(item: dict) -> str:
        return (item.get("release_date") or "")[:4]

    for item in results:
        if isinstance(item, dict) and item.get("title", "").strip().lower() == q_lower:
            if year is None or release_year(item) == str(year):
                return item
    for item in results:
        if isinstance(item, dict) and item.get("title", "").strip().lower() == q_lower:
            return item
    return results[0] if isinstance(results[0], dict) else None


def discover_tmdb_movies(filters: dict, api_key: str, limit: int) -> list[dict]:
    """List movies matching the given /discover/movie filters.

    URL shape:
      https://api.themoviedb.org/5/discover/movie?api_key=<key>&<filters>
    Unlike /search, /discover is designed for ranked lists: give it filters and
    a sort order and it returns a paginated list already sorted how you asked.
    The response shape is the same — {"results": [...]} — with each item
    already containing id, title, release_date, vote_average, popularity, and
    overview, so we don't need a second /movie/{id} call for these rows.
    """
    params = {"api_key": api_key, **{k: str(v) for k, v in filters.items()}}
    url = f"{TMDB_API_BASE}/discover/movie?{urllib.parse.urlencode(params)}"

    payload = tmdb_get_json(url, context="discover movies")
    if payload is None:
        return []
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        print("  [not found] /discover returned no movies for the given filters.")
        return []
    return [item for item in results[:limit] if isinstance(item, dict)]


def get_tmdb_movie(movie_id: int, api_key: str) -> dict | None:
    """Fetch one movie's full JSON record from TMDB, or None if unavailable.

    URL shape:
      https://api.themoviedb.org/5/movie/<id>?api_key=<key>
    Used only by "search" mode, because /search results omit some fields; in
    discover mode the list already has what we need.
    """
    query_string = urllib.parse.urlencode({"api_key": api_key})
    url = f"{TMDB_API_BASE}/movie/{movie_id}?{query_string}"
    return tmdb_get_json(url, context=f"movie id {movie_id}")


def extract_fields(movie: dict) -> dict:
    """Pull the five comparison fields from a raw TMDB movie record.
    - title: display title shown to readers.
    - release_date: YYYY-MM-DD of first theatrical release (useful context).
    - vote_average: mean user rating from 0-10; reflects perceived quality.
    - popularity: TMDB's internal score based on recent views/activity;
      high popularity doesn't necessarily mean high quality.
    - overview: short plot summary, handy for quick context.
    """
    return {
        "title": movie.get("title", "Unknown title"),
        "release_date": movie.get("release_date", "Unknown"),
        "vote_average": movie.get("vote_average"),
        "popularity": movie.get("popularity"),
        "overview": movie.get("overview", ""),
    }

def print_movie(fields: dict) -> None:
    """Print one movie's fields in a clean, readable block."""
    overview = fields["overview"] or "(no overview provided)"
    if len(overview) > OVERVIEW_PREVIEW_CHARS:
        overview = overview[:OVERVIEW_PREVIEW_CHARS].rstrip() + "…"

    vote = fields["vote_average"]
    pop = fields["popularity"]
    vote_str = f"{vote:.1f}/10" if isinstance(vote, (int, float)) else "n/a"
    pop_str = f"{pop:.2f}" if isinstance(pop, (int, float)) else "n/a"

    print(f"Title:        {fields['title']}")
    print(f"Released:     {fields['release_date']}")
    print(f"Vote avg:     {vote_str}")
    print(f"Popularity:   {pop_str}")
    print(f"Overview:     {overview}")


def print_insights(results: list[dict]) -> None:
    """Compare collected movies and print a short popularity-vs-rating note."""
    rated = [r for r in results if isinstance(r.get("vote_average"), (int, float))]
    popular = [r for r in results if isinstance(r.get("popularity"), (int, float))]
    if not rated or not popular:
        print("Not enough data to compute insights.")
        return

    top_rated = max(rated, key=lambda r: r["vote_average"])
    top_popular = max(popular, key=lambda r: r["popularity"])

    print(f"Highest rated:    {top_rated['title']} ({top_rated['vote_average']:.1f}/10)")
    print(f"Most popular:     {top_popular['title']} (score {top_popular['popularity']:.2f})")

    if top_rated["title"] == top_popular["title"]:
        print(
            "Insight: popularity and rating agree — the same film leads on both "
            "buzz and audience score."
        )
    else:
        print(
            "Insight: popularity and rating diverge — TMDB popularity reflects "
            "recent activity and buzz, while vote_average reflects user-submitted "
            "quality scores, so the most-talked-about film isn't always the "
            "best-rated one."
        )


def collect_via_search(api_key: str) -> list[dict]:
    """Resolve each SEARCHES entry to a movie id, then fetch its full record."""
    results: list[dict] = []
    for entry in SEARCHES:
        query = entry["query"]
        year = entry.get("year")
        label = f"{query} ({year})" if year else query
        print(f"--- Searching TMDB for: {label} ---")

        match = search_tmdb_movie(query, api_key, year=year)
        if match is None:
            print()
            continue
        movie_id = match.get("id")
        if not isinstance(movie_id, int):
            print(f"  [error] Search result for {label} had no usable id.")
            print()
            continue
        print(f"  matched: {match.get('title')} ({(match.get('release_date') or '?')[:4]}) — id {movie_id}")

        movie = get_tmdb_movie(movie_id, api_key)
        if movie is None:
            print()
            continue
        fields = extract_fields(movie)
        fields["movie_id"] = movie_id
        print_movie(fields)
        print()
        results.append(fields)
    return results


def collect_via_discover(preset_name: str, api_key: str) -> list[dict]:
    """Run a /discover preset and turn each returned item into a result row."""
    filters = DISCOVER_PRESETS[preset_name]
    print(f"--- /discover preset: {preset_name} ---")
    print(f"  filters: {filters}")
    movies = discover_tmdb_movies(filters, api_key, DISCOVER_LIMIT)
    if not movies:
        return []

    results: list[dict] = []
    for movie in movies:
        fields = extract_fields(movie)
        # /discover already returns id on each item, so no second call needed.
        fields["movie_id"] = movie.get("id")
        print()
        print_movie(fields)
        results.append(fields)
    print()
    return results


def write_csv(out_path: str, rows: list[dict]) -> None:
    """Save the comparison rows to a CSV alongside the script."""
    with open(out_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
    print(f"Saved {len(rows)} rows to {out_path}")


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load KEY=VALUE pairs from `week 4/.env` into os.environ, then read the
    # key through os.environ.get so the secret never appears in source code.
    load_env_file(os.path.join(script_dir, ".env"))
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        print(
            "Missing TMDB_API_KEY. Add a line like `TMDB_API_KEY=your_key_here` "
            "to week 4/.env and try again."
        )
        sys.exit(1)

    # Dispatch on the configured mode. Each branch returns a list of dict rows
    # with the same shape, so downstream printing/CSV code stays identical.
    # All modes write to a single CSV so "the results of this run" always
    # land in tmdb_movies.csv regardless of which mode is active.
    output_name = "tmdb_movies.csv"

    if LOOKUP_MODE == "search":
        print(f"Comparing {len(SEARCHES)} video-game adaptation movies from TMDB\n")
        results = collect_via_search(api_key)
    elif LOOKUP_MODE in DISCOVER_PRESETS:
        print(f"Comparing top {DISCOVER_LIMIT} movies via preset '{LOOKUP_MODE}'\n")
        results = collect_via_discover(LOOKUP_MODE, api_key)
    else:
        print(
            f"Unknown LOOKUP_MODE {LOOKUP_MODE!r}. "
            f"Use one of: 'search', {list(DISCOVER_PRESETS)}."
        )
        sys.exit(1)

    if not results:
        print("No movies could be loaded from TMDB; nothing to compare.")
        sys.exit(1)

    print("=== Insights ===")
    print_insights(results)

    out_path = os.path.join(script_dir, output_name)
    print()
    write_csv(out_path, results)


if __name__ == "__main__":
    main()
