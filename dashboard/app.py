"""U.S. Labor Market Dashboard — Main entry point."""

from components.page_config import setup_page

setup_page("Home")

import streamlit as st

st.sidebar.title("U.S. Labor Market Dashboard")
st.sidebar.markdown(
    "Data sourced from [FRED](https://fred.stlouisfed.org/) (Federal Reserve Bank of St. Louis). "
    "Updated monthly after BLS releases and weekly for jobless claims."
)
st.sidebar.markdown("---")

st.title("U.S. Labor Market Dashboard")
st.markdown(
    """
    Welcome to the U.S. Labor Market Dashboard. This tool provides up-to-date
    visualizations and analysis of key employment and labor market indicators
    published by the Bureau of Labor Statistics (BLS).

    **Navigate** using the sidebar to explore:
    - **Overview** — Scorecard of all key indicators
    - **Employment** — Nonfarm payrolls, participation rate, employment-population ratio
    - **Unemployment** — U-3 and U-6 rates with historical context
    - **Wages** — Average hourly earnings trends
    - **Job Openings** — JOLTS data and the Beveridge curve
    - **Claims** — Weekly initial jobless claims
    - **Industry** — Employment breakdown across 12 major industry sectors
    - **Net Compensation** — SSA wage distribution data (2004–2023)

    Data refreshes automatically after each monthly BLS Employment Situation release
    and weekly for Initial Jobless Claims.
    """
)
