# Week 2 — Competencies 2 & 7

**C2 — Code literacy and documentation** · **C7 — Critical evaluation and professional judgment**

---

## What I did (Week 2)

1. **Data + script**: Added `demo_responses.csv` and `demo_word_count.py` (which reads that CSV) and **ran** the script.
2. **Dashboard pipeline**: Built `demo_dashboard.html` and used `build_dashboard.py` to connect the CSV data into the dashboard.
3. **Version control**: **Committed** the work and **pushed** to GitHub.

---

## For someone who does not read code

This section explains **what the Week 2 scripts do** and **how to run them**, without assuming you read Python.

All paths below use the folder `**week 2/`** (there is a space in the name—quotes matter in Terminal).

### `demo_word_count.py` — table of word counts

- **Purpose**: Reads survey-style rows from `**demo_responses.csv`** and prints a **text table** in the Terminal. For each person it shows ID, role, **how many words** are in their written response, and a **short preview** of the response (only the first **60 characters**, so long answers do not flood the screen).
- **Inputs**: `week 2/demo_responses.csv` (must sit in the **same folder** as the script).
- **Output**: Printed text in the Terminal (no files are overwritten).

**How to run it**

```bash
cd "week 2"
python3 demo_word_count.py
```

**What “success” looks like**: You see a header row, a line of dashes, then one line per participant, and at the end a small **Summary** block (total responses, shortest/longest/average word counts).

---

### `build_dashboard.py` — bake CSV data into the HTML dashboard

- **Purpose**: Takes the **same** `demo_responses.csv`, adds a **word count** per row, converts the rows to **JSON** (a structured text format browsers understand), and **inserts** that JSON into `**demo_dashboard.html`** inside a special `<script id="embedded-data">` block. After this runs, the dashboard page can **read** the data without a separate server fetching the CSV.
- **Inputs**: `week 2/demo_responses.csv` and `week 2/demo_dashboard.html`.
- **Output**: **Updates** `demo_dashboard.html` in place (the file on disk changes). The script prints one confirmation line naming the HTML path and how many rows it embedded.

**How to run it**

```bash
cd "week 2"
python3 build_dashboard.py
```

**What “success” looks like**: Terminal shows something like `Updated .../demo_dashboard.html with N rows from .../demo_responses.csv`. Then open `**demo_dashboard.html`** in a browser (double-click or File → Open) to view the dashboard with **fresh** data.

---

## Competency 2 evidence in this repo (checklist)

Use this block to show **reading + explaining + documenting** in one place.


| Rubric item                                                       | Where to look                                                   |
| ----------------------------------------------------------------- | --------------------------------------------------------------- |
| **Inline comments** (prefer *why*, not only *what*)               | `week 2/demo_word_count.py`, `week 2/build_dashboard.py`        |
| **Docstring** (what it takes, returns, does)                      | `count_words()` in `week 2/demo_word_count.py`                  |
| **Commit messages** (*what changed* and *why*, not only “update”) | Paste real messages below; in Terminal: `git log --oneline -10` |
| **Markdown for a non-technical reader**                           | This file — section **“For someone who does not read code”**    |


### Commit messages I used this week *(paste from `git log`)*

1. Enhance word count script to include median word count calculation for week 2 demo responses
2. Update `README.md` to include project context and instructions for running the code
3. *Added week2 md for reference along w cursorrules*

---

## Competency 7 — Critical evaluation and professional judgment

**What it means:** I do not treat AI output as automatically correct. I decide **what to trust**, **what to verify**, and I can say **what I checked** and **why**—not only “the tool said so.”

### Evidence (Week 2)

- **A specific example of something the tool got wrong, and what I did about it**  
When I made a commit, **Cursor suggested a commit message** that felt **generic**—it did **not** describe the **actual edits** I was committing (like a vague or random placeholder instead of the real changes). I **did not use that text as-is**. I **rewrote the message** so it matched the **relevant changes** I had made (which files, and what kind of update: scripts, README, `week2.md`, etc.).
- **Something I would not show a client (or stakeholder) without checking**  
I would not ship **AI-generated commit messages** (or other AI copy about “what we changed”) without comparing them to **what actually changed** in the diff. The log is part of professional communication; it has to be **accurate**.
- **A decision to override, correct, or supplement AI output**  
I **overrode** Cursor’s suggested message and **replaced it with my own** summary tied to the **real work** in that commit. Same principle as with code: **verify first**, then stand behind what you publish.

### Strong claim (one sentence)

*“Cursor generated a generic commit message that didn’t match my staged changes; I rewrote it so the message described the actual updates, because the commit log has to be trustworthy for graders and collaborators.”*

---

## What “code literacy” meant for me this week

- **Loading the CSV**: I could see that the code is set up to read a CSV and that it **points at** `demo_responses.csv`, then **loads** that file.
- **The first loop**: In the `for` loop over the CSV reader, I understood that **each row** from the file gets **appended** to the list of responses.
- **The word-count section**: In the loop over responses, I could follow that the script **walks through each response** to compute counts. I also followed the **preview** logic: when a response is **longer than 60 characters**, the display uses the **first 60 characters** (and adds truncation) so the table does not print the whole text.

---

## What “documentation” meant for me this week

- **Git / commits**: I first tried to commit **without a message** just to test. In **Cursor**, I could not get the work **fully pushed** until I added a **commit message**—so the tool **forced** that step. After that I used **short commit messages that matched what changed** in the code.
- **In-code comments**: I added **comments in the scripts** so the file is easier to **read and follow** later.
- **Repo-level context**: I added `**.cursorrules`** (and related project context) so **instructors, TAs, or classmates** opening the repo have **orientation**—not only raw files.
- **This file (`week2.md`)**: I am writing **week 2 notes** here to spell out **what work was done** and how it connects to **Competency 2**.

---

## Observations

- **Documentation is not only paragraphs in a report**—it also shows up as **commit messages** and **repo context** so others can follow *what changed* and *why*.
- **Tools can enforce literacy habits**: Cursor **blocked the push** until there was a **commit comment**, which made “name your change” part of the workflow, not optional.

---

## So what? (for future weeks)

- Treat **every commit message** as a **one-line label** for my future self and for graders: **what file or behavior moved**, in plain language.
- Keep **short week notes** (like this file) when a competency asks for **reflection**, not only **working code**.
- If I use Cursor or another GUI for Git, notice **what it requires** (messages, review steps)—those are clues to what **good documentation** looks like in practice.

---

