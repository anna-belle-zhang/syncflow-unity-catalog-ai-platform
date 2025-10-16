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

"""Load testing for SyncFlow API.

Run with: locust -f tests/load_test/load_test.py --host=http://localhost:8080
"""

import random
from typing import Any, Dict

from locust import HttpUser, between, task


class SyncFlowUser(HttpUser):
    """Simulated SyncFlow user for load testing."""

    wait_time = between(1, 3)

    @task(1)
    def health_check(self) -> None:
        """Task: Check API health."""
        self.client.get("/health")

    @task(2)
    def discover_data(self) -> None:
        """Task: Discover data."""
        queries = [
            {"query": "customer"},
            {"query": "sales"},
            {"query": "product"},
            {"query": "order"},
        ]
        query = random.choice(queries)
        self.client.post("/discover", json=query)

    @task(1)
    def get_compliance(self) -> None:
        """Task: Get compliance metrics."""
        self.client.get("/compliance")

    @task(1)
    def analyze_pii(self) -> None:
        """Task: Analyze PII risk."""
        self.client.get("/pii-analysis")

    @task(1)
    def check_metadata_health(self) -> None:
        """Task: Check metadata health."""
        self.client.get("/metadata-health")

    def on_start(self) -> None:
        """Called when user starts."""
        self.client.get("/health")
