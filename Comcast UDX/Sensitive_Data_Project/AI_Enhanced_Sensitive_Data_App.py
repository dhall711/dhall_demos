"""
🤖 AI-Enhanced Snowflake Sensitive Data Discovery & Masking
Powered by Snowflake Cortex AI and Intelligence

A comprehensive single-file Streamlit application that leverages Snowflake's 
native AI capabilities for intelligent sensitive data discovery and masking policy recommendations.
"""

import streamlit as st
import pandas as pd
import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Set page configuration
st.set_page_config(
    page_title="🤖 AI-Enhanced Snowflake Sensitive Data Discovery & Masking",
    page_icon="🔒",
    layout="wide"
)

# Global configuration
DEFAULT_AI_MODEL = 'mistral-large'
BATCH_SIZE = 3
MAX_SAMPLE_SIZE = 10
MAX_TEXT_LENGTH = 2000

@dataclass
class AIAnalysisResult:
    """Result structure for AI analysis"""
    is_sensitive: bool
    confidence: float
    sensitive_type: str
    reasoning: str
    source: str
    raw_response: str = ""

class CortexAIEngine:
    """
    Snowflake Cortex AI Engine for intelligent data analysis
    Primary recommendation engine using native Snowflake AI capabilities
    """
    
    def __init__(self, connection, ai_model: str = DEFAULT_AI_MODEL):
        self.connection = connection
        self.ai_model = ai_model
        
    def _safe_ai_query(self, query: str, operation_name: str) -> Optional[Dict[str, Any]]:
        """Safely execute AI query with error handling"""
        try:
            result = self.connection.query(query)
            if not result.empty:
                return result.iloc[0].to_dict()
            return None
        except Exception as e:
            st.warning(f"❌ AI {operation_name} error: {str(e)}")
            return None
    
    def classify_column_sensitivity(self, sample_data: List[str], column_name: str, 
                                   table_context: str = "") -> AIAnalysisResult:
        """
        Use Snowflake Cortex CLASSIFY_TEXT for intelligent column sensitivity classification
        """
        if not sample_data:
            return AIAnalysisResult(
                is_sensitive=False, confidence=0.0, sensitive_type="Unknown",
                reasoning="No sample data available", source="NO_DATA"
            )
        
        try:
            # Prepare sample data (limit to avoid token limits)
            sample_text = " | ".join([str(val) for val in sample_data[:MAX_SAMPLE_SIZE] if val is not None])
            
            if len(sample_text) > MAX_TEXT_LENGTH:
                sample_text = sample_text[:MAX_TEXT_LENGTH] + "..."
            
            # Escape single quotes for SQL
            safe_sample_text = sample_text.replace("'", "''")
            
            # Use Cortex CLASSIFY_TEXT for sensitivity classification
            classification_query = f"""
            SELECT SNOWFLAKE.CORTEX.CLASSIFY_TEXT(
                '{safe_sample_text}', 
                ['PII', 'Financial', 'Medical', 'Personal_Identifier', 'Public', 'Confidential', 'Address', 'Contact_Info']
            ) as classification_result
            """
            
            result = self._safe_ai_query(classification_query, "sensitivity classification")
            if result:
                classification = result.get('CLASSIFICATION_RESULT', 'Public')
                
                # Map classifications to sensitivity
                sensitive_classifications = ['PII', 'Financial', 'Medical', 'Personal_Identifier', 'Confidential', 'Address', 'Contact_Info']
                is_sensitive = classification in sensitive_classifications
                confidence = 0.9 if is_sensitive else 0.2
                
                return AIAnalysisResult(
                    is_sensitive=is_sensitive,
                    confidence=confidence,
                    sensitive_type=classification,
                    reasoning=f"Cortex AI classified as: {classification}",
                    source="CORTEX_CLASSIFY_TEXT",
                    raw_response=classification
                )
                
        except Exception as e:
            st.warning(f"⚠️ AI Classification error: {str(e)}")
            
        return AIAnalysisResult(
            is_sensitive=False, confidence=0.0, sensitive_type="Error",
            reasoning="AI classification failed", source="ERROR"
        )
    
    def analyze_semantic_context(self, column_name: str, table_name: str, 
                                sample_data: List[str], column_comment: str = "") -> AIAnalysisResult:
        """
        Use Snowflake Cortex COMPLETE for deep semantic analysis
        """
        if not sample_data:
            return AIAnalysisResult(
                is_sensitive=False, confidence=0.0, sensitive_type="Unknown",
                reasoning="No sample data for analysis", source="NO_DATA"
            )
        
        try:
            # Create structured analysis prompt
            sample_preview = ', '.join([str(val) for val in sample_data[:5] if val is not None])
            if len(sample_preview) > 500:
                sample_preview = sample_preview[:500] + "..."
                
            context_prompt = f"""Analyze this Snowflake database column for sensitive data:

COLUMN DETAILS:
- Column Name: {column_name}
- Table: {table_name}
- Comment: {column_comment or 'No description provided'}
- Sample Values: {sample_preview}

ANALYSIS REQUIREMENTS:
1. Determine if this column contains sensitive data (yes/no)
2. Classify the type of sensitive data if applicable
3. Assign confidence score (0.0 to 1.0)
4. Provide brief reasoning (max 100 words)

RESPONSE FORMAT (JSON):
{{"is_sensitive": boolean, "data_type": "string", "confidence": float, "reasoning": "string"}}

Consider data privacy regulations (GDPR, CCPA), common PII patterns, and business context."""

            # Escape quotes for SQL
            safe_prompt = context_prompt.replace("'", "''")
            
            analysis_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{self.ai_model}', 
                '{safe_prompt}'
            ) as ai_analysis
            """
            
            result = self._safe_ai_query(analysis_query, "semantic analysis")
            if result:
                ai_response = result.get('AI_ANALYSIS', '')
                
                try:
                    # Try to parse JSON response
                    analysis = json.loads(ai_response)
                    return AIAnalysisResult(
                        is_sensitive=bool(analysis.get('is_sensitive', False)),
                        confidence=float(analysis.get('confidence', 0.5)),
                        sensitive_type=str(analysis.get('data_type', 'General')),
                        reasoning=str(analysis.get('reasoning', 'AI analysis completed')),
                        source="CORTEX_COMPLETE_JSON",
                        raw_response=ai_response
                    )
                except (json.JSONDecodeError, ValueError):
                    # Parse text response for key indicators
                    is_sensitive = any(word in ai_response.lower() 
                                     for word in ['sensitive', 'pii', 'personal', 'confidential', 'private'])
                    confidence = 0.6 if is_sensitive else 0.3
                    reasoning = ai_response[:200] + "..." if len(ai_response) > 200 else ai_response
                    
                    return AIAnalysisResult(
                        is_sensitive=is_sensitive,
                        confidence=confidence,
                        sensitive_type="AI_Detected" if is_sensitive else "Public",
                        reasoning=reasoning,
                        source="CORTEX_COMPLETE_TEXT",
                        raw_response=ai_response
                    )
                    
        except Exception as e:
            st.warning(f"⚠️ AI Semantic Analysis error: {str(e)}")
            
        return AIAnalysisResult(
            is_sensitive=False, confidence=0.0, sensitive_type="Error",
            reasoning="AI semantic analysis failed", source="ERROR"
        )
    
    def generate_masking_recommendation(self, sensitive_type: str, column_name: str, 
                                      data_type: str, business_context: str = "") -> Dict[str, Any]:
        """
        Use Snowflake Cortex AI to generate intelligent masking policy recommendations
        """
        try:
            policy_prompt = f"""Generate a Snowflake Dynamic Data Masking policy recommendation:

