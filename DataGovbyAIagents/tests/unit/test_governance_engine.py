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

"""Unit tests for governance engine."""

import unittest
from unittest.mock import MagicMock, patch

from app.governance_engine import GovernanceEngine


class TestGovernanceEngine(unittest.TestCase):
    """Test GovernanceEngine class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        with patch("app.governance_engine.bigquery.Client"):
            self.engine = GovernanceEngine(
                project_id="test-project",
                metadata_dataset="metadata",
                ml_dataset="ml_models",
            )
            self.engine.bq_client = MagicMock()

    def test_initialization(self) -> None:
        """Test GovernanceEngine initialization."""
        self.assertEqual(self.engine.project_id, "test-project")
        self.assertEqual(self.engine.metadata_dataset, "metadata")
        self.assertEqual(self.engine.ml_dataset, "ml_models")

    def test_get_compliance_score(self) -> None:
        """Test compliance score calculation."""
        # Mock BigQuery response
        mock_df = MagicMock()
        mock_df.to_dataframe.return_value.to_dict.return_value = [
            {
                "total_tables": 100,
                "tables_with_pii": 20,
                "high_risk_tables": 5,
                "documented_tables": 80,
                "documentation_pct": 80.0,
                "high_risk_pct": 25.0,
            }
        ]
        self.engine.bq_client.query.return_value = mock_df.to_dataframe.return_value

        # This test shows the expected structure
        result = self.engine.get_compliance_score()
        self.assertIn("overall_compliance_score", result)
        self.assertTrue(0 <= result["overall_compliance_score"] <= 100)

    def test_validate_table_exists(self) -> None:
        """Test table existence validation."""
        # Valid format
        self.assertTrue(self.engine.validate_table_exists("catalog.schema.table"))

        # Invalid format
        self.assertFalse(self.engine.validate_table_exists("catalog.table"))
        self.assertFalse(self.engine.validate_table_exists("table"))

    def test_get_high_risk_tables(self) -> None:
        """Test getting high-risk tables."""
        result = self.engine.get_high_risk_tables()
        self.assertIsInstance(result, list)

    def test_get_undocumented_tables(self) -> None:
        """Test getting undocumented tables."""
        result = self.engine.get_undocumented_tables(limit=10)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
