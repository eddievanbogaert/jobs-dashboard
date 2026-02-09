"""Cloud Function: Compute analytics from raw FRED observations in BigQuery."""

import json
import os

import functions_framework
from google.cloud import bigquery

PROJECT = os.environ.get("GCP_PROJECT", "jobs-dashboard")
DATASET = os.environ.get("BQ_DATASET", "labor_market")

TRANSFORM_SQL = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.analytics_monthly` AS
WITH ordered AS (
    SELECT
        series_id,
        observation_date,
        value,
        LAG(value) OVER (PARTITION BY series_id ORDER BY observation_date) AS prev_value,
        LAG(value, 12) OVER (PARTITION BY series_id ORDER BY observation_date) AS value_12m_ago,
        AVG(value) OVER (
            PARTITION BY series_id ORDER BY observation_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ma_3m,
        AVG(value) OVER (
            PARTITION BY series_id ORDER BY observation_date
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS ma_12m,
        AVG(value) OVER (
            PARTITION BY series_id ORDER BY observation_date
            ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
        ) AS mean_5y,
        STDDEV(value) OVER (
            PARTITION BY series_id ORDER BY observation_date
            ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
        ) AS stddev_5y
    FROM (
        SELECT
            series_id,
            observation_date,
            value,
            ROW_NUMBER() OVER (
                PARTITION BY series_id, observation_date
                ORDER BY ingested_at DESC
            ) AS rn
        FROM `{PROJECT}.{DATASET}.raw_fred_observations`
    )
    WHERE rn = 1
)
SELECT
    series_id,
    observation_date,
    value,
    value - prev_value AS mom_change,
    SAFE_DIVIDE(value - prev_value, ABS(prev_value)) * 100 AS mom_pct_change,
    value - value_12m_ago AS yoy_change,
    SAFE_DIVIDE(value - value_12m_ago, ABS(value_12m_ago)) * 100 AS yoy_pct_change,
    ROUND(ma_3m, 4) AS ma_3m,
    ROUND(ma_12m, 4) AS ma_12m,
    SAFE_DIVIDE(value - mean_5y, stddev_5y) AS z_score_5y
FROM ordered
ORDER BY series_id, observation_date
"""


@functions_framework.http
def transform(request):
    """HTTP entry point for the analytics transform function."""
    client = bigquery.Client(project=PROJECT)

    try:
        query_job = client.query(TRANSFORM_SQL)
        query_job.result()

        # Get row count of the output table
        table = client.get_table(f"{PROJECT}.{DATASET}.analytics_monthly")
        row_count = table.num_rows

        return (
            json.dumps({
                "status": "ok",
                "table": f"{PROJECT}.{DATASET}.analytics_monthly",
                "rows": row_count,
            }),
            200,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        return (
            json.dumps({"status": "error", "error": str(e)}),
            500,
            {"Content-Type": "application/json"},
        )
