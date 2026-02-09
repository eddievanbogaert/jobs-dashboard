output "dashboard_url" {
  description = "Public URL of the Streamlit dashboard"
  value       = google_cloud_run_v2_service.dashboard.uri
}

output "ingest_function_url" {
  description = "URL of the FRED ingestion Cloud Function"
  value       = google_cloudfunctions2_function.ingest_fred.url
}

output "transform_function_url" {
  description = "URL of the analytics transform Cloud Function"
  value       = google_cloudfunctions2_function.transform_analytics.url
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.labor_market.dataset_id
}
