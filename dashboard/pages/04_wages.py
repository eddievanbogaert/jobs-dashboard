"""Wages page — Average hourly earnings trends."""

import streamlit as st

from components.charts import time_series_chart
from components.data_loader import load_series
from components.filters import date_range_selector

st.header("Wages")
start_date = date_range_selector(default_years=5, key_prefix="wages")

# --- Average Hourly Earnings Level ---
st.subheader("Average Hourly Earnings (All Private Employees)")
df = load_series("CES0500000003", start_date=start_date)

if not df.empty:
    fig = time_series_chart(df, "CES0500000003", show_ma=True, title="Average Hourly Earnings")
    st.plotly_chart(fig, use_container_width=True)

    # Year-over-year % change
    st.subheader("Year-over-Year Wage Growth")
    df_yoy = df.dropna(subset=["yoy_pct_change"])
    if not df_yoy.empty:
        import plotly.graph_objects as go
        fig2 = go.Figure(go.Scatter(
            x=df_yoy["observation_date"], y=df_yoy["yoy_pct_change"],
            mode="lines", name="YoY % Change",
            fill="tozeroy", line=dict(color="#ff7f0e", width=2),
        ))
        fig2.update_layout(
            title="Average Hourly Earnings — Year-over-Year % Change",
            yaxis_title="% Change",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            hovermode="x unified",
            height=400,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "Average hourly earnings measure the average pay per hour for all private-sector employees. "
        "Year-over-year growth is a key indicator of wage inflation pressures."
    )
else:
    st.info("No wage data available.")
