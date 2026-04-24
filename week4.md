# Week 4 — Competencies 2 & 4

**C2 — Code literacy and documentation** · **C4 — APIs and data acquisition**

---

## What I did (Week 4)

1. **Picked an API myself**: I chose **TMDB** (The Movie Database), created an account, and generated an API key. TMDB has a well-documented REST API and returns JSON, so it was a clean fit for this week.
2. **Secured the API key**: Added the key to `week 4/.env` as `TMDB_API_KEY=...`, wrote a small `.env` loader, and made sure the script reads the key through `os.environ.get("TMDB_API_KEY")`—never hardcoded. I also added `**/.env` to `.gitignore` so the key cannot be committed by accident.
3. **Built `tmdb_movies.py`**: A script that fetches structured movie data from TMDB, prints a comparison block for each movie, ends with a short insight (highest rated vs. most popular), and saves the results to `tmdb_movies.csv`.
4. **Three lookup modes in one script**: The script can (a) search specific titles, (b) list the most popular 2025 releases, or (c) list 2025 movies tagged as video-game adaptations. I switch between them by changing one constant at the top.
5. **Documentation**: Inline comments explain *why* choices were made (not only *what* a line does), the functions have docstrings, and this markdown file explains the script for a non-technical reader.

---

## For someone who does not read code

This section explains **what the Week 4 script does** and **how to run it**, without assuming you read Python.

All paths below use the folder `**week 4/`** (there is a space in the name—quotes matter in Terminal).

### `tmdb_movies.py` — fetch and compare movies from TMDB

- **Purpose**: Talks to **TMDB** (a public movie database with an API) and pulls back a small set of movies. For each one it prints the **title**, **release date**, **vote average** (the community’s 0–10 score), **popularity** (TMDB’s own activity/buzz score), and a short **overview** (the plot summary). At the bottom it prints a quick insight: which movie is **highest rated**, which is **most popular**, and whether popularity and rating agree. It also saves the same information to `**tmdb_movies.csv`** so the results can be opened in a spreadsheet.
- **Inputs**: `week 4/.env` (must contain a line like `TMDB_API_KEY=your_key_here`). No other input files are needed—the script fetches live data over the internet.
- **Output**: Text printed in the Terminal, plus `**week 4/tmdb_movies.csv`** (overwritten each time you run the script).

**How to run it**

```bash
cd "week 4"
python3 tmdb_movies.py
```

**What "success" looks like**: The Terminal shows a block for each movie with Title / Released / Vote avg / Popularity / Overview, then a short `=== Insights ===` section, then a line like `Saved 5 rows to .../tmdb_movies.csv`.

### Which movies does it compare?

The script has one knob near the top called `LOOKUP_MODE`. The default is the "most popular 2025" mode; the other two are there as toggles so the same script can answer different questions:

| `LOOKUP_MODE` | What it compares |
| --- | --- |
| `"discover_popular_2025"` *(default)* | The top 5 most popular movies **released in 2025** (any genre). |
| `"search"` | Three specific video-game adaptations I wanted to compare: *The Super Mario Bros. Movie*, *Sonic the Hedgehog*, and *Uncharted*. |
| `"discover_game_2025"` | Top 5 of 2025 that TMDB tags with the **"video game"** keyword (id 282). |

Changing one string at the top and re-running the script switches modes—no other edits needed.

---

## Competency 2 — Code literacy and documentation

### Evidence in this repo (checklist)

| Rubric item | Where to look |
| --- | --- |
| **Inline comments** (*why*, not only *what*) | `week 4/tmdb_movies.py` — e.g. the block that explains why the key goes in `.env`, why the script uses two endpoints (`/search/movie` then `/movie/{id}` vs. `/discover/movie`), and what each extracted field means |
| **Docstrings** (what inputs mean, what the function does, what it returns) | `load_env_file()`, `tmdb_get_json()`, `search_tmdb_movie()`, `discover_tmdb_movies()`, `get_tmdb_movie()`, `extract_fields()` in `week 4/tmdb_movies.py` |
| **Commit messages** (*what changed* and *why*) | in Terminal: `git log --oneline -10` |
| **Markdown for a non-technical reader** | This file — section **"For someone who does not read code"** |

