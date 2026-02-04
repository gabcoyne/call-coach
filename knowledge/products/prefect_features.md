# Prefect Product Knowledge

## Overview
Prefect is a modern workflow orchestration platform for building, running, and monitoring data pipelines. It's designed to make workflow engineering simple, scalable, and reliable.

## Core Philosophy
- **Python-native**: Workflows are just Python functions, no proprietary DSLs
- **Hybrid execution**: Run workflows anywhere (cloud, on-prem, laptop)
- **Dynamic workflows**: Generate tasks at runtime based on data
- **Obsenvability-first**: Built-in monitoring without extra configuration

## Key Features

### 1. Python-Native Workflows
**What it is**: Write workflows using standard Python functions with decorators.

**Why it matters**:
- No learning curve for Python developers
- Test with pytest locally before deploying
- Use any Python library or package
- Familiar debugging with standard tools

**Example**:
```python
from prefect import flow, task

@task
def extract_data(source: str):
    return load_from_source(source)

@flow
def etl_pipeline(sources: list[str]):
    results = extract_data.map(sources)  # Parallel execution
    return transform_and_load(results)
```

**Differentiation**: Unlike Airflow's DAG syntax or complex YAML configs, it's just Python.

### 2. Dynamic Workflows
**What it is**: Tasks and flows can be generated at runtime based on data.

**Why it matters**:
- Handle variable workloads without manual configuration
- Process data of unknown shape/size
- Conditional logic based on runtime state
- True dynamic parallelism

**Use case**: Process varying number of files from S3 bucket without knowing count upfront.

**Differentiation**: Airflow DAGs are static and must be predefined. Temporal requires more boilerplate for dynamic workflows.

### 3. Hybrid Execution Model
**What it is**: Code runs where you want - cloud workers, Kubernetes, on-prem servers, even locally.

**Why it matters**:
- Data never leaves your environment if required
- Gradual cloud migration path
- Cost optimization (run expensive tasks on-prem)
- Disaster recovery across regions

**Architecture**:
- Prefect Cloud: Orchestration engine (metadata, scheduling, UI)
- Execution: Your infrastructure (work pools)
- Decoupled: Orchestration ≠ Execution

**Differentiation**: Most platforms couple orchestration with execution. Prefect decouples them.

### 4. Built-in Observability
**What it is**: Comprehensive monitoring, logging, and alerting without extra setup.

**Features**:
- Real-time flow run tracking
- Task-level logs with automatic capture
- Execution graphs and visualizations
- Alerting on failures, retries, late runs
- Historical run data and analytics

**Why it matters**:
- No need to configure external logging (Datadog, Splunk)
- Troubleshoot failures faster with detailed logs
- Proactive alerting prevents silent failures
- Audit trail for compliance

### 5. Subflows and Modularity
**What it is**: Flows can call other flows as subflows, creating hierarchical pipelines.

**Why it matters**:
- Reusable pipeline components
- Logical separation of concerns
- Independent testing of subflows
- Cleaner failure isolation

**Use case**: Main ETL flow orchestrates separate extract, transform, load subflows.

### 6. Task Caching
**What it is**: Cache task results to avoid redundant computation.

**Why it matters**:
- Skip expensive API calls or computations
- Faster development iteration
- Cost savings on cloud resources
- Deterministic reruns for debugging

**Configuration**: Control cache expiration, invalidation, and scope.

### 7. Work Pools and Queues
**What it is**: Organize execution infrastructure with work pools and prioritize with queues.

**Why it matters**:
- Route different workloads to appropriate infrastructure
- Priority-based execution
- Resource isolation (production vs. dev)
- Scalability through multiple pools

**Example**: GPU work pool for ML tasks, standard pool for data processing.

### 8. Retry and Error Handling
**What it is**: Configurable retry policies and error handling per task.

**Features**:
- Exponential backoff
- Max retries with custom logic
- Retry on specific exceptions
- Failure callbacks

**Why it matters**:
- Handle transient failures gracefully
- Reduce manual intervention
- Custom business logic on failure

### 9. Parameterized Flows
**What it is**: Pass parameters to flows at runtime via UI or API.

**Why it matters**:
- Ad-hoc execution with different inputs
- No code changes for parameter tweaks
- Scheduled runs with varying parameters
- User-triggered flows

### 10. Blocks (Configuration Management)
**What it is**: Reusable configuration objects for credentials, connections, settings.

**Why it matters**:
- Centralized secret management
- Reuse across multiple flows
- Version control for configurations
- Easy credential rotation

**Examples**: S3 block, Database connection block, Slack webhook block.

## Common Use Cases

### Data Engineering
- ETL/ELT pipelines
- Data lake/warehouse orchestration
- Real-time streaming processing
- Data validation and quality checks

### ML/AI Operations
- Model training pipelines
- Feature engineering workflows
- Model deployment and serving
- Batch inference jobs
- A/B test orchestration

### DevOps and IT
- Infrastructure provisioning
- CI/CD pipeline orchestration
- Backup and disaster recovery
- Log aggregation and processing

### Business Operations
- Report generation
- Multi-system integrations
- Scheduled data exports
- Compliance and audit workflows

## Typical Tech Stacks

Works well with:
- **Data**: Pandas, Polars, Spark, Dask, DuckDB
- **Databases**: PostgreSQL, MySQL, Snowflake, BigQuery, Redshift
- **Storage**: S3, GCS, Azure Blob, MinIO
- **Compute**: Kubernetes, Docker, AWS Batch, GCP Cloud Run
- **ML**: PyTorch, TensorFlow, scikit-learn, XGBoost
- **Monitoring**: Prometheus, Grafana, Datadog (optional integrations)

## Deployment Options

### Self-Hosted (Open Source)
- Free and open source
- Host Prefect Server yourself
- Full control over infrastructure
- Requires ops maintenance

### Prefect Cloud (SaaS)
- Managed orchestration plane
- Zero ops burden
- Enterprise SLAs and support
- Advanced features (RBAC, SSO, audit logs)

## Pricing Model

### Open Source
- Free forever
- Community support
- Self-hosted required

### Prefect Cloud
- Free tier: 20K task runs/month
- Pro: Usage-based ($0.xx per task run over limit)
- Enterprise: Custom pricing with volume discounts, SLAs
