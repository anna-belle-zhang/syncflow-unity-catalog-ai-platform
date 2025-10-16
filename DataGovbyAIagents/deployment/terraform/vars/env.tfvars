# Copyright 2025 SyncFlow Contributors
# Terraform variables for environment configuration

# Set these to your values
project_id  = "your-gcp-project-id"
region      = "us-central1"
environment = "dev"
app_name    = "syncflow-api"

tags = {
  project     = "syncflow"
  environment = "dev"
  managed_by  = "terraform"
  created_by  = "terraform"
}
