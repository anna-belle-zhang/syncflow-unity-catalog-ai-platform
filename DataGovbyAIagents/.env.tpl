# Copyright 2025 SyncFlow Contributors
# Environment configuration template for SyncFlow

# GCP Configuration
PROJECT_ID=your-gcp-project-id
REGION=us-central1
LOCATION=us-central1

# Vertex AI Configuration
MODEL_ID=gemini-2.5-flash-002

# BigQuery Datasets
METADATA_DATASET=unity_catalog_metadata
ML_DATASET=ml_models

# Unity Catalog Configuration
UNITY_CATALOG_HOST=your-unity-catalog-host
UNITY_CATALOG_TOKEN=your-unity-catalog-token

# API Configuration
PORT=8080
API_BASE_URL=http://localhost:8080

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false

# Backend Server Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8080
UVICORN_RELOAD=true

# Streamlit Configuration
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=true
