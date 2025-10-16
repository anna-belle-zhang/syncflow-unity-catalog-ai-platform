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

.PHONY: install test playground backend ui lint setup-dev-env help

help:
	@echo "SyncFlow - AI-Powered Data Governance Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install dependencies with uv"
	@echo "  make test           Run unit and integration tests"
	@echo "  make playground     Run backend + frontend locally"
	@echo "  make backend        Run backend API server only"
	@echo "  make ui             Run Streamlit frontend only"
	@echo "  make lint           Run code quality checks"
	@echo "  make setup-dev-env  Deploy dev infrastructure"

install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; source ~/.bashrc; }
	uv sync --dev

test:
	uv run pytest tests/unit -v && uv run pytest tests/integration -v

test-unit:
	uv run pytest tests/unit -v

test-integration:
	uv run pytest tests/integration -v

test-coverage:
	uv run pytest --cov=app --cov=frontend tests/ -v

playground:
	@echo "Starting backend and frontend..."
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8080 --reload &
	sleep 2
	uv run streamlit run frontend/streamlit_app.py --server.enableCORS=false --browser.serverAddress=localhost --server.enableXsrfProtection=false

backend:
	@echo "Starting backend API server..."
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8080 --reload

ui:
	@echo "Starting Streamlit frontend..."
	uv run streamlit run frontend/streamlit_app.py --server.enableCORS=false --browser.serverAddress=localhost --server.enableXsrfProtection=false

lint:
	@echo "Running linters..."
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run mypy app tests --no-error-summary 2>&1 | head -20 || true

format:
	@echo "Formatting code..."
	uv run ruff format .
	uv run ruff check . --fix

setup-dev-env:
	@if [ -z "$$PROJECT_ID" ]; then echo "Error: PROJECT_ID environment variable is not set"; exit 1; fi
	@echo "Setting up dev environment..."
	@(cd deployment/terraform/dev && terraform init && terraform apply --var-file vars/env.tfvars --var dev_project_id=$$PROJECT_ID --auto-approve)

docker-build:
	@echo "Building Docker image..."
	docker build -t syncflow-api:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8080:8080 --env-file .env syncflow-api:latest

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache build dist *.egg-info
	find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true

requirements:
	@echo "Exporting requirements.txt from uv.lock..."
	uv export --output-file requirements.txt

.DEFAULT_GOAL := help
