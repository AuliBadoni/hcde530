# Week 5 — Competencies 5 & 6

**C5 — Data analysis with pandas** · **C6 — Data visualization**

**Note on (1) vs. the miniproject:** Week 5 evidence in this repo uses `**tmdb_popular_2025.csv`**. I plan to use **a different dataset for the miniproject** — so this week’s notebook is **practice / course evidence**, not the same table I will ship as my MP analysis.

---

## Data pipeline: API → CSV → notebook

The `**tmdb_popular_2025.csv`** file is not arbitrary sample data: it comes from the **TMDB API workflow** (Week 4 — discover popular **2025** releases). The API returns a **ranked list** (this snapshot is **50 rows** — “top” popular 2025 titles as TMDB defines popularity). That response was **flattened and saved as CSV**; `**week 5/week5_exploration.ipynb`** **reads that file** with `**pd.read_csv("tmdb_popular_2025.csv")`** instead of calling the API inside the notebook. That separation keeps Week 5 focused on **pandas + plotting** on a **stable** table; Week 4 handled **HTTP + JSON + key hygiene**.

---

## What I did (Week 5)

1. **Notebook**: Built `**week 5/week5_exploration.ipynb`** — loads `**tmdb_popular_2025.csv**`, documents the table with `**head()**` and `**info()**`, and answers several concrete questions with pandas.
2. **Pandas operations** (C5): `**value_counts**` on derived `**release_month**`, **boolean filter** (`vote_count >= 500`) for a “reliable ratings” subset, `**groupby('release_month')[['vote_average','popularity']].mean()**`, and `**isnull().sum()**` for missingness. Inline `**#` comments** tie each step to a plain-English question and what the output means.
3. **Visualization** (C6): **Histogram** of `**popularity**` via `**movies["popularity"].plot.hist(...)**` and `**matplotlib.pyplot**` labels/title. I leaned on **matplotlib** deliberately for the movie `**popularity**` distribution — with **prior data science experience**, choosing a standard **distribution plot** for a continuous score was straightforward; the “tough” part here was less the chart grammar than **getting the plotting stack running** (see below).
4. **Interpretation**: Markdown sections and comments explain findings (e.g., subset size after filtering; monthly averages; **no** missing cells in this CSV).
5. **Environment**: Notebook expects the Jupyter **working directory** to be `**week 5/**` so the CSV path resolves; `**matplotlib**` is in `**requirements.txt**`.

---

## Kernel / environment debugging (what actually happened)

My notebook **was tied to a Python environment that was not the one I intended** — imports and plotting failed or behaved inconsistently because the **kernel** did not match my `**.venv**` (packages like `**matplotlib**` were installed in the project venv, but the IDE/kernel picker was pointed elsewhere). **Cursor alone did not resolve the mismatch** for me; I **debugged it myself**: checked which interpreter the notebook was using, switched the kernel to the **project `.venv**`, and confirmed `**matplotlib**` imports inside that environment. When I was stuck on prompts or wording, I used **Claude** opportunistically — but the **environment fix** was manual verification, not an AI guess I ran blindly.

**C7 :** I overrode a **wrong default** (the notebook’s kernel) after **verifying** which Python actually had my packages — I did not accept “it runs” or an AI’s guess until the **active interpreter** matched the evidence (`**import pandas/matplotlib**` in the right venv).

---

## For someone who does not read code

This section explains **what to open** and **how to run it**, without reading Python.

### `week5_exploration.ipynb` — explore TMDB popular 2025 films

- **Purpose**: Opens a **50-row** table of TMDB “popular” **2025** titles with `**vote_average**`, `**vote_count**`, `**popularity**`, `**release_date**`, and plot `**overview**` text. The notebook previews the data, plots how `**popularity**` is distributed, restricts to films with **at least 500 votes**, summarizes **average rating and popularity by release month**, and checks for **missing** values.
- **Inputs**: `**week 5/tmdb_popular_2025.csv**` *(originating from the TMDB API pipeline above)*. Run Jupyter with **working directory `week 5**` so the relative CSV path works. Select the kernel that matches your **project `.venv**` so `**pandas**` / `**matplotlib**` resolve.
- **Output**: Chart and tables **inside the notebook** (Cell outputs).

**How to run it**

1. Open the folder `**week 5**` in Cursor/VS Code (or `cd` there in Terminal).
2. Start Jupyter / select `**week 5/week5_exploration.ipynb**` and choose the kernel for `**hcde530**` / `**.venv**` *(not a stray system Python)*.
3. **Run All** from top to bottom so derived columns (e.g. `**release_month**`) exist before later cells.