COLUMN CONTEXT:
- Column Name: {column_name}
- Data Type: {data_type}
- Sensitive Classification: {sensitive_type}
- Business Context: {business_context or 'General business application'}

REQUIREMENTS:
1. Recommend appropriate masking strategy (full/partial/format-preserving/conditional)
2. Suggest role-based access control considerations
3. Provide specific SQL masking expression
4. Consider compliance requirements (GDPR, CCPA, etc.)

RESPONSE FORMAT:
Strategy: [strategy type]
Roles: [recommended role access]
SQL: [specific masking expression]
Compliance: [relevant considerations]
Reasoning: [brief explanation]

Keep response practical and implementable in Snowflake."""

            safe_prompt = policy_prompt.replace("'", "''")
            
            policy_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{self.ai_model}',
                '{safe_prompt}'
            ) as policy_recommendation
            """
            
            result = self._safe_ai_query(policy_query, "masking policy generation")
            if result:
                recommendation = result.get('POLICY_RECOMMENDATION', '')
                return {
                    'recommendation': recommendation,
                    'source': 'CORTEX_MASKING_POLICY',
                    'success': True
                }
                
        except Exception as e:
            st.warning(f"⚠️ AI Policy Generation error: {str(e)}")
            
        return {
            'recommendation': None,
            'source': 'ERROR',
            'success': False,
            'error': str(e) if 'e' in locals() else 'Unknown error'
        }
    
    def discover_cross_table_patterns(self, database: str, schema: str, 
                                     tables: List[str]) -> Dict[str, Any]:
        """
        Use AI to discover sensitive data patterns across multiple tables
        """
        if not tables:
            return {'pattern_analysis': None, 'source': 'NO_TABLES'}
        
        try:
            # Get column metadata across all tables
            tables_list = "', '".join(tables)
            pattern_query = f"""
            WITH table_columns AS (
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    comment,
                    CONCAT(table_name, '.', column_name, ' (', data_type, ')') as column_desc
                FROM {database}.INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema = '{schema}'
                AND table_name IN ('{tables_list}')
                ORDER BY table_name, ordinal_position
            ),
            column_summary AS (
                SELECT 
                    LISTAGG(column_desc, ', ') WITHIN GROUP (ORDER BY table_name, column_name) as columns_desc
                FROM table_columns
            )
            SELECT 
                SNOWFLAKE.CORTEX.COMPLETE(
                    '{self.ai_model}',
                    'Analyze these database columns for sensitive data patterns and relationships. Identify potential PII, financial data, or other sensitive information based on naming conventions and data types. Focus on cross-table relationships and common patterns: ' || 
                    SUBSTR(columns_desc, 1, 1500)
                ) as pattern_analysis
            FROM column_summary
            """
            
            result = self._safe_ai_query(pattern_query, "cross-table pattern discovery")
            if result:
                pattern_analysis = result.get('PATTERN_ANALYSIS', '')
                return {
                    'pattern_analysis': pattern_analysis,
                    'source': 'CORTEX_PATTERN_DISCOVERY',
                    'success': True
                }
                
        except Exception as e:
            st.warning(f"⚠️ Cross-table pattern discovery error: {str(e)}")
            
        return {'pattern_analysis': None, 'source': 'ERROR', 'success': False}
    
    def test_ai_connectivity(self) -> Dict[str, Any]:
        """Test Cortex AI connectivity and capabilities"""
        try:
            test_query = """
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                'Respond with exactly: "Snowflake Cortex AI is operational and ready for sensitive data analysis."'
            ) as ai_test
            """
            
            result = self._safe_ai_query(test_query, "connectivity test")
            if result:
                response = result.get('AI_TEST', '')
                is_working = "operational" in response.lower()
                return {
                    'status': 'OPERATIONAL' if is_working else 'RESPONDING',
                    'response': response,
                    'model': 'mistral-large',
                    'source': 'CORTEX_AI_TEST'
                }
            else:
                return {
                    'status': 'FAILED',
                    'response': 'No response received',
                    'model': 'mistral-large',
                    'source': 'CORTEX_AI_TEST'
                }
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'response': str(e),
                'model': 'mistral-large',
                'source': 'CORTEX_AI_TEST'
            }

