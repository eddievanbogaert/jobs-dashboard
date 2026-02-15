# Cloud Build triggers require GitHub repo connection via GCP Console.
# After connecting: Cloud Build > Triggers > Connect Repository, uncomment below.

# resource "google_cloudbuild_trigger" "dashboard_deploy" {
#   name     = "dashboard-deploy"
#   project  = var.project_id
#   location = var.region
#
#   github {
#     owner = var.github_owner
#     name  = var.github_repo
#     push {
#       branch = "^main$"
#     }
#   }
#
#   included_files = ["dashboard/**", "cloudbuild.yaml"]
#   filename       = "cloudbuild.yaml"
#
#   depends_on = [google_project_service.apis["cloudbuild.googleapis.com"]]
# }

# resource "google_cloudbuild_trigger" "functions_deploy" {
#   name     = "functions-deploy"
#   project  = var.project_id
#   location = var.region
#
#   github {
#     owner = var.github_owner
#     name  = var.github_repo
#     push {
#       branch = "^main$"
#     }
#   }
#
#   included_files = ["functions/**", "cloudbuild-functions.yaml"]
#   filename       = "cloudbuild-functions.yaml"
#
#   depends_on = [google_project_service.apis["cloudbuild.googleapis.com"]]
# }
