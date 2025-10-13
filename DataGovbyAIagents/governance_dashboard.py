"""
🌊 SyncFlow AI Governance Platform
Interactive Streamlit Dashboard

Powered by Google Gemini 2.5 Flash

Features:
- Overview dashboard with key metrics
- PII Discovery interface (Gemini-powered)
- Natural language table search (Gemini-powered)
- Auto-documentation (Gemini-powered)
- Compliance monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for agent imports
sys.path.append(os.path.dirname(__file__))

try:
    # Import AI agents (renamed file)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "vertex_ai_agents",
        os.path.join(os.path.dirname(__file__), "gemini_ai_agents.py")
    )
    vertex_ai_agents = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vertex_ai_agents)

    DataDiscoveryAgent = vertex_ai_agents.DataDiscoveryAgent
    ComplianceGuardianAgent = vertex_ai_agents.ComplianceGuardianAgent
    AutoDocumentationAgent = vertex_ai_agents.AutoDocumentationAgent
    DataQualityMonitorAgent = vertex_ai_agents.DataQualityMonitorAgent
except ImportError as e:
    st.error(f"⚠️ Please run: pip install -r requirements.txt\n\nError: {e}")
    st.stop()


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ID = "YOUR_GCP_PROJECT_ID"
METADATA_DATASET = "unity_catalog_metadata"
ML_DATASET = "ml_models"

# Page config
st.set_page_config(
    page_title="SyncFlow AI Governance",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize BigQuery client
@st.cache_resource
def get_bq_client():
    return bigquery.Client(project=PROJECT_ID)

bq = get_bq_client()

# Initialize AI agents
@st.cache_resource
def get_agents():
    return {
        'discovery': DataDiscoveryAgent(),
        'compliance': ComplianceGuardianAgent(),
        'documentation': AutoDocumentationAgent(),
        'quality': DataQualityMonitorAgent()
    }

agents = get_agents()


# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def run_query(query: str) -> pd.DataFrame:
    """Execute BigQuery query and return DataFrame"""
    return bq.query(query).to_dataframe()


def get_summary_metrics():
    """Get overall platform metrics"""
    try:
        query = f"""
        SELECT * FROM `{PROJECT_ID}.{ML_DATASET}.governance_dashboard_summary`
        ORDER BY metric
        """
        return run_query(query)
    except Exception:
        # Fallback to basic metrics from metadata tables
        query = f"""
        SELECT 'Total Tables' as metric, COUNT(*) as value, 'tables' as unit
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        UNION ALL
        SELECT 'Total Columns' as metric, COUNT(*) as value, 'columns' as unit
        FROM `{PROJECT_ID}.{METADATA_DATASET}.columns`
        UNION ALL
        SELECT 'Total Schemas' as metric, COUNT(DISTINCT schema_name) as value, 'schemas' as unit
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        UNION ALL
        SELECT 'Total Catalogs' as metric, COUNT(DISTINCT catalog_name) as value, 'catalogs' as unit
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        ORDER BY metric
        """
        return run_query(query)


def get_pii_summary():
    """Get PII detection summary"""
    try:
        query = f"""
        SELECT
            risk_level,
            COUNT(*) as table_count,
            SUM(pii_columns_count) as total_pii_columns
        FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table`
        GROUP BY risk_level
        ORDER BY
            CASE risk_level
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
                ELSE 4
            END
        """
        return run_query(query)
    except Exception:
        # Return empty DataFrame with correct schema
        return pd.DataFrame({
            'risk_level': ['NONE'],
            'table_count': [0],
            'total_pii_columns': [0]
        })


def get_table_growth_forecast():
    """Get table growth predictions"""
    try:
        query = f"""
        SELECT
            date,
            predicted_tables,
            prediction_interval_lower_bound,
            prediction_interval_upper_bound
        FROM `{PROJECT_ID}.{ML_DATASET}.table_growth_predictions`
        ORDER BY date
        """
        return run_query(query)
    except Exception:
        return pd.DataFrame()


def get_schema_anomalies():
    """Get detected schema anomalies"""
    try:
        query = f"""
        SELECT
            table_catalog,
            table_schema,
            table_count,
            anomaly_level,
            anomaly_score
        FROM `{PROJECT_ID}.{ML_DATASET}.schema_anomalies`
        WHERE anomaly_level IN ('HIGH', 'MEDIUM')
        ORDER BY anomaly_score DESC
        LIMIT 20
        """
        return run_query(query)
    except Exception:
        return pd.DataFrame()


def get_high_risk_pii_tables():
    """Get tables with high PII risk"""
    try:
        query = f"""
        SELECT
            full_table_name,
            pii_columns_count,
            pii_columns,
            risk_level,
            avg_pii_score_pct
        FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table`
        WHERE risk_level IN ('HIGH', 'MEDIUM')
        ORDER BY pii_columns_count DESC
        LIMIT 50
        """
        return run_query(query)
    except Exception:
        return pd.DataFrame()


def get_table_clusters():
    """Get table clustering results"""
    try:
        query = f"""
        SELECT
            cluster_name,
            COUNT(*) as table_count
        FROM `{PROJECT_ID}.{ML_DATASET}.table_clusters`
        GROUP BY cluster_name
        ORDER BY table_count DESC
        """
        return run_query(query)
    except Exception:
        return pd.DataFrame()


# ============================================================================
# Sidebar Navigation
# ============================================================================

st.sidebar.title("🌊 SyncFlow AI Governance")
st.sidebar.markdown("*Data Engineering Excellence*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Overview",
        "🔎 Table Search",
        "📝 Documentation",
        "✅ Compliance"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About SyncFlow")
st.sidebar.info(
    """
    **SyncFlow** - Data Engineering Company

    This AI-powered platform provides:
    - Automated PII detection (Gemini)
    - Natural language search (Gemini)
    - Auto-documentation (Gemini)
    - Compliance monitoring
    - Real-time insights

    **Data Source:**
    Databricks Unity Catalog via Fivetran

    **Powered by:**
    🤖 Google Gemini 2.5 Flash
    """
)


# ============================================================================
# Page: Overview Dashboard
# ============================================================================

if page == "📊 Overview":
    st.title("🌊 SyncFlow AI Governance Platform")
    st.markdown("**Real-time insights from your Unity Catalog metadata**")
    st.markdown("*🤖 Powered by Google Gemini 2.5 Flash*")

    # Get metrics
    metrics = get_summary_metrics()
    freshness = agents['quality'].check_metadata_freshness()

    # Freshness indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Last Sync:** {freshness['minutes_since_sync']} minutes ago")
    with col2:
        status_color = {
            'FRESH': '🟢',
            'ACCEPTABLE': '🟡',
            'STALE': '🔴'
        }[freshness['freshness_status']]
        st.markdown(f"**Status:** {status_color} {freshness['freshness_status']}")

    st.markdown("---")

    # Key metrics
    st.subheader("Key Metrics")

    # Create metric cards
    metric_cols = st.columns(4)

    for idx, row in metrics.iterrows():
        col_idx = idx % 4
        with metric_cols[col_idx]:
            st.metric(
                label=row['metric'],
                value=f"{int(row['value']):,}",
                help=f"{row['unit']}"
            )

    st.markdown("---")

    # PII Risk Summary
    st.subheader("🔒 PII Risk Summary")

    pii_summary = get_pii_summary()

    col1, col2 = st.columns(2)

    with col1:
        # PII risk pie chart
        fig = px.pie(
            pii_summary,
            values='table_count',
            names='risk_level',
            title='Tables by PII Risk Level',
            color='risk_level',
            color_discrete_map={
                'HIGH': '#ff4444',
                'MEDIUM': '#ffaa00',
                'LOW': '#44ff44',
                'NONE': '#cccccc'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # PII columns bar chart
        fig = px.bar(
            pii_summary,
            x='risk_level',
            y='total_pii_columns',
            title='Total PII Columns by Risk Level',
            color='risk_level',
            color_discrete_map={
                'HIGH': '#ff4444',
                'MEDIUM': '#ffaa00',
                'LOW': '#44ff44',
                'NONE': '#cccccc'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Table Clustering
    st.subheader("📊 Table Clusters")
    st.markdown("Tables grouped by ML clustering based on characteristics")

    clusters = get_table_clusters()

    if not clusters.empty:
        fig = px.bar(
            clusters,
            x='cluster_name',
            y='table_count',
            title='Tables by Cluster Type',
            color='table_count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 ML-based table clustering not yet available. Run ML models to enable this feature.")

    # Compliance Score
    st.markdown("---")
    st.subheader("✅ Compliance Score")

    compliance_score = agents['compliance'].get_compliance_score()

    col1, col2, col3 = st.columns(3)

    with col1:
        score = compliance_score['overall_compliance_score']
        st.metric(
            "Overall Compliance",
            f"{score}/100",
            help="Based on documentation rate and PII risk management"
        )

        # Progress bar
        st.progress(score / 100)

    with col2:
        st.metric(
            "Documentation Rate",
            f"{compliance_score['documentation_pct']:.1f}%",
            help="Percentage of tables with descriptions"
        )

    with col3:
        st.metric(
            "High Risk Tables",
            compliance_score['high_risk_tables'],
            delta=f"-{compliance_score['high_risk_tables']}" if compliance_score['high_risk_tables'] > 0 else "0",
            delta_color="inverse"
        )


# ============================================================================
# Page: PII Discovery - REMOVED (requires ML dataset)
# ============================================================================

elif False and page == "🔍 PII Discovery":
    st.title("🔍 PII Discovery")
    st.markdown("AI-powered detection of Personally Identifiable Information")

    # Filter options
    col1, col2 = st.columns([3, 1])

    with col1:
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            options=['HIGH', 'MEDIUM', 'LOW', 'NONE'],
            default=['HIGH', 'MEDIUM']
        )

    with col2:
        min_columns = st.number_input(
            "Min PII Columns",
            min_value=0,
            value=1,
            step=1
        )

    # Get PII tables
    pii_tables = get_high_risk_pii_tables()

    # Apply filters
    filtered_tables = pii_tables[
        (pii_tables['risk_level'].isin(risk_filter)) &
        (pii_tables['pii_columns_count'] >= min_columns)
    ]

    # Display summary
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tables with PII", len(filtered_tables))

    with col2:
        high_risk_count = len(filtered_tables[filtered_tables['risk_level'] == 'HIGH'])
        st.metric("High Risk Tables", high_risk_count)

    with col3:
        total_pii_cols = filtered_tables['pii_columns_count'].sum()
        st.metric("Total PII Columns", int(total_pii_cols))

    st.markdown("---")

    # Display table
    st.subheader("PII Tables")

    # Add search
    search_term = st.text_input("🔍 Search tables", placeholder="Enter table name...")

    if search_term:
        filtered_tables = filtered_tables[
            filtered_tables['full_table_name'].str.contains(search_term, case=False)
        ]

    # Format and display
    display_df = filtered_tables[[
        'full_table_name',
        'risk_level',
        'pii_columns_count',
        'avg_pii_score_pct',
        'pii_columns'
    ]].copy()

    display_df.columns = ['Table', 'Risk', 'PII Columns', 'Confidence %', 'PII Column Names']

    # Color-code risk levels
    def highlight_risk(row):
        if row['Risk'] == 'HIGH':
            return ['background-color: #ffcccc'] * len(row)
        elif row['Risk'] == 'MEDIUM':
            return ['background-color: #fff4cc'] * len(row)
        else:
            return [''] * len(row)

    styled_df = display_df.style.apply(highlight_risk, axis=1)

    st.dataframe(styled_df, use_container_width=True, height=600)

    # Export option
    st.markdown("---")
    col1, col2 = st.columns([1, 3])

    with col1:
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"pii_discovery_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


# ============================================================================
# Page: Table Search
# ============================================================================

elif page == "🔎 Table Search":
    st.title("🔎 AI-Powered Table Search")
    st.markdown("Ask questions in natural language about your Unity Catalog metadata")

    # Natural language search
    st.subheader("Natural Language Query")

    question = st.text_input(
        "Ask a question:",
        placeholder="Example: Find all tables related to customer data",
        help="Try asking about: table search, PII detection, similar tables, or table details"
    )

    if st.button("🔍 Search") and question:
        with st.spinner("Searching with AI..."):
            answer = agents['discovery'].query(question)

        st.markdown("---")
        st.subheader("Results")
        st.markdown(answer)

    # Quick search examples
    st.markdown("---")
    st.subheader("Quick Search Examples")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Find customer tables"):
            with st.spinner("Searching..."):
                answer = agents['discovery'].query("Find tables with customer in the name")
            st.markdown(answer)

        if st.button("🔒 Show PII tables"):
            with st.spinner("Searching..."):
                answer = agents['discovery'].query("Show tables with PII")
            st.markdown(answer)

    with col2:
        if st.button("📊 List gold layer tables"):
            with st.spinner("Searching..."):
                answer = agents['discovery'].query("Find tables in gold schema")
            st.markdown(answer)

        if st.button("🔗 Similar to dim_customer"):
            with st.spinner("Searching..."):
                answer = agents['discovery'].query("Find tables similar to dim_customer")
            st.markdown(answer)

    # Manual table lookup
    st.markdown("---")
    st.subheader("Direct Table Lookup")

    table_name = st.text_input(
        "Enter full table name:",
        placeholder="catalog.schema.table",
        help="Format: catalog.schema.table (e.g., wwi_databricks_uat.gold.dim_customer)"
    )

    if st.button("Get Details") and table_name:
        with st.spinner("Fetching details..."):
            details = agents['discovery'].get_table_details(table_name)

        if 'error' in details:
            st.error(details['error'])
        else:
            # Display table info
            st.markdown(f"### {table_name}")

            table_info = details['table']
            st.markdown(f"**Type:** {table_info['table_type']}")
            if table_info.get('comment'):
                st.markdown(f"**Description:** {table_info['comment']}")
            st.markdown(f"**Created:** {table_info.get('created', 'N/A')}")
            st.markdown(f"**Columns:** {details['column_count']}")

            # PII info
            if details.get('pii_info'):
                pii = details['pii_info']
                st.markdown("---")
                st.markdown("### 🔒 PII Detection")

                col1, col2, col3 = st.columns(3)
                with col1:
                    risk_color = {
                        'HIGH': '🔴',
                        'MEDIUM': '🟡',
                        'LOW': '🟢',
                        'NONE': '⚪'
                    }.get(pii['risk_level'], '⚪')
                    st.metric("Risk Level", f"{risk_color} {pii['risk_level']}")

                with col2:
                    st.metric("PII Columns", pii['pii_columns_count'])

                with col3:
                    st.metric("Confidence", f"{pii['avg_pii_score_pct']:.1f}%")

                if pii['pii_columns']:
                    st.markdown(f"**PII Columns:** {pii['pii_columns']}")

            # Columns table
            st.markdown("---")
            st.markdown("### Columns")

            columns_df = pd.DataFrame(details['columns'])
            st.dataframe(columns_df, use_container_width=True)


# ============================================================================
# Page: Growth Forecast - REMOVED (requires ML dataset)
# ============================================================================

elif False and page == "📈 Growth Forecast":
    st.title("📈 Table Growth Forecast")
    st.markdown("ARIMA-based predictions for future table creation trends")

    # Get forecast data
    forecast_df = get_table_growth_forecast()

    if not forecast_df.empty:
        # Create forecast visualization
        fig = go.Figure()

        # Predicted values
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_tables'],
            mode='lines',
            name='Predicted Tables',
            line=dict(color='blue', width=3)
        ))

        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['prediction_interval_upper_bound'],
            mode='lines',
            name='Upper Bound',
            line=dict(width=0),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['prediction_interval_lower_bound'],
            mode='lines',
            name='Lower Bound',
            line=dict(width=0),
            fillcolor='rgba(0, 100, 255, 0.2)',
            fill='tonexty',
            showlegend=True
        ))

        fig.update_layout(
            title='30-Day Table Growth Forecast',
            xaxis_title='Date',
            yaxis_title='Cumulative Tables',
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Forecast summary
        st.markdown("---")
        st.subheader("Forecast Summary")

        col1, col2, col3 = st.columns(3)

        current_tables = forecast_df.iloc[0]['predicted_tables']
        final_tables = forecast_df.iloc[-1]['predicted_tables']
        growth = final_tables - current_tables

        with col1:
            st.metric("Current Tables", f"{int(current_tables):,}")

        with col2:
            st.metric("Predicted (30 days)", f"{int(final_tables):,}")

        with col3:
            st.metric("Expected Growth", f"+{int(growth):,}", delta=f"+{(growth/current_tables*100):.1f}%")

        # Show forecast table
        st.markdown("---")
        st.subheader("Detailed Forecast Data")

        display_forecast = forecast_df.copy()
        display_forecast['predicted_tables'] = display_forecast['predicted_tables'].round(0).astype(int)
        display_forecast['prediction_interval_lower_bound'] = display_forecast['prediction_interval_lower_bound'].round(0).astype(int)
        display_forecast['prediction_interval_upper_bound'] = display_forecast['prediction_interval_upper_bound'].round(0).astype(int)

        st.dataframe(display_forecast, use_container_width=True)

    else:
        st.warning("No forecast data available. Ensure the ARIMA model has been trained with sufficient historical data.")


# ============================================================================
# Page: Anomalies - REMOVED (requires ML dataset)
# ============================================================================

elif False and page == "⚠️ Anomalies":
    st.title("⚠️ Schema Anomaly Detection")
    st.markdown("ML-powered detection of unusual schemas based on K-Means clustering")

    # Get anomalies
    anomalies = get_schema_anomalies()

    if not anomalies.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Anomalies", len(anomalies))

        with col2:
            high_count = len(anomalies[anomalies['anomaly_level'] == 'HIGH'])
            st.metric("High Severity", high_count)

        with col3:
            avg_score = anomalies['anomaly_score'].mean()
            st.metric("Avg Anomaly Score", f"{avg_score:.2f}")

        st.markdown("---")

        # Anomaly visualization
        st.subheader("Anomaly Scores")

        fig = px.bar(
            anomalies,
            x='table_schema',
            y='anomaly_score',
            color='anomaly_level',
            title='Schema Anomaly Scores',
            color_discrete_map={
                'HIGH': '#ff4444',
                'MEDIUM': '#ffaa00'
            },
            hover_data=['table_count']
        )

        st.plotly_chart(fig, use_container_width=True)

        # Anomaly table
        st.markdown("---")
        st.subheader("Detected Anomalies")

        display_anomalies = anomalies[[
            'table_catalog',
            'table_schema',
            'table_count',
            'anomaly_level',
            'anomaly_score'
        ]].copy()

        display_anomalies.columns = ['Catalog', 'Schema', 'Tables', 'Severity', 'Score']

        st.dataframe(display_anomalies, use_container_width=True)

        # Export
        st.markdown("---")
        csv = display_anomalies.to_csv(index=False)
        st.download_button(
            label="📥 Download Anomalies",
            data=csv,
            file_name=f"schema_anomalies_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    else:
        st.success("✅ No anomalies detected. All schemas appear normal.")


# ============================================================================
# Page: Compliance
# ============================================================================

elif page == "✅ Compliance":
    st.title("✅ Compliance Monitoring")
    st.markdown("Data governance compliance tracking and reporting")

    # Get compliance data
    compliance_score = agents['compliance'].get_compliance_score()
    high_risk_tables = agents['compliance'].get_high_risk_tables()
    undocumented = agents['compliance'].get_undocumented_tables(30)

    # Overall score
    st.subheader("Overall Compliance Score")

    score = compliance_score['overall_compliance_score']

    col1, col2 = st.columns([1, 3])

    with col1:
        # Score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Compliance Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 75], 'color': "gray"},
                    {'range': [75, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Key Metrics")

        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            st.metric("Total Tables", compliance_score['total_tables'])
            st.metric("Tables with PII", compliance_score['tables_with_pii'])

        with metric_col2:
            st.metric("Documentation Rate", f"{compliance_score['documentation_pct']:.1f}%")
            st.metric("High Risk Tables", compliance_score['high_risk_tables'])

    # High risk tables
    st.markdown("---")
    st.subheader("🔴 High Risk Tables Requiring Attention")

    if high_risk_tables:
        risk_df = pd.DataFrame(high_risk_tables)
        display_risk = risk_df[[
            'full_table_name',
            'risk_level',
            'pii_columns_count',
            'undocumented'
        ]].head(20)

        display_risk.columns = ['Table', 'Risk', 'PII Columns', 'Undocumented']
        display_risk['Undocumented'] = display_risk['Undocumented'].map({True: '❌', False: '✓'})

        st.dataframe(display_risk, use_container_width=True)

    # Undocumented tables
    st.markdown("---")
    st.subheader("📝 Undocumented Tables")

    if undocumented:
        undoc_df = pd.DataFrame(undocumented)
        display_undoc = undoc_df[['full_name', 'table_type', 'created']].head(20)
        display_undoc.columns = ['Table', 'Type', 'Created']

        st.dataframe(display_undoc, use_container_width=True)

        st.info(f"💡 {len(undocumented)} tables found without documentation. Use the Documentation page to generate AI descriptions.")

    # Generate compliance report
    st.markdown("---")
    if st.button("📄 Generate Full Compliance Report"):
        with st.spinner("Generating AI-powered compliance report..."):
            report = agents['compliance'].generate_compliance_report()

        st.markdown("### Compliance Report")
        st.markdown(report)


# ============================================================================
# Page: Documentation
# ============================================================================

elif page == "📝 Documentation":
    st.title("📝 AI Auto-Documentation")
    st.markdown("Generate descriptions for tables and columns using AI")

    # Table description generator
    st.subheader("Generate Table Description")

    table_name = st.text_input(
        "Enter full table name:",
        placeholder="catalog.schema.table",
        key="doc_table_name"
    )

    if st.button("✨ Generate Description") and table_name:
        with st.spinner("Generating AI description..."):
            description = agents['documentation'].generate_table_description(table_name)

        st.markdown("---")
        st.subheader("Generated Description")
        st.success(description)

        # Copy button
        st.code(description, language=None)

    # Data dictionary generator
    st.markdown("---")
    st.subheader("Generate Data Dictionary for Schema")

    schema_name = st.text_input(
        "Enter schema name:",
        placeholder="e.g., gold",
        key="doc_schema_name"
    )

    if st.button("📚 Generate Data Dictionary") and schema_name:
        with st.spinner("Generating data dictionary... This may take a few minutes for large schemas."):
            try:
                dictionary_df = agents['documentation'].generate_data_dictionary(schema_name)

                st.markdown("---")
                st.subheader(f"Data Dictionary: {schema_name}")

                st.dataframe(dictionary_df, use_container_width=True)

                # Download option
                csv = dictionary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data Dictionary",
                    data=csv,
                    file_name=f"data_dictionary_{schema_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"Error generating data dictionary: {str(e)}")

    # Documentation statistics
    st.markdown("---")
    st.subheader("Documentation Statistics")

    query = f"""
    SELECT
        schema_name,
        COUNT(*) as total_tables,
        SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) as documented_tables,
        ROUND(100.0 * SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) as documentation_pct
    FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
    GROUP BY schema_name
    ORDER BY documentation_pct DESC
    """

    doc_stats = run_query(query)

    if not doc_stats.empty:
        fig = px.bar(
            doc_stats,
            x='schema_name',
            y='documentation_pct',
            title='Documentation Rate by Schema',
            color='documentation_pct',
            color_continuous_scale='Greens'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(doc_stats, use_container_width=True)


# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p><strong>🌊 SyncFlow - Data Engineering Excellence</strong></p>
        <p>Powered by Fivetran • Databricks Unity Catalog • Google Cloud</p>
        <p style='font-size: 0.9em; margin-top: 10px;'>
            🤖 Google Gemini 2.5 Flash
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