class SnowflakeDataManager:
    """Handles all Snowflake data operations with optimized caching"""
    
    def __init__(self, connection):
        self.connection = connection
    
    @st.cache_data(ttl=300)
    def get_databases(_conn) -> List[str]:
        """Get list of available databases"""
        try:
            query = "SELECT DATABASE_NAME FROM INFORMATION_SCHEMA.DATABASES ORDER BY DATABASE_NAME"
            df = _conn.query(query)
            return df['DATABASE_NAME'].tolist()
        except Exception as e:
            st.error(f"❌ Error fetching databases: {str(e)}")
            return []
    
    @st.cache_data(ttl=300)
    def get_schemas(_conn, database_name: str) -> List[str]:
        """Get list of schemas for the selected database"""
        try:
            query = f"SELECT SCHEMA_NAME FROM {database_name}.INFORMATION_SCHEMA.SCHEMATA ORDER BY SCHEMA_NAME"
            df = _conn.query(query)
            return df['SCHEMA_NAME'].tolist()
        except Exception as e:
            st.error(f"❌ Error fetching schemas: {str(e)}")
            return []
    
    @st.cache_data(ttl=300)
    def get_tables(_conn, database_name: str, schema_name: str) -> List[str]:
        """Get list of tables for the selected database and schema"""
        try:
            query = f"""
            SELECT TABLE_NAME 
            FROM {database_name}.INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{schema_name}'
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
            df = _conn.query(query)
            return df['TABLE_NAME'].tolist()
        except Exception as e:
            st.error(f"❌ Error fetching tables: {str(e)}")
            return []
    
    @st.cache_data(ttl=300)
    def get_column_metadata(_conn, database: str, schema: str, table: str) -> pd.DataFrame:
        """Get comprehensive column metadata"""
        try:
            query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COMMENT,
                ORDINAL_POSITION
            FROM {database}.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' 
            AND TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
            """
            df = _conn.query(query)
            return df
        except Exception as e:
            st.error(f"❌ Error fetching column metadata: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def get_sample_data(_conn, database: str, schema: str, table: str, 
                       column_name: str, limit: int = 50) -> List[str]:
        """Get sample data for a specific column"""
        try:
            query = f"""
            SELECT DISTINCT {column_name}
            FROM {database}.{schema}.{table}
            WHERE {column_name} IS NOT NULL
            LIMIT {limit}
            """
            df = _conn.query(query)
            return df[column_name].tolist() if not df.empty else []
        except Exception as e:
            st.warning(f"⚠️ Error fetching sample data for {column_name}: {str(e)}")
            return []

