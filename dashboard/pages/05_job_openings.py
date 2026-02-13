"""Job Openings page — JOLTS data and Beveridge curve."""

import streamlit as st

from components.charts import scatter_chart, time_series_chart
from components.data_loader import load_series
from components.filters import date_range_selector

st.header("Job Openings (JOLTS)")
start_date = date_range_selector(default_years=5, key_prefix="jolts")

# --- Job Openings Level ---
st.subheader("Total Job Openings")
df_jolts = load_series("JTSJOL", start_date=start_date)

if not df_jolts.empty:
    fig = time_series_chart(df_jolts, "JTSJOL", show_ma=True, title="JOLTS Job Openings")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "JOLTS (Job Openings and Labor Turnover Survey) measures the number of job openings "
        "at the end of each month. Higher openings indicate stronger labor demand."
    )
else:
    st.info("No JOLTS data available.")

st.markdown("---")

# --- Beveridge Curve ---
st.subheader("Beveridge Curve")
st.caption(
    "The Beveridge curve plots the unemployment rate against the job openings rate. "
    "Shifts in this relationship can signal structural changes in the labor market."
)

df_unrate = load_series("UNRATE", start_date=start_date)

if not df_jolts.empty and not df_unrate.empty:
    fig = scatter_chart(
        df_unrate, df_jolts,
        x_series="UNRATE", y_series="JTSJOL",
        title="Beveridge Curve: Unemployment vs. Job Openings",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Insufficient data for Beveridge curve.")
