"""
MoveInSync Review Analysis - Interactive Analytics Dashboard
Phase 4 Implementation: Multi-App Intelligence, Dynamic Filtering, and Audited Governance.
"""

import math
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import dashboard_data as dd

# -----------------------------------------------------------------------------
# Streamlit App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MoveInSync Review Intelligence",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Enterprise Aesthetics
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .kpi-card {
        background: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0F172A;
        margin: 4px 0;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #94A3B8;
    }
    .badge-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-neg { background: #FEE2E2; color: #DC2626; }
    .badge-neu { background: #FEF3C7; color: #D97706; }
    .badge-pos { background: #DCFCE7; color: #16A34A; }
    .badge-theme { background: #E0E7FF; color: #4338CA; margin-right: 4px; margin-bottom: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def get_cached_raw_data():
    """Caches raw data loading across dashboard reruns."""
    apps_cfg = dd.load_apps_config()
    tax_cfg = dd.load_taxonomy_config()
    df = dd.load_reviews_data()
    ratings_df = dd.load_ratings_history()
    holdout_df = dd.load_holdout_metrics()
    return apps_cfg, tax_cfg, df, ratings_df, holdout_df


# -----------------------------------------------------------------------------
# Load Baseline Data
# -----------------------------------------------------------------------------
try:
    apps_config, taxonomy_config, raw_df, ratings_history_df, holdout_summary_df = get_cached_raw_data()
except Exception as e:
    st.error(f"❌ Critical Error Loading Data: {str(e)}")
    st.info("Please make sure `reports/processed_all_reviews.csv` exists or run local recomputation.")
    if st.button("Run Initial Recomputation"):
        success, msg = dd.run_recompute_pipeline()
        if success:
            st.success(msg)
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(msg)
    st.stop()

# Data Governance Metadata
freshness = dd.get_data_freshness_metadata()
app_id_to_name = {a["app_id"]: a["display_name"] for a in apps_config}
app_id_to_slug = {a["app_id"]: a["slug"] for a in apps_config}
tax_themes_dict = taxonomy_config.get("themes", {})
functional_theme_keys = list(tax_themes_dict.keys())

# -----------------------------------------------------------------------------
# Sidebar: Controls, Filters & Pipeline Management
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🚖 MoveInSync Intelligence")
st.sidebar.caption(f"Last Pipeline Sync: **{freshness.get('last_recomputed_str', 'N/A')}**")

# 1. App Selector
app_options = ["All Apps"] + [a["display_name"] for a in apps_config]
selected_app_label = st.sidebar.selectbox("Select Application", options=app_options, index=0)

if selected_app_label == "All Apps":
    selected_app_id = "all"
else:
    selected_app_id = next(a["app_id"] for a in apps_config if a["display_name"] == selected_app_label)

# Filter by App initially to dynamically bound downstream filters
app_filtered_df = raw_df if selected_app_id == "all" else raw_df[raw_df["app_id"] == selected_app_id]

# 2. Date Range Filter
min_date = app_filtered_df["date_dt"].min()
max_date = app_filtered_df["date_dt"].max()

if pd.notna(min_date) and pd.notna(max_date):
    default_start = min_date.date()
    default_end = max_date.date()
    date_selection = st.sidebar.date_input(
        "Date Range",
        value=(default_start, default_end),
        min_value=default_start,
        max_value=default_end,
    )
    if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
        selected_date_range = date_selection
    else:
        selected_date_range = (default_start, default_end)
else:
    selected_date_range = None

# 3. Rating Filter (1-5 stars)
all_stars = [1, 2, 3, 4, 5]
selected_stars = st.sidebar.multiselect(
    "Star Ratings",
    options=all_stars,
    default=all_stars,
    format_func=lambda x: f"{x} ★",
)

# 4. Version Filter
unique_versions = sorted([v for v in app_filtered_df["version_clean"].unique() if v != "Unknown/Unspecified"])
version_options = ["All Versions"] + unique_versions
if "Unknown/Unspecified" in app_filtered_df["version_clean"].values:
    version_options.append("Unknown/Unspecified")

selected_versions = st.sidebar.multiselect(
    "App Versions",
    options=version_options,
    default=["All Versions"],
)

# 5. Theme Filter
theme_filter_options = [
    (k, tax_themes_dict.get(k, {}).get("name", k))
    for k in functional_theme_keys
] + [("other_unclassified", "Other / Generic (No specific feature)")]

theme_name_map = dict(theme_filter_options)
theme_display_names = [v for _, v in theme_filter_options]
name_to_key = {v: k for k, v in theme_filter_options}

selected_theme_names = st.sidebar.multiselect(
    "Problem & Feedback Themes",
    options=theme_display_names,
    default=[],
    help="Select one or more themes to show reviews matching any selected category.",
)
selected_theme_keys = [name_to_key[n] for n in selected_theme_names] if selected_theme_names else None

# 6. Text Search Filter
search_query = st.sidebar.text_input(
    "Search Review Text",
    value="",
    placeholder="e.g. crash, otp, driver, route...",
)

# Apply All Filters Dynamically
active_df = dd.filter_reviews(
    df=raw_df,
    app_id=selected_app_id,
    date_range=selected_date_range,
    ratings=selected_stars if selected_stars else all_stars,
    versions=selected_versions if selected_versions else ["All Versions"],
    themes=selected_theme_keys,
    search_term=search_query,
)

# -----------------------------------------------------------------------------
# Sidebar: Maintenance & Pipeline Controls
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Pipeline Controls")

if st.sidebar.button("🔄 Recompute Analytics Pipeline", use_container_width=True):
    with st.spinner("Executing local analysis pipeline across all apps..."):
        success, message = dd.run_recompute_pipeline()
        if success:
            st.sidebar.success("Pipeline refreshed successfully!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.sidebar.error("Recomputation failed:")
            st.sidebar.code(message)

with st.sidebar.expander("🌐 Google Play Scraper (Remote)"):
    st.caption("Fetches new public reviews over Google Play Scraper API.")
    confirm_scrape = st.checkbox("Confirm live external scraping")
    if st.button("Run Scraper Now", disabled=not confirm_scrape, use_container_width=True):
        with st.spinner("Connecting to Google Play and updating review databases..."):
            s_ok, s_msg = dd.run_remote_scraping()
            if s_ok:
                st.success("Scraper executed successfully!")
                # Automatically recompute after scrape
                dd.run_recompute_pipeline()
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Scraper error: {s_msg}")

# -----------------------------------------------------------------------------
# Main Header & Scope Banners
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">MoveInSync Enterprise Review Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Multi-app customer sentiment analytics, theme classification, and operational diagnostics</div>',
    unsafe_allow_html=True,
)

# Driver Partner Low-Sample Warning
if selected_app_id == "com.moveinsync.driver.dco":
    st.warning(
        "⚠️ **Preliminary Sample Notice**: MoveInSync - Driver Partner contains only **7 total public reviews** in the Play Store database. "
        "All calculated percentages and version averages carry high statistical variance and are presented strictly for qualitative context.",
        icon="⚠️",
    )

# Ratings Snapshot Governance Notice
st.info(
    "ℹ️ **Data Governance & Snapshot Note**: Play Store store-level ratings (`ratings_history.csv`) represent a **single-date snapshot (2026-10-10)**. "
    "To avoid misrepresenting static snapshots as historical trends, store-level ratings (e.g. Employee 4.64★, Lite 4.29★, DCO 3.50★) are maintained separate from review-level sample averages.",
    icon="ℹ️",
)

# -----------------------------------------------------------------------------
# KPI Overview Cards
# -----------------------------------------------------------------------------
kpi_data = dd.calculate_kpis(active_df, functional_theme_keys)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        label="Total Reviews Analyzed",
        value=f"{kpi_data['total_reviews']:,}",
        delta=f"{round((kpi_data['total_reviews']/len(raw_df))*100, 1)}% of all reviews" if len(raw_df) > 0 else None,
    )

with k2:
    st.metric(
        label="Average Star Rating",
        value=f"{kpi_data['average_rating']} ★" if kpi_data["total_reviews"] > 0 else "N/A",
        delta=f"Positive (4–5★): {kpi_data['positive_pct']}%",
    )

with k3:
    st.metric(
        label="Negative Feedback (1–2★)",
        value=f"{kpi_data['negative_pct']}%",
        delta=f"{kpi_data['negative_count']} critical reviews",
        delta_color="inverse",
    )

with k4:
    most_th_key = kpi_data["most_mentioned_theme"]
    if most_th_key:
        most_th_name = tax_themes_dict.get(most_th_key, {}).get("name", most_th_key)
        st.metric(
            label="Top Problem Theme",
            value=most_th_name.split(",")[0].split("&")[0].strip(),
            delta=f"{kpi_data['most_mentioned_theme_count']} mentions ({kpi_data['most_mentioned_theme_share_pct']}%)",
            delta_color="inverse",
        )
    else:
        st.metric(label="Top Problem Theme", value="None Detected", delta="0 mentions")

# -----------------------------------------------------------------------------
# Empty Results Guard
# -----------------------------------------------------------------------------
if active_df.empty:
    st.warning(
        "⚠️ **No reviews match the current filter selection.**\n\n"
        "Please adjust your date range, rating checkboxes, version selectors, or clear your keyword search.",
        icon="🔍",
    )
    st.stop()

# -----------------------------------------------------------------------------
# Interactive Visualizations Section
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📊 Interactive Visualizations")

tab_dist, tab_time, tab_themes, tab_validation = st.tabs(
    ["⭐ Rating Distribution", "📈 Volume & Rating Trajectory", "🏷️ Problem Theme Breakdown", "🛡️ Validation & Model Quality"]
)

with tab_dist:
    dist_df = dd.calculate_rating_distribution(active_df)
    
    # Custom color palette for star ratings
    star_colors = ["#EF4444", "#F97316", "#EAB308", "#84CC16", "#22C55E"]
    
    fig_dist = go.Figure()
    fig_dist.add_trace(
        go.Bar(
            x=[f"{s} ★" for s in dist_df["star"]],
            y=dist_df["count"],
            text=[f"{c} ({p}%)" for c, p in zip(dist_df["count"], dist_df["pct"])],
            textposition="auto",
            marker=dict(color=star_colors, line=dict(color="#334155", width=1)),
            hovertemplate="Rating: %{x}<br>Count: %{y}<br>Share: %{text}<extra></extra>",
        )
    )
    fig_dist.update_layout(
        title=f"Rating Distribution — {selected_app_label} (N={len(active_df):,})",
        xaxis_title="Star Rating",
        yaxis_title="Review Count",
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with tab_time:
    ts_df = dd.calculate_time_series(active_df, freq="W-MON")
    if ts_df.empty or len(ts_df) < 2:
        st.info("Insufficient weekly data points to plot longitudinal trajectory for current selection.")
    else:
        fig_time = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Primary axis: Volume
        fig_time.add_trace(
            go.Bar(
                x=ts_df["period"],
                y=ts_df["review_count"],
                name="Review Volume",
                marker_color="#94A3B8",
                opacity=0.6,
                hovertemplate="Week: %{x}<br>Volume: %{y} reviews<extra></extra>",
            ),
            secondary_y=False,
        )
        
        # Secondary axis: Mean Rating
        fig_time.add_trace(
            go.Scatter(
                x=ts_df["period"],
                y=ts_df["average_rating"],
                name="Average Rating (★)",
                mode="lines+markers",
                line=dict(color="#2563EB", width=3),
                marker=dict(size=7, color="#1D4ED8"),
                hovertemplate="Week: %{x}<br>Mean Rating: %{y:.2f} ★<extra></extra>",
            ),
            secondary_y=True,
        )
        
        fig_time.update_layout(
            title=f"Weekly Review Volume & Star Trajectory — {selected_app_label}",
            xaxis_title="Week Starting (Monday)",
            template="plotly_white",
            height=400,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        fig_time.update_yaxes(title_text="Review Count", secondary_y=False)
        fig_time.update_yaxes(title_text="Average Rating (1–5)", secondary_y=True, range=[1.0, 5.0])
        st.plotly_chart(fig_time, use_container_width=True)

with tab_themes:
    theme_bd_df = dd.calculate_theme_breakdown(active_df, taxonomy_config, include_other=True)
    
    # Exclude other_unclassified from problem chart for clarity, or let user toggle
    show_unclassified = st.checkbox("Include 'Other / Generic' reviews in theme chart", value=False)
    chart_theme_df = theme_bd_df if show_unclassified else theme_bd_df[theme_bd_df["theme_key"] != "other_unclassified"]
    
    if chart_theme_df.empty or chart_theme_df["mention_count"].sum() == 0:
        st.info("No functional themes matched the current filtered reviews.")
    else:
        # Sort ascending for horizontal bar chart
        plot_themes = chart_theme_df.sort_values(by="mention_count", ascending=True)
        
        fig_theme = go.Figure()
        
        # Stacked breakdown: Negative, Neutral, Positive within each theme
        fig_theme.add_trace(
            go.Bar(
                y=plot_themes["theme_name"],
                x=plot_themes["negative_reviews_1_2_star"],
                name="Negative (1–2★)",
                orientation="h",
                marker_color="#DC2626",
                hovertemplate="%{y}<br>Negative: %{x} reviews<extra></extra>",
            )
        )
        fig_theme.add_trace(
            go.Bar(
                y=plot_themes["theme_name"],
                x=plot_themes["neutral_reviews_3_star"],
                name="Neutral (3★)",
                orientation="h",
                marker_color="#F59E0B",
                hovertemplate="%{y}<br>Neutral: %{x} reviews<extra></extra>",
            )
        )
        fig_theme.add_trace(
            go.Bar(
                y=plot_themes["theme_name"],
                x=plot_themes["positive_reviews_4_5_star"],
                name="Positive (4–5★)",
                orientation="h",
                marker_color="#10B981",
                hovertemplate="%{y}<br>Positive: %{x} reviews<extra></extra>",
            )
        )
        
        fig_theme.update_layout(
            barmode="stack",
            title="Problem & Feature Themes Breakdown (Multi-Label Mentions by Sentiment)",
            xaxis_title="Total Theme Mentions",
            yaxis_title="Theme Category",
            template="plotly_white",
            height=440,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=150, r=40, t=60, b=40),
        )
        st.plotly_chart(fig_theme, use_container_width=True)
        st.caption(
            "📌 **Multi-Label Cardinality Note**: Reviews can mention multiple themes simultaneously. "
            "Therefore, the sum of theme mentions across categories exceeds unique review count."
        )

with tab_validation:
    st.markdown("#### Independent Holdout Classification Quality ($N=50$)")
    st.markdown(
        "Performance audited on an independent, stratified 50-review holdout sample (seed `101`, zero overlap with the 30-review tuning set):"
    )
    
    val_c1, val_c2, val_c3, val_c4 = st.columns(4)
    val_c1.metric("Exact Match Ratio", "84.0%", help="Exact match across all multi-label theme sets")
    val_c2.metric("Hamming Loss", "0.0267", help="Only 12 label errors across 450 evaluation slots")
    val_c3.metric("Micro F1-Score", "0.893", help="Aggregate micro-averaged precision/recall balance")
    val_c4.metric("Macro F1-Score", "0.722", help="Unweighted average across all theme categories")
    
    if not holdout_summary_df.empty:
        st.dataframe(
            holdout_summary_df.rename(
                columns={
                    "theme": "Theme",
                    "precision": "Precision",
                    "recall": "Recall",
                    "f1_score": "F1 Score",
                    "support": "Support (N)",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Holdout metrics summary file (`reports/holdout_metrics_summary.csv`) not found.")

# -----------------------------------------------------------------------------
# Review Explorer & Data Table
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🔍 Customer Review Explorer")

r_col1, r_col2, r_col3 = st.columns([2, 1, 1])

with r_col1:
    sort_option = st.selectbox(
        "Sort By",
        options=[
            "Date: Newest First",
            "Date: Oldest First",
            "Rating: Lowest First",
            "Rating: Highest First",
            "Thumbs Up: Most Helpful",
        ],
        index=0,
    )

with r_col2:
    page_size = st.selectbox("Reviews Per Page", options=[10, 25, 50, 100], index=0)

# Sort Data
sorted_df = active_df.copy()
if sort_option == "Date: Newest First":
    sorted_df.sort_values(by="date_dt", ascending=False, inplace=True)
elif sort_option == "Date: Oldest First":
    sorted_df.sort_values(by="date_dt", ascending=True, inplace=True)
elif sort_option == "Rating: Lowest First":
    sorted_df.sort_values(by=["score", "date_dt"], ascending=[True, False], inplace=True)
elif sort_option == "Rating: Highest First":
    sorted_df.sort_values(by=["score", "date_dt"], ascending=[False, False], inplace=True)
elif sort_option == "Thumbs Up: Most Helpful":
    sorted_df.sort_values(by=["thumbsUpCount", "date_dt"], ascending=[False, False], inplace=True)

total_records = len(sorted_df)
total_pages = max(1, math.ceil(total_records / page_size))

with r_col3:
    current_page = st.number_input(
        f"Page (1 to {total_pages})",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
    )

# Slice page
start_idx = (current_page - 1) * page_size
end_idx = min(start_idx + page_size, total_records)
page_df = sorted_df.iloc[start_idx:end_idx]

st.caption(f"Showing reviews **{start_idx + 1}** to **{end_idx}** of **{total_records:,}** matching records.")

# Render Review Cards
for _, row in page_df.iterrows():
    star_val = int(row.get("score", 0))
    star_badge_cls = "badge-neg" if star_val <= 2 else ("badge-neu" if star_val == 3 else "badge-pos")
    app_label = app_id_to_name.get(row.get("app_id"), row.get("app_id", "App"))
    date_str = str(row.get("date", "Unknown Date"))
    ver_str = str(row.get("version_clean", "Unknown/Unspecified"))
    thumbs = int(row.get("thumbsUpCount", 0))
    
    # Parse assigned themes
    raw_themes = row.get("assigned_themes", "")
    if isinstance(raw_themes, str) and raw_themes.startswith("["):
        try:
            import ast
            theme_list = ast.literal_eval(raw_themes)
        except Exception:
            theme_list = [raw_themes]
    elif isinstance(raw_themes, list):
        theme_list = raw_themes
    else:
        theme_list = [t.strip() for t in str(raw_themes).split(",") if t.strip()]
        
    theme_chips_html = "".join(
        [f'<span class="badge-pill badge-theme">{tax_themes_dict.get(t, {}).get("name", t).split(",")[0]}</span>' for t in theme_list]
    )

    with st.container():
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:14px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div>
                        <span class="badge-pill {star_badge_cls}">{star_val} ★</span>
                        <strong style="margin-left:8px; color:#1E293B;">{app_label}</strong>
                        <span style="color:#64748B; font-size:0.8rem; margin-left:8px;">v{ver_str}</span>
                    </div>
                    <div style="color:#94A3B8; font-size:0.8rem;">
                        📅 {date_str} &nbsp;|&nbsp; 👍 {thumbs}
                    </div>
                </div>
                <div style="color:#334155; font-size:0.95rem; line-height:1.45; margin-bottom:8px;">
                    "{row.get('content', '')}"
                </div>
                <div>{theme_chips_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# Data Export Section
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 💾 Export Filtered Dataset")

export_cols = [
    "app_id", "reviewId", "score", "date", "version_clean",
    "content", "thumbsUpCount", "assigned_themes", "primary_theme",
]

csv_data = dd.export_filtered_csv(active_df, export_cols)

st.download_button(
    label=f"📥 Download Filtered Reviews ({len(active_df):,} rows as CSV)",
    data=csv_data,
    file_name=f"moveinsync_filtered_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
    use_container_width=True,
)
