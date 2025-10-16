# Copyright 2025 SyncFlow Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "syncflow-api"
}

variable "container_image" {
  description = "Container image URL"
  type        = string
  default     = "gcr.io/cloudfunctions/python311"
}

variable "enable_apis" {
  description = "List of APIs to enable"
  type        = list(string)
  default = [
    "run.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "logging.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
  ]
}

variable "tags" {
  description = "Labels to apply to resources"
  type        = map(string)
  default = {
    project     = "syncflow"
    environment = "dev"
    managed_by  = "terraform"
  }
}
