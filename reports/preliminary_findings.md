# MoveInSync Review Analysis — Preliminary Findings Report (Phase 2)
**Date:** 2026-10-13
**Dataset Analyzed:** `data/com.moveinsync.ets_reviews.csv` (Employee App)
**Sample Size:** N = 600 reviews (2026-07-28 to 2026-10-09)

---

## 1. Executive Summary & Sample vs. Store Metrics

- **Store All-Time Metrics (Play Store snapshot):** 
  - Overall Rating: **4.64★**
  - Total Lifetime Ratings: **114,843** | Lifetime Written Reviews: **23,617**
  - Lifetime Star Breakdown: 5★ (85.5%), 4★ (6.4%), 3★ (1.1%), 2★ (0.7%), 1★ (6.4%)
- **Scraped Sample Metrics (Recent N=600 reviews):**
  - Sample Average Rating: **3.77★**
  - Positive (4–5★): **409 (68.2%)**
  - Neutral (3★): **15 (2.5%)**
  - Negative (1–2★): **176 (29.3%)**
- **Critical Distinction**: Written reviews skew significantly more negative (29.3% 1–2★) than overall star ratings (7.1% 1–2★ lifetime) due to negative voluntary response bias (users encountering bugs are more compelled to write detailed reviews).

---

## 2. Core Issue Breakdown (Multi-Theme Classification)

Each review can mention multiple themes. Below are the actual counts and negative rates across the 8 core themes:

| Rank | Category / Theme | Total Mentions | 1–2★ Reviews | Negative Share within Theme (%) | Share of All Negative Feedback (%) | Mean Rating (★) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | **Crashes & Update Issues** | 36 | 29 | 80.56% | 16.48% | 1.5★ |
| 2 | **ETA, Route & Live Tracking** | 42 | 27 | 64.29% | 15.34% | 2.38★ |
| 3 | **Support, Driver Behavior & Ops** | 35 | 25 | 71.43% | 14.2% | 2.17★ |
| 4 | **Booking & Roster Scheduling** | 33 | 24 | 72.73% | 13.64% | 2.18★ |
| 5 | **UI, Speed & Usability (incl. Dark Mode)** | 46 | 18 | 39.13% | 10.23% | 3.33★ |
| 6 | **Login, OTP & Authentication** | 26 | 18 | 69.23% | 10.23% | 1.96★ |
| 7 | **Notifications & Alerts** | 10 | 8 | 80.0% | 4.55% | 1.9★ |
| 8 | **Safety, Permissions & Night Commute** | 13 | 7 | 53.85% | 3.98% | 3.0★ |
| - | *Other / Generic (No specific feature)* | 416 | 64 | 15.38% | 36.36% | 4.35★ |

---

## 3. Top Pain Points & Verified Review Quotes

### 1. Crashes, Updates & "Not Installed from Play Store" Loop
- **Impact**: 29 negative reviews (16.48% of all negative feedback).
- **Core Symptoms**: The app displays an erroneous dialog claiming *"the app cannot be opened as it is not installed from play store"*, forcing repetitive uninstall/reinstall cycles.
- **Direct Evidence**:
  > *"after every 2 days getting error of "not installed from play store even though I'm installing from play store". do we have any other store to install? this is pathetic"* (vUnknown/Unspecified, 1★)
  > *"again and again it's getting stopped.. showing that it can't open as it is not downloaded from playstore. in last 3 weeks I uninstall an installed it for 10 times due to the same error"* (vUnknown/Unspecified, 2★)
  > *"whenever i update this app, i am not able to open the app again, I need to uninstall and reinstall again. facing this issue since 3 months"* (vUnknown/Unspecified, 1★)

### 2. ETA Inaccuracy, Route Detours & Live Tracking
- **Impact**: 27 negative reviews.
- **Core Symptoms**: Routing algorithm pooling far-apart employees leading to severe delays; map zooming out automatically during tracking.
- **Direct Evidence**:
  > *"MoveOutSync doesn't plan commutes; it plans cross-country pilgrimages. The ETA is an abstract joke where a 1-hour delay is considered punctual. The routing algorithm is pure genius: it clubs passengers from two different states into one cab at 8 AM, while empty cabs glide right past us. If you want a free Bharat Darshan tour before reaching office, this is it. Coding isn't for everyone-definitely not for the monkeys who built this. Try copying Routematic fools."* (v12.19.0, 1★)
  > *"when we have zoomed in the map to track a vehicle what's the necessity to zoom out and show the ETA"* (v12.16.0, 2★)

### 3. Support, Operations & Driver Misalignment
- **Impact**: 25 negative reviews.
- **Core Symptoms**: False "no-show" markings without driver calling; poor coordination during shift end.
- **Direct Evidence**:
  > *"No concern for female employees at logout time, they won't even call the employee at late night logout before making no show."* (v12.16.0, 1★)

### 4. Safety, Night Logout & Mandatory Permissions
- **Impact**: 7 negative reviews.
- **Core Symptoms**: Compulsory microphone permissions when in-app VoIP calling is not provided; night logout safety protocol gaps.
- **Direct Evidence**:
  > *"Hi Team, The MoveInSync app is forcing users to grant microphone access, even though it does not provide any direct in-app calling feature and all calls are routed through the regular phone dialer. Could you please clarify why microphone permission is mandatory? If it is not essential for the core functionality of the app, please stop forcing users to grant this permission and allow the app to function without it. Greater transparency around permission requirements would be appreciated."* (v12.16.1, 1★)

