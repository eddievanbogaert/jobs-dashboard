"""Employment page — Nonfarm payrolls, participation rate, emp-pop ratio."""

from components.page_config import setup_page

setup_page("Employment")

import streamlit as st

from components.charts import bar_chart_changes, dual_series_chart, time_series_chart
from components.data_loader import load_multiple_series, load_series
from components.filters import date_range_selector

st.header("Employment")
start_date = date_range_selector(default_years=5, key_prefix="employment")

# --- Nonfarm Payrolls ---
st.subheader("Total Nonfarm Payrolls")
df_payems = load_series("PAYEMS", start_date=start_date)

if not df_payems.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig = time_series_chart(df_payems, "PAYEMS", show_ma=True, title="Nonfarm Payrolls Level")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = bar_chart_changes(df_payems, "PAYEMS", title="Monthly Change in Payrolls")
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Nonfarm payrolls measure the number of U.S. workers excluding farm employees, "
        "private household employees, and nonprofit organization employees."
    )
else:
    st.info("No payrolls data available.")

st.markdown("---")

# --- Participation Rate & Employment-Population Ratio ---
st.subheader("Participation Rate & Employment-Population Ratio")
df_multi = load_multiple_series(["CIVPART", "EMRATIO"], start_date=start_date)

if not df_multi.empty:
    fig = dual_series_chart(df_multi, ["CIVPART", "EMRATIO"], title="LFPR vs. Employment-Population Ratio")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "The labor force participation rate (LFPR) measures the share of the working-age population "
        "that is either employed or actively seeking work. The employment-population ratio shows the "
        "share of the working-age population that is employed."
    )
else:
    st.info("No participation/employment data available.")
