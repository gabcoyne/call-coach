variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "prefect-sbx-sales-engineering"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "github_owner" {
  description = "GitHub organization or user"
  type        = string
  default     = "prefect"
}

variable "github_repository" {
  description = "GitHub repository name"
  type        = string
  default     = "call-coach"
}

# Cloud Run API configuration
variable "api_min_instances" {
  description = "Minimum instances for API service (1 to avoid cold starts)"
  type        = number
  default     = 1
}

variable "api_max_instances" {
  description = "Maximum instances for API service"
  type        = number
  default     = 10
}

variable "api_memory" {
  description = "Memory allocation for API service"
  type        = string
  default     = "1Gi"
}

variable "api_cpu" {
  description = "CPU allocation for API service"
  type        = string
  default     = "1"
}

# Cloud Run Frontend configuration
variable "frontend_min_instances" {
  description = "Minimum instances for frontend service (0 allows scale to zero)"
  type        = number
  default     = 0
}

variable "frontend_max_instances" {
  description = "Maximum instances for frontend service"
  type        = number
  default     = 10
}

variable "frontend_memory" {
  description = "Memory allocation for frontend service"
  type        = string
  default     = "512Mi"
}

variable "frontend_cpu" {
  description = "CPU allocation for frontend service"
  type        = string
  default     = "1"
}

# Cloud Run Job (DLT Sync) configuration
variable "dlt_memory" {
  description = "Memory allocation for DLT sync job"
  type        = string
  default     = "2Gi"
}

variable "dlt_cpu" {
  description = "CPU allocation for DLT sync job"
  type        = string
  default     = "2"
}

variable "dlt_timeout" {
  description = "Timeout for DLT sync job in seconds"
  type        = number
  default     = 1800 # 30 minutes
}

variable "dlt_schedule" {
  description = "Cron schedule for DLT sync (hourly by default)"
  type        = string
  default     = "0 * * * *"
}

variable "dlt_schedule_timezone" {
  description = "Timezone for DLT sync schedule"
  type        = string
  default     = "America/Los_Angeles"
}

# Monitoring configuration
variable "alert_email" {
  description = "Email address for monitoring alerts (leave empty to disable email notifications)"
  type        = string
  default     = ""
}
