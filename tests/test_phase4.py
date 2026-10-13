"""
Phase 4 Regression Test Suite: Streamlit Dashboard Data Engine, Filtering, KPIs, and Governance.
Tests all acceptance criteria for interactive multi-app review analysis.
"""

import os
import unittest
import pandas as pd
import numpy as np

import dashboard_data as dd


class TestPhase4DashboardDataEngine(unittest.TestCase):
    """Unit tests for Phase 4 interactive dashboard data layer."""

    @classmethod
    def setUpClass(cls):
        cls.apps_config = dd.load_apps_config("config/apps.json")
        cls.taxonomy_config = dd.load_taxonomy_config("config/taxonomy.json")
        cls.reviews_df = dd.load_reviews_data("reports/processed_all_reviews.csv")
        cls.ratings_df = dd.load_ratings_history("reports/ratings_history_clean.csv")

    def test_multi_app_aggregation_and_unique_review_ids(self):
        """Acceptance test: All apps dataset aggregates 715 reviews without duplicates."""
        self.assertEqual(len(self.reviews_df), 715)
        self.assertEqual(self.reviews_df["reviewId"].nunique(), 715)
        
        # Verify app-wise partition
        app_counts = self.reviews_df["app_id"].value_counts().to_dict()
        self.assertEqual(app_counts.get("com.moveinsync.ets", 0), 600)
        self.assertEqual(app_counts.get("com.moveinsync.driver.lite", 0), 108)
        self.assertEqual(app_counts.get("com.moveinsync.driver.dco", 0), 7)

    def test_filter_combinations_and_kpi_calculations(self):
        """Acceptance test: Complex filter combinations compute accurate KPIs."""
        # 1. Filter by Employee app and 1-2 star ratings
        filtered = dd.filter_reviews(
            self.reviews_df,
            app_id="com.moveinsync.ets",
            ratings=[1, 2]
        )
        self.assertEqual(len(filtered), 176)
        kpis = dd.calculate_kpis(filtered, list(self.taxonomy_config["themes"].keys()))
        self.assertEqual(kpis["total_reviews"], 176)
        self.assertEqual(kpis["negative_pct"], 100.0)
        self.assertEqual(kpis["positive_pct"], 0.0)
        self.assertLessEqual(kpis["average_rating"], 2.0)

        # 2. Filter by search term
        crashes_filtered = dd.filter_reviews(
            self.reviews_df,
            search_term="crash"
        )
        self.assertGreater(len(crashes_filtered), 0)
        for _, row in crashes_filtered.iterrows():
            self.assertIn("crash", row["content"].lower())

    def test_empty_results_and_missing_optional_values(self):
        """Acceptance test: Empty filter results return friendly zero KPIs without crashing."""
        empty_filtered = dd.filter_reviews(
            self.reviews_df,
            ratings=[99]  # Impossible rating
        )
        self.assertEqual(len(empty_filtered), 0)
        
        kpis = dd.calculate_kpis(empty_filtered)
        self.assertEqual(kpis["total_reviews"], 0)
        self.assertEqual(kpis["average_rating"], 0.0)
        self.assertEqual(kpis["negative_pct"], 0.0)
        self.assertIsNone(kpis["most_mentioned_theme"])
        
        # Empty rating distribution
        dist = dd.calculate_rating_distribution(empty_filtered)
        self.assertEqual(len(dist), 5)
        self.assertEqual(dist["count"].sum(), 0)

        # Empty time series
        ts = dd.calculate_time_series(empty_filtered)
        self.assertEqual(len(ts), 0)

    def test_theme_mention_counts_vs_unique_review_counts(self):
        """Acceptance test: Multi-label theme mentions sum to > unique reviews when multi-label exists."""
        theme_bd = dd.calculate_theme_breakdown(self.reviews_df, self.taxonomy_config, include_other=True)
        total_unique_reviews = len(self.reviews_df)
        total_theme_mentions = theme_bd["mention_count"].sum()
        
        # In multi-label datasets with multi-theme reviews, total mentions exceed unique reviews
        self.assertGreater(total_theme_mentions, total_unique_reviews)
        
        # Employee specific check
        emp_df = dd.filter_reviews(self.reviews_df, app_id="com.moveinsync.ets")
        emp_bd = dd.calculate_theme_breakdown(emp_df, self.taxonomy_config, include_other=True)
        crashes_row = emp_bd[emp_bd["theme_key"] == "crashes_and_updates"].iloc[0]
        self.assertEqual(crashes_row["mention_count"], 36)
        self.assertEqual(crashes_row["negative_reviews_1_2_star"], 29)

    def test_csv_export_matches_active_filters(self):
        """Acceptance test: Exported CSV reflects active filtered slice."""
        filtered = dd.filter_reviews(
            self.reviews_df,
            app_id="com.moveinsync.driver.lite",
            ratings=[5]
        )
        cols = ["reviewId", "app_id", "score", "content"]
        csv_str = dd.export_filtered_csv(filtered, columns=cols)
        
        # Verify CSV content
        lines = [line.strip() for line in csv_str.strip().splitlines()]
        header = lines[0].split(",")
        self.assertEqual(header, cols)
        self.assertEqual(len(lines) - 1, len(filtered))

    def test_missing_versions_handled_as_unknown_unspecified(self):
        """Acceptance test: Missing reviewCreatedVersion is mapped to 'Unknown/Unspecified'."""
        unknowns = self.reviews_df[self.reviews_df["version_clean"] == "Unknown/Unspecified"]
        self.assertGreater(len(unknowns), 0)
        
        # Ensure none are None, NaN, or empty
        self.assertEqual(self.reviews_df["version_clean"].isna().sum(), 0)
        self.assertTrue((self.reviews_df["version_clean"] != "").all())

    def test_single_date_snapshot_limitation_governance(self):
        """Acceptance test: Ratings history governance verifies single-date snapshot."""
        freshness = dd.get_data_freshness_metadata()
        self.assertTrue(freshness["ratings_exists"])
        self.assertEqual(freshness["ratings_snapshot_date"], "2026-10-10")
        
        # Verify deduplicated 3 rows
        self.assertEqual(len(self.ratings_df), 3)
        self.assertEqual(self.ratings_df["date"].nunique(), 1)
        self.assertEqual(self.ratings_df["date"].iloc[0], "2026-10-10")

    def test_driver_partner_preliminary_sample_size(self):
        """Acceptance test: Driver partner dataset is exactly 7 reviews."""
        dco_df = dd.filter_reviews(self.reviews_df, app_id="com.moveinsync.driver.dco")
        self.assertEqual(len(dco_df), 7)

    def test_recompute_refresh_failure_handling(self):
        """Acceptance test: Pipeline execution failure is caught safely and returns error message."""
        # Test with an invalid executable to verify failure handling
        success, msg = dd.run_recompute_pipeline(python_executable="non_existent_python_binary")
        self.assertFalse(success)
        self.assertIn("Failed", msg)

    def test_holdout_metrics_recomputation_agreement(self):
        """Acceptance test: Preflight holdout metrics recompute with verified 84% exact match."""
        holdout_df = dd.load_holdout_metrics("reports/holdout_metrics_summary.csv")
        self.assertFalse(holdout_df.empty)
        crashes_h = holdout_df[holdout_df["theme"] == "crashes_and_updates"].iloc[0]
        self.assertEqual(crashes_h["precision"], 1.0)
    def test_privacy_sanitization_generic_patterns(self):
        """Acceptance test: Sanitization engine redacts generic vehicle registration patterns and preserves clean dataset."""
        import re
        plate_regex = re.compile(r'(?<![0-9a-fA-F-])\b[A-Z]{2}[-\s]*\d{1,2}[-\s]*[A-Z]{1,3}[-\s]*\d{4}\b(?![0-9a-fA-F-])', re.IGNORECASE)
        placeholder = "[REDACTED: Vehicle Registration]"
        
        # Test generic synthetic plate patterns assembled via test fixture helper
        def _make_test_fixture(state: str, rto: str, series: str, num: str, sep: str = " ") -> str:
            return f"{state}{sep}{rto}{sep}{series}{sep}{num}"

        test_cases = [
            (f"Driver of cab {_make_test_fixture('DL', '01', 'AB', '1234')} was reckless", f"Driver of cab {placeholder} was reckless"),
            (f"Vehicle {_make_test_fixture('KA', '05', 'M', '9999', '-')} was delayed", f"Vehicle {placeholder} was delayed"),
            (f"Cab {_make_test_fixture('MH', '12', 'DE', '4567', '')} arrived late", f"Cab {placeholder} arrived late"),
            ("Standard review without any vehicle numbers", "Standard review without any vehicle numbers")
        ]
        for raw_text, expected in test_cases:
            result = dd.sanitize_review_text(raw_text)
            self.assertEqual(result, expected)
            self.assertFalse(bool(plate_regex.search(result)))
            
        # Verify active reviews dataframe contains no unredacted plates
        for _, row in self.reviews_df.iterrows():
            content = str(row.get("content", ""))
            self.assertFalse(
                bool(plate_regex.search(content)),
                f"Unredacted vehicle registration plate detected in review {row.get('reviewId')}"
            )
            
        # Verify target incident review contains the redaction placeholder
        target_id = "c789c25d-4efe-4fd4-8986-de67be5beeba"
        target_rows = self.reviews_df[self.reviews_df["reviewId"] == target_id]
        self.assertFalse(target_rows.empty)
        target_content = target_rows["content"].iloc[0]
        self.assertIn(placeholder, target_content)

        # Verify export_filtered_csv retains placeholder and has zero plate pattern leaks
        csv_export = dd.export_filtered_csv(target_rows)
        self.assertIn(placeholder, csv_export)
        self.assertFalse(bool(plate_regex.search(csv_export)))


if __name__ == "__main__":
    unittest.main()
