from __future__ import annotations

import datetime as dt
import difflib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "BIDDERS_PROFILE_INSIGHTS_15TO24.json"
STYLE_FILE = BASE_DIR / "style.css"
PAGE_TITLE = "Contractor Intelligence Dashboard"


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_bidders_data() -> dict[str, list[dict[str, Any]]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_stylesheet() -> str:
    return STYLE_FILE.read_text(encoding="utf-8")


def format_inr(value: Any) -> str:
    try:
        amount = float(str(value).replace(",", ""))
    except (TypeError, ValueError, AttributeError):
        return "NA"

    absolute_amount = abs(amount)
    if absolute_amount >= 10**7:
        return f"₹ {amount / 10**7:.2f} Cr"
    if absolute_amount >= 10**5:
        return f"₹ {amount / 10**5:.2f} Lakh"
    return f"₹ {amount:,.0f}"


def parse_datetime(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%d-%b-%Y %I:%M %p")


def safe_float(value: Any) -> float | None:
    if value in (None, "", "NA"):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError, AttributeError):
        return None


def first_non_empty(series: pd.Series, fallback: str = "Not available") -> str:
    for value in series:
        if pd.notna(value) and str(value).strip() and str(value).strip() != "NA":
            return str(value).strip()
    return fallback


def build_contractor_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(records).copy()
    if frame.empty:
        return frame

    frame["submitted_on"] = pd.to_datetime(
        frame["bid_submission_date"],
        format="%d-%b-%Y %I:%M %p",
        errors="coerce",
    )
    frame["department"] = frame["org"].fillna("Unknown").astype(str).str.split("|").str[0]
    frame["gov_price_num"] = frame["gov_price"].apply(safe_float)
    frame["bid_won_price_num"] = frame["bid_won_price"].apply(safe_float)
    frame["l1_price_num"] = frame["l1_price"].apply(safe_float)
    frame["bid_percentage_num"] = frame["bid_percentage"].apply(safe_float)
    frame = frame.sort_values("submitted_on", ascending=False, na_position="last").reset_index(drop=True)
    return frame


def metric_card(label: str, value: str, help_text: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">{label}</span>
            <span class="metric-value">{value}</span>
            <span class="metric-help">{help_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="info-card">
            <span class="info-title">{title}</span>
            <span class="info-value">{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(frame: pd.DataFrame, contractor_name: str) -> None:
    total_awarded_value = frame["l1_price_num"].dropna().sum()
    avg_bid_pct = frame["bid_percentage_num"].dropna().mean()
    win_count = len(frame)
    top_department = first_non_empty(frame["department"].mode(), "No department data")
    top_district = first_non_empty(frame["district"].mode(), "No district data")
    latest_submission = frame["submitted_on"].dropna().max()

    hero_left, hero_right = st.columns([1.6, 1.0], gap="large")
    with hero_left:
        st.markdown(
            f"""
            <section class="hero-panel">
                <p class="eyebrow">Tender Intelligence Workspace</p>
                <h1>{contractor_name}</h1>
                <p class="hero-copy">
                    A focused view of awarded tenders, bid behaviour, department concentration,
                    and district-level footprint pulled from the project dataset.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        info_card(
            "Latest submission",
            latest_submission.strftime("%d %b %Y, %I:%M %p") if pd.notna(latest_submission) else "Not available",
        )
        info_card("Top department", top_department)
        info_card("Top district", top_district)

    metric_columns = st.columns(4, gap="medium")
    with metric_columns[0]:
        metric_card("Awarded value", format_inr(total_awarded_value), "Aggregate L1 value across recorded wins")
    with metric_columns[1]:
        metric_card("Tenders won", f"{win_count:,}", "Total awarded tenders in the profile")
    with metric_columns[2]:
        metric_card(
            "Average bid %",
            f"{avg_bid_pct:.2f}%" if pd.notna(avg_bid_pct) else "NA",
            "Mean bid percentage where available",
        )
    with metric_columns[3]:
        active_districts = frame["district"].dropna().nunique()
        metric_card("Active districts", f"{active_districts:,}", "Unique districts covered by wins")


def render_distribution_charts(frame: pd.DataFrame) -> None:
    charts_left, charts_right = st.columns(2, gap="large")

    district_counts = (
        frame["district"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("District")
        .reset_index(name="Tenders Won")
    )
    department_counts = (
        frame["department"]
        .fillna("Unknown")
        .value_counts()
        .head(10)
        .rename_axis("Department")
        .reset_index(name="Tenders Won")
    )

    district_fig = px.pie(
        district_counts,
        names="District",
        values="Tenders Won",
        hole=0.58,
        title="District distribution",
        color_discrete_sequence=[
            "#114B5F",
            "#1A936F",
            "#88D498",
            "#C6DABF",
            "#F3E9D2",
            "#DA6A00",
        ],
    )
    district_fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="#FFFFFF", width=2)))
    district_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=20, l=20, r=20),
        font=dict(color="#16313C"),
    )

    department_fig = px.bar(
        department_counts,
        x="Tenders Won",
        y="Department",
        orientation="h",
        title="Top departments",
        color="Tenders Won",
        color_continuous_scale=["#D9ED92", "#34A0A4", "#184E77"],
    )
    department_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(t=60, b=20, l=20, r=20),
        font=dict(color="#16313C"),
        yaxis=dict(categoryorder="total ascending"),
    )
    department_fig.update_traces(marker_line_width=0)

    with charts_left:
        st.plotly_chart(district_fig, use_container_width=True)
    with charts_right:
        st.plotly_chart(department_fig, use_container_width=True)


def render_time_series(frame: pd.DataFrame) -> None:
    timeline = (
        frame.dropna(subset=["submitted_on"])
        .set_index("submitted_on")
        .resample("Q")
        .agg(
            tenders_won=("tenderid", "count"),
            awarded_value=("l1_price_num", "sum"),
        )
        .reset_index()
    )

    if timeline.empty:
        st.info("No submission dates are available for timeline analysis.")
        return

    timeline["quarter"] = timeline["submitted_on"].dt.to_period("Q").astype(str)
    timeline_fig = px.line(
        timeline,
        x="quarter",
        y="tenders_won",
        markers=True,
        title="Win activity over time",
        line_shape="spline",
    )
    timeline_fig.update_traces(line=dict(color="#DA6A00", width=4), marker=dict(size=9, color="#114B5F"))
    timeline_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=20, l=20, r=20),
        xaxis_title="Quarter",
        yaxis_title="Tenders won",
        font=dict(color="#16313C"),
    )
    st.plotly_chart(timeline_fig, use_container_width=True)


def render_recent_tenders(frame: pd.DataFrame) -> None:
    tender_table = frame[
        [
            "tender_titile",
            "department",
            "district",
            "gov_price_num",
            "bid_won_price_num",
            "bid_percentage_num",
            "bid_submission_date",
        ]
    ].rename(
        columns={
            "tender_titile": "Tender Title",
            "department": "Department",
            "district": "District",
            "gov_price_num": "Gov. Estimate",
            "bid_won_price_num": "Bid Won Price",
            "bid_percentage_num": "Bid %",
            "bid_submission_date": "Submitted On",
        }
    )

    tender_table["Gov. Estimate"] = tender_table["Gov. Estimate"].apply(format_inr)
    tender_table["Bid Won Price"] = tender_table["Bid Won Price"].apply(format_inr)
    tender_table["Bid %"] = tender_table["Bid %"].apply(lambda value: f"{value:.2f}%" if pd.notna(value) else "NA")

    st.dataframe(
        tender_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tender Title": st.column_config.TextColumn(width="large"),
            "Department": st.column_config.TextColumn(width="medium"),
            "District": st.column_config.TextColumn(width="medium"),
            "Submitted On": st.column_config.TextColumn(width="medium"),
        },
    )


def render_search_panel(contractor_names: list[str]) -> str | None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <p class="eyebrow">Search</p>
                <h2>Find a contractor</h2>
                <p>Use the exact name or type a close variation to surface similar profiles.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        search_term = st.text_input(
            "Contractor name",
            placeholder="Start typing a contractor name",
            help="Fuzzy search is enabled, so near matches will still be suggested.",
        ).strip()

        if not search_term:
            return None

        matches = difflib.get_close_matches(search_term, contractor_names, n=8, cutoff=0.35)
        if search_term in contractor_names and search_term not in matches:
            matches.insert(0, search_term)

        if not matches:
            st.warning("No close matches found. Try a shorter or more exact contractor name.")
            return None

        selected_name = st.selectbox("Suggested matches", options=matches, index=0)
        st.caption(f"{len(matches)} candidate profiles found")
        return selected_name


def render_empty_state(total_contractors: int) -> None:
    st.markdown(
        f"""
        <section class="empty-state">
            <p class="eyebrow">Portfolio-ready Streamlit dashboard</p>
            <h1>Explore {total_contractors:,} contractor profiles</h1>
            <p>
                Search from the sidebar to inspect awarded tenders, pricing patterns, department focus,
                district distribution, and recent submission history.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    preview_left, preview_right, preview_third = st.columns(3, gap="medium")
    with preview_left:
        info_card("What you can inspect", "Awarded value, win count, average bid behaviour")
    with preview_right:
        info_card("Visual analytics", "District mix, department concentration, timeline")
    with preview_third:
        info_card("Data source", "Local bidder intelligence JSON for rapid analysis")


def main() -> None:
    st.markdown(f"<style>{load_stylesheet()}</style>", unsafe_allow_html=True)
    bidders_data = load_bidders_data()
    contractor_names = sorted(bidders_data.keys())

    selected_name = render_search_panel(contractor_names)
    if not selected_name:
        render_empty_state(len(contractor_names))
        return

    frame = build_contractor_frame(bidders_data[selected_name])
    if frame.empty:
        st.error("The selected contractor does not have any usable records in the dataset.")
        return

    render_overview(frame, selected_name)

    overview_tab, trend_tab, records_tab = st.tabs(["Overview", "Trend Analysis", "Tender Records"])
    with overview_tab:
        render_distribution_charts(frame)
    with trend_tab:
        render_time_series(frame)
    with records_tab:
        render_recent_tenders(frame)


if __name__ == "__main__":
    main()
