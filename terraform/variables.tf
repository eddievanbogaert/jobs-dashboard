variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "jobs-dashboard"
}

variable "region" {
  description = "GCP region for deployed resources"
  type        = string
  default     = "us-central1"
}

variable "bq_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "eddievanbogaert"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "jobs-dashboard"
}
