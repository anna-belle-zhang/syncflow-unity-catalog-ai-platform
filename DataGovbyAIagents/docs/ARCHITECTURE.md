# SyncFlow Architecture

## System Overview

SyncFlow is an AI-powered data governance platform that provides intelligent insights into Unity Catalog metadata. It leverages Google Gemini 2.5 Flash to enable natural language discovery, automated documentation, and compliance monitoring.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Streamlit Web Application                    │   │
│  │  - Data Discovery UI                                 │   │
│  │  - Compliance Dashboard                              │   │
│  │  - Documentation Generator                           │   │
│  │  - PII Risk Analysis                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼──────────────────────────────────────┐
│                  Backend API Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    FastAPI Server (Uvicorn)                         │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │     API Endpoints                           │   │   │
│  │  │  - /discover - Data discovery               │   │   │
│  │  │  - /compliance - Compliance metrics         │   │   │
│  │  │  - /pii-analysis - PII risk analysis        │   │   │
│  │  │  - /table-details - Get table info          │   │   │
│  │  │  - /query - AI-powered queries              │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬──────────────────────────────────┬──────────────┘
             │                                  │
      Vertex AI API                       BigQuery API
             │                                  │
┌────────────▼───────────────┐      ┌──────────▼───────────────┐
│   Gemini 2.5 Flash         │      │   BigQuery              │
│                             │      │                         │
│  - Natural Language Q&A    │      │ UC Metadata Dataset     │
│  - Table Descriptions      │      │ - Tables               │
│  - Compliance Reports      │      │ - Columns              │
│  - PII Detection Insights  │      │ - Schemas              │
│                             │      │                         │
│                             │      │ ML Models Dataset      │
│                             │      │ - PII Summary          │
│                             │      │ - Anomaly Detection    │
│                             │      │ - Clustering           │
└─────────────────────────────┘      └────────────────────────┘
```

## Core Components

### Frontend (`frontend/`)
- **streamlit_app.py**: Main Streamlit application with 5 pages:
  - Overview: Dashboard with compliance metrics
  - Discover: Natural language data discovery
  - Documentation: AI-generated table descriptions
  - Compliance: Governance tracking
  - PII Risk: Sensitive data analysis

- **utils/api_client.py**: HTTP client for backend API communication

### Backend (`app/`)

#### server.py
FastAPI application with RESTful endpoints:
- Health check
- Data discovery
- Compliance scoring
- Table details retrieval
- Description generation
- PII analysis
- Metadata health

#### agent.py
DataGovernanceAgent orchestrates:
- AI interactions via Gemini
- Governance operations
- Metadata queries
- Report generation

#### governance_engine.py
GovernanceEngine provides:
- Compliance score calculation
- High-risk table identification
- Documentation rate tracking
- Undocumented table detection

#### unity_catalog_client.py
UnityCatalogClient interfaces with:
- BigQuery metadata tables
- ML models dataset
- Metadata freshness checks

### Data Flow

#### Discovery Flow
```
User Query
    ↓
Streamlit UI
    ↓
API Client (HTTP POST /discover)
    ↓
FastAPI Endpoint
    ↓
DataGovernanceAgent.discover_data()
    ↓
UnityCatalogClient.search_tables_by_keyword()
    ↓
BigQuery Query
    ↓
Results → API Response → Streamlit Display
```

#### Compliance Flow
```
Compliance Dashboard
    ↓
API Client (HTTP GET /compliance)
    ↓
FastAPI Endpoint
    ↓
DataGovernanceAgent.check_compliance()
    ↓
GovernanceEngine Methods:
  - get_compliance_score()
  - get_high_risk_tables()
  - get_undocumented_tables()
    ↓
BigQuery Queries
    ↓
Results → API Response → Dashboard Metrics
```

## Deployment Architecture

### Local Development
```
Your Machine
├── Python 3.11 Environment
├── Backend (Uvicorn on :8080)
├── Frontend (Streamlit on :8501)
└── BigQuery (Cloud)
```

### Cloud Deployment
```
Google Cloud Platform
├── Cloud Run (API)
│   ├── Containerized FastAPI
│   └── Auto-scaling
├── Secret Manager
│   └── Credentials & Tokens
├── BigQuery
│   ├── UC Metadata
│   └── ML Models
├── Vertex AI
│   └── Gemini 2.5 Flash API
└── Cloud Logging
    └── Application Logs
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI**: Vertex AI (Gemini 2.5 Flash)
- **Data**: Google Cloud BigQuery
- **Logging**: Google Cloud Logging
- **Server**: Uvicorn

### Frontend
- **Framework**: Streamlit
- **HTTP Client**: Requests
- **Visualization**: Plotly
- **Data Processing**: Pandas

### Infrastructure
- **Container**: Docker
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Registry**: Artifact Registry

## Database Schema (Assumed)

### Metadata Dataset (unity_catalog_metadata)
```sql
tables
├── catalog_name
├── schema_name
├── table_name
├── full_name
├── table_type
├── comment
├── created_at
└── _fivetran_synced

columns
├── table_full_name
├── column_name
├── data_type
├── nullable
├── position
└── comment
```

### ML Dataset (ml_models)
```sql
pii_summary_by_table
├── table_catalog
├── table_schema
├── table_name
├── full_table_name
├── pii_columns_count
├── pii_columns
├── risk_level
└── avg_pii_score_pct
```

## Security Considerations

### Authentication
- Google Cloud authentication via service account
- API keys stored in Secret Manager
- Streamlit session management

### Authorization
- Service account with minimal BigQuery permissions
- Row-level access control via BigQuery policies
- API rate limiting

### Data Protection
- SSL/TLS for all communication
- Encrypted credentials in Secret Manager
- Audit logging for compliance

## Performance Optimization

### Caching
- Streamlit @st.cache_resource for API client
- BigQuery results caching
- API response caching

### Scalability
- Cloud Run auto-scaling for backend
- BigQuery partitioned tables
- Streamlit horizontal scaling

## Monitoring & Observability

### Logging
- Application logs → Google Cloud Logging
- Structured logging with JSON
- Log-based metrics

### Metrics
- API latency
- Error rates
- Request throughput
- Resource utilization

### Alerts
- Error rate > 5%
- API latency > 1s
- Metadata staleness > 60 min

## Disaster Recovery

### Backup Strategy
- BigQuery snapshots for metadata
- Terraform state in GCS
- Code in GitHub

### Recovery Procedures
- Terraform apply to restore infrastructure
- BigQuery restore from snapshots
- Container rebuild from Docker registry

## Future Enhancements

- Advanced AI reasoning with multi-step queries
- Real-time data lineage tracking
- Custom governance policies
- Integration with external data catalogs
- ML-based anomaly detection
- Advanced access control
