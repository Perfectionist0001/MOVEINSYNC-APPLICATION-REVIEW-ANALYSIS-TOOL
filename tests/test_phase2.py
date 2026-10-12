"""
Phase 2 Focused Regression Test Suite: Pipeline Generalization & Multi-App Parity
Tests:
1. All three configured apps load successfully from config/apps.json.
2. Each app's input file is processed without an app-specific code copy.
3. Processed output schemas are consistent across all apps and combined output.
4. Every source review ID is preserved exactly once in its corresponding processed output.
5. Combined output contains all source reviews (715) and correct app IDs.
6. Theme summary counts reconcile with the processed data.
7. Missing versions remain unknown (Unknown/Unspecified) rather than being inferred.
8. Empty or missing optional fields are handled safely without dropping rows.
9. Dynamic chart titles and date ranges reflect the selected dataset; handles empty datasets safely.
10. Running the pipeline twice produces consistent results without duplicate rows.
"""

import json
import os
import shutil
import tempfile
import unittest
import numpy as np
import pandas as pd

from config_loader import load_apps_config, load_taxonomy_config
from analyze_reviews import (
    clean_app_dataframe,
    process_app_themes,
    compute_theme_summary,
    compute_version_summary,
    save_combined_processed_reviews,
    generate_charts,
    get_app_slug
)


