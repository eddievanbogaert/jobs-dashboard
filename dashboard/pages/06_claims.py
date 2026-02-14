"""Claims page — Weekly initial jobless claims."""

from components.page_config import setup_page

setup_page("Claims")

import streamlit as st

from components.data_loader import load_raw_series, load_series
from components.filters import date_range_selector
from utils.constants import SERIES_META

st.header("Initial Jobless Claims")
start_date = date_range_selector(default_years=3, key_prefix="claims")

# --- Weekly Claims ---
st.subheader("Weekly Initial Claims")
df_raw = load_raw_series("ICSA", start_date=start_date)

if not df_raw.empty:
    import plotly.graph_objects as go

    # Compute 4-week moving average
    df_raw = df_raw.sort_values("observation_date")
    df_raw["ma_4w"] = df_raw["value"].rolling(window=4).mean()

    meta = SERIES_META["ICSA"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_raw["observation_date"], y=df_raw["value"],
        mode="lines", name="Weekly Claims",
        line=dict(color=meta["color"], width=1),
        opacity=0.6,
    ))
    fig.add_trace(go.Scatter(
        x=df_raw["observation_date"], y=df_raw["ma_4w"],
        mode="lines", name="4-Week Moving Avg",
        line=dict(color=meta["color"], width=2.5),
    ))
    fig.update_layout(
        title="Initial Jobless Claims (Weekly)",
        yaxis_title="Claims",
        template="plotly_white",
        margin=dict(l=40, r=20, t=40, b=40),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Initial jobless claims represent the number of people filing for unemployment insurance "
        "for the first time each week. The 4-week moving average smooths out weekly volatility."
    )

    # --- Year-over-year comparison ---
    st.subheader("Year-over-Year Comparison")
    import pandas as pd

    df_raw["observation_date"] = pd.to_datetime(df_raw["observation_date"])
    df_raw["year"] = df_raw["observation_date"].dt.year
    df_raw["week"] = df_raw["observation_date"].dt.isocalendar().week.astype(int)
    current_year = df_raw["year"].max()
    years_to_show = [current_year, current_year - 1]

    fig2 = go.Figure()
    for yr in years_to_show:
        yr_data = df_raw[df_raw["year"] == yr].sort_values("week")
        fig2.add_trace(go.Scatter(
            x=yr_data["week"], y=yr_data["value"],
            mode="lines", name=str(yr),
            line=dict(width=2 if yr == current_year else 1.5,
                      dash=None if yr == current_year else "dot"),
        ))

    fig2.update_layout(
        title="Claims by Week of Year",
        xaxis_title="Week Number",
        yaxis_title="Claims",
        template="plotly_white",
        margin=dict(l=40, r=20, t=40, b=40),
        hovermode="x unified",
        height=400,
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No claims data available.")
