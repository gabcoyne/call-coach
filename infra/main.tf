/**
 * Call Coach Infrastructure
 *
 * This Terraform configuration manages all GCP infrastructure for the Call Coach application.
 * It deploys:
 * - Artifact Registry for Docker images
 * - Secret Manager for credentials
 * - Workload Identity for GitHub Actions authentication
 * - Cloud Run services for API and Frontend
 * - Cloud Run Job for DLT data sync
 * - Cloud Scheduler for hourly sync triggers
 */

# =============================================================================
# Provider Configuration
# =============================================================================

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# =============================================================================
# Data Sources
# =============================================================================

data "google_project" "project" {
  project_id = var.project_id
}

# =============================================================================
# API Services (must be enabled first)
# =============================================================================

module "api_services" {
  source     = "./modules/api-services"
  project_id = var.project_id
}

# =============================================================================
# Artifact Registry
# =============================================================================

module "artifact_registry" {
  source        = "./modules/artifact-registry"
  project_id    = var.project_id
  location      = var.region
  repository_id = "call-coach"

  depends_on = [module.api_services]
}

# =============================================================================
# Secret Manager
# =============================================================================

module "secrets" {
  source     = "./modules/secret-manager"
  project_id = var.project_id

  depends_on = [module.api_services]
}

# =============================================================================
# Workload Identity (GitHub Actions Authentication)
# =============================================================================

module "workload_identity" {
  source            = "./modules/workload-identity"
  project_id        = var.project_id
  project_number    = data.google_project.project.number
  github_owner      = var.github_owner
  github_repository = var.github_repository

  depends_on = [module.api_services]
}

# =============================================================================
# Runtime Service Account (for Cloud Run services)
# =============================================================================

resource "google_service_account" "runtime" {
  account_id   = "call-coach-runtime"
  display_name = "Call Coach Runtime"
  description  = "Service account for Cloud Run services and jobs"
}

# Allow runtime service account to access secrets
resource "google_project_iam_member" "runtime_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# Allow runtime service account to read BigQuery data (for DLT sync)
resource "google_project_iam_member" "runtime_bigquery_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# Allow runtime service account to run BigQuery jobs (for DLT sync)
resource "google_project_iam_member" "runtime_bigquery_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# Allow runtime service account to invoke Cloud Run (for scheduler)
resource "google_project_iam_member" "runtime_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

# =============================================================================
# Cloud Run: REST API Service
# =============================================================================

module "api_service" {
  source     = "./modules/cloud-run"
  project_id = var.project_id
  location   = var.region
  name       = "call-coach-api"

  # Use a placeholder image initially; CI/CD will deploy the real image
  image = "${module.artifact_registry.repository_url}/api:latest"
  port  = 8000

  memory        = var.api_memory
  cpu           = var.api_cpu
  min_instances = var.api_min_instances
  max_instances = var.api_max_instances

  service_account_email = google_service_account.runtime.email

  secret_env_vars = {
    DATABASE_URL      = module.secrets.secret_ids["DATABASE_URL"]
    ANTHROPIC_API_KEY = module.secrets.secret_ids["ANTHROPIC_API_KEY"]
  }

  health_check_path = "/health"

  # Org policy prevents allUsers - using IAM-based auth instead
  allow_unauthenticated = false

  labels = {
    component = "api"
  }

  depends_on = [
    module.secrets,
    module.artifact_registry,
    google_project_iam_member.runtime_secret_accessor,
  ]
}

# =============================================================================
# Cloud Run: Frontend Service
# =============================================================================

module "frontend_service" {
  source     = "./modules/cloud-run"
  project_id = var.project_id
  location   = var.region
  name       = "call-coach-frontend"

  # Use a placeholder image initially; CI/CD will deploy the real image
  image = "${module.artifact_registry.repository_url}/frontend:latest"
  port  = 3000

  memory        = var.frontend_memory
  cpu           = var.frontend_cpu
  min_instances = var.frontend_min_instances
  max_instances = var.frontend_max_instances

  service_account_email = google_service_account.runtime.email

  env_vars = {
    # API URL will be set after API service is created
    NEXT_PUBLIC_API_URL = module.api_service.service_url
  }

  secret_env_vars = {
    CLERK_SECRET_KEY = module.secrets.secret_ids["CLERK_SECRET_KEY"]
  }

  # Next.js health check endpoint
  health_check_path = "/api/health"

  # Org policy prevents allUsers - using IAM-based auth instead
  allow_unauthenticated = false

  labels = {
    component = "frontend"
  }

  depends_on = [
    module.secrets,
    module.artifact_registry,
    module.api_service,
    google_project_iam_member.runtime_secret_accessor,
  ]
}

# =============================================================================
# Cloud Run Job: DLT Data Sync
# =============================================================================

module "dlt_sync_job" {
  source     = "./modules/cloud-run-job"
  project_id = var.project_id
  location   = var.region
  name       = "call-coach-dlt-sync"

  # Use a placeholder image initially; CI/CD will deploy the real image
  image = "${module.artifact_registry.repository_url}/dlt:latest"

  memory          = var.dlt_memory
  cpu             = var.dlt_cpu
  timeout_seconds = var.dlt_timeout
  max_retries     = 3

  service_account_email = google_service_account.runtime.email

  # DATABASE_URL from secret, BigQuery uses attached service account credentials
  secret_env_vars = {
    DATABASE_URL = module.secrets.secret_ids["DATABASE_URL"]
  }

  # Use GCP project for BigQuery access (SA already has bigquery.dataViewer role)
  env_vars = {
    GCP_PROJECT = var.project_id
  }

  # Schedule: run every hour
  schedule          = var.dlt_schedule
  schedule_timezone = var.dlt_schedule_timezone

  labels = {
    component = "dlt-sync"
  }

  depends_on = [
    module.secrets,
    module.artifact_registry,
    google_project_iam_member.runtime_secret_accessor,
    google_project_iam_member.runtime_bigquery_viewer,
    google_project_iam_member.runtime_bigquery_user,
    google_project_iam_member.runtime_run_invoker,
  ]
}
