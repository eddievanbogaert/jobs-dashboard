# --- Service Accounts ---

resource "google_service_account" "ingest" {
  account_id   = "ingest-fred"
  display_name = "FRED Data Ingestion"
  project      = var.project_id
}

resource "google_service_account" "dashboard" {
  account_id   = "dashboard"
  display_name = "Dashboard Cloud Run Service"
  project      = var.project_id
}

resource "google_service_account" "scheduler" {
  account_id   = "scheduler-invoker"
  display_name = "Cloud Scheduler HTTP Invoker"
  project      = var.project_id
}

# --- Ingestion SA permissions ---

resource "google_project_iam_member" "ingest_bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}

resource "google_project_iam_member" "ingest_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.ingest.email}"
}

resource "google_secret_manager_secret_iam_member" "ingest_fred_key" {
  secret_id = google_secret_manager_secret.fred_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ingest.email}"
}

# --- Dashboard SA permissions ---

resource "google_project_iam_member" "dashboard_bq_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.dashboard.email}"
}

resource "google_project_iam_member" "dashboard_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dashboard.email}"
}

# --- Scheduler SA: allowed to invoke Cloud Run (Cloud Functions 2nd gen) ---

resource "google_cloud_run_v2_service_iam_member" "scheduler_invoke_ingest" {
  project  = var.project_id
  location = var.region
  name     = google_cloudfunctions2_function.ingest_fred.service_config[0].service
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

resource "google_cloud_run_v2_service_iam_member" "scheduler_invoke_transform" {
  project  = var.project_id
  location = var.region
  name     = google_cloudfunctions2_function.transform_analytics.service_config[0].service
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

# --- Cloud Build default SA permissions ---

resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# --- Public access to dashboard ---

resource "google_cloud_run_v2_service_iam_member" "dashboard_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.dashboard.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
