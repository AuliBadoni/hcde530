#!/usr/bin/env python3
"""Compare movies using the TMDB API across three lookup modes.

The script loads `TMDB_API_KEY` from a local `.env` file next to this script
(format: `TMDB_API_KEY=your_key_here`) and never hardcodes the secret.

Lookup modes (set LOOKUP_MODE below):
  "search"                — look up three specific titles (video-game adaptations).
  "discover_popular_2025" — most popular movies RELEASED in 2025 (any genre).
  "discover_game_2025"    — most popular 2025 movies tagged as video-game
                            adaptations (TMDB keyword 282 = "video game").

Run from anywhere:
  python3 "week 4/tmdb_movies.py"
"""

from __future__ import annotations

# Standard-library imports only — no third-party packages required.
# csv: write the results table. json: turn TMDB's response text into a Python
# dict. os: read environment variables and build file paths. sys: exit cleanly
# when the key is missing. urllib.*: make the HTTP request that talks to TMDB.
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

# --- Mode 1: search by title/year --------------------------------------------
# Used when LOOKUP_MODE == "search". Each entry tells the script what to look
# up:
#   query: the title string we send to TMDB's /search/movie endpoint.
#   year:  the primary release year used to disambiguate sequels/remakes
#          (e.g. there are multiple "Sonic the Hedgehog" movies on TMDB).
SEARCHES: list[dict] = [
    {"query": "The Super Mario Bros. Movie", "year": 2023},
    {"query": "Sonic the Hedgehog", "year": 2020},
    {"query": "Uncharted", "year": 2022},
]

# --- Modes 2 & 3: discover filters -------------------------------------------
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

# Columns written to the output CSV.
CSV_FIELDS = ["movie_id", "title", "release_date", "vote_average", "popularity", "overview"]


