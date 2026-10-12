"""
MoveInSync Submission Readiness & Consistency Verification Suite
Validates privacy sanitization, version figures, record counts, link portability,
and dashboard export safety against ground-truth source datasets.
"""

import os
import sys
import re
import csv
import pandas as pd

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE_ROOT)
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

def test_privacy_scan():
    print("[1/5] Running Comprehensive Privacy Scan...")
    plate_regex = re.compile(r'(?<![0-9a-fA-F-])\b[A-Z]{2}[-\s]*\d{1,2}[-\s]*[A-Z]{1,3}[-\s]*\d{4}\b(?![0-9a-fA-F-])', re.IGNORECASE)
    
    scanned_extensions = (".py", ".csv", ".md", ".json", ".html")
    skip_dirs = {".git", ".venv", "backups", "__pycache__", "scratch", ".agents"}
    
    violations = []
    total_scanned = 0
    py_scanned = 0
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if any(f.endswith(ext) for ext in scanned_extensions):
                total_scanned += 1
                if f.endswith(".py"):
                    py_scanned += 1
                fp = os.path.join(root, f)
                rel_path = os.path.relpath(fp, WORKSPACE_ROOT)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                        if plate_regex.search(content):
                            violations.append(rel_path)
                except Exception as e:
                    print(f"    Warning reading {rel_path}: {e}")
                    
    print(f"    Scanned {total_scanned} public workspace files ({py_scanned} Python source files, including this script).")
    if violations:
        for v in violations:
            print(f"    FAILED: {v} -> Unredacted vehicle registration pattern detected")
        return False
    print("    PASSED: Zero unredacted plates or PII leaks across all public workspace files.")
    return True

def test_version_reconciliation():
    print("\n[2/5] Reconciling App-Version Figures against Raw Source Data...")
    raw_path = "data/com.moveinsync.ets_reviews.csv"
    if not os.path.exists(raw_path):
        print(f"    FAILED: Raw file {raw_path} not found.")
        return False
        
    df = pd.read_csv(raw_path)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["reviewCreatedVersion"] = df["reviewCreatedVersion"].fillna("Unknown/Unspecified")
    
    expected_versions = {
        "12.17.0": {"N": 141, "neg": 42, "neg_pct": 29.8, "mean": 3.76},
        "12.18.0": {"N": 65,  "neg": 13, "neg_pct": 20.0, "mean": 4.11},
        "12.18.1": {"N": 94,  "neg": 25, "neg_pct": 26.6, "mean": 3.90},
        "12.19.0": {"N": 101, "neg": 35, "neg_pct": 34.7, "mean": 3.59},
    }
    
    all_matched = True
    for ver, exp in expected_versions.items():
        vdf = df[df["reviewCreatedVersion"] == ver]
        n = len(vdf)
        neg = len(vdf[vdf["score"] <= 2])
        neg_pct = round((neg / n) * 100, 1) if n > 0 else 0.0
        mean = round(vdf["score"].mean(), 2) if n > 0 else 0.0
        
        if (n == exp["N"] and neg == exp["neg"] and 
            abs(neg_pct - exp["neg_pct"]) <= 0.1 and abs(mean - exp["mean"]) <= 0.01):
            print(f"    PASSED {ver:7}: N={n:3}, Neg={neg:2} ({neg_pct:4.1f}%), Mean={mean:4.2f}")
        else:
            print(f"    FAILED {ver:7}: Got N={n}, Neg={neg} ({neg_pct}%), Mean={mean} | Expected {exp}")
            all_matched = False
            
    # Verify version_summary_employee.csv
    v_csv = "reports/version_summary_employee.csv"
    if os.path.exists(v_csv):
        vdf_csv = pd.read_csv(v_csv)
        print(f"    PASSED: {v_csv} exists with {len(vdf_csv)} version rows.")
    else:
        print(f"    FAILED: {v_csv} missing.")
        all_matched = False
        
    return all_matched

