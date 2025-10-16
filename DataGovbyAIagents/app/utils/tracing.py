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

"""OpenTelemetry tracing utilities for SyncFlow."""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CloudTraceLoggingSpanExporter:
    """Cloud Trace exporter for OpenTelemetry spans.

    This exporter sends OpenTelemetry spans to Google Cloud Logging
    in a format that integrates with Cloud Trace.
    """

    def __init__(self) -> None:
        """Initialize the Cloud Trace exporter."""
        self.logger = logging.getLogger(__name__)

    def export(self, spans: list[Any]) -> None:
        """Export spans to Cloud Logging.

        Args:
            spans: List of spans to export
        """
        for span in spans:
            try:
                span_dict = self._span_to_dict(span)
                self.logger.info(f"Trace span: {span_dict}")
            except Exception as e:
                self.logger.error(f"Failed to export span: {e}")

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush pending spans.

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            True if successful
        """
        return True

    @staticmethod
    def _span_to_dict(span: Any) -> Dict[str, Any]:
        """Convert span to dictionary.

        Args:
            span: OpenTelemetry span

        Returns:
            Dictionary representation of span
        """
        return {
            "name": getattr(span, "name", "unknown"),
            "context": str(getattr(span, "context", "unknown")),
            "start_time": getattr(span, "start_time", None),
            "end_time": getattr(span, "end_time", None),
            "status": str(getattr(span, "status", "unknown")),
        }


def setup_tracing(
    app_name: str, service_name: Optional[str] = None
) -> Optional[Any]:
    """Setup OpenTelemetry tracing for application.

    Args:
        app_name: Name of application
        service_name: Name of service (defaults to app_name)

    Returns:
        Traceloop instance or None if tracing not available
    """
    if service_name is None:
        service_name = app_name

    try:
        from traceloop.sdk import Instruments, Traceloop

        logger.info(f"Initializing tracing for {app_name}")

        Traceloop.init(
            app_name=app_name,
            disable_batch=False,
            exporter=CloudTraceLoggingSpanExporter(),
            instruments={Instruments.LANGCHAIN},
        )

        logger.info("Tracing initialized successfully")
        return Traceloop

    except ImportError:
        logger.warning("Traceloop not available - tracing disabled")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize tracing: {e}")
        return None
