/**
 * Outputs
 *
 * These values are used to configure GitHub Actions and for reference.
 * Run `terraform output` to see all values.
 * Run `terraform output -json github_actions_variables` to get GitHub Actions config.
 */

# =============================================================================
# Artifact Registry
# =============================================================================

output "artifact_registry_url" {
  description = "Artifact Registry URL for Docker images"
  value       = module.artifact_registry.repository_url
}

# =============================================================================
# Cloud Run Services
# =============================================================================

output "api_service_url" {
  description = "Cloud Run API service URL"
  value       = module.api_service.service_url
}

output "api_service_name" {
  description = "Cloud Run API service name"
  value       = module.api_service.service_name
}

output "frontend_service_url" {
  description = "Cloud Run Frontend service URL"
  value       = module.frontend_service.service_url
}

output "frontend_service_name" {
  description = "Cloud Run Frontend service name"
  value       = module.frontend_service.service_name
}

# =============================================================================
# Cloud Run Job
# =============================================================================

output "dlt_sync_job_name" {
  description = "Cloud Run DLT sync job name"
  value       = module.dlt_sync_job.job_name
}

output "dlt_sync_scheduler_name" {
  description = "Cloud Scheduler job name for DLT sync"
  value       = module.dlt_sync_job.scheduler_name
}

# =============================================================================
# Workload Identity (GitHub Actions)
# =============================================================================

output "workload_identity_provider" {
  description = "Workload Identity Provider for GitHub Actions"
  value       = module.workload_identity.workload_identity_provider
}

output "github_actions_service_account" {
  description = "Service account email for GitHub Actions"
  value       = module.workload_identity.service_account_email
}

# =============================================================================
# Service Accounts
# =============================================================================

output "runtime_service_account" {
  description = "Runtime service account email for Cloud Run"
  value       = google_service_account.runtime.email
}

# =============================================================================
# GitHub Actions Configuration
# =============================================================================

output "github_actions_variables" {
  description = "Variables to add to GitHub repository settings"
  value = {
    GCP_PROJECT_ID                 = var.project_id
    GCP_REGION                     = var.region
    GCP_WORKLOAD_IDENTITY_PROVIDER = module.workload_identity.workload_identity_provider
    GCP_SERVICE_ACCOUNT            = module.workload_identity.service_account_email
    ARTIFACT_REGISTRY_URL          = module.artifact_registry.repository_url
    API_SERVICE_NAME               = module.api_service.service_name
    FRONTEND_SERVICE_NAME          = module.frontend_service.service_name
    DLT_JOB_NAME                   = module.dlt_sync_job.job_name
  }
}

# =============================================================================
# Secret Manager
# =============================================================================

output "secret_ids" {
  description = "Secret Manager secret IDs (add values via GCP Console)"
  value       = module.secrets.secret_ids
}
