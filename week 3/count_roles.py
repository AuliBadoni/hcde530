#!/usr/bin/env python3
"""Count how many times each role appears in responses_cleaned.csv."""

import csv
import os
from collections import Counter


def main() -> None:
    base = os.path.dirname(__file__)
    in_path = os.path.join(base, "responses_cleaned.csv")

    counts: Counter[str] = Counter()
    with open(in_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "role" not in reader.fieldnames:
            raise ValueError("responses_cleaned.csv must have a header row with a 'role' column")
        for row in reader:
            raw = row.get("role")
            if raw is None or not str(raw).strip():
                key = "(blank)"
            else:
                key = str(raw).strip()
            counts[key] += 1

    # Highest count first; ties broken alphabetically by role
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    print(f"{'Role':<40} {'Count':>6}")
    print("-" * 47)
    for role, n in ordered:
        print(f"{role:<40} {n:>6}")
    print()
    print(f"Total rows counted: {sum(counts.values())}")


if __name__ == "__main__":
    main()
