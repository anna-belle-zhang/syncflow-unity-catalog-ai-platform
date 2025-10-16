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

"""AI Agents for data governance powered by Gemini 2.5 Flash."""

import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel

from app.governance_engine import GovernanceEngine
from app.unity_catalog_client import UnityCatalogClient

logger = logging.getLogger(__name__)


class DataGovernanceAgent:
    """Main AI agent for data governance combining discovery, compliance, and documentation.

    Powered by Google Gemini 2.5 Flash via Vertex AI.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        metadata_dataset: str = "unity_catalog_metadata",
        ml_dataset: Optional[str] = None,
        model_id: str = "gemini-2.5-flash-002",
    ) -> None:
        """Initialize the data governance agent.

        Args:
            project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            location: Vertex AI location
            metadata_dataset: BigQuery dataset with UC metadata
            ml_dataset: BigQuery dataset with ML results (optional)
            model_id: Gemini model ID to use
        """
        if project_id is None:
            project_id = os.getenv("PROJECT_ID")
            if not project_id:
                raise ValueError(
                    "project_id must be provided or GOOGLE_CLOUD_PROJECT must be set"
                )

        self.project_id = project_id
        self.location = location
        self.metadata_dataset = metadata_dataset
        self.ml_dataset = ml_dataset
        self.model_id = model_id

        # Initialize Vertex AI
        try:
            vertexai.init(project=project_id, location=location)
            self.model = GenerativeModel(model_id)
            logger.info(f"Initialized Gemini model {model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise

        # Initialize clients
        self.uc_client = UnityCatalogClient(
            project_id=project_id,
            metadata_dataset=metadata_dataset,
            ml_dataset=ml_dataset,
        )

        self.governance = GovernanceEngine(
            project_id=project_id,
            metadata_dataset=metadata_dataset,
            ml_dataset=ml_dataset,
        )

        logger.info(
            f"Initialized DataGovernanceAgent for project {project_id} "
            f"with model {model_id}"
        )

    def discover_data(self, query: str) -> Dict[str, Any]:
        """Discover data in Unity Catalog using natural language.

        Args:
            query: Natural language query about data

        Returns:
            Dictionary with discovery results
        """
        try:
            logger.info(f"Processing discovery query: {query}")

            # Use keyword search for now
            keywords = [w for w in query.split() if len(w) > 3]
            if not keywords:
                return {"results": [], "message": "No meaningful keywords found"}

            keyword = keywords[0].lower()
            tables = self.uc_client.search_tables_by_keyword(keyword, limit=20)

            return {
                "query": query,
                "keyword": keyword,
                "results": tables,
                "count": len(tables),
            }

        except Exception as e:
            logger.error(f"Error in discovery query: {e}")
            return {"error": str(e), "query": query}

    def check_compliance(self) -> Dict[str, Any]:
        """Check overall data governance compliance.

        Returns:
            Dictionary with compliance metrics
        """
        try:
            logger.info("Checking governance compliance")

            score = self.governance.get_compliance_score()
            high_risk = self.governance.get_high_risk_tables()
            undocumented = self.governance.get_undocumented_tables(limit=20)
            freshness = self.uc_client.get_metadata_freshness()

            return {
                "compliance_score": score,
                "high_risk_tables": high_risk,
                "undocumented_tables": undocumented,
                "metadata_freshness": freshness,
                "summary": {
                    "overall_score": score.get("overall_compliance_score", 0),
                    "high_risk_count": len(high_risk),
                    "undocumented_count": len(undocumented),
                },
            }

        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            return {"error": str(e)}

    def get_table_details(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table.

        Args:
            table_name: Fully qualified table name (catalog.schema.table)

        Returns:
            Dictionary with table details
        """
        try:
            logger.info(f"Fetching details for table: {table_name}")
            return self.uc_client.get_table_details(table_name)
        except Exception as e:
            logger.error(f"Error getting table details: {e}")
            return {"error": str(e)}

    def generate_table_description(self, table_name: str) -> str:
        """Generate AI description for a table using Gemini.

        Args:
            table_name: Fully qualified table name

        Returns:
            AI-generated description
        """
        try:
            logger.info(f"Generating description for {table_name}")

            # Get table details
            details = self.get_table_details(table_name)
            if "error" in details:
                return f"Error: {details['error']}"

            # Build column information
            columns = details.get("columns", [])
            column_info = "\n".join(
                [f"- {col['column_name']} ({col['data_type']})" for col in columns]
            )

            # Create prompt for Gemini
            prompt = f"""
            Generate a clear, concise description for this database table:

            Table: {table_name}
            Total Columns: {len(columns)}

            Columns:
            {column_info}

            Analyze the column names and types to infer:
            1. What business entity or concept this table represents
            2. The table's purpose in the data architecture
            3. Key information stored

            Provide a 2-3 sentence description that would be helpful for:
            - Data analysts searching for data
            - Business users understanding available data
            - Data governance documentation

            Format: Professional, clear, and business-focused.
            """

            response = self.model.generate_content(prompt)
            description = response.text

            logger.info(f"Generated description for {table_name}")
            return description

        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"Error generating description: {str(e)}"

    def analyze_pii_risk(self) -> Dict[str, Any]:
        """Analyze PII risk across the catalog.

        Returns:
            Dictionary with PII risk analysis
        """
        try:
            logger.info("Analyzing PII risk")

            pii_tables = self.uc_client.get_pii_status()
            high_risk = [t for t in pii_tables if t.get("risk_level") == "HIGH"]
            medium_risk = [t for t in pii_tables if t.get("risk_level") == "MEDIUM"]

            return {
                "total_tables_with_pii": len(pii_tables),
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "high_risk_tables": high_risk[:10],
                "medium_risk_tables": medium_risk[:10],
            }

        except Exception as e:
            logger.error(f"Error analyzing PII risk: {e}")
            return {"error": str(e), "total_tables_with_pii": 0}

    def get_metadata_health(self) -> Dict[str, Any]:
        """Check health and freshness of metadata.

        Returns:
            Dictionary with metadata health metrics
        """
        try:
            logger.info("Checking metadata health")
            return self.uc_client.get_metadata_freshness()
        except Exception as e:
            logger.error(f"Error checking metadata health: {e}")
            return {"error": str(e)}

    def query_with_ai(self, question: str) -> str:
        """Answer questions about data using AI.

        Args:
            question: Natural language question

        Returns:
            AI-generated answer
        """
        try:
            logger.info(f"Processing AI query: {question}")

            # Create context from available information
            compliance = self.check_compliance()
            metadata_health = self.get_metadata_health()

            prompt = f"""
            You are a data governance expert. Answer the following question about
            a data catalog based on the provided metadata:

            Question: {question}

            Context:
            - Compliance Score: {compliance.get('summary', {}).get('overall_score', 0)}/100
            - High Risk Tables: {compliance.get('summary', {}).get('high_risk_count', 0)}
            - Metadata Status: {metadata_health.get('freshness_status', 'UNKNOWN')}

            Provide a helpful, professional answer based on the context.
            """

            response = self.model.generate_content(prompt)
            answer = response.text

            logger.info("AI query processed successfully")
            return answer

        except Exception as e:
            logger.error(f"Error in AI query: {e}")
            return f"Error processing query: {str(e)}"