### Commit messages I used this week *(paste from `git log` after committing)*

1. Update .gitignore to exclude environment files
2. 

### How I demonstrated C2

I demonstrated code literacy and documentation by reading TMDB's API reference, figuring out which endpoints actually answered the question I wanted to ask, and then writing the script so someone else could follow the logic. The inline comments focus on the *why*: why the key lives in `.env`, why `/discover/movie` does not need a second `/movie/{id}` call, why the insight line differentiates **popularity** from **vote_average**. Each function has a docstring that names the inputs, the URL shape it builds, and what it returns or prints on failure. I also wrote this markdown file in plain language so a non-technical reader can run the script and understand the result without reading Python.

### What "code literacy" meant for me this week

- I traced the request/response path: **build URL → open HTTP request → parse JSON → pick fields → print + write CSV**, and I could point to the line where each step happens.
- I connected TMDB's response shape to my output columns. The `results` list from `/discover/movie` already contains `title`, `release_date`, `vote_average`, `popularity`, and `overview`, so I skipped an extra network call—that decision lives in a comment so it is not invisible.
- I kept **error handling in one helper** (`tmdb_get_json`) so HTTP errors, timeouts, bad JSON, and TMDB's "success: false" responses all produce a readable message instead of a crash.

### What "documentation" meant for me this week

- **In-code**: Comments explain *why* (secret in `.env`, which endpoint is doing what, why popularity ≠ quality). Docstrings explain *inputs → behavior → outputs*.
- **For humans**: This `week4.md` file plus a run command that does not require reading Python.
- **For reproducibility**: `tmdb_movies.csv` captures the fetched rows in a stable format so results can be re-opened in a spreadsheet or compared across runs.

---

## Competency 4 — APIs and data acquisition

### Evidence in this repo (checklist)

| Rubric item | Where to look |
| --- | --- |
| **Python script that makes an HTTP request and parses JSON** | `tmdb_get_json()` in `week 4/tmdb_movies.py` |
| **API I found myself (not a class demo)** | TMDB — I made the account, generated the key, and read TMDB's docs to pick endpoints |
| **API key kept out of version control** | `week 4/.env` (loaded by `load_env_file()`), plus `**/.env` in `.gitignore` |
| **Short explanation of endpoints and what I did with the response** | The "How the TMDB API is used" section below, and inline comments on the three endpoint helpers |

### How I demonstrated C4

I chose **TMDB** because it is free for non-commercial use, requires a personal API key (so it is a realistic example of secret handling), and has well-documented JSON endpoints. I read TMDB's reference to understand what each endpoint returns, picked the smallest set that answered my question, and wrote helper functions for each one. The API key is loaded from `week 4/.env` through a tiny stdlib loader and read through `os.environ.get("TMDB_API_KEY")`—it never appears in the source file. `week 4/.env` is ignored by Git via `**/.env` in `.gitignore`, and I verified it does not appear in `git status` before committing. If the key is missing the script prints a friendly message and exits instead of sending an invalid request.

### How the TMDB API is used (in plain language)

The script talks to three endpoints depending on the mode:

