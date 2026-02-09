"""Overview page — Labor market scorecard with KPI cards."""

import streamlit as st

from components.data_loader import load_latest_values, load_multiple_series
from components.filters import date_range_selector
from components.metrics import render_kpi_card
from utils.constants import OVERVIEW_SERIES, SERIES_META

st.header("Labor Market Overview")

# --- KPI Scorecard ---
latest = load_latest_values()

cols = st.columns(4)
for i, sid in enumerate(OVERVIEW_SERIES):
    row_data = latest[latest["series_id"] == sid]
    if row_data.empty:
        continue
    row = row_data.iloc[0].to_dict()
    with cols[i % 4]:
        render_kpi_card(sid, row)

st.markdown("---")

# --- Z-Score Pulse Chart ---
st.subheader("Labor Market Pulse (Z-Scores vs. 5-Year History)")
st.caption(
    "Z-scores show how far current values are from their trailing 5-year average. "
    "Values above zero indicate above-average readings; below zero, below-average."
)

start_date = date_range_selector(default_years=3, key_prefix="overview")
df = load_multiple_series(OVERVIEW_SERIES, start_date=start_date)

if not df.empty:
    import plotly.graph_objects as go

    fig = go.Figure()
    for sid in OVERVIEW_SERIES:
        sdf = df[df["series_id"] == sid].copy()
        if sdf.empty:
            continue
        meta = SERIES_META.get(sid, {})
        fig.add_trace(go.Scatter(
            x=sdf["observation_date"],
            y=sdf["z_score_5y"],
            mode="lines",
            name=meta.get("short_name", sid),
            line=dict(color=meta.get("color", "#333"), width=1.5),
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40, r=20, t=20, b=40),
        hovermode="x unified",
        yaxis_title="Z-Score",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available yet. Run the ingestion pipeline to populate the dashboard.")