def render_ai_capabilities_banner():
    """Render AI capabilities and status banner"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #1f4e79, #2e86ab); 
        border-radius: 10px; margin: 1rem 0; color: white;'>
        <h3>🤖 Powered by Snowflake Cortex AI</h3>
        <p>Advanced AI-driven sensitive data discovery with intelligent masking recommendations</p>
        </div>
        """, unsafe_allow_html=True)

def render_connection_status(conn, ai_engine: CortexAIEngine):
    """Render connection and AI status"""
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            # Test basic connection
            test_query = "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()"
            test_result = conn.query(test_query)
            
            if not test_result.empty:
                st.success("✅ **Snowflake Connected**")
                st.write(f"**User:** {test_result.iloc[0]['CURRENT_USER()']}")
                st.write(f"**Role:** {test_result.iloc[0]['CURRENT_ROLE()']}")
                st.write(f"**Warehouse:** {test_result.iloc[0]['CURRENT_WAREHOUSE()']}")
            
        except Exception as e:
            st.error(f"❌ **Connection Failed:** {str(e)}")
            return False
    
    with col2:
        # Test AI connectivity
        with st.spinner("Testing Cortex AI..."):
            ai_status = ai_engine.test_ai_connectivity()
            
            if ai_status['status'] == 'OPERATIONAL':
                st.success("🤖 **Cortex AI Operational**")
                st.write(f"**Model:** {ai_status['model']}")
                st.write("**Capabilities:** Classification, Analysis, Recommendations")
            elif ai_status['status'] == 'RESPONDING':
                st.warning("⚠️ **Cortex AI Responding** (Limited)")
                st.write(f"**Model:** {ai_status['model']}")
            else:
                st.error("❌ **Cortex AI Failed**")
                st.write(f"**Error:** {ai_status['response']}")
                
    return True

