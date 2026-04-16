# Week 3 — Competencies 2 & 3

**C2 — Code literacy and documentation** · **C3 — Data cleaning and file handling**

---

## What I did (Week 3)

1. **Messy survey data**: Worked with `week3_survey_messy.csv` (inconsistent capitalization, missing cells, non-numeric text in numeric-looking fields).
2. **Analysis script**: Read and revised `week3_analysis_buggy.py` so it handles messy input more safely, summarizes responses, and writes a frequency export.
3. **Documentation**: Added comments, docstrings, and this markdown file so the work is explainable to others (including people who do not read Python).

---

## For someone who does not read code

This section explains **what the Week 3 script does** and **how to run it**, without assuming you read code.

All paths below use the folder `**week 3/`** (there is a space in the name—quotes matter in Terminal).

### `week3_analysis_buggy.py` — summarize a messy survey and export counts

- **Purpose**: Loads `**week3_survey_messy.csv`**, prints how many responses fall into each role, department, and primary tool (with cleaning rules so similar spellings are grouped sensibly). It also prints average years of experience (using safer parsing than “integer only”) and top satisfaction scores. It writes a small summary file: `**week3_frequency_summary.csv`** with columns **category**, **value**, and **count** so the breakdowns are easy to open in a spreadsheet.
- **Inputs**: `week 3/week3_survey_messy.csv` (must sit in the **same folder** as the script).
- **Output**: Text printed in the Terminal, plus `**week 3/week3_frequency_summary.csv`** (regenerated each time you run the script).

**How to run it**

```bash
cd "week 3"
python3 week3_analysis_buggy.py
```

**What “success” looks like**: You see sections for roles, departments, and primary tools (counts listed), then average experience and top satisfaction scores, and the CSV file appears or updates next to the script.

---

## Competency 2 — Code literacy and documentation

### Evidence in this repo (checklist)


| Rubric item                                                                | Where to look                                                                                                                    |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Inline comments** (prefer *why*, not only *what*)                        | `week 3/week3_analysis_buggy.py` (e.g. cleaning / parsing logic and frequency helpers)                                           |
| **Docstrings** (what inputs mean, what the function does, what it returns) | Module docstring; `parse_experience_years()`, `count_most_common()`, `write_frequency_csv()` in `week 3/week3_analysis_buggy.py` |
| **Commit messages** (*what changed* and *why*)                             | Paste real messages below; in Terminal: `git log --oneline -10`                                                                  |
| **Markdown for a non-technical reader**                                    | This file — section **“For someone who does not read code”**                                                                     |


### Commit messages I used this week *(paste from `git log`)*

1. fixed 2 bugs in week3 analysis buggy file (avg experience and satisfaction score)
2. added a week 3 competency claims w evidence

### How I demonstrated C2

I demonstrated code literacy and documentation by reading through the buggy script, understanding what each part was trying to do, and then making changes that improved both correctness and readability. I documented the script in multiple ways: with inline comments that explain why certain cleaning steps were necessary, with docstrings on my functions that explain what each function takes, what it does, and what it returns, and with commit messages that clearly describe each fix. I also explained the script in this markdown file so that someone without much technical background could still understand what the program is doing and what I changed.

### What “code literacy” meant for me this week

- I traced how the script **loads** the CSV, **loops** over rows, and where it assumed data would already be “clean.”
- I connected **error messages** (like failed integer conversion) to **specific lines** and to **real cells** in the file.
- I separated **normalization rules** (for roles, departments, tools) from **printing** and **file export** so the script is easier to follow and change later.

### What “documentation” meant for me this week

- **In-code**: Comments and docstrings that match what the code actually does after fixes—not only what the first draft tried to do.
- **For humans**: This `week3.md` file plus run instructions that do not require reading Python.
- **For reproducibility**: A generated CSV that captures the summarized counts in a stable format for analysis or grading.

---

## Competency 3 — Data cleaning and file handling

### How I demonstrated C3

I demonstrated data cleaning and file handling by working with a real CSV file that contained messy data, including inconsistent capitalization, missing entries, and an invalid non-numeric value in the `experience_years` column. When the script crashed with `ValueError: invalid literal for int() with base 10: 'fifteen'`, I used the traceback to identify the exact line causing the problem and understood that the script was assuming every value in that column could be converted directly to an integer. I then updated the script so it could handle messy input more safely and continue running. I also extended the script to write summarized output into a new CSV file (`week3_frequency_summary.csv`), which made the process repeatable and produced a clearer dataset for analysis.

### What in the data was “messy” (concrete examples)

- **Capitalization**: The same role or department might appear in different cases; tool names might repeat with different casing.
- **Missing cells**: Some fields can be empty (for example, a missing role on a row that still has other answers).
- **Experience years**: Values may be digits *or* words (for example **fifteen**), which breaks a naive `int()` conversion.

### What I changed in handling (high level)

- **Safer parsing for experience** so word-like numbers can be interpreted when possible, instead of crashing the whole script.
- **Explicit rules for summarizing categories** (including how blank values are labeled, and how tool names are grouped without breaking multi-word names like **VS Code**).
- **File output** so frequency summaries are not only visible in the Terminal but also saved as **CSV** for reuse.

---

## Observations

- **Cleaning is a design choice**: “Same” answer spelled differently can be one bucket or many; I made rules that match what I want the analysis to say and documented them in code and here.
- **A traceback is a map**: It points to a line number and a value—pairing that with the CSV row makes debugging fast.
- **Exporting CSV** turns a one-off script into something a teammate (or grader) can **rerun** and **inspect** without re-counting by hand.

---

## So what? (for future weeks)

- When a column *looks* numeric, **verify** a few raw cells before assuming `int()` is enough.
- Keep **one short markdown note per week** when competencies ask for reflection tied to real files and real errors.
- Prefer **stable output files** (CSV) when the assignment asks for repeatable analysis or submission artifacts.

---

