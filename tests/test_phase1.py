"""
Phase 1 Focused Regression Test Suite
Tests:
1. Snapshot upsert deduplication and edge cases (missing file, empty file, atomic write)
2. Configuration loading and validation (valid configs, malformed JSON, missing fields, bad regex)
3. Review-version attribution integrity (missing version -> Unknown/Unspecified)
"""

import json
import os
import shutil
import tempfile
import unittest
import numpy as np
import pandas as pd

from scrape_reviews import save_snapshot_record, SNAPSHOT_COLS
from config_loader import (
    load_apps_config, load_taxonomy_config,
    get_theme_patterns, get_theme_display_names,
    get_priority_order, compile_taxonomy_rules
)
from analyze_reviews import get_quote_with_metadata


class TestSnapshotUpsert(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_history_path = os.path.join(self.test_dir, "test_ratings_history.csv")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_missing_history_file_handled_safely(self):
        """Missing ratings history file must be created safely with standard header and row."""
        self.assertFalse(os.path.exists(self.test_history_path))
        row = {
            "date": "2026-10-12", "app_id": "com.moveinsync.ets",
            "title": "MoveInSync", "score": 4.64, "ratings": 114843, "reviews": 23617,
            "star1": 7341, "star2": 828, "star3": 1232, "star4": 7300, "star5": 98137,
            "version": "12.19.0", "updated": "Oct 8, 2026"
        }
        df_out = save_snapshot_record(row, filepath=self.test_history_path)
        self.assertTrue(os.path.exists(self.test_history_path))
        self.assertEqual(len(df_out), 1)
        self.assertEqual(list(df_out.columns), SNAPSHOT_COLS)

        df_disk = pd.read_csv(self.test_history_path)
        self.assertEqual(len(df_disk), 1)
        self.assertEqual(df_disk.iloc[0]["app_id"], "com.moveinsync.ets")
        self.assertEqual(df_disk.iloc[0]["score"], 4.64)

    def test_empty_history_file_handled_safely(self):
        """Existing 0-byte file must be handled safely without parsing error."""
        with open(self.test_history_path, "w") as f:
            pass  # create 0-byte file
        self.assertEqual(os.path.getsize(self.test_history_path), 0)

        row = {
            "date": "2026-10-12", "app_id": "com.moveinsync.ets",
            "title": "MoveInSync", "score": 4.64, "ratings": 114843, "reviews": 23617,
            "star1": 7341, "star2": 828, "star3": 1232, "star4": 7300, "star5": 98137,
            "version": "12.19.0", "updated": "Oct 8, 2026"
        }
        df_out = save_snapshot_record(row, filepath=self.test_history_path)
        self.assertEqual(len(df_out), 1)
        df_disk = pd.read_csv(self.test_history_path)
        self.assertEqual(len(df_disk), 1)

    def test_rerun_same_date_app_updates_without_duplicate(self):
        """Re-running snapshot for same (date, app_id) must replace the record logically, not duplicate."""
        row1 = {
            "date": "2026-10-12", "app_id": "com.moveinsync.ets",
            "title": "MoveInSync", "score": 4.60, "ratings": 114000, "reviews": 23000,
            "star1": 7000, "star2": 800, "star3": 1200, "star4": 7000, "star5": 98000,
            "version": "12.18.1", "updated": "Oct 1, 2026"
        }
        save_snapshot_record(row1, filepath=self.test_history_path)

        # Re-run same day and same app with updated metrics
        row2 = {
            "date": "2026-10-12", "app_id": "com.moveinsync.ets",
            "title": "MoveInSync", "score": 4.64, "ratings": 114843, "reviews": 23617,
            "star1": 7341, "star2": 828, "star3": 1232, "star4": 7300, "star5": 98137,
            "version": "12.19.0", "updated": "Oct 8, 2026"
        }
        save_snapshot_record(row2, filepath=self.test_history_path)

        df_disk = pd.read_csv(self.test_history_path)
        self.assertEqual(len(df_disk), 1, "Rerunning on same date and app should yield exactly 1 record")
        self.assertEqual(df_disk.iloc[0]["score"], 4.64)
        self.assertEqual(df_disk.iloc[0]["version"], "12.19.0")

    def test_snapshots_for_different_apps_and_dates_remain_separate(self):
        """Snapshots across different apps and dates must all be preserved independently."""
        records = [
            {"date": "2026-10-10", "app_id": "com.moveinsync.ets", "title": "ETS", "score": 4.63},
            {"date": "2026-10-10", "app_id": "com.moveinsync.driver.lite", "title": "Lite", "score": 4.29},
            {"date": "2026-10-11", "app_id": "com.moveinsync.ets", "title": "ETS", "score": 4.64},
            {"date": "2026-10-12", "app_id": "com.moveinsync.driver.dco", "title": "DCO", "score": 3.50},
        ]
        for r in records:
            save_snapshot_record(r, filepath=self.test_history_path)

        df_disk = pd.read_csv(self.test_history_path)
        self.assertEqual(len(df_disk), 4, "4 distinct (date, app_id) combinations must yield 4 rows")

        # Now update only (2026-10-11, com.moveinsync.ets)
        updated_r = {"date": "2026-10-11", "app_id": "com.moveinsync.ets", "title": "ETS", "score": 4.65}
        save_snapshot_record(updated_r, filepath=self.test_history_path)

        df_after = pd.read_csv(self.test_history_path)
        self.assertEqual(len(df_after), 4, "Total row count must remain 4 after upsert")
        matched = df_after[(df_after["date"] == "2026-10-11") & (df_after["app_id"] == "com.moveinsync.ets")]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched.iloc[0]["score"], 4.65)


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_configuration_files_load_correctly(self):
        """Standard project configs config/apps.json and config/taxonomy.json must load and validate."""
        apps_cfg = load_apps_config("config/apps.json")
        self.assertIn("apps", apps_cfg)
        self.assertGreaterEqual(len(apps_cfg["apps"]), 3)

        tax_cfg = load_taxonomy_config("config/taxonomy.json")
        self.assertIn("themes", tax_cfg)
        self.assertIn("crashes_and_updates", tax_cfg["themes"])
        self.assertIn("other_unclassified", tax_cfg["fallback_theme"]["id"])

        rules = compile_taxonomy_rules(tax_cfg)
        self.assertEqual(len(rules), len(tax_cfg["themes"]))
        for theme_id, pattern in rules.items():
            self.assertIsNotNone(pattern)

    def test_invalid_json_produces_useful_error(self):
        """Malformed JSON must raise ValueError with diagnostic message."""
        bad_json_path = os.path.join(self.test_dir, "bad.json")
        with open(bad_json_path, "w") as f:
            f.write("{apps: [invalid json,")

        with self.assertRaises(ValueError) as ctx:
            load_apps_config(bad_json_path)
        self.assertIn("Malformed JSON", str(ctx.exception))

    def test_missing_required_keys_produces_useful_error(self):
        """Config missing required fields must raise ValueError naming the missing fields."""
        incomplete_apps_path = os.path.join(self.test_dir, "incomplete_apps.json")
        with open(incomplete_apps_path, "w") as f:
            json.dump({"apps": [{"app_id": "com.test"}]}, f)  # missing name, role, raw_reviews_file

        with self.assertRaises(ValueError) as ctx:
            load_apps_config(incomplete_apps_path)
        self.assertIn("missing required fields", str(ctx.exception))

    def test_invalid_regex_pattern_produces_useful_error(self):
        """Uncompilable regex in taxonomy config must raise ValueError identifying pattern and theme."""
        bad_tax_path = os.path.join(self.test_dir, "bad_tax.json")
        bad_tax = {
            "themes": {
                "test_theme": {
                    "display_name": "Test",
                    "patterns": [r"[a-z("]  # unclosed parenthesis
                }
            },
            "fallback_theme": {"id": "other", "display_name": "Other"},
            "priority_order": ["test_theme", "other"]
        }
        with open(bad_tax_path, "w") as f:
            json.dump(bad_tax, f)

        with self.assertRaises(ValueError) as ctx:
            load_taxonomy_config(bad_tax_path)
        self.assertIn("Invalid regex pattern", str(ctx.exception))

    def test_missing_file_raises_file_not_found(self):
        """Non-existent config file must raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_apps_config("non_existent_apps_config.json")


class TestReviewVersionAttribution(unittest.TestCase):
    def test_missing_review_version_never_presented_as_known_version(self):
        """A review record with missing/NaN reviewCreatedVersion must be formatted as vUnknown/Unspecified."""
        df = pd.DataFrame([{
            "reviewId": "test-1",
            "content_clean": "whenever i update this app, i am not able to open the app again, I need to uninstall and reinstall again. facing this issue since 3 months",
            "score": 1,
            "version_clean": "Unknown/Unspecified",
            "reviewCreatedVersion": np.nan
        }])

        formatted = get_quote_with_metadata(
            df,
            snippet="whenever i update this app",
            default_quote="fallback",
            default_ver="12.19.0",
            default_score=1
        )
        self.assertIn("(vUnknown/Unspecified, 1★)", formatted)
        self.assertNotIn("v12.19.0", formatted)

    def test_known_version_retains_true_version(self):
        """A review record with known version (e.g. 12.19.0) must display its authentic version."""
        df = pd.DataFrame([{
            "reviewId": "test-2",
            "content_clean": "The routing algorithm is pure genius: it clubs passengers from two different states",
            "score": 1,
            "version_clean": "12.19.0",
            "reviewCreatedVersion": "12.19.0"
        }])

        formatted = get_quote_with_metadata(
            df,
            snippet="The routing algorithm is pure genius",
            default_quote="fallback",
            default_ver="Unknown/Unspecified",
            default_score=1
        )
        self.assertIn("(v12.19.0, 1★)", formatted)


if __name__ == "__main__":
    unittest.main()
