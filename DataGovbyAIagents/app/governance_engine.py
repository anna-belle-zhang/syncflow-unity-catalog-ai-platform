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

"""Data governance engine for compliance monitoring and scoring."""

import logging
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

logger = logging.getLogger(__name__)


class GovernanceEngine:
    """Engine for data governance, compliance monitoring, and PII detection.

    Provides methods for calculating compliance scores, identifying high-risk
    tables, and generating governance reports.
    """

    def __init__(
        self,
        project_id: str,
        metadata_dataset: str,
        ml_dataset: Optional[str] = None,
    ) -> None:
        """Initialize governance engine.

        Args:
            project_id: GCP project ID
            metadata_dataset: BigQuery dataset with UC metadata
            ml_dataset: BigQuery dataset with ML results (optional)
        """
        self.project_id = project_id
        self.metadata_dataset = metadata_dataset
        self.ml_dataset = ml_dataset
        self.bq_client = bigquery.Client(project=project_id)
        logger.info(f"Initialized GovernanceEngine for project {project_id}")

    def get_compliance_score(self) -> Dict[str, Any]:
        """Calculate overall compliance score.

        Returns:
            Dictionary with compliance metrics and overall score
        """
        try:
            if self.ml_dataset:
                query = f"""
                WITH metrics AS (
                    SELECT
                        (SELECT COUNT(*) FROM `{self.project_id}.{self.metadata_dataset}.tables`) as total_tables,
                        (SELECT COUNT(*) FROM `{self.project_id}.{self.ml_dataset}.pii_summary_by_table`
                         WHERE pii_columns_count > 0) as tables_with_pii,
                        (SELECT COUNT(*) FROM `{self.project_id}.{self.ml_dataset}.pii_summary_by_table`
                         WHERE risk_level = 'HIGH') as high_risk_tables,
                        (SELECT COUNT(*) FROM `{self.project_id}.{self.metadata_dataset}.tables`
                         WHERE comment IS NOT NULL) as documented_tables
                )

                SELECT
                    *,
                    ROUND(100.0 * documented_tables / NULLIF(total_tables, 0), 2) as documentation_pct,
                    ROUND(100.0 * high_risk_tables / NULLIF(tables_with_pii, 0), 2) as high_risk_pct
                FROM metrics
                """
            else:
                query = f"""
                SELECT
                    COUNT(*) as total_tables,
                    0 as tables_with_pii,
                    0 as high_risk_tables,
                    SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) as documented_tables,
                    ROUND(100.0 * SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as documentation_pct,
                    0.0 as high_risk_pct
                FROM `{self.project_id}.{self.metadata_dataset}.tables`
                """

            result = self.bq_client.query(query).to_dataframe().to_dict("records")[0]

            # Calculate overall score (0-100)
            doc_score = result["documentation_pct"] * 0.4
            risk_score = max(0, 100 - result.get("high_risk_pct", 0)) * 0.6
            overall_score = doc_score + risk_score

            result["overall_compliance_score"] = round(overall_score, 2)

            logger.info(f"Compliance score calculated: {overall_score}")
            return result

        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
            return {
                "overall_compliance_score": 0,
                "documentation_pct": 0,
                "high_risk_pct": 0,
                "total_tables": 0,
            }

    def get_high_risk_tables(self) -> List[Dict[str, Any]]:
        """Get list of high-risk tables requiring attention.

        Returns:
            List of high-risk tables
        """
        if not self.ml_dataset:
            logger.debug("ML dataset not configured - returning empty list")
            return []

        try:
            query = f"""
            SELECT
                t.table_catalog,
                t.table_schema,
                t.table_name,
                t.full_table_name,
                t.pii_columns_count,
                t.pii_columns,
                t.risk_level,
                t.avg_pii_score_pct,
                CASE WHEN tm.comment IS NULL THEN TRUE ELSE FALSE END as undocumented,
                tm._fivetran_synced as last_synced
            FROM `{self.project_id}.{self.ml_dataset}.pii_summary_by_table` t
            LEFT JOIN `{self.project_id}.{self.metadata_dataset}.tables` tm
                ON t.table_catalog = tm.catalog_name
                AND t.table_schema = tm.schema_name
                AND t.table_name = tm.table_name
            WHERE t.risk_level IN ('HIGH', 'MEDIUM')
            ORDER BY
                CASE t.risk_level WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
                t.pii_columns_count DESC
            """

            results = self.bq_client.query(query).to_dataframe()
            logger.info(f"Found {len(results)} high-risk tables")
            return results.to_dict("records")

        except Exception as e:
            logger.error(f"Error getting high-risk tables: {e}")
            return []

    def get_undocumented_tables(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Find tables without documentation.

        Args:
            limit: Maximum number of results

        Returns:
            List of undocumented tables
        """
        try:
            query = f"""
            SELECT
                catalog_name,
                schema_name,
                table_name,
                full_name,
                table_type,
                created_at as created,
                _fivetran_synced as last_synced
            FROM `{self.project_id}.{self.metadata_dataset}.tables`
            WHERE comment IS NULL OR comment = ''
            ORDER BY created_at DESC
            LIMIT {limit}
            """

            results = self.bq_client.query(query).to_dataframe()
            logger.info(f"Found {len(results)} undocumented tables")
            return results.to_dict("records")

        except Exception as e:
            logger.error(f"Error getting undocumented tables: {e}")
            return []

    def get_documentation_rate_by_schema(self) -> List[Dict[str, Any]]:
        """Get documentation rate statistics by schema.

        Returns:
            List of schemas with documentation metrics
        """
        try:
            query = f"""
            SELECT
                schema_name,
                COUNT(*) as total_tables,
                SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) as documented_tables,
                ROUND(100.0 * SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as documentation_pct
            FROM `{self.project_id}.{self.metadata_dataset}.tables`
            GROUP BY schema_name
            ORDER BY documentation_pct DESC
            """

            results = self.bq_client.query(query).to_dataframe()
            logger.info(f"Retrieved documentation rates for {len(results)} schemas")
            return results.to_dict("records")

        except Exception as e:
            logger.error(f"Error getting documentation rates: {e}")
            return []

    def validate_table_exists(self, full_table_name: str) -> bool:
        """Check if table exists in catalog.

        Args:
            full_table_name: Fully qualified table name

        Returns:
            True if table exists, False otherwise
        """
        parts = full_table_name.split(".")
        if len(parts) != 3:
            return False

        catalog, schema, table = parts

        try:
            query = f"""
            SELECT COUNT(*) as cnt
            FROM `{self.project_id}.{self.metadata_dataset}.tables`
            WHERE catalog_name = '{catalog}'
              AND schema_name = '{schema}'
              AND table_name = '{table}'
            """

            result = self.bq_client.query(query).to_dataframe()
            exists = result["cnt"].iloc[0] > 0
            logger.debug(f"Table {full_table_name} exists: {exists}")
            return exists

        except Exception as e:
            logger.error(f"Error validating table existence: {e}")
            return False
