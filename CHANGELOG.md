# MoveInSync Review Analysis — Changelog

All notable changes to this project are documented in this file following the Keep a Changelog standard format.
Historical entries are preserved and future changes are appended chronologically.

## [Phase 7: Deployment Readiness & Portfolio Preparation] — 2026-10-13

### Added
- [`reports/phase7_deployment_readiness.md`](reports/phase7_deployment_readiness.md): Comprehensive pre-deployment audit report evaluating clean environment reproducibility, secret/PII posture, path portability, documented command verifications, and hosting platform compatibility. Deployment recommendation: **READY TO DEPLOY**.

### Verification & Safety
- **Public Repository Security**: Confirmed 0 secrets, API keys, credentials, or personal tokens across all 61 tracked files.
- **Data Privacy (PII)**: Confirmed 0 PII columns (`userName`, `email`, `phone`) across all 23 CSV files.
- **Path Portability**: Confirmed 0 hardcoded absolute Windows paths in Python code; verified platform-independent relative paths and dynamic `sys.executable` child process execution.
- **Dashboard Acceptance Testing**: Verified app selection partitioning, bounded date filtering, 1–5★ filtering, version handling, keyword searching, Plotly chart rendering, empty-slice boundary handling, and RFC-4180 CSV export.
- **Regression Suite**: Full 31-test suite passing cleanly in 4.289s.
- **Live Cloud Verification**: Deployed and independently tested on Streamlit Community Cloud at [`https://moveinsync-application-review-analysis-tool.streamlit.app/`](https://moveinsync-application-review-analysis-tool.streamlit.app/) via automated browser subagent. Verified all 4 application scopes, KPIs, multi-tab Plotly visualizations, holdout metrics ($N=50$), and Driver Partner sample warning.

---

## [Phase 6: Git Initialization & Remote Publication] — 2026-10-13

### Added
- Initialized local Git repository (`git init`) and set default branch to `main`.
- Remote origin configured to `https://github.com/Perfectionist0001/MOVEINSYNC-APPLICATION-REVIEW-ANALYSIS-TOOL.git`.
- Pre-edit backups in [`backups/20261013_010900/`](backups/20261013_010900/).

### Modified
- [`.gitignore`](.gitignore): Added explicit repository exclusions for `backups/` (preventing multimegabyte snapshot commits) and `.agents/` (workspace assistant customizations).
- [`project_status.py`](project_status.py): Updated version control status to report repository origin and branch state.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Updated project tracking to Phase 6 complete with remote repository details.

### Verification & Safety
- **Staging Verification**: 61 reviewed and appropriate files staged for baseline commit (`git add`). Excluded data (`backups/`, `.venv/`, `scratch/`, `.agents/`) verified unstaged.
- **Initial Baseline Commit**: Created root commit `4703fee` (`feat: complete MoveInSync review analysis platform (Phases 0-5)`).
- **Remote Push**: Successfully pushed `main` branch to GitHub remote `origin` (`https://github.com/Perfectionist0001/MOVEINSYNC-APPLICATION-REVIEW-ANALYSIS-TOOL.git`).
- **Regression Testing**: All 31 automated tests passed cleanly in 4.016 seconds.
- **Raw Data Immutability**: All source review CSVs and `ratings_history.csv` retain 100% SHA-256 match.

---

## [Phase 5: Final QA & Release Readiness] — 2026-10-13

### Added
- [`README.md`](README.md): Comprehensive project technical guide covering prerequisites, virtual environment setup, dashboard launching, test execution, pipeline recomputation, opt-in scraping, classification benchmarks, and data governance rules.
- [`.gitignore`](.gitignore): Standardized repository protections excluding virtual environments, python bytecode caches, scratch scripts, IDE files, and temporary artifacts.
- [`reports/final_qa_and_release_readiness_report.md`](reports/final_qa_and_release_readiness_report.md): Final non-destructive release readiness audit evaluating test results, checksums, security checks, dashboard acceptance tests, and limitations. Release recommendation: **READY WITH LIMITATIONS**.
- Pre-edit backups in [`backups/20261013_005800/`](backups/20261013_005800/).

### Modified
- [`project_status.py`](project_status.py): Added verification checks for the Phase 5 QA report and updated the live summary banner to reflect release readiness status.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Updated project milestone tracking to Phase 5 complete with full QA verification evidence.

### Verification & Quality Assurance
- **Automated Regression Testing**: Complete 31-test suite passed cleanly (`11 test_phase1.py` + `10 test_phase2.py` + `10 test_phase4.py`) in 4.129 seconds with 0 failures and 0 errors.
- **Source Data Checksum Verification**: All raw CSV files (`data/com.moveinsync.ets_reviews.csv`, `data/com.moveinsync.driver.lite_reviews.csv`, `data/com.moveinsync.driver.dco_reviews.csv`, `data/ratings_history.csv`) retain 100% matching baseline SHA-256 hashes.
- **Security Audit**: AST and regex scan detected 0 hardcoded credentials, API keys, tokens, or private paths.
- **Data Governance Safeguards**: Confirmed single-date snapshot limitations on `ratings_history.csv` (`2026-10-10`) and preliminary disclosures for Driver Partner ($N=7$) across all reports, documentation, and the dashboard UI.
- **Git Readiness**: Confirmed Git status as uninitialized; recommended baseline commit workflow documented.

---

## [Phase 4: Interactive Dashboard Architecture] — 2026-10-13

### Added
- [`dashboard.py`](dashboard.py): Interactive full-featured Streamlit dashboard powered by Plotly visualizations. Supports dynamic multi-app selection (Employee, Driver Lite, Driver Partner, All Apps), date range filtering, 1–5 star selection, version filtering (including explicit Unknown/Unspecified), multi-theme filtering, review keyword search, sortable review cards with pagination, and filtered CSV export.
- [`dashboard_data.py`](dashboard_data.py): Decoupled, fully unit-testable data transformation and filtering engine. Handles multi-app aggregation, KPI calculations, theme breakdowns, time-series binning, and safe pipeline/scraper subprocess execution without swallowing errors.
- [`requirements.txt`](requirements.txt): Pinned dependency manifest (`streamlit==1.65.0`, `plotly==7.1.0`, `pandas==3.0.6`, `matplotlib==3.11.2`, `google-play-scraper==1.2.7`).
- [`tests/test_phase4.py`](tests/test_phase4.py): Standard-library regression test suite (10 tests) covering all acceptance criteria (filter combinations, KPI calculations, empty results, multi-app aggregation, theme mention vs unique review cardinality, CSV export, unknown version mapping, single-date snapshot governance, driver partner sample size, recompute error handling, and holdout metric agreement).
- Pre-edit backups in [`backups/20261013_004200/`](backups/20261013_004200/).

### Modified
- [`project_status.py`](project_status.py): Added checks for `dashboard.py`, `dashboard_data.py`, and `test_phase4.py`; updated status banner to Phase 4 Complete with live launch and test commands.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Updated project status to Phase 4 Complete with operational dashboard evidence.

### Verification & Quality Assurance
- **Full Test Suite**: All 31 regression tests passed cleanly (`11 test_phase1.py` + `10 test_phase2.py` + `10 test_phase4.py`).
- **Live Local Server**: Successfully launched Streamlit daemon on `http://localhost:8501`.
- **Browser Interaction Verification**: Headless browser subagent verified page load, KPI cards (715 reviews, 3.73★, 29.9% neg), interactive Plotly tabs, rating distribution, theme breakdown, pagination, and download button.
- **Data Integrity**: Raw review CSVs and `data/ratings_history.csv` remained 100% untouched and hash-verified.

---

## [Phase 3: Independent Validation & Findings Reconciliation] — 2026-10-13

### Added
- [`reports/holdout_validation_sample.csv`](reports/holdout_validation_sample.csv): Reproducible, stratified 50-review holdout sample generated with seed `101`, completely separate from the initial 30-review tuning set (35 Employee, 12 Driver Lite, 3 Driver Partner).
- [`reports/holdout_validation_results.csv`](reports/holdout_validation_results.csv): Comprehensive review-by-review multi-label classification evaluation against human ground truth.
- [`reports/holdout_metrics_summary.csv`](reports/holdout_metrics_summary.csv): Full multi-label metrics summary including per-theme Precision, Recall, F1, and Support, alongside multi-label Exact Match Ratio (84.0%), Hamming Loss (0.0267), Micro F1 (0.893), and Macro F1 (0.722).
- [`reports/taxonomy_gap_analysis.csv`](reports/taxonomy_gap_analysis.csv): Audit logging 9 concrete taxonomy boundary instances across 4 categories (Driver App Self-Reference, Commute Shift Phrasing, Driver Onboarding/KYC, Brief Launch Defects) with review IDs, ratings, current/proposed themes, rationale, and expected impact.
- Pre-edit backups in [`backups/20261013_002600/`](backups/20261013_002600/) safeguarding all report files before reconciliation.

### Modified
- [`reports/moveinsync_case_study_report.md`](reports/moveinsync_case_study_report.md): Reconciled historical rounded lifetime ratings to verified database values (5★: 98,137, 4★: 7,300, 3★: 1,232, 2★: 828, 1★: 7,341); aligned theme counts; added data evidence box; reconciled driver benchmarks to 4.29★ and 3.50★; added explicit single-date snapshot disclaimer for `ratings_history.csv`.
- [`reports/final_case_study_report.html`](reports/final_case_study_report.html): Reconciled executive KPI cards, theme breakdown table, and direct qualitative quotes to verified source data.
- [`reports/validation_report.md`](reports/validation_report.md): Updated theme audit table to post-refinement counts; added Section 3B documenting independent 50-review holdout validation and multi-label metrics; corrected driver ratings history snapshot figures.
- [`project_status.py`](project_status.py): Added verification checks for Phase 3 holdout and taxonomy gap artifacts and updated summary banner to Phase 3 complete.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Marked Phase 3 as verified complete; documented holdout metrics and resolved discrepancies.

### Integrity & Quality Assurance
- **Raw CSV Integrity**: All raw CSV files (`data/com.moveinsync.ets_reviews.csv`, `data/com.moveinsync.driver.lite_reviews.csv`, `data/com.moveinsync.driver.dco_reviews.csv`, `data/ratings_history.csv`) verified untouched with 100% SHA-256 match before and after Phase 3.
- **Rule Preservation**: Zero classification regex rules were modified prior to recording initial holdout benchmark results.
- **Test Suite Execution**: Full regression suite (`unittest discover -s tests -p "test_*.py"`) passed cleanly: 21 tests ran, 21 passed, 0 failed, 0 skipped.
- **Scope Discipline**: No Streamlit packages installed; `dashboard.py` deferred to Phase 4.

---

## [Phase 2: Pipeline Generalization & Multi-App Parity] — 2026-10-13

### Added
- [`tests/test_phase2.py`](tests/test_phase2.py): Standard-library regression test suite covering all 10 Phase 2 requirements (dynamic app loading, generalized processing, schema consistency, review ID preservation, combined 715 row reconciliation, theme count reconciliation, unknown version preservation, empty/missing optional field safety, dynamic chart generation, and idempotent re-runs).
- [`reports/processed_driver_lite_reviews.csv`](reports/processed_driver_lite_reviews.csv): Processed dataset for Driver Lite (108 reviews, 29 standard columns).
- [`reports/processed_driver_dco_reviews.csv`](reports/processed_driver_dco_reviews.csv): Processed dataset for Driver Partner (7 reviews, 29 standard columns).
- [`reports/processed_all_reviews.csv`](reports/processed_all_reviews.csv): Combined multi-app processed dataset (715 reviews, explicit `app_id` column, 0 duplicate review IDs).
- [`reports/theme_summary_driver_lite.csv`](reports/theme_summary_driver_lite.csv): Theme metrics for Driver Lite across all 8 taxonomy themes + other_unclassified.
- [`reports/theme_summary_driver_dco.csv`](reports/theme_summary_driver_dco.csv): Theme metrics for Driver Partner with safe zero-denominator handling.
- [`reports/version_summary_driver_lite.csv`](reports/version_summary_driver_lite.csv): Version degradation summary for Driver Lite.
- [`reports/version_summary_driver_dco.csv`](reports/version_summary_driver_dco.csv): Version degradation summary for Driver Partner.
- Dynamic charts generated for Driver Lite and Driver Partner in `charts/` (`driver_lite_*.png` and `driver_dco_*.png`).
- [`backups/20261013_000447/`](backups/20261013_000447): Pre-Phase 2 backups of `analyze_reviews.py`, `config_loader.py`, `config/apps.json`, `config/taxonomy.json`.

### Modified
- [`config/apps.json`](config/apps.json): Added explicit `"slug"` identifiers (`employee`, `driver_lite`, `driver_dco`) for deterministic report file naming.
- [`analyze_reviews.py`](analyze_reviews.py):
  - Refactored pipeline into reusable, generalized functions (`clean_app_dataframe`, `load_all_apps_data`, `process_app_themes`, `compute_theme_summary`, `compute_version_summary`, `save_combined_processed_reviews`, `generate_charts`).
  - Added standard 29-column schema across all processed reviews files, ensuring complete schema consistency.
  - Dynamically computes chart titles, subtitles, date ranges, and axis bounds from dataset metadata; safely renders informational empty charts without crashing on empty or sparse data.
  - Preserved backward-compatible wrappers (`load_and_clean_data`, `process_employee_themes`, `compute_driver_summary`, `run_manual_validation`, `generate_preliminary_findings_markdown`).
- [`project_status.py`](project_status.py): Updated core files list to include `test_phase2.py`, expanded expected reports list to 13 files, and added reporting of combined multi-app dataset rows and unique IDs.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Updated project status to reflect completion and verification of Phase 2.

### Reason for Change
- Eliminate hardcoded application logic and support all three configured applications (`com.moveinsync.ets`, `com.moveinsync.driver.lite`, `com.moveinsync.driver.dco`) through `config/apps.json`.
- Provide complete data parity across employee and driver apps with consistent schemas.
- Ensure all chart titles, date ranges, and metrics are derived dynamically from underlying datasets.

### Tests Executed
- Executed `.\.venv\Scripts\python.exe -m unittest tests/test_phase1.py`: 11/11 tests passed in 0.113s.
- Executed `.\.venv\Scripts\python.exe -m unittest tests/test_phase2.py`: 10/10 tests passed in 3.393s.
- Executed `.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"`: All 21 tests passed in 3.336s.
- Executed `.\.venv\Scripts\python.exe analyze_reviews.py`: Full generalized pipeline executed cleanly; processed 715 reviews across 3 apps.
- Executed `.\.venv\Scripts\python.exe project_status.py`: Verified 13/13 reports present, 715 combined reviews (715 unique IDs, 0 duplicates), 15 PNG charts.

### Data Integrity
- Baseline SHA-256 hashes of all 3 raw review CSVs and `data/ratings_history.csv` verified untouched:
  - `data/com.moveinsync.ets_reviews.csv`: `8470f0eb0f8fc69fab1e8e736067a0a9a976559264dcd4b7d74693804108d3f5` (600 rows)
  - `data/com.moveinsync.driver.lite_reviews.csv`: `099dd476420245466cf37a8a3cad882e9f15a52390d3540489524f3f74212d4b` (108 rows)
  - `data/com.moveinsync.driver.dco_reviews.csv`: `12135541b3ec29e3340f611a7e1f5cf8e5aa2aef9e335dffae5e1df9c8d73013` (7 rows)
  - `data/ratings_history.csv`: `dc0d7bcd5f51d356e43b0aa4b616ccbaa40162be8f3d0ffd41fbde78124c2454` (3 rows)
- All 715 source review records represented exactly once in `reports/processed_all_reviews.csv` with zero duplicate IDs.

### Remaining Known Issues / Open Items
- Git repository remains uninitialized in the workspace.
- Static reports (`moveinsync_case_study_report.md`, `final_case_study_report.html`) still contain historical rounded lifetime counts pending Phase 3 synthesis.
- Dashboard (`dashboard.py`) and Streamlit installation deferred to Phase 4 per project constraints.

---

## [Phase 1b: Controlled Cleanup & Classification Correction] — 2026-10-12

### Added
- [`reports/classification_refinement_audit.csv`](reports/classification_refinement_audit.csv): Full audit trail documenting all 14 changed review classifications across Employee and Driver apps with specific root-cause reasons.
- [`backups/20261012_235125/`](backups/20261012_235125): Pre-edit timestamped backups of `data/ratings_history.csv` and `config/taxonomy.json`.

### Modified
- [`config/taxonomy.json`](config/taxonomy.json):
  - Refined `crashes_and_updates` pattern regexes:
    - Added lookbehind exclusion for negated stuck: `\b(?<!never\s)(?<!never\sget\s)(?<!never\sgets\s)(?<!not\s)stuck\b`.
    - Replaced bare `(un)?install` with explicit `uninstall` and `failed to install` patterns.
    - Replaced bare `update` with targeted defect patterns (`update made it worse`, `after update`, `auto update`, `slow after update`).
  - Successfully eliminated 5 positive false-positive matches (*"real-time update"*, *"never get stuck"*, *"useful updates"*, *"helped to install"*).
  - Reclassified 7 data-latency / ops reviews out of crashes into their appropriate operational buckets.
- [`data/ratings_history.csv`](data/ratings_history.csv):
  - Verified duplicate rows were 100% identical with zero column conflicts.
  - Consolidated file atomically from 4 rows to 3 unique `(date, app_id)` rows (0 duplicates remaining).
- [`project_status.py`](project_status.py): Updated status display to report clean ratings history and applied rule refinements.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Updated project status to reflect completion of Phase 1b.

### Reason for Change
- Eliminate lexical leakage in multi-theme classification where praise reviews were categorized as crashes.
- Consolidate ratings history snapshots into clean, unique primary keys.

### Tests Executed
- Executed `.\.venv\Scripts\python.exe -m unittest tests/test_phase1.py`: 11/11 tests passed in 0.117s.
- Executed `.\.venv\Scripts\python.exe analyze_reviews.py`: Pipeline regenerated clean summary CSVs and charts.
- Executed `.\.venv\Scripts\python.exe project_status.py`: Verified 3 rows, 0 duplicate snapshots, clean taxonomy.

### Data Integrity
- Checksums of raw review files in `data/` recomputed; 100% match with baseline SHA-256 hashes (`ets`: `8470f0eb...`, `lite`: `099dd476...`, `dco`: `12135541...`).
- Ratings history deduplicated safely from 4 to 3 rows.

### Remaining Known Issues
- Git repository not initialized.
- Driver apps deep analysis (theme classification & version aggregations for driver apps) pending Phase 2.

---

## [Phase 1.1: Project Tracking System Initialization] — 2026-10-12

### Added
- [`project_status.py`](project_status.py): Standard-library, read-only status diagnostic tool. Inspects raw CSV row counts, duplicate IDs, snapshot keys, config validity, report status, and git state.
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): Persistent source of truth for project objectives, architecture, test results, verified vs pending items, and phase protocol.
- [`CHANGELOG.md`](CHANGELOG.md): Chronological history of engineering phases.

