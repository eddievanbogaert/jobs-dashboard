"""Shared page configuration for consistent titles, favicon, and styling."""

import os

import streamlit as st

_FAVICON_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "favicon.png")
_DASHBOARD_URL = "https://jobs-dashboard-187197452217.us-central1.run.app"

# Custom CSS: loading animation + OG meta tags
_CUSTOM_HEAD = f"""\
<meta property="og:title" content="U.S. Labor Market Dashboard">
<meta property="og:description" content="Real-time labor market indicators from BLS, FRED & SSA — employment, wages, industry trends, and more.">
<meta property="og:image" content="{_DASHBOARD_URL}/app/static/og-image.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="U.S. Labor Market Dashboard">
<meta name="twitter:description" content="Real-time labor market indicators from BLS, FRED & SSA.">
<meta name="twitter:image" content="{_DASHBOARD_URL}/app/static/og-image.png">
"""

_CUSTOM_CSS = """\
<style>
/* Subtle status widget — no background */
[data-testid="stStatusWidget"] {
    background: transparent;
    border: none;
    box-shadow: none;
}

/* Subtle top decoration bar — thin neutral line */
[data-testid="stDecoration"] {
    background-image: none !important;
    background-color: #ccc !important;
    height: 2px !important;
}

/* Smooth page transitions */
[data-testid="stAppViewBlockContainer"] {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""


def setup_page(page_name: str):
    """Configure a dashboard page with consistent title, favicon, and styling.

    Must be called as the first Streamlit command on each page.
    """
    st.set_page_config(
        page_title=f"US Labor Market Dashboard | {page_name}",
        page_icon=_FAVICON_PATH,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CUSTOM_HEAD, unsafe_allow_html=True)
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)
