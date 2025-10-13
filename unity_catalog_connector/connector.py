# Unity Catalog to BigQuery Connector for Fivetran SDK
# This connector extracts metadata and data from Databricks Unity Catalog
# and loads it into BigQuery for AI-powered analytics
# See the Technical Reference documentation (https://fivetran.com/docs/connectors/connector-sdk/technical-reference#update)
# and the Best Practices documentation (https://fivetran.com/docs/connectors/connector-sdk/best-practices) for details

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Import required classes from fivetran_connector_sdk
from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Logging as log
from fivetran_connector_sdk import Operations as op

# Constants
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
API_VERSION = "2.1"


class UnityCatalogClient:
    """
    Client for interacting with Databricks Unity Catalog REST API
    """

    def __init__(self, workspace_url: str, access_token: str):
        """
        Initialize Unity Catalog client
        Args:
            workspace_url: Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)
            access_token: Personal access token for authentication
        """
        self.workspace_url = workspace_url.rstrip("/")
        self.access_token = access_token
        self.base_url = f"{self.workspace_url}/api/{API_VERSION}/unity-catalog"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self, endpoint: str, method: str = "GET", params: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request to Unity Catalog API
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method=method, url=url, headers=self.headers, params=params, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.warning(f"API request failed for {endpoint}: {str(e)}")
            raise

    def list_catalogs(self) -> List[Dict]:
        """List all catalogs in Unity Catalog"""
        log.info("Fetching catalogs from Unity Catalog")
        response = self._make_request("catalogs")
        return response.get("catalogs", [])

    def list_schemas(self, catalog_name: str) -> List[Dict]:
        """List all schemas in a catalog"""
        log.fine(f"Fetching schemas for catalog: {catalog_name}")
        response = self._make_request("schemas", params={"catalog_name": catalog_name})
        return response.get("schemas", [])

    def list_tables(self, catalog_name: str, schema_name: str) -> List[Dict]:
        """List all tables in a schema"""
        log.fine(f"Fetching tables for {catalog_name}.{schema_name}")
        response = self._make_request(
            "tables", params={"catalog_name": catalog_name, "schema_name": schema_name}
        )
        return response.get("tables", [])

    def get_table_metadata(self, full_table_name: str) -> Dict:
        """Get detailed metadata for a specific table"""
        log.fine(f"Fetching metadata for table: {full_table_name}")
        return self._make_request(f"tables/{full_table_name}")

    def list_volumes(self, catalog_name: str, schema_name: str) -> List[Dict]:
        """List all volumes in a schema"""
        log.fine(f"Fetching volumes for {catalog_name}.{schema_name}")
        try:
            response = self._make_request(
                "volumes", params={"catalog_name": catalog_name, "schema_name": schema_name}
            )
            return response.get("volumes", [])
        except Exception:
            # Volumes might not be available in all Unity Catalog installations
            return []


def dt2str(incoming: datetime) -> str:
    """Convert datetime to ISO format string"""
    if isinstance(incoming, str):
        return incoming
    return incoming.strftime(TIMESTAMP_FORMAT)


