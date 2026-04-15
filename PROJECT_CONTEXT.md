# HCDE 530 — project context

This file describes **intent, audience, and working agreements** for this repository. It is written for **you** (UX / HCD practitioner), **your instructor and TA**, **a few classmates**, and **tools** (for example Cursor) that use repo-level context. Technical defaults also appear in **`.cursorrules`**.

---

## What this repository is

- **Course**: HCDE 530 — computation concepts in human-centered design and engineering.
- **Purpose**: Complete **class assignments**, **run and adapt** instructor-provided **artifacts and prototypes**, and keep a clear record of what you built and how to reproduce it.
- **Primary goal**: Learn the ideas—code is a **means**, not the product—while keeping work **easy to run and grade** from a fresh **GitHub clone**.

---

## Audience and submission

- **Who should “get” this repo**: You, your **professor**, **TA**, and a **small set of peers**.
- **How work is submitted**: Changes are **committed to GitHub**; you submit a **link to this repository** (graders will clone it).

---

## What “it works” means

1. **Python**: Someone can run the relevant scripts from the **terminal** on a typical setup (see Environment) and see **expected console output** or generated files.
2. **Web demos**: Someone can **open the HTML** in a browser (local file or simple server, per assignment) and see the **intended prototype or dashboard behavior**.

---

## Environment and dependencies

- **Your machine**: **macOS** day to day.
- **Python**: **Python 3**; use what the course materials specify when they specify it.
- **Libraries**:
  - Prefer the **Python standard library** when the assignment allows (matches small class scripts and avoids surprise installs).
  - When the handout requires **`pip install`**, follow the **exact commands** from the instructor first.
- **When commands differ by system**: It is normal for install or run steps to **vary by OS or Python install**. When you discover what **actually works on your Mac**, record it in **two places**:
  - A **short note** in that **week’s folder** (quick reference).
  - Anything graders must not miss also belongs in the **main `README.md`** at the repo root.

If you add third-party packages for a week, prefer capturing them the way the course asks (for example `requirements.txt` or pasted commands)—**match the handout** when in doubt.

---

## Data and privacy

- **Default assumption for files in this repo**: Materials are **class-safe** (synthetic, provided, or otherwise **OK to share on GitHub**).
- **Habit**: Still avoid committing **secrets** (API keys, passwords) and **accidental personal notes**; keep `.gitignore` sensible for local junk (for example `.DS_Store`).

---

## Repository layout

- **Week folders**: Keep work grouped by week (for example `week 2/`, `week 3/`), consistent with how the class organizes assignments.
- **Code and data**: Colocate scripts with the **CSV and HTML** (or other data) they use **in that week’s folder**, unless an assignment dictates otherwise.
- **Write-ups, screenshots, figures, exports**: Keep them **in the repo**, organized **per week**—for example `week 3/README.md` (or similar) plus **`week 3/assets/`** for images and non-code artifacts so everything for that assignment stays together.

---

## How you want code to read

You are a **design / HCD practitioner**, not a software engineer. The top priority for readability is:

- **(A) A short “how to run this” block at the top** of each runnable script: commands, working directory assumptions, and what output or file changes to expect.

Prefer **plain language**, **small steps**, and **boring, clear structure** over clever one-liners or unexplained jargon. Explanations that help *you* understand can also live in the **week note** or **root `README`**.

---

## AI tools and academic integrity

- **Course policy on AI** (if any): **Not confirmed here**—follow the **syllabus and assignment instructions** when they conflict with any generic tooling advice.
- **Practical default**: Use assistants to **understand errors**, **suggest edits**, and **document run steps**—and **review** anything merged so you can explain it. If the course requires **disclosure** of AI use on assignments, **comply** and update this section when you know the rule.

---

## Related files

- **`.cursorrules`**: Short, tool-oriented defaults for this repo (languages, Python habits, small diffs, HTML embedding patterns).
- **`README.md`**: Entry point for humans cloning the repo; keep high-signal **run instructions** and **week pointers** there.

When this context and `.cursorrules` disagree with an **assignment handout**, **the handout wins**.
