# Week 6 — Billboard Hot 100 Analysis

Dataset: weekly Billboard Hot 100 charts, 2023-01-07 to 2026-05-02 — 17,400 rows across 174 chart weeks, 2,181 unique songs, 506 unique primary artists. Source notebook: [week 6/week6_mp1_starter.ipynb](week%206/week6_mp1_starter.ipynb).

## Charts built this week

- [chart1_songs_top10.png](chart1_songs_top10.png) — horizontal bar chart, "Billboard Hot 100: Top 10 Most Charted Songs (2023–2026)". Answers Q1: which songs/artists had the strongest chart presence by Top 10 and #1 weeks.
- [chart2_song_trajectories.png](chart2_song_trajectories.png) — multi-line chart, "Three Ways a Song Can Win (2023–2026)". Answers Q2: do songs climb slowly, debut high, or spike and drop?
- [chart3_chart_behavior.png](chart3_chart_behavior.png) — 3-panel line chart, "Has Chart Behavior Changed? (2023–2026)". Answers Q3: are new entries, average longevity, or rank volatility shifting over time?

## Chart justifications

### Chart 1 — `chart1_songs_top10.png` (horizontal bar)

I chose a horizontal bar chart because the main goal was to compare ranked songs clearly, and the song + artist labels are long. A vertical bar chart would have crowded the labels or forced them to rotate, which makes the chart harder to read. With the horizontal layout each song title has enough space, and the ranking from most to least charted reads naturally top to bottom. It also lets me layer two metrics on the same row — weeks in the Top 10 (longer bar) and weeks at #1 (shorter bar overlaid) — so the viewer instantly sees which songs stayed popular for a long time and which ones actually reached the very top. A table could show the same numbers but would not make the gap as visible; a scatter or treemap would lose the clean ranking. A practitioner (label, A&R, music-supervision client) would use this to identify the few songs delivering the bulk of long-tail attention — the ones worth licensing or building campaigns around.

### Chart 2 — `chart2_song_trajectories.png` (line chart, three representative songs)

A line chart is the right shape because trajectory is fundamentally rank-over-time, and lines make the climb-peak-drop shape literally visible. After my professor flagged that classifying trajectories across the full dataset would be hard to implement, I filtered to the top 20 most-charted songs (ranked by total `chart_score`) and classified within that set. Each line is one representative song per category — Debut High, Spike & Drop, Slow Climber — chosen so the three shapes read cleanly against each other. A practitioner would use this to recognize which trajectory pattern a current single is following early, and decide whether to keep promoting (Slow Climber) or move resources elsewhere (Spike & Drop).

### Chart 3 — `chart3_chart_behavior.png` (3-panel line chart, monthly with rolling average)

Three panels stacked vertically share an x-axis (time), which is the right shape for comparing three different "is this changing?" metrics across the same window without overloading one axis. Each panel includes a rolling-average overlay so the underlying trend is visible through the week-to-week noise. The honest finding is that **no single metric trends cleanly in one direction**. New entries per month are cyclical/spiky rather than steadily rising, average weeks on chart dips in the middle then rises later but still fluctuates a lot, and rank volatility is noisy but mostly stable with occasional spikes. A practitioner glancing at this should walk away knowing the Hot 100 in 2023–2026 is shaped by bursts, seasonality, and short-term events more than by one smooth structural change — which is itself a useful, non-overclaimed finding.

## Analytical findings

