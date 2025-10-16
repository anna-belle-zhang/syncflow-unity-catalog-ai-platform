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

"""SyncFlow Streamlit UI for data governance."""

import logging
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.utils.api_client import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="SyncFlow AI Governance",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize API client
api_base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
api_client = APIClient(base_url=api_base_url)


# Page styling
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        color: #0066cc;
        margin-bottom: 2rem;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f4f8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client."""
    return APIClient(base_url=api_base_url)


def render_sidebar() -> str:
    """Render sidebar navigation.

    Returns:
        Selected page
    """
    st.sidebar.title("🌊 SyncFlow")
    st.sidebar.markdown("*AI-Powered Data Governance*")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["📊 Overview", "🔎 Discover", "📝 Documentation", "✅ Compliance", "🔒 PII Risk"],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        """
        **SyncFlow** is an AI-powered data governance platform
        that helps teams manage their data assets effectively.

        **Features:**
        - Natural language data discovery
        - AI-generated documentation
        - Compliance monitoring
        - PII risk analysis
        - Metadata health tracking

        Powered by Google Gemini 2.5 Flash
        """
    )

    return page


def render_overview() -> None:
    """Render overview page."""
    st.title("📊 SyncFlow Overview")
    st.markdown("*Real-time insights from your data governance platform*")

    # Check API health
    health = api_client.health_check()

    if health.get("status") != "healthy":
        st.error(
            "⚠️ Backend API is not responding. Make sure the backend server is running."
        )
        st.info("Run `make backend` to start the backend server.")
        return

    st.success("✓ Backend connected")

    # Get compliance data
    with st.spinner("Loading compliance metrics..."):
        compliance = api_client.get_compliance()
        health_info = api_client.get_metadata_health()

    # Display error if any
    if "error" in compliance:
        st.error(f"Error loading compliance data: {compliance['error']}")
        return

    # Metadata health
    st.subheader("📡 Metadata Health")
    col1, col2, col3 = st.columns(3)

    with col1:
        status_emoji = {
            "FRESH": "🟢",
            "ACCEPTABLE": "🟡",
            "STALE": "🔴",
            "UNKNOWN": "⚪",
        }.get(health_info.get("freshness_status"), "⚪")
        st.metric("Status", f"{status_emoji} {health_info.get('freshness_status', 'N/A')}")

    with col2:
        st.metric("Minutes Since Sync", health_info.get("minutes_since_sync", -1))

    with col3:
        st.metric("Tables Synced", health_info.get("tables_synced", 0))

    st.markdown("---")

    # Compliance metrics
    st.subheader("✅ Compliance Metrics")

    summary = compliance.get("summary", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        score = summary.get("overall_score", 0)
        st.metric("Compliance Score", f"{score:.1f}/100")
        st.progress(score / 100)

    with col2:
        score_data = compliance.get("compliance_score", {})
        st.metric("Documentation Rate", f"{score_data.get('documentation_pct', 0):.1f}%")

    with col3:
        st.metric("High Risk Tables", summary.get("high_risk_count", 0))

    with col4:
        st.metric("Undocumented", summary.get("undocumented_count", 0))

    st.markdown("---")

    # High risk tables
    st.subheader("🔴 High Risk Tables")
    high_risk = compliance.get("high_risk_tables", [])

    if high_risk:
        risk_df = pd.DataFrame(high_risk[:10])
        if "risk_level" in risk_df.columns:
            display_cols = ["full_table_name", "risk_level", "pii_columns_count"]
            if all(col in risk_df.columns for col in display_cols):
                st.dataframe(
                    risk_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                )
    else:
        st.info("✓ No high-risk tables detected")


def render_discover() -> None:
    """Render data discovery page."""
    st.title("🔎 AI-Powered Data Discovery")
    st.markdown("Search for tables using natural language")

    # Check API health
    health = api_client.health_check()
    if health.get("status") != "healthy":
        st.error("Backend API is not available")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_input(
            "Ask a question about your data:",
            placeholder="Find tables related to customers...",
        )

    with col2:
        search_btn = st.button("🔍 Search", use_container_width=True)

    if search_btn and query:
        with st.spinner("Searching..."):
            results = api_client.discover_data(query)

        if "error" in results:
            st.error(f"Error: {results['error']}")
        else:
            st.subheader("Results")

            results_list = results.get("results", [])
            if results_list:
                results_df = pd.DataFrame(results_list)
                st.dataframe(results_df, use_container_width=True, hide_index=True)

                # Allow selecting a table for details
                st.subheader("Get Table Details")
                selected_idx = st.selectbox(
                    "Select a table",
                    range(len(results_list)),
                    format_func=lambda i: results_list[i].get("full_name", "Unknown"),
                )

                if st.button("Get Details"):
                    table_name = results_list[selected_idx].get("full_name")
                    with st.spinner(f"Loading details for {table_name}..."):
                        details = api_client.get_table_details(table_name)

                    if "error" not in details:
                        st.markdown(f"### {table_name}")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Type", details.get("table", {}).get("table_type"))
                        with col2:
                            st.metric("Columns", details.get("column_count", 0))

                        if details.get("pii_info"):
                            pii = details["pii_info"]
                            st.warning(f"🔒 PII Detected: {pii.get('pii_columns_count')} columns")
            else:
                st.info("No tables found matching your query")


def render_documentation() -> None:
    """Render documentation page."""
    st.title("📝 AI Auto-Documentation")
    st.markdown("Generate descriptions for your tables using AI")

    health = api_client.health_check()
    if health.get("status") != "healthy":
        st.error("Backend API is not available")
        return

    col1, col2 = st.columns([3, 1])

    with col1:
        table_name = st.text_input(
            "Enter full table name:",
            placeholder="catalog.schema.table",
        )

    with col2:
        gen_btn = st.button("✨ Generate", use_container_width=True)

    if gen_btn and table_name:
        with st.spinner("Generating description with AI..."):
            result = api_client.generate_description(table_name)

        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.success("Description generated!")
            st.markdown(result.get("description", ""))

            # Copy button
            st.code(result.get("description", ""), language=None)


def render_compliance() -> None:
    """Render compliance page."""
    st.title("✅ Compliance Monitoring")
    st.markdown("Track data governance compliance metrics")

    health = api_client.health_check()
    if health.get("status") != "healthy":
        st.error("Backend API is not available")
        return

    with st.spinner("Loading compliance data..."):
        compliance = api_client.get_compliance()

    if "error" in compliance:
        st.error(f"Error: {compliance['error']}")
        return

    # Overall score
    score = compliance.get("compliance_score", {})
    overall = score.get("overall_compliance_score", 0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Overall Score", f"{overall:.1f}/100")
        st.progress(overall / 100)

    with col2:
        st.metric("Total Tables", score.get("total_tables", 0))
        st.metric("Documented", f"{score.get('documentation_pct', 0):.1f}%")

    with col3:
        st.metric("With PII", score.get("tables_with_pii", 0))
        st.metric("High Risk", score.get("high_risk_tables", 0))

    st.markdown("---")

    # Undocumented tables
    st.subheader("📝 Undocumented Tables")
    undocumented = compliance.get("undocumented_tables", [])

    if undocumented:
        undoc_df = pd.DataFrame(undocumented[:20])
        display_cols = [col for col in ["full_name", "table_type", "created"] if col in undoc_df.columns]
        if display_cols:
            st.dataframe(undoc_df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.success("✓ All tables are documented!")


def render_pii_risk() -> None:
    """Render PII risk page."""
    st.title("🔒 PII Risk Analysis")
    st.markdown("Identify and manage data containing personally identifiable information")

    health = api_client.health_check()
    if health.get("status") != "healthy":
        st.error("Backend API is not available")
        return

    with st.spinner("Analyzing PII risk..."):
        pii_data = api_client.analyze_pii()

    if "error" in pii_data:
        st.error(f"Error: {pii_data['error']}")
        return

    # PII metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tables with PII", pii_data.get("total_tables_with_pii", 0))

    with col2:
        st.metric("High Risk", pii_data.get("high_risk_count", 0))

    with col3:
        st.metric("Medium Risk", pii_data.get("medium_risk_count", 0))

    st.markdown("---")

    # High risk tables
    st.subheader("🔴 High Risk Tables")
    high_risk = pii_data.get("high_risk_tables", [])

    if high_risk:
        risk_df = pd.DataFrame(high_risk)
        display_cols = [col for col in ["full_table_name", "risk_level", "pii_columns_count"]
                       if col in risk_df.columns]
        if display_cols:
            st.dataframe(risk_df[display_cols], use_container_width=True, hide_index=True)

    st.markdown("---")

    # Medium risk tables
    st.subheader("🟡 Medium Risk Tables")
    medium_risk = pii_data.get("medium_risk_tables", [])

    if medium_risk:
        risk_df = pd.DataFrame(medium_risk)
        display_cols = [col for col in ["full_table_name", "risk_level", "pii_columns_count"]
                       if col in risk_df.columns]
        if display_cols:
            st.dataframe(risk_df[display_cols], use_container_width=True, hide_index=True)


# Main app
def main() -> None:
    """Main Streamlit app."""
    page = render_sidebar()

    if page == "📊 Overview":
        render_overview()
    elif page == "🔎 Discover":
        render_discover()
    elif page == "📝 Documentation":
        render_documentation()
    elif page == "✅ Compliance":
        render_compliance()
    elif page == "🔒 PII Risk":
        render_pii_risk()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p><strong>🌊 SyncFlow - Data Governance Excellence</strong></p>
            <p>Powered by Fivetran • Databricks Unity Catalog • Google Cloud</p>
            <p style='font-size: 0.9em; margin-top: 10px;'>
                🤖 Google Gemini 2.5 Flash
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
