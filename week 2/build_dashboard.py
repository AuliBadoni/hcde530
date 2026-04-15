#!/usr/bin/env python3
"""Re-embed demo_responses.csv data into demo_dashboard.html (same folder as this script)."""

import csv
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "demo_responses.csv")
HTML_PATH = os.path.join(BASE, "demo_dashboard.html")

# Main function to build the dashboard
def main() -> None:
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # Count the number of words in each response
    for r in rows:
        r["word_count"] = len(r["response"].split())
    payload = json.dumps(rows, ensure_ascii=False)
    # Read the HTML file
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    # Replace the embedded data with the new data
    pattern = r'(<script id="embedded-data" type="application/json">\s*)[\s\S]*?(\s*</script>)'
    new_html, n = re.subn(pattern, r"\1" + payload + r"\2", html, count=1)
    if n != 1:
        raise SystemExit(
            "Could not find <script id=\"embedded-data\"> block in demo_dashboard.html"
        )

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Updated {HTML_PATH} with {len(rows)} rows from {CSV_PATH}")


if __name__ == "__main__":
    main()
