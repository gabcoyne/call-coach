#!/bin/bash

# GitHub Secrets Setup Script
# This script helps set up required GitHub secrets for CI/CD
# Usage: ./setup-secrets.sh [github-token] [repo-owner] [repo-name]

set -e

GITHUB_TOKEN="${1:-$GITHUB_TOKEN}"
REPO_OWNER="${2:-gabcoyne}"
REPO_NAME="${3:-call-coach}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GitHub token not provided"
    echo "Usage: ./setup-secrets.sh <github-token> [repo-owner] [repo-name]"
    echo ""
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_value=$2

    if [ -z "$secret_value" ]; then
        echo "⚠️  Skipping $secret_name (empty value)"
        return
    fi

    # Check if gh CLI is available
    if command -v gh &> /dev/null; then
        echo "Setting secret: $secret_name"
        echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO_OWNER/$REPO_NAME"
        echo "✅ $secret_name set"
    else
        echo "⚠️  gh CLI not available, showing manual instructions for $secret_name"
        echo "   Value: $secret_value"
    fi
}

# Function to list required secrets
list_required_secrets() {
    cat <<EOF

Required GitHub Secrets:

DATABASE & DEPLOYMENT (Staging):
  STAGING_DATABASE_URL          PostgreSQL connection string for staging
  STAGING_API_URL               API base URL for frontend configuration
  STAGING_API_ENDPOINT          Backend health check endpoint
  STAGING_WEB_URL               Frontend URL for smoke tests
  STAGING_TEST_USER_EMAIL       Test user email
  STAGING_TEST_USER_PASSWORD    Test user password
  STAGING_DEPLOYMENT_TOKEN      Token for deploying to staging

DATABASE & DEPLOYMENT (Production):
  PRODUCTION_DATABASE_URL       PostgreSQL connection string for production
  PRODUCTION_API_URL            API base URL for production
  PRODUCTION_API_ENDPOINT       Backend health check endpoint
  PRODUCTION_DEPLOYMENT_TOKEN   Token for deploying to production

VERCEL (Frontend Deployment):
  VERCEL_TOKEN                  Vercel authentication token
  VERCEL_ORG_ID                 Vercel organization ID
  VERCEL_PROJECT_ID             Vercel project ID for production
  VERCEL_PROJECT_ID_STAGING     Vercel project ID for staging

TESTING:
  TEST_USER_EMAIL               Test user email for E2E tests
  TEST_USER_PASSWORD            Test user password for E2E tests
  TEST_CALL_ID                  Sample call ID for testing
  TEST_REP_EMAIL                Sample representative email

EOF
}

