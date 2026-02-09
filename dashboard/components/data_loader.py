"""BigQuery data loading with Streamlit caching."""

import pandas as pd
import streamlit as st
from google.cloud import bigquery

from utils.bq_client import DATASET, PROJECT, get_client


@st.cache_data(ttl=3600)
def load_series(series_id: str, start_date: str = "2000-01-01") -> pd.DataFrame:
    """Load analytics data for a single series."""
    client = get_client()
    query = f"""
        SELECT
            observation_date, value,
            mom_change, mom_pct_change,
            yoy_change, yoy_pct_change,
            ma_3m, ma_12m, z_score_5y
        FROM `{PROJECT}.{DATASET}.analytics_monthly`
        WHERE series_id = @series_id
          AND observation_date >= @start_date
        ORDER BY observation_date
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("series_id", "STRING", series_id),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        ]
    )
    return client.query(query, job_config=job_config).to_dataframe()


@st.cache_data(ttl=3600)
def load_latest_values() -> pd.DataFrame:
    """Load the most recent value for every series (for the overview scorecard)."""
    client = get_client()
    query = f"""
        WITH latest AS (
            SELECT
                series_id,
                observation_date,
                value,
                mom_change,
                mom_pct_change,
                yoy_change,
                yoy_pct_change,
                z_score_5y,
                ROW_NUMBER() OVER (PARTITION BY series_id ORDER BY observation_date DESC) AS rn
            FROM `{PROJECT}.{DATASET}.analytics_monthly`
        )
        SELECT * EXCEPT(rn)
        FROM latest
        WHERE rn = 1
        ORDER BY series_id
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600)
def load_multiple_series(series_ids: list[str], start_date: str = "2000-01-01") -> pd.DataFrame:
    """Load analytics data for multiple series."""
    client = get_client()
    query = f"""
        SELECT
            series_id, observation_date, value,
            mom_change, mom_pct_change,
            yoy_change, yoy_pct_change,
            ma_3m, ma_12m, z_score_5y
        FROM `{PROJECT}.{DATASET}.analytics_monthly`
        WHERE series_id IN UNNEST(@series_ids)
          AND observation_date >= @start_date
        ORDER BY series_id, observation_date
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("series_ids", "STRING", series_ids),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        ]
    )
    return client.query(query, job_config=job_config).to_dataframe()


@st.cache_data(ttl=3600)
def load_raw_series(series_id: str, start_date: str = "2000-01-01") -> pd.DataFrame:
    """Load raw observations for a series (used for weekly data like ICSA)."""
    client = get_client()
    query = f"""
        SELECT observation_date, value
        FROM `{PROJECT}.{DATASET}.raw_fred_observations`
        WHERE series_id = @series_id
          AND observation_date >= @start_date
        ORDER BY observation_date
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("series_id", "STRING", series_id),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        ]
    )
    return client.query(query, job_config=job_config).to_dataframe()
