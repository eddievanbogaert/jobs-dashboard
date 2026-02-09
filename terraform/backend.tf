terraform {
  backend "gcs" {
    bucket = "jobs-dashboard-tf-state"
    prefix = "terraform/state"
  }
}
