# Horizon (Managed Prefect) Product Knowledge

## Overview

Horizon is Prefect's fully managed platform that provides enterprise-grade workflow orchestration without operational overhead. It combines Prefect's powerful capabilities with enterprise features, SLAs, and hands-off infrastructure management.

## Value Proposition

**"All the power of Prefect, none of the ops burden."**

Horizon lets data teams focus on building pipelines, not managing infrastructure. You get enterprise-grade reliability, security, and support without hiring a platform team.

## What's Included

### 1. Managed Prefect Cloud

**What it is**: Fully managed orchestration plane with 99.9% SLA.

**What you get**:

- Zero infrastructure management
- Automatic scaling
- Global CDN for UI/API
- Redundant, multi-region deployment
- Automatic upgrades (no downtime)
- 24/7 monitoring and incident response

**Why it matters**: Your team builds pipelines, not Kubernetes clusters.

### 2. Enterprise Security & Compliance

**Access Control**:

- Role-Based Access Control (RBAC)
- Team-based permissions
- SSO/SAML integration (Okta, Azure AD, etc.)
- API key management with scoping

**Audit & Compliance**:

- Complete audit logs for all actions
- SOC 2 Type II certified
- GDPR compliant
- Data residency options (US, EU, etc.)
- Encryption at rest and in transit

**Why it matters**: Meet enterprise security requirements without building custom solutions.

### 3. Advanced Work Pool Management

**Features**:

- Managed work pools (we run the infrastructure)
- Bring-your-own work pools (run on your infra)
- Auto-scaling based on queue depth
- Multi-region work pool support
- Container-based execution

**Why it matters**: Right-size infrastructure automatically, pay only for what you use.

### 4. Enhanced Observability

**Beyond Open Source**:

- Custom dashboards and analytics
- Advanced alerting with PagerDuty/Slack integration
- Longer data retention (12+ months)
- Custom metrics and reporting
- Anomaly detection for flow runs

**Why it matters**: Proactive issue detection, better cost visibility, compliance reporting.

### 5. Dedicated Support

**Support Tiers**:

- Standard: Email support, 24-hour response
- Premium: Slack channel, 4-hour response, dedicated CSM
- Enterprise: 1-hour response, solutions architect, quarterly business reviews

**Professional Services**:

- Migration assistance from Airflow/Luigi/other tools
- Custom workflow development
- Architecture reviews
- Training and onboarding

**Why it matters**: Faster time to value, expert guidance, guaranteed response times.

### 6. CI/CD Integrations

**Native Integrations**:

- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps
- CircleCI

**Features**:

- Automated deployment from git
- Environment-based deployments (dev/staging/prod)
- Rollback capabilities
- Deployment previews

**Why it matters**: Seamless developer workflows, gitops-style deployments.

### 7. Advanced Scheduling

**Capabilities**:

- Cron scheduling with timezone support
- Interval-based scheduling
- Custom schedule logic (Python functions)
- External event triggers (webhooks)
- Backfill support for historical runs

**Why it matters**: Flexible scheduling without custom cron jobs or Lambda functions.

## Pricing Model

### Structure

**Usage-based**: Pay per execution hour

**What's an execution hour?**

- Sum of all task run durations in a flow run
- Example: 10 tasks running 6 minutes each = 1 hour
- Parallel tasks count separately

### Pricing Tiers

**Starter** (~$500/month)

- 500 execution hours included
- Standard support
- Community Slack
- 3-month data retention

**Pro** (~$2,000/month)

- 2,000 execution hours included
- Premium support (4-hour SLA)
- Dedicated Slack channel
- 12-month data retention
- SSO/SAML

**Enterprise** (Custom)

- Custom execution hours
- Volume discounts
- 1-hour support SLA
- Dedicated solutions architect
- Custom data retention
- On-premise deployment option

### ROI Calculation

**Typical savings compared to self-hosted**:

- **Infrastructure costs**: $2-5K/month (servers, databases, load balancers)
- **Engineering time**: 40-80 hours/month = $6-12K/month at $150/hr loaded cost
- **Opportunity cost**: Strategic projects vs. ops work

**Total self-hosted cost**: $8-17K/month
**Horizon cost**: $2-5K/month
**Net savings**: $6-12K/month or 50-70% reduction

## Migration Path

### From Airflow

