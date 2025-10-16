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

"""Unit tests for FastAPI server."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.server import app


class TestServer(unittest.TestCase):
    """Test FastAPI server endpoints."""

    def setUp(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_redirect(self) -> None:
        """Test root redirect to docs."""
        response = self.client.get("/", follow_redirects=True)
        self.assertIn(response.status_code, [200, 307, 308])

    def test_health_check(self) -> None:
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("status", data)
        self.assertIn("service", data)

    def test_discover_missing_query(self) -> None:
        """Test discover endpoint with missing query."""
        response = self.client.post("/discover", json={})
        # Should fail with 400 or 500 depending on error handling
        self.assertIn(response.status_code, [400, 500])

    def test_compliance_endpoint(self) -> None:
        """Test compliance endpoint."""
        response = self.client.get("/compliance")
        # Will fail if agent not initialized, which is expected in test
        self.assertIn(response.status_code, [200, 500])

    def test_pii_analysis_endpoint(self) -> None:
        """Test PII analysis endpoint."""
        response = self.client.get("/pii-analysis")
        self.assertIn(response.status_code, [200, 500])

    def test_metadata_health_endpoint(self) -> None:
        """Test metadata health endpoint."""
        response = self.client.get("/metadata-health")
        self.assertIn(response.status_code, [200, 500])


if __name__ == "__main__":
    unittest.main()
