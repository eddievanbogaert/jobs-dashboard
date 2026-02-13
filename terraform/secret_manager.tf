resource "google_secret_manager_secret" "fred_api_key" {
  secret_id = "fred-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis["secretmanager.googleapis.com"]]
}