def render_database_selector(data_manager: SnowflakeDataManager) -> Tuple[str, str, List[str]]:
    """Render database selection interface"""
    st.subheader("🗃️ Database and Schema Selection")
    
    # Get databases
    databases = SnowflakeDataManager.get_databases(data_manager.connection)
    if not databases:
        st.warning("No databases found or unable to fetch database list")
        return None, None, []
    
    # Database selection
    selected_database = st.selectbox("Select Database:", databases, key="db_select")
    if not selected_database:
        return None, None, []
    
    # Get schemas
    schemas = SnowflakeDataManager.get_schemas(data_manager.connection, selected_database)
    if not schemas:
        st.warning(f"No schemas found in database {selected_database}")
        return selected_database, None, []
    
    # Schema selection
    selected_schema = st.selectbox("Select Schema:", schemas, key="schema_select")
    if not selected_schema:
        return selected_database, None, []
    
    # Get tables
    tables = SnowflakeDataManager.get_tables(data_manager.connection, selected_database, selected_schema)
    if not tables:
        st.warning(f"No tables found in {selected_database}.{selected_schema}")
        return selected_database, selected_schema, []
    
    # Table multi-selection
    selected_tables = st.multiselect(
        "Select Tables for Analysis:",
        options=tables,
        default=[],
        key="tables_select"
    )
    
    # Display selection summary
    if selected_tables:
        with st.expander("📋 Selection Summary", expanded=False):
            st.write(f"**Database:** {selected_database}")
            st.write(f"**Schema:** {selected_schema}")
            st.write(f"**Tables:** {', '.join(selected_tables)}")
    
    return selected_database, selected_schema, selected_tables

def analyze_table_with_ai(ai_engine: CortexAIEngine, data_manager: SnowflakeDataManager, 
                         database: str, schema: str, table: str) -> Dict[str, Any]:
    """Analyze a single table using AI"""
    
    # Get column metadata
    column_metadata = SnowflakeDataManager.get_column_metadata(data_manager.connection, database, schema, table)
    if column_metadata.empty:
        return {'error': 'No column metadata available', 'columns': []}
    
    analyzed_columns = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_columns = len(column_metadata)
    
    for idx, (_, row) in enumerate(column_metadata.iterrows()):
        column_name = row['COLUMN_NAME']
        data_type = row['DATA_TYPE']
        comment = row.get('COMMENT', '')
        
        # Update progress
        progress = (idx + 1) / total_columns
        progress_bar.progress(progress)
        status_text.text(f"Analyzing {column_name}... ({idx + 1}/{total_columns})")
        
        # Get sample data
        sample_data = SnowflakeDataManager.get_sample_data(
            data_manager.connection, database, schema, table, column_name
        )
        
        # AI Classification
        classification_result = ai_engine.classify_column_sensitivity(
            sample_data, column_name, f"{database}.{schema}.{table}"
        )
        
        # AI Semantic Analysis
        semantic_result = ai_engine.analyze_semantic_context(
            column_name, table, sample_data, comment
        )
        
        # Determine final assessment (prioritize higher confidence)
        if classification_result.confidence > semantic_result.confidence:
            final_result = classification_result
        else:
            final_result = semantic_result
        
        analyzed_columns.append({
            'Column Name': column_name,
            'Data Type': data_type,
            'Is Sensitive': final_result.is_sensitive,
            'Sensitive Type': final_result.sensitive_type,
            'Confidence': f"{final_result.confidence:.1%}",
            'AI Reasoning': final_result.reasoning,
            'Detection Source': final_result.source,
            'Comment': comment or 'No comment',
            'Sample Count': len(sample_data),
            'classification_raw': classification_result,
            'semantic_raw': semantic_result
        })
    
    progress_bar.empty()
    status_text.empty()
    
    return {
        'table': f"{database}.{schema}.{table}",
        'columns': analyzed_columns,
        'total_columns': total_columns,
        'sensitive_columns': sum(1 for col in analyzed_columns if col['Is Sensitive'])
    }

