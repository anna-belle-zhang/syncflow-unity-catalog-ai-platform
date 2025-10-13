# AI Dashboard Architecture

## Overview

**The Integration Gap**: Databricks Unity Catalog and Google Cloud Platform lack native integration, preventing organizations from leveraging GCP's AI/ML services for data governance.

**Our Solution**: A custom Fivetran connector bridges this gap by syncing Unity Catalog metadata to BigQuery, enabling AI-powered governance through Vertex AI Gemini 2.5 Flash. The platform provides natural language search, automated documentation, compliance monitoring, and data quality assessments - bringing Databricks governance into the Google Cloud AI ecosystem.

## Technical Architecture

```mermaid
graph TB
    subgraph "Data Source"
        UC[Databricks<br/>Unity Catalog<br/>REST API]
    end

    subgraph "Data Integration Layer"
        FT[Fivetran<br/>Custom Connector<br/>Python SDK]
    end

    subgraph "Google Cloud Platform"
        subgraph "Data Warehouse"
            BQ[(BigQuery<br/>unity_catalog_metadata<br/>Dataset)]
        end

        subgraph "AI/ML Services"
            GEMINI[Vertex AI<br/>Gemini 2.5 Flash API<br/>Natural Language Processing]
        end

        subgraph "Compute"
            GCE[Cloud Run / GCE<br/>Streamlit Server<br/>Python 3.9+]
        end
    end

    subgraph "Application Layer"
        AGENTS[AI Agents Module<br/>gemini_ai_agents.py<br/>Python Classes]
        DASH[Dashboard UI<br/>governance_dashboard.py<br/>Streamlit Framework]
    end

    subgraph "End User"
        USER[Web Browser<br/>HTTP/8501]
    end

    UC -->|REST API<br/>JSON| FT
    FT -->|SQL INSERT<br/>Incremental Sync| BQ
    BQ -->|SQL Queries<br/>Metadata Retrieval| AGENTS
    AGENTS -->|API Calls<br/>Prompt Engineering| GEMINI
    GEMINI -->|JSON Response<br/>AI Insights| AGENTS
    AGENTS -->|Python Objects| DASH
    DASH -->|Streamlit Components| GCE
    GCE -->|HTTPS| USER

    style UC fill:#FF3621,color:#fff
    style FT fill:#0073E6,color:#fff
    style BQ fill:#669df6,color:#fff
    style GEMINI fill:#4285f4,color:#fff
    style GCE fill:#34a853,color:#fff
    style AGENTS fill:#fbbc04,color:#000
    style DASH fill:#ea4335,color:#fff
    style USER fill:#5f6368,color:#fff
```

## ASCII Diagram (Alternative View)

```
┌─────────────────────────────────────────────────────────────────┐
│                    governance_dashboard.py                       │
│                   (Interactive Web Interface)                    │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │  Overview  │  │   Search   │  │    Docs    │  │Compliance│ │
│  │    Page    │  │    Page    │  │    Page    │  │   Page   │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘ │
└────────┼───────────────┼───────────────┼──────────────┼────────┘
         │               │               │              │
         │  ┌────────────▼───────────────▼──────────────▼───────┐
         │  │                                                    │
         └──►         gemini_ai_agents.py                       │
            │       (Gemini AI Agents Module)                   │
            │                                                    │
            │  ┌──────────────────────────────────────────────┐ │
            │  │  DataDiscoveryAgent                          │ │
            │  │  • Natural language search                   │ │
            │  │  • Table/schema lookup                       │ │
            │  │  • Metadata queries                          │ │
            │  └──────────────────────────────────────────────┘ │
            │                                                    │
            │  ┌──────────────────────────────────────────────┐ │
            │  │  ComplianceGuardianAgent                     │ │
            │  │  • Compliance scoring                        │ │
            │  │  • Risk assessment                           │ │
            │  │  • Policy monitoring                         │ │
            │  └──────────────────────────────────────────────┘ │
            │                                                    │
            │  ┌──────────────────────────────────────────────┐ │
            │  │  AutoDocumentationAgent                      │ │
            │  │  • AI-generated descriptions                 │ │
            │  │  • Data dictionary creation                  │ │
            │  │  • Column documentation                      │ │
            │  └──────────────────────────────────────────────┘ │
            │                                                    │
            │  ┌──────────────────────────────────────────────┐ │
            │  │  DataQualityMonitorAgent                     │ │
            │  │  • Freshness checks                          │ │
            │  │  • Anomaly detection                         │ │
            │  │  • Quality reports                           │ │
            │  └──────────────────────────────────────────────┘ │
            │                                                    │
            │              Powered by ⚡                         │
            │         Google Gemini 2.5 Flash                   │
            └───────────────────┬────────────────────────────────┘
                                │
                                │ SQL Queries
                                ▼
                    ┌───────────────────────┐
                    │   Google BigQuery     │
                    │  (Metadata Storage)   │
                    │                       │
                    │ • unity_catalog_      │
                    │   metadata dataset    │
                    │ • Tables metadata     │
                    │ • Columns metadata    │
                    └───────────────────────┘
```

## Component Interaction Flow

1. **User** interacts with **Streamlit Dashboard** UI
2. **Dashboard** calls **AI Agents** for intelligent features
3. **AI Agents** query **BigQuery** for metadata
4. **AI Agents** use **Gemini 2.5 Flash** to process and analyze data
5. **Dashboard** displays results to user

## File Descriptions

### `gemini_ai_agents.py` (Located in DataGovbyAIagents/)
**Role**: Backend AI intelligence layer

**Contains**:
- 4 AI agent classes powered by Gemini 2.5 Flash
- BigQuery query logic
- Natural language processing
- Response formatting

**Key Classes**:
- `DataDiscoveryAgent` - Search and discovery
- `ComplianceGuardianAgent` - Governance monitoring
- `AutoDocumentationAgent` - AI documentation generation
- `DataQualityMonitorAgent` - Quality monitoring

### `governance_dashboard.py` (Located in DataGovbyAIagents/)
**Role**: Frontend web interface

**Contains**:
- Streamlit UI components
- Page layouts and navigation
- Data visualizations (Plotly charts)
- User interaction handlers

**Pages**:
- 📊 Overview - Key metrics dashboard
- 🔎 Table Search - Natural language search
- 📝 Documentation - AI-powered doc generation
- ✅ Compliance - Governance monitoring

## Data Flow Example

```
User Query: "Find all customer tables"
         ↓
   Streamlit Dashboard
         ↓
   DataDiscoveryAgent.query()
         ↓
   BigQuery SQL Query
         ↓
   Results Processing
         ↓
   Gemini 2.5 Flash (if needed)
         ↓
   Formatted Response
         ↓
   Display in UI
```
