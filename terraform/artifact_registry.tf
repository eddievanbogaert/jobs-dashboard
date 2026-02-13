resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "jobs-dashboard"
  description   = "Docker images for the jobs-dashboard project"
  format        = "DOCKER"
  project       = var.project_id

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
