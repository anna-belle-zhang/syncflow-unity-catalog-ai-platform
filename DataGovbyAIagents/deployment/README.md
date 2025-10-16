# Deployment Guide

This directory contains deployment configurations for SyncFlow.

## Structure

```
deployment/
├── ci/                 # Continuous Integration pipelines
│   └── pr_checks.yaml  # GitHub Actions PR validation
├── cd/                 # Continuous Deployment
│   ├── staging.yaml    # Staging deployment
│   └── deploy-to-prod.yaml  # Production deployment
└── terraform/          # Infrastructure as Code
    ├── dev/           # Development environment
    └── main/          # Production environment
```

## Quick Start

### Local Development

1. Set up environment variables:
   ```bash
   cp .env.tpl .env
   # Edit .env with your configuration
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Run locally:
   ```bash
   make playground
   ```

### Development Environment Deployment

Prerequisites:
- Terraform installed
- GCP project created
- gcloud CLI configured

Deploy dev environment:
```bash
PROJECT_ID=your-project-id make setup-dev-env
```

## CI/CD Pipeline

### Pull Request Checks

Runs when PR is opened:
- Unit tests
- Code linting
- Type checking
- Code coverage verification

### Staging Deployment

Deploys to staging when merged to develop branch:
- Build Docker image
- Push to Artifact Registry
- Deploy to Cloud Run

### Production Deployment

Deploys to production when merged to main branch:
- Build Docker image
- Push to Artifact Registry
- Deploy to Cloud Run with traffic gradually

## Environment Variables

See `.env.tpl` for all required environment variables.

Key variables:
- `PROJECT_ID`: GCP project ID
- `REGION`: GCP region (default: us-central1)
- `MODEL_ID`: Gemini model to use
- `METADATA_DATASET`: BigQuery dataset with Unity Catalog metadata
- `ML_DATASET`: BigQuery dataset with ML results

## Terraform

### Initialize

```bash
cd deployment/terraform/dev
terraform init
```

### Plan

```bash
terraform plan -var-file vars/env.tfvars
```

### Apply

```bash
terraform apply -var-file vars/env.tfvars
```

### Destroy

```bash
terraform destroy -var-file vars/env.tfvars
```

## Monitoring

### Logs

View application logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=syncflow-api" \
  --limit 50 \
  --format json
```

### Metrics

Monitor in Cloud Console:
- Application latency
- Error rates
- Request count
- Resource utilization

## Troubleshooting

### Backend not starting

Check logs:
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 20
```

### BigQuery connection issues

Verify:
1. Service account has BigQuery roles
2. Datasets exist and are accessible
3. Environment variables are set correctly

### Frontend cannot reach backend

Ensure:
1. Backend is running and accessible
2. `API_BASE_URL` is correctly configured
3. CORS is properly configured
4. Network policies allow traffic

## Cost Optimization

- Use Cloud Run for auto-scaling
- Enable Cloud Caching for BigQuery
- Set appropriate resource limits
- Use preemptible VMs for non-critical workloads

## Security

- Secrets stored in Secret Manager
- Service accounts with minimal permissions
- VPC isolation for sensitive data
- Audit logging enabled

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform Documentation](https://www.terraform.io/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