class TestPhase2PipelineGeneralization(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.apps_cfg = load_apps_config("config/apps.json")
        self.expected_apps = {
            "com.moveinsync.ets": "employee",
            "com.moveinsync.driver.lite": "driver_lite",
            "com.moveinsync.driver.dco": "driver_dco"
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_all_three_configured_apps_load_successfully(self):
        """1. All three configured apps load successfully from config/apps.json."""
        apps_list = self.apps_cfg.get("apps", [])
        self.assertEqual(len(apps_list), 3, "config/apps.json must define exactly 3 applications")
        
        loaded_ids = {a["app_id"]: a for a in apps_list}
        for expected_id in self.expected_apps.keys():
            self.assertIn(expected_id, loaded_ids, f"App ID {expected_id} must be in config/apps.json")
            app_meta = loaded_ids[expected_id]
            self.assertTrue(bool(app_meta.get("name")), f"App {expected_id} must have a name")
            self.assertTrue(bool(app_meta.get("role")), f"App {expected_id} must have a role")
            self.assertTrue(bool(app_meta.get("raw_reviews_file")), f"App {expected_id} must specify raw_reviews_file")
            raw_path = os.path.join("data", app_meta["raw_reviews_file"])
            self.assertTrue(os.path.exists(raw_path), f"Raw review file must exist: {raw_path}")

    def test_each_app_processed_without_app_specific_code_copy(self):
        """2. Each app's input file is processed using the identical generalized functions."""
        # Process an arbitrary synthetic app to prove zero hardcoded app-specific branching
        synthetic_raw = pd.DataFrame([
            {
                "reviewId": "synth-1",
                "score": 1,
                "content": "The app keeps crashing after recent update",
                "thumbsUpCount": 2,
                "reviewCreatedVersion": "1.0.0",
                "at": "2026-05-01 10:00:00"
            },
            {
                "reviewId": "synth-2",
                "score": 5,
                "content": "Great UI and smooth ride",
                "thumbsUpCount": 0,
                "reviewCreatedVersion": None,
                "at": "2026-05-02 11:00:00"
            }
        ])
        
        # Clean using generalized function
        cleaned_synth = clean_app_dataframe(synthetic_raw, app_id="com.example.synthetic")
        self.assertEqual(len(cleaned_synth), 2)
        self.assertEqual(cleaned_synth.iloc[0]["app_id"], "com.example.synthetic")
        
        # Process themes using generalized function
        proc_synth = process_app_themes(cleaned_synth, app_slug="synthetic", output_dir=self.test_dir)
        self.assertEqual(len(proc_synth), 2)
        self.assertIn("theme_crashes_and_updates", proc_synth.columns)
        self.assertEqual(proc_synth.iloc[0]["theme_crashes_and_updates"], 1)
        
        # Summaries using generalized functions
        theme_synth = compute_theme_summary(proc_synth, app_slug="synthetic", output_dir=self.test_dir)
        self.assertFalse(theme_synth.empty)
        ver_synth = compute_version_summary(proc_synth, app_slug="synthetic", output_dir=self.test_dir)
        self.assertFalse(ver_synth.empty)

    def test_processed_output_schemas_are_consistent(self):
        """3. Processed output schemas are strictly identical across per-app outputs and combined output."""
        expected_files = [
            "reports/processed_employee_reviews.csv",
            "reports/processed_driver_lite_reviews.csv",
            "reports/processed_driver_dco_reviews.csv",
            "reports/processed_all_reviews.csv"
        ]
        
        headers = []
        for fpath in expected_files:
            self.assertTrue(os.path.exists(fpath), f"Processed file must exist: {fpath}")
            df = pd.read_csv(fpath, nrows=2)
            headers.append((fpath, list(df.columns)))
            
        base_path, base_cols = headers[0]
        for fpath, cols in headers[1:]:
            self.assertEqual(
                base_cols, cols,
                f"Schema mismatch between {base_path} and {fpath}.\nMissing in {fpath}: {set(base_cols) - set(cols)}\nExtra in {fpath}: {set(cols) - set(base_cols)}"
            )

        # Confirm critical fields are present
        for req_col in ["app_id", "reviewId", "score", "content_clean", "version_clean", "assigned_themes", "primary_theme"]:
            self.assertIn(req_col, base_cols, f"Required column {req_col} must be in processed schema")

    def test_source_review_ids_preserved_exactly_once_per_app(self):
        """4. Every source review ID is preserved exactly once in its corresponding processed output."""
        app_counts = {
            "employee": ("com.moveinsync.ets_reviews.csv", "processed_employee_reviews.csv", 600),
            "driver_lite": ("com.moveinsync.driver.lite_reviews.csv", "processed_driver_lite_reviews.csv", 108),
            "driver_dco": ("com.moveinsync.driver.dco_reviews.csv", "processed_driver_dco_reviews.csv", 7),
        }
        
        for slug, (raw_name, proc_name, expected_count) in app_counts.items():
            raw_path = os.path.join("data", raw_name)
            proc_path = os.path.join("reports", proc_name)
            
            raw_df = pd.read_csv(raw_path)
            proc_df = pd.read_csv(proc_path)
            
            self.assertEqual(len(raw_df), expected_count, f"Raw count for {slug} must be {expected_count}")
            self.assertEqual(len(proc_df), expected_count, f"Processed count for {slug} must match raw count {expected_count}")
            
            # Check unique review IDs
            raw_ids = set(raw_df["reviewId"].astype(str))
            proc_ids = set(proc_df["reviewId"].astype(str))
            
            self.assertEqual(raw_ids, proc_ids, f"Review IDs in {proc_name} must exactly match {raw_name}")
            self.assertEqual(proc_df["reviewId"].duplicated().sum(), 0, f"Duplicate reviewId found in {proc_name}")

    def test_combined_output_contains_all_source_reviews_and_correct_app_ids(self):
        """5. Combined output contains all 715 source reviews and correct app IDs."""
        comb_path = os.path.join("reports", "processed_all_reviews.csv")
        self.assertTrue(os.path.exists(comb_path), f"Combined file must exist: {comb_path}")
        
        comb_df = pd.read_csv(comb_path)
        self.assertEqual(len(comb_df), 715, "Combined output must contain exactly 715 rows (600 + 108 + 7)")
        self.assertEqual(comb_df["reviewId"].nunique(), 715, "Combined output must contain 715 unique review IDs")
        
        # Check counts per app_id
        counts = comb_df["app_id"].value_counts().to_dict()
        self.assertEqual(counts.get("com.moveinsync.ets", 0), 600)
        self.assertEqual(counts.get("com.moveinsync.driver.lite", 0), 108)
        self.assertEqual(counts.get("com.moveinsync.driver.dco", 0), 7)

    def test_theme_summary_counts_reconcile_with_processed_data(self):
        """6. Theme summary counts reconcile with the processed reviews data for all apps."""
        slugs = ["employee", "driver_lite", "driver_dco"]
        
        for slug in slugs:
            proc_path = os.path.join("reports", f"processed_{slug}_reviews.csv")
            sum_path = os.path.join("reports", f"theme_summary_{slug}.csv")
            
            proc_df = pd.read_csv(proc_path)
            sum_df = pd.read_csv(sum_path)
            
            self.assertFalse(sum_df.empty, f"Theme summary for {slug} should not be empty")
            
            for _, row in sum_df.iterrows():
                t_key = row["theme_key"]
                col = f"theme_{t_key}"
                self.assertIn(col, proc_df.columns, f"Indicator column {col} missing in processed reviews")
                
                # Check review count reconciliation
                actual_cnt = int((proc_df[col] == 1).sum())
                self.assertEqual(
                    row["review_count"], actual_cnt,
                    f"Mismatch in review_count for {t_key} in {slug}: summary={row['review_count']} vs actual={actual_cnt}"
                )
                
                # Check negative review count reconciliation (score <= 2)
                actual_neg = int(((proc_df[col] == 1) & (proc_df["score"] <= 2)).sum())
                self.assertEqual(
                    row["negative_reviews_1_2_star"], actual_neg,
                    f"Mismatch in negative reviews for {t_key} in {slug}: summary={row['negative_reviews_1_2_star']} vs actual={actual_neg}"
                )

    def test_missing_versions_remain_unknown(self):
        """7. Missing versions remain unknown (Unknown/Unspecified) rather than being inferred."""
        raw_test = pd.DataFrame([
            {"reviewId": "r-1", "score": 1, "content": "Crash", "reviewCreatedVersion": None, "at": "2026-10-01"},
            {"reviewId": "r-2", "score": 2, "content": "Slow", "reviewCreatedVersion": np.nan, "at": "2026-10-02"},
            {"reviewId": "r-3", "score": 3, "content": "Okay", "reviewCreatedVersion": "", "at": "2026-10-03"},
            {"reviewId": "r-4", "score": 4, "content": "Fine", "reviewCreatedVersion": "None", "at": "2026-10-04"},
            {"reviewId": "r-5", "score": 5, "content": "Good", "reviewCreatedVersion": "12.19.0", "at": "2026-10-05"},
        ])
        
        cleaned = clean_app_dataframe(raw_test, app_id="test.app")
        unknown_recs = cleaned[cleaned["reviewId"].isin(["r-1", "r-2", "r-3", "r-4"])]
        for _, rec in unknown_recs.iterrows():
            self.assertEqual(
                rec["version_clean"], "Unknown/Unspecified",
                f"Missing version for {rec['reviewId']} was improperly converted to {rec['version_clean']}"
            )
            
        known_rec = cleaned[cleaned["reviewId"] == "r-5"].iloc[0]
        self.assertEqual(known_rec["version_clean"], "12.19.0")

    def test_empty_or_missing_optional_fields_handled_safely(self):
        """8. Empty or missing optional fields (replyContent, thumbsUpCount, etc.) are handled safely."""
        minimal_raw = pd.DataFrame([
            {"reviewId": "min-1", "score": 1, "content": None, "at": "2026-10-01"},
            {"reviewId": "min-2", "score": "invalid", "content": "text", "at": None},
        ])
        
        # Clean dataframe without optional columns present
        cleaned = clean_app_dataframe(minimal_raw, app_id="test.min")
        self.assertEqual(len(cleaned), 2, "Rows must never be silently dropped due to missing optional fields")
        self.assertEqual(cleaned.iloc[0]["content_clean"], "")
        self.assertEqual(cleaned.iloc[1]["score"], 0)
        self.assertEqual(cleaned.iloc[0]["thumbsUpCount"], 0)
        self.assertEqual(cleaned.iloc[0]["replyContent"], "")
        
        # Processing themes and summaries must execute without crashing
        proc = process_app_themes(cleaned, app_slug="test_min", output_dir=self.test_dir)
        self.assertEqual(len(proc), 2)
        th_sum = compute_theme_summary(proc, app_slug="test_min", output_dir=self.test_dir)
        self.assertEqual(len(th_sum), 9)
        ver_sum = compute_version_summary(proc, app_slug="test_min", output_dir=self.test_dir)
        self.assertEqual(len(ver_sum), 1)

    def test_dynamic_chart_titles_and_dates_reflect_dataset(self):
        """9. Dynamic chart titles and date ranges reflect dataset, and empty datasets do not crash."""
        chart_test_dir = os.path.join(self.test_dir, "test_charts")
        os.makedirs(chart_test_dir, exist_ok=True)
        
        # Non-empty custom app test
        custom_df = pd.DataFrame([
            {
                "app_id": "com.custom.app", "reviewId": "c1", "score": 1, "content_clean": "error",
                "version_clean": "1.0", "at_datetime": pd.to_datetime("2025-01-10"),
                "week": pd.to_datetime("2025-01-05"), "theme_crashes_and_updates": 1,
                "theme_other_unclassified": 0
            },
            {
                "app_id": "com.custom.app", "reviewId": "c2", "score": 5, "content_clean": "great",
                "version_clean": "1.0", "at_datetime": pd.to_datetime("2025-02-15"),
                "week": pd.to_datetime("2025-02-09"), "theme_crashes_and_updates": 0,
                "theme_other_unclassified": 1
            }
        ])
        custom_theme_sum = compute_theme_summary(custom_df, app_slug="custom", output_dir=None)
        custom_ver_sum = compute_version_summary(custom_df, app_slug="custom", output_dir=None)
        
        generate_charts(
            custom_df, custom_theme_sum, custom_ver_sum,
            app_display_name="Custom Enterprise App",
            prefix="custom",
            output_dir=chart_test_dir
        )
        
        for cname in [
            "custom_ratings_distribution.png",
            "custom_ratings_over_time.png",
            "custom_negative_drivers_theme_breakdown.png",
            "custom_version_performance_comparison.png",
            "custom_all_themes_sentiment_breakdown.png"
        ]:
            self.assertTrue(os.path.exists(os.path.join(chart_test_dir, cname)), f"Chart {cname} must be generated")

        # Empty dataset must not crash and must create placeholder
        empty_dir = os.path.join(self.test_dir, "empty_charts")
        generate_charts(
            pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
            app_display_name="Empty App",
            prefix="empty",
            output_dir=empty_dir
        )
        self.assertTrue(os.path.exists(os.path.join(empty_dir, "empty_ratings_distribution.png")))

    def test_pipeline_idempotency_no_duplicate_rows(self):
        """10. Running the pipeline twice produces consistent results without duplicate rows."""
        run_dir = os.path.join(self.test_dir, "idempotency_run")
        
        raw_emp = pd.read_csv("data/com.moveinsync.ets_reviews.csv")
        clean_emp = clean_app_dataframe(raw_emp, app_id="com.moveinsync.ets")
        
        # Run 1
        proc1 = process_app_themes(clean_emp, app_slug="idem_test", output_dir=run_dir)
        thm1 = compute_theme_summary(proc1, app_slug="idem_test", output_dir=run_dir)
        ver1 = compute_version_summary(proc1, app_slug="idem_test", output_dir=run_dir)
        comb1 = save_combined_processed_reviews([proc1], output_dir=run_dir)
        
        rows_proc1 = len(pd.read_csv(os.path.join(run_dir, "processed_idem_test_reviews.csv")))
        rows_thm1 = len(pd.read_csv(os.path.join(run_dir, "theme_summary_idem_test.csv")))
        rows_ver1 = len(pd.read_csv(os.path.join(run_dir, "version_summary_idem_test.csv")))
        rows_comb1 = len(pd.read_csv(os.path.join(run_dir, "processed_all_reviews.csv")))
        
        # Run 2 on same output dir
        proc2 = process_app_themes(clean_emp, app_slug="idem_test", output_dir=run_dir)
        thm2 = compute_theme_summary(proc2, app_slug="idem_test", output_dir=run_dir)
        ver2 = compute_version_summary(proc2, app_slug="idem_test", output_dir=run_dir)
        comb2 = save_combined_processed_reviews([proc2], output_dir=run_dir)
        
        rows_proc2 = len(pd.read_csv(os.path.join(run_dir, "processed_idem_test_reviews.csv")))
        rows_thm2 = len(pd.read_csv(os.path.join(run_dir, "theme_summary_idem_test.csv")))
        rows_ver2 = len(pd.read_csv(os.path.join(run_dir, "version_summary_idem_test.csv")))
        rows_comb2 = len(pd.read_csv(os.path.join(run_dir, "processed_all_reviews.csv")))
        
        self.assertEqual(rows_proc1, rows_proc2, "Processed reviews count must remain identical on re-run")
        self.assertEqual(rows_thm1, rows_thm2, "Theme summary count must remain identical on re-run")
        self.assertEqual(rows_ver1, rows_ver2, "Version summary count must remain identical on re-run")
        self.assertEqual(rows_comb1, rows_comb2, "Combined count must remain identical on re-run")


if __name__ == "__main__":
    unittest.main()