- **`GET /3/search/movie?query=<title>&year=<YYYY>`** — Given a title (and an optional release year), TMDB returns a JSON object with a `results` list of short movie summaries. I pick the best match using simple conditions (exact title + exact year first, then exact title, then TMDB's top-ranked result).
- **`GET /3/discover/movie?primary_release_year=...&sort_by=popularity.desc&...`** — Ranked list endpoint. I hand it filters (release year, sort order, optional `with_keywords`) and it returns movies already sorted the way I asked. The `results` items already include every field I need, so I skip the per-movie detail call here.
- **`GET /3/movie/{movie_id}`** — Full record for a single movie, used only after a search resolves to an id. Returns the same five fields (`title`, `release_date`, `vote_average`, `popularity`, `overview`) plus extras I do not use.

**What the response looks like** (trimmed):

```json
{
  "results": [
    {
      "id": 83533,
      "title": "Avatar: Fire and Ash",
      "release_date": "2025-12-17",
      "vote_average": 7.4,
      "popularity": 246.31,
      "overview": "..."
    }
  ]
}
```

**What I chose to do with it**: I extract five fields per movie, print them as a readable block, compute two simple insights (highest `vote_average` and highest `popularity`), and write everything to `tmdb_movies.csv` so the results are reusable outside the Terminal.

---

## HCD reflection & C7 critical evaluation of AI output

This week the script went through **several rounds of AI suggestions that I had to verify and sometimes reject**. Four concrete moments stood out:

- **Wrong TMDB keyword id.** The AI initially set `with_keywords=9717` in the "video-game adaptation" preset. When I ran the script the results were *Superman* and *Fantastic 4*—clearly not video-game adaptations. I did not accept the output at face value. I hit TMDB's `/search/keyword?query=video+game` endpoint myself and found that the correct keyword id is **282**, not 9717, and fixed the preset. Lesson: when an AI writes a magic number, I should check it against the source of truth before trusting the filter.
- **Wrong TMDB movie id for Sonic.** In an earlier version the AI used `335977` for *Sonic the Hedgehog*. When I read the printed output, that id resolved to *Indiana Jones and the Dial of Destiny*. Again I refused to treat the AI's choice as correct—I looked up the real Sonic id (**454626**) through TMDB's search endpoint and updated the list. Lesson: a script that runs without errors is not the same as a script that is *right*; reading the output matters.
- **API key handling.** At one point the AI produced a one-off Terminal command that read the API key straight out of `.env` to test a URL. That was fine as a throwaway diagnostic, but it is not how the script itself should work. I made sure the script always goes through `load_env_file(...)` and `os.environ.get("TMDB_API_KEY")`, and I added `**/.env` to `.gitignore` so the real key never lands in a commit. Lesson: convenience shortcuts in an agent session are not the same standard as the code I am handing in.
- **Popularity vs. vote_average.** Once the data came back, I had to decide what "the best movie" even means. `popularity` is TMDB's internal buzz score (driven by recent views, searches, ratings activity); `vote_average` is the community rating out of 10. They do not always agree. In the 2025 discover run, *Avatar: Fire and Ash* won on popularity (246.31) while *Demon Slayer: Infinity Castle* had the higher `vote_average` (7.7/10). I documented the difference in the insight line rather than pretending one metric tells the whole story.

### Strong claim (one sentence)

*"I did not treat the AI's first answer as correct: I caught a wrong TMDB keyword id (9717 → 282) and a wrong movie id (335977 → 454626) by reading the actual API output, I kept the API key out of the script by loading it from `week 4/.env` through `os.environ.get`, and I documented the popularity-vs-rating distinction instead of collapsing them into one 'winner'."*

---

## Observations

- **An API response is not a result.** `/discover/movie` returned JSON the first time I asked, but the results were wrong because the *keyword id* was wrong. "It didn't error" is not the same as "it's right."
- **Secrets belong in one place.** Putting the TMDB key in `week 4/.env` plus a matching `.gitignore` entry is boring and repetitive—but it is the single step that keeps a personal key out of a public GitHub repo.
- **Two metrics, two stories.** Popularity and rating disagreed on the 2025 list, and that disagreement is the interesting finding. A script that only prints one of them would have hidden it.

---

## So what? (for future weeks)

- When the AI (or I) uses a **magic number** (an id, a keyword code, a status constant), treat it like a citation that needs checking before it ships.
- Keep **"how the key is loaded"** as explicit in the script as any other step, because future-me will copy this pattern to the next API and the next student assignment.
- When an API returns multiple "ranking" metrics, **show them both** and write one honest sentence about when they disagree.

---
