"""
MoveInSync Review Analysis - Dashboard Data Layer
Pure business logic, filtering engine, aggregation metrics, and pipeline interface for Streamlit dashboard.
"""

import ast
import json
import os
import subprocess
import sys
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd


def load_apps_config(config_path: str = "config/apps.json") -> List[Dict[str, Any]]:
    """Loads configured applications from JSON config."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Apps configuration not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("apps", [])


def load_taxonomy_config(config_path: str = "config/taxonomy.json") -> Dict[str, Any]:
    """Loads taxonomy definitions from JSON config."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Taxonomy configuration not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_reviews_data(file_path: str = "reports/processed_all_reviews.csv") -> pd.DataFrame:
    """Loads standardized processed reviews dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Processed reviews dataset not found at {file_path}. Run analytics pipeline first.")
    
    df = pd.read_csv(file_path, low_memory=False)
    
    # Ensure standard types
    if "date" in df.columns:
        df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date_dt"] = pd.to_datetime(df.get("at", ""), errors="coerce")
        df["date"] = df["date_dt"].dt.strftime("%Y-%m-%d")
        
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
        
    if "version_clean" not in df.columns:
        if "reviewCreatedVersion" in df.columns:
            df["version_clean"] = df["reviewCreatedVersion"].fillna("Unknown/Unspecified")
        else:
            df["version_clean"] = "Unknown/Unspecified"
            
    if "content" not in df.columns:
        df["content"] = ""
    else:
        df["content"] = df["content"].fillna("").astype(str)
        
    return df


def load_ratings_history(file_path: str = "reports/ratings_history_clean.csv") -> pd.DataFrame:
    """Loads clean Play Store aggregate ratings snapshots."""
    if not os.path.exists(file_path):
        fallback = "data/ratings_history.csv"
        if os.path.exists(fallback):
            df = pd.read_csv(fallback)
            return df.drop_duplicates(subset=["date", "app_id"])
        return pd.DataFrame()
    return pd.read_csv(file_path)


def load_holdout_metrics(file_path: str = "reports/holdout_metrics_summary.csv") -> pd.DataFrame:
    """Loads holdout validation metrics summary if available."""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)


def filter_reviews(
    df: pd.DataFrame,
    app_id: Optional[str] = None,
    date_range: Optional[Tuple[Any, Any]] = None,
    ratings: Optional[List[int]] = None,
    versions: Optional[List[str]] = None,
    themes: Optional[List[str]] = None,
    search_term: Optional[str] = None,
) -> pd.DataFrame:
    """
    Filters review records dynamically based on active filter parameters.
    Handles empty dataframes and boundary conditions safely without raising exceptions.
    """
    if df.empty:
        return df.copy()

    filtered = df.copy()

    # 1. App filter
    if app_id and app_id.lower() != "all":
        filtered = filtered[filtered["app_id"] == app_id]

    # 2. Date range filter
    if date_range and len(date_range) == 2:
        start_d, end_d = date_range
        if start_d:
            start_ts = pd.to_datetime(start_d)
            filtered = filtered[filtered["date_dt"] >= start_ts]
        if end_d:
            end_ts = pd.to_datetime(end_d)
            # Include entire end day
            filtered = filtered[filtered["date_dt"] <= end_ts + pd.Timedelta(days=1, microseconds=-1)]

    # 3. Rating filter
    if ratings is not None and len(ratings) > 0:
        filtered = filtered[filtered["score"].isin(ratings)]

    # 4. Version filter
    if versions is not None and len(versions) > 0:
        if "All Versions" not in versions:
            filtered = filtered[filtered["version_clean"].isin(versions)]

    # 5. Themes filter (multi-label OR filter: review matches if it has ANY of selected themes)
    if themes is not None and len(themes) > 0:
        theme_cols = [f"theme_{t}" for t in themes if f"theme_{t}" in filtered.columns]
        if theme_cols:
            theme_mask = filtered[theme_cols].any(axis=1)
            filtered = filtered[theme_mask]

    # 6. Search term filter
    if search_term and search_term.strip():
        term = search_term.strip().lower()
        content_mask = filtered["content"].str.lower().str.contains(term, regex=False, na=False)
        filtered = filtered[content_mask]

    return filtered


def calculate_kpis(df: pd.DataFrame, functional_theme_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calculates summary KPIs for the currently filtered reviews dataset.
    Never hardcodes totals; handles empty datasets gracefully.
    """
    if df.empty:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "negative_count": 0,
            "negative_pct": 0.0,
            "positive_count": 0,
            "positive_pct": 0.0,
            "neutral_count": 0,
            "neutral_pct": 0.0,
            "most_mentioned_theme": None,
            "most_mentioned_theme_count": 0,
            "most_mentioned_theme_share_pct": 0.0,
        }

    total = len(df)
    scores = df["score"]
    avg_rating = round(float(scores.mean()), 2)

    neg_count = int((scores <= 2).sum())
    neg_pct = round((neg_count / total) * 100, 1)

    pos_count = int((scores >= 4).sum())
    pos_pct = round((pos_count / total) * 100, 1)

    neu_count = int((scores == 3).sum())
    neu_pct = round((neu_count / total) * 100, 1)

    # Find most mentioned functional theme (excluding other_unclassified if specified)
    most_theme = None
    most_count = 0
    most_share = 0.0

    if functional_theme_keys:
        candidates = functional_theme_keys
    else:
        candidates = [c.replace("theme_", "") for c in df.columns if c.startswith("theme_") and c != "theme_other_unclassified"]

    for t in candidates:
        col = f"theme_{t}"
        if col in df.columns:
            cnt = int(df[col].sum())
            if cnt > most_count:
                most_count = cnt
                most_theme = t

    if most_theme and total > 0:
        most_share = round((most_count / total) * 100, 1)

    return {
        "total_reviews": total,
        "average_rating": avg_rating,
        "negative_count": neg_count,
        "negative_pct": neg_pct,
        "positive_count": pos_count,
        "positive_pct": pos_pct,
        "neutral_count": neu_count,
        "neutral_pct": neu_pct,
        "most_mentioned_theme": most_theme,
        "most_mentioned_theme_count": most_count,
        "most_mentioned_theme_share_pct": most_share,
    }


