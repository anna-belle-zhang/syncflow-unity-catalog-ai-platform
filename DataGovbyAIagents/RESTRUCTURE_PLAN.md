# DataGovbyAIagents Restructuring Plan

## Overview
Restructure the DataGovbyAIagents project to follow production-ready architecture patterns based on the prod-monitoring-assistant reference implementation.

## Current State
```
DataGovbyAIagents/
├── gemini_ai_agents.py          (31,931 bytes)
├── governance_dashboard.py      (31,642 bytes)
└── requirements.txt             (330 bytes)
```

## Target State
```
DataGovbyAIagents/
├── local_test/                  # Original code preserved for local testing
│   ├── gemini_ai_agents.py
│   ├── governance_dashboard.py
│   └── requirements.txt
│
├── app/                         # Backend application code
│   ├── __init__.py
│   ├── server.py               # FastAPI/Uvicorn backend server
│   ├── agent.py                # AI agent logic
│   ├── governance_engine.py    # Unity Catalog governance logic
│   ├── unity_catalog_client.py # UC integration
│   └── utils/
│       ├── __init__.py
│       ├── tracing.py          # OpenTelemetry tracing
│       └── typing.py           # Type definitions
│
├── frontend/                    # Streamlit UI
│   ├── streamlit_app.py        # Main Streamlit application
│   ├── side_bar.py             # Sidebar components
│   ├── style/
│   │   ├── __init__.py
│   │   └── app_markdown.py     # Custom styling
│   └── utils/
│       ├── __init__.py
│       ├── chat_utils.py       # Chat UI utilities
│       ├── local_chat_history.py
│       ├── message_editing.py
│       ├── multimodal_utils.py
│       ├── stream_handler.py   # Streaming response handler
│       └── title_summary.py
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   ├── test_server.py
│   │   ├── test_agent.py
│   │   └── test_governance_engine.py
│   ├── integration/            # Integration tests
│   │   ├── __init__.py
│   │   ├── test_agent.py
│   │   └── test_server_e2e.py
│   └── load_test/             # Load/performance tests
│       ├── __init__.py
│       ├── README.md
│       ├── load_test.py
│       └── .results/
│           └── .placeholder
│
├── deployment/                  # Infrastructure & CI/CD
│   ├── README.md               # Deployment documentation
│   ├── ci/                     # Continuous Integration
│   │   └── pr_checks.yaml     # PR validation pipeline
│   ├── cd/                     # Continuous Deployment
│   │   ├── staging.yaml       # Staging deployment
│   │   └── deploy-to-prod.yaml # Production deployment
│   └── terraform/              # Infrastructure as Code
│       ├── backend.tf
│       ├── providers.tf
│       ├── variables.tf
│       ├── apis.tf            # GCP APIs enablement
│       ├── artifact_registry.tf
│       ├── build_triggers.tf
│       ├── iam.tf
│       ├── cicd_variables.tf
│       ├── vars/
│       │   └── env.tfvars     # Environment variables
│       └── dev/               # Dev environment
│           ├── backend.tf
│           ├── providers.tf
│           ├── variables.tf
│           ├── apis.tf
│           ├── iam.tf
│           ├── log_sinks.tf
│           ├── service_accounts.tf
│           ├── storage.tf
│           └── vars/
│               └── env.tfvars
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── DEPLOYMENT_GUIDE.md
│
├── notebooks/                   # Jupyter notebooks for experimentation
│   └── .gitkeep
│
├── .env.tpl                    # Environment template
├── .gitignore
├── Dockerfile                  # Container definition
├── Makefile                    # Build automation
├── pyproject.toml             # Python project config (uv/poetry)
├── uv.lock                    # Dependency lock file
├── requirements.txt           # Pip requirements
├── README.md                  # Project README
└── RESTRUCTURE_PLAN.md        # This file
```

## Implementation Tasks

### Phase 1: Preserve Existing Code
- [x] Create `local_test/` folder
- [ ] Move existing files to `local_test/`:
  - gemini_ai_agents.py
  - governance_dashboard.py
  - requirements.txt

### Phase 2: Backend Structure (app/)
- [ ] Create `app/` folder structure
- [ ] Split gemini_ai_agents.py into modular components:
  - `server.py` - FastAPI/Uvicorn backend
  - `agent.py` - AI agent orchestration
  - `governance_engine.py` - Governance logic
  - `unity_catalog_client.py` - UC API integration
- [ ] Create `app/utils/` with:
  - `tracing.py` - OpenTelemetry instrumentation
  - `typing.py` - Type definitions

### Phase 3: Frontend Structure (frontend/)
- [ ] Create `frontend/` folder structure
- [ ] Extract Streamlit UI from governance_dashboard.py into:
  - `streamlit_app.py` - Main app
  - `side_bar.py` - Sidebar components
- [ ] Create `frontend/style/` with custom styling
- [ ] Create `frontend/utils/` with:
  - `chat_utils.py`
  - `local_chat_history.py`
  - `stream_handler.py`
  - `message_editing.py`
  - `multimodal_utils.py`