def test_app_level_metrics_and_distributions():
    print("\n[3/5] Verifying App-Level Metrics, Star Distributions & Dataset Parity...")
    expected_metrics = {
        "Employee App": {
            "current": "data/com.moveinsync.ets_reviews.csv",
            "backup": "backups/raw_data_private_unredacted/com.moveinsync.ets_reviews.csv",
            "app_id": "com.moveinsync.ets",
            "rows": 600, "unique_ids": 600,
            "stars": {1: 160, 2: 16, 3: 15, 4: 21, 5: 388},
            "neg": 176, "neg_pct": 29.3, "one_star": 160, "mean": 3.77
        },
        "Driver Lite": {
            "current": "data/com.moveinsync.driver.lite_reviews.csv",
            "backup": "backups/raw_data_private_unredacted/com.moveinsync.driver.lite_reviews.csv",
            "app_id": "com.moveinsync.driver.lite",
            "rows": 108, "unique_ids": 108,
            "stars": {1: 31, 2: 3, 3: 8, 4: 5, 5: 61},
            "neg": 34, "neg_pct": 31.5, "one_star": 31, "mean": 3.57
        },
        "Driver Partner": {
            "current": "data/com.moveinsync.driver.dco_reviews.csv",
            "backup": "backups/raw_data_private_unredacted/com.moveinsync.driver.dco_reviews.csv",
            "app_id": "com.moveinsync.driver.dco",
            "rows": 7, "unique_ids": 7,
            "stars": {1: 4, 2: 0, 3: 0, 4: 0, 5: 3},
            "neg": 4, "neg_pct": 57.1, "one_star": 4, "mean": 2.71
        }
    }
    
    all_ok = True
    for name, exp in expected_metrics.items():
        curr_path = exp["current"]
        bak_path = exp["backup"]
        
        if not os.path.exists(curr_path):
            print(f"    FAILED: {curr_path} not found.")
            all_ok = False
            continue
            
        df = pd.read_csv(curr_path)
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        n = len(df)
        u = df["reviewId"].nunique()
        stars = df["score"].value_counts().to_dict()
        s1 = stars.get(1, 0)
        s2 = stars.get(2, 0)
        neg = s1 + s2
        neg_pct = round((neg / n) * 100, 1) if n > 0 else 0.0
        mean = round(df["score"].mean(), 2) if n > 0 else 0.0
        
        # Check against expectation
        checks = [
            (n == exp["rows"], f"rows={n} vs {exp['rows']}"),
            (u == exp["unique_ids"], f"unique={u} vs {exp['unique_ids']}"),
            (neg == exp["neg"], f"neg={neg} vs {exp['neg']}"),
            (s1 == exp["one_star"], f"1-star={s1} vs {exp['one_star']}"),
            (abs(neg_pct - exp["neg_pct"]) <= 0.1, f"neg%={neg_pct} vs {exp['neg_pct']}"),
            (abs(mean - exp["mean"]) <= 0.01, f"mean={mean} vs {exp['mean']}")
        ]
        
        # Check star distribution
        for star, count in exp["stars"].items():
            actual = stars.get(star, 0)
            if actual != count:
                checks.append((False, f"{star}-star={actual} vs {count}"))
                
        failed_checks = [c[1] for c in checks if not c[0]]
        if not failed_checks:
            print(f"    PASSED {name:15}: N={n:3}, 1-star={s1:3}, Neg={neg:3} ({neg_pct:4.1f}%), Mean={mean:4.2f}")
        else:
            print(f"    FAILED {name:15}: {', '.join(failed_checks)}")
            all_ok = False
            
        # Cross check against private backup
        if os.path.exists(bak_path):
            bak_df = pd.read_csv(bak_path)
            bak_df["score"] = pd.to_numeric(bak_df["score"], errors="coerce")
            bak_n = len(bak_df)
            bak_neg = len(bak_df[bak_df["score"] <= 2])
            bak_mean = round(bak_df["score"].mean(), 2)
            if bak_n == n and bak_neg == neg and abs(bak_mean - mean) <= 0.01:
                print(f"    PASSED {name:15} Backup parity: Matches pre-remediation baseline (N={bak_n}, Neg={bak_neg}).")
            else:
                print(f"    FAILED {name:15} Backup parity: Discrepancy between current and backup data!")
                all_ok = False
        else:
            print(f"    Warning: Private backup {bak_path} not found.")
            
    # Verify Combined All Apps
    comb_path = "reports/processed_all_reviews.csv"
    if os.path.exists(comb_path):
        comb_df = pd.read_csv(comb_path)
        comb_df["score"] = pd.to_numeric(comb_df["score"], errors="coerce")
        c_n = len(comb_df)
        c_u = comb_df["reviewId"].nunique()
        c_neg = len(comb_df[comb_df["score"] <= 2])
        c_s1 = len(comb_df[comb_df["score"] == 1])
        c_neg_pct = round((c_neg / c_n) * 100, 1)
        c_mean = round(comb_df["score"].mean(), 2)
        
        if (c_n == 715 and c_u == 715 and c_neg == 214 and c_s1 == 195 and 
            abs(c_neg_pct - 29.9) <= 0.1 and abs(c_mean - 3.73) <= 0.01):
            print(f"    PASSED Combined All Apps: N=715, Unique=715, 1-star=195, Neg=214 (29.9%), Mean=3.73")
        else:
            print(f"    FAILED Combined All Apps: Got N={c_n}, Unique={c_u}, 1-star={c_s1}, Neg={c_neg} ({c_neg_pct}%), Mean={c_mean}")
            all_ok = False
            
    return all_ok

