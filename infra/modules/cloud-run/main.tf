/**
 * Cloud Run Service Module
 *
 * Creates a Cloud Run service with configurable scaling, secrets, and health checks.
 */

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "location" {
  description = "GCP region for the service"
  type        = string
}

variable "name" {
  description = "Service name"
  type        = string
}

variable "image" {
  description = "Container image URL"
  type        = string
}

variable "port" {
  description = "Container port"
  type        = number
  default     = 8080
}

variable "memory" {
  description = "Memory limit (e.g., '512Mi', '1Gi')"
  type        = string
  default     = "512Mi"
}

variable "cpu" {
  description = "CPU limit (e.g., '1', '2')"
  type        = string
  default     = "1"
}

variable "min_instances" {
  description = "Minimum number of instances (0 allows scale to zero)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "concurrency" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 80
}

variable "timeout" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "service_account_email" {
  description = "Service account email for the service"
  type        = string
}

variable "env_vars" {
  description = "Environment variables (non-secret)"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Map of environment variable names to Secret Manager secret IDs"
  type        = map(string)
  default     = {}
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access to the service"
  type        = bool
  default     = true
}

variable "health_check_path" {
  description = "Path for health check endpoint"
  type        = string
  default     = "/health"
}

variable "labels" {
  description = "Labels to apply to the service"
  type        = map(string)
  default     = {}
}

locals {
  default_labels = {
    app     = "call-coach"
    managed = "terraform"
  }
  labels = merge(local.default_labels, var.labels)
}

resource "google_cloud_run_v2_service" "service" {
  name     = var.name
  location = var.location
  ingress  = "INGRESS_TRAFFIC_ALL"

  labels = local.labels

  template {
    labels          = local.labels
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.image

      ports {
        container_port = var.port
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        cpu_idle          = var.min_instances == 0
        startup_cpu_boost = true
      }

      # Non-secret environment variables
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secret environment variables
      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }

      startup_probe {
        http_get {
          path = var.health_check_path
          port = var.port
        }
        initial_delay_seconds = 5
        period_seconds        = 5
        failure_threshold     = 10
        timeout_seconds       = 5
      }

      liveness_probe {
        http_get {
          path = var.health_check_path
          port = var.port
        }
        period_seconds    = 30
        failure_threshold = 3
        timeout_seconds   = 5
      }
    }

    max_instance_request_concurrency = var.concurrency
    timeout                          = "${var.timeout}s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      # Image is managed by CI/CD, not Terraform
      template[0].containers[0].image,
      # Client info added by Cloud Run
      client,
      client_version,
    ]
  }
}

# IAM binding for public access
resource "google_cloud_run_v2_service_iam_member" "public" {
  count = var.allow_unauthenticated ? 1 : 0

  location = google_cloud_run_v2_service.service.location
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.service.name
}

output "service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.service.uri
}

output "service_id" {
  description = "Cloud Run service ID"
  value       = google_cloud_run_v2_service.service.id
}
