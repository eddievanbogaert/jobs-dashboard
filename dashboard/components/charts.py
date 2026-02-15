"""Reusable Plotly chart builders."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import SERIES_META

LAYOUT_DEFAULTS = dict(
    template="plotly_white",
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def time_series_chart(
    df: pd.DataFrame,
    series_id: str,
    y_col: str = "value",
    title: str | None = None,
    show_ma: bool = False,
) -> go.Figure:
    """Line chart for a single time series."""
    meta = SERIES_META.get(series_id, {})
    color = meta.get("color", "#1f77b4")
    name = meta.get("short_name", series_id)
    t = title or name

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["observation_date"], y=df[y_col],
        mode="lines", name=name,
        line=dict(color=color, width=2),
    ))

    if show_ma and "ma_12m" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["observation_date"], y=df["ma_12m"],
            mode="lines", name="12-mo Avg",
            line=dict(color=color, width=1, dash="dash"),
        ))

    fig.update_layout(title=t, yaxis_title=meta.get("units", ""), **LAYOUT_DEFAULTS)
    return fig


def bar_chart_changes(
    df: pd.DataFrame,
    series_id: str,
    change_col: str = "mom_change",
    title: str | None = None,
) -> go.Figure:
    """Bar chart showing period-over-period changes."""
    meta = SERIES_META.get(series_id, {})
    name = meta.get("short_name", series_id)
    t = title or f"{name} — Monthly Change"

    colors = ["#2ca02c" if v >= 0 else "#d62728" for v in df[change_col]]

    fig = go.Figure(go.Bar(
        x=df["observation_date"], y=df[change_col],
        marker_color=colors, name=change_col,
    ))
    fig.update_layout(title=t, yaxis_title=meta.get("units", ""), **LAYOUT_DEFAULTS)
    return fig


def dual_series_chart(
    df: pd.DataFrame,
    series_ids: list[str],
    title: str = "",
) -> go.Figure:
    """Overlay two series on dual y-axes."""
    fig = go.Figure()
    for i, sid in enumerate(series_ids[:2]):
        meta = SERIES_META.get(sid, {})
        sdf = df[df["series_id"] == sid]
        yaxis = "y" if i == 0 else "y2"
        fig.add_trace(go.Scatter(
            x=sdf["observation_date"], y=sdf["value"],
            mode="lines", name=meta.get("short_name", sid),
            line=dict(color=meta.get("color", "#333"), width=2),
            yaxis=yaxis,
        ))

    meta0 = SERIES_META.get(series_ids[0], {})
    meta1 = SERIES_META.get(series_ids[1], {}) if len(series_ids) > 1 else {}
    fig.update_layout(
        title=title,
        yaxis=dict(title=meta0.get("units", ""), side="left"),
        yaxis2=dict(title=meta1.get("units", ""), side="right", overlaying="y"),
        **LAYOUT_DEFAULTS,
    )
    return fig


def scatter_chart(
    df_x: pd.DataFrame,
    df_y: pd.DataFrame,
    x_series: str,
    y_series: str,
    title: str = "",
) -> go.Figure:
    """Scatter plot between two series (e.g., Beveridge curve)."""
    merged = pd.merge(
        df_x[["observation_date", "value"]].rename(columns={"value": "x"}),
        df_y[["observation_date", "value"]].rename(columns={"value": "y"}),
        on="observation_date",
    )
    merged["observation_date"] = pd.to_datetime(merged["observation_date"])
    meta_x = SERIES_META.get(x_series, {})
    meta_y = SERIES_META.get(y_series, {})

    fig = px.scatter(
        merged, x="x", y="y",
        color=merged["observation_date"].dt.year.astype(str),
        hover_data=["observation_date"],
        title=title,
        labels={"x": meta_x.get("short_name", x_series), "y": meta_y.get("short_name", y_series)},
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    return fig


def stacked_area_chart(
    df: pd.DataFrame,
    series_ids: list[str],
    title: str = "",
) -> go.Figure:
    """Stacked area chart for multiple series (e.g., industry employment)."""
    fig = go.Figure()
    for sid in series_ids:
        meta = SERIES_META.get(sid, {})
        sdf = df[df["series_id"] == sid].sort_values("observation_date")
        if sdf.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sdf["observation_date"], y=sdf["value"],
            mode="lines",
            name=meta.get("short_name", sid),
            line=dict(width=0.5, color=meta.get("color", "#333")),
            stackgroup="one",
        ))

    fig.update_layout(
        title=title,
        yaxis_title="Thousands of Persons",
        height=500,
        **LAYOUT_DEFAULTS,
    )
    return fig


def industry_changes_bar(
    df: pd.DataFrame,
    series_ids: list[str],
    title: str = "Monthly Employment Change by Industry",
) -> go.Figure:
    """Horizontal bar chart of latest MoM change per series."""
    rows = []
    for sid in series_ids:
        meta = SERIES_META.get(sid, {})
        sdf = df[df["series_id"] == sid].sort_values("observation_date")
        if sdf.empty:
            continue
        latest = sdf.iloc[-1]
        mom = latest.get("mom_change")
        if mom is None:
            continue
        rows.append({
            "name": meta.get("short_name", sid),
            "change": mom,
            "color": meta.get("color", "#333"),
        })

    if not rows:
        return go.Figure()

    bar_df = pd.DataFrame(rows).sort_values("change")
    colors = ["#2ca02c" if v >= 0 else "#d62728" for v in bar_df["change"]]

    fig = go.Figure(go.Bar(
        x=bar_df["change"],
        y=bar_df["name"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Change (Thousands)",
        height=max(350, len(rows) * 35),
        **LAYOUT_DEFAULTS,
    )
    return fig