def calculate_theme_breakdown(
    df: pd.DataFrame,
    taxonomy_metadata: Dict[str, Any],
    include_other: bool = True
) -> pd.DataFrame:
    """
    Computes per-theme aggregation statistics for active reviews.
    Explicitly distinguishes unique review count from theme mention counts.
    """
    rows = []
    total_reviews = len(df)
    themes_dict = taxonomy_metadata.get("themes", {})

    all_keys = list(themes_dict.keys())
    if include_other:
        all_keys.append("other_unclassified")

    for key in all_keys:
        col = f"theme_{key}"
        if col not in df.columns:
            continue

        theme_name = themes_dict.get(key, {}).get("name", "Other / Generic (No specific feature)" if key == "other_unclassified" else key)
        theme_reviews = df[df[col] == True]
        mention_count = len(theme_reviews)

        if mention_count > 0:
            scores = theme_reviews["score"]
            neg_count = int((scores <= 2).sum())
            neu_count = int((scores == 3).sum())
            pos_count = int((scores >= 4).sum())
            neg_rate = round((neg_count / mention_count) * 100, 1)
            mean_score = round(float(scores.mean()), 2)
            share_of_reviews = round((mention_count / total_reviews) * 100, 1) if total_reviews > 0 else 0.0
        else:
            neg_count = 0
            neu_count = 0
            pos_count = 0
            neg_rate = 0.0
            mean_score = 0.0
            share_of_reviews = 0.0

        rows.append({
            "theme_key": key,
            "theme_name": theme_name,
            "mention_count": mention_count,
            "share_of_reviews_pct": share_of_reviews,
            "negative_reviews_1_2_star": neg_count,
            "neutral_reviews_3_star": neu_count,
            "positive_reviews_4_5_star": pos_count,
            "negative_rate_within_theme_pct": neg_rate,
            "mean_rating": mean_score,
        })

    result_df = pd.DataFrame(rows)
    if not result_df.empty:
        result_df.sort_values(by="mention_count", ascending=False, inplace=True)
    return result_df


