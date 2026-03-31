"""BigQuery client singleton."""

import os

import streamlit as st
from google.cloud import bigquery

PROJECT = os.environ.get("GCP_PROJECT")
DATASET = "labor_market"


@st.cache_resource
def get_client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT)