### Reason for Change
- Provide persistent, reproducible tracking across conversation sessions without relying on volatile chat memory.

### Tests Executed
- Executed `.\.venv\Scripts\python.exe project_status.py`: Clean execution with 0 errors. Verified all checks report live state accurately.
- Executed `.\.venv\Scripts\python.exe -m unittest tests/test_phase1.py`: 11/11 tests passed.

### Data Integrity
- Checksums of all files in `data/` recomputed; 100% match with baseline SHA-256 hashes.

### Remaining Known Issues
- Git repository is not initialized.
- `data/ratings_history.csv` still contains 1 duplicate row pending cleanup approval.
- False-positive rule changes are tested and reported but remain pending approval before committing to `config/taxonomy.json`.

---

## [Phase 1.0: Data Integrity & Configuration Extraction] — 2026-10-12

### Added
- [`config/apps.json`](config/apps.json): Externalized application definitions for Employee and Driver apps.
- [`config/taxonomy.json`](config/taxonomy.json): Externalized regex taxonomy with 8 problem categories, display labels, fallback category, and priority order.
- [`config_loader.py`](config_loader.py): Validation engine for configuration files with diagnostic error messages.
- [`tests/test_phase1.py`](tests/test_phase1.py): Standard-library regression test suite covering snapshot upsert, config loading, and version attribution.
- [`backups/20261012_232226/`](backups/20261012_232226): Pre-edit backup copies of `scrape_reviews.py` and `analyze_reviews.py`.