---

## 4. App Version Performance & Correlation Limitations

| App Version | Sample Size (N) | Mean Rating (★) | 1–2★ Negative % | 4–5★ Positive % | Crash/Update Issue Mentions |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **v12.17.0** | 141 | 3.76★ | 29.79% | 68.09% | 5 (3.55%) |
| **v12.19.0** | 101 | 3.59★ | 34.65% | 65.35% | 11 (10.89%) |
| **v12.18.1** | 94 | 3.9★ | 26.6% | 72.34% | 4 (4.26%) |
| **v12.16.0** | 68 | 3.81★ | 27.94% | 66.18% | 6 (8.82%) |
| **v12.18.0** | 65 | 4.11★ | 20.0% | 78.46% | 0 (0.0%) |
| **vUnknown/Unspecified** | 65 | 3.52★ | 33.85% | 60.0% | 6 (9.23%) |
| **v12.16.1** | 38 | 3.53★ | 34.21% | 60.53% | 3 (7.89%) |
| **v12.15.0** | 7 | 4.43★ | 14.29% | 85.71% | 0 (0.0%) |
| **v12.14.1** | 5 | 3.4★ | 40.0% | 60.0% | 0 (0.0%) |
| **v12.20.0** | 4 | 4.0★ | 25.0% | 75.0% | 0 (0.0%) |
| **v12.11.2** | 2 | 2.5★ | 50.0% | 50.0% | 0 (0.0%) |
| **v11.0.2** | 1 | 2.0★ | 100.0% | 0.0% | 1 (100.0%) |
| **v11.4.34** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v12.1.1** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v11.5.5** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v11.5.21** | 1 | 1.0★ | 100.0% | 0.0% | 0 (0.0%) |
| **v12.12.0** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v12.13.1** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v12.1.2** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v12.10.2** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |
| **v12.4** | 1 | 5.0★ | 0.0% | 100.0% | 0 (0.0%) |

> **Methodological Note on Version Comparison:**
> - Major active versions `v12.16.0`, `v12.17.0`, `v12.18.1`, and `v12.19.0` all exhibit sample sizes > 60 reviews.
> - While `v12.19.0` exhibits a mean score of 3.59★ (34.65% negative rate) compared to `v12.17.0` (3.76★, 29.79% negative rate), **correlation does not prove causation**.
> - Many users reporting "not installed from Play Store" leave reviews under `Unknown/Unspecified` version because the app failed prior to telemetry initialization or during uninstalled state.

---

## 5. Driver Apps Comparison Summary

| App Name | Sample Size (N) | Date Range | Sample Mean Score | 1★ Share (%) | 5★ Share (%) | Negative (1–2★) % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Moveinsync Partner - Lite** | 108 | 2019-12-11 to 2026-10-08 | 3.57★ | 28.7% | 56.48% | 31.48% |
| **MoveInSync - Driver Partner** | 7 | 2025-06-19 to 2026-08-21 | 2.71★ | 57.14% | 42.86% | 57.14% |

- **Key Observation**: The driver app (`com.moveinsync.driver.lite`) has a 31.5% negative rate across its 7-year lifetime sample, primarily driven by GPS battery consumption, OTP validation lag at cab pickup, and trip cancellation penalties.

---

## 6. Classification Validation Sample (Human Verification)
A 30-review stratified validation sample (12 negative, 6 neutral, 12 positive) was inspected:
- **Rule-based Accuracy**: **93.3%** precision across primary tags (28/30 accurately captured main intent; 2 boundary cases with keyword false-triggers).
- **Verified Multi-Label Classifications (Successes)**:
  - *"app stuck all the time unable to schedule pathetic"* (1★) -> Correctly tagged `[crashes_and_updates, booking_and_roster]`.
  - *"This is a third class app which is not at all user friendly for employees... Help desk and vendors are not at all helpful..."* (1★) -> Correctly tagged `[ui_and_usability, support_and_operations]`.
  - *"This app is going from bad to horrible. The seat buckle verification is absolutely horrendous and the OTP keeps disappearing behind the seat belt check..."* (1★) -> Correctly tagged `[booking_and_roster, login_and_otp]`.
- **Observed Classification Errors & Edge Cases (Failures/Limitations)**:
  - **False Positive (Lexical Ambiguity)**: Review `"overall a good app... also the app sometimes refuses to open and displays a message that says the app cannot be opened as it is not installed..."` was tagged as `[crashes_and_updates, notifications]`. The word *"message"* was intended as an on-screen modal dialog rather than a push notification / SMS alert.
  - **Contextual Sarcasm**: Sarcastic praise (e.g. *"The routing algorithm is pure genius: it clubs passengers from two different states..."*) requires domain-specific keywords (`bharat darshan`, `pilgrimage`) to avoid sentiment misclassification.
  - **Uninformative Feedback**: Short reviews like *"wrost"*, *"waste"*, *"not a reliable aap"* contain no feature details and are properly preserved in `other_unclassified` (68.5% of sample) to prevent artificial inflation of specific themes.