### Phase 4: Test Infrastructure (tests/)
- [ ] Create `tests/unit/` with:
  - `test_server.py`
  - `test_agent.py`
  - `test_governance_engine.py`
- [ ] Create `tests/integration/` with:
  - `test_agent.py`
  - `test_server_e2e.py`
- [ ] Create `tests/load_test/` with:
  - `load_test.py`
  - `README.md`

### Phase 5: Deployment Infrastructure (deployment/)
- [ ] Create `deployment/ci/` with:
  - `pr_checks.yaml` - Run tests on PRs
- [ ] Create `deployment/cd/` with:
  - `staging.yaml` - Deploy to staging
  - `deploy-to-prod.yaml` - Production deployment
- [ ] Create `deployment/terraform/` with:
  - Core Terraform files (backend.tf, providers.tf, variables.tf)
  - `apis.tf` - Enable required GCP APIs
  - `artifact_registry.tf` - Container registry
  - `build_triggers.tf` - Cloud Build triggers
  - `iam.tf` - IAM permissions
  - `cicd_variables.tf` - CI/CD variables
  - `vars/env.tfvars` - Configuration
- [ ] Create `deployment/terraform/dev/` for dev environment
- [ ] Create `deployment/README.md` with deployment guide

### Phase 6: Root Configuration Files
- [ ] Create `Dockerfile` based on reference:
  - Use Python 3.11-slim
  - Install uv package manager
  - Copy app/ folder
  - Expose port 8080
  - Run uvicorn server
- [ ] Create `Makefile` with targets:
  - `install` - Install dependencies with uv
  - `test` - Run unit and integration tests
  - `playground` - Run backend + frontend locally
  - `backend` - Run backend only
  - `ui` - Run frontend only
  - `lint` - Code quality checks
  - `setup-dev-env` - Deploy dev infrastructure
- [ ] Create `pyproject.toml` with:
  - Project metadata
  - Dependencies (google-cloud-aiplatform, fastapi, streamlit, etc.)
  - Dev dependencies (pytest, ruff, mypy)
  - Tool configurations
- [ ] Create `.env.tpl` environment template
- [ ] Update `.gitignore`
- [ ] Update `README.md` with new structure

### Phase 7: Documentation
- [ ] Create `docs/ARCHITECTURE.md`
- [ ] Create `docs/API_REFERENCE.md`
- [ ] Create `docs/DEPLOYMENT_GUIDE.md`

## Key Technologies & Patterns

### Backend Stack
- **Framework**: FastAPI + Uvicorn
- **AI**: Vertex AI (Gemini 2.5 Flash)
- **Data Governance**: Unity Catalog
- **Tracing**: OpenTelemetry
- **Package Manager**: uv

### Frontend Stack
- **Framework**: Streamlit
- **Communication**: REST API to backend
- **Chat History**: Local storage

### Deployment Stack
- **Container**: Docker
- **Registry**: Artifact Registry
- **CI/CD**: Cloud Build
- **IaC**: Terraform
- **Orchestration**: Cloud Run / GKE

### Testing Stack
- **Unit Tests**: pytest
- **Integration Tests**: pytest with test client
- **Load Tests**: locust or custom load testing
- **Code Quality**: ruff, mypy, codespell

## Environment Variables Required
```bash
# GCP Configuration
PROJECT_ID=your-gcp-project
REGION=us-central1
MODEL_ID=gemini-2.5-flash-preview-0514

# Unity Catalog
UNITY_CATALOG_HOST=your-unity-catalog-host
UNITY_CATALOG_TOKEN=your-token

# Application
LOG_LEVEL=INFO
PORT=8080
```

## Migration Strategy
1. Keep original code in `local_test/` - NO CHANGES
2. Build new structure in parallel
3. Test new structure thoroughly
4. Once validated, deprecate `local_test/`

## GCP Data Engineer Agent Tasks
The following tasks will be handed off to the GCP data engineer agent:

1. **Create folder structure** - All 4 main folders + subfolders
2. **Backend refactoring** - Split monolithic code into modular app/
3. **Frontend extraction** - Create Streamlit app in frontend/
4. **Test suite creation** - Unit, integration, and load tests
5. **CI/CD pipelines** - Cloud Build configurations
6. **Terraform IaC** - Complete infrastructure as code
7. **Docker configuration** - Dockerfile and deployment configs
8. **Documentation** - Architecture, API, and deployment docs
9. **Makefile automation** - Build and deployment commands
10. **Environment setup** - .env templates and configuration

## Success Criteria
- [ ] All existing functionality preserved in local_test/
- [ ] Modular, maintainable code structure
- [ ] Comprehensive test coverage (>80%)
- [ ] Working CI/CD pipeline
- [ ] Infrastructure fully defined in Terraform
- [ ] Complete documentation
- [ ] Successful deployment to dev environment

## Timeline Estimate
- Phase 1: 30 minutes
- Phase 2: 2-3 hours
- Phase 3: 2-3 hours
- Phase 4: 2-3 hours
- Phase 5: 3-4 hours
- Phase 6: 1-2 hours
- Phase 7: 1-2 hours

**Total: 12-18 hours** (can be parallelized by agent)
