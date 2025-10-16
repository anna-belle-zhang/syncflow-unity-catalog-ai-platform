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

"""HTTP client for communicating with SyncFlow backend API."""

import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with SyncFlow backend API."""

    def __init__(self, base_url: str = "http://localhost:8080") -> None:
        """Initialize API client.

        Args:
            base_url: Base URL of backend API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check API health.

        Returns:
            Health status
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    def discover_data(self, query: str) -> Dict[str, Any]:
        """Discover data using query.

        Args:
            query: Search query

        Returns:
            Discovery results
        """
        try:
            response = self.session.post(
                f"{self.base_url}/discover", json={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Discovery error: {e}")
            return {"error": str(e)}

    def get_compliance(self) -> Dict[str, Any]:
        """Get compliance metrics.

        Returns:
            Compliance information
        """
        try:
            response = self.session.get(f"{self.base_url}/compliance")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            return {"error": str(e)}

    def get_table_details(self, table_name: str) -> Dict[str, Any]:
        """Get table details.

        Args:
            table_name: Fully qualified table name

        Returns:
            Table details
        """
        try:
            response = self.session.get(
                f"{self.base_url}/table-details/{table_name}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Table details error: {e}")
            return {"error": str(e)}

    def generate_description(self, table_name: str) -> Dict[str, str]:
        """Generate table description.

        Args:
            table_name: Fully qualified table name

        Returns:
            Generated description
        """
        try:
            response = self.session.post(
                f"{self.base_url}/generate-description",
                json={"table_name": table_name},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Description generation error: {e}")
            return {"error": str(e)}

    def analyze_pii(self) -> Dict[str, Any]:
        """Analyze PII risk.

        Returns:
            PII risk analysis
        """
        try:
            response = self.session.get(f"{self.base_url}/pii-analysis")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"PII analysis error: {e}")
            return {"error": str(e)}

    def get_metadata_health(self) -> Dict[str, Any]:
        """Get metadata health.

        Returns:
            Metadata health metrics
        """
        try:
            response = self.session.get(f"{self.base_url}/metadata-health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Metadata health error: {e}")
            return {"error": str(e)}

    def query_ai(self, question: str) -> Dict[str, str]:
        """Query AI agent.

        Args:
            question: Natural language question

        Returns:
            AI response
        """
        try:
            response = self.session.post(
                f"{self.base_url}/query", json={"question": question}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return {"error": str(e)}

    def send_feedback(
        self,
        feedback_type: str,
        feedback_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Send feedback to backend.

        Args:
            feedback_type: Type of feedback
            feedback_text: Feedback text
            metadata: Additional metadata

        Returns:
            Success response
        """
        try:
            data = {
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "metadata": metadata or {},
            }
            response = self.session.post(f"{self.base_url}/feedback", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Feedback submission error: {e}")
            return {"error": str(e)}
