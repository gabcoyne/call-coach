/**
 * Secret Manager Module
 *
 * Creates Secret Manager secrets for the application.
 * Note: This only creates the secret resources, not the secret values.
 * Secret values must be added manually via GCP Console.
 */

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "secrets" {
  description = "Map of secret names to their descriptions"
  type        = map(string)
  default = {
    "DATABASE_URL"                      = "Neon Postgres connection string"
    "ANTHROPIC_API_KEY"                 = "Anthropic Claude API key"
    "BIGQUERY_CREDENTIALS"              = "BigQuery service account JSON credentials"
    "CLERK_SECRET_KEY"                  = "Clerk authentication secret key"
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" = "Clerk authentication publishable key"
  }
}

variable "labels" {
  description = "Labels to apply to all secrets"
  type        = map(string)
  default = {
    app     = "call-coach"
    managed = "terraform"
  }
}

resource "google_secret_manager_secret" "secrets" {
  for_each = var.secrets

  secret_id = each.key

  labels = var.labels

  replication {
    auto {}
  }
}

output "secret_ids" {
  description = "Map of secret names to their IDs"
  value       = { for k, v in google_secret_manager_secret.secrets : k => v.secret_id }
}

output "secret_names" {
  description = "Map of secret names to their full resource names"
  value       = { for k, v in google_secret_manager_secret.secrets : k => v.name }
}
