/**
 * Artifact Registry Module
 *
 * Creates a Docker repository for storing container images.
 */

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "location" {
  description = "Location for the repository"
  type        = string
  default     = "us-central1"
}

variable "repository_id" {
  description = "Repository ID"
  type        = string
  default     = "call-coach"
}

resource "google_artifact_registry_repository" "repo" {
  location      = var.location
  repository_id = var.repository_id
  description   = "Call Coach Docker images"
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = 10
    }
  }

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "604800s" # 7 days
    }
  }
}

output "repository_id" {
  description = "Artifact Registry repository ID"
  value       = google_artifact_registry_repository.repo.repository_id
}

output "repository_url" {
  description = "Artifact Registry repository URL for Docker images"
  value       = "${var.location}-docker.pkg.dev/${var.project_id}/${var.repository_id}"
}

output "repository_name" {
  description = "Full repository name"
  value       = google_artifact_registry_repository.repo.name
}