def calculate_rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Computes exact 1–5 star counts and percentages."""
    total = len(df)
    data = []
    for star in [1, 2, 3, 4, 5]:
        count = int((df["score"] == star).sum()) if total > 0 else 0
        pct = round((count / total) * 100, 1) if total > 0 else 0.0
        data.append({"star": star, "count": count, "pct": pct})
    return pd.DataFrame(data)


def calculate_time_series(df: pd.DataFrame, freq: str = "W-MON") -> pd.DataFrame:
    """
    Computes time-series trajectory of reviews volume and average rating.
    """
    if df.empty or "date_dt" not in df.columns:
        return pd.DataFrame(columns=["period", "review_count", "average_rating"])

    valid_df = df.dropna(subset=["date_dt"]).copy()
    if valid_df.empty:
        return pd.DataFrame(columns=["period", "review_count", "average_rating"])

    # Group by period
    grouped = valid_df.groupby(pd.Grouper(key="date_dt", freq=freq)).agg(
        review_count=("score", "count"),
        average_rating=("score", "mean")
    ).reset_index()

    # Filter out empty future/past bins if whole range is selected
    grouped = grouped[grouped["review_count"] > 0].copy()
    grouped["period"] = grouped["date_dt"].dt.strftime("%Y-%m-%d")
    grouped["average_rating"] = grouped["average_rating"].round(2)
    return grouped[["period", "review_count", "average_rating"]]


def export_filtered_csv(df: pd.DataFrame, columns: Optional[List[str]] = None) -> str:
    """Exports filtered dataframe as CSV string for download."""
    if df.empty:
        return ""
    if columns:
        cols_to_export = [c for c in columns if c in df.columns]
        return df[cols_to_export].to_csv(index=False)
    return df.to_csv(index=False)


def get_data_freshness_metadata(
    processed_file: str = "reports/processed_all_reviews.csv",
    ratings_file: str = "reports/ratings_history_clean.csv",
    holdout_file: str = "reports/holdout_metrics_summary.csv",
) -> Dict[str, Any]:
    """Retrieves modification timestamps and file governance status."""
    meta = {
        "processed_exists": os.path.exists(processed_file),
        "ratings_exists": os.path.exists(ratings_file),
        "holdout_exists": os.path.exists(holdout_file),
        "last_recomputed_str": "Never",
        "ratings_snapshot_date": "Unknown",
        "holdout_verified": False,
    }

    if meta["processed_exists"]:
        mtime = os.path.getmtime(processed_file)
        dt = datetime.fromtimestamp(mtime)
        meta["last_recomputed_str"] = dt.strftime("%Y-%m-%d %H:%M:%S")

    if meta["ratings_exists"]:
        try:
            r_df = pd.read_csv(ratings_file)
            if "date" in r_df.columns and not r_df.empty:
                dates = r_df["date"].unique().tolist()
                meta["ratings_snapshot_date"] = ", ".join(dates)
        except Exception:
            pass

    if meta["holdout_exists"]:
        try:
            h_df = pd.read_csv(holdout_file)
            meta["holdout_verified"] = not h_df.empty
        except Exception:
            pass

    return meta


def run_recompute_pipeline(python_executable: Optional[str] = None) -> Tuple[bool, str]:
    """
    Runs the existing analysis pipeline (`analyze_reviews.py`) locally.
    Never swallows errors silently. Returns (success, output_or_error_message).
    """
    py_exec = python_executable or sys.executable
    script_path = "analyze_reviews.py"
    if not os.path.exists(script_path):
        return False, f"Analysis script '{script_path}' not found."

    try:
        res = subprocess.run(
            [py_exec, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120
        )
        if res.returncode == 0:
            return True, "Recomputation completed successfully. Processed review datasets and charts refreshed."
        else:
            return False, f"Recomputation failed (exit code {res.returncode}):\n{res.stderr.strip() or res.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Recomputation timed out after 120 seconds."
    except Exception as e:
        return False, f"Failed to execute recomputation subprocess: {str(e)}"


def run_remote_scraping(python_executable: Optional[str] = None) -> Tuple[bool, str]:
    """
    Executes remote Google Play scraper (`scrape_reviews.py`) on explicit user request.
    Never swallows errors silently. Returns (success, output_or_error_message).
    """
    py_exec = python_executable or sys.executable
    script_path = "scrape_reviews.py"
    if not os.path.exists(script_path):
        return False, f"Scraper script '{script_path}' not found."

    try:
        res = subprocess.run(
            [py_exec, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180
        )
        if res.returncode == 0:
            return True, "Play Store scraping completed successfully. Raw CSVs and rating snapshots updated."
        else:
            return False, f"Scraping failed (exit code {res.returncode}):\n{res.stderr.strip() or res.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Remote scraping timed out after 180 seconds."
    except Exception as e:
        return False, f"Failed to execute scraper subprocess: {str(e)}"
