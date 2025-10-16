# SyncFlow Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Testing](#testing)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Python 3.10+
- Docker (for containerization)
- gcloud CLI (for GCP deployment)
- Terraform (for infrastructure)
- Git (for version control)

### GCP Setup
1. Create a GCP project
2. Enable required APIs:
   ```bash
   gcloud services enable \
     run.googleapis.com \
     bigquery.googleapis.com \
     aiplatform.googleapis.com \
     logging.googleapis.com \
     artifactregistry.googleapis.com \
     cloudbuild.googleapis.com
   ```

3. Create a service account:
   ```bash
   gcloud iam service-accounts create syncflow-sa \
     --display-name "SyncFlow Service Account"
   ```

4. Grant necessary roles:
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member=serviceAccount:syncflow-sa@PROJECT_ID.iam.gserviceaccount.com \
     --role=roles/bigquery.dataEditor

   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member=serviceAccount:syncflow-sa@PROJECT_ID.iam.gserviceaccount.com \
     --role=roles/aiplatform.user

   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member=serviceAccount:syncflow-sa@PROJECT_ID.iam.gserviceaccount.com \
     --role=roles/logging.logWriter
   ```

5. Create and download service account key:
   ```bash
   gcloud iam service-accounts keys create sa-key.json \
     --iam-account=syncflow-sa@PROJECT_ID.iam.gserviceaccount.com
   ```

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd DataGovbyAIagents
```

### 2. Install Dependencies
```bash
make install
```

This will:
- Install uv if not present
- Sync all dependencies from pyproject.toml

### 3. Create Environment File
```bash
cp .env.tpl .env
```

Edit `.env` with your configuration:
```bash
PROJECT_ID=your-gcp-project
REGION=us-central1
MODEL_ID=gemini-2.5-flash-002
METADATA_DATASET=unity_catalog_metadata
ML_DATASET=ml_models
```

### 4. Set GCP Credentials
```bash
export GOOGLE_APPLICATION_CREDENTIALS=path/to/sa-key.json
```

### 5. Run Local Application
```bash
# Run both backend and frontend
make playground

# Or run separately:
make backend    # Terminal 1
make ui        # Terminal 2
```

- Backend: http://localhost:8080
- Frontend: http://localhost:8501
- API Docs: http://localhost:8080/docs

## Testing

### Run All Tests
```bash
make test
```

### Run Unit Tests Only
```bash
make test-unit
```

### Run Integration Tests Only
```bash
make test-integration
```

### Run with Coverage
```bash
make test-coverage
```

### Run Linting
```bash
make lint
```

Format code:
```bash
make format
```

## Docker Deployment

### Build Docker Image
```bash
make docker-build
```

### Run Docker Container
```bash
make docker-run
```

### Push to Artifact Registry
```bash
docker tag syncflow-api:latest gcr.io/PROJECT_ID/syncflow-api:latest
docker push gcr.io/PROJECT_ID/syncflow-api:latest
```

## Cloud Deployment

### 1. Set Environment
```bash
export PROJECT_ID=your-gcp-project
export REGION=us-central1
```

### 2. Deploy to Cloud Run
```bash
gcloud run deploy syncflow-api \
  --image gcr.io/$PROJECT_ID/syncflow-api:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=$PROJECT_ID,METADATA_DATASET=unity_catalog_metadata \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 100
```

### 3. Deploy Frontend to Cloud Run
```bash
gcloud run deploy syncflow-frontend \
  --source frontend/ \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated
```

### 4. Infrastructure with Terraform

Initialize Terraform:
```bash
cd deployment/terraform
terraform init
```

Plan deployment:
```bash
terraform plan -var-file vars/env.tfvars \
  -var project_id=$PROJECT_ID \
  -var region=$REGION
```

Apply configuration:
```bash
terraform apply -var-file vars/env.tfvars \
  -var project_id=$PROJECT_ID \
  -var region=$REGION
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PROJECT_ID | GCP Project ID | Required |
| REGION | GCP Region | us-central1 |
| MODEL_ID | Gemini Model ID | gemini-2.5-flash-002 |
| METADATA_DATASET | BigQuery metadata dataset | unity_catalog_metadata |
| ML_DATASET | BigQuery ML dataset | ml_models |
| PORT | API port | 8080 |
| API_BASE_URL | Backend URL | http://localhost:8080 |
| LOG_LEVEL | Logging level | INFO |
| DEBUG | Debug mode | false |

### BigQuery Datasets

Ensure these datasets exist with the following tables:

**metadata_dataset:**
- `tables` - Catalog tables metadata
- `columns` - Column definitions

**ml_dataset:**
- `pii_summary_by_table` - PII detection results

## Monitoring

### Cloud Logging
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --format json
```

### Cloud Monitoring
View metrics in Cloud Console:
- Go to Monitoring → Dashboards
- Select the SyncFlow dashboard

### Application Logs
```bash
gcloud logging read "labels.app=syncflow" --limit 100
```

## Troubleshooting

### Issue: "Cannot import module 'vertexai'"

**Solution:**
```bash
make install
export GOOGLE_APPLICATION_CREDENTIALS=path/to/sa-key.json
```

### Issue: "BigQuery dataset not found"

**Solution:**
1. Verify dataset names in .env
2. Check service account permissions
3. Ensure datasets exist in BigQuery

### Issue: "Gemini API error"

**Solution:**
1. Verify MODEL_ID is correct
2. Check Vertex AI is enabled
3. Verify service account has aiplatform.user role

### Issue: "Frontend cannot reach backend"

**Solution:**
1. Verify backend is running: `curl http://localhost:8080/health`
2. Check API_BASE_URL in .env
3. Verify CORS configuration

### Issue: "Streamlit connection timeout"

**Solution:**
1. Restart both backend and frontend
2. Clear Streamlit cache: `rm -rf .streamlit_chats`
3. Check network connectivity

### Issue: "Tests fail"

**Solution:**
1. Ensure mocks are properly configured
2. Check environment variables are set
3. Verify Python version: `python --version`

## Rollback

### Rollback Cloud Run
```bash
gcloud run services describe syncflow-api --region $REGION --format='value(status.traffic[0].revision)'
gcloud run services update-traffic syncflow-api \
  --to-revisions <previous-revision>=100 \
  --region $REGION
```

### Rollback Terraform
```bash
terraform destroy -var-file vars/env.tfvars
# Or restore from tfstate backup
```

## Performance Tuning

### Backend Optimization
- Increase Cloud Run memory: `--memory 4Gi`
- Increase CPU: `--cpu 4`
- Adjust BigQuery query caching

### Frontend Optimization
- Enable Streamlit caching
- Minimize API calls
- Use pagination for large datasets

## Security Checklist

- [ ] Service account key is not committed
- [ ] Secret Manager configured for credentials
- [ ] IAM roles follow least privilege
- [ ] VPC policies restrict access
- [ ] Audit logging enabled
- [ ] SSL/TLS enabled for all communication
- [ ] Authentication configured

## Next Steps

1. Deploy to staging environment
2. Run integration tests
3. Monitor application metrics
4. Configure alerts
5. Set up backups
6. Document runbooks

## Support

For issues or questions:
1. Check logs: `make docker-run` or `gcloud logging read`
2. Review API docs: http://localhost:8080/docs
3. Check architecture: see ARCHITECTURE.md
4. Review API reference: see API_REFERENCE.md
