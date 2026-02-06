#!/bin/bash

# GitHub Branch Protection Setup Script
# This script sets up required status checks and branch protection rules
# Usage: ./setup-branch-protection.sh [token] [repo-owner] [repo-name]

set -e

GITHUB_TOKEN="${1:-$GITHUB_TOKEN}"
REPO_OWNER="${2:-gabcoyne}"
REPO_NAME="${3:-call-coach}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GitHub token not provided"
    echo "Usage: ./setup-branch-protection.sh <github-token> [repo-owner] [repo-name]"
    echo ""
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

echo "Setting up branch protection for $REPO_OWNER/$REPO_NAME"
echo ""

# Function to create or update branch protection
setup_branch_protection() {
    local branch=$1
    local description=$2

    echo "Configuring branch protection for: $branch"
    echo "Description: $description"
    echo ""

    # Build the JSON payload
    local payload=$(cat <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "lint",
      "type-check",
      "python-tests",
      "build-mcp",
      "build-webhook",
      "security"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": false,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_auto_merge": false,
  "allow_deletions": false,
  "allow_force_pushes": false,
  "required_linear_history": false,
  "required_conversation_resolution": false
}
EOF
)

    # Call GitHub API
    curl -X PUT \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $GITHUB_TOKEN" \
        -d "$payload" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/branches/$branch/protection"

    if [ $? -eq 0 ]; then
        echo "✅ Successfully configured branch protection for $branch"
    else
        echo "❌ Failed to configure branch protection for $branch"
        return 1
    fi
    echo ""
}

# Function to add code owners
setup_code_owners() {
    echo "Setting up CODEOWNERS file..."

    if [ ! -f ".github/CODEOWNERS" ]; then
        mkdir -p .github
        cat > .github/CODEOWNERS <<EOF
# CODEOWNERS file for call-coach project
# This file specifies who should review changes to various parts of the codebase

# All Python code
/analysis/**/*.py @gabcoyne
/coaching_mcp/**/*.py @gabcoyne
/api/**/*.py @gabcoyne

# Database code
/db/**/*.py @gabcoyne

# Frontend code
/frontend/** @gabcoyne

# CI/CD configuration
.github/ @gabcoyne
scripts/ci/ @gabcoyne

# Project configuration
pyproject.toml @gabcoyne
docker-compose.yml @gabcoyne
Dockerfile* @gabcoyne

EOF
        echo "✅ Created .github/CODEOWNERS file"
    else
        echo "⚠️ CODEOWNERS file already exists, skipping..."
    fi
    echo ""
}

# Function to verify status checks
verify_status_checks() {
    echo "Verifying available status checks..."
    echo ""

    # Try to get branch protection status
    RESPONSE=$(curl -s \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/branches/main/protection")

    echo "Response:"
    echo "$RESPONSE" | jq '.required_status_checks.contexts[]' 2>/dev/null || echo "Status checks not yet configured"
    echo ""
}

# Main execution
echo "=========================================="
echo "GitHub Branch Protection Setup"
echo "=========================================="
echo ""

# Setup code owners
setup_code_owners

# Setup branch protection for main and develop
setup_branch_protection "main" "Production branch - requires all checks and PR review"
setup_branch_protection "develop" "Development branch - requires checks and PR review"

# Verify setup
echo "=========================================="
echo "Verifying Setup"
echo "=========================================="
echo ""

verify_status_checks

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "✅ Branch protection configured for main"
echo "✅ Branch protection configured for develop"
echo "✅ CODEOWNERS file created"
echo ""
echo "Next steps:"
echo "1. Verify branch protection rules in GitHub Settings > Branches"
echo "2. Ensure all required secrets are configured"
echo "3. Test a PR to ensure status checks are running"
echo ""
