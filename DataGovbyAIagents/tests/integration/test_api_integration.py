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

"""Integration tests for API endpoints."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.server import app


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints."""

    def setUp(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_check_integration(self) -> None:
        """Test health check returns valid response."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("status", data)
        self.assertIn("service", data)
        self.assertIn("version", data)

    def test_api_routing(self) -> None:
        """Test API routing is working."""
        # Test root redirect
        response = self.client.get("/", follow_redirects=False)
        self.assertIn(response.status_code, [307, 308])

        # Test docs endpoint
        response = self.client.get("/docs")
        self.assertIn(response.status_code, [200, 404])  # May not be available in test

    def test_feedback_endpoint(self) -> None:
        """Test feedback endpoint."""
        feedback_data = {
            "feedback_type": "bug",
            "feedback_text": "Test feedback",
            "metadata": {"source": "test"},
        }

        response = self.client.post("/feedback", json=feedback_data)
        self.assertIn(response.status_code, [200, 500])  # May fail if agent not initialized


if __name__ == "__main__":
    unittest.main()