- **Lose Control by Teddy Swims charted for 112 weeks**, the longest run in the dataset and ~26% longer than the #2 song (Beautiful Things — Benson Boone, 89 weeks). It still only spent 1 week at #1, so longevity and chart dominance are clearly different metrics.
- **A Bar Song (Tipsy) by Shaboozey spent 19 weeks at #1** — the most weeks at #1 of any song in 2023–2026 — despite ranking 4th by total weeks on chart (77). It is the clearest dominance story in the dataset.
- Of the 17,400 weekly rows, **only 2,044 (~12%) were new entries**, while 7,882 were songs moving down, 5,493 moving up, 1,237 holding, and **744 re-entries** — re-entries outnumber several types of in-chart movement, which is why songs leaving and coming back (e.g. All I Want For Christmas Is You returning at #3 by `weeks_on_board`) materially shapes longevity stats.
- **Lose Control was classified as Spike & Drop, not Slow Climber**, because its peak fell within the first half of its 112-week run (`peak_position < 0.60`). Culturally it feels like a slow burn, but the algorithm calls it the way the math reads — an honest limitation of fixed thresholds when total chart life varies from ~5 weeks to over 100.
- **Pink Pony Club by Chappell Roan** landed in Slow Climber, which matches the cultural narrative — it genuinely took months to build before exploding in summer 2024 — so at least one of the three categories is producing labels that align with how listeners actually experienced the song.

## Competency claims

### C5 — Data Analysis with Pandas (primary)

This week's analysis is built almost entirely on pandas operations: `groupby(['song', 'primary_artist']).agg(top10_weeks=('is_top_10', 'sum'), number1_weeks=('is_number_one', 'sum'), peak_rank=('rank', 'min'))` to produce the Chart 1 ranking; `groupby('song_key').cumcount() + 1` to build `week_number` for each song's chart life sorted by `chart_date`; `chart_score = 101 - rank` so higher = better and weekly performance can be summed or averaged; and `df_top20.groupby('song_key').apply(_trajectory_for)` where `_trajectory_for` uses `idxmax()` on `chart_score` to find the peak week and computes `peak_position = peak_week / total_weeks` for classification. Chart 3 adds monthly aggregation plus a `rolling(...)` mean to surface the trend through noise. Findings tied back: A Bar Song (Tipsy)'s 19 weeks at #1 fell out of the `('is_number_one', 'sum')` aggregation, and the Spike & Drop label on Lose Control fell out of the `idxmax()` step — both numbers I can trace back to a specific pandas call.

### C6 — Data Visualization (primary)

I matched chart type to data structure deliberately. Chart 1 ([chart1_songs_top10.png](chart1_songs_top10.png)) is a **horizontal bar** because the categorical axis (song + artist labels) is long and ranked, and because I needed to layer two related metrics (`top10_weeks` and `number1_weeks`) on the same row to make the "long run" vs "peak dominance" gap visible at a glance. Chart 2 ([chart2_song_trajectories.png](chart2_song_trajectories.png)) is a **multi-series line** because trajectory is rank-over-time and the climb-peak-drop shape only reads in a line — one line per representative song, one color per algorithmic category. Chart 3 ([chart3_chart_behavior.png](chart3_chart_behavior.png)) is a **3-panel stacked line chart** with rolling-average overlays so three different "change over time" questions share an x-axis without competing on a single y. All three PNGs are committed at the repo root for the grader.

### C2 — Code Literacy and Documentation (secondary)

The notebook is organized into clearly labeled sections (Section 1 setup, Section 2 cleaning, Section 3 analysis with one Q&A pair per question), and every chart cell starts with a `# --- BUILD DATA ---` / `# --- BUILD FIGURE ---` block so the data-shaping step is visually separate from the plotting step. The Q2 trajectory cell carries an explicit input contract in comments (`# Inputs (already present in df_top20): song_key, chart_date, rank, week_number, chart_score, ...`) and notes the threshold rule (`<= 0.25 -> Debut High`, `>= 0.60 -> Slow Climber`, else `Spike & Drop`) so a reader can rerun or re-threshold without re-reading the function body.

### C3 — Data Cleaning and File Handling (secondary)

The most interesting data-quality issue was **artist string inconsistency**: collaborations appear as `&`, `Featuring`, `X`, and `,` with no standardization, so the same kind of credit looked different to a `groupby`. I handled it by deriving a `primary_artist` column that takes the first credited artist before any of those collaboration markers, and then building `song_key = song + " — " + primary_artist` to dedupe across small variations. This is an explicit trade-off, not a clean fix: a true duet like "Lady Gaga & Bruno Mars" reduces to Lady Gaga, which can under-credit the collaborator. For chart-behavior analysis I prioritized consistent grouping over perfectly representing every collaboration, and I called it out in the cleaning notes so the limitation travels with the data.

## Extra credit — Plotly Exercises

Built a **bird strikes calendar heatmap** in [week 6/plotly-exercises.ipynb](week%206/plotly-exercises.ipynb) using `px.imshow` on a pivot table of incident counts. The y-axis is `Visibility` (DAY / NIGHT / DAWN / DUSK) used as a proxy for time of day since the dataset doesn't carry an explicit hour-of-day field, and the x-axis is calendar month (Jan–Dec). Color encodes the total number of reported strikes in that month/visibility bucket, with cell annotations on for exact counts.

`px.imshow` is a new chart type beyond what Exercises 1–3 covered (bar, scatter, line, choropleth) — it renders a 2D matrix as color and is the right pick when you want to show how a value varies across two categorical axes simultaneously. The heatmap shows that strikes concentrate heavily in the **DAY** band and peak in **late summer / early fall months** (visible months 7–10), while DAWN and DUSK bands are an order of magnitude smaller — a useful "where to focus mitigation" signal that a pair of bar charts would have hidden across two views. Reference: <https://plotly.com/python/heatmaps/>.
