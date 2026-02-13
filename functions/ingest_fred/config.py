"""FRED series configuration for labor market data ingestion."""

FRED_SERIES = [
    {
        "series_id": "PAYEMS",
        "name": "Total Nonfarm Payrolls",
        "frequency": "monthly",
        "units": "Thousands of Persons",
        "category": "employment",
    },
    {
        "series_id": "UNRATE",
        "name": "Unemployment Rate",
        "frequency": "monthly",
        "units": "Percent",
        "category": "unemployment",
    },
    {
        "series_id": "CIVPART",
        "name": "Labor Force Participation Rate",
        "frequency": "monthly",
        "units": "Percent",
        "category": "employment",
    },
    {
        "series_id": "CES0500000003",
        "name": "Average Hourly Earnings (Private)",
        "frequency": "monthly",
        "units": "Dollars per Hour",
        "category": "wages",
    },
    {
        "series_id": "JTSJOL",
        "name": "Job Openings (JOLTS)",
        "frequency": "monthly",
        "units": "Thousands",
        "category": "job_openings",
    },
    {
        "series_id": "ICSA",
        "name": "Initial Jobless Claims",
        "frequency": "weekly",
        "units": "Number",
        "category": "claims",
    },
    {
        "series_id": "U6RATE",
        "name": "U-6 Underemployment Rate",
        "frequency": "monthly",
        "units": "Percent",
        "category": "unemployment",
    },
    {
        "series_id": "EMRATIO",
        "name": "Employment-Population Ratio",
        "frequency": "monthly",
        "units": "Percent",
        "category": "employment",
    },
]

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
DEFAULT_OBSERVATION_START = "2000-01-01"