### Modified
- [`scrape_reviews.py`](scrape_reviews.py):
  - Added `save_snapshot_record(row, filepath)`: Prevents duplicate snapshot accumulation by treating `(date, app_id)` as unique composite key.
  - Implemented safe atomic write using temporary file replacement to prevent file corruption.
  - Preserved backward-compatible CLI interface.
- [`analyze_reviews.py`](analyze_reviews.py):
  - Integrated `config_loader` to load taxonomy dynamically from `config/taxonomy.json`.
  - Added `get_quote_with_metadata()`: Automatically extracts authentic version and rating metadata from records. Corrected misattribution of quote to `v12.19.0`, now correctly rendering `vUnknown/Unspecified`.

### Reason for Change
- Eliminate hardcoded configuration from Python source.
- Resolve rating snapshot duplication bug in scraper.
- Correct factual error in report narrative attribution.
- Establish regression safety before expanding the pipeline.

### Tests Executed
- Executed `.\.venv\Scripts\python.exe -m unittest tests/test_phase1.py`: 11 tests ran in 0.123s, 11 passed (0 failed).
- Executed `.\.venv\Scripts\python.exe analyze_reviews.py`: Full analysis pipeline completed successfully; generated updated summaries and charts.

### Data Integrity
- Baseline SHA-256 hashes recorded before editing.
- Hashes rechecked after pipeline execution: All 4 files in `data/` match baseline SHA-256 hashes bit-for-bit.

### Remaining Known Issues
- `data/ratings_history.csv` retains the historical duplicate from earlier runs (not cleaned in Phase 1 to preserve read-only principle on data files).
- Multi-app deep analysis (themes and version metrics for driver apps) not yet implemented (scheduled for Phase 2).

---

## [Phase 0: Baseline Audit & Exploratory Analysis] — 2026-10-10 to 2026-10-12

### Initial State
- Initial pipeline scripts [`scrape_reviews.py`](scrape_reviews.py) and [`analyze_reviews.py`](analyze_reviews.py).
- Raw data scraped: 600 employee reviews, 108 driver lite reviews, 7 driver partner reviews, 4 rating snapshot rows.
- Static reports generated in `reports/` and static PNG charts in `charts/`.
- 22 engineering discrepancies cataloged in the comprehensive Phase 0 audit.
