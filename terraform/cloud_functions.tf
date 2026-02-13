# --- Source bucket for function code ---

resource "google_storage_bucket" "functions_source" {
  name                        = "${var.project_id}-functions-source"
  location                    = var.region
  project                     = var.project_id
  uniform_bucket_level_access = true
  force_destroy               = true

  depends_on = [google_project_service.apis["cloudfunctions.googleapis.com"]]
}

# --- Ingest FRED function ---

data "archive_file" "ingest_fred" {
  type        = "zip"
  source_dir  = "${path.module}/../functions/ingest_fred"
  output_path = "${path.module}/../functions/ingest_fred/deploy.zip"
  excludes    = ["deploy.zip", "__pycache__", "*.pyc", "test_*.py"]
}

resource "google_storage_bucket_object" "ingest_fred_source" {
  name   = "ingest_fred/${data.archive_file.ingest_fred.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.ingest_fred.output_path
}

resource "google_cloudfunctions2_function" "ingest_fred" {
  name     = "ingest-fred"
  location = var.region
  project  = var.project_id

  build_config {
    runtime     = "python312"
    entry_point = "ingest"
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.ingest_fred_source.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "512Mi"
    timeout_seconds       = 300
    service_account_email = google_service_account.ingest.email

    environment_variables = {
      GCP_PROJECT = var.project_id
      BQ_DATASET  = google_bigquery_dataset.labor_market.dataset_id
    }

    secret_environment_variables {
      key        = "FRED_API_KEY"
      project_id = var.project_id
      secret     = google_secret_manager_secret.fred_api_key.secret_id
      version    = "latest"
    }
  }

  depends_on = [
    google_project_service.apis["cloudfunctions.googleapis.com"],
    google_project_service.apis["run.googleapis.com"],
    google_secret_manager_secret_iam_member.ingest_fred_key,
  ]
}

# --- Transform analytics function ---

data "archive_file" "transform" {
  type        = "zip"
  source_dir  = "${path.module}/../functions/transform"
  output_path = "${path.module}/../functions/transform/deploy.zip"
  excludes    = ["deploy.zip", "__pycache__", "*.pyc", "test_*.py"]
}

resource "google_storage_bucket_object" "transform_source" {
  name   = "transform/${data.archive_file.transform.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.transform.output_path
}

resource "google_cloudfunctions2_function" "transform_analytics" {
  name     = "transform-analytics"
  location = var.region
  project  = var.project_id

  build_config {
    runtime     = "python312"
    entry_point = "transform"
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.transform_source.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "512Mi"
    timeout_seconds       = 300
    service_account_email = google_service_account.ingest.email

    environment_variables = {
      GCP_PROJECT = var.project_id
      BQ_DATASET  = google_bigquery_dataset.labor_market.dataset_id
    }
  }

  depends_on = [
    google_project_service.apis["cloudfunctions.googleapis.com"],
    google_project_service.apis["run.googleapis.com"],
  ]
}
