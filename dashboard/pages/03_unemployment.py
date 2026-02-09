"""Unemployment page — U-3 and U-6 rates."""

import streamlit as st

from components.charts import dual_series_chart, time_series_chart
from components.data_loader import load_multiple_series, load_series
from components.filters import date_range_selector

st.header("Unemployment")
start_date = date_range_selector(default_years=5, key_prefix="unemployment")

# --- U-3 Unemployment Rate ---
st.subheader("Unemployment Rate (U-3)")
df_unrate = load_series("UNRATE", start_date=start_date)

if not df_unrate.empty:
    fig = time_series_chart(df_unrate, "UNRATE", show_ma=True, title="U-3 Unemployment Rate")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No U-3 data available.")

st.markdown("---")

# --- U-3 vs U-6 Comparison ---
st.subheader("U-3 vs. U-6 Comparison")
st.caption(
    "U-3 is the official unemployment rate. U-6 is a broader measure that includes "
    "discouraged workers and those employed part-time for economic reasons."
)

df_both = load_multiple_series(["UNRATE", "U6RATE"], start_date=start_date)

if not df_both.empty:
    fig = dual_series_chart(df_both, ["UNRATE", "U6RATE"], title="U-3 vs. U-6 Unemployment")
    st.plotly_chart(fig, use_container_width=True)

    # Spread analysis
    import pandas as pd
    df_u3 = df_both[df_both["series_id"] == "UNRATE"][["observation_date", "value"]].rename(columns={"value": "u3"})
    df_u6 = df_both[df_both["series_id"] == "U6RATE"][["observation_date", "value"]].rename(columns={"value": "u6"})
    spread = pd.merge(df_u3, df_u6, on="observation_date")
    spread["spread"] = spread["u6"] - spread["u3"]

    if not spread.empty:
        import plotly.graph_objects as go
        fig2 = go.Figure(go.Scatter(
            x=spread["observation_date"], y=spread["spread"],
            mode="lines", name="U-6 minus U-3",
            fill="tozeroy", line=dict(color="#9467bd", width=1.5),
        ))
        fig2.update_layout(
            title="U-6 / U-3 Spread",
            yaxis_title="Percentage Points",
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40),
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(
            "The spread between U-6 and U-3 captures the 'hidden' slack in the labor market — "
            "a wider spread suggests more underemployment relative to headline unemployment."
        )
else:
    st.info("No unemployment comparison data available.")
