# Unity Catalog to BigQuery Connector

[![Fivetran SDK](https://img.shields.io/badge/Fivetran-Connector%20SDK-00A4E4?style=flat-square)](https://fivetran.com/docs/connectors/connector-sdk)
[![Databricks](https://img.shields.io/badge/Databricks-Unity%20Catalog-FF3621?style=flat-square)](https://www.databricks.com/product/unity-catalog)
[![BigQuery](https://img.shields.io/badge/Google-BigQuery-4285F4?style=flat-square)](https://cloud.google.com/bigquery)

> **Extract metadata from Databricks Unity Catalog and load it into Google BigQuery for AI-powered data governance and analytics**

## 🎯 Overview

This Fivetran connector extracts comprehensive metadata from Databricks Unity Catalog and syncs it to Google BigQuery, enabling:

- **📊 Data Catalog Intelligence**: Centralized metadata repository in BigQuery
- **🔍 AI-Powered Discovery**: Use BigQuery AI to query and understand your data landscape
- **📈 Governance Analytics**: Track data lineage, ownership, and usage patterns
- **🤖 Automated Documentation**: Generate data dictionaries with ML.GENERATE_TEXT
- **🔐 Compliance Monitoring**: Audit data access and security configurations

## ✨ Features

### Metadata Extraction

- ✅ **Catalogs**: All catalog metadata including ownership and timestamps
- ✅ **Schemas**: Schema-level metadata and organization
- ✅ **Tables**: Complete table metadata with storage locations
- ✅ **Columns**: Detailed column definitions, types, and constraints
- ✅ **Volumes**: Unity Catalog volumes for unstructured data
- ✅ **Incremental Sync**: Efficient updates with state management
- ✅ **Catalog Filtering**: Sync specific catalogs only

### Integration Benefits

When combined with the BigQuery AI architect project in this repository:

- 🧠 **AI-Powered Metadata Analysis**: Use Gemini models to understand data relationships
- 📝 **Auto-Generated Documentation**: Create comprehensive data catalogs automatically
- 🔮 **Predictive Analytics**: Forecast data growth and usage patterns
- ⚡ **Smart Search**: Natural language queries over your data catalog

## 🏗️ Architecture

```
Databricks Unity Catalog (Source)
         ↓
    REST API v2.1
         ↓
  Fivetran Connector SDK
         ↓
    BigQuery (Destination)
         ↓
  BigQuery AI/ML Functions
         ↓
  Analytics & Insights
```

## 📋 Prerequisites

### Databricks Setup

1. **Unity Catalog Enabled**: Your Databricks workspace must have Unity Catalog enabled
2. **Access Token**: Generate a personal access token with appropriate permissions
   - Navigate to: User Settings → Access Tokens → Generate New Token
   - Required permissions: Read access to Unity Catalog metadata
3. **Workspace URL**: Your Databricks workspace URL (e.g., `https://your-workspace.cloud.databricks.com`)

### Google Cloud Setup

1. **BigQuery Dataset**: Create a target dataset in BigQuery
2. **Fivetran Account**: Active Fivetran account with connector SDK support
3. **Service Account**: GCP service account with BigQuery Data Editor permissions

## 🚀 Quick Start

### 1. Configure the Connector

Edit `configuration.json`:

```json
{
  "workspace_url": "https://your-workspace.cloud.databricks.com",
  "access_token": "dapi1234567890abcdef",
  "catalog_filter": "main,analytics"
}
```

**Configuration Options:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `workspace_url` | Yes | Your Databricks workspace URL |
| `access_token` | Yes | Databricks personal access token |
| `catalog_filter` | No | Comma-separated list of catalogs to sync (empty = all) |

### 2. Install Dependencies

```bash
cd connectors/unity_catalog
pip install -r requirements.txt
```

### 3. Test Locally

```bash
python connector.py
```

This will:
- Validate your configuration
- Connect to Unity Catalog
- Extract metadata
- Display results in the console

### 4. Deploy to Fivetran

```bash
# Package the connector
zip -r unity_catalog_connector.zip connector.py configuration.json requirements.txt

# Upload to Fivetran (via UI or API)
# Follow Fivetran's connector SDK deployment guide
```

## 📊 Data Schema

### Catalogs Table

Stores top-level catalog metadata.

| Column | Type | Description |
|--------|------|-------------|
| `catalog_name` | STRING | Catalog name (Primary Key) |
| `catalog_type` | STRING | Type (MANAGED_CATALOG, etc.) |
| `comment` | STRING | Catalog description |
| `owner` | STRING | Catalog owner |
| `created_at` | UTC_DATETIME | Creation timestamp |
| `created_by` | STRING | Creator user |
| `updated_at` | UTC_DATETIME | Last update timestamp |
| `updated_by` | STRING | Last updater user |
| `metastore_id` | STRING | Associated metastore ID |

### Schemas Table

Stores schema-level metadata.

| Column | Type | Description |
|--------|------|-------------|
| `full_name` | STRING | Full schema name (Primary Key) |
| `catalog_name` | STRING | Parent catalog |
| `schema_name` | STRING | Schema name |
| `comment` | STRING | Schema description |
| `owner` | STRING | Schema owner |
| `created_at` | UTC_DATETIME | Creation timestamp |
| `created_by` | STRING | Creator user |
| `updated_at` | UTC_DATETIME | Last update timestamp |
| `updated_by` | STRING | Last updater user |

### Tables Table

Stores table metadata.

| Column | Type | Description |
|--------|------|-------------|
| `full_name` | STRING | Full table name (Primary Key) |
| `catalog_name` | STRING | Parent catalog |
| `schema_name` | STRING | Parent schema |
| `table_name` | STRING | Table name |
| `table_type` | STRING | MANAGED, EXTERNAL, VIEW, etc. |
| `data_source_format` | STRING | DELTA, PARQUET, CSV, etc. |
| `storage_location` | STRING | Storage path |
| `comment` | STRING | Table description |
| `owner` | STRING | Table owner |
| `created_at` | UTC_DATETIME | Creation timestamp |
| `created_by` | STRING | Creator user |
| `updated_at` | UTC_DATETIME | Last update timestamp |
| `updated_by` | STRING | Last updater user |

### Columns Table

Stores column-level metadata.

| Column | Type | Description |
|--------|------|-------------|
| `table_full_name` | STRING | Parent table (Composite PK) |
| `column_name` | STRING | Column name (Composite PK) |
| `position` | INT | Column position in table |
| `data_type` | STRING | Column data type |
| `nullable` | BOOLEAN | Nullability flag |
| `comment` | STRING | Column description |
| `partition_index` | INT | Partition column index |

### Volumes Table

Stores Unity Catalog volume metadata.

| Column | Type | Description |
|--------|------|-------------|
| `full_name` | STRING | Full volume name (Primary Key) |
| `catalog_name` | STRING | Parent catalog |
| `schema_name` | STRING | Parent schema |
| `volume_name` | STRING | Volume name |
| `volume_type` | STRING | MANAGED, EXTERNAL |
| `storage_location` | STRING | Storage path |
| `comment` | STRING | Volume description |
| `owner` | STRING | Volume owner |
| `created_at` | UTC_DATETIME | Creation timestamp |
| `created_by` | STRING | Creator user |
| `updated_at` | UTC_DATETIME | Last update timestamp |
| `updated_by` | STRING | Last updater user |

## 🤖 BigQuery AI Integration

Once your Unity Catalog metadata is in BigQuery, leverage AI capabilities:

### 1. Auto-Generate Data Dictionary

```sql
-- Use ML.GENERATE_TEXT to create table documentation
SELECT
  full_name,
  ML.GENERATE_TEXT(
    MODEL `project.dataset.text_bison_model`,
    CONCAT(
      'Generate a business description for this table: ',
      full_name,
      '. Type: ', table_type,
      '. Columns: ',
      (SELECT STRING_AGG(column_name, ', ')
       FROM `project.dataset.columns` c
       WHERE c.table_full_name = t.full_name)
    ),
    STRUCT(0.2 AS temperature, 512 AS max_output_tokens)
  ) AS generated_description
FROM `project.dataset.tables` t
WHERE comment IS NULL OR comment = '';
```

### 2. Smart Metadata Search

```sql
-- Find all PII-related tables using AI classification
SELECT
  full_name,
  AI.GENERATE_BOOL(
    MODEL `project.dataset.text_bison_model`,
    CONCAT(
      'Does this table likely contain PII? Table: ', full_name,
      '. Columns: ',
      (SELECT STRING_AGG(column_name, ', ')
       FROM `project.dataset.columns` c
       WHERE c.table_full_name = t.full_name)
    )
  ) AS contains_pii
FROM `project.dataset.tables` t
WHERE AI.GENERATE_BOOL(...) = TRUE;
```

### 3. Predict Data Growth

```sql
-- Forecast table growth patterns
CREATE OR REPLACE MODEL `project.dataset.table_growth_forecast`
OPTIONS(model_type='ARIMA_PLUS', time_series_timestamp_col='sync_date') AS
SELECT
  DATE(updated_at) as sync_date,
  COUNT(*) as table_count,
  catalog_name
FROM `project.dataset.tables`
GROUP BY sync_date, catalog_name;

-- Get 30-day forecast
SELECT * FROM ML.FORECAST(
  MODEL `project.dataset.table_growth_forecast`,
  STRUCT(30 AS horizon)
);
```

### 4. Generate Lineage Insights

```sql
-- Use AI to suggest data lineage relationships
SELECT * FROM ML.GENERATE_TABLE(
  MODEL `project.dataset.text_bison_model`,
  CONCAT(
    'Generate a data lineage analysis table for: ',
    (SELECT STRING_AGG(full_name, ', ' LIMIT 10) FROM `project.dataset.tables`)
  ),
  STRUCT('lineage_analysis' AS table_name)
);
```

## 🔧 Advanced Configuration

### Catalog Filtering

Sync only specific catalogs:

```json
{
  "catalog_filter": "production,analytics,ml_models"
}
```

Leave empty to sync all catalogs:

```json
{
  "catalog_filter": ""
}
```

### State Management

The connector tracks sync state to enable incremental updates:

```python
# State structure
{
  "last_sync_time": "2025-10-10T12:00:00Z",
  "catalogs_synced": 5
}
```

### Error Handling

The connector includes robust error handling:

- API request retries with exponential backoff
- Graceful handling of missing volumes (not all UC installations support them)
- Detailed logging for debugging
- Checkpoint after each catalog for resume capability

## 📈 Use Cases

### Data Governance

1. **Catalog Inventory**: Track all data assets across Unity Catalog
2. **Ownership Tracking**: Identify data owners and stewards
3. **Compliance Auditing**: Monitor data classification and access

### Analytics

1. **Usage Analysis**: Analyze table creation and update patterns
2. **Schema Evolution**: Track schema changes over time
3. **Storage Optimization**: Identify large or unused tables

### AI-Powered Insights

1. **Smart Search**: Natural language search across your data catalog
2. **Auto-Documentation**: Generate descriptions for undocumented tables
3. **Anomaly Detection**: Identify unusual metadata patterns

## 🔍 Troubleshooting

### Connection Issues

**Problem**: `Failed to connect to Unity Catalog API`

**Solution**:
- Verify workspace URL format (include `https://`)
- Check access token validity
- Ensure network connectivity to Databricks

### Authentication Errors

**Problem**: `401 Unauthorized`

**Solution**:
- Regenerate access token
- Verify token has Unity Catalog read permissions
- Check token expiration date

### Missing Data

**Problem**: Some tables/schemas not syncing

**Solution**:
- Check catalog_filter configuration
- Verify Unity Catalog permissions
- Review Fivetran logs for errors

### Performance Optimization

For large catalogs (1000+ tables):

1. Use catalog filtering to sync incrementally
2. Increase checkpoint frequency
3. Run during off-peak hours
4. Consider parallel sync jobs for multiple catalogs

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- [ ] Support for Unity Catalog functions and procedures
- [ ] Data lineage extraction
- [ ] Table statistics and metrics
- [ ] User and group permissions
- [ ] Delta Lake version history
- [ ] Notebook metadata integration

## 📄 License

This connector is open source under the MIT License. See LICENSE file for details.

## 🔗 Related Projects

- [BigQuery AI Architect](../../bigquery_ai_architect/README.md) - AI-powered analytics on this data
- [Fivetran Connector SDK Docs](https://fivetran.com/docs/connectors/connector-sdk)
- [Unity Catalog API Docs](https://docs.databricks.com/api/workspace/catalogs)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/fivetran_connector_sdk/issues)
- **Documentation**: [Fivetran SDK Docs](https://fivetran.com/docs/connectors/connector-sdk)
- **Community**: [Fivetran Community](https://community.fivetran.com)

## 🏆 Fivetran Challenge Submission

This connector demonstrates:

✅ **Custom Data Source**: Unity Catalog metadata extraction
✅ **BigQuery Integration**: Direct loading to BigQuery warehouse
✅ **AI Application**: Powers the BigQuery AI Architect project
✅ **Production Ready**: Comprehensive error handling and testing
✅ **Open Source**: MIT licensed with full documentation

---

**Built with ❤️ for the Fivetran + Google Cloud Challenge**

_Transform your Unity Catalog metadata into actionable insights with BigQuery AI_
