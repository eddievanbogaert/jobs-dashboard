"""Analysis page — Written assessment of current labor market conditions."""

from components.page_config import setup_page

setup_page("Analysis")

import streamlit as st

st.header("Labor Market Analysis")
st.caption("Updated April 2026")

st.markdown("""
The U.S. labor market in early 2026 is settled into a **low-hire, low-fire equilibrium**
that shows few signs of breaking in either direction. Unemployment has drifted up to
4.3%, meaningfully above the 3.4–3.7% range of 2023, while the labor force participation
rate remains stalled near 62% — well short of pre-pandemic levels — and the
employment-population ratio has plateaued around 59%. Together, these suggest a workforce
that is neither rapidly expanding nor contracting, but gradually losing momentum.

Beneath the surface, **labor fluidity has deteriorated**. The JOLTS hiring rate fell to 3.1%
in February, its lowest since the early COVID lockdowns, and the quits rate sits at a
depressed 1.9%, signaling that workers see limited upside in switching jobs. Job openings
have fallen to roughly 7 million, nearly half their 2022 peak. Meanwhile, initial claims
remain remarkably low around 205K, confirming that employers are holding onto existing
workers even as they pull back on new hiring.

**Job creation is increasingly narrow.** Healthcare and construction continue to drive the
bulk of payroll gains, while federal government employment has declined by roughly 330,000
since late 2024. Information and financial activities have also shed jobs. Wage growth has
moderated to 3.8% year-over-year but remains positive in real terms at +1.4%, offering some
support to consumer spending.

This is not a crisis — but the combination of cooling hiring, stagnant participation, and
concentrated sector growth warrants close monitoring heading into mid-2026.
""")

st.divider()
st.caption("Prepared by Claude (Anthropic) using BLS, FRED, and SSA data tracked by this dashboard.")