def render_analysis_results(results: Dict[str, Any], ai_engine: CortexAIEngine):
    """Render comprehensive analysis results"""
    
    if 'error' in results:
        st.error(f"❌ Analysis Error: {results['error']}")
        return
    
    columns = results['columns']
    sensitive_columns = [col for col in columns if col['Is Sensitive']]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Columns", results['total_columns'])
    with col2:
        st.metric("Sensitive Columns", results['sensitive_columns'])
    with col3:
        sensitivity_rate = (results['sensitive_columns'] / results['total_columns']) * 100
        st.metric("Sensitivity Rate", f"{sensitivity_rate:.1f}%")
    with col4:
        ai_sources = len(set(col['Detection Source'] for col in columns))
        st.metric("AI Detection Methods", ai_sources)
    
    # Sensitive columns analysis
    if sensitive_columns:
        st.subheader("🔍 Sensitive Data Found")
        
        # Create detailed dataframe
        sensitive_df = pd.DataFrame([{
            'Column': col['Column Name'],
            'Type': col['Data Type'],
            'Sensitive Classification': col['Sensitive Type'],
            'Confidence': col['Confidence'],
            'AI Method': col['Detection Source'],
            'Reasoning': col['AI Reasoning'][:100] + "..." if len(col['AI Reasoning']) > 100 else col['AI Reasoning']
        } for col in sensitive_columns])
        
        st.dataframe(sensitive_df, use_container_width=True, height=300)
        
        # AI-Generated Masking Recommendations
        st.subheader("🛡️ AI-Generated Masking Recommendations")
        
        for col in sensitive_columns:
            with st.expander(f"🔒 {col['Column Name']} - {col['Sensitive Type']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Column Details:**")
                    st.write(f"**Data Type:** {col['Data Type']}")
                    st.write(f"**Confidence:** {col['Confidence']}")
                    st.write(f"**Sample Size:** {col['Sample Count']} values")
                    st.write(f"**AI Reasoning:** {col['AI Reasoning']}")
                
                with col2:
                    st.markdown("**AI Masking Recommendation:**")
                    
                    # Generate AI masking recommendation
                    with st.spinner("Generating AI masking policy..."):
                        masking_rec = ai_engine.generate_masking_recommendation(
                            col['Sensitive Type'], col['Column Name'], col['Data Type']
                        )
                        
                        if masking_rec['success']:
                            st.markdown(masking_rec['recommendation'])
                        else:
                            st.error("Failed to generate masking recommendation")
                
                # Detailed AI analysis
                if st.button(f"View Detailed AI Analysis", key=f"detail_{col['Column Name']}"):
                    st.markdown("**🤖 Classification Analysis:**")
                    st.json(col['classification_raw'].__dict__)
                    
                    st.markdown("**🧠 Semantic Analysis:**")
                    st.json(col['semantic_raw'].__dict__)
    
    else:
        st.success("✅ No sensitive data patterns detected by AI analysis")
    
    # All columns overview
    st.subheader("📊 Complete Column Analysis")
    all_columns_df = pd.DataFrame([{
        'Column': col['Column Name'],
        'Data Type': col['Data Type'],
        'Sensitive': '🔴' if col['Is Sensitive'] else '🟢',
        'Type': col['Sensitive Type'] if col['Is Sensitive'] else 'Public',
        'Confidence': col['Confidence'],
        'AI Source': col['Detection Source']
    } for col in columns])
    
    st.dataframe(all_columns_df, use_container_width=True)

def render_cross_table_analysis(ai_engine: CortexAIEngine, database: str, schema: str, tables: List[str]):
    """Render cross-table pattern analysis using AI"""
    if len(tables) < 2:
        st.info("💡 Select multiple tables to enable cross-table pattern analysis")
        return
    
    st.subheader("🔄 AI Cross-Table Pattern Analysis")
    
    with st.spinner("Analyzing patterns across tables with Cortex AI..."):
        pattern_analysis = ai_engine.discover_cross_table_patterns(database, schema, tables)
        
        if pattern_analysis['success']:
            st.markdown("**🤖 AI Pattern Discovery Results:**")
            st.markdown(pattern_analysis['pattern_analysis'])
        else:
            st.error("❌ Cross-table pattern analysis failed")

