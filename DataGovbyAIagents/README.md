# SyncFlow - AI-Powered Data Governance Platform

A production-ready data governance platform that combines AI intelligence with data discovery and compliance monitoring for Unity Catalog.

Powered by Google Gemini 2.5 Flash and Vertex AI.

## Features

- **AI-Powered Data Discovery**: Natural language search over your data catalog
- **Automated Documentation**: Generate table and column descriptions with AI
- **Compliance Monitoring**: Track governance metrics and high-risk data
- **PII Detection**: Identify and manage sensitive data
- **Metadata Health**: Monitor freshness and quality of catalog metadata
- **RESTful API**: Complete API for integration with other systems
- **Cloud-Native**: Deploy to Google Cloud Run with Terraform IaC

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd DataGovbyAIagents
   make install
   cp .env.tpl .env
   # Edit .env with your configuration
   ```

2. **Run Locally**
   ```bash
   make playground
   ```
   - Backend: http://localhost:8080
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8080/docs

3. **Run Tests**
   ```bash
   make test
   ```

### Cloud Deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

```bash
# Deploy to Cloud Run
export PROJECT_ID=your-gcp-project
gcloud run deploy syncflow-api \
  --image gcr.io/$PROJECT_ID/syncflow-api:latest \
  --region us-central1 \
  --allow-unauthenticated
```

## Project Structure

```
DataGovbyAIagents/
├── app/                        # Backend application
│   ├── server.py              # FastAPI application
│   ├── agent.py               # AI agent orchestration
│   ├── governance_engine.py    # Compliance & governance
│   ├── unity_catalog_client.py # UC metadata queries
│   └── utils/
│       ├── typing.py          # Type definitions
│       └── tracing.py         # OpenTelemetry tracing
│
├── frontend/                   # Streamlit UI
│   ├── streamlit_app.py       # Main application
│   └── utils/
│       └── api_client.py      # API communication
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── load_test/             # Performance tests
│
├── deployment/                 # Infrastructure & CI/CD
│   ├── terraform/             # Infrastructure as Code
│   ├── ci/                     # GitHub Actions workflows
│   └── cd/                     # Deployment pipelines
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # System design
│   ├── API_REFERENCE.md       # API documentation
│   └── DEPLOYMENT_GUIDE.md    # Deployment instructions
│
├── local_test/                # Original code (preserved)
├── Dockerfile                  # Container definition
├── Makefile                    # Build automation
├── pyproject.toml             # Project configuration
└── README.md                   # This file
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **AI**: Vertex AI (Gemini 2.5 Flash)
- **Database**: Google Cloud BigQuery
- **Server**: Uvicorn
- **Package Manager**: uv

### Frontend
- **Framework**: Streamlit
- **Visualization**: Plotly
- **HTTP Client**: Requests

### Infrastructure
- **Container**: Docker
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Registry**: Artifact Registry
- **Platform**: Google Cloud Run

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /discover` - Search for tables
- `GET /compliance` - Get compliance metrics
- `GET /table-details/{table_name}` - Get table information
- `POST /generate-description` - Generate AI description
- `GET /pii-analysis` - Analyze PII risk
- `GET /metadata-health` - Check metadata freshness
- `POST /query` - AI-powered queries
- `POST /feedback` - Submit feedback

See [API_REFERENCE.md](docs/API_REFERENCE.md) for complete documentation.

## Configuration

### Environment Variables
Create `.env` file (see `.env.tpl`):

```bash
# GCP
PROJECT_ID=your-gcp-project
REGION=us-central1

# Vertex AI
MODEL_ID=gemini-2.5-flash-002

# BigQuery
METADATA_DATASET=unity_catalog_metadata
ML_DATASET=ml_models

# Application
PORT=8080
LOG_LEVEL=INFO
```

### GCP Setup
1. Create GCP project
2. Enable required APIs
3. Create service account
4. Set `GOOGLE_APPLICATION_CREDENTIALS`

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed setup.

## Usage

### Frontend (Streamlit)
- **Overview**: Dashboard with compliance metrics
- **Discover**: Natural language table search
- **Documentation**: AI-generated descriptions
- **Compliance**: Governance tracking
- **PII Risk**: Sensitive data analysis

### Backend (API)
```python
import requests