**What “success” looks like**: Preview tables, a **histogram** of popularity, a line like **“34 of 50 movies kept”** after filtering, a **monthly** summary table, and **zero** missing counts per column for this file.

---

## Competency 5 — Data analysis with pandas

### Evidence in this repo (checklist)


| Rubric item                          | Where to look                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| **Loads a dataset**                  | `pd.read_csv("tmdb_popular_2025.csv")` in `**week 5/week5_exploration.ipynb**` |
| `**head()` / `info()**`              | Same notebook — load section                                                   |
| `**value_counts**`                   | `**release_month**` after parsing dates                                        |
| **Filter subset**                    | `**movies["vote_count"] >= 500**` → `well_voted`                               |
| `**groupby` + aggregate**            | `**groupby("release_month")[["vote_average","popularity"]].mean()**`           |
| **Missing data**                     | `**movies.isnull().sum()**`                                                    |
| **Interpretation (not only output)** | Markdown sections + `**#` comments** next to operations                        |


### How I demonstrated C5

I used pandas to ask **specific questions** of a real table: what the columns look like (`**head`/`info**`), which **release months** appear most often (`**value_counts**`), which rows have **trustworthy** rating averages (**filter by `vote_count**`), whether **average rating and popularity shift by month** (`**groupby**`), and whether any field is **incomplete** (`**isnull**`). The answers are **interpreted** in prose: e.g., filtering to ≥500 votes **narrows 50 rows to 34** — meaning **16** titles in this “popular” list still have **thin** vote totals, so their `**vote_average**` is **noisier**. Monthly means are **descriptive** (this is a **small convenience sample**, not a full calendar of every 2025 release).

### Strong claim (one sentence)

*"I loaded `**tmdb_popular_2025.csv**` *(from the TMDB popular-2025 API extract)*, counted films per `**release_month**`, filtered to `**vote_count >= 500**`, grouped by month for **mean `vote_average` and `popularity**`, and verified **no missing cells** — and I wrote **what each result implies** about noise vs. signal in the ratings."*

---

## Competency 6 — Data visualization

### Evidence in this repo (checklist)


| Rubric item                     | Where to look                                                                                                          |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Chart in Python**             | `**movies["popularity"].plot.hist(...)**` + `**matplotlib.pyplot**` axis/title in `**week 5/week5_exploration.ipynb**` |
| **Chart type matches question** | **Histogram** for a **continuous** score (`popularity`)                                                                |
| **Notebook + markdown**         | Same `**.ipynb**` — narrative cells explain steps and findings                                                         |
| **Publish on GitHub**           | Push the repo with the notebook committed; paste **repo or file URL** here: `***[add your GitHub link]**`*             |


### Why a histogram for `popularity`

`**popularity*`* is TMDB’s **continuous** activity score, not a small set of categories. A **histogram** shows **how many films fall into each popularity band** — whether attention is **spread out** or **skewed toward a few hits** — without collapsing rows into misleading bars per title. **Vertical bar charts** would be poor here (**50** distinct values / long labels); **line charts** need an ordered x-axis we did not define for “rank in list.” So **histogram + `describe()`** pair **shape** (plot) with **numeric spread** (table). Given **prior data science practice**, this was the natural chart–variable pairing; the harder piece was **environment setup**, not picking “what plot exists.”

### Strong claim (one sentence)

*"I plotted a **15-bin histogram** of `**popularity`** with labeled axes (**matplotlib**) because it fits a **continuous buzz score**; the notebook is `**week 5/week5_exploration.ipynb`** (and GitHub once pushed) with markdown tying the shape of the distribution back to how concentrated attention is in this **50-film** list."*

---

## Observations

- **Aggregation changes meaning**: **Monthly means** mix **unequal** numbers of films per month in this **n=50** slice — exploratory, not a definitive seasonal claim.
- `**vote_count` and `vote_average` pull apart**: A film can be **“popular”** in TMDB’s sense but still have **few** votes; the **filter** step makes that explicit.
- **Kernel matters more than the chart code**: If the notebook kernel isn’t your `**.venv`**, `**matplotlib**` may be missing even when the code is correct — I learned that by **checking the interpreter**, not by rewriting the histogram.

---

## So what? (for the MP and future weeks)

- **Week 5 ≠ MP dataset**: I’m keeping `**tmdb_popular_2025.csv`** as Week 5 evidence; the **miniproject** will use **another dataset** — same habits (**question → operation → interpretation**), different table.
- Reuse the **discipline**: every submitted analysis block gets a **sentence of meaning**, not only output.
- **Trust but verify tools**: AI assistants helped with **prompts**; **kernel selection** I verified locally because wrong-environment errors don’t fix themselves from better prose.

---

