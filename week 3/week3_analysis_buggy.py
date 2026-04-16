#!/usr/bin/env python3
"""Load messy survey CSV; parse experience_years as int or English words.

Run from anywhere:
  python3 "week 3/week3_analysis_buggy.py"

Reads: week3_survey_messy.csv (same folder as this script).
Writes: week3_frequency_summary.csv (role / department / primary_tool counts).
"""

import csv
import os
from collections import Counter, defaultdict
from typing import Literal

# Units and teens (single-token numbers 0–19)
_UNITS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)

# Tens stem -> base value (covers "twenty", "twenty-one", "twenty one", …)
_TENS = (
    ("twenty", 20),
    ("thirty", 30),
    ("forty", 40),
    ("fifty", 50),
    ("sixty", 60),
)


def _build_experience_word_map() -> dict[str, int]:
    m: dict[str, int] = {}
    for i, w in enumerate(_UNITS):
        m[w] = i
    # Common typos / variants in free-text or messy exports
    m["fiftee"] = 15
    for stem, base in _TENS:
        m[stem] = base
        for u in range(1, 10):
            unit = _UNITS[u]
            m[f"{stem}-{unit}"] = base + u
            m[f"{stem} {unit}"] = base + u
    return m


_EXPERIENCE_WORD_MAP = _build_experience_word_map()


def parse_experience_years(raw: str | None) -> int | None:
    """Parse digits or English number words to int years; None if unknown."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        key = " ".join(s.lower().replace("-", " ").split())
        return _EXPERIENCE_WORD_MAP.get(key)


def count_most_common(
    rows: list[dict[str, str | None]],
    field_name: str,
    *,
    how: Literal["title", "case_insensitive"],
) -> list[tuple[str, int]]:
    """Count values in one column; return (label, count) sorted by count desc, then label asc.

    Blank or missing cells are counted as ``(blank)``. Use ``how="title"`` for roles and
    departments. Use ``how="case_insensitive"`` for tools so ``figma`` and ``Figma`` merge
    without breaking multi-word names like ``VS Code`` (display is the most common spelling).
    """
    if how == "title":
        counts: Counter[str] = Counter()
        for row in rows:
            raw = row.get(field_name)
            if raw is None or not str(raw).strip():
                counts["(blank)"] += 1
            else:
                counts[str(raw).strip().title()] += 1
        pairs = list(counts.items())
    else:
        group_counts: Counter[str] = Counter()
        variants: dict[str, Counter[str]] = defaultdict(Counter)
        for row in rows:
            raw = row.get(field_name)
            if raw is None or not str(raw).strip():
                group_counts["__blank__"] += 1
            else:
                s = str(raw).strip()
                key = s.casefold()
                group_counts[key] += 1
                variants[key][s] += 1
        pairs = []
        for key, n in group_counts.items():
            if key == "__blank__":
                pairs.append(("(blank)", n))
            else:
                best = sorted(variants[key].items(), key=lambda item: (-item[1], item[0]))[0][0]
                pairs.append((best, n))
    return sorted(pairs, key=lambda item: (-item[1], item[0]))


def write_frequency_csv(path: str, summaries: dict[str, list[tuple[str, int]]]) -> None:
    """Write one CSV with columns category, value, count for each named summary list."""
    fieldnames = ["category", "value", "count"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for category, rows in summaries.items():
            for value, count in rows:
                writer.writerow({"category": category, "value": value, "count": count})


def main() -> None:
    filename = os.path.join(os.path.dirname(__file__), "week3_survey_messy.csv")
    rows = []

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    role_summary = count_most_common(rows, "role", how="title")
    dept_summary = count_most_common(rows, "department", how="title")
    tool_summary = count_most_common(rows, "primary_tool", how="case_insensitive")

    print("Responses by role:")
    for role, count in role_summary:
        print(f"  {role}: {count}")

    print("\nResponses by department:")
    for dept, count in dept_summary:
        print(f"  {dept}: {count}")

    print("\nResponses by primary tool:")
    for tool, count in tool_summary:
        print(f"  {tool}: {count}")

    out_csv = os.path.join(os.path.dirname(__file__), "week3_frequency_summary.csv")
    write_frequency_csv(
        out_csv,
        {
            "role": role_summary,
            "department": dept_summary,
            "primary_tool": tool_summary,
        },
    )

    # Average years: only rows with parseable experience_years
    total_experience = 0
    parsed_n = 0
    skipped: list[str] = []
    for row in rows:
        y = parse_experience_years(row.get("experience_years"))
        if y is None:
            rid = row.get("response_id", "?")
            skipped.append(f"{rid} ({row.get('experience_years', '')!r})")
            continue
        total_experience += y
        parsed_n += 1

    if parsed_n:
        avg_experience = total_experience / parsed_n
        print(f"\nAverage years of experience: {avg_experience:.1f} (from {parsed_n} of {len(rows)} rows)")
    else:
        print("\nAverage years of experience: (no parseable experience_years values)")

    if skipped:
        print(f"  Skipped unparseable experience_years: {', '.join(skipped)}")

    # Top 5 satisfaction scores (sorted highest to lowest)
    scored_rows = []
    for row in rows:
        if row["satisfaction_score"].strip():
            scored_rows.append((row["participant_name"], int(row["satisfaction_score"])))

    scored_rows.sort(key=lambda x: x[1], reverse=True)
    top5 = scored_rows[:5]

    print("\nTop 5 satisfaction scores:")
    for name, score in top5:
        print(f"  {name}: {score}")


if __name__ == "__main__":
    main()
