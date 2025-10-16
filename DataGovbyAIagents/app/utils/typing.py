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

"""Type definitions and Pydantic models for SyncFlow API."""

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def dumps(obj: Any) -> str:
    """Serialize object to JSON string.

    Args:
        obj: Object to serialize

    Returns:
        JSON string representation
    """
    return json.dumps(obj)


class Message(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class InputChat(BaseModel):
    """Input chat request model."""

    messages: List[Message] = Field(
        default_factory=list, description="List of messages in conversation"
    )


class Metadata(BaseModel):
    """Request metadata model."""

    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


class Request(BaseModel):
    """API request model for streaming messages."""

    input: InputChat = Field(..., description="Input chat messages")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration dict")


class Feedback(BaseModel):
    """Feedback model for collecting user feedback."""

    run_id: Optional[str] = Field(None, description="Run identifier")
    feedback_type: str = Field(..., description="Type of feedback")
    feedback_text: str = Field(..., description="Feedback text")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DataDiscoveryResult(BaseModel):
    """Result from data discovery query."""

    tables: List[Dict[str, Any]] = Field(..., description="Found tables")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total number of results")


class ComplianceScoreResult(BaseModel):
    """Compliance score result."""

    overall_score: float = Field(..., description="Overall compliance score (0-100)")
    documentation_pct: float = Field(..., description="Documentation percentage")
    high_risk_tables: int = Field(..., description="Count of high-risk tables")
    tables_with_pii: int = Field(..., description="Count of tables with PII")


class PIIDetectionResult(BaseModel):
    """PII detection result."""

    table_name: str = Field(..., description="Table name")
    risk_level: str = Field(..., description="Risk level: HIGH, MEDIUM, LOW, NONE")
    pii_columns_count: int = Field(..., description="Number of PII columns detected")
    pii_columns: List[str] = Field(..., description="List of PII column names")
    confidence: float = Field(..., description="Confidence score (0-100)")
