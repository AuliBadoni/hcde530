import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import billboard
import numpy as np
import pandas as pd


CHART_NAME = "hot-100"
START_DATE = "2023-01-07"
END_DATE = "2026-05-02"
REQUEST_DELAY_SEC = 0.1
REQUEST_TIMEOUT_SEC = 20
MAX_RETRIES = 1
MAX_WORKERS = 24
OUTPUT_PATH = Path("data") / "billboard_hot100_2023_2026.csv"


def generate_chart_dates(start: str, end: str) -> list[str]:
    """Saturday-dated weekly chart strings between start and end (inclusive)."""
    return (
        pd.date_range(start=start, end=end, freq="W-SAT")
        .strftime("%Y-%m-%d")
        .tolist()
    )


def fetch_chart(date_str: str) -> list[dict]:
    """Fetch one Hot 100 chart and return a list of row dicts."""
    chart = billboard.ChartData(
        CHART_NAME,
        date=date_str,
        timeout=REQUEST_TIMEOUT_SEC,
        max_retries=MAX_RETRIES,
    )
    return [
        {
            "chart_date": chart.date,
            "rank": entry.rank,
            "song": entry.title,
            "artist": entry.artist,
            "last_week": entry.lastPos,
            "peak_rank": entry.peakPos,
            "weeks_on_board": entry.weeks,
            "is_new": entry.isNew,
            "image_url": entry.image,
        }
        for entry in chart
    ]


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add analytical columns derived from the raw Billboard fields."""
    df = df.copy()
    df["chart_date"] = pd.to_datetime(df["chart_date"], errors="coerce")

    # In billboard.py, lastPos = 0 means the song was not on the previous week's chart.
    df["last_week"] = df["last_week"].replace(0, pd.NA)

    df["year"] = df["chart_date"].dt.year
    df["month"] = df["chart_date"].dt.month
    df["decade"] = (df["year"] // 10) * 10

    df["is_top_10"] = df["rank"] <= 10
    df["is_number_one"] = df["rank"] == 1

    last_week_num = pd.to_numeric(df["last_week"], errors="coerce")
    df["rank_change"] = last_week_num - df["rank"]

    is_new = df["is_new"].astype(bool)
    last_week_missing = last_week_num.isna()

    conditions = [
        is_new,
        last_week_missing & ~is_new,
        last_week_num > df["rank"],
        last_week_num < df["rank"],
    ]
    choices = ["new", "re-entry", "up", "down"]
    df["movement_type"] = np.select(conditions, choices, default="same")

    return df


def _polite_fetch(date_str: str, throttle: Lock) -> list[dict]:
    """Acquire the throttle long enough to space request starts, then fetch."""
    with throttle:
        time.sleep(REQUEST_DELAY_SEC)
    return fetch_chart(date_str)


def main() -> None:
    dates = generate_chart_dates(START_DATE, END_DATE)
    total = len(dates)
    print(
        f"Fetching {total} weekly Hot 100 charts from {START_DATE} to {END_DATE} "
        f"with {MAX_WORKERS} workers."
    )

    all_rows: list[dict] = []
    failures: list[tuple[str, str]] = []
    throttle = Lock()
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_polite_fetch, d, throttle): d for d in dates
        }
        for future in as_completed(futures):
            date_str = futures[future]
            completed += 1
            try:
                rows = future.result()
                all_rows.extend(rows)
                print(f"[{completed}/{total}] {date_str} -> {len(rows)} rows")
            except Exception as e:
                failures.append((date_str, str(e)))
                print(f"[{completed}/{total}] {date_str} FAILED: {e}")

    if not all_rows:
        print("No data fetched. Nothing to save.")
        return

    df = pd.DataFrame(all_rows)
    df = df.sort_values(["chart_date", "rank"]).reset_index(drop=True)
    df = add_derived_columns(df)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Saved {len(df):,} rows from {df['chart_date'].nunique()} charts to {OUTPUT_PATH}")
    if failures:
        print(f"Failures: {len(failures)} weeks")
        for date_str, reason in failures:
            print(f"  - {date_str}: {reason}")


if __name__ == "__main__":
    main()
