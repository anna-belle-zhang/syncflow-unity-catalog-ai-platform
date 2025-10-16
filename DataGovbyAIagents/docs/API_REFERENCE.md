# SyncFlow API Reference

## Base URL
```
http://localhost:8080
```

## Authentication
All requests use Google Cloud authentication via service account credentials.

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "SyncFlow Data Governance API",
  "version": "0.1.0"
}
```

---

### Data Discovery

#### POST /discover
Search for tables using natural language query.

**Request:**
```json
{
  "query": "Find tables related to customers"
}
```

**Response:**
```json
{
  "query": "Find tables related to customers",
  "keyword": "customers",
  "results": [
    {
      "catalog_name": "default",
      "schema_name": "gold",
      "table_name": "dim_customer",
      "full_name": "default.gold.dim_customer",
      "table_type": "TABLE",
      "comment": "Customer dimension table"
    }
  ],
  "count": 1
}
```

---

### Compliance

#### GET /compliance
Get compliance metrics and high-risk tables.

**Response:**
```json
{
  "compliance_score": {
    "total_tables": 150,
    "tables_with_pii": 45,
    "high_risk_tables": 8,
    "documented_tables": 120,
    "documentation_pct": 80.0,
    "overall_compliance_score": 85.5
  },
  "high_risk_tables": [
    {
      "table_catalog": "default",
      "table_schema": "raw",
      "table_name": "customer_pii",
      "risk_level": "HIGH",
      "pii_columns_count": 5,
      "pii_columns": "email, phone, ssn, address, dob"
    }
  ],
  "undocumented_tables": [
    {
      "catalog_name": "default",
      "schema_name": "staging",
      "table_name": "temp_orders",
      "full_name": "default.staging.temp_orders"
    }
  ],
  "metadata_freshness": {
    "freshness_status": "FRESH",
    "minutes_since_sync": 5
  },
  "summary": {
    "overall_score": 85.5,
    "high_risk_count": 8,
    "undocumented_count": 30
  }
}
```

---

### Table Details

#### GET /table-details/{table_name}
Get detailed information about a specific table.

**Parameters:**
- `table_name` (path): Fully qualified table name (e.g., `default.gold.dim_customer`)

**Response:**
```json
{
  "table": {
    "catalog_name": "default",
    "schema_name": "gold",
    "table_name": "dim_customer",
    "table_type": "TABLE",
    "comment": "Customer dimension table",
    "created": "2024-01-15",
    "last_synced": "2024-10-17T10:30:00Z"
  },
  "columns": [
    {
      "column_name": "customer_id",
      "data_type": "INT64",
      "is_nullable": false,
      "ordinal_position": 1,
      "comment": "Unique customer identifier"
    },
    {
      "column_name": "email",
      "data_type": "STRING",
      "is_nullable": false,
      "ordinal_position": 2
    }
  ],
  "column_count": 15,
  "pii_info": {
    "pii_columns_count": 2,
    "pii_columns": "email, phone",
    "risk_level": "MEDIUM",
    "avg_pii_score_pct": 85.5
  }
}
```

---

### Generate Description

#### POST /generate-description
Generate AI-powered description for a table.

**Request:**
```json
{
  "table_name": "default.gold.dim_customer"
}
```

**Response:**
```json
{
  "table_name": "default.gold.dim_customer",
  "description": "This table contains customer master data including demographics, contact information, and behavioral metrics. It serves as the primary dimension for customer analytics and reporting, updated daily via incremental loads from the customer systems."
}
```

---

### PII Analysis

#### GET /pii-analysis
Analyze PII risk across the catalog.

**Response:**
```json
{
  "total_tables_with_pii": 45,
  "high_risk_count": 8,
  "medium_risk_count": 15,
  "high_risk_tables": [
    {
      "full_table_name": "default.raw.customer_pii",
      "risk_level": "HIGH",
      "pii_columns_count": 8,
      "avg_pii_score_pct": 92.5
    }
  ],
  "medium_risk_tables": [
    {
      "full_table_name": "default.staging.orders",
      "risk_level": "MEDIUM",
      "pii_columns_count": 3,
      "avg_pii_score_pct": 75.0
    }
  ]
}
```

---

### Metadata Health

#### GET /metadata-health
Check freshness and health of catalog metadata.

**Response:**
```json
{
  "oldest_sync": "2024-10-16T08:00:00Z",
  "latest_sync": "2024-10-17T10:30:00Z",
  "minutes_since_sync": 5,
  "catalogs_synced": 3,
  "tables_synced": 250,
  "freshness_status": "FRESH"
}
```

Freshness statuses:
- `FRESH`: < 20 minutes
- `ACCEPTABLE`: 20-60 minutes
- `STALE`: > 60 minutes

---

### AI Query

#### POST /query
Ask the AI agent questions about your data.

**Request:**
```json
{
  "question": "What are the most frequently used tables?"
}
```

**Response:**
```json
{
  "question": "What are the most frequently used tables?",
  "answer": "Based on the catalog analysis, the most frequently used tables are... [AI-generated response]"
}
```

---

### Feedback

#### POST /feedback
Submit feedback about the system.

**Request:**
```json
{
  "feedback_type": "bug",
  "feedback_text": "Discovery search not working correctly",
  "metadata": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

---

## Error Responses

### 400 Bad Request
Missing or invalid parameters.

```json
{
  "detail": "Query parameter required"
}
```

### 404 Not Found
Resource not found.

```json
{
  "detail": "Table default.gold.nonexistent not found"
}
```

### 500 Internal Server Error
Server error.

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting
No rate limiting currently implemented. Will be added based on usage patterns.

---

## Pagination
Currently, all results are returned. Pagination will be added in future versions.

---

## Examples

### Python
```python
import requests

# Health check
response = requests.get("http://localhost:8080/health")
print(response.json())

# Search for tables
response = requests.post(
    "http://localhost:8080/discover",
    json={"query": "customer"}
)
print(response.json())

# Get compliance metrics
response = requests.get("http://localhost:8080/compliance")
print(response.json())
```

### cURL
```bash
# Health check
curl http://localhost:8080/health

# Discover data
curl -X POST http://localhost:8080/discover \
  -H "Content-Type: application/json" \
  -d '{"query": "customer tables"}'

# Get compliance
curl http://localhost:8080/compliance
```

---

## OpenAPI Documentation
Interactive API documentation is available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