def render_ai_settings_sidebar():
    """Render AI configuration settings in sidebar"""
    with st.sidebar:
        st.header("🤖 AI Configuration")
        
        # AI Model Selection
        ai_model = st.selectbox(
            "Cortex AI Model:",
            options=['mistral-large', 'mixtral-8x7b', 'llama2-70b-chat'],
            index=0,
            help="Select the Cortex AI model for analysis"
        )
        
        # AI Analysis Settings
        st.subheader("Analysis Settings")
        
        enable_classification = st.checkbox(
            "Enable AI Classification", 
            value=True,
            help="Use Cortex CLASSIFY_TEXT for sensitivity classification"
        )
        
        enable_semantic = st.checkbox(
            "Enable Semantic Analysis", 
            value=True,
            help="Use Cortex COMPLETE for deep semantic understanding"
        )
        
        enable_cross_table = st.checkbox(
            "Enable Cross-Table Analysis", 
            value=True,
            help="Analyze patterns across multiple tables"
        )
        
        # Performance Settings
        st.subheader("Performance")
        
        batch_size = st.slider(
            "Analysis Batch Size",
            min_value=1, max_value=10, value=3,
            help="Number of columns to analyze simultaneously"
        )
        
        sample_limit = st.slider(
            "Sample Data Limit",
            min_value=10, max_value=100, value=50,
            help="Maximum sample values per column"
        )
        
        return {
            'ai_model': ai_model,
            'enable_classification': enable_classification,
            'enable_semantic': enable_semantic,
            'enable_cross_table': enable_cross_table,
            'batch_size': batch_size,
            'sample_limit': sample_limit
        }

def main():
    """Main application entry point"""
    
    # Header
    st.title("🤖 AI-Enhanced Snowflake Sensitive Data Discovery & Masking")
    st.markdown("*Powered by Snowflake Cortex AI and Intelligence for intelligent data classification*")
    
    # AI capabilities banner
    render_ai_capabilities_banner()
    
    # AI settings sidebar
    ai_settings = render_ai_settings_sidebar()
    
    st.markdown("---")
    
    # Establish Snowflake connection
    try:
        conn = st.connection('snowflake')
        
        # Initialize AI engine and data manager
        ai_engine = CortexAIEngine(conn, ai_settings['ai_model'])
        data_manager = SnowflakeDataManager(conn)
        
        # Connection and AI status
        if not render_connection_status(conn, ai_engine):
            st.stop()
        
        st.markdown("---")
        
        # Database selection
        database, schema, selected_tables = render_database_selector(data_manager)
        
        if not database or not schema:
            st.info("👆 Please select a database and schema to begin analysis")
            st.stop()
        
        if not selected_tables:
            st.info("👆 Please select one or more tables for AI-powered sensitive data analysis")
            st.stop()
        
        st.markdown("---")
        
        # Main analysis section
        st.subheader("🔍 AI-Powered Sensitive Data Analysis")
        
        if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
            
            # Cross-table analysis for multiple tables
            if len(selected_tables) > 1 and ai_settings['enable_cross_table']:
                render_cross_table_analysis(ai_engine, database, schema, selected_tables)
                st.markdown("---")
            
            # Analyze each selected table
            for table in selected_tables:
                st.subheader(f"📋 Analyzing: {database}.{schema}.{table}")
                
                with st.container():
                    # Analyze table with AI
                    results = analyze_table_with_ai(ai_engine, data_manager, database, schema, table)
                    
                    # Render results
                    render_analysis_results(results, ai_engine)
                
                st.markdown("---")
        
        # Export and additional features
        st.subheader("📥 Export and Integration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Analysis Report", use_container_width=True):
                st.info("Analysis report export feature - coming soon!")
        
        with col2:
            if st.button("🔧 Generate DDL Scripts", use_container_width=True):
                st.info("DDL script generation - coming soon!")
        
        with col3:
            if st.button("📋 Save to Snowflake", use_container_width=True):
                st.info("Save results to Snowflake table - coming soon!")
        
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.info("Please ensure you have a valid Snowflake connection configured.")

if __name__ == "__main__":
    main() 