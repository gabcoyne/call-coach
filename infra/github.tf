/**
 * GitHub Configuration
 *
 * Manages GitHub repository settings including branch protection rules.
 * Requires a GITHUB_TOKEN environment variable with repo admin permissions.
 *
 * To enable GitHub resources, set:
 *   export GITHUB_TOKEN=ghp_your_token_here
 *
 * The github_enabled variable controls whether GitHub resources are created.
 */

# =============================================================================
# Variables
# =============================================================================

variable "github_enabled" {
  description = "Whether to manage GitHub resources (requires GITHUB_TOKEN)"
  type        = bool
  default     = false # Disabled by default; enable when GITHUB_TOKEN is set
}

# =============================================================================
# Provider Configuration
# =============================================================================

provider "github" {
  owner = var.github_owner
  # Token provided via GITHUB_TOKEN environment variable
}

# =============================================================================
# Repository Data Source
# =============================================================================

data "github_repository" "repo" {
  count     = var.github_enabled ? 1 : 0
  full_name = "${var.github_owner}/${var.github_repository}"
}

# =============================================================================
# Branch Protection for main branch (using v3 API)
# =============================================================================

resource "github_branch_protection_v3" "main" {
  count      = var.github_enabled ? 1 : 0
  repository = var.github_repository
  branch     = "main"

  # Require pull request reviews
  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = false
    required_approving_review_count = 1
    require_last_push_approval      = true
  }

  # Require status checks to pass
  required_status_checks {
    strict = true # Require branches to be up to date
    contexts = [
      "lint",
      "type-check",
      "unit-tests",
      "build-check",
    ]
  }

  # Enforce for administrators
  enforce_admins = true

  # Require linear history (squash/rebase only)
  require_signed_commits = false

  # Restrictions (no teams/users restrictions)
  restrictions {}
}

# =============================================================================
# Repository Settings
# =============================================================================

resource "github_repository" "settings" {
  count = var.github_enabled ? 1 : 0
  name  = var.github_repository

  # Merge settings - squash only for clean history
  allow_merge_commit = false
  allow_squash_merge = true
  allow_rebase_merge = false

  # Squash merge commit settings
  squash_merge_commit_title   = "PR_TITLE"
  squash_merge_commit_message = "PR_BODY"

  # Auto-delete head branches after merge
  delete_branch_on_merge = true

  # Other settings (keep existing)
  has_issues = data.github_repository.repo[0].has_issues
  has_wiki   = data.github_repository.repo[0].has_wiki

  # Vulnerability alerts
  vulnerability_alerts = true

  lifecycle {
    # Prevent changing repository name or visibility
    ignore_changes = [
      name,
      visibility,
      description,
      homepage_url,
      topics,
      archived,
      archive_on_destroy,
    ]
  }
}

# =============================================================================
# Outputs
# =============================================================================

output "repository_url" {
  description = "GitHub repository URL"
  value       = var.github_enabled ? data.github_repository.repo[0].html_url : "GitHub resources disabled"
}

output "branch_protection_enabled" {
  description = "Whether branch protection is enabled on main"
  value       = var.github_enabled
}
