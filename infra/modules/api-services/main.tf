/**
 * API Services Module
 *
 * Enables required GCP APIs for the Call Coach application.
 * Must be applied before other resources can be created.
 */

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

locals {
  services = [
    "run.googleapis.com",                  # Cloud Run
    "artifactregistry.googleapis.com",     # Artifact Registry
    "secretmanager.googleapis.com",        # Secret Manager
    "cloudscheduler.googleapis.com",       # Cloud Scheduler
    "iam.googleapis.com",                  # IAM
    "iamcredentials.googleapis.com",       # IAM Credentials (Workload Identity)
    "cloudresourcemanager.googleapis.com", # Resource Manager
    "compute.googleapis.com",              # Compute Engine (Load Balancer)
    "iap.googleapis.com",                  # Identity-Aware Proxy
  ]
}

resource "google_project_service" "services" {
  for_each = toset(local.services)

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false

  timeouts {
    create = "30m"
    update = "40m"
  }
}

output "enabled_services" {
  description = "List of enabled GCP APIs"
  value       = [for s in google_project_service.services : s.service]
}
