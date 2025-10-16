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

# Enable required GCP APIs
resource "google_project_service" "required_apis" {
  for_each = toset(var.enable_apis)

  service            = each.value
  disable_on_destroy = false
}

# Wait for APIs to be enabled
resource "time_sleep" "wait_for_apis" {
  depends_on      = [google_project_service.required_apis]
  create_duration = "30s"
}

output "enabled_apis" {
  description = "List of enabled APIs"
  value       = var.enable_apis
}
