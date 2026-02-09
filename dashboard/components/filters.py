"""Shared filter/selector components."""

from datetime import date

import streamlit as st


def date_range_selector(
    default_years: int = 5,
    key_prefix: str = "",
) -> str:
    """Sidebar date range picker. Returns start_date as ISO string."""
    options = {
        "1 Year": 1,
        "3 Years": 3,
        "5 Years": 5,
        "10 Years": 10,
        "All (since 2000)": 25,
    }
    choice = st.sidebar.selectbox(
        "Date range",
        list(options.keys()),
        index=list(options.values()).index(default_years),
        key=f"{key_prefix}_date_range",
    )
    years = options[choice]
    start_year = max(date.today().year - years, 2000)
    return f"{start_year}-01-01"
