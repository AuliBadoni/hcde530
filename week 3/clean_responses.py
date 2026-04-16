#!/usr/bin/env python3
"""Read demo_responses.csv, drop rows with empty name, uppercase role, write responses_cleaned.csv."""

import csv
import os

# Output column order: id, participant name, role, response text
OUTPUT_FIELDS = ["participant_id", "name", "role", "response"]


def _should_skip_row(fieldnames: list[str], row: dict[str, str]) -> bool:
    if "name" in fieldnames:
        name = row.get("name")
        return name is None or not str(name).strip()
    ident = row.get("participant_id")
    return ident is None or not str(ident).strip()


def main() -> None:
    base = os.path.dirname(__file__)
    in_path = os.path.join(base, "demo_responses.csv")
    out_path = os.path.join(base, "responses_cleaned.csv")

    with open(in_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise ValueError("demo_responses.csv has no header row")
        fieldnames_in = list(reader.fieldnames)
        cleaned = []
        for row in reader:
            if _should_skip_row(fieldnames_in, row):
                continue
            role = row.get("role")
            if role is None:
                role = ""
            row["role"] = str(role).strip().upper()
            cleaned.append({k: row.get(k, "") for k in OUTPUT_FIELDS})

    with open(out_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(cleaned)


if __name__ == "__main__":
    main()