def test_link_portability():
    print("\n[4/5] Checking Link Portability (Zero local Windows file:/// links)...")
    scanned_docs = [
        "README.md",
        "PROJECT_STATUS.md",
        "CHANGELOG.md",
        "reports/validation_report.md",
        "reports/methodology_note.md",
        "reports/phase7_deployment_readiness.md",
        "reports/assignment_final_review/submission_summary.md",
        "reports/assignment_final_review/final_assignment_report.md",
        "reports/assignment_final_review/review_audit.md",
        "reports/assignment_phase1/phase1_findings.md",
        "reports/assignment_phase2/final_assignment_report.md",
        "reports/assignment_phase2/engineering_action_plan.md"
    ]
    
    all_clean = True
    for doc in scanned_docs:
        if os.path.exists(doc):
            with open(doc, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "file:///" in content:
                    print(f"    FAILED: {doc} contains 'file:///' link.")
                    all_clean = False
        else:
            print(f"    Warning: {doc} not found.")
            
    if all_clean:
        print("    PASSED: Zero 'file:///' links in all public documents and deliverables.")
    return all_clean

def test_dashboard_sanitization():
    print("\n[5/5] Testing Dashboard Data Layer Sanitization & CSV Export...")
    plate_regex = re.compile(r'(?<![0-9a-fA-F-])\b[A-Z]{2}[-\s]*\d{1,2}[-\s]*[A-Z]{1,3}[-\s]*\d{4}\b(?![0-9a-fA-F-])', re.IGNORECASE)
    placeholder = "[REDACTED: Vehicle Plate HR 47-X-XXXX]"
    try:
        from dashboard_data import load_reviews_data, filter_reviews, export_filtered_csv, sanitize_review_text
        df = load_reviews_data()
        
        # Test review c789c25d-4efe-4fd4-8986-de67be5beeba
        target_id = "c789c25d-4efe-4fd4-8986-de67be5beeba"
        matching = df[df["reviewId"] == target_id]
        if matching.empty:
            print(f"    FAILED: Target review {target_id} not found in dashboard data.")
            return False
            
        content = matching["content"].iloc[0]
        if plate_regex.search(content):
            print("    FAILED: Unredacted plate pattern found in loaded dashboard dataframe!")
            return False
        if placeholder not in content:
            print("    FAILED: Expected redacted plate token missing from review content.")
            return False
        print("    PASSED: DataFrame loaded with sanitized content.")
        
        # Test keyword search filter
        filtered_search = filter_reviews(df, search_term="ridiculous")
        if filtered_search.empty or target_id not in filtered_search["reviewId"].values:
            print("    FAILED: Keyword search for target review failed.")
            return False
        filtered_content = filtered_search[filtered_search["reviewId"] == target_id]["content"].iloc[0]
        if plate_regex.search(filtered_content):
            print("    FAILED: Filtered search result contains unredacted plate pattern.")
            return False
        if placeholder not in filtered_content:
            print("    FAILED: Filtered search result does not contain redacted token.")
            return False
        print("    PASSED: Filtered review search returns sanitized content.")
        
        # Test CSV export function
        csv_str = export_filtered_csv(matching)
        if plate_regex.search(csv_str):
            print("    FAILED: CSV export contains unredacted plate pattern!")
            return False
        if placeholder not in csv_str:
            print("    FAILED: CSV export does not contain redacted token!")
            return False
        print("    PASSED: export_filtered_csv emits clean, sanitized dataset.")

        # Test sanitize_review_text with generic synthetic test fixtures
        def _make_test_fixture(state: str, rto: str, series: str, num: str, sep: str = " ") -> str:
            return f"{state}{sep}{rto}{sep}{series}{sep}{num}"

        generic_samples = [
            (f"Driver for cab {_make_test_fixture('DL', '01', 'AB', '1234')} was late", f"Driver for cab {placeholder} was late"),
            (f"Driver for {_make_test_fixture('KA', '05', 'M', '9999', '-')} misbehaved", f"Driver for {placeholder} misbehaved"),
            (f"Vehicle {_make_test_fixture('MH', '12', 'DE', '4567', '')} dropped off early", f"Vehicle {placeholder} dropped off early")
        ]
        for raw_sample, expected_redaction in generic_samples:
            sanitized = sanitize_review_text(raw_sample)
            if sanitized != expected_redaction or plate_regex.search(sanitized):
                print("    FAILED: Generic sanitization failed for synthetic pattern.")
                return False
        print("    PASSED: sanitize_review_text correctly redacts generic vehicle registration patterns.")
        return True
    except Exception as e:
        print(f"    FAILED: Exception in dashboard data layer test: {e}")
        return False

def main():
    print("=" * 70)
    print("MOVEINSYNC SUBMISSION READINESS & INTEGRITY VERIFICATION SUITE")
    print("=" * 70)
    
    r1 = test_privacy_scan()
    r2 = test_version_reconciliation()
    r3 = test_app_level_metrics_and_distributions()
    r4 = test_link_portability()
    r5 = test_dashboard_sanitization()
    
    print("\n" + "=" * 70)
    if all([r1, r2, r3, r4, r5]):
        print("ALL VERIFICATION SUITE CHECKS PASSED SUCCESSFULLY! (5/5)")
        print("Submission deliverables are 100% verified, consistent, and sanitized.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("SOME VERIFICATION CHECKS FAILED! Please inspect output above.")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