def load_env_file(env_path: str) -> None:
    """Read a simple `.env` file and copy KEY=VALUE pairs into os.environ.

    We do this with the standard library instead of python-dotenv to keep the
    project dependency-free. Lines that are blank or start with `#` are
    ignored; surrounding single or double quotes around the value are stripped
    so entries like `TMDB_API_KEY='abc123'` work as expected.
    """
    # open the .env file sitting next to the script, look at
    # each line, and for every `NAME=value` line copy that pair into the
    # program's environment variables. After this runs, the rest of the code
    # can ask for "TMDB_API_KEY" via os.environ.get without the key ever being
    # typed into the source file.
    if not os.path.isfile(env_path):
        # No .env file? Silently do nothing — maybe the user already set the
        # key as a real shell environment variable instead.
        return
    with open(env_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            # Skip blank lines, comments (`# ...`), and anything that doesn't
            # look like a KEY=VALUE pair.
            if not line or line.startswith("#") or "=" not in line:
                continue
            # Split on the FIRST `=` only, in case the value itself contains `=`.
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # If the value is wrapped in matching quotes (single or double),
            # peel them off — users often write `KEY='abc'` out of habit.
            if (len(value) >= 2) and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            # Only set the variable if it's not already in the environment, so
            # a real shell variable always wins over a stale .env entry.
            if key and key not in os.environ:
                os.environ[key] = value


def tmdb_get_json(url: str, context: str) -> dict | None:
    """Shared HTTP helper: GET a TMDB URL and return parsed JSON (or None).

    Handles every failure mode we care about — bad HTTP status, network
    problems, timeouts, and malformed JSON — and prints a clear message that
    includes `context` (so the caller knows which request the error belongs to).
    """
    # this is the "phone call" layer. Every function that
    # talks to TMDB funnels through here. It takes a fully-built URL (which
    # already contains the api_key query parameter), fetches it, turns the
    # JSON text into a Python dict, and returns that dict — or prints a
    # friendly error and returns None if anything went wrong.

    # Build the request object. The Accept header tells TMDB we want JSON
    # back (it already defaults to JSON, but being explicit is good hygiene).
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        # Open the connection, wait up to REQUEST_TIMEOUT seconds for a reply,
        # then parse the response body as JSON (TMDB always returns JSON).
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        # HTTP-level failure — the server answered but with an error code.
        # Common examples: 401 (bad/missing api_key), 404 (unknown movie id),
        # 429 (rate-limited, too many requests).
        print(f"  [error] TMDB returned HTTP {exc.code} for {context}: {exc.reason}")
        return None
    except urllib.error.URLError as exc:
        # Lower-level network failure — we never reached the server. Usually a
        # DNS problem, connection refused, TLS handshake issue, or no internet.
        print(f"  [error] Could not reach TMDB for {context}: {exc.reason}")
        return None
    except TimeoutError:
        # The request took longer than REQUEST_TIMEOUT seconds; skip it.
        print(f"  [error] TMDB request timed out for {context}.")
        return None
    except json.JSONDecodeError:
        # We got a reply, but it wasn't valid JSON (rare, usually a proxy
        # returning an HTML error page).
        print(f"  [error] TMDB response for {context} was not valid JSON.")
        return None

    # Even on HTTP 200, TMDB sometimes flags a soft failure in the body:
    # {"success": false, "status_message": "..."}. Treat that as "not found".
    if isinstance(payload, dict) and payload.get("success") is False:
        print(f"  [error] TMDB: {payload.get('status_message', 'request failed')}")
        return None
    # All good — hand the parsed dict back to the caller.
    return payload if isinstance(payload, dict) else None


def search_tmdb_movie(query: str, api_key: str, year: int | None = None) -> dict | None:
    """Find a movie by title (and optional release year) using TMDB search.

    URL shape:
      https://api.themoviedb.org/3/search/movie?api_key=<key>&query=<title>&year=<YYYY>
    TMDB returns {"results": [...]} with short movie summaries. We pick the
    best match using the conditions below.
    """
    # this is how we look up a movie by its NAME. We bundle
    # the title (and optional year) into the URL together with the api_key,
    # ask TMDB "what movies match this?", and then pick the best of the
    # matches. The api_key is passed in from main() — it was read from .env.

    # Build the query-string parameters as a normal Python dict. Every request
    # to TMDB's v3 API needs `api_key=<your key>`; that's how TMDB identifies
    # who is calling. `include_adult=false` hides adult content.
    params: dict[str, str] = {"api_key": api_key, "query": query, "include_adult": "false"}
    if year is not None:
        # Narrow to a specific release year so sequels/remakes with the same
        # title don't win the match.
        params["year"] = str(year)
    # urlencode turns the dict into a safe URL tail like
    # "api_key=...&query=Super+Mario&year=2023" (spaces → + etc.).
    url = f"{TMDB_API_BASE}/search/movie?{urllib.parse.urlencode(params)}"

    # Hand the finished URL to the shared helper, which does the HTTP call.
    payload = tmdb_get_json(url, context=f'search "{query}"')
    if payload is None:
        return None
    # TMDB returns a list of candidate movies under the "results" key.
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        print(f"  [not found] No TMDB match for '{query}'" + (f" ({year})" if year else ""))
        return None

    # Selection conditions in order of confidence:
    # 1) exact title + exact year match;
    # 2) exact title match, any year;
    # 3) fall back to TMDB's top-ranked result (results are ordered by popularity).
    q_lower = query.strip().lower()

    def release_year(item: dict) -> str:
        # TMDB release_date is "YYYY-MM-DD"; the first four chars are the year.
        return (item.get("release_date") or "")[:4]

    # Pass 1: exact title + exact year (most trustworthy match).
    for item in results:
        if isinstance(item, dict) and item.get("title", "").strip().lower() == q_lower:
            if year is None or release_year(item) == str(year):
                return item
    # Pass 2: exact title, any year (still confident, just a year mismatch).
    for item in results:
        if isinstance(item, dict) and item.get("title", "").strip().lower() == q_lower:
            return item
    # Pass 3: give up on exact match, take whatever TMDB thinks is #1.
    return results[0] if isinstance(results[0], dict) else None


def discover_tmdb_movies(filters: dict, api_key: str, limit: int) -> list[dict]:
    """List movies matching the given /discover/movie filters.

    URL shape:
      https://api.themoviedb.org/3/discover/movie?api_key=<key>&<filters>
    Unlike /search, /discover is designed for ranked lists: give it filters and
    a sort order and it returns a paginated list already sorted how you asked.
    The response shape is the same — {"results": [...]} — with each item
    already containing id, title, release_date, vote_average, popularity, and
    overview, so we don't need a second /movie/{id} call for these rows.
    """
    # this is how we get a LIST of movies that match a set
    # of rules (e.g. "released in 2025, sorted by popularity"). The api_key is
    # merged in with the caller's filter rules, then the finished URL goes to
    # the shared HTTP helper.

    # Merge the api_key with the caller's filter dict. Every value is turned
    # into a string because urlencode expects strings only.
    params = {"api_key": api_key, **{k: str(v) for k, v in filters.items()}}
    url = f"{TMDB_API_BASE}/discover/movie?{urllib.parse.urlencode(params)}"

    payload = tmdb_get_json(url, context="discover movies")
    if payload is None:
        return []
    results = payload.get("results")
    if not isinstance(results, list) or not results:
        print("  [not found] /discover returned no movies for the given filters.")
        return []
    # Keep only the first `limit` items so we don't compare 20 movies at once.
    return [item for item in results[:limit] if isinstance(item, dict)]


def get_tmdb_movie(movie_id: int, api_key: str) -> dict | None:
    """Fetch one movie's full JSON record from TMDB, or None if unavailable.

    URL shape:
      https://api.themoviedb.org/3/movie/<id>?api_key=<key>
    Used only by "search" mode, because /search results omit some fields; in
    discover mode the list already has what we need.
    """
    # once we know a movie's numeric TMDB id (from search),
    # this function fetches the FULL record for that one movie. The api_key
    # goes in the URL query string, same as every other call.
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
    # TMDB responses include dozens of fields (budget,
    # genres, production companies, etc.). This function grabs only the five
    # we care about for the comparison and gives back a small, clean dict.
    # .get(..., default) is used so a missing field becomes a placeholder
    # instead of crashing the script.
    return {
        "title": movie.get("title", "Unknown title"),
        "release_date": movie.get("release_date", "Unknown"),
        "vote_average": movie.get("vote_average"),
        "popularity": movie.get("popularity"),
        "overview": movie.get("overview", ""),
    }


def print_movie(fields: dict) -> None:
    """Print one movie's fields in a clean, readable block."""
    # format one movie's fields into a nicely aligned block
    # for the Terminal. No API work happens here — this is presentation only.

    # Trim very long overviews so the terminal doesn't get flooded with text.
    overview = fields["overview"] or "(no overview provided)"
    if len(overview) > OVERVIEW_PREVIEW_CHARS:
        overview = overview[:OVERVIEW_PREVIEW_CHARS].rstrip() + "…"

    # Format the numeric fields defensively: if TMDB ever returns a missing
    # value, show "n/a" instead of crashing on the f-string format spec.
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
    # after we have fields for every movie, look across the
    # whole set and answer two questions — which movie is most popular, and
    # which is highest rated? Then say whether those two winners agree.

    # Only consider movies where the numeric fields actually came back as
    # numbers (defensive: ignores rare cases where TMDB omitted a field).
    rated = [r for r in results if isinstance(r.get("vote_average"), (int, float))]
    popular = [r for r in results if isinstance(r.get("popularity"), (int, float))]
    if not rated or not popular:
        print("Not enough data to compute insights.")
        return

    # max(list, key=...) picks the dict with the highest value for that key.
    top_rated = max(rated, key=lambda r: r["vote_average"])
    top_popular = max(popular, key=lambda r: r["popularity"])

    print(f"Highest rated:    {top_rated['title']} ({top_rated['vote_average']:.1f}/10)")
    print(f"Most popular:     {top_popular['title']} (score {top_popular['popularity']:.2f})")

    # If the same movie wins both metrics, popularity and quality agree.
    # Otherwise call out the split — popularity can reward buzz over quality.
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
    # this is the top-level "search mode" loop. For each
    # title in the SEARCHES list, we search TMDB by name/year, pick the best
    # match, fetch that movie's full record, extract our five comparison
    # fields, print them, and collect the result for the CSV.
    results: list[dict] = []
    for entry in SEARCHES:
        query = entry["query"]
        year = entry.get("year")
        label = f"{query} ({year})" if year else query
        print(f"--- Searching TMDB for: {label} ---")

        # Step 1: convert the title/year into a TMDB result summary.
        match = search_tmdb_movie(query, api_key, year=year)
        if match is None:
            # Error already printed inside search_tmdb_movie; skip to next.
            print()
            continue
        movie_id = match.get("id")
        if not isinstance(movie_id, int):
            print(f"  [error] Search result for {label} had no usable id.")
            print()
            continue
        print(f"  matched: {match.get('title')} ({(match.get('release_date') or '?')[:4]}) — id {movie_id}")

        # Step 2: use the numeric id to fetch the FULL movie record.
        movie = get_tmdb_movie(movie_id, api_key)
        if movie is None:
            print()
            continue
        # Step 3: reduce the big TMDB record to just the five fields we want.
        fields = extract_fields(movie)
        # Keep the resolved TMDB id alongside the extracted fields so each
        # CSV row can be traced back to the exact movie record we fetched.
        fields["movie_id"] = movie_id
        print_movie(fields)
        print()
        results.append(fields)
    return results


def collect_via_discover(preset_name: str, api_key: str) -> list[dict]:
    """Run a /discover preset and turn each returned item into a result row."""
    # this is the top-level "discover mode" loop. We look up
    # the chosen preset's filter dict, ask TMDB /discover/movie for a ranked
    # list of matching movies, and turn each one into a row just like search
    # mode does — except we don't need the extra /movie/{id} call because
    # /discover already returns every field we care about.
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
    # write the collected movie rows to a CSV file next to
    # the script. Opening the CSV in a spreadsheet is easier than re-reading
    # terminal output, and the file can be committed or shared.
    with open(out_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            # Build each CSV row from only the columns we declared, so no
            # extra keys leak into the file.
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})
    print(f"Saved {len(rows)} rows to {out_path}")


