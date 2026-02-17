/**
 * Cloud Run Job Module
 *
 * Creates a Cloud Run Job with optional Cloud Scheduler trigger.
 * Used for batch jobs like the DLT data sync.
 */

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "location" {
  description = "GCP region for the job"
  type        = string
}

variable "name" {
  description = "Job name"
  type        = string
}

variable "image" {
  description = "Container image URL"
  type        = string
}

variable "memory" {
  description = "Memory limit (e.g., '2Gi')"
  type        = string
  default     = "2Gi"
}

variable "cpu" {
  description = "CPU limit (e.g., '2')"
  type        = string
  default     = "2"
}

variable "timeout_seconds" {
  description = "Task timeout in seconds"
  type        = number
  default     = 1800 # 30 minutes
}

variable "max_retries" {
  description = "Maximum retry attempts for failed tasks"
  type        = number
  default     = 3
}

variable "parallelism" {
  description = "Number of tasks to run in parallel"
  type        = number
  default     = 1
}

variable "task_count" {
  description = "Total number of tasks to run"
  type        = number
  default     = 1
}

variable "service_account_email" {
  description = "Service account email for the job"
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

variable "schedule" {
  description = "Cron schedule for the job (null to disable scheduling)"
  type        = string
  default     = null
}

variable "schedule_timezone" {
  description = "Timezone for the schedule"
  type        = string
  default     = "America/Los_Angeles"
}

variable "labels" {
  description = "Labels to apply to the job"
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

resource "google_cloud_run_v2_job" "job" {
  name     = var.name
  location = var.location

  labels = local.labels

  template {
    labels      = local.labels
    parallelism = var.parallelism
    task_count  = var.task_count

    template {
      service_account = var.service_account_email
      timeout         = "${var.timeout_seconds}s"
      max_retries     = var.max_retries

      containers {
        image = var.image

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
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
      }
    }
  }

  lifecycle {
    ignore_changes = [
      # Image is managed by CI/CD, not Terraform
      template[0].template[0].containers[0].image,
      # Client info added by Cloud Run
      client,
      client_version,
    ]
  }
}

# Cloud Scheduler to trigger the job on a schedule
resource "google_cloud_scheduler_job" "trigger" {
  count = var.schedule != null ? 1 : 0

  name        = "${var.name}-trigger"
  description = "Triggers ${var.name} Cloud Run Job on schedule"
  schedule    = var.schedule
  time_zone   = var.schedule_timezone
  region      = var.location

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job.name}:run"

    oauth_token {
      service_account_email = var.service_account_email
    }
  }
}

output "job_name" {
  description = "Cloud Run Job name"
  value       = google_cloud_run_v2_job.job.name
}

output "job_id" {
  description = "Cloud Run Job ID"
  value       = google_cloud_run_v2_job.job.id
}

output "scheduler_name" {
  description = "Cloud Scheduler job name (null if not scheduled)"
  value       = var.schedule != null ? google_cloud_scheduler_job.trigger[0].name : null
}

output "scheduler_id" {
  description = "Cloud Scheduler job ID (null if not scheduled)"
  value       = var.schedule != null ? google_cloud_scheduler_job.trigger[0].id : null
}
