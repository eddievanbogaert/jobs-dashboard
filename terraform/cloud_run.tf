resource "google_cloud_run_v2_service" "dashboard" {
  name     = "jobs-dashboard"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.dashboard.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/dashboard:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          memory = "1Gi"
          cpu    = "1"
        }
      }
    }
  }

  depends_on = [
    google_project_service.apis["run.googleapis.com"],
    google_artifact_registry_repository.docker,
  ]
}
