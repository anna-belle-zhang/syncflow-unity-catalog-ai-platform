"""
🌊 SyncFlow AI Governance Platform
Gemini AI Agents Implementation

This module implements AI agents using Google Gemini 2.5 Flash for:
1. Data Discovery - Natural language search over Unity Catalog metadata
2. PII Detection - Automated detection of sensitive data
3. Auto Documentation - AI-generated table and column descriptions
4. Compliance Monitoring - Governance scoring and reporting
"""

import json
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
import google.generativeai as genai
import pandas as pd


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ID = "YOUR_GCP_PROJECT_ID"
METADATA_DATASET = "unity_catalog_metadata"
ML_DATASET = "ml_models"

# Configure Gemini API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini 2.5 Flash model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)


# ============================================================================
# Agent 1: Data Discovery Agent
# ============================================================================

class DataDiscoveryAgent:
    """
    AI Agent for natural language data discovery over Unity Catalog metadata.

    Powered by Google Gemini 2.5 Flash

    Features:
    - Search tables by keyword
    - Find tables by schema/catalog
    - Get detailed table information
    - Find similar tables
    - Check PII status
    """

    def __init__(self):
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.model = model  # Gemini 2.5 Flash

        # Define tools for the agent
        self.tools = [
            self.search_tables_by_keyword,
            self.search_tables_by_schema,
            self.get_table_details,
            self.find_similar_tables,
            self.check_pii_status
        ]

    def search_tables_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Search for tables matching a keyword in name or comment"""
        query = f"""
        SELECT
            catalog_name,
            schema_name,
            table_name,
            full_name,
            table_type,
            comment,
            _fivetran_synced as last_synced
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        WHERE LOWER(table_name) LIKE '%{keyword.lower()}%'
           OR LOWER(COALESCE(comment, '')) LIKE '%{keyword.lower()}%'
        LIMIT {limit}
        """

        results = self.bq_client.query(query).to_dataframe()
        return results.to_dict('records')

    def search_tables_by_schema(self, schema_name: str) -> List[Dict]:
        """Get all tables in a specific schema"""
        query = f"""
        SELECT
            catalog_name,
            schema_name,
            table_name,
            full_name,
            table_type,
            comment
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        WHERE schema_name = '{schema_name}'
        ORDER BY table_name
        """

        results = self.bq_client.query(query).to_dataframe()
        return results.to_dict('records')

    def get_table_details(self, full_table_name: str) -> Dict:
        """Get detailed information about a specific table including columns and PII status"""

        # Parse table name
        parts = full_table_name.split('.')
        if len(parts) != 3:
            return {"error": "Invalid table name format. Use: catalog.schema.table"}

        catalog, schema, table = parts

        # Get table metadata
        table_query = f"""
        SELECT
            catalog_name,
            schema_name,
            table_name,
            table_type,
            comment,
            created_at as created,
            _fivetran_synced as last_synced
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        WHERE catalog_name = '{catalog}'
          AND schema_name = '{schema}'
          AND table_name = '{table}'
        """

        table_info = self.bq_client.query(table_query).to_dataframe()
        if table_info.empty:
            return {"error": f"Table {full_table_name} not found"}

        # Get columns
        columns_query = f"""
        SELECT
            column_name,
            data_type,
            nullable as is_nullable,
            position as ordinal_position,
            comment
        FROM `{PROJECT_ID}.{METADATA_DATASET}.columns`
        WHERE table_full_name = '{full_table_name}'
        ORDER BY position
        """

        columns = self.bq_client.query(columns_query).to_dataframe()

        # Get PII status
        pii_query = f"""
        SELECT
            pii_columns_count,
            pii_columns,
            risk_level,
            avg_pii_score_pct
        FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table`
        WHERE table_catalog = '{catalog}'
          AND table_schema = '{schema}'
          AND table_name = '{table}'
        """

        pii_info = self.bq_client.query(pii_query).to_dataframe()

        return {
            "table": table_info.to_dict('records')[0],
            "columns": columns.to_dict('records'),
            "pii_info": pii_info.to_dict('records')[0] if not pii_info.empty else None,
            "column_count": len(columns)
        }

    def find_similar_tables(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Find tables with similar characteristics using ML clustering"""

        try:
            query = f"""
            WITH target_cluster AS (
                SELECT cluster_id
                FROM `{PROJECT_ID}.{ML_DATASET}.table_clusters`
                WHERE LOWER(table_name) = LOWER('{table_name}')
                LIMIT 1
            )

            SELECT
                tc.full_name,
                tc.cluster_name,
                tc.column_count,
                tc.pii_columns,
                tc.cluster_distance
            FROM `{PROJECT_ID}.{ML_DATASET}.table_clusters` tc
            CROSS JOIN target_cluster t
            WHERE tc.cluster_id = t.cluster_id
              AND LOWER(tc.table_name) != LOWER('{table_name}')
            ORDER BY tc.cluster_distance
            LIMIT {limit}
            """

            results = self.bq_client.query(query).to_dataframe()
            return results.to_dict('records')
        except Exception:
            # Return empty list if ML dataset doesn't exist
            return []

    def check_pii_status(self, schema_name: Optional[str] = None) -> List[Dict]:
        """Check PII status across tables, optionally filtered by schema"""

        try:
            where_clause = f"WHERE table_schema = '{schema_name}'" if schema_name else ""

            query = f"""
            SELECT
                full_table_name,
                pii_columns_count,
                pii_columns,
                risk_level,
                avg_pii_score_pct
            FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table`
            {where_clause}
            ORDER BY pii_columns_count DESC
            LIMIT 20
            """

            results = self.bq_client.query(query).to_dataframe()
            return results.to_dict('records')
        except Exception:
            # Return empty list if ML dataset doesn't exist
            return []

    def query(self, user_question: str) -> str:
        """
        Process a natural language question about the Unity Catalog metadata.

        Example questions:
        - "Find all tables related to customer data"
        - "Show me tables with PII in the sales schema"
        - "What tables are similar to dim_customer?"
        - "List all tables in the gold layer"
        """

        # Create context from available tools
        tools_description = """
        You have access to the following tools for querying Unity Catalog metadata:

        1. search_tables_by_keyword(keyword, limit): Search tables by name or description
        2. search_tables_by_schema(schema_name): Get all tables in a schema
        3. get_table_details(full_table_name): Get detailed info about a table (format: catalog.schema.table)
        4. find_similar_tables(table_name, limit): Find similar tables using ML clustering
        5. check_pii_status(schema_name): Check PII detection results

        Analyze the user's question and use the appropriate tool(s) to answer it.
        """

        # Generate response with Gemini
        prompt = f"""
        {tools_description}

        User question: {user_question}

        Think step by step:
        1. What information is the user looking for?
        2. Which tool(s) should be used?
        3. What are the appropriate parameters?

        Provide a helpful, conversational answer based on the Unity Catalog metadata.
        """

        # For this implementation, we'll use simple keyword matching
        # In production, you'd use the Reasoning Engine with function calling

        question_lower = user_question.lower()

        if 'pii' in question_lower or 'sensitive' in question_lower:
            schema = None
            if 'in' in question_lower:
                # Try to extract schema name
                words = user_question.split()
                if 'in' in words:
                    idx = words.index('in')
                    if idx + 1 < len(words):
                        schema = words[idx + 1].strip('?.,')

            results = self.check_pii_status(schema)
            return self._format_pii_results(results)

        elif 'similar' in question_lower:
            # Extract table name
            words = user_question.split()
            for i, word in enumerate(words):
                if word.lower() in ['to', 'like']:
                    if i + 1 < len(words):
                        table_name = words[i + 1].strip('?.,')
                        results = self.find_similar_tables(table_name)
                        return self._format_similar_tables(results, table_name)

        elif 'details' in question_lower or 'about' in question_lower:
            # Look for table name (format: catalog.schema.table)
            words = user_question.split()
            for word in words:
                if '.' in word and word.count('.') == 2:
                    table_name = word.strip('?.,')
                    result = self.get_table_details(table_name)
                    return self._format_table_details(result)

        else:
            # Default to keyword search
            keywords = [w for w in user_question.split() if len(w) > 3 and w.lower() not in ['table', 'tables', 'find', 'show', 'list', 'what', 'where']]
            if keywords:
                keyword = keywords[0]
                results = self.search_tables_by_keyword(keyword)
                return self._format_search_results(results, keyword)

        return "I'm not sure how to answer that question. Try asking about: table search, PII detection, similar tables, or table details."

    def _format_search_results(self, results: List[Dict], keyword: str) -> str:
        if not results:
            return f"No tables found matching '{keyword}'"

        output = f"Found {len(results)} tables matching '{keyword}':\n\n"
        for r in results:
            output += f"• {r['full_name']} ({r['table_type']})\n"
            if r.get('comment'):
                output += f"  Description: {r['comment']}\n"

        return output

    def _format_pii_results(self, results: List[Dict]) -> str:
        if not results:
            return "No tables with PII detected."

        output = f"Found {len(results)} tables with PII:\n\n"
        for r in results:
            output += f"• {r['full_table_name']}\n"
            output += f"  Risk Level: {r['risk_level']}\n"
            output += f"  PII Columns ({r['pii_columns_count']}): {r['pii_columns']}\n"
            output += f"  Confidence: {r['avg_pii_score_pct']}%\n\n"

        return output

    def _format_similar_tables(self, results: List[Dict], original_table: str) -> str:
        if not results:
            return f"No similar tables found for '{original_table}'"

        output = f"Tables similar to '{original_table}':\n\n"
        for r in results:
            output += f"• {r['full_name']}\n"
            output += f"  Cluster: {r['cluster_name']}\n"
            output += f"  Columns: {r['column_count']}, PII Columns: {r['pii_columns']}\n\n"

        return output

    def _format_table_details(self, result: Dict) -> str:
        if 'error' in result:
            return result['error']

        table = result['table']
        columns = result['columns']
        pii = result.get('pii_info')

        output = f"Table: {table['catalog_name']}.{table['schema_name']}.{table['table_name']}\n\n"
        output += f"Type: {table['table_type']}\n"
        if table.get('comment'):
            output += f"Description: {table['comment']}\n"
        output += f"Created: {table.get('created', 'N/A')}\n"
        output += f"Columns: {result['column_count']}\n\n"

        if pii:
            output += f"PII Detection:\n"
            output += f"  Risk Level: {pii['risk_level']}\n"
            output += f"  PII Columns: {pii['pii_columns_count']}\n"
            output += f"  Affected: {pii['pii_columns']}\n\n"

        output += "Columns:\n"
        for col in columns[:20]:  # Show first 20 columns
            nullable_flag = col['is_nullable']
            output += f"  • {col['column_name']} ({col['data_type']})"
            if nullable_flag == False or str(nullable_flag).upper() == 'NO':
                output += " NOT NULL"
            output += "\n"

        if len(columns) > 20:
            output += f"  ... and {len(columns) - 20} more columns\n"

        return output


# ============================================================================
# Agent 2: Compliance Guardian Agent
# ============================================================================

class ComplianceGuardianAgent:
    """
    AI Agent for monitoring compliance and data governance policies.

    Powered by Google Gemini 2.5 Flash

    Features:
    - Monitor PII exposure across catalogs
    - Track undocumented tables
    - Identify high-risk data assets
    - Generate compliance reports
    """

    def __init__(self):
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.model = model  # Gemini 2.5 Flash

    def get_compliance_score(self) -> Dict:
        """Calculate overall compliance score"""

        try:
            query = f"""
            WITH metrics AS (
                SELECT
                    -- Total tables
                    (SELECT COUNT(*) FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`) as total_tables,

                    -- Tables with PII
                    (SELECT COUNT(*) FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table`
                     WHERE pii_columns_count > 0) as tables_with_pii,

                    -- High risk tables
                    (SELECT COUNT(*) FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table`
                     WHERE risk_level = 'HIGH') as high_risk_tables,

                    -- Documented tables
                    (SELECT COUNT(*) FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
                     WHERE comment IS NOT NULL) as documented_tables
            )

            SELECT
                *,
                ROUND(100.0 * documented_tables / NULLIF(total_tables, 0), 2) as documentation_pct,
                ROUND(100.0 * high_risk_tables / NULLIF(tables_with_pii, 0), 2) as high_risk_pct
            FROM metrics
            """

            result = self.bq_client.query(query).to_dataframe().to_dict('records')[0]
        except Exception:
            # Fallback query without ML dataset
            query = f"""
            SELECT
                COUNT(*) as total_tables,
                0 as tables_with_pii,
                0 as high_risk_tables,
                SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) as documented_tables,
                ROUND(100.0 * SUM(CASE WHEN comment IS NOT NULL THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) as documentation_pct,
                0.0 as high_risk_pct
            FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
            """
            result = self.bq_client.query(query).to_dataframe().to_dict('records')[0]

        # Calculate overall score (0-100)
        doc_score = result['documentation_pct'] * 0.4
        risk_score = max(0, 100 - result.get('high_risk_pct', 0)) * 0.6
        overall_score = doc_score + risk_score

        result['overall_compliance_score'] = round(overall_score, 2)

        return result

    def get_high_risk_tables(self) -> List[Dict]:
        """Get list of high-risk tables requiring attention"""

        try:
            query = f"""
            SELECT
                t.table_catalog,
                t.table_schema,
                t.table_name,
                t.full_table_name,
                t.pii_columns_count,
                t.pii_columns,
                t.risk_level,
                t.avg_pii_score_pct,
                CASE WHEN tm.comment IS NULL THEN TRUE ELSE FALSE END as undocumented,
                tm._fivetran_synced as last_synced
            FROM `{PROJECT_ID}.{ML_DATASET}.pii_summary_by_table` t
            LEFT JOIN `{PROJECT_ID}.{METADATA_DATASET}.tables` tm
                ON t.table_catalog = tm.catalog_name
                AND t.table_schema = tm.schema_name
                AND t.table_name = tm.table_name
            WHERE t.risk_level IN ('HIGH', 'MEDIUM')
            ORDER BY
                CASE t.risk_level WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
                t.pii_columns_count DESC
            """

            results = self.bq_client.query(query).to_dataframe()
            return results.to_dict('records')
        except Exception:
            # Return empty list if ML dataset doesn't exist
            return []

    def get_undocumented_tables(self, limit: int = 50) -> List[Dict]:
        """Find tables without documentation"""

        query = f"""
        SELECT
            catalog_name,
            schema_name,
            table_name,
            full_name,
            table_type,
            created_at as created,
            _fivetran_synced as last_synced
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        WHERE comment IS NULL OR comment = ''
        ORDER BY created_at DESC
        LIMIT {limit}
        """

        results = self.bq_client.query(query).to_dataframe()
        return results.to_dict('records')

    def generate_compliance_report(self) -> str:
        """Generate a comprehensive compliance report"""

        score_data = self.get_compliance_score()
        high_risk = self.get_high_risk_tables()
        undocumented = self.get_undocumented_tables(20)

        # Use Gemini to generate narrative report
        prompt = f"""
        Generate a compliance report based on this data governance analysis:

        Overall Metrics:
        - Total Tables: {score_data['total_tables']}
        - Tables with PII: {score_data['tables_with_pii']}
        - High Risk Tables: {score_data['high_risk_tables']}
        - Documentation Rate: {score_data['documentation_pct']}%
        - Overall Compliance Score: {score_data['overall_compliance_score']}/100

        High Risk Tables: {len(high_risk)} found
        Undocumented Tables: {len(undocumented)} found

        Create a professional compliance report with:
        1. Executive Summary
        2. Key Findings
        3. Risk Assessment
        4. Recommendations
        5. Action Items

        Use a professional, data-driven tone.
        """

        response = self.model.generate_content(prompt)
        return response.text


# ============================================================================
# Agent 3: Auto Documentation Agent
# ============================================================================

class AutoDocumentationAgent:
    """
    AI Agent for automatically generating table and column descriptions.

    Powered by Google Gemini 2.5 Flash

    Features:
    - Generate table descriptions from column names and types
    - Suggest business-friendly names
    - Create data dictionaries
    - Infer table purposes
    """

    def __init__(self):
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.model = model  # Gemini 2.5 Flash

    def generate_table_description(self, full_table_name: str) -> str:
        """Generate AI description for a table based on its structure"""

        # Get table details
        parts = full_table_name.split('.')
        if len(parts) != 3:
            return "Error: Invalid table name format"

        catalog, schema, table = parts

        # Get column information
        query = f"""
        SELECT
            column_name,
            data_type,
            comment
        FROM `{PROJECT_ID}.{METADATA_DATASET}.columns`
        WHERE table_full_name = '{full_table_name}'
        ORDER BY position
        """

        columns = self.bq_client.query(query).to_dataframe()

        if columns.empty:
            return "Error: Table not found"

        # Build context for Gemini
        column_info = "\n".join([
            f"- {row['column_name']} ({row['data_type']})"
            for _, row in columns.iterrows()
        ])

        prompt = f"""
        Generate a clear, concise description for this database table:

        Table: {full_table_name}
        Schema: {schema}

        Columns:
        {column_info}

        Analyze the column names and types to infer:
        1. What business entity or concept this table represents
        2. The table's purpose in the data architecture
        3. Key information stored

        Provide a 2-3 sentence description that would be helpful for:
        - Data analysts searching for data
        - Business users understanding available data
        - Data governance documentation

        Format: Professional, clear, and business-focused.
        """

        response = self.model.generate_content(prompt)
        return response.text

    def generate_column_description(self, full_table_name: str, column_name: str) -> str:
        """Generate AI description for a specific column"""

        parts = full_table_name.split('.')
        if len(parts) != 3:
            return "Error: Invalid table name format"

        catalog, schema, table = parts

        # Get column info and surrounding context
        query = f"""
        SELECT
            column_name,
            data_type,
            nullable as is_nullable,
            comment
        FROM `{PROJECT_ID}.{METADATA_DATASET}.columns`
        WHERE table_full_name = '{full_table_name}'
        ORDER BY position
        """

        columns = self.bq_client.query(query).to_dataframe()

        if columns.empty:
            return "Error: Table not found"

        target_column = columns[columns['column_name'] == column_name]
        if target_column.empty:
            return "Error: Column not found"

        col_info = target_column.iloc[0]

        prompt = f"""
        Generate a clear description for this database column:

        Table: {full_table_name}
        Column: {column_name}
        Data Type: {col_info['data_type']}
        Nullable: {col_info['is_nullable']}

        Context - Other columns in this table:
        {', '.join(columns['column_name'].tolist())}

        Provide a 1-2 sentence description explaining:
        - What this column represents
        - How it might be used
        - Any important characteristics

        Format: Clear, concise, business-focused.
        """

        response = self.model.generate_content(prompt)
        return response.text

    def generate_data_dictionary(self, schema_name: str) -> pd.DataFrame:
        """Generate a complete data dictionary for a schema"""

        # Get all tables in schema
        tables_query = f"""
        SELECT DISTINCT
            catalog_name,
            schema_name,
            table_name,
            full_name
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        WHERE schema_name = '{schema_name}'
        ORDER BY table_name
        """

        tables = self.bq_client.query(tables_query).to_dataframe()

        dictionary_data = []

        for _, table_row in tables.iterrows():
            full_name = table_row['full_name']

            # Generate table description
            table_desc = self.generate_table_description(full_name)

            # Get columns
            columns_query = f"""
            SELECT column_name, data_type, nullable
            FROM `{PROJECT_ID}.{METADATA_DATASET}.columns`
            WHERE table_full_name = '{full_name}'
            ORDER BY position
            """

            columns = self.bq_client.query(columns_query).to_dataframe()

            for _, col_row in columns.iterrows():
                dictionary_data.append({
                    'table_name': table_row['table_name'],
                    'table_description': table_desc,
                    'column_name': col_row['column_name'],
                    'data_type': col_row['data_type'],
                    'nullable': col_row['nullable'],
                    'full_table_name': full_name
                })

        return pd.DataFrame(dictionary_data)


# ============================================================================
# Agent 4: Data Quality Monitor Agent
# ============================================================================

class DataQualityMonitorAgent:
    """
    AI Agent for monitoring data quality and detecting issues.

    Powered by Google Gemini 2.5 Flash

    Features:
    - Detect schema anomalies
    - Monitor metadata freshness
    - Identify quality issues
    - Generate alerts
    """

    def __init__(self):
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.model = model  # Gemini 2.5 Flash

    def get_schema_anomalies(self) -> List[Dict]:
        """Get list of schemas with anomalous characteristics"""

        try:
            query = f"""
            SELECT
                table_catalog,
                table_schema,
                table_count,
                total_columns,
                anomaly_level,
                anomaly_score,
                CENTROID_ID as cluster_id
            FROM `{PROJECT_ID}.{ML_DATASET}.schema_anomalies`
            WHERE anomaly_level IN ('HIGH', 'MEDIUM')
            ORDER BY anomaly_score DESC
            """

            results = self.bq_client.query(query).to_dataframe()
            return results.to_dict('records')
        except Exception:
            # Return empty list if ML dataset doesn't exist
            return []

    def check_metadata_freshness(self) -> Dict:
        """Check how fresh the synced metadata is"""

        query = f"""
        SELECT
            MIN(_fivetran_synced) as oldest_sync,
            MAX(_fivetran_synced) as latest_sync,
            TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_fivetran_synced), MINUTE) as minutes_since_sync,
            COUNT(DISTINCT catalog_name) as catalogs_synced,
            COUNT(*) as tables_synced
        FROM `{PROJECT_ID}.{METADATA_DATASET}.tables`
        """

        result = self.bq_client.query(query).to_dataframe().to_dict('records')[0]

        # Add freshness status
        minutes = result['minutes_since_sync']
        if minutes < 20:
            result['freshness_status'] = 'FRESH'
        elif minutes < 60:
            result['freshness_status'] = 'ACCEPTABLE'
        else:
            result['freshness_status'] = 'STALE'

        return result

    def generate_quality_report(self) -> str:
        """Generate data quality monitoring report"""

        anomalies = self.get_schema_anomalies()
        freshness = self.check_metadata_freshness()

        prompt = f"""
        Generate a data quality monitoring report:

        Metadata Freshness:
        - Last Sync: {freshness['minutes_since_sync']} minutes ago
        - Status: {freshness['freshness_status']}
        - Catalogs: {freshness['catalogs_synced']}
        - Tables: {freshness['tables_synced']}

        Schema Anomalies Detected: {len(anomalies)}

        Create a concise report with:
        1. Overall Status
        2. Issues Found
        3. Recommended Actions

        Use a monitoring/operational tone.
        """

        response = self.model.generate_content(prompt)
        return response.text


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🌊 SyncFlow AI Governance Platform - Gemini 2.5 Flash Agents")
    print("=" * 80)
    print()

    # Initialize agents
    print("Initializing agents...")
    discovery_agent = DataDiscoveryAgent()
    compliance_agent = ComplianceGuardianAgent()
    documentation_agent = AutoDocumentationAgent()
    quality_agent = DataQualityMonitorAgent()
    print("✓ All agents initialized\n")

    # Example 1: Data Discovery
    print("=" * 80)
    print("Example 1: Data Discovery Agent")
    print("=" * 80)

    question = "Find tables with customer data"
    print(f"Question: {question}\n")
    answer = discovery_agent.query(question)
    print(answer)
    print()

    # Example 2: Compliance Monitoring
    print("=" * 80)
    print("Example 2: Compliance Guardian Agent")
    print("=" * 80)

    score = compliance_agent.get_compliance_score()
    print(f"Overall Compliance Score: {score['overall_compliance_score']}/100")
    print(f"Documentation Rate: {score['documentation_pct']}%")
    print(f"High Risk Tables: {score['high_risk_tables']}")
    print()

    # Example 3: Auto Documentation
    print("=" * 80)
    print("Example 3: Auto Documentation Agent")
    print("=" * 80)

    # This would generate description for a specific table
    # Uncomment and provide a real table name:
    # description = documentation_agent.generate_table_description("wwi_databricks_uat.gold.dim_customer")
    # print(description)
    print("Ready to generate descriptions for any table in Unity Catalog")
    print()

    # Example 4: Quality Monitoring
    print("=" * 80)
    print("Example 4: Data Quality Monitor Agent")
    print("=" * 80)

    freshness = quality_agent.check_metadata_freshness()
    print(f"Metadata Freshness: {freshness['freshness_status']}")
    print(f"Last Sync: {freshness['minutes_since_sync']} minutes ago")
    print(f"Tables Synced: {freshness['tables_synced']}")
    print()

    print("=" * 80)
    print("All agents operational and ready!")
    print("=" * 80)
