"""
MoveInSync Play Store review scraper (repeatable / incremental).

Setup:
    pip install google-play-scraper pandas

Usage:
    1) Find the right app IDs:
        python scrape_reviews.py discover "MoveInSync"
        python scrape_reviews.py discover "MoveInSync driver"
    2) Scrape (first run = full history up to --max, later runs = only NEW reviews):
        python scrape_reviews.py scrape com.xxx.yyy --max 8000
    3) Run step 2 weekly -> data/ratings_history.csv builds a rating trend.
"""
import argparse
import os
import time
from datetime import datetime

import pandas as pd
from google_play_scraper import Sort, app, reviews, search

DATA_DIR = "data"
COLS = ["reviewId", "score", "content", "thumbsUpCount",
        "reviewCreatedVersion", "at", "replyContent", "repliedAt"]
SNAPSHOT_COLS = [
    "date", "app_id", "title", "score", "ratings", "reviews",
    "star1", "star2", "star3", "star4", "star5", "version", "updated"
]


def discover(query: str, country: str = "in") -> None:
    hits = search(query, lang="en", country=country, n_hits=15)
    print(f"{'appId':45} | {'title':35} | score | developer")
    for r in hits:
        app_id = str(r.get('appId') or '')
        title = str(r.get('title') or '')[:35]
        score = float(r.get('score') or 0.0)
        developer = str(r.get('developer') or '')
        print(f"{app_id:45} | {title:35} | {score:4.2f}  | {developer}")


def save_snapshot_record(row: dict, filepath: str = None) -> pd.DataFrame:
    """
    Safely upserts a rating snapshot record keyed by (date, app_id).
    - If file is missing or empty: creates new file with standard header.
    - If (date, app_id) exists: updates/replaces that snapshot logically instead of appending duplicates.
    - Preserves existing snapshots for all other dates and apps.
    - Uses atomic write (temp file + rename/replace) to prevent data corruption.
    """
    if filepath is None:
        filepath = os.path.join(DATA_DIR, "ratings_history.csv")

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        try:
            df = pd.read_csv(filepath)
            for col in SNAPSHOT_COLS:
                if col not in df.columns:
                    df[col] = None
            df = df[SNAPSHOT_COLS]
        except Exception:
            df = pd.DataFrame(columns=SNAPSHOT_COLS)
    else:
        df = pd.DataFrame(columns=SNAPSHOT_COLS)

    new_row_df = pd.DataFrame([row])
    for col in SNAPSHOT_COLS:
        if col not in new_row_df.columns:
            new_row_df[col] = None
    new_row_df = new_row_df[SNAPSHOT_COLS]

    key_mask = (df["date"] == row["date"]) & (df["app_id"] == row["app_id"])
    if key_mask.any():
        df_other = df[~key_mask]
        df_out = pd.concat([df_other, new_row_df], ignore_index=True)
    else:
        df_out = pd.concat([df, new_row_df], ignore_index=True)

    df_out = df_out[SNAPSHOT_COLS]

    tmp_path = f"{filepath}.tmp.{os.getpid()}"
    try:
        df_out.to_csv(tmp_path, index=False)
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise

    return df_out


def snapshot(app_id: str, country: str = "in", lang: str = "en", filepath: str = None) -> dict:
    """Fetch and upsert today's overall rating to ratings_history.csv."""
    info = app(app_id, lang=lang, country=country)
    hist = info.get("histogram") or [0, 0, 0, 0, 0]
    score = float(info.get("score") or 0.0)
    ratings = int(info.get("ratings") or 0)
    row = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "app_id": app_id,
        "title": info.get("title", ""),
        "score": score,
        "ratings": ratings,
        "reviews": info.get("reviews", 0),
        "star1": hist[0], "star2": hist[1], "star3": hist[2],
        "star4": hist[3], "star5": hist[4],
        "version": info.get("version"),
        "updated": info.get("lastUpdatedOn"),
    }
    save_snapshot_record(row, filepath=filepath)
    print(f"[snapshot] {info.get('title', '')}: {score:.2f} "
          f"({ratings} ratings, v{info.get('version')})")
    return row



def scrape(app_id: str, country: str, lang: str, max_reviews: int) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    snapshot(app_id, country, lang)

    path = os.path.join(DATA_DIR, f"{app_id}_reviews.csv")
    old = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=COLS)
    known = set(old["reviewId"])
    print(f"[scrape] already have {len(known)} reviews")

    new, token = [], None
    while len(new) < max_reviews:
        batch, token = reviews(app_id, lang=lang, country=country,
                               sort=Sort.NEWEST, count=200,
                               continuation_token=token)
        if not batch:
            break
        fresh = [r for r in batch if r["reviewId"] not in known]
        new.extend(fresh)
        print(f"  fetched {len(new)} new...", end="\r")
        if len(fresh) < len(batch) or token is None:
            break  # reached already-saved reviews or end of history
        time.sleep(1)  # be polite

    if new:
        df_new = pd.DataFrame(new)[COLS]
        out = pd.concat([df_new, old], ignore_index=True)
        out["at"] = pd.to_datetime(out["at"])
        out = out.sort_values("at", ascending=False)
        out.to_csv(path, index=False)
    print(f"\n[scrape] +{len(new)} new reviews -> {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover")
    d.add_argument("query")

    s = sub.add_parser("scrape")
    s.add_argument("app_id")
    s.add_argument("--country", default="in")
    s.add_argument("--lang", default="en")
    s.add_argument("--max", type=int, default=8000)

    a = p.parse_args()
    if a.cmd == "discover":
        discover(a.query)
    else:
        scrape(a.app_id, a.country, a.lang, a.max)

