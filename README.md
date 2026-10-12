# MoveInSync Enterprise Review Analysis & Intelligence Platform

An enterprise-grade review ingestion, multi-label theme classification, analytical pipeline, and interactive dashboard for MoveInSync Google Play applications:
- **Employee Transport App**: `com.moveinsync.ets` ($N=600$ reviews)
- **Partner Lite (Driver)**: `com.moveinsync.driver.lite` ($N=108$ reviews)
- **Driver Partner**: `com.moveinsync.driver.dco` ($N=7$ reviews, preliminary sample)

---

## 1. Environment Setup & Installation

### Prerequisites
- Python 3.11 or higher
- Windows / macOS / Linux

### Virtual Environment Setup
```powershell
# Navigate to workspace
cd D:\MOVENSYNC

# Create virtual environment (if not already present)
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install pinned dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 2. Launching the Interactive Dashboard

Launch the Streamlit web dashboard:
```powershell
.\.venv\Scripts\streamlit.exe run dashboard.py
```
Open your browser at `http://localhost:8501`.

### Dashboard Features
- **Multi-App Selection**: Toggle between *All Apps (715 reviews)*, *Employee App*, *Driver Lite*, or *Driver Partner*.
- **Dynamic Filters**: Bounded date range, 1–5 star ratings, app versions (including explicit `Unknown/Unspecified`), and multi-select problem themes.
- **KPI Diagnostic Cards**: Total reviews, average rating, negative feedback rate (1–2★), and top problem theme.
- **Interactive Visualizations (Plotly)**:
  - Rating distribution bar chart with count and percentage annotations.
  - Weekly review volume and star rating trajectory over time.
  - Stacked horizontal bar chart of problem themes split by Negative (1–2★), Neutral (3★), and Positive (4–5★) sentiment.
  - Model quality tab displaying independent holdout classification metrics.
- **Customer Review Explorer**: Full review cards with rating badge, app tag, version, date, thumbs-up count, theme tags, text search, and pagination.
- **Filtered CSV Export**: One-click download button exporting the currently active filtered dataset to CSV.
- **Pipeline Refresh**: Local recomputation button that runs `analyze_reviews.py` safely without querying remote APIs.

---

## 3. Running Automated Tests

Run the full standard-library regression test suite (31 tests across Phases 1, 2, and 4):
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

### Test Suite Structure
- `tests/test_phase1.py`: Configuration loading, JSON schema validation, safe history upsert, and known/unknown version handling (11 tests).
- `tests/test_phase2.py`: Multi-app parity, schema uniformity (29 columns), review ID preservation, and dynamic chart titles (10 tests).
- `tests/test_phase4.py`: Dashboard filtering engine, KPI calculations, empty-result safety, theme mention cardinality, CSV export, and governance limitations (10 tests).

---

## 4. Running the Project Integrity Audit

Run the read-only live project status checker:
```powershell
.\.venv\Scripts\python.exe project_status.py
```
This utility verifies:
- Core scripts and config JSON schemas
- SHA-256 integrity of raw CSV datasets
- Zero duplicates in ratings snapshots and combined reviews
- Generated reports and publication chart counts

---

## 5. Data Pipeline & Recomputation

### Local Analytics Pipeline (Non-destructive)
To re-process raw CSVs, apply multi-label taxonomy rules, compute theme summaries, and regenerate charts:
```powershell
.\.venv\Scripts\python.exe analyze_reviews.py
```
*Note: This operates exclusively from existing local CSVs in `data/` and does not call external APIs.*

### Remote Play Store Scraper (Opt-in)
To fetch new reviews from the Google Play Store via `google-play-scraper`:
```powershell
.\.venv\Scripts\python.exe scrape_reviews.py
```
*Note: Kept strictly opt-in and decoupled from dashboard startup to prevent unprompted network calls.*

---

## 6. Classification Architecture & Model Performance

- **Taxonomy**: 8 core functional themes (`crashes_and_updates`, `booking_and_roster`, `eta_and_tracking`, `login_and_otp`, `notifications`, `ui_and_usability`, `support_and_operations`, `safety_and_permissions`) plus `other_unclassified`. Defined in `config/taxonomy.json`.
- **Independent Holdout Validation ($N=50$, seed `101`)**:
  - **Exact Match Ratio**: `84.0%` (42/50 reviews)
  - **Hamming Loss**: `0.0267` (12 label errors across 450 evaluation slots)
  - **Micro F1-Score**: `0.893`
  - **Macro F1-Score**: `0.722`
  - Zero review overlap with the Phase 1 30-review tuning set.
  - Audited in `reports/holdout_validation_results.csv` and `reports/holdout_metrics_summary.csv`.

---

## 7. Known Data Governance & Methodological Limitations

1. **Ratings History Single-Date Snapshot**:
   - All records in `data/ratings_history.csv` represent a **single-date snapshot (`2026-10-10`)**.
   - No longitudinal time-series trends or historical rating degradation across time can be claimed from `ratings_history.csv`.
   - Store lifetime ratings (Employee: 4.64★, Lite: 4.29★, DCO: 3.50★) are kept strictly separate from review sample averages (Employee: 3.77★, Lite: 3.57★, DCO: 2.71★).
2. **Driver Partner Sample Size**:
   - `com.moveinsync.driver.dco` contains only 7 total public reviews ($N=3$ in holdout sample).
   - Metrics carry high statistical variance and are explicitly designated preliminary in the dashboard.
3. **Multi-Label Cardinality**:
   - Because customer reviews can mention multiple themes simultaneously, the sum of theme mentions across categories exceeds the unique review count. This is mathematically standard under multi-label classification.
4. **Voluntary Response Bias**:
   - Scraped written reviews skew more negative (29.9% 1–2★ combined) than overall Play Store star ratings (7.1% 1–2★ lifetime) due to voluntary response bias.
