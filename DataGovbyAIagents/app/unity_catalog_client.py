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

"""Unity Catalog client for metadata querying."""

import logging
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

logger = logging.getLogger(__name__)


class UnityCatalogClient:
    """Client for querying Unity Catalog metadata from BigQuery.

    This client provides methods to query Unity Catalog metadata
    that has been synced to BigQuery via Fivetran.
    """

    def __init__(
        self,
        project_id: str,
        metadata_dataset: str,
        ml_dataset: Optional[str] = None,
    ) -> None:
        """Initialize Unity Catalog client.

        Args:
            project_id: GCP project ID
            metadata_dataset: BigQuery dataset containing UC metadata
            ml_dataset: BigQuery dataset containing ML results (optional)
        """
        self.project_id = project_id
        self.metadata_dataset = metadata_dataset
        self.ml_dataset = ml_dataset
        self.bq_client = bigquery.Client(project=project_id)
        logger.info(
            f"Initialized UnityCatalogClient for project {project_id}, "
            f"metadata_dataset {metadata_dataset}"
        )

    def search_tables_by_keyword(
        self, keyword: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for tables matching a keyword.

        Args:
            keyword: Search keyword
            limit: Maximum number of results

        Returns:
            List of matching tables
        """
        query = f"""
        SELECT
            catalog_name,
            schema_name,
            table_name,
            full_name,
            table_type,
            comment,
            _fivetran_synced as last_synced
        FROM `{self.project_id}.{self.metadata_dataset}.tables`
        WHERE LOWER(table_name) LIKE '%{keyword.lower()}%'
           OR LOWER(COALESCE(comment, '')) LIKE '%{keyword.lower()}%'
        LIMIT {limit}
        """

        try:
            results = self.bq_client.query(query).to_dataframe()
            logger.info(f"Found {len(results)} tables matching '{keyword}'")
            return results.to_dict("records")
        except Exception as e:
            logger.error(f"Error searching tables: {e}")
            return []

    def search_tables_by_schema(self, schema_name: str) -> List[Dict[str, Any]]:
        """Get all tables in a specific schema.

        Args:
            schema_name: Schema name to search

        Returns:
            List of tables in schema
        """
        query = f"""
        SELECT
            catalog_name,
            schema_name,
            table_name,
            full_name,
            table_type,
            comment
        FROM `{self.project_id}.{self.metadata_dataset}.tables`
        WHERE schema_name = '{schema_name}'
        ORDER BY table_name
        """

        try:
            results = self.bq_client.query(query).to_dataframe()
            logger.info(f"Found {len(results)} tables in schema '{schema_name}'")
            return results.to_dict("records")
        except Exception as e:
            logger.error(f"Error searching schema: {e}")
            return []

    def get_table_details(self, full_table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table.

        Args:
            full_table_name: Fully qualified table name (catalog.schema.table)

        Returns:
            Dictionary with table details including columns and PII info
        """
        # Parse table name
        parts = full_table_name.split(".")
        if len(parts) != 3:
            return {"error": "Invalid table name format. Use: catalog.schema.table"}

        catalog, schema, table = parts

        try:
            # Get table metadata
            table_query = f"""
            SELECT
                catalog_name,
                schema_name,
                table_name,
                table_type,
                comment,
                created_at as created,
                _fivetran_synced as last_synced
            FROM `{self.project_id}.{self.metadata_dataset}.tables`
            WHERE catalog_name = '{catalog}'
              AND schema_name = '{schema}'
              AND table_name = '{table}'
            """

            table_info = self.bq_client.query(table_query).to_dataframe()
            if table_info.empty:
                return {"error": f"Table {full_table_name} not found"}

            # Get columns
            columns_query = f"""
            SELECT
                column_name,
                data_type,
                nullable as is_nullable,
                position as ordinal_position,
                comment
            FROM `{self.project_id}.{self.metadata_dataset}.columns`
            WHERE table_full_name = '{full_table_name}'
            ORDER BY position
            """

            columns = self.bq_client.query(columns_query).to_dataframe()

            result = {
                "table": table_info.to_dict("records")[0],
                "columns": columns.to_dict("records"),
                "column_count": len(columns),
            }

            # Get PII status if ML dataset available
            if self.ml_dataset:
                pii_query = f"""
                SELECT
                    pii_columns_count,
                    pii_columns,
                    risk_level,
                    avg_pii_score_pct
                FROM `{self.project_id}.{self.ml_dataset}.pii_summary_by_table`
                WHERE table_catalog = '{catalog}'
                  AND table_schema = '{schema}'
                  AND table_name = '{table}'
                """

                try:
                    pii_info = self.bq_client.query(pii_query).to_dataframe()
                    if not pii_info.empty:
                        result["pii_info"] = pii_info.to_dict("records")[0]
                except Exception as e:
                    logger.debug(f"Could not fetch PII info: {e}")

            logger.info(f"Retrieved details for table {full_table_name}")
            return result

        except Exception as e:
            logger.error(f"Error getting table details: {e}")
            return {"error": str(e)}

    def get_pii_status(
        self, schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get PII status across tables.

        Args:
            schema_name: Optional schema filter

        Returns:
            List of tables with PII information
        """
        if not self.ml_dataset:
            logger.warning("ML dataset not configured - cannot retrieve PII status")
            return []

        try:
            where_clause = (
                f"WHERE table_schema = '{schema_name}'" if schema_name else ""
            )

            query = f"""
            SELECT
                full_table_name,
                pii_columns_count,
                pii_columns,
                risk_level,
                avg_pii_score_pct
            FROM `{self.project_id}.{self.ml_dataset}.pii_summary_by_table`
            {where_clause}
            ORDER BY pii_columns_count DESC
            LIMIT 20
            """

            results = self.bq_client.query(query).to_dataframe()
            logger.info(f"Found {len(results)} tables with PII information")
            return results.to_dict("records")
        except Exception as e:
            logger.error(f"Error getting PII status: {e}")
            return []

    def get_metadata_freshness(self) -> Dict[str, Any]:
        """Check freshness of synced metadata.

        Returns:
            Dictionary with freshness information
        """
        try:
            query = f"""
            SELECT
                MIN(_fivetran_synced) as oldest_sync,
                MAX(_fivetran_synced) as latest_sync,
                TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_fivetran_synced), MINUTE) as minutes_since_sync,
                COUNT(DISTINCT catalog_name) as catalogs_synced,
                COUNT(*) as tables_synced
            FROM `{self.project_id}.{self.metadata_dataset}.tables`
            """

            result = self.bq_client.query(query).to_dataframe().to_dict("records")[0]

            # Add freshness status
            minutes = result["minutes_since_sync"]
            if minutes < 20:
                result["freshness_status"] = "FRESH"
            elif minutes < 60:
                result["freshness_status"] = "ACCEPTABLE"
            else:
                result["freshness_status"] = "STALE"

            logger.info(f"Metadata freshness: {result['freshness_status']}")
            return result

        except Exception as e:
            logger.error(f"Error checking metadata freshness: {e}")
            return {"freshness_status": "UNKNOWN", "minutes_since_sync": -1}
