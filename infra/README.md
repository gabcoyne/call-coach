# Call Coach Infrastructure

Terraform configuration for deploying Call Coach to Google Cloud Platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GCP Project: prefect-sbx-sales-engineering       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │   Cloud Run      │    │   Cloud Run      │    │  Cloud Run     │ │
│  │   (Frontend)     │    │   (REST API)     │    │  Jobs (DLT)    │ │
│  │   Next.js SSR    │───▶│   FastAPI        │    │  Hourly Sync   │ │
│  │   Port 3000      │    │   Port 8000      │    │                │ │
│  └──────────────────┘    └──────────────────┘    └───────┬────────┘ │
│                                   │                       │          │
│                                   ▼                       │          │
│                          ┌──────────────────┐             │          │
│                          │  Secret Manager  │◀────────────┘          │
│                          │  (Credentials)   │                        │
│                          └──────────────────┘                        │
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │  Artifact        │    │  Workload        │    │  Cloud         │ │
│  │  Registry        │    │  Identity        │    │  Scheduler     │ │
│  │  (Docker)        │    │  (GitHub OIDC)   │    │  (Cron)        │ │
│  └──────────────────┘    └──────────────────┘    └────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Terraform** >= 1.5.0

   ```bash
   brew install terraform
   ```

2. **Google Cloud SDK**

   ```bash
   brew install --cask google-cloud-sdk
   ```

3. **GCP Authentication**

   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

4. **Project Access**
   - You need Owner or Editor role on `prefect-sbx-sales-engineering`

## Bootstrap (One-Time Setup)

Before Terraform can manage state remotely, create the GCS bucket:

```bash
# Set project
export PROJECT_ID=prefect-sbx-sales-engineering
gcloud config set project $PROJECT_ID

# Create Terraform state bucket
gsutil mb -l us-central1 gs://prefect-sbx-terraform-state
gsutil versioning set on gs://prefect-sbx-terraform-state
```

## Usage

### Initialize

```bash
cd infra
terraform init
```

### Plan Changes

```bash
terraform plan
```

### Apply Changes

```bash
terraform apply
```

### View Outputs

```bash
# All outputs
terraform output

# GitHub Actions variables (JSON)
terraform output -json github_actions_variables
```

## Adding Secret Values

Terraform creates Secret Manager secrets but **not** the secret values.
Add values via GCP Console after initial apply:

1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=prefect-sbx-sales-engineering)

2. Add versions for each secret:

| Secret                              | Source                                   |
| ----------------------------------- | ---------------------------------------- |
| `DATABASE_URL`                      | Neon Console → Connection string         |
| `ANTHROPIC_API_KEY`                 | Anthropic Console → API Keys             |
| `BIGQUERY_CREDENTIALS`              | GCP Console → Service Account → JSON Key |
| `CLERK_SECRET_KEY`                  | Clerk Dashboard → API Keys               |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk Dashboard → API Keys               |

## Module Structure

```
infra/
├── main.tf                 # Root module - wires everything together
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── versions.tf             # Provider versions
├── backend.tf              # GCS state backend
├── terraform.tfvars.example
│
└── modules/
    ├── api-services/       # Enable GCP APIs
    ├── artifact-registry/  # Docker image storage
    ├── secret-manager/     # Secret resources
    ├── workload-identity/  # GitHub OIDC authentication
    ├── cloud-run/          # Cloud Run services
    └── cloud-run-job/      # Cloud Run Jobs + Scheduler
```

## Configuring GitHub Actions

After `terraform apply`, configure GitHub repository:

1. Get the values:

   ```bash
   terraform output github_actions_variables
   ```

2. Go to: Repository → Settings → Secrets and variables → Actions → Variables

3. Add these **Repository Variables**:
   - `GCP_PROJECT_ID`
   - `GCP_REGION`
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`
   - `GCP_SERVICE_ACCOUNT`
   - `ARTIFACT_REGISTRY_URL`
   - `API_SERVICE_NAME`
   - `FRONTEND_SERVICE_NAME`
   - `DLT_JOB_NAME`

## Common Operations

### Deploy New Image Manually

```bash
# Configure Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push
docker build -f Dockerfile.api -t us-central1-docker.pkg.dev/prefect-sbx-sales-engineering/call-coach/api:v1 .
docker push us-central1-docker.pkg.dev/prefect-sbx-sales-engineering/call-coach/api:v1

# Deploy
gcloud run deploy call-coach-api \
  --image=us-central1-docker.pkg.dev/prefect-sbx-sales-engineering/call-coach/api:v1 \
  --region=us-central1
```

### Trigger DLT Sync Manually

```bash
gcloud run jobs execute call-coach-dlt-sync --region=us-central1
```

### View Logs

```bash
# API service
gcloud run services logs read call-coach-api --region=us-central1 --limit=50

# DLT job
gcloud run jobs executions list call-coach-dlt-sync --region=us-central1
gcloud run jobs logs read call-coach-dlt-sync --region=us-central1
```

## Troubleshooting

### "Error 403: Permission denied"

Ensure you have the required IAM roles:

```bash
gcloud projects get-iam-policy prefect-sbx-sales-engineering \
  --format='table(bindings.role,bindings.members)' \
  --filter="bindings.members:$(gcloud config get-value account)"
```

### "Backend configuration changed"

Re-initialize with:

```bash
terraform init -reconfigure
```

### Cloud Run service unhealthy

Check startup logs:

```bash
gcloud run services logs read call-coach-api --region=us-central1 --limit=100
```

Common causes:

- Missing secret values in Secret Manager
- Wrong port in Dockerfile
- Application crash on startup

### Workload Identity not working

Verify the GitHub repository matches:

```bash
terraform output workload_identity_provider
# Should include: attribute.repository/prefect/call-coach
```

## CI/CD Integration

After bootstrap, infrastructure changes go through GitHub Actions:

1. **Pull Request** → `terraform plan` runs and comments on PR
2. **Merge to main** → `terraform apply` runs automatically

See `.github/workflows/terraform.yml` for the workflow configuration.
