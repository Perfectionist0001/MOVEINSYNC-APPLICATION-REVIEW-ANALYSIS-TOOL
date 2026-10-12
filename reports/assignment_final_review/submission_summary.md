# MoveInSync Review Intelligence & Strategic Engineering Roadmap
## Forward Deployed Engineer Candidate Assignment — Executive Submission Briefing

**Candidate:** Forward Deployed Engineer (FDE)  
**Workspace:** `D:\MOVENSYNC`  
**GitHub Repository:** [MOVEINSYNC-APPLICATION-REVIEW-ANALYSIS-TOOL](https://github.com/Perfectionist0001/MOVEINSYNC-APPLICATION-REVIEW-ANALYSIS-TOOL)  
**Live Deployed Dashboard:** [Streamlit Cloud Deployment](https://moveinsync-application-review-analysis-tool.streamlit.app/)  
**Detailed Report:** [final_assignment_report.md](final_assignment_report.md) | **Audit:** [review_audit.md](review_audit.md)  
**Date:** October 13, 2026  

---

## 1. Executive Summary

This executive briefing presents an evidence-based diagnosis of customer and fleet partner feedback across MoveInSync's Google Play mobile ecosystem: **MoveInSync Employee** (`com.moveinsync.ets`), **Driver Lite** (`com.moveinsync.driver.lite`), and **Driver Partner DCO** (`com.moveinsync.driver.dco`).

The objective is to explain **why MoveInSync's app store ratings are lower than expected**, rank the core operational failure drivers, establish a credible Day-1 forward deployed engineering plan, and provide a disciplined 30-day implementation roadmap.

### Headline Discoveries:
1. **Public Review Sentiment Skews Acutely Negative**: While lifetime Play Store aggregate scores appear strong (4.64★ Employee, 4.29★ Driver Lite), written public reviews skew sharply negative: **29.9% (214 of 715 reviews) are 1–2 stars**, with 1-star reviews alone accounting for **27.3% (195 reviews)**. Commuters and drivers write reviews primarily when physical transit breaks down.
2. **Prioritized Problem Ranking**:
   - **Rank #1 (P0) — Commuter Safety & Driver Misconduct**: 23 negative reviews cite abusive conduct, female employees dropped before authorized locations, and unreachable transport desks. Physical safety carries catastrophic corporate liability, employee vulnerability, and client attrition risk, placing it at top priority.
   - **Rank #2 (P1) — Telematics & Live Tracking Stagnation**: 26 negative reviews report frozen cab icons ("teleporting" cabs) and internal ETAs underestimating travel times by up to 3x compared to Google Maps.
   - **Rank #3 (P1) — Dispatch Latency & Multi-Stop Detours**: 27 negative reviews (largest single complaint category) cite last-minute allocations and multi-stop pooling circuits turning 30-minute rides into two-hour journeys.
   - **Rank #4 (P2) — Authentication Lockout & OTP Non-Delivery**: 19 negative reviews report complete inability to receive SMS or email login verification codes.
   - **Rank #5 (P2) — App Crashes & Play Integrity Verification**: 14 negative reviews (100% 1-star) report reproducible cold-start crashes on Vivo devices and spurious installation check errors blocking legitimate users.
3. **Analytical & Governance Standards**:
   - **6-Layer Diagnostic Separation**: Every finding strictly distinguishes *Observed Evidence* $\rightarrow$ *User Symptoms* $\rightarrow$ *Root-Cause Hypotheses* $\rightarrow$ *Recommended Investigations* $\rightarrow$ *Conditional Fixes* $\rightarrow$ *Provisional Metrics*.
   - **Conditional Technical Solutions**: No code fix is assumed blindly; all engineering fixes are conditional upon telemetry verification (e.g., investigating background GPS ping frequencies before modifying background services).
   - **Human-in-the-Loop Safety Governance**: We reject arbitrary automated driver rating bans (<4.2★) or unvetted dispatch rules. We propose rapid safety triage SLAs (<3 min operator response), documented human inquiries, and policy-based safeguards.
   - **Privacy Remediation**: Vehicle registration plates have been sanitized to `[REDACTED: Vehicle Plate HR 47-X-XXXX]` across the current repository. Note: This identifier was previously committed to public Git history; deleting it from the active tree sanitizes future releases but does not rewrite historic Git commits.

---

## 2. Key Evidence & Critical Data Limitations

### 2.1 Dataset Inventory & Verification
Verified from raw CSV source data:
- **Employee App (`com.moveinsync.ets`)**: 600 reviews | 176 negative (29.3%) | 160 1-star, 16 2-star | Mean 3.77★ | Date range: 2026-07-28 to 2026-10-09 (74 days).
- **Driver Lite (`com.moveinsync.driver.lite`)**: 108 reviews | 34 negative (31.5%) | 31 1-star, 3 2-star | Mean 3.57★ | Date range: 2019-12-11 to 2026-10-08 (~7 years).
- **Driver Partner (`com.moveinsync.driver.dco`)**: 7 reviews | 4 negative (57.1%) | 4 1-star | Mean 2.71★ | Date range: 2025-06-19 to 2026-08-21 (14 months).
- **Combined Ecosystem**: 715 unique reviews | 214 negative (29.9%) | 195 1-star, 19 2-star | Mean 3.73★.

### 2.2 Verified Employee App Version Figures
Verified directly against raw `reviewCreatedVersion` data:
- **`12.17.0`**: N=141 | 42 negative (29.8%) | 96 positive (68.1%) | 3 neutral (2.1%) | Mean 3.76★
- **`12.18.0`**: N=65 | 13 negative (20.0%) | 51 positive (78.5%) | 1 neutral (1.5%) | Mean 4.11★
- **`12.18.1`**: N=94 | 25 negative (26.6%) | 68 positive (72.3%) | 1 neutral (1.1%) | Mean 3.90★
- **`12.19.0`**: N=101 | 35 negative (34.7%) | 66 positive (65.3%) | 0 neutral (0.0%) | Mean 3.59★
- **`12.16.0`**: N=68 | 19 negative (27.9%) | 45 positive (66.2%) | 4 neutral (5.9%) | Mean 3.81★
- **`Unknown/Unspecified`**: N=65 | 22 negative (33.8%) | 39 positive (60.0%) | 4 neutral (6.2%) | Mean 3.52★

*Version Trend Observation*: Release `12.19.0` exhibited the highest negative review rate (34.7%, mean 3.59★ vs. 20.0% in `12.18.0`), correlating with user reports of startup crashes on select devices and spurious installation integrity check warnings. However, correlation does not prove software causality without Crashlytics traces and server logs.

### 2.3 Taxonomy Reconciliation: Automated Classification vs. Manual Curated Clusters
- **Automated Multi-Label Theme Taxonomy** (Rule-based keyword regex on 715 reviews):
  Crashes/Updates: 32 neg (15.0%) | Support/Ops: 29 neg (13.6%) | ETA/Tracking: 27 neg (12.6%) | Booking/Roster: 24 neg (11.2%) | Login/OTP: 21 neg (9.8%) | UI/Usability: 18 neg (8.4%) | Safety/Permissions: 8 neg (3.7%) | Notifications: 8 neg (3.7%) | Other Unclassified: 91 neg (42.5%).
- **Reconciliation of the Safety Discrepancy (8 Automated vs. 23 Manual Cluster Reviews)**:
  The automated regex for `safety_and_permissions` searched strictly for literal tokens (`safety`, `sos`, `emergency`, `female`, `permission`), matching only 8 negative reviews. Manual qualitative triage identified **23 distinct negative reviews** describing physical safety vulnerabilities, driver abusive misconduct, off-location drop-offs, and escort failures. Reviews like `c789c25d...` (*"misbehaved with girl employee. dropped before location"*) used colloquial language that regex routed to `support_and_operations` (matching "driver") or left unclassified. Manual curation unifies all physical safety and conduct issues into **Issue 1 (P0)** to reflect real-world enterprise liability.
- **Other Curated Clusters**: Tracking lag (26 reviews) is separated from pooling detour fatigue (27 reviews); OTP lockouts (19 reviews) are isolated from general login friction; startup crashes (14 reviews) are isolated from general update complaints.

### 2.4 Data Limitations & Boundaries
1. **Ratings History Single Snapshot (`2026-10-10`)**: `data/ratings_history.csv` contains only 3 records from `2026-10-10`. It does NOT support historical trend or time-decay modeling.
2. **Driver Partner Sample Size ($N=7$)**: Findings for `com.moveinsync.driver.dco` are strictly qualitative indicators and cannot support statistical generalizations.
3. **Absence of Internal Telemetry**: Public review text reveals user symptoms; internal telemetry, carrier delivery receipts, and dispatch logs are necessary to validate root causes before production deployments.

---

## 3. Prioritized Problems & Why They Matter

Prioritized via multi-criteria scoring: $\text{Score} = (F \times 0.25) + (S \times 0.35) + (U \times 0.25) + (C \times 0.15)$.

```
+----+-------------------------------------------------------+----------+-------+-------------------+
|Rank| Issue Title                                           | Priority | Score | Negative Reviews  |
+----+-------------------------------------------------------+----------+-------+-------------------+
| #1 | Driver Misconduct, Premature Drops & Safety Protocols |    P0    | 4.65  | 23 / 214 (10.7%)  |
| #2 | Live GPS Tracking Stagnation & Inaccurate ETAs        |    P1    | 4.60  | 26 / 214 (12.1%)  |
| #3 | Dispatch Latency, Unpunctuality & Multi-Stop Detours  |    P1    | 4.38  | 27 / 214 (12.6%)  |
| #4 | Authentication Lockout & OTP Non-Delivery             |    P2    | 4.18  | 19 / 214 (8.9%)   |
| #5 | Client Launch Crashes & Spurious Play Store Errors    |    P2    | 3.88  | 14 / 214 (6.5%)   |
+----+-------------------------------------------------------+----------+-------+-------------------+
```

### Problem 1 (P0): Driver Misconduct, Premature Drop-Offs & Commuter Safety Protocols
- **Observed Review Evidence**: 23 negative reviews (22 1-star, 1 2-star).  
  *Excerpt (`c789c25d...`, v12.17.0)*: *"Driver for cab number [REDACTED: Vehicle Plate HR 47-X-XXXX] is ridiculous.dont hire people with no manners .misbehaved with girl employee. dropped before location. Please escalate it further."*  
  *Excerpt (`fb887543...`, v12.18.1)*: *"Why does the company keep assigning rude, disrespectful, and abusive cab drivers? Is there no proper quality check or background verification done?"*
- **User Symptom**: Passenger vulnerability, fear, stranded commuters, unreachable transport helpdesks.
- **Root-Cause Hypothesis**: Unvetted third-party vendor drivers; Driver Lite allows manual trip termination outside destination geofences; SOS alerts route to asynchronous ticketing queues.
- **Recommended Investigation (Phase A)**: Joint triage with Fleet Safety Operations; audit trip telematics for incident review `c789c25d...`; audit 60-day safety ticket queue and telephony connection logs.
- **Conditional Technical / Policy Fix (Phase B)**:
  1. *Policy-Based Human Inquiry*: Mandatory same-day documented inquiry by Fleet Safety Managers, with provisional roster reassignment pending human review (avoiding arbitrary automated rating-based bans).
  2. *Geofenced Drop-off Verification*: Prompt driver if trip termination is attempted >100m outside destination geofence, requiring passenger confirmation code or recorded dispatch override.
  3. *Priority SOS Voice Bridge*: Connect in-app SOS triggers directly to an automated outbound telephony bridge with guaranteed human operator callback.
- **Provisional Metric**: Safety Incident First-Response Time < 3 minutes (p95); Geofenced Drop-off Compliance > 98%.

### Problem 2 (P1): Live GPS Tracking Stagnation, Map Freezes & Inaccurate "Teleporting" ETAs
- **Observed Review Evidence**: 26 negative reviews (25 1-star, 1 2-star).  
  *Excerpt (`7a6441a0...`, v12.18.1)*: *"Can't do live tracking or live boarding activities. suddenly it shows up at your location. You guys loved surprises huh??!!! Ridiculous..."*  
  *Excerpt (`2ce14584...`, v12.19.0)*: *"ETA calculator very bad... google maps always shows 3x the time shown in moveinsync app."*
- **User Symptom**: Passenger anxiety, missed cabs, sudden unannounced arrivals, false ETA promises.
- **Root-Cause Hypothesis**: OEM battery management (Android Doze mode on Xiaomi, Vivo, Samsung) throttles Driver Lite background location broadcasts; WebSocket connection drops silently; static speed routing models.
- **Recommended Investigation (Phase A)**: Request 24h anonymized Driver Lite heartbeat timestamp logs across OEMs; evaluate WebSocket drop/reconnect error logs; compare internal ETA vs Google Maps across 5,000 trips.
- **Conditional Technical Fix (Phase B)**:
  1. *Driver Lite Foreground Service*: If background throttling is confirmed, harden Foreground Service with explicit battery optimization guidance.
  2. *Client Stale Telemetry Warning*: If location update is unreceived for >45s, display warning chip: *"Reconnecting to cab... Last updated 1m ago"*, eliminating frozen icons in false real-time.
  3. *Dynamic Traffic Calibration*: Integrate live traffic speed matrices into peak-hour ETA modeling.
- **Provisional Metric**: GPS Ping Freshness p95 latency < 15s; Stale UI Warning Availability 100%; ETA MAE < 5 minutes.

### Problem 3 (P1): Vehicle Assignment Latency, Pickup Unpunctuality & Multi-Stop Detours
- **Observed Review Evidence**: 27 negative reviews (24 1-star, 3 2-star). Largest single complaint category.  
  *Excerpt (`7476b129...`, v12.19.0)*: *"MoveOutSync doesn't plan commutes; it plans cross-country pilgrimages. The ETA is an abstract joke where a 1-hour delay is considered punctual. The routes make you tour the entire city before dropping you home."*  
  *Excerpt (`1239e342...`, v12.18.0)*: *"When trying to reach helpdesk, the line disconnects. Cab ETA keeps changing and the worst part is routing & pickup timings, spending over 2 hours to reach office."*
- **User Symptom**: Shift absenteeism penalties, prolonged commuter exhaustion, unpredictable daily schedules.
- **Root-Cause Hypothesis**: Routing engine maximizes pooling occupancy over individual travel time; dispatch notifications fire too close to pickup (~15m prior); fleet supply bottlenecks.
- **Recommended Investigation (Phase A)**: Extract planned vs. actual trip durations across peak shifts (07:00–09:00 and 19:00–21:00) over past 14 days; run solver simulations on detour trade-offs.
- **Conditional Technical Fix (Phase B)**:
  1. *Policy-Calibrated Detour Cap*: Implement routing constraint capping shared commute travel time at max **1.5x of direct route duration**.
  2. *Advance Assignment Notification*: Advance vehicle allocation notifications from ~15m to **30–45 minutes prior to pickup** where fleet supply permits.
  3. *Dynamic Congestion Buffering*: Inject automatic traffic buffers on high-delay commute corridors.
- **Provisional Metric**: On-Time Pickup Rate (-5m to +5m window) > 90%; Shared Commute Detour Ratio < 1.4x for 90% of commuters.

### Problem 4 (P2): Authentication Lockout, OTP Non-Delivery & Session Invalidation
- **Observed Review Evidence**: 19 negative reviews (18 1-star, 1 2-star).  
  *Excerpt (`1d73eadd...`, v12.19.0)*: *"Such a worst app. I am not receiving the OTP even after trying multiple times. Because of this, I am unable to complete the login/verification process."*  
  *Excerpt (`d6cbf0b5...`, v12.18.1)*: *"Unable to login in the App. Both Mobile Otp and Email OTP options are not working"*
- **User Symptom**: Total access lockout, missed shift bookings, inability for drivers to start duty.
- **Root-Cause Hypothesis**: Telecom DLT template scrubbing rejections; SMS aggregator gateway queue latency; session token invalidation on app updates.
- **Recommended Investigation (Phase A)**: Inspect SMS aggregator Delivery Receipts (DLRs) and error codes across Indian carriers for past 7 days; audit TRAI DLT template registration logs; inspect auth rate-limiter rejections.
- **Conditional Technical Fix (Phase B)**:
  1. *Multi-Channel OTP Fallback*: If SMS delivery is unacknowledged after 30s, dynamically offer *"Send OTP via WhatsApp"* and *"Call Me with Code"*.
  2. *Corporate SSO Integration*: Accelerate SAML 2.0 / OAuth integration (Microsoft Entra ID, Okta) for corporate email domains, bypassing SMS entirely.
  3. *Session Token Persistence*: Fix refresh token storage to prevent unnecessary logouts post-update.
- **Provisional Metric**: OTP Delivery Success Rate > 99.0%; p95 Delivery Latency < 20s.

### Problem 5 (P2): App Crashes, Launch Failures & Spurious Play Store Integrity Checks
- **Observed Review Evidence**: 14 negative reviews (100% 1-star severity).  
  *Excerpt (`93d75126...`, v12.19.0)*: *"Please fix the bug..Quite frequently it gives error as 'move in synch application can not be installed/opened as it was not downloaded from play store'."*  
  *Excerpt (`9936bf10...`, v12.19.0)*: *"app crashed did not open in my mobile plx fixed it vivo v25 Pro"*
- **User Symptom**: Immediate app crash on launch; legitimate Play Store installations blocked by false security dialogs.
- **Root-Cause Hypothesis**: Google Play Integrity API or package installer verification logic rejecting installer signatures returned on custom OEM Android ROMs (Vivo FuntouchOS, Oppo ColorOS); unhandled initialization exception during startup.
- **Recommended Investigation (Phase A)**: Inspect Google Play Console Android Vitals and Crashlytics traces for v12.19.0 segmented by OEM and OS; audit Play Integrity token validation logic in v12.19.0.
- **Conditional Technical Fix (Phase B)**:
  1. *Installer Signature Normalization*: Update installer validation logic to recognize OEM package installer signatures returned on Vivo and Oppo devices.
  2. *Safe Startup Initializers*: Wrap non-critical startup initializers in fallback try-catch blocks with telemetry logging.
  3. *OEM Pre-Release Matrix*: Add physical/virtual Chinese OEM devices to automated pre-release test suites.
- **Provisional Metric**: Crash-Free Users > 99.5%; Crash-Free Sessions > 99.9%; Spurious Install Verification Errors = 0.

---

## 4. Specific Actions for the First Working Day (FDE Day-1 Plan)

An incoming Forward Deployed Engineer on Day 1 does not possess administrative access to internal production databases, Google Play Console, AWS clusters, or driver fleets. The plan focuses on realistic discovery, targeted data requests, and diagnostic alignment:

```
+----------------------------------------------------------------------------------------------------------------+
|                                  FORWARD DEPLOYED ENGINEER: FIRST WORKING DAY PLAN                             |
+---------------------+------------------------------------------------------------------------------------------+
| Time Horizon        | Realistic Practical Action                                                               |
+---------------------+------------------------------------------------------------------------------------------+
| Hour 01–03:         | • Host joint discovery briefing with Fleet Safety Operations & Transport Desk Product    |
| Discovery Briefing  |   Lead. Review the 23 public safety reviews and present redacted case study [HR 47-X-XXXX].|
|                     | • Audit internal support ticket queue against the 5 public complaint categories.         |
|                     |                                                                                          |
| Hour 03–05:         | • Submit formal telemetry extraction request to Platform Data Engineering:               |
| Telemetry Requests  |   1. 24h extract of Driver Lite coordinate heartbeat timestamps across device OEMs.      |
|                     |   2. 7-day SMS aggregator DLR delivery receipt logs segmented by telecom carrier.        |
|                     |   3. 14-day trip detour ratio and on-time pickup metrics across peak shift windows.      |
|                     |   4. Crashlytics stack traces and Android Vitals for Employee build 12.19.0.             |
|                     |                                                                                          |
| Hour 05–07:         | • Meet with Mobile Core (Android) Lead to inspect build 12.19.0 ProGuard/R8 mappings.    |
| Engineering Sync    | • Formulate hypothesis validation criteria for Vivo v25 Pro crash traces.                |
|                     | • Share reproduction steps for Play Integrity installer verification dialogs.            |
|                     |                                                                                          |
| Hour 07–08:         | • Consolidate Day-1 findings into an executive briefing for Head of Product & VP Eng.    |
| Executive Synthesis | • Establish 7-day telemetry deep-dive milestones and daily standup schedule.             |
+---------------------+------------------------------------------------------------------------------------------+
```

---

## 5. Credible 30-Day Phased Implementation Roadmap

```
+----------------------------------------------------------------------------------------------------------------+
|                                      CREDIBLE 30-DAY IMPLEMENTATION ROADMAP                                    |
+--------------------+-------------------------------------------------------------------------------------------+
| Phase & Horizon    | Core Engineering & Operational Milestones                                                 |
+--------------------+-------------------------------------------------------------------------------------------+
| PHASE 1: DAYS 1–7  | • Audit 60-day safety ticket backlog; establish <3m operator response SLA.                |
| Investigation &    | • Analyze 24h Driver Lite telematics extract to confirm/refute OS Doze mode throttling.   |
| Diagnostic Deep-Dive| • Audit SMS aggregator DLR logs to quantify true carrier delivery failure rates.         |
|                    | • Inspect Crashlytics stack traces for build 12.19.0; isolate Vivo crash mechanism.       |
|                    | • Shadow-simulate 1.5x detour cap on historical routing datasets.                         |
|                    |                                                                                           |
| PHASE 2: DAYS 8–14 | • Develop conditional fixes in feature branches based on Phase 1 validation:              |
| Solution Dev &     |   - SAFETY: Deploy geofenced drop-off confirmation prompt in Driver Lite staging.         |
| Staging Validation |   - TELEMETRY: Add client stale location UI chip; harden foreground service if validated. |
|                    |   - ROUTING: Configure dynamic traffic buffer and early notification rules.               |
|                    |   - AUTH: Implement WhatsApp OTP fallback and corporate SSO staging connector.            |
|                    |   - STABILITY: Patch OEM installer signature check and wrap startup initializers.         |
|                    | • Release internal dogfooding build (v12.19.1-beta) across internal employee fleet.       |
|                    |                                                                                           |
| PHASE 3: DAYS 15–21| • 5–10% Google Play Canary Rollout of Employee v12.19.1 and Driver Lite v10.2.0.         |
| Canary Pilot &     | • Daily Android Vitals monitoring: Confirm Crash-Free Users >99.5% on Vivo/Oppo.         |
| Telemetry Soak     | • Benchmark real-time ping freshness and tracking stagnation warnings.                    |
|                    | • Measure OTP delivery latency across fallback channels.                                  |
|                    |                                                                                           |
| PHASE 4: DAYS 22–30| • Multi-Stakeholder Release Gate Review (Product, Engineering, Fleet Ops, Compliance).   |
| Pilot Review &     | • Evaluate canary Crashlytics, telemetry ping freshness, and vendor compliance metrics.   |
| Rollout Decision   | • If validation targets are met, authorize expansion from 10% to 25%–50% canary cohorts.   |
| Gate               | • Note: Full 100% production rollout of routing or authentication changes is explicitly    |
|                    |   gated on post-canary validation and formal stakeholder release approval.                |
+--------------------+-------------------------------------------------------------------------------------------+
```

---

## 6. Provisional Measurement Framework & Tooling

### 6.1 Measurement Framework Summary
Full metric formulas and telemetry streams are archived in [measurement_framework.csv](measurement_framework.csv).

| Metric Name | Formula / Definition | Baseline Window | Provisional Target | Responsible Lead |
| :--- | :--- | :--- | :--- | :--- |
| **Safety First-Response Time** | $\text{Timestamp}_{\text{Operator Ack}} - \text{Timestamp}_{\text{SOS Alert}}$ | 14-day pre-fix observation window | Median < 60s; p95 < 3m | Fleet Safety Ops Lead |
| **Geofenced Drop Compliance** | $\frac{\text{Trips Dropped } \le 100\text{m}}{\text{Total Completed Trips}} \times 100$ | 14-day completed trip audit | > 98% compliance | Compliance Ops Lead |
| **GPS Telemetry Freshness** | $\frac{\text{Duration with Ping } \le 15\text{s}}{\text{Active Trip Duration}} \times 100$ | 7-day driver telemetry audit | p95 latency < 15s; Freshness > 95% | Telematics Ingestion Lead |
| **Tracking Stagnation Warning** | $\frac{\text{Sessions with UI Warning}}{\text{Sessions with Gap } > 45\text{s}} \times 100$ | Staging deployment observation | 100% of gaps >45s show chip | Mobile Core (Android) Lead |
| **ETA Prediction MAE** | $\frac{1}{N} \sum \|\text{Predicted ETA} - \text{Actual Arrival}\|$ | 10,000 completed peak-shift trips | Pickup MAE < 4m; Drop MAE < 7m | Routing Algorithm Lead |
| **On-Time Pickup Rate** | $\frac{\text{Trips Within } [-5\text{m}, +5\text{m}]}{\text{Total Scheduled Trips}} \times 100$ | 14-day pre-fix observation window | > 90% across corporate accounts | Enterprise Fleet Ops Lead |
| **Shared Ride Detour Ratio** | $\frac{\text{Shared Ride Transit Time}}{\text{Direct Route Duration}}$ | 30-day pooling routes | Detour Ratio < 1.4x for 90% | Routing Algorithm Lead |
| **OTP Delivery Success Rate** | $\frac{\text{Carrier DLR Acknowledged OTPs } \le 60\text{s}}{\text{Total Requested OTPs}} \times 100$ | 14-day SMS aggregator DLRs | Delivery Success > 99.0% | Platform Comms Lead |
| **Crash-Free Users / Sessions** | $\frac{\text{Sessions Without Crash}}{\text{Total Sessions}} \times 100$ | Continuous Android Vitals on 12.19.0 | Users > 99.5%; Sessions > 99.9% | Mobile Core Lead |
| **Issue-Specific Negative Rate** | $\frac{\text{1–2★ Reviews Tagged with Issue}}{\text{Total Written Reviews for Build}} \times 100$ | Verified baselines: v12.17 (29.8%), v12.18 (20.0%), v12.19 (34.7%) | Overall version negative < 18.0% | Product Experience Lead |

*Governance Notice*: Target values are designated as **Provisional Operating Targets**, requiring empirical baseline measurement across production telemetry during the 14-day pre-fix window before contractual SLA adoption.

### 6.2 Methodology & Engineering Tooling
- **Analysis Pipeline**: Python 3.11.5, Pandas 3.0.6, NumPy 2.4.6, Matplotlib 3.11.2.
- **Classification Engine**: Multi-label taxonomy classifier evaluated on an independent stratified holdout sample achieving **84.0% exact match accuracy** and **0.893 micro-F1**.
- **Automated Regression Suite**: 31 unit tests executing in 5.012s (`unittest`), verifying dataset schemas, classification consistency, and SHA-256 data immutability.
- **Interactive Visualization**: Deployed Streamlit Cloud application with dynamic filtering, KPI trend cards, theme drilldowns, and filtered CSV export.

---

## 7. Submission Artifacts & References

- **Concise Submission Briefing**: [submission_summary.md](submission_summary.md)
- **Full Comprehensive Assignment Report**: [final_assignment_report.md](final_assignment_report.md)
- **Executive Audit Document**: [review_audit.md](review_audit.md)
- **Prioritized Recommendations Matrix (CSV)**: [prioritized_recommendations.csv](prioritized_recommendations.csv)
- **Provisional Measurement Framework (CSV)**: [measurement_framework.csv](measurement_framework.csv)
- **Public GitHub Repository**: [MOVEINSYNC-APPLICATION-REVIEW-ANALYSIS-TOOL](https://github.com/Perfectionist0001/MOVEINSYNC-APPLICATION-REVIEW-ANALYSIS-TOOL)
- **Live Deployed Dashboard**: [Streamlit Cloud Deployment](https://moveinsync-application-review-analysis-tool.streamlit.app/)
