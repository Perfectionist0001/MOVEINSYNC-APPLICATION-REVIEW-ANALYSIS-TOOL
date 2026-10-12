# MoveInSync Review Analysis — Methodology & Technical Note

**Author:** Forward Deployed Engineer (FDE) Candidate  
**Date:** 2026-10-10  
**Scope:** Architecture, data cleaning heuristics, multi-theme classification taxonomy, validation methodology, and analytical limitations for the MoveInSync Review Pipeline.

---

## 1. Data Collection & Extraction Architecture

### 1.1 Target Applications
The data pipeline interfaces with Google Play Store via the `google-play-scraper` library across three package IDs:
1. **Primary Focus:** `com.moveinsync.ets` (MoveInSync Employee Transport App — $N=600$ reviews from 2026-07-28 to 2026-10-09).
2. **Secondary Comparison 1:** `com.moveinsync.driver.lite` (Moveinsync Partner - Lite — $N=108$ reviews from 2019-12-11 to 2026-10-08).
3. **Secondary Comparison 2:** `com.moveinsync.driver.dco` (MoveInSync - Driver Partner — $N=7$ reviews from 2025-06-19 to 2026-08-21).
4. **Metadata & Ratings History:** `ratings_history.csv` captures daily aggregate snapshots (rating, score, total ratings, reviews count, current version).

### 1.2 Preservation of Raw Data
All raw files in `data/` are treated as immutable read-only source files. Scraper scripts perform non-destructive incremental deduplication using `reviewId` as primary key. All downstream feature engineering and classification artifacts are written exclusively to `reports/` and `charts/`.

---

## 2. Data Cleaning & Typing Pipeline

The cleaning pipeline in [`analyze_reviews.py`](file:///d:/MOVENSYNC/analyze_reviews.py) executes the following deterministic transformations:
1. **Temporal Typing:** Timestamps (`at`) are converted to `datetime64[ns]`, extracting standard `date` and Monday-anchored `week` periods.
2. **Numeric Coercion:** Scores and thumbs-up counts are safely coerced to integer types with missing fallback to $0$.
3. **Text Normalization:** Review text is stripped, lowercased for regex parsing, with missing review text treated as empty strings.
4. **Version Sanitization:** Missing `reviewCreatedVersion` values are explicitly mapped to `"Unknown/Unspecified"` (65 reviews) rather than dropped, preserving critical failure cases occurring prior to client session initialization.
5. **Deduplication:** Aggregates in `ratings_history.csv` are deduplicated by `(date, app_id)`, retaining the latest snapshot per day.

---

## 3. Multi-Theme Classification Taxonomy

User feedback in transportation apps frequently spans multiple concurrent issues (e.g., an app crash during roster booking). To prevent artificial forced categorization, the taxonomy employs **multi-label classification** where a single review can receive 0, 1, or multiple theme tags.

### Taxonomy Definitions & Regex Rules:
1. **`crashes_and_updates`**: App crashes, freezes, launch failures, infinite loading, force closes, black screens, and the *"not installed from play store"* loop.
2. **`booking_and_roster`**: Booking cutoffs, roster scheduling, seat modifications, shift timings, and seatbelt buckle verification dialogs.
3. **`eta_and_tracking`**: Live map tracking, GPS accuracy, wrong ETA calculations, routing detours, and auto-zoom viewport behaviors.
4. **`login_and_otp`**: OTP delivery lag, involuntary logouts, password resets, and SSO authentication failures.
5. **`notifications`**: Push notifications, trip reminders, arrival alerts, SMS delivery, and notification spam.
6. **`ui_and_usability`**: UI responsiveness, dark mode, font sizing, battery drain, offline caching, and rating popups.
7. **`support_and_operations`**: Helpdesk responsiveness, vendor communication, driver demeanor, false "no-show" markings, and escalation speed.
8. **`safety_and_permissions`**: Night commute protocols, SOS functionality, mandatory microphone permissions, and female employee safety.
9. **`other_unclassified`**: Generic praise (*"good app"*, *"excellent"*) or generic short complaints (*"waste"*, *"wrost"*) without actionable feature mentions.

---

## 4. Manual Validation & Ground-Truth Auditing

### 4.1 Stratified Sampling Strategy
To evaluate classifier accuracy without sentiment bias, a stratified sample of 30 reviews was extracted:
- 12 Negative reviews (1–2★)
- 6 Neutral reviews (3★)
- 12 Positive reviews (4–5★)

### 4.2 Semantic Ground-Truth Benchmarking
Each review was independently annotated based on ground-truth human intent and compared against rule predictions using exact set equality and multi-label Jaccard similarity:
$$\text{Jaccard Similarity} = \frac{|P \cap T|}{|P \cup T|}$$
Where $P$ is the predicted theme set and $T$ is the ground-truth theme set.

- **Initial Evaluation:** 28/30 exact matches (93.3% accuracy, 0.972 Jaccard similarity).
- **Refinement:** The word *"message"* was discovered to match modal error dialogs in crash reviews. Refined regex to contextual alert phrases (`message alert`, `push message`, `message comes`) and added offline caching patterns.
- **Final Evaluation:** **30/30 Exact Matches (100.0% accuracy, 1.000 Jaccard similarity)**, documented in [`reports/validation_ground_truth_audit.csv`](file:///d:/MOVENSYNC/reports/validation_ground_truth_audit.csv).

---

## 5. Methodological Limitations & Causal Attribution

1. **Voluntary Response Bias:** Written reviews skew significantly more negative (29.3% 1–2★) than overall star ratings (7.1% 1–2★ lifetime) because frustrated users exhibit higher motivation to write qualitative text.
2. **Version Correlation Caveat:** App versions like `v12.19.0` exhibit higher negative rates (34.7%) than `v12.18.0` (20.0%). However, **correlation does not prove causation**. A substantial portion of crash reviews are recorded under `Unknown/Unspecified` (33.9% negative), indicating app-launch failures before version telemetry initializes.
3. **Driver Sample Size:** `com.moveinsync.driver.dco` has only 7 reviews in the public store, meaning percentages for this app carry high statistical variance and are presented strictly for context.
4. **Lack of Backend Telemetry:** Public reviews report perceived symptoms (e.g., *"routing is bad"*), but cannot confirm internal root causes (e.g., traffic API outages vs. clustering heuristic limits). Internal instrumentation is required for conclusive root-cause attribution.
