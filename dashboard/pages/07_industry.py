"""Employment by Industry — BLS CES sector-level data."""

from components.page_config import setup_page

setup_page("Industry")

import streamlit as st

from components.charts import (
    industry_changes_bar,
    stacked_area_chart,
    time_series_chart,
)
from components.data_loader import load_multiple_series
from components.filters import date_range_selector
from utils.constants import INDUSTRY_SERIES, SERIES_META

st.header("Employment by Industry")
st.caption(
    "Nonfarm payroll employment across 12 major industry sectors, "
    "sourced from the BLS Current Employment Statistics (CES) survey via FRED."
)

start_date = date_range_selector(default_years=5, key_prefix="industry")

df = load_multiple_series(INDUSTRY_SERIES, start_date=start_date)

if not df.empty:
    # --- Stacked Area: Employment Composition ---
    st.subheader("Employment Composition Over Time")
    fig_area = stacked_area_chart(
        df, INDUSTRY_SERIES,
        title="Nonfarm Employment by Industry Sector",
    )
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("---")

    # --- Bar Chart: Latest MoM Changes ---
    st.subheader("Latest Monthly Change by Sector")
    fig_bar = industry_changes_bar(df, INDUSTRY_SERIES)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # --- Individual Series ---
    st.subheader("Individual Sector Trends")
    for sid in INDUSTRY_SERIES:
        meta = SERIES_META.get(sid, {})
        sdf = df[df["series_id"] == sid]
        if sdf.empty:
            continue
        with st.expander(meta.get("short_name", sid)):
            fig = time_series_chart(sdf, sid, show_ma=True)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No industry employment data available. Run the ingestion pipeline to populate.")