1. **Assessment**: We analyze your DAGs and provide migration plan
2. **Conversion**: Automated DAG-to-Prefect conversion tool + manual refinement
3. **Parallel Running**: Run both systems during transition
4. **Cutover**: Gradual migration by pipeline priority
5. **Decommission**: Shut down Airflow infrastructure

**Timeline**: 4-12 weeks depending on complexity
**Success rate**: 95%+ of migrations complete successfully

### From Luigi, Argo, or Custom Solutions

Similar phased approach with tailored conversion strategies.

## Deployment Architecture

### How it Works

```
┌─────────────────────────────────────┐
│  Horizon Control Plane (Managed)    │
│  - API/UI                           │
│  - Scheduling                       │
│  - Metadata DB                      │
│  - Monitoring                       │
└─────────────────────────────────────┘
         │
         │ Secure connection
         ▼
┌─────────────────────────────────────┐
│  Your Execution Environment         │
│  - Work pools                       │
│  - Your compute (K8s, VMs, etc.)    │
│  - Your data (never leaves)         │
└─────────────────────────────────────┘
```

**Key Points**:

- Orchestration metadata in Horizon Cloud
- Code and data execute in your environment
- Hybrid architecture for security + convenience

## Common Objections & Responses

### "We can self-host for free"

**Response**: True upfront, but factor in:

- Engineer time maintaining infrastructure (40-80 hrs/month)
- Opportunity cost of strategic projects
- Risk of downtime without dedicated ops team
- Scaling costs (load balancers, databases, monitoring)

Horizon breaks even at ~20 hours/month of ops work.

### "Concerned about vendor lock-in"

**Response**:

- Built on open-source Prefect (can always self-host)
- Standard Python code (portable)
- Export functionality for all metadata
- Hybrid architecture (you control execution)

### "Need to keep data on-premise"

**Response**:

- Data never leaves your environment
- Only metadata (run status, logs) goes to Horizon
- Enterprise tier offers on-premise deployment option
- Hybrid execution model addresses compliance

### "Too expensive for our scale"

**Response**:

- Calculate TCO vs. self-hosted (infrastructure + engineering time)
- Free tier for small workloads (500 hours)
- Volume discounts at scale
- ROI typically 3-6 months

## Competitive Positioning

### vs. AWS Step Functions

- **Horizon advantage**: Not locked to AWS, richer Python support, better observability
- **Step Functions**: Deeper AWS integration

### vs. Google Cloud Composer (Managed Airflow)

- **Horizon advantage**: Modern Python-native code, dynamic workflows, lower ops burden
- **Composer**: Familiar to Airflow users

### vs. Databricks Workflows

- **Horizon advantage**: Not Databricks-specific, broader use cases, lower cost
- **Databricks**: Integrated with Delta Lake/ML

### vs. Temporal Cloud

- **Horizon advantage**: Higher-level abstractions, easier learning curve, data-focused
- **Temporal**: Lower-level durability guarantees, microservices workflows

## Ideal Customer Profile

### Best Fit

- Data teams (5-50 engineers)
- 50-500 workflows
- Growing quickly, limited ops resources
- Need enterprise security/compliance
- Multi-cloud or hybrid environment
- Currently on Airflow (pain points)

### Not Ideal

- <5 workflows (over-engineering)
- Need on-premise-only solution (unless Enterprise tier)
- Deeply embedded in AWS ecosystem (Step Functions may suffice)
- Ultra-high-frequency workflows (millions of tasks/day)

## Success Metrics

### Customer Outcomes

- **Time to deploy first workflow**: <1 week (vs. 4-8 weeks self-hosted)
- **Engineering time saved**: 40-80 hours/month
- **Workflow reliability**: 99.5%+ success rate
- **Scaling capacity**: 10x growth without ops team growth

## Getting Started

### Trial Process

1. **Sign up**: Free tier, no credit card
2. **Connect work pool**: Docker, Kubernetes, or managed
3. **Deploy first flow**: From template or convert existing
4. **Iterate**: Build, test, monitor
5. **Scale**: Upgrade tier as needed

### Typical POC (Proof of Concept)

- **Duration**: 30 days
- **Goal**: Migrate 3-5 critical workflows
- **Support**: Dedicated solutions engineer
- **Success criteria**: Reliability, ease of use, team adoption
