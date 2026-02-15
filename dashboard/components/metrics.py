"""KPI card components for the dashboard."""

import streamlit as st

from utils.constants import HIGHER_IS_BETTER, SERIES_META
from utils.formatting import format_date_label, format_value


def render_kpi_card(series_id: str, row: dict):
    """Render a single KPI metric card using st.metric."""
    meta = SERIES_META.get(series_id, {})
    name = meta.get("short_name", series_id)
    fmt = meta.get("format", ".1f")
    chg_fmt = meta.get("change_format", "+.1f")

    value = row.get("value")
    mom = row.get("mom_change")
    date_label = format_date_label(row["observation_date"]) if row.get("observation_date") else ""

    # Apply display divisor (e.g., thousands → millions)
    divisor = meta.get("display_divisor")
    if divisor and value is not None:
        value = value / divisor
    if divisor and mom is not None:
        mom = mom / divisor

    # Determine delta color direction
    higher_good = HIGHER_IS_BETTER.get(series_id, True)
    delta_color = "normal" if higher_good else "inverse"

    delta_str = None
    if mom is not None:
        units = meta.get("units", "")
        suffix = f" {units}" if units and units != "%" else units
        delta_str = f"{format_value(mom, chg_fmt)}{suffix} MoM"

    st.metric(
        label=f"{name} ({date_label})",
        value=f"{format_value(value, fmt)} {meta.get('units', '')}".strip(),
        delta=delta_str,
        delta_color=delta_color,
    )
