"""Number and date formatting utilities."""

from datetime import date


def format_value(value: float, fmt: str) -> str:
    if value is None:
        return "N/A"
    return f"{value:{fmt}}"


def format_date_label(d: date) -> str:
    return d.strftime("%b %Y")


def format_date_short(d: date) -> str:
    return d.strftime("%m/%Y")