def main() -> None:
    # main() is the conductor. It (1) loads the API key
    # from .env, (2) picks the right lookup function based on LOOKUP_MODE,
    # (3) prints the insight block, and (4) writes the CSV.

    # Resolve the folder this script lives in, so .env and the CSV work no
    # matter which directory the user ran `python3` from.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Step 1: read `week 4/.env` into os.environ, then ask Python's
    # environment for TMDB_API_KEY. This is the only place the key enters
    # the program — it is never hardcoded in the source file.
    load_env_file(os.path.join(script_dir, ".env"))
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        # Missing key → don't even attempt a network call; tell the user how
        # to fix it and exit with a non-zero status so scripts can detect it.
        print(
            "Missing TMDB_API_KEY. Add a line like `TMDB_API_KEY=your_key_here` "
            "to week 4/.env and try again."
        )
        sys.exit(1)

    # All modes write to a single CSV so "the results of this run" always
    # land in tmdb_movies.csv regardless of which mode is active.
    output_name = "tmdb_movies.csv"

    # Step 2: dispatch on LOOKUP_MODE. Each branch returns a list of dict rows
    # with the same shape, so the printing/CSV code below stays identical.
    if LOOKUP_MODE == "search":
        print(f"Comparing {len(SEARCHES)} video-game adaptation movies from TMDB\n")
        results = collect_via_search(api_key)
    elif LOOKUP_MODE in DISCOVER_PRESETS:
        print(f"Comparing top {DISCOVER_LIMIT} movies via preset '{LOOKUP_MODE}'\n")
        results = collect_via_discover(LOOKUP_MODE, api_key)
    else:
        # Typo in LOOKUP_MODE? Fail loudly with a list of the valid options.
        print(
            f"Unknown LOOKUP_MODE {LOOKUP_MODE!r}. "
            f"Use one of: 'search', {list(DISCOVER_PRESETS)}."
        )
        sys.exit(1)

    if not results:
        # Every movie failed (bad key, no network, wrong filters) — nothing to
        # write or compare. Exit non-zero so the failure is visible.
        print("No movies could be loaded from TMDB; nothing to compare.")
        sys.exit(1)

    # Step 3: compare the collected movies and print the one-paragraph insight.
    print("=== Insights ===")
    print_insights(results)

    # Step 4: save the same rows to CSV for reuse outside the terminal.
    out_path = os.path.join(script_dir, output_name)
    print()
    write_csv(out_path, results)


if __name__ == "__main__":
    # Only run main() when the file is executed directly, not when it's
    # imported by another script (good Python habit).
    main()