# Search for tables
response = requests.post(
    "http://localhost:8080/discover",
    json={"query": "customer data"}
)
tables = response.json()

# Get compliance metrics
response = requests.get("http://localhost:8080/compliance")
compliance = response.json()

# Generate description
response = requests.post(
    "http://localhost:8080/generate-description",
    json={"table_name": "default.gold.dim_customer"}
)
description = response.json()
```

## Development

### Install Dependencies
```bash
make install
```

### Run Tests
```bash
make test              # All tests
make test-unit        # Unit tests only
make test-coverage    # With coverage report
```

### Code Quality
```bash
make lint             # Run linters
make format           # Format code
```

### Local Development
```bash
make backend          # Backend only
make ui              # Frontend only
make playground      # Both services
```

## Deployment

### Docker
```bash
make docker-build
make docker-run
```

### Cloud Run
```bash
export PROJECT_ID=your-project
gcloud run deploy syncflow-api \
  --image gcr.io/$PROJECT_ID/syncflow-api:latest \
  --region us-central1
```

### Terraform
```bash
cd deployment/terraform
terraform init
terraform plan -var-file vars/env.tfvars
terraform apply -var-file vars/env.tfvars
```

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flows
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API documentation
- **[DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Deployment and configuration

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/name`
3. Make your changes
4. Run tests: `make test`
5. Run linting: `make lint`
6. Commit: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature/name`
8. Create Pull Request

## Local Test Code

The original working code is preserved in `local_test/`:
- `local_test/gemini_ai_agents.py` - Original AI agents
- `local_test/governance_dashboard.py` - Original Streamlit app
- `local_test/requirements.txt` - Original dependencies

## CI/CD Pipeline

### Pull Request Checks
- Unit tests
- Integration tests
- Code linting
- Type checking
- Docker build

### Staging Deployment
- Triggered on push to `develop`
- Builds and pushes Docker image
- Deploys to Cloud Run staging

### Production Deployment
- Triggered on push to `main`
- Builds and pushes Docker image
- Deploys to Cloud Run production
- Smoke tests
- Slack notification

## Monitoring

### Logs
```bash
gcloud logging read "resource.type=cloud_run_revision"
```

### Metrics
- API latency
- Error rates
- Request throughput
- Resource utilization

### Alerts
- Error rate > 5%
- API latency > 1s
- Metadata staleness > 60 min

## Security

- Service account with minimal permissions
- Credentials in Secret Manager
- SSL/TLS for all communication
- Audit logging enabled
- VPC isolation

## Troubleshooting

### Backend Issues
```bash
# Check logs
make backend  # Check output

# Health check
curl http://localhost:8080/health
```

### Frontend Issues
```bash
# Clear cache
rm -rf .streamlit_chats/

# Check logs
make ui  # Check output
```

### Test Failures
```bash
# Run with verbose output
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/unit/test_server.py::TestServer::test_health_check -v
```

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for more troubleshooting.

## Performance

- Backend: ~500ms API response time
- Frontend: <2s page load
- Metadata sync: Real-time via Fivetran
- Compliance scoring: <1s calculation

## Roadmap

- [ ] Advanced AI reasoning
- [ ] Real-time data lineage
- [ ] Custom governance policies
- [ ] External catalog integration
- [ ] ML-based anomaly detection
- [ ] Advanced access control

## License

Apache License 2.0

## Support

For issues, questions, or suggestions:
1. Check [docs/](docs/) for documentation
2. Check logs and error messages
3. Review API reference at `/docs`
4. Create an issue in the repository

## Authors

SyncFlow Contributors

---

**Powered by Google Gemini 2.5 Flash and Google Cloud Platform**

Built for data teams who care about governance, quality, and compliance.
