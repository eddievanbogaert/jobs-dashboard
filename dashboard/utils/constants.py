"""Series metadata, display names, and color palette."""

SERIES_META = {
    "PAYEMS": {
        "display_name": "Total Nonfarm Payrolls",
        "short_name": "Nonfarm Payrolls",
        "units": "Thousands of Persons",
        "format": ",.0f",
        "change_format": "+,.0f",
        "category": "employment",
        "color": "#1f77b4",
    },
    "UNRATE": {
        "display_name": "Unemployment Rate",
        "short_name": "Unemployment (U-3)",
        "units": "%",
        "format": ".1f",
        "change_format": "+.1f",
        "category": "unemployment",
        "color": "#d62728",
    },
    "CIVPART": {
        "display_name": "Labor Force Participation Rate",
        "short_name": "Participation Rate",
        "units": "%",
        "format": ".1f",
        "change_format": "+.1f",
        "category": "employment",
        "color": "#2ca02c",
    },
    "CES0500000003": {
        "display_name": "Average Hourly Earnings (Private)",
        "short_name": "Avg. Hourly Earnings",
        "units": "$/hr",
        "format": ",.2f",
        "change_format": "+,.2f",
        "category": "wages",
        "color": "#ff7f0e",
    },
    "JTSJOL": {
        "display_name": "Job Openings (JOLTS)",
        "short_name": "Job Openings",
        "units": "Thousands",
        "format": ",.0f",
        "change_format": "+,.0f",
        "category": "job_openings",
        "color": "#9467bd",
    },
    "ICSA": {
        "display_name": "Initial Jobless Claims",
        "short_name": "Jobless Claims",
        "units": "",
        "format": ",.0f",
        "change_format": "+,.0f",
        "category": "claims",
        "color": "#8c564b",
    },
    "U6RATE": {
        "display_name": "U-6 Underemployment Rate",
        "short_name": "Underemployment (U-6)",
        "units": "%",
        "format": ".1f",
        "change_format": "+.1f",
        "category": "unemployment",
        "color": "#e377c2",
    },
    "EMRATIO": {
        "display_name": "Employment-Population Ratio",
        "short_name": "Emp-Pop Ratio",
        "units": "%",
        "format": ".1f",
        "change_format": "+.1f",
        "category": "employment",
        "color": "#17becf",
    },
}

# Ordered list for overview page
OVERVIEW_SERIES = ["PAYEMS", "UNRATE", "CIVPART", "CES0500000003", "JTSJOL", "ICSA", "U6RATE", "EMRATIO"]

# Which direction is "good" for each series (used for coloring changes)
# True = higher is better, False = lower is better
HIGHER_IS_BETTER = {
    "PAYEMS": True,
    "UNRATE": False,
    "CIVPART": True,
    "CES0500000003": True,
    "JTSJOL": True,
    "ICSA": False,
    "U6RATE": False,
    "EMRATIO": True,
}
