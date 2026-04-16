#!/usr/bin/env python3
"""Load messy survey CSV; parse experience_years as int or English words."""

import csv
import os

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


def main() -> None:
    filename = os.path.join(os.path.dirname(__file__), "week3_survey_messy.csv")
    rows = []

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Count responses by role
    role_counts: dict[str, int] = {}

    for row in rows:
        role = row["role"].strip().title()
        if role in role_counts:
            role_counts[role] += 1
        else:
            role_counts[role] = 1

    print("Responses by role:")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count}")

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
