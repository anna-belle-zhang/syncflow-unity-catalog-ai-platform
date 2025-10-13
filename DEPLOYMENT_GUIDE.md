# Deployment Guide - Fivetran Challenge Submission

This guide covers deploying the SyncFlow Unity Catalog AI Governance Platform to the cloud for the Fivetran Challenge submission.

## 🎯 Deployment Options

### Option 1: Streamlit Community Cloud (Easiest, Free)

**Best for**: Quick deployment, demo purposes

**Steps**:

1. **Push code to GitHub** (if not already done):
```bash
cd /mnt/e/A/syncflow-unity-catalog-ai-platform
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/syncflow-unity-catalog-ai-platform.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**:
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Connect your GitHub repository
   - Select repository: `syncflow-unity-catalog-ai-platform`
   - Main file path: `DataGovbyAIagents/governance_dashboard.py`
   - Click "Deploy"

3. **Configure Secrets** (in Streamlit Cloud dashboard):
```toml
# .streamlit/secrets.toml
GOOGLE_CLOUD_PROJECT = "your-gcp-project-id"
GEMINI_API_KEY = "your-gemini-api-key"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

4. **Update code to use Streamlit secrets** (if needed):
```python
import streamlit as st

# Instead of:
# project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

# Use:
project_id = st.secrets.get("GOOGLE_CLOUD_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT"))
```

**Result**: Get URL like `https://your-app-name.streamlit.app`

---

### Option 2: Google Cloud Run (Production-Ready)

**Best for**: Professional deployment, auto-scaling, Google Cloud integration

**Prerequisites**:
- Google Cloud account with billing enabled
- gcloud CLI installed
- Docker installed (optional, Cloud Build can handle it)

**Steps**:

1. **Set up environment variables**:
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export SERVICE_NAME="governance-dashboard"
```

2. **Enable required APIs**:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

3. **Build and deploy using Cloud Build**:
```bash
cd /mnt/e/A/syncflow-unity-catalog-ai-platform/DataGovbyAIagents

# Build container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --set-env-vars GEMINI_API_KEY=your-gemini-api-key \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

4. **Add service account credentials** (if needed):
```bash
# Create secret for service account
gcloud secrets create bigquery-credentials \
  --data-file=../service-account.json

# Grant Cloud Run access to secret
gcloud run services update $SERVICE_NAME \
  --update-secrets=/secrets/gcp/credentials.json=bigquery-credentials:latest \
  --region $REGION
```

**Result**: Get URL like `https://governance-dashboard-abc123-uc.a.run.app`

---

### Option 3: Google Compute Engine (Full Control)

**Best for**: Custom configuration, persistent VM

**Steps**:

1. **Create VM instance**:
```bash
gcloud compute instances create governance-dashboard \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --boot-disk-size=20GB \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y python3-pip git
    git clone https://github.com/YOUR_USERNAME/syncflow-unity-catalog-ai-platform.git
    cd syncflow-unity-catalog-ai-platform/DataGovbyAIagents
    pip3 install -r requirements.txt
    nohup streamlit run governance_dashboard.py --server.port=8501 --server.address=0.0.0.0 &'
```

2. **Configure firewall**:
```bash
gcloud compute firewall-rules create allow-streamlit \
  --allow tcp:8501 \
  --target-tags http-server
```

3. **Get external IP**:
```bash
gcloud compute instances describe governance-dashboard \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

**Result**: Access via `http://EXTERNAL_IP:8501`

---

## 🔧 Pre-Deployment Configuration

### Update governance_dashboard.py for Cloud Deployment

Add this at the top of `governance_dashboard.py`:

```python
import os
import json
import streamlit as st

# Cloud deployment: Load credentials from environment or Streamlit secrets
def load_gcp_credentials():
    """Load GCP credentials for cloud deployment"""
    # Try Streamlit secrets first (for Streamlit Cloud)
    if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
        return st.secrets['gcp_service_account']

    # Try environment variable
    creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if creds_json:
        return json.loads(creds_json)

    # Try file path
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path and os.path.exists(creds_path):
        with open(creds_path) as f:
            return json.load(f)

    return None

# Load credentials at startup
credentials = load_gcp_credentials()
if credentials:
    # Configure BigQuery client with credentials
    from google.oauth2 import service_account
    credentials_obj = service_account.Credentials.from_service_account_info(credentials)
    # Pass to BigQuery client initialization
```