def schema(configuration: dict):
    """
    Define the schema function which lets you configure the schema your connector delivers.
    See the technical reference documentation for more details on the schema function:
    https://fivetran.com/docs/connectors/connector-sdk/technical-reference#schema
    Args:
        configuration: a dictionary that holds the configuration settings for the connector.
    """
    return [
        {
            "table": "catalogs",
            "primary_key": ["catalog_name"],
            "columns": {
                "catalog_name": "STRING",
                "catalog_type": "STRING",
                "comment": "STRING",
                "owner": "STRING",
                "created_at": "UTC_DATETIME",
                "created_by": "STRING",
                "updated_at": "UTC_DATETIME",
                "updated_by": "STRING",
                "metastore_id": "STRING",
            },
        },
        {
            "table": "schemas",
            "primary_key": ["full_name"],
            "columns": {
                "full_name": "STRING",
                "catalog_name": "STRING",
                "schema_name": "STRING",
                "comment": "STRING",
                "owner": "STRING",
                "created_at": "UTC_DATETIME",
                "created_by": "STRING",
                "updated_at": "UTC_DATETIME",
                "updated_by": "STRING",
            },
        },
        {
            "table": "tables",
            "primary_key": ["full_name"],
            "columns": {
                "full_name": "STRING",
                "catalog_name": "STRING",
                "schema_name": "STRING",
                "table_name": "STRING",
                "table_type": "STRING",
                "data_source_format": "STRING",
                "storage_location": "STRING",
                "comment": "STRING",
                "owner": "STRING",
                "created_at": "UTC_DATETIME",
                "created_by": "STRING",
                "updated_at": "UTC_DATETIME",
                "updated_by": "STRING",
            },
        },
        {
            "table": "columns",
            "primary_key": ["table_full_name", "column_name"],
            "columns": {
                "table_full_name": "STRING",
                "column_name": "STRING",
                "position": "INT",
                "data_type": "STRING",
                "nullable": "BOOLEAN",
                "comment": "STRING",
                "partition_index": "INT",
            },
        },
        {
            "table": "volumes",
            "primary_key": ["full_name"],
            "columns": {
                "full_name": "STRING",
                "catalog_name": "STRING",
                "schema_name": "STRING",
                "volume_name": "STRING",
                "volume_type": "STRING",
                "storage_location": "STRING",
                "comment": "STRING",
                "owner": "STRING",
                "created_at": "UTC_DATETIME",
                "created_by": "STRING",
                "updated_at": "UTC_DATETIME",
                "updated_by": "STRING",
            },
        },
    ]