# Function to create interactive secret setup
interactive_setup() {
    echo "=========================================="
    echo "Interactive GitHub Secrets Setup"
    echo "=========================================="
    echo ""
    echo "Repository: $REPO_OWNER/$REPO_NAME"
    echo ""

    # Staging secrets
    echo "--- STAGING ENVIRONMENT ---"
    echo ""

    read -p "Enter STAGING_DATABASE_URL: " STAGING_DATABASE_URL
    set_secret "STAGING_DATABASE_URL" "$STAGING_DATABASE_URL"

    read -p "Enter STAGING_API_URL: " STAGING_API_URL
    set_secret "STAGING_API_URL" "$STAGING_API_URL"

    read -p "Enter STAGING_API_ENDPOINT: " STAGING_API_ENDPOINT
    set_secret "STAGING_API_ENDPOINT" "$STAGING_API_ENDPOINT"

    read -p "Enter STAGING_WEB_URL: " STAGING_WEB_URL
    set_secret "STAGING_WEB_URL" "$STAGING_WEB_URL"

    read -p "Enter STAGING_TEST_USER_EMAIL: " STAGING_TEST_USER_EMAIL
    set_secret "STAGING_TEST_USER_EMAIL" "$STAGING_TEST_USER_EMAIL"

    read -sp "Enter STAGING_TEST_USER_PASSWORD: " STAGING_TEST_USER_PASSWORD
    echo ""
    set_secret "STAGING_TEST_USER_PASSWORD" "$STAGING_TEST_USER_PASSWORD"

    read -sp "Enter STAGING_DEPLOYMENT_TOKEN: " STAGING_DEPLOYMENT_TOKEN
    echo ""
    set_secret "STAGING_DEPLOYMENT_TOKEN" "$STAGING_DEPLOYMENT_TOKEN"

    # Production secrets
    echo ""
    echo "--- PRODUCTION ENVIRONMENT ---"
    echo ""

    read -p "Enter PRODUCTION_DATABASE_URL: " PRODUCTION_DATABASE_URL
    set_secret "PRODUCTION_DATABASE_URL" "$PRODUCTION_DATABASE_URL"

    read -p "Enter PRODUCTION_API_URL: " PRODUCTION_API_URL
    set_secret "PRODUCTION_API_URL" "$PRODUCTION_API_URL"

    read -p "Enter PRODUCTION_API_ENDPOINT: " PRODUCTION_API_ENDPOINT
    set_secret "PRODUCTION_API_ENDPOINT" "$PRODUCTION_API_ENDPOINT"

    read -sp "Enter PRODUCTION_DEPLOYMENT_TOKEN: " PRODUCTION_DEPLOYMENT_TOKEN
    echo ""
    set_secret "PRODUCTION_DEPLOYMENT_TOKEN" "$PRODUCTION_DEPLOYMENT_TOKEN"

    # Vercel secrets
    echo ""
    echo "--- VERCEL CONFIGURATION ---"
    echo ""

    read -sp "Enter VERCEL_TOKEN: " VERCEL_TOKEN
    echo ""
    set_secret "VERCEL_TOKEN" "$VERCEL_TOKEN"

    read -p "Enter VERCEL_ORG_ID: " VERCEL_ORG_ID
    set_secret "VERCEL_ORG_ID" "$VERCEL_ORG_ID"

    read -p "Enter VERCEL_PROJECT_ID (Production): " VERCEL_PROJECT_ID
    set_secret "VERCEL_PROJECT_ID" "$VERCEL_PROJECT_ID"

    read -p "Enter VERCEL_PROJECT_ID_STAGING: " VERCEL_PROJECT_ID_STAGING
    set_secret "VERCEL_PROJECT_ID_STAGING" "$VERCEL_PROJECT_ID_STAGING"

    # Testing secrets
    echo ""
    echo "--- TESTING CONFIGURATION ---"
    echo ""

    read -p "Enter TEST_USER_EMAIL: " TEST_USER_EMAIL
    set_secret "TEST_USER_EMAIL" "$TEST_USER_EMAIL"

    read -sp "Enter TEST_USER_PASSWORD: " TEST_USER_PASSWORD
    echo ""
    set_secret "TEST_USER_PASSWORD" "$TEST_USER_PASSWORD"

    read -p "Enter TEST_CALL_ID: " TEST_CALL_ID
    set_secret "TEST_CALL_ID" "$TEST_CALL_ID"

    read -p "Enter TEST_REP_EMAIL: " TEST_REP_EMAIL
    set_secret "TEST_REP_EMAIL" "$TEST_REP_EMAIL"

    echo ""
    echo "=========================================="
    echo "✅ All secrets configured!"
    echo "=========================================="
}

# Function to verify secrets are set
verify_secrets() {
    echo "Verifying secrets in repository..."
    echo ""

    if command -v gh &> /dev/null; then
        gh secret list --repo "$REPO_OWNER/$REPO_NAME" | grep -E "STAGING|PRODUCTION|VERCEL|TEST" || true
    else
        echo "⚠️  gh CLI not available for verification"
        echo "   Please verify secrets manually in GitHub Settings > Secrets"
    fi
}

# Main execution
echo "=========================================="
echo "GitHub Secrets Setup Tool"
echo "=========================================="
echo ""

# Show options
echo "What would you like to do?"
echo ""
echo "1. Show required secrets (list only)"
echo "2. Interactive setup (requires gh CLI)"
echo "3. Verify existing secrets"
echo "4. Exit"
echo ""

read -p "Select option (1-4): " option

case $option in
    1)
        list_required_secrets
        ;;
    2)
        # Check if gh CLI is available
        if ! command -v gh &> /dev/null; then
            echo "❌ Error: gh CLI is required for interactive setup"
            echo ""
            echo "Install gh CLI from: https://cli.github.com"
            exit 1
        fi
        interactive_setup
        ;;
    3)
        verify_secrets
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "For manual setup instructions, see: scripts/ci/README.md"