---

## 🧪 Testing Your Deployment

### Checklist:
- [ ] Homepage loads successfully
- [ ] Overview page shows metrics and charts
- [ ] Search page accepts queries and returns results
- [ ] Documentation page generates AI descriptions
- [ ] Compliance page displays scores and recommendations
- [ ] No console errors
- [ ] API keys/credentials work correctly
- [ ] BigQuery connection successful
- [ ] Gemini API responds within 3 seconds
- [ ] Mobile responsive (if applicable)

### Test URLs:
```bash
# Local test
streamlit run DataGovbyAIagents/governance_dashboard.py

# Cloud test
curl -I https://your-deployed-url.com
```

---

## 📊 Monitoring & Logging

### Streamlit Cloud:
- View logs in Streamlit Cloud dashboard
- Monitor app health and usage

### Google Cloud Run:
```bash
# View logs
gcloud run services logs read $SERVICE_NAME --region $REGION

# Monitor metrics
gcloud run services describe $SERVICE_NAME --region $REGION
```

### Google Compute Engine:
```bash
# SSH into VM
gcloud compute ssh governance-dashboard --zone=us-central1-a

# View application logs
journalctl -u streamlit -f
```

---

## 🔒 Security Best Practices

1. **Never commit sensitive data**:
   - Use `.env` files (in `.gitignore`)
   - Use Google Secret Manager
   - Use Streamlit secrets

2. **Restrict API access**:
   - Use API key restrictions (HTTP referrers, IP addresses)
   - Enable billing alerts
   - Set up quotas

3. **Secure BigQuery**:
   - Use service account with minimal permissions
   - Enable data access logs
   - Set up VPC Service Controls (production)

---

## 💰 Cost Estimates

### Streamlit Community Cloud:
- **FREE** for public apps

### Google Cloud Run:
- **$0.001** per request (first 2M requests/month free)
- **$0.00002** per vCPU-second (first 180K vCPU-seconds free)
- **Estimated**: $5-20/month for demo usage

### Google Compute Engine:
- **e2-medium**: ~$25/month (24/7)
- **Preemptible**: ~$7/month
- **Estimated**: $7-25/month

### Google BigQuery:
- **Storage**: $0.02/GB/month (first 10GB free)
- **Queries**: $5/TB (first 1TB/month free)
- **Estimated**: <$5/month for demo data

### Gemini API:
- **Gemini 2.5 Flash**: Very affordable (check current pricing)
- **Free tier**: Available for testing
- **Estimated**: $0-10/month for demo usage

**Total Estimated Cost**: $0-50/month depending on deployment choice

---

## 🚀 Quick Deploy Commands

### For Streamlit Cloud (Fastest):
```bash
# Just push to GitHub and use web UI
git push origin main
# Then visit https://streamlit.io/cloud
```

### For Cloud Run (One Command):
```bash
cd DataGovbyAIagents
gcloud run deploy governance-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GEMINI_API_KEY=YOUR_KEY
```

---

## 📝 Update README with Deployment URL

After deploying, add to README.md:

```markdown
## 🌐 Live Demo

**Hosted Application**: [https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)

Try it out! The dashboard is pre-loaded with sample Unity Catalog metadata.
```

---

## ❓ Troubleshooting

### Issue: Streamlit Cloud deployment fails
- Check `requirements.txt` is in correct location
- Verify Python version compatibility
- Check for missing dependencies

### Issue: Cloud Run timeout
- Increase `--timeout` to 300 seconds
- Increase `--memory` to 2Gi
- Check Gemini API response times

### Issue: BigQuery connection fails
- Verify service account permissions
- Check credentials are properly loaded
- Verify dataset exists and is accessible

### Issue: Gemini API errors
- Check API key is valid
- Verify billing is enabled
- Check API quotas and limits

---

## 🎬 Next Steps

1. Choose deployment option (Streamlit Cloud recommended for quick start)
2. Deploy application
3. Test all features
4. Record demo video showing hosted application
5. Add deployment URL to submission form

**Good luck with your Fivetran Challenge submission! 🚀**