def update(configuration: dict, state: dict):
    """
    Define the update function, which is a required function, and is called by Fivetran during each sync.
    See the technical reference documentation for more details on the update function
    https://fivetran.com/docs/connectors/connector-sdk/technical-reference#update
    Args:
        configuration: A dictionary containing connection details
        state: A dictionary containing state information from previous runs
        The state dictionary is empty for the first sync or for any full re-sync
    """
    log.warning("Unity Catalog to BigQuery Connector - Starting sync")

    # Validate required configuration
    required_fields = ["workspace_url", "access_token"]
    for field in required_fields:
        if field not in configuration:
            raise ValueError(f"Missing required configuration field: {field}")

    # Initialize Unity Catalog client
    client = UnityCatalogClient(
        workspace_url=configuration["workspace_url"],
        access_token=configuration["access_token"],
    )

    # Get optional catalog filter from configuration
    catalog_filter = (
        configuration.get("catalog_filter", "").split(",")
        if configuration.get("catalog_filter")
        else None
    )

    # Track last update time for incremental sync
    last_sync_time = state.get("last_sync_time", "1990-01-01T00:00:00Z")
    current_sync_time = datetime.utcnow()

    log.info(f"Last sync time: {last_sync_time}")

    # Fetch and sync catalogs
    catalogs = client.list_catalogs()
    catalog_count = 0

    for catalog in catalogs:
        catalog_name = catalog.get("name")

        # Apply catalog filter if specified
        if catalog_filter and catalog_name not in catalog_filter:
            log.fine(f"Skipping catalog {catalog_name} (not in filter)")
            continue

        catalog_count += 1

        # Sync catalog metadata
        op.upsert(
            table="catalogs",
            data={
                "catalog_name": catalog_name,
                "catalog_type": catalog.get("catalog_type", "MANAGED_CATALOG"),
                "comment": catalog.get("comment"),
                "owner": catalog.get("owner"),
                "created_at": dt2str(datetime.fromtimestamp(catalog.get("created_at", 0) / 1000)),
                "created_by": catalog.get("created_by"),
                "updated_at": dt2str(datetime.fromtimestamp(catalog.get("updated_at", 0) / 1000)),
                "updated_by": catalog.get("updated_by"),
                "metastore_id": catalog.get("metastore_id"),
            },
        )

        # Fetch schemas for this catalog
        schemas = client.list_schemas(catalog_name)

        for schema in schemas:
            schema_name = schema.get("name")
            full_schema_name = f"{catalog_name}.{schema_name}"

            # Sync schema metadata
            op.upsert(
                table="schemas",
                data={
                    "full_name": full_schema_name,
                    "catalog_name": catalog_name,
                    "schema_name": schema_name,
                    "comment": schema.get("comment"),
                    "owner": schema.get("owner"),
                    "created_at": dt2str(
                        datetime.fromtimestamp(schema.get("created_at", 0) / 1000)
                    ),
                    "created_by": schema.get("created_by"),
                    "updated_at": dt2str(
                        datetime.fromtimestamp(schema.get("updated_at", 0) / 1000)
                    ),
                    "updated_by": schema.get("updated_by"),
                },
            )

            # Fetch tables for this schema
            tables = client.list_tables(catalog_name, schema_name)

            for table in tables:
                table_name = table.get("name")
                full_table_name = f"{catalog_name}.{schema_name}.{table_name}"

                # Get detailed table metadata
                try:
                    table_details = client.get_table_metadata(full_table_name)

                    # Sync table metadata
                    op.upsert(
                        table="tables",
                        data={
                            "full_name": full_table_name,
                            "catalog_name": catalog_name,
                            "schema_name": schema_name,
                            "table_name": table_name,
                            "table_type": table_details.get("table_type"),
                            "data_source_format": table_details.get("data_source_format"),
                            "storage_location": table_details.get("storage_location"),
                            "comment": table_details.get("comment"),
                            "owner": table_details.get("owner"),
                            "created_at": dt2str(
                                datetime.fromtimestamp(table_details.get("created_at", 0) / 1000)
                            ),
                            "created_by": table_details.get("created_by"),
                            "updated_at": dt2str(
                                datetime.fromtimestamp(table_details.get("updated_at", 0) / 1000)
                            ),
                            "updated_by": table_details.get("updated_by"),
                        },
                    )

                    # Sync column metadata
                    columns = table_details.get("columns", [])
                    for idx, column in enumerate(columns):
                        op.upsert(
                            table="columns",
                            data={
                                "table_full_name": full_table_name,
                                "column_name": column.get("name"),
                                "position": column.get("position", idx),
                                "data_type": column.get("type_text", column.get("type_name")),
                                "nullable": column.get("nullable", True),
                                "comment": column.get("comment"),
                                "partition_index": column.get("partition_index"),
                            },
                        )

                except Exception as e:
                    log.warning(f"Failed to fetch details for table {full_table_name}: {str(e)}")

            # Fetch volumes for this schema
            volumes = client.list_volumes(catalog_name, schema_name)
            for volume in volumes:
                volume_name = volume.get("name")
                full_volume_name = f"{catalog_name}.{schema_name}.{volume_name}"

                op.upsert(
                    table="volumes",
                    data={
                        "full_name": full_volume_name,
                        "catalog_name": catalog_name,
                        "schema_name": schema_name,
                        "volume_name": volume_name,
                        "volume_type": volume.get("volume_type"),
                        "storage_location": volume.get("storage_location"),
                        "comment": volume.get("comment"),
                        "owner": volume.get("owner"),
                        "created_at": dt2str(
                            datetime.fromtimestamp(volume.get("created_at", 0) / 1000)
                        ),
                        "created_by": volume.get("created_by"),
                        "updated_at": dt2str(
                            datetime.fromtimestamp(volume.get("updated_at", 0) / 1000)
                        ),
                        "updated_by": volume.get("updated_by"),
                    },
                )

        # Checkpoint after each catalog
        state["last_sync_time"] = dt2str(current_sync_time)
        state["catalogs_synced"] = catalog_count
        op.checkpoint(state)

    log.info(f"Sync completed. Processed {catalog_count} catalogs")


# Create the connector object
connector = Connector(update=update, schema=schema)

# Check if the script is being run as the main module.
if __name__ == "__main__":
    # Open the configuration.json file and load its contents into a dictionary.
    with open("configuration.json", "r") as f:
        configuration = json.load(f)
    # Test the connector locally
    connector.debug(configuration=configuration)
