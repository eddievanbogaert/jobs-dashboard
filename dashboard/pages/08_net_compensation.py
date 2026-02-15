"""Net Compensation — SSA Wage Statistics (Distribution of Wage Earners)."""

from components.page_config import setup_page

setup_page("Net Compensation")

import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

LAYOUT_DEFAULTS = dict(
    template="plotly_white",
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


@st.cache_data
def load_distribution():
    return pd.read_csv(os.path.join(DATA_DIR, "ssa_wage_distribution.csv"))


@st.cache_data
def load_summary():
    return pd.read_csv(os.path.join(DATA_DIR, "ssa_wage_summary.csv"))


st.header("Net Compensation")
st.caption(
    "Distribution of U.S. wage earners by net compensation level, "
    "based on W-2 data reported to the Social Security Administration. "
    "Source: [SSA Wage Statistics](https://www.ssa.gov/cgi-bin/netcomp.cgi)."
)

summary = load_summary()
dist = load_distribution()

years = sorted(dist["year"].unique())


# Create bracket labels
def bracket_label(row):
    lower = row["bracket_lower"]
    upper = row["bracket_upper"]
    if pd.isna(upper):
        return f"${lower / 1e6:.0f}M+"
    if upper >= 1_000_000:
        return f"${lower / 1e6:.1f}M–{upper / 1e6:.1f}M"
    if lower >= 100_000:
        return f"${lower / 1e3:.0f}K–{upper / 1e3:.0f}K"
    return f"${lower / 1e3:.0f}K–{upper / 1e3:.0f}K"


# --- Summary Metrics ---
st.subheader(f"Summary Trends ({years[0]}–{years[-1]})")

col1, col2, col3 = st.columns(3)
latest = summary[summary["year"] == years[-1]].iloc[0]
prev = summary[summary["year"] == years[-2]].iloc[0]

with col1:
    st.metric(
        label=f"Median Wage ({years[-1]})",
        value=f"${latest['median_wage']:,.0f}",
        delta=f"${latest['median_wage'] - prev['median_wage']:+,.0f} vs {years[-2]}",
    )
with col2:
    st.metric(
        label=f"Average Wage ({years[-1]})",
        value=f"${latest['avg_wage']:,.0f}",
        delta=f"${latest['avg_wage'] - prev['avg_wage']:+,.0f} vs {years[-2]}",
    )
with col3:
    st.metric(
        label=f"Total Wage Earners ({years[-1]})",
        value=f"{latest['total_earners'] / 1e6:,.1f}M",
        delta=f"{(latest['total_earners'] - prev['total_earners']) / 1e6:+,.1f}M vs {years[-2]}",
    )

# --- Full Data Table (for selected year) ---
selected_year_table = st.selectbox("Select year", years[::-1], key="ssa_year_table")
year_dist_table = dist[dist["year"] == selected_year_table].copy()
year_dist_table["label"] = year_dist_table.apply(bracket_label, axis=1)

with st.expander("View full data table"):
    display_dist = year_dist_table[["label", "num_earners", "cumulative_num", "pct_of_total", "aggregate_amount", "avg_amount"]].copy()
    display_dist.columns = ["Bracket", "Workers", "Cumulative Workers", "Cumulative %", "Aggregate Compensation ($)", "Average Compensation ($)"]
    st.dataframe(display_dist, use_container_width=True, hide_index=True)

# --- Median & Average Wage Over Time ---
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=summary["year"], y=summary["median_wage"],
    mode="lines+markers", name="Median Wage",
    line=dict(color="#1f77b4", width=2.5),
))
fig_trend.add_trace(go.Scatter(
    x=summary["year"], y=summary["avg_wage"],
    mode="lines+markers", name="Average Wage",
    line=dict(color="#ff7f0e", width=2.5),
))
fig_trend.update_layout(
    title="Median vs. Average Net Compensation",
    yaxis_title="Annual Wage ($)",
    yaxis_tickformat="$,.0f",
    height=400,
    **LAYOUT_DEFAULTS,
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# --- Distribution for Selected Year ---
st.subheader("Wage Distribution")
selected_year = st.selectbox("Select year", years[::-1], key="ssa_year")

year_dist = dist[dist["year"] == selected_year].copy()
year_summary = summary[summary["year"] == selected_year].iloc[0]

year_dist["label"] = year_dist.apply(bracket_label, axis=1)

# Focus on brackets up to $200K for the main chart (most workers)
main_dist = year_dist[year_dist["bracket_lower"] < 200_000]

fig_dist = go.Figure(go.Bar(
    x=main_dist["label"],
    y=main_dist["num_earners"],
    marker_color="#1f77b4",
    hovertemplate="<b>%{x}</b><br>Workers: %{y:,.0f}<extra></extra>",
))
fig_dist.update_layout(
    title=f"Distribution of Wage Earners ({selected_year}) — Under $200K",
    yaxis_title="Number of Wage Earners",
    xaxis_title="Net Compensation Bracket",
    xaxis_tickangle=-45,
    height=500,
    **LAYOUT_DEFAULTS,
)
st.plotly_chart(fig_dist, use_container_width=True)

# --- Cumulative Distribution ---
st.subheader("Cumulative Distribution")

fig_cum = go.Figure()
fig_cum.add_trace(go.Scatter(
    x=year_dist["bracket_lower"],
    y=year_dist["pct_of_total"],
    mode="lines",
    name="Cumulative %",
    line=dict(color="#2ca02c", width=2.5),
    fill="tozeroy",
    fillcolor="rgba(44, 160, 44, 0.1)",
    hovertemplate="Up to $%{x:,.0f}: %{y:.1f}%<extra></extra>",
))
# Add reference lines for median and average
fig_cum.add_vline(
    x=year_summary["median_wage"], line_dash="dash", line_color="#1f77b4",
    annotation_text=f"Median: ${year_summary['median_wage']:,.0f}",
    annotation_position="top",
)
fig_cum.add_vline(
    x=year_summary["avg_wage"], line_dash="dash", line_color="#ff7f0e",
    annotation_text=f"Average: ${year_summary['avg_wage']:,.0f}",
    annotation_position="top",
)
fig_cum.update_layout(
    title=f"Cumulative Wage Distribution ({selected_year})",
    xaxis_title="Net Compensation ($)",
    yaxis_title="Cumulative % of Workers",
    xaxis_tickformat="$,.0f",
    xaxis_range=[0, 250_000],
    height=450,
    **LAYOUT_DEFAULTS,
)
st.plotly_chart(fig_cum, use_container_width=True)

st.markdown("---")

# --- Year-over-Year Comparison ---
st.subheader("Year-over-Year Comparison")

compare_years = st.multiselect(
    "Compare years", years[::-1], default=[years[-1], years[0]],
    key="ssa_compare",
)

if len(compare_years) >= 2:
    fig_compare = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
    for i, yr in enumerate(sorted(compare_years)):
        yr_data = dist[dist["year"] == yr]
        # Focus on main range
        yr_data = yr_data[yr_data["bracket_lower"] < 200_000]
        fig_compare.add_trace(go.Scatter(
            x=yr_data["bracket_lower"],
            y=yr_data["pct_of_total"],
            mode="lines",
            name=str(yr),
            line=dict(color=colors[i % len(colors)], width=2),
        ))
    fig_compare.update_layout(
        title="Cumulative Distribution Comparison",
        xaxis_title="Net Compensation ($)",
        yaxis_title="Cumulative % of Workers",
        xaxis_tickformat="$,.0f",
        height=450,
        **LAYOUT_DEFAULTS,
    )
    st.plotly_chart(fig_compare, use_container_width=True)
else:
    st.info("Select at least 2 years to compare.")
