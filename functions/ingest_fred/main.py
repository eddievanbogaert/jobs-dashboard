"""Cloud Function: Ingest labor market data from FRED API into BigQuery."""

import json
import os
from datetime import datetime, timezone

import functions_framework
import requests
from google.cloud import bigquery

from config import DEFAULT_OBSERVATION_START, FRED_BASE_URL, FRED_SERIES

PROJECT = os.environ.get("GCP_PROJECT", "jobs-dashboard")
DATASET = os.environ.get("BQ_DATASET", "labor_market")
TABLE = "raw_fred_observations"


def get_fred_api_key() -> str:
    key = os.environ.get("FRED_API_KEY", "")
    if not key:
        raise RuntimeError("FRED_API_KEY environment variable is not set")
    return key


def get_last_observation_date(client: bigquery.Client, series_id: str) -> str | None:
    """Return the most recent observation_date for a series, or None."""
    query = f"""
        SELECT MAX(observation_date) AS last_date
        FROM `{PROJECT}.{DATASET}.{TABLE}`
        WHERE series_id = @series_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("series_id", "STRING", series_id),
        ]
    )
    rows = list(client.query(query, job_config=job_config).result())
    if rows and rows[0].last_date:
        return rows[0].last_date.isoformat()
    return None


def fetch_fred_series(api_key: str, series_id: str, observation_start: str) -> list[dict]:
    """Fetch observations from FRED API for a single series."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
        "sort_order": "asc",
    }
    resp = requests.get(FRED_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("observations", [])


def load_to_bigquery(client: bigquery.Client, rows: list[dict]) -> int:
    """Load rows into BigQuery using a MERGE (upsert) via a temp table."""
    if not rows:
        return 0

    table_ref = f"{PROJECT}.{DATASET}.{TABLE}"
    temp_table = f"{PROJECT}.{DATASET}._temp_ingest_{int(datetime.now(timezone.utc).timestamp())}"

    # Load into a temporary table first
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("series_id", "STRING"),
            bigquery.SchemaField("observation_date", "DATE"),
            bigquery.SchemaField("value", "FLOAT64"),
            bigquery.SchemaField("realtime_start", "DATE"),
            bigquery.SchemaField("realtime_end", "DATE"),
            bigquery.SchemaField("ingested_at", "TIMESTAMP"),
        ],
        write_disposition="WRITE_TRUNCATE",
    )
    load_job = client.load_table_from_json(rows, temp_table, job_config=job_config)
    load_job.result()

    # MERGE from temp into target
    merge_sql = f"""
        MERGE `{table_ref}` AS target
        USING `{temp_table}` AS source
        ON target.series_id = source.series_id
           AND target.observation_date = source.observation_date
        WHEN MATCHED THEN
            UPDATE SET
                value = source.value,
                realtime_start = source.realtime_start,
                realtime_end = source.realtime_end,
                ingested_at = source.ingested_at
        WHEN NOT MATCHED THEN
            INSERT (series_id, observation_date, value, realtime_start, realtime_end, ingested_at)
            VALUES (source.series_id, source.observation_date, source.value,
                    source.realtime_start, source.realtime_end, source.ingested_at)
    """
    client.query(merge_sql).result()
    client.delete_table(temp_table, not_found_ok=True)
    return len(rows)


@functions_framework.http
def ingest(request):
    """HTTP entry point for the FRED ingestion function."""
    request_json = request.get_json(silent=True) or {}
    backfill = request_json.get("backfill", False)
    series_filter = request_json.get("series")  # optional list of series IDs

    api_key = get_fred_api_key()
    client = bigquery.Client(project=PROJECT)
    now = datetime.now(timezone.utc).isoformat()

    results = {}
    errors = {}

    series_list = FRED_SERIES
    if series_filter:
        series_list = [s for s in FRED_SERIES if s["series_id"] in series_filter]

    for series_cfg in series_list:
        sid = series_cfg["series_id"]
        try:
            if backfill:
                obs_start = request_json.get("observation_start", DEFAULT_OBSERVATION_START)
            else:
                last_date = get_last_observation_date(client, sid)
                obs_start = last_date if last_date else DEFAULT_OBSERVATION_START

            observations = fetch_fred_series(api_key, sid, obs_start)

            rows = []
            for obs in observations:
                val = obs.get("value", ".")
                if val == ".":
                    continue  # FRED uses "." for missing values
                rows.append({
                    "series_id": sid,
                    "observation_date": obs["date"],
                    "value": float(val),
                    "realtime_start": obs.get("realtime_start"),
                    "realtime_end": obs.get("realtime_end"),
                    "ingested_at": now,
                })

            count = load_to_bigquery(client, rows)
            results[sid] = {"status": "ok", "rows_loaded": count}
        except Exception as e:
            errors[sid] = str(e)
            results[sid] = {"status": "error", "error": str(e)}

    status_code = 200 if not errors else 207
    return (
        json.dumps({"results": results, "errors": errors}, indent=2),
        status_code,
        {"Content-Type": "application/json"},
    )
