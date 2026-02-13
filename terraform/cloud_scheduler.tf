# Monthly ingestion: Saturday after first-Friday BLS release (9th-15th), 6 AM ET.
# FRED updates lag BLS by hours; Saturday morning provides a safe buffer.
resource "google_cloud_scheduler_job" "ingest_monthly" {
  name      = "ingest-monthly"
  project   = var.project_id
  region    = var.region
  schedule  = "0 6 9-15 * 6"
  time_zone = "America/New_York"

  http_target {
    uri         = google_cloudfunctions2_function.ingest_fred.url
    http_method = "POST"
    body        = base64encode(jsonencode({ backfill = false }))
    headers     = { "Content-Type" = "application/json" }

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = google_cloudfunctions2_function.ingest_fred.url
    }
  }

  retry_config {
    retry_count          = 2
    max_backoff_duration = "3600s"
  }

  depends_on = [google_project_service.apis["cloudscheduler.googleapis.com"]]
}

# Weekly ingestion: Thursday noon ET for Initial Jobless Claims (released Thursday morning).
resource "google_cloud_scheduler_job" "ingest_weekly" {
  name      = "ingest-weekly"
  project   = var.project_id
  region    = var.region
  schedule  = "0 12 * * 4"
  time_zone = "America/New_York"

  http_target {
    uri         = google_cloudfunctions2_function.ingest_fred.url
    http_method = "POST"
    body        = base64encode(jsonencode({ series = ["ICSA"] }))
    headers     = { "Content-Type" = "application/json" }

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = google_cloudfunctions2_function.ingest_fred.url
    }
  }

  retry_config {
    retry_count          = 2
    max_backoff_duration = "3600s"
  }

  depends_on = [google_project_service.apis["cloudscheduler.googleapis.com"]]
}

# Transform analytics: 30 minutes after monthly ingestion.
resource "google_cloud_scheduler_job" "transform_monthly" {
  name      = "transform-monthly"
  project   = var.project_id
  region    = var.region
  schedule  = "30 6 9-15 * 6"
  time_zone = "America/New_York"

  http_target {
    uri         = google_cloudfunctions2_function.transform_analytics.url
    http_method = "POST"
    body        = base64encode(jsonencode({}))
    headers     = { "Content-Type" = "application/json" }

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = google_cloudfunctions2_function.transform_analytics.url
    }
  }

  retry_config {
    retry_count          = 2
    max_backoff_duration = "3600s"
  }

  depends_on = [google_project_service.apis["cloudscheduler.googleapis.com"]]
}

# Transform after weekly claims ingestion.
resource "google_cloud_scheduler_job" "transform_weekly" {
  name      = "transform-weekly"
  project   = var.project_id
  region    = var.region
  schedule  = "30 12 * * 4"
  time_zone = "America/New_York"

  http_target {
    uri         = google_cloudfunctions2_function.transform_analytics.url
    http_method = "POST"
    body        = base64encode(jsonencode({}))
    headers     = { "Content-Type" = "application/json" }

    oidc_token {
      service_account_email = google_service_account.scheduler.email
      audience              = google_cloudfunctions2_function.transform_analytics.url
    }
  }

  retry_config {
    retry_count          = 2
    max_backoff_duration = "3600s"
  }

  depends_on = [google_project_service.apis["cloudscheduler.googleapis.com"]]
}
