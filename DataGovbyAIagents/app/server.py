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

"""FastAPI server for SyncFlow data governance platform."""

import logging
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from google.cloud import logging as google_cloud_logging

from app.agent import DataGovernanceAgent
from app.utils.typing import Feedback, Request, dumps

# Configure logging
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(
    title="SyncFlow Data Governance API",
    description="AI-powered data governance platform for Unity Catalog",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize agent
try:
    agent = DataGovernanceAgent(
        project_id=os.getenv("PROJECT_ID"),
        location=os.getenv("REGION", "us-central1"),
        metadata_dataset=os.getenv("METADATA_DATASET", "unity_catalog_metadata"),
        ml_dataset=os.getenv("ML_DATASET"),
        model_id=os.getenv("MODEL_ID", "gemini-2.5-flash-002"),
    )
    logger.info("DataGovernanceAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    agent = None


# Routes


@app.get("/", response_class=RedirectResponse)
def redirect_root_to_docs() -> RedirectResponse:
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status
    """
    status = "healthy" if agent is not None else "unhealthy"
    return {
        "status": status,
        "service": "SyncFlow Data Governance API",
        "version": "0.1.0",
    }


@app.post("/discover")
def discover_data(request: Dict[str, Any]) -> Dict[str, Any]:
    """Discover data in Unity Catalog.

    Args:
        request: Request with query field

    Returns:
        Discovery results
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        query = request.get("query", "")
        if not query:
            raise ValueError("Query parameter required")

        result = agent.discover_data(query)
        return result

    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/compliance")
def get_compliance() -> Dict[str, Any]:
    """Get compliance metrics.

    Returns:
        Compliance information
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        return agent.check_compliance()
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/table-details/{table_name:path}")
def get_table_details(table_name: str) -> Dict[str, Any]:
    """Get detailed information about a table.

    Args:
        table_name: Fully qualified table name (catalog.schema.table)

    Returns:
        Table details
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        return agent.get_table_details(table_name)
    except Exception as e:
        logger.error(f"Error getting table details: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate-description")
def generate_description(request: Dict[str, Any]) -> Dict[str, str]:
    """Generate AI description for a table.

    Args:
        request: Request with table_name field

    Returns:
        Generated description
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        table_name = request.get("table_name", "")
        if not table_name:
            raise ValueError("table_name parameter required")

        description = agent.generate_table_description(table_name)
        return {"table_name": table_name, "description": description}

    except Exception as e:
        logger.error(f"Description generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/pii-analysis")
def analyze_pii() -> Dict[str, Any]:
    """Analyze PII risk across catalog.

    Returns:
        PII risk analysis
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        return agent.analyze_pii_risk()
    except Exception as e:
        logger.error(f"PII analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/metadata-health")
def get_metadata_health() -> Dict[str, Any]:
    """Check metadata health.

    Returns:
        Metadata health metrics
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        return agent.get_metadata_health()
    except Exception as e:
        logger.error(f"Metadata health check error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/query")
def query_with_ai(request: Dict[str, Any]) -> Dict[str, str]:
    """Query the AI agent with a natural language question.

    Args:
        request: Request with question field

    Returns:
        AI response
    """
    if agent is None:
        raise HTTPException(
            status_code=500, detail="Agent not initialized"
        )

    try:
        question = request.get("question", "")
        if not question:
            raise ValueError("question parameter required")

        answer = agent.query_with_ai(question)
        return {"question": question, "answer": answer}

    except Exception as e:
        logger.error(f"AI query error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> Dict[str, str]:
    """Collect user feedback.

    Args:
        feedback: Feedback data

    Returns:
        Success response
    """
    try:
        logger.log_struct(
            feedback.model_dump(), severity="INFO"
        )
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Feedback collection error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Main execution
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
