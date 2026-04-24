#!/usr/bin/env python3
"""Fetch reviews from the HCDE 530 week 4 API; print category and helpful votes; save CSV.

API host: https://hcde530-week4-api.onrender.com/
Review list: GET /reviews?limit=100

Run from anywhere:
  python3 "week 4/week4_reviews_fetch.py"

Writes:
  reviews_category_helpful.csv — category and helpful_votes per review
  reviews_avg_rating_by_app.csv — mean rating per app
"""

from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.request
from collections import defaultdict

API_BASE = "https://hcde530-week4-api.onrender.com"
API_ROOT_URL = f"{API_BASE}/"
REVIEWS_URL = f"{API_BASE}/reviews?limit=100"
OUTPUT_CSV = "reviews_category_helpful.csv"
AVG_RATING_BY_APP_CSV = "reviews_avg_rating_by_app.csv"


def fetch_json(url: str) -> object:
    """GET a URL and parse JSON."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def parse_reviews_payload(payload: object) -> list[dict]:
    """Extract the reviews list from the /reviews response."""
    if not isinstance(payload, dict):
        raise ValueError("Unexpected API response: top-level value is not an object")
    reviews = payload.get("reviews")
    if not isinstance(reviews, list):
        raise ValueError("Unexpected API response: missing 'reviews' list")
    return reviews


def average_ratings_by_app(reviews: list[dict]) -> list[dict[str, object]]:
    """Sum numeric ratings per app; return sorted rows with count and mean."""
    rating_sum: dict[str, float] = defaultdict(float)
    rating_count: dict[str, int] = defaultdict(int)

    for review in reviews:
        if not isinstance(review, dict):
            continue
        app = review.get("app")
        rating = review.get("rating")
        if not isinstance(app, str) or not app.strip():
            continue
        try:
            value = float(rating)
        except (TypeError, ValueError):
            continue
        rating_sum[app] += value
        rating_count[app] += 1

    rows: list[dict[str, object]] = []
    for app in sorted(rating_sum.keys()):
        count = rating_count[app]
        mean = rating_sum[app] / count if count else 0.0
        rows.append(
            {
                "app": app,
                "review_count": count,
                "average_rating": round(mean, 4),
            }
        )
    return rows


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, OUTPUT_CSV)
    avg_by_app_path = os.path.join(script_dir, AVG_RATING_BY_APP_CSV)

    # 1) Call the API root (service metadata).
    root_payload = fetch_json(API_ROOT_URL)
    if isinstance(root_payload, dict) and "name" in root_payload:
        print(f"Connected to: {root_payload.get('name')}")

    # Reviews payload includes category and helpful_votes for each item.
    reviews = parse_reviews_payload(fetch_json(REVIEWS_URL))

    rows: list[dict[str, object]] = []
    for review in reviews:
        if not isinstance(review, dict):
            continue
        category = review.get("category", "")
        helpful_votes = review.get("helpful_votes", "")
        rows.append({"category": category, "helpful_votes": helpful_votes})
        print(f"{category}: {helpful_votes} helpful votes")

    with open(out_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["category", "helpful_votes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {out_path}")

    avg_rows = average_ratings_by_app(reviews)
    for row in avg_rows:
        print(
            f"{row['app']}: avg rating {row['average_rating']} "
            f"({row['review_count']} reviews)"
        )
    with open(avg_by_app_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=["app", "review_count", "average_rating"]
        )
        writer.writeheader()
        writer.writerows(avg_rows)
    print(f"Saved {len(avg_rows)} app summaries to {avg_by_app_path}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to fetch reviews: {exc}") from exc
