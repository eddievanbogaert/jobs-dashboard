"""BigQuery client singleton."""

import streamlit as st
from google.cloud import bigquery

PROJECT = "jobs-dashboard"
DATASET = "labor_market"


@st.cache_resource
def get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT)
