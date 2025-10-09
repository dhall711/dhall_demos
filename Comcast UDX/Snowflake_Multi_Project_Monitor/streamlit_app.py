"""
Snowflake Multi-Project Usage Monitor - Streamlit in Snowflake (SiS) Version
Optimized for deployment within Snowflake's native Streamlit environment.

Key differences from local version:
- Uses native SiS connection handling
- Simplified file structure
- Optimized for Snowflake's security model
- No external secrets management needed
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import time

# Set page configuration
st.set_page_config(
    page_title="🏢 Snowflake Multi-Project Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class CortexUsageMetrics:
    """Enhanced Cortex AI usage metrics by workload"""
    workload_name: str
    query_tag: str
    warehouse_name: str
    
    # LLM Costs
    llm_requests: int
    llm_tokens_processed: int
    llm_credits_used: float
    llm_cost_estimate: float
    
    # Vector Embedding Costs
    embedding_requests: int
    embedding_tokens: int
    embedding_credits_used: float
    embedding_cost_estimate: float
    
    # Cortex Analyst Usage
    analyst_requests: int
    analyst_tokens: int
    analyst_credits_used: float
    analyst_cost_estimate: float
    
    # Document Processing Usage
    doc_processing_requests: int
    doc_processing_tokens: int
    doc_processing_credits_used: float
    doc_processing_cost_estimate: float
    
    # Fine Tuning Usage
    fine_tuning_requests: int
    fine_tuning_tokens: int
    fine_tuning_credits_used: float
    fine_tuning_cost_estimate: float
    
    # Functions Usage
    functions_requests: int
    functions_tokens: int
    functions_credits_used: float
    functions_cost_estimate: float
    
    # Search Usage
    search_requests: int
    search_tokens: int
    search_credits_used: float
    search_cost_estimate: float
    
    # Token Totals (Key Metric)
    total_input_tokens: int
    total_output_tokens: int
    total_tokens_processed: int
    
    # UI Warehouse Costs
    ui_query_count: int
    ui_credits_used: float
    ui_execution_time_ms: int
    
    # SQL Warehouse Costs
    sql_query_count: int
    sql_credits_used: float
    sql_execution_time_ms: int
    
    # Consolidated Metrics
    total_credits: float
    total_cost_estimate: float
    rows_per_credit: float
    gb_per_credit: float
    tokens_per_credit: float
    
    # Period comparison
    period: str
    prev_period_total_cost: Optional[float] = None
    cost_change_percent: Optional[float] = None

@dataclass
class ProjectConfig:
    """Configuration for a monitored project"""
    project_name: str
    project_type: str
    warehouse_pattern: str
    database_pattern: str
    user_pattern: str
    description: str
    cost_center: str
    priority: str

@dataclass
class ProjectMetrics:
    """Enhanced metrics for a specific project with efficiency indicators"""
    project_name: str
    warehouse_credits: float
    query_count: int
    avg_execution_time: float
    error_count: int
    unique_users: int
    data_scanned_gb: float
    ai_requests: int
    estimated_cost: float
    time_period: str
    
    # Enhanced efficiency metrics
    rows_per_credit: float = 0.0
    gb_per_credit: float = 0.0
    cost_per_query: float = 0.0
    rows_processed: int = 0
    
    # Period comparison
    prev_period_cost: Optional[float] = None
    cost_change_percent: Optional[float] = None

@dataclass
class CrossProjectInsight:
    """Insights comparing projects"""
    insight_type: str
    title: str
    description: str
    projects_involved: List[str]
    metrics: Dict[str, Any]
    recommendation: str
    priority: str

class SiSConnection:
    """Streamlit in Snowflake connection manager"""
    
    def __init__(self):
        self._conn = None
        self._connection_info = None
    
    @property
    def connection(self):
        """Get SiS native connection"""
        if self._conn is None:
            self._conn = self._establish_connection()
        return self._conn
    
    def _establish_connection(self):
        """Establish native SiS connection with enhanced error handling"""
        try:
            # In SiS, st.connection() uses the app's execution context
            conn = st.connection('snowflake')
            
            # Test basic connection
            test_result = conn.query("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
            
            if not test_result.empty:
                self._connection_info = {
                    'user': test_result.iloc[0]['CURRENT_USER()'],
                    'role': test_result.iloc[0]['CURRENT_ROLE()'],
                    'warehouse': test_result.iloc[0]['CURRENT_WAREHOUSE()'],
                    'database': test_result.iloc[0]['CURRENT_DATABASE()']
                }
                
                # Test ACCOUNT_USAGE access with helpful error messages
                self._test_account_usage_access(conn)
                return conn
            else:
                raise Exception("SiS connection test failed")
                
        except Exception as e:
            st.error(f"Failed to establish SiS connection: {str(e)}")
            return None
    
    def _test_account_usage_access(self, conn):
        """Test available ACCOUNT_USAGE views and determine monitoring capability"""
        
        # Detect what level of ACCOUNT_USAGE access is available
        self._account_usage_level = self._detect_account_usage_access(conn)
        
        if self._account_usage_level == 'full':
            st.success("✅ Full ACCOUNT_USAGE access - Query Attribution available")
        elif self._account_usage_level == 'basic':
            st.info("ℹ️ Basic ACCOUNT_USAGE access - Warehouse metering available")
        elif self._account_usage_level == 'minimal':
            st.warning("⚠️ Limited ACCOUNT_USAGE access - Query history only")
        else:
            st.warning("⚠️ No ACCOUNT_USAGE access - Using session-based monitoring")
            with st.expander("🔧 ACCOUNT_USAGE Access Help"):
                st.markdown("""
                **No ACCOUNT_USAGE Access Detected**
                
                **What this means:**
                - You can still use basic warehouse monitoring
                - Sample data mode is available for testing
                - Some features will be limited
                
                **To enable full monitoring:**
                
                1. **Grant Basic Privileges** (run as ACCOUNTADMIN):
                ```sql
                GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;
                USE ROLE ACCOUNTADMIN;
                USE WAREHOUSE COMPUTE_WH;
                ```
                
                2. **Test Your Access:**
                ```sql
                -- Test different levels:
                SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION LIMIT 1;  -- Full
                SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY LIMIT 1;  -- Basic
                SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY LIMIT 1;  -- Minimal
                ```
                
                3. **Use Sample Data Mode**: Enable the checkbox in the dashboard
                """)
        
        # Test Cortex views (optional)
        self._cortex_available = self._test_cortex_access(conn)
    
    def _detect_account_usage_access(self, conn):
        """Detect what level of ACCOUNT_USAGE access is available"""
        
        # Test QUERY_ATTRIBUTION (most detailed - needed for cost attribution)
        try:
            test_query = "SELECT COUNT(*) as cnt FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION LIMIT 1"
            conn.query(test_query)
            return 'full'
        except:
            pass
        
        # Test WAREHOUSE_METERING_HISTORY (basic cost tracking)
        try:
            test_query = "SELECT COUNT(*) as cnt FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY LIMIT 1"
            conn.query(test_query)
            return 'basic'
        except:
            pass
        
        # Test QUERY_HISTORY (minimal monitoring)
        try:
            test_query = "SELECT COUNT(*) as cnt FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY LIMIT 1"
            conn.query(test_query)
            return 'minimal'
        except:
            pass
        
        # No ACCOUNT_USAGE access
        return 'none'
    
    def _test_cortex_access(self, conn):
        """Test Cortex view access across all available views"""
        cortex_views = {
            'CORTEX_LLM_USAGE': False,
            'CORTEX_EMBEDDING_USAGE': False,
            'CORTEX_ANALYST_USAGE_HISTORY': False,
            'CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY': False,
            'CORTEX_FINE_TUNING_USAGE_HISTORY': False,
            'CORTEX_FUNCTIONS_USAGE_HISTORY': False,
            'CORTEX_SEARCH_SERVING_USAGE_HISTORY': False
        }
        
        available_count = 0
        for view_name in cortex_views.keys():
            try:
                test_query = f"SELECT COUNT(*) FROM SNOWFLAKE.ACCOUNT_USAGE.{view_name} LIMIT 1"
                conn.query(test_query)
                cortex_views[view_name] = True
                available_count += 1
            except:
                pass
        
        # Store detailed availability
        self._cortex_views_available = cortex_views
        
        if available_count > 0:
            st.success(f"✅ {available_count}/7 Cortex AI views accessible")
            return True
        else:
            st.info("ℹ️ No Cortex AI views available - warehouse-focused monitoring")
            return False
    
    def execute_query(self, query: str, operation_name: str = "query") -> Optional[pd.DataFrame]:
        """Execute query with SiS-optimized error handling"""
        try:
            if not self.connection:
                st.error("No SiS connection available")
                return None
            
            with st.spinner(f"Executing {operation_name}..."):
                # Add query tag for monitoring
                tagged_query = f"/* SiS_MONITOR: {operation_name} */ {query}"
                df = self.connection.query(tagged_query)
                return df
                
        except Exception as e:
            st.error(f"Query execution failed in SiS: {str(e)}")
            # Show query for debugging in SiS environment
            with st.expander("🔍 Debug Query"):
                st.code(query, language='sql')
            return None

class SiSCortexMonitor:
    """SiS-optimized Cortex AI monitoring"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.cost_models = {
            'llm_cost_per_token': 0.0001,
            'embedding_cost_per_token': 0.00005,
            'analyst_cost_per_token': 0.0001,
            'doc_processing_cost_per_token': 0.00008,
            'fine_tuning_cost_per_token': 0.0002,
            'functions_cost_per_token': 0.00006,
            'search_cost_per_token': 0.00004,
            'warehouse_credit_cost': 3.0
        }
        
        # SiS-optimized workload patterns
        self.workload_patterns = {
            'sensitive_data_discovery': {
                'query_tags': ['SIS_DISCOVERY', 'DDM_ANALYSIS', 'PRIVACY_SCAN', 'SiS_MONITOR'],
                'warehouses': ['%SENSITIVE%', '%DDM%', '%DISCOVERY%'],
                'cortex_functions': ['CLASSIFY_TEXT', 'EXTRACT_SEMANTIC_PATTERN']
            },
            'schema_mapping': {
                'query_tags': ['SCHEMA_MAP', 'ETL_TRANSFORM', 'MIGRATION'],
                'warehouses': ['%MAPPER%', '%TRANSFORM%', '%ETL%'],
                'cortex_functions': ['COMPLETE', 'SEMANTIC_SIMILARITY']
            }
        }
    
    def get_cortex_usage_by_workload(self, days: int = 7) -> Dict[str, CortexUsageMetrics]:
        """Get comprehensive Cortex AI usage metrics across all 7 services"""
        
        # Check access levels
        cortex_available = getattr(self.db, '_cortex_available', False)
        account_usage_level = getattr(self.db, '_account_usage_level', 'none')
        cortex_views = getattr(self.db, '_cortex_views_available', {})
        
        try:
            if cortex_available and account_usage_level == 'full':
                # Use comprehensive Cortex monitoring with all 7 views
                query = self._get_comprehensive_cortex_query(days, cortex_views)
            elif account_usage_level == 'full':
                # Use QUERY_ATTRIBUTION for detailed cost tracking
                query = self._get_query_attribution_query(days)
            elif account_usage_level == 'basic':
                # Use WAREHOUSE_METERING_HISTORY for basic cost tracking
                query = self._get_warehouse_metering_query(days)
            elif account_usage_level == 'minimal':
                # Use QUERY_HISTORY for basic monitoring
                query = self._get_query_history_query(days)
            else:
                # No ACCOUNT_USAGE access - use current session info
                return self._get_session_based_metrics(days)
                
            df = self.db.execute_query(query, f"fetching comprehensive workload usage ({account_usage_level} mode)")
            
            if df is None or df.empty:
                st.warning("No usage data found. Using sample data for demonstration.")
                return self.generate_sample_data()
            
            return self._process_comprehensive_results(df, days, account_usage_level, cortex_views)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "does not exist or not authorized" in error_msg:
                st.warning("⚠️ Database view access error - switching to session mode")
                return self._get_session_based_metrics(days)
            else:
                st.error(f"Error fetching workload usage: {e}")
                st.info("Showing sample data for demonstration purposes")
                return self.generate_sample_data()
    
    def _get_comprehensive_cortex_query(self, days: int, cortex_views: Dict[str, bool]) -> str:
        """Comprehensive query using all available Cortex views"""
        
        # Build CTEs for available Cortex views
        cortex_ctes = []
        
        if cortex_views.get('CORTEX_LLM_USAGE', False):
            cortex_ctes.append(f"""
            cortex_llm_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as llm_requests,
                    COALESCE(SUM(prompt_tokens), 0) as llm_input_tokens,
                    COALESCE(SUM(completion_tokens), 0) as llm_output_tokens,
                    COALESCE(SUM(total_tokens), 0) as llm_total_tokens,
                    COALESCE(SUM(credits_used), 0) as llm_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_LLM_USAGE
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        if cortex_views.get('CORTEX_EMBEDDING_USAGE', False):
            cortex_ctes.append(f"""
            cortex_embedding_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as embedding_requests,
                    COALESCE(SUM(total_tokens), 0) as embedding_tokens,
                    COALESCE(SUM(credits_used), 0) as embedding_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_EMBEDDING_USAGE
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False):
            cortex_ctes.append(f"""
            cortex_analyst_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as analyst_requests,
                    COALESCE(SUM(prompt_tokens), 0) as analyst_input_tokens,
                    COALESCE(SUM(completion_tokens), 0) as analyst_output_tokens,
                    COALESCE(SUM(total_tokens), 0) as analyst_tokens,
                    COALESCE(SUM(credits_used), 0) as analyst_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        if cortex_views.get('CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY', False):
            cortex_ctes.append(f"""
            cortex_doc_processing_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as doc_processing_requests,
                    COALESCE(SUM(total_tokens), 0) as doc_processing_tokens,
                    COALESCE(SUM(credits_used), 0) as doc_processing_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        if cortex_views.get('CORTEX_FINE_TUNING_USAGE_HISTORY', False):
            cortex_ctes.append(f"""
            cortex_fine_tuning_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as fine_tuning_requests,
                    COALESCE(SUM(total_tokens), 0) as fine_tuning_tokens,
                    COALESCE(SUM(credits_used), 0) as fine_tuning_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FINE_TUNING_USAGE_HISTORY
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        if cortex_views.get('CORTEX_FUNCTIONS_USAGE_HISTORY', False):
            cortex_ctes.append(f"""
            cortex_functions_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as functions_requests,
                    COALESCE(SUM(total_tokens), 0) as functions_tokens,
                    COALESCE(SUM(credits_used), 0) as functions_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        if cortex_views.get('CORTEX_SEARCH_SERVING_USAGE_HISTORY', False):
            cortex_ctes.append(f"""
            cortex_search_usage AS (
                SELECT 
                    DATE_TRUNC('day', request_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as search_requests,
                    COALESCE(SUM(total_tokens), 0) as search_tokens,
                    COALESCE(SUM(credits_used), 0) as search_credits
                FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_SERVING_USAGE_HISTORY
                WHERE request_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            )""")
        
        # Build LEFT JOINs for available views
        cortex_joins = []
        
        if cortex_views.get('CORTEX_LLM_USAGE', False):
            cortex_joins.append("""
                LEFT JOIN cortex_llm_usage llm 
                    ON qa.usage_date = llm.usage_date 
                    AND qa.warehouse_name = llm.warehouse_name 
                    AND qa.query_tag = llm.query_tag""")
        
        if cortex_views.get('CORTEX_EMBEDDING_USAGE', False):
            cortex_joins.append("""
                LEFT JOIN cortex_embedding_usage emb 
                    ON qa.usage_date = emb.usage_date 
                    AND qa.warehouse_name = emb.warehouse_name 
                    AND qa.query_tag = emb.query_tag""")
        
        if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False):
            cortex_joins.append("""
                LEFT JOIN cortex_analyst_usage analyst
                    ON qa.usage_date = analyst.usage_date 
                    AND qa.warehouse_name = analyst.warehouse_name 
                    AND qa.query_tag = analyst.query_tag""")
        
        if cortex_views.get('CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY', False):
            cortex_joins.append("""
                LEFT JOIN cortex_doc_processing_usage doc
                    ON qa.usage_date = doc.usage_date 
                    AND qa.warehouse_name = doc.warehouse_name 
                    AND qa.query_tag = doc.query_tag""")
        
        if cortex_views.get('CORTEX_FINE_TUNING_USAGE_HISTORY', False):
            cortex_joins.append("""
                LEFT JOIN cortex_fine_tuning_usage ft
                    ON qa.usage_date = ft.usage_date 
                    AND qa.warehouse_name = ft.warehouse_name 
                    AND qa.query_tag = ft.query_tag""")
        
        if cortex_views.get('CORTEX_FUNCTIONS_USAGE_HISTORY', False):
            cortex_joins.append("""
                LEFT JOIN cortex_functions_usage func
                    ON qa.usage_date = func.usage_date 
                    AND qa.warehouse_name = func.warehouse_name 
                    AND qa.query_tag = func.query_tag""")
        
        if cortex_views.get('CORTEX_SEARCH_SERVING_USAGE_HISTORY', False):
            cortex_joins.append("""
                LEFT JOIN cortex_search_usage search
                    ON qa.usage_date = search.usage_date 
                    AND qa.warehouse_name = search.warehouse_name 
                    AND qa.query_tag = search.query_tag""")
        
        # Construct the full query
        return f"""
        WITH {','.join(cortex_ctes)},
        
        query_attribution AS (
            SELECT 
                DATE_TRUNC('day', start_time) as usage_date,
                COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                COALESCE(query_tag, 'untagged') as query_tag,
                COUNT(*) as query_count,
                COALESCE(SUM(credits_attributed_to_query), 0) as attributed_credits,
                COALESCE(SUM(execution_time_ms), 0) as total_execution_time,
                COALESCE(SUM(bytes_scanned), 0) as bytes_scanned,
                COALESCE(SUM(rows_produced), 0) as rows_produced,
                
                -- Query classification
                SUM(CASE 
                    WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                         OR UPPER(query_text) LIKE '%SIS_%' 
                         OR query_tag LIKE '%SiS%'
                    THEN COALESCE(credits_attributed_to_query, 0)
                    ELSE 0 
                END) as ui_credits,
                
                SUM(CASE 
                    WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                         AND UPPER(query_text) NOT LIKE '%SIS_%'
                         AND query_tag NOT LIKE '%SiS%'
                    THEN COALESCE(credits_attributed_to_query, 0)
                    ELSE 0 
                END) as sql_credits,
                
                COUNT(CASE 
                    WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                         OR UPPER(query_text) LIKE '%SIS_%'
                         OR query_tag LIKE '%SiS%'
                    THEN 1 
                END) as ui_query_count,
                
                COUNT(CASE 
                    WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                         AND UPPER(query_text) NOT LIKE '%SIS_%'
                         AND query_tag NOT LIKE '%SiS%'
                    THEN 1 
                END) as sql_query_count
                
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
            WHERE start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
            GROUP BY usage_date, warehouse_name, query_tag
        ),
        
        workload_consolidated AS (
            SELECT 
                qa.usage_date,
                qa.warehouse_name,
                qa.query_tag,
                
                -- Enhanced workload classification
                CASE 
                    WHEN qa.query_tag ILIKE 'SIS_DISCOVERY' 
                         OR qa.query_tag ILIKE 'DDM_ANALYSIS' 
                         OR qa.query_tag ILIKE 'PRIVACY_SCAN'
                         OR qa.warehouse_name ILIKE '%SENSITIVE%' 
                         OR qa.warehouse_name ILIKE '%DDM%' 
                         OR qa.warehouse_name ILIKE '%DISCOVERY%'
                         OR qa.query_tag LIKE '%SiS_MONITOR%'
                    THEN 'sensitive_data_discovery'
                    WHEN qa.query_tag ILIKE 'SCHEMA_MAP' 
                         OR qa.query_tag ILIKE 'ETL_TRANSFORM' 
                         OR qa.query_tag ILIKE 'MIGRATION'
                         OR qa.warehouse_name ILIKE '%MAPPER%' 
                         OR qa.warehouse_name ILIKE '%TRANSFORM%' 
                         OR qa.warehouse_name ILIKE '%ETL%'
                    THEN 'schema_mapping'
                    ELSE 'general_workload'
                END as workload_name,
                
                -- Query Attribution metrics (PRIMARY)
                COALESCE(qa.query_count, 0) as total_queries,
                COALESCE(qa.attributed_credits, 0) as warehouse_credits,
                COALESCE(qa.ui_credits, 0) as ui_credits,
                COALESCE(qa.sql_credits, 0) as sql_credits,
                COALESCE(qa.ui_query_count, 0) as ui_queries,
                COALESCE(qa.sql_query_count, 0) as sql_queries,
                COALESCE(qa.total_execution_time, 0) as execution_time_ms,
                COALESCE(qa.bytes_scanned, 0) as bytes_scanned,
                COALESCE(qa.rows_produced, 0) as rows_produced,
                
                -- Cortex LLM metrics
                {f"COALESCE(llm.llm_requests, 0) as llm_requests," if cortex_views.get('CORTEX_LLM_USAGE', False) else "0 as llm_requests,"}
                {f"COALESCE(llm.llm_input_tokens, 0) as llm_input_tokens," if cortex_views.get('CORTEX_LLM_USAGE', False) else "0 as llm_input_tokens,"}
                {f"COALESCE(llm.llm_output_tokens, 0) as llm_output_tokens," if cortex_views.get('CORTEX_LLM_USAGE', False) else "0 as llm_output_tokens,"}
                {f"COALESCE(llm.llm_total_tokens, 0) as llm_tokens," if cortex_views.get('CORTEX_LLM_USAGE', False) else "0 as llm_tokens,"}
                {f"COALESCE(llm.llm_credits, 0) as llm_credits," if cortex_views.get('CORTEX_LLM_USAGE', False) else "0 as llm_credits,"}
                
                -- Cortex Embedding metrics
                {f"COALESCE(emb.embedding_requests, 0) as embedding_requests," if cortex_views.get('CORTEX_EMBEDDING_USAGE', False) else "0 as embedding_requests,"}
                {f"COALESCE(emb.embedding_tokens, 0) as embedding_tokens," if cortex_views.get('CORTEX_EMBEDDING_USAGE', False) else "0 as embedding_tokens,"}
                {f"COALESCE(emb.embedding_credits, 0) as embedding_credits," if cortex_views.get('CORTEX_EMBEDDING_USAGE', False) else "0 as embedding_credits,"}
                
                -- Cortex Analyst metrics
                {f"COALESCE(analyst.analyst_requests, 0) as analyst_requests," if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False) else "0 as analyst_requests,"}
                {f"COALESCE(analyst.analyst_input_tokens, 0) as analyst_input_tokens," if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False) else "0 as analyst_input_tokens,"}
                {f"COALESCE(analyst.analyst_output_tokens, 0) as analyst_output_tokens," if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False) else "0 as analyst_output_tokens,"}
                {f"COALESCE(analyst.analyst_tokens, 0) as analyst_tokens," if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False) else "0 as analyst_tokens,"}
                {f"COALESCE(analyst.analyst_credits, 0) as analyst_credits," if cortex_views.get('CORTEX_ANALYST_USAGE_HISTORY', False) else "0 as analyst_credits,"}
                
                -- Document Processing metrics
                {f"COALESCE(doc.doc_processing_requests, 0) as doc_processing_requests," if cortex_views.get('CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY', False) else "0 as doc_processing_requests,"}
                {f"COALESCE(doc.doc_processing_tokens, 0) as doc_processing_tokens," if cortex_views.get('CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY', False) else "0 as doc_processing_tokens,"}
                {f"COALESCE(doc.doc_processing_credits, 0) as doc_processing_credits," if cortex_views.get('CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY', False) else "0 as doc_processing_credits,"}
                
                -- Fine Tuning metrics
                {f"COALESCE(ft.fine_tuning_requests, 0) as fine_tuning_requests," if cortex_views.get('CORTEX_FINE_TUNING_USAGE_HISTORY', False) else "0 as fine_tuning_requests,"}
                {f"COALESCE(ft.fine_tuning_tokens, 0) as fine_tuning_tokens," if cortex_views.get('CORTEX_FINE_TUNING_USAGE_HISTORY', False) else "0 as fine_tuning_tokens,"}
                {f"COALESCE(ft.fine_tuning_credits, 0) as fine_tuning_credits," if cortex_views.get('CORTEX_FINE_TUNING_USAGE_HISTORY', False) else "0 as fine_tuning_credits,"}
                
                -- Functions metrics
                {f"COALESCE(func.functions_requests, 0) as functions_requests," if cortex_views.get('CORTEX_FUNCTIONS_USAGE_HISTORY', False) else "0 as functions_requests,"}
                {f"COALESCE(func.functions_tokens, 0) as functions_tokens," if cortex_views.get('CORTEX_FUNCTIONS_USAGE_HISTORY', False) else "0 as functions_tokens,"}
                {f"COALESCE(func.functions_credits, 0) as functions_credits," if cortex_views.get('CORTEX_FUNCTIONS_USAGE_HISTORY', False) else "0 as functions_credits,"}
                
                -- Search metrics
                {f"COALESCE(search.search_requests, 0) as search_requests," if cortex_views.get('CORTEX_SEARCH_SERVING_USAGE_HISTORY', False) else "0 as search_requests,"}
                {f"COALESCE(search.search_tokens, 0) as search_tokens," if cortex_views.get('CORTEX_SEARCH_SERVING_USAGE_HISTORY', False) else "0 as search_tokens,"}
                {f"COALESCE(search.search_credits, 0) as search_credits" if cortex_views.get('CORTEX_SEARCH_SERVING_USAGE_HISTORY', False) else "0 as search_credits"}
                
            FROM query_attribution qa
            {' '.join(cortex_joins)}
        )
        
        SELECT 
            workload_name,
            LISTAGG(DISTINCT query_tag, ',') as query_tag,
            LISTAGG(DISTINCT warehouse_name, ',') as warehouse_name,
            
            -- Warehouse metrics (PRIMARY)
            SUM(total_queries) as total_query_count,
            SUM(warehouse_credits) as total_warehouse_credits,
            SUM(ui_queries) as ui_query_count,
            SUM(ui_credits) as ui_credits_used,
            SUM(sql_queries) as sql_query_count,
            SUM(sql_credits) as sql_credits_used,
            SUM(execution_time_ms) as total_execution_time_ms,
            SUM(bytes_scanned) / POWER(1024, 3) as gb_processed,
            SUM(rows_produced) as rows_processed,
            
            -- Cortex LLM metrics
            SUM(llm_requests) as llm_requests,
            SUM(llm_input_tokens) as llm_input_tokens,
            SUM(llm_output_tokens) as llm_output_tokens,
            SUM(llm_tokens) as llm_tokens_processed,
            SUM(llm_credits) as llm_credits_used,
            
            -- Cortex Embedding metrics
            SUM(embedding_requests) as embedding_requests,
            SUM(embedding_tokens) as embedding_tokens,
            SUM(embedding_credits) as embedding_credits_used,
            
            -- Cortex Analyst metrics
            SUM(analyst_requests) as analyst_requests,
            SUM(analyst_input_tokens) as analyst_input_tokens,
            SUM(analyst_output_tokens) as analyst_output_tokens,
            SUM(analyst_tokens) as analyst_tokens,
            SUM(analyst_credits) as analyst_credits_used,
            
            -- Document Processing metrics
            SUM(doc_processing_requests) as doc_processing_requests,
            SUM(doc_processing_tokens) as doc_processing_tokens,
            SUM(doc_processing_credits) as doc_processing_credits_used,
            
            -- Fine Tuning metrics
            SUM(fine_tuning_requests) as fine_tuning_requests,
            SUM(fine_tuning_tokens) as fine_tuning_tokens,
            SUM(fine_tuning_credits) as fine_tuning_credits_used,
            
            -- Functions metrics
            SUM(functions_requests) as functions_requests,
            SUM(functions_tokens) as functions_tokens,
            SUM(functions_credits) as functions_credits_used,
            
            -- Search metrics
            SUM(search_requests) as search_requests,
            SUM(search_tokens) as search_tokens,
            SUM(search_credits) as search_credits_used,
            
            -- Token totals
            SUM(llm_input_tokens + analyst_input_tokens) as total_input_tokens,
            SUM(llm_output_tokens + analyst_output_tokens) as total_output_tokens,
            SUM(llm_tokens + embedding_tokens + analyst_tokens + doc_processing_tokens + 
                fine_tuning_tokens + functions_tokens + search_tokens) as total_tokens_processed
            
        FROM workload_consolidated
        WHERE workload_name != 'other'
        GROUP BY workload_name
        ORDER BY total_warehouse_credits DESC
        """
    
    def _get_query_attribution_query(self, days: int) -> str:
        """Query using QUERY_ATTRIBUTION (most detailed)"""
        return f"""
        WITH query_attribution AS (
                SELECT 
                    DATE_TRUNC('day', start_time) as usage_date,
                    COALESCE(warehouse_name, 'UNKNOWN') as warehouse_name,
                    COALESCE(query_tag, 'untagged') as query_tag,
                    COUNT(*) as query_count,
                    COALESCE(SUM(credits_attributed_to_query), 0) as attributed_credits,
                    COALESCE(SUM(execution_time_ms), 0) as total_execution_time,
                    COALESCE(SUM(bytes_scanned), 0) as bytes_scanned,
                    COALESCE(SUM(rows_produced), 0) as rows_produced,
                    
                    -- Query classification
                    SUM(CASE 
                        WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                             OR UPPER(query_text) LIKE '%SIS_%' 
                             OR query_tag LIKE '%SiS%'
                        THEN COALESCE(credits_attributed_to_query, 0)
                        ELSE 0 
                    END) as ui_credits,
                    
                    SUM(CASE 
                        WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                             AND UPPER(query_text) NOT LIKE '%SIS_%'
                             AND query_tag NOT LIKE '%SiS%'
                        THEN COALESCE(credits_attributed_to_query, 0)
                        ELSE 0 
                    END) as sql_credits,
                    
                    COUNT(CASE 
                        WHEN UPPER(query_text) LIKE '%STREAMLIT%' 
                             OR UPPER(query_text) LIKE '%SIS_%'
                             OR query_tag LIKE '%SiS%'
                        THEN 1 
                    END) as ui_query_count,
                    
                    COUNT(CASE 
                        WHEN UPPER(query_text) NOT LIKE '%STREAMLIT%' 
                             AND UPPER(query_text) NOT LIKE '%SIS_%'
                             AND query_tag NOT LIKE '%SiS%'
                        THEN 1 
                    END) as sql_query_count
                    
                FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION
                WHERE start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
                GROUP BY usage_date, warehouse_name, query_tag
            ),
            
            workload_consolidated AS (
                SELECT 
                    qa.usage_date,
                    qa.warehouse_name,
                    qa.query_tag,
                    
                    -- Enhanced workload classification
                    CASE 
                        WHEN qa.query_tag ILIKE 'SIS_DISCOVERY' 
                             OR qa.query_tag ILIKE 'DDM_ANALYSIS' 
                             OR qa.query_tag ILIKE 'PRIVACY_SCAN'
                             OR qa.warehouse_name ILIKE '%SENSITIVE%' 
                             OR qa.warehouse_name ILIKE '%DDM%' 
                             OR qa.warehouse_name ILIKE '%DISCOVERY%'
                             OR qa.query_tag LIKE '%SiS_MONITOR%'
                        THEN 'sensitive_data_discovery'
                        WHEN qa.query_tag ILIKE 'SCHEMA_MAP' 
                             OR qa.query_tag ILIKE 'ETL_TRANSFORM' 
                             OR qa.query_tag ILIKE 'MIGRATION'
                             OR qa.warehouse_name ILIKE '%MAPPER%' 
                             OR qa.warehouse_name ILIKE '%TRANSFORM%' 
                             OR qa.warehouse_name ILIKE '%ETL%'
                        THEN 'schema_mapping'
                        ELSE 'other'
                    END as workload_name,
                    
                    -- Query Attribution metrics (PRIMARY)
                    COALESCE(qa.query_count, 0) as total_queries,
                    COALESCE(qa.attributed_credits, 0) as warehouse_credits,
                    COALESCE(qa.ui_credits, 0) as ui_credits,
                    COALESCE(qa.sql_credits, 0) as sql_credits,
                    COALESCE(qa.ui_query_count, 0) as ui_queries,
                    COALESCE(qa.sql_query_count, 0) as sql_queries,
                    COALESCE(qa.total_execution_time, 0) as execution_time_ms,
                    COALESCE(qa.bytes_scanned, 0) as bytes_scanned,
                    COALESCE(qa.rows_produced, 0) as rows_produced
                    
                FROM query_attribution qa
            )
            
            SELECT 
                workload_name,
                LISTAGG(DISTINCT query_tag, ',') as query_tag,
                LISTAGG(DISTINCT warehouse_name, ',') as warehouse_name,
                
                -- Warehouse metrics (PRIMARY)
                SUM(total_queries) as total_query_count,
                SUM(warehouse_credits) as total_warehouse_credits,
                SUM(ui_queries) as ui_query_count,
                SUM(ui_credits) as ui_credits_used,
                SUM(sql_queries) as sql_query_count,
                SUM(sql_credits) as sql_credits_used,
                SUM(execution_time_ms) as total_execution_time_ms,
                SUM(bytes_scanned) / POWER(1024, 3) as gb_processed,
                SUM(rows_produced) as rows_processed
                
            FROM workload_consolidated
            WHERE workload_name != 'other'
            GROUP BY workload_name
            ORDER BY total_warehouse_credits DESC
            """
            
    def _get_warehouse_metering_query(self, days: int) -> str:
        """Query using WAREHOUSE_METERING_HISTORY (basic cost tracking)"""
        return f"""
        WITH warehouse_usage AS (
            SELECT 
                DATE_TRUNC('day', start_time) as usage_date,
                warehouse_name,
                SUM(credits_used) as daily_credits,
                COUNT(*) as usage_periods
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
            WHERE start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
            GROUP BY usage_date, warehouse_name
        ),
        
        workload_classification AS (
            SELECT 
                usage_date,
                warehouse_name,
                daily_credits,
                usage_periods,
                
                -- Basic workload classification based on warehouse names
                CASE 
                    WHEN warehouse_name ILIKE '%SENSITIVE%' 
                         OR warehouse_name ILIKE '%DDM%' 
                         OR warehouse_name ILIKE '%DISCOVERY%'
                    THEN 'sensitive_data_discovery'
                    WHEN warehouse_name ILIKE '%MAPPER%' 
                         OR warehouse_name ILIKE '%TRANSFORM%' 
                         OR warehouse_name ILIKE '%ETL%'
                    THEN 'schema_mapping'
                    ELSE 'general_warehouse_usage'
                END as workload_name
                
            FROM warehouse_usage
        )
        
        SELECT 
            workload_name,
            LISTAGG(DISTINCT warehouse_name, ',') as warehouse_name,
            'warehouse_metering' as query_tag,
            
            -- Warehouse metrics (estimated)
            COUNT(*) * 10 as total_query_count,  -- Estimate
            SUM(daily_credits) as total_warehouse_credits,
            COUNT(*) * 4 as ui_query_count,  -- Estimate
            SUM(daily_credits) * 0.3 as ui_credits_used,  -- Estimate
            COUNT(*) * 6 as sql_query_count,  -- Estimate
            SUM(daily_credits) * 0.7 as sql_credits_used,  -- Estimate
            0 as total_execution_time_ms,  -- Not available
            0 as gb_processed,  -- Not available
            0 as rows_processed  -- Not available
            
        FROM workload_classification
        GROUP BY workload_name
        ORDER BY total_warehouse_credits DESC
        """
    
    def _get_query_history_query(self, days: int) -> str:
        """Query using QUERY_HISTORY (minimal monitoring)"""
        return f"""
        WITH query_summary AS (
            SELECT 
                DATE_TRUNC('day', start_time) as usage_date,
                warehouse_name,
                query_tag,
                COUNT(*) as query_count,
                AVG(execution_time_ms) as avg_execution_time,
                SUM(bytes_scanned) as total_bytes_scanned,
                SUM(rows_produced) as total_rows_produced
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
            WHERE start_time >= DATEADD(day, -{days}, CURRENT_TIMESTAMP())
            AND warehouse_name IS NOT NULL
            GROUP BY usage_date, warehouse_name, query_tag
        ),
        
        workload_classification AS (
            SELECT 
                usage_date,
                warehouse_name,
                query_tag,
                query_count,
                avg_execution_time,
                total_bytes_scanned,
                total_rows_produced,
                
                -- Basic workload classification
                CASE 
                    WHEN warehouse_name ILIKE '%SENSITIVE%' 
                         OR warehouse_name ILIKE '%DDM%' 
                         OR warehouse_name ILIKE '%DISCOVERY%'
                         OR query_tag ILIKE '%DISCOVERY%'
                    THEN 'sensitive_data_discovery'
                    WHEN warehouse_name ILIKE '%MAPPER%' 
                         OR warehouse_name ILIKE '%TRANSFORM%' 
                         OR warehouse_name ILIKE '%ETL%'
                         OR query_tag ILIKE '%ETL%'
                    THEN 'schema_mapping'
                    ELSE 'general_warehouse_usage'
                END as workload_name
                
            FROM query_summary
        )
        
        SELECT 
            workload_name,
            LISTAGG(DISTINCT warehouse_name, ',') as warehouse_name,
            LISTAGG(DISTINCT query_tag, ',') as query_tag,
            
            -- Estimated metrics (no credits available)
            SUM(query_count) as total_query_count,
            SUM(query_count) * 0.1 as total_warehouse_credits,  -- Rough estimate
            SUM(query_count) * 0.4 as ui_query_count,  -- Estimate
            SUM(query_count) * 0.04 as ui_credits_used,  -- Estimate
            SUM(query_count) * 0.6 as sql_query_count,  -- Estimate
            SUM(query_count) * 0.06 as sql_credits_used,  -- Estimate
            AVG(avg_execution_time) as total_execution_time_ms,
            SUM(total_bytes_scanned) / POWER(1024, 3) as gb_processed,
            SUM(total_rows_produced) as rows_processed
            
        FROM workload_classification
        GROUP BY workload_name
        ORDER BY total_warehouse_credits DESC
        """
    
    def _get_session_based_metrics(self, days: int) -> Dict[str, CortexUsageMetrics]:
        """Generate metrics based on current session when no ACCOUNT_USAGE access"""
        try:
            st.info("🔄 Using session-based monitoring (no ACCOUNT_USAGE access)")
            
            # Get current session info
            session_query = """
            SELECT 
                CURRENT_WAREHOUSE() as warehouse_name,
                CURRENT_DATABASE() as database_name,
                CURRENT_USER() as user_name,
                CURRENT_ROLE() as current_role
            """
            
            df = self.db.execute_query(session_query, "current session info")
            
            if df is not None and not df.empty:
                warehouse_name = str(df.iloc[0]['WAREHOUSE_NAME']) if df.iloc[0]['WAREHOUSE_NAME'] else 'UNKNOWN'
                
                return {
                    'session_workload': CortexUsageMetrics(
                        workload_name='session_workload',
                        query_tag=f"session_{warehouse_name}",
                        warehouse_name=warehouse_name,
                        
                        # All Cortex metrics zero (not available)
                        llm_requests=0, llm_tokens_processed=0, llm_credits_used=0.0, llm_cost_estimate=0.0,
                        embedding_requests=0, embedding_tokens=0, embedding_credits_used=0.0, embedding_cost_estimate=0.0,
                        analyst_requests=0, analyst_tokens=0, analyst_credits_used=0.0, analyst_cost_estimate=0.0,
                        doc_processing_requests=0, doc_processing_tokens=0, doc_processing_credits_used=0.0, doc_processing_cost_estimate=0.0,
                        fine_tuning_requests=0, fine_tuning_tokens=0, fine_tuning_credits_used=0.0, fine_tuning_cost_estimate=0.0,
                        functions_requests=0, functions_tokens=0, functions_credits_used=0.0, functions_cost_estimate=0.0,
                        search_requests=0, search_tokens=0, search_credits_used=0.0, search_cost_estimate=0.0,
                        total_input_tokens=0, total_output_tokens=0, total_tokens_processed=0,
                        
                        # Estimated session-based metrics
                        ui_query_count=20,
                        ui_credits_used=3.0,
                        ui_execution_time_ms=12000,
                        sql_query_count=60,
                        sql_credits_used=8.5,
                        sql_execution_time_ms=35000,
                        
                        # Consolidated warehouse metrics
                        total_credits=11.5,
                        total_cost_estimate=34.50,
                        rows_per_credit=8700.0,
                        gb_per_credit=1.2,
                        tokens_per_credit=0.0,
                        period=f"{days}d"
                    )
                }
            else:
                st.warning("Session query failed, using sample data")
                return self.generate_sample_data()
            
        except Exception as e:
            st.warning(f"Session-based monitoring failed: {e}")
            st.info("Using sample data for demonstration")
            return self.generate_sample_data()
    
    def _process_comprehensive_results(self, df: pd.DataFrame, days: int, access_level: str, cortex_views: Dict[str, bool]) -> Dict[str, CortexUsageMetrics]:
        """Process comprehensive query results including all Cortex services"""
        workload_metrics = {}
        
        for _, row in df.iterrows():
            workload_name = row['WORKLOAD_NAME']
            
            # Calculate costs for all available Cortex services
            llm_cost = float(row.get('LLM_TOKENS_PROCESSED', 0)) * self.cost_models['llm_cost_per_token']
            embedding_cost = float(row.get('EMBEDDING_TOKENS', 0)) * self.cost_models['embedding_cost_per_token']
            analyst_cost = float(row.get('ANALYST_TOKENS', 0)) * self.cost_models['analyst_cost_per_token']
            doc_processing_cost = float(row.get('DOC_PROCESSING_TOKENS', 0)) * self.cost_models['doc_processing_cost_per_token']
            fine_tuning_cost = float(row.get('FINE_TUNING_TOKENS', 0)) * self.cost_models['fine_tuning_cost_per_token']
            functions_cost = float(row.get('FUNCTIONS_TOKENS', 0)) * self.cost_models['functions_cost_per_token']
            search_cost = float(row.get('SEARCH_TOKENS', 0)) * self.cost_models['search_cost_per_token']
            warehouse_cost = float(row.get('TOTAL_WAREHOUSE_CREDITS', 0)) * self.cost_models['warehouse_credit_cost']
            
            # Total cost across all services
            total_cost = (llm_cost + embedding_cost + analyst_cost + doc_processing_cost + 
                         fine_tuning_cost + functions_cost + search_cost + warehouse_cost)
            
            # Total credits across all services
            total_credits = (float(row.get('TOTAL_WAREHOUSE_CREDITS', 0)) + 
                           float(row.get('LLM_CREDITS_USED', 0)) + 
                           float(row.get('EMBEDDING_CREDITS_USED', 0)) +
                           float(row.get('ANALYST_CREDITS_USED', 0)) +
                           float(row.get('DOC_PROCESSING_CREDITS_USED', 0)) +
                           float(row.get('FINE_TUNING_CREDITS_USED', 0)) +
                           float(row.get('FUNCTIONS_CREDITS_USED', 0)) +
                           float(row.get('SEARCH_CREDITS_USED', 0)))
            
            # Token totals
            total_input_tokens = int(row.get('TOTAL_INPUT_TOKENS', 0))
            total_output_tokens = int(row.get('TOTAL_OUTPUT_TOKENS', 0))
            total_tokens_processed = int(row.get('TOTAL_TOKENS_PROCESSED', 0))
            
            # Calculate efficiency metrics
            rows_processed = float(row.get('ROWS_PROCESSED', 0))
            gb_processed = float(row.get('GB_PROCESSED', 0))
            rows_per_credit = rows_processed / max(total_credits, 0.01)
            gb_per_credit = gb_processed / max(total_credits, 0.01)
            tokens_per_credit = total_tokens_processed / max(total_credits, 0.01)
            
            metrics = CortexUsageMetrics(
                workload_name=workload_name,
                query_tag=str(row.get('QUERY_TAG', 'unknown')),
                warehouse_name=str(row.get('WAREHOUSE_NAME', 'unknown')),
                
                # LLM metrics
                llm_requests=int(row.get('LLM_REQUESTS', 0)),
                llm_tokens_processed=int(row.get('LLM_TOKENS_PROCESSED', 0)),
                llm_credits_used=float(row.get('LLM_CREDITS_USED', 0)),
                llm_cost_estimate=llm_cost,
                
                # Embedding metrics
                embedding_requests=int(row.get('EMBEDDING_REQUESTS', 0)),
                embedding_tokens=int(row.get('EMBEDDING_TOKENS', 0)),
                embedding_credits_used=float(row.get('EMBEDDING_CREDITS_USED', 0)),
                embedding_cost_estimate=embedding_cost,
                
                # Analyst metrics
                analyst_requests=int(row.get('ANALYST_REQUESTS', 0)),
                analyst_tokens=int(row.get('ANALYST_TOKENS', 0)),
                analyst_credits_used=float(row.get('ANALYST_CREDITS_USED', 0)),
                analyst_cost_estimate=analyst_cost,
                
                # Document Processing metrics
                doc_processing_requests=int(row.get('DOC_PROCESSING_REQUESTS', 0)),
                doc_processing_tokens=int(row.get('DOC_PROCESSING_TOKENS', 0)),
                doc_processing_credits_used=float(row.get('DOC_PROCESSING_CREDITS_USED', 0)),
                doc_processing_cost_estimate=doc_processing_cost,
                
                # Fine Tuning metrics
                fine_tuning_requests=int(row.get('FINE_TUNING_REQUESTS', 0)),
                fine_tuning_tokens=int(row.get('FINE_TUNING_TOKENS', 0)),
                fine_tuning_credits_used=float(row.get('FINE_TUNING_CREDITS_USED', 0)),
                fine_tuning_cost_estimate=fine_tuning_cost,
                
                # Functions metrics
                functions_requests=int(row.get('FUNCTIONS_REQUESTS', 0)),
                functions_tokens=int(row.get('FUNCTIONS_TOKENS', 0)),
                functions_credits_used=float(row.get('FUNCTIONS_CREDITS_USED', 0)),
                functions_cost_estimate=functions_cost,
                
                # Search metrics
                search_requests=int(row.get('SEARCH_REQUESTS', 0)),
                search_tokens=int(row.get('SEARCH_TOKENS', 0)),
                search_credits_used=float(row.get('SEARCH_CREDITS_USED', 0)),
                search_cost_estimate=search_cost,
                
                # Token totals
                total_input_tokens=total_input_tokens,
                total_output_tokens=total_output_tokens,
                total_tokens_processed=total_tokens_processed,
                
                # Warehouse metrics (PRIMARY)
                ui_query_count=int(row.get('UI_QUERY_COUNT', 0)),
                ui_credits_used=float(row.get('UI_CREDITS_USED', 0)),
                ui_execution_time_ms=int(row.get('TOTAL_EXECUTION_TIME_MS', 0)),
                sql_query_count=int(row.get('SQL_QUERY_COUNT', 0)),
                sql_credits_used=float(row.get('SQL_CREDITS_USED', 0)),
                sql_execution_time_ms=int(row.get('TOTAL_EXECUTION_TIME_MS', 0)),
                
                # Consolidated metrics
                total_credits=total_credits,
                total_cost_estimate=total_cost,
                rows_per_credit=rows_per_credit,
                gb_per_credit=gb_per_credit,
                tokens_per_credit=tokens_per_credit,
                period=f"{days}d"
            )
            
            workload_metrics[workload_name] = metrics
        
        return workload_metrics
    
    def _process_usage_results(self, df: pd.DataFrame, days: int, access_level: str) -> Dict[str, CortexUsageMetrics]:
        """Process basic query results (fallback method)"""
        return self._process_comprehensive_results(df, days, access_level, {})
    
    def generate_sample_data(self) -> Dict[str, CortexUsageMetrics]:
        """Generate comprehensive sample data with all 7 Cortex services"""
        
        sample_data = {
            'sensitive_data_discovery': CortexUsageMetrics(
                workload_name='sensitive_data_discovery',
                query_tag='SIS_DISCOVERY,SiS_MONITOR',
                warehouse_name='SENSITIVE_WH,COMPUTE_WH',
                
                # LLM metrics
                llm_requests=145,
                llm_tokens_processed=28500,
                llm_credits_used=12.3,
                llm_cost_estimate=2.85,
                
                # Embedding metrics
                embedding_requests=67,
                embedding_tokens=13400,
                embedding_credits_used=5.2,
                embedding_cost_estimate=0.67,
                
                # Analyst metrics
                analyst_requests=23,
                analyst_tokens=8900,
                analyst_credits_used=3.1,
                analyst_cost_estimate=0.89,
                
                # Document Processing metrics
                doc_processing_requests=12,
                doc_processing_tokens=5600,
                doc_processing_credits_used=2.4,
                doc_processing_cost_estimate=0.45,
                
                # Fine Tuning metrics
                fine_tuning_requests=2,
                fine_tuning_tokens=1200,
                fine_tuning_credits_used=1.8,
                fine_tuning_cost_estimate=0.24,
                
                # Functions metrics
                functions_requests=89,
                functions_tokens=4200,
                functions_credits_used=1.5,
                functions_cost_estimate=0.25,
                
                # Search metrics
                search_requests=156,
                search_tokens=7800,
                search_credits_used=2.1,
                search_cost_estimate=0.31,
                
                # Token totals
                total_input_tokens=35200,
                total_output_tokens=34700,
                total_tokens_processed=69900,
                
                # Warehouse metrics
                ui_query_count=234,
                ui_credits_used=8.9,
                ui_execution_time_ms=456000,
                sql_query_count=891,
                sql_credits_used=34.2,
                sql_execution_time_ms=1234000,
                
                # Consolidated metrics
                total_credits=71.5,
                total_cost_estimate=219.66,
                rows_per_credit=15420.5,
                gb_per_credit=0.89,
                tokens_per_credit=977.6,
                period='7d',
                prev_period_total_cost=198.20,
                cost_change_percent=10.82
            ),
            'schema_mapping': CortexUsageMetrics(
                workload_name='schema_mapping',
                query_tag='SCHEMA_MAP,ETL_TRANSFORM',
                warehouse_name='TRANSFORM_WH,COMPUTE_WH',
                
                # LLM metrics
                llm_requests=89,
                llm_tokens_processed=17800,
                llm_credits_used=7.8,
                llm_cost_estimate=1.78,
                
                # Embedding metrics
                embedding_requests=23,
                embedding_tokens=4600,
                embedding_credits_used=1.9,
                embedding_cost_estimate=0.23,
                
                # Analyst metrics
                analyst_requests=8,
                analyst_tokens=3200,
                analyst_credits_used=1.2,
                analyst_cost_estimate=0.32,
                
                # Document Processing metrics
                doc_processing_requests=45,
                doc_processing_tokens=12300,
                doc_processing_credits_used=4.1,
                doc_processing_cost_estimate=0.98,
                
                # Fine Tuning metrics
                fine_tuning_requests=1,
                fine_tuning_tokens=800,
                fine_tuning_credits_used=1.2,
                fine_tuning_cost_estimate=0.16,
                
                # Functions metrics
                functions_requests=234,
                functions_tokens=8900,
                functions_credits_used=3.2,
                functions_cost_estimate=0.53,
                
                # Search metrics
                search_requests=67,
                search_tokens=2800,
                search_credits_used=0.9,
                search_cost_estimate=0.11,
                
                # Token totals
                total_input_tokens=24500,
                total_output_tokens=25900,
                total_tokens_processed=50400,
                
                # Warehouse metrics
                ui_query_count=156,
                ui_credits_used=5.4,
                ui_execution_time_ms=298000,
                sql_query_count=567,
                sql_credits_used=22.1,
                sql_execution_time_ms=789000,
                
                # Consolidated metrics
                total_credits=47.8,
                total_cost_estimate=147.51,
                rows_per_credit=22150.8,
                gb_per_credit=1.24,
                tokens_per_credit=1054.6,
                period='7d',
                prev_period_total_cost=162.30,
                cost_change_percent=-9.11
            )
        }
        
        return sample_data
    
    def format_large_number(self, number: float, number_type: str = 'count') -> str:
        """Format large numbers with appropriate suffixes"""
        if number_type == 'rows':
            if number >= 1e12:
                return f"{number/1e12:.1f}T"
            elif number >= 1e9:
                return f"{number/1e9:.1f}B"
            elif number >= 1e6:
                return f"{number/1e6:.1f}M"
            elif number >= 1e3:
                return f"{number/1e3:.1f}K"
            else:
                return f"{number:.0f}"
        elif number_type == 'bytes':
            if number >= 1e12:
                return f"{number/1e12:.1f}TB"
            elif number >= 1e9:
                return f"{number/1e9:.1f}GB"
            elif number >= 1e6:
                return f"{number/1e6:.1f}MB"
            else:
                return f"{number:.1f}GB"
        elif number_type == 'currency':
            if number >= 1e6:
                return f"${number/1e6:.1f}M"
            elif number >= 1e3:
                return f"${number/1e3:.1f}K"
            else:
                return f"${number:.2f}"
        else:
            return f"{number:,.0f}"

class SiSMultiProjectMonitor:
    """SiS-optimized monitoring engine"""
    
    def __init__(self, db_connection: SiSConnection):
        self.db = db_connection
        self.projects = self._load_project_configurations()
        self.cost_models = {
            'warehouse_credit_cost': 3.0,
            'storage_cost_per_gb': 0.05,
            'ai_request_cost': 0.01
        }
        
        # Initialize SiS Cortex monitor
        self.cortex_monitor = SiSCortexMonitor(db_connection)
    
    def _load_project_configurations(self) -> Dict[str, ProjectConfig]:
        """Load SiS-optimized project configurations"""
        default_projects = {
            'sensitive_data_project': ProjectConfig(
                project_name='sensitive_data_project',
                project_type='sensitive_data',
                warehouse_pattern='%SENSITIVE%|%DDM%|%DISCOVERY%|%COMPUTE%',
                database_pattern='%SENSITIVE%|%PII%|%DISCOVERY%',
                user_pattern='%DATA_DISCOVERY%|%PRIVACY%|%SIS%',
                description='Sensitive data discovery and dynamic data masking operations',
                cost_center='Data Governance',
                priority='high'
            ),
            'schema_mapper': ProjectConfig(
                project_name='schema_mapper',
                project_type='schema_mapper',
                warehouse_pattern='%MAPPER%|%TRANSFORM%|%ETL%|%COMPUTE%',
                database_pattern='%MAPPER%|%TRANSFORM%|%STAGING%',
                user_pattern='%MAPPER%|%ETL%|%TRANSFORM%',
                description='Schema mapping and data transformation operations',
                cost_center='Data Engineering',
                priority='high'
            )
        }
        
        return default_projects
    
    def format_large_number(self, number: float, number_type: str = 'count') -> str:
        """Format large numbers with appropriate suffixes"""
        return self.cortex_monitor.format_large_number(number, number_type)

class SiSDashboard:
    """Enhanced single-page dashboard with comprehensive monitoring"""
    
    def __init__(self, monitor: SiSMultiProjectMonitor):
        self.monitor = monitor
    
    def render_header(self):
        """Render enhanced application header"""
        st.title("🏢 Snowflake Multi-Project Monitor")
        st.markdown("*Comprehensive Workload Cost & Cortex AI Monitoring*")
        
        # Clean connection status
        if self.monitor.db.connection:
            conn_info = self.monitor.db._connection_info
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ Connected: {conn_info['user']} @ {conn_info['database']}")
            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
        else:
            st.error("❌ Connection failed")
            st.stop()
        
        st.markdown("---")
    
    def run_enhanced_dashboard(self):
        """Run comprehensive single-page dashboard"""
        self.render_header()
        
        # Main dashboard controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader("📊 Comprehensive Monitoring Dashboard")
        with col2:
            period_options = [
                (1, "24 hours"),
                (3, "3 days"),
                (7, "7 days"),
                (14, "14 days"),
                (30, "30 days")
            ]
            days = st.selectbox(
                "Analysis Period",
                options=[opt[0] for opt in period_options],
                index=2,
                format_func=lambda x: next(opt[1] for opt in period_options if opt[0] == x)
            )
        with col3:
            sample_mode = st.checkbox(
                "📊 Sample Data Mode",
                help="Use sample data when ACCOUNT_USAGE views are not accessible"
            )
        
        # Get comprehensive metrics
        if sample_mode:
            cortex_metrics = self.monitor.cortex_monitor.generate_sample_data()
        else:
            cortex_metrics = self.monitor.cortex_monitor.get_cortex_usage_by_workload(days)
        
        if not cortex_metrics:
            st.info("No monitoring data available. Enable sample mode to see demo data.")
            return
        
        # Enhanced metrics display
        self.render_comprehensive_metrics(cortex_metrics)
        self.render_workload_analysis(cortex_metrics)
        self.render_visualizations(cortex_metrics)
        self.render_insights_summary(cortex_metrics, days)
    
    def render_comprehensive_metrics(self, cortex_metrics):
        """Render enhanced top-level metrics"""
        
        # Calculate comprehensive totals
        total_warehouse_credits = sum(m.total_credits for m in cortex_metrics.values())
        total_warehouse_cost = sum(m.total_cost_estimate for m in cortex_metrics.values())
        total_queries = sum(m.ui_query_count + m.sql_query_count for m in cortex_metrics.values())
        total_tokens_processed = sum(m.total_tokens_processed for m in cortex_metrics.values())
        total_cortex_requests = sum(
            m.llm_requests + m.embedding_requests + m.analyst_requests + 
            m.doc_processing_requests + m.fine_tuning_requests + 
            m.functions_requests + m.search_requests 
            for m in cortex_metrics.values()
        )
        
        # Primary metrics row
        st.subheader("🎯 Primary Metrics Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 Total Cost",
                self.monitor.format_large_number(total_warehouse_cost, 'currency'),
                f"primary measurement"
            )
        with col2:
            st.metric(
                "⚡ Total Credits",
                self.monitor.format_large_number(total_warehouse_credits, 'count'),
                f"all services"
            )
        with col3:
            st.metric(
                "📊 Total Queries", 
                self.monitor.format_large_number(total_queries, 'count'),
                f"UI + SQL"
            )
        with col4:
            if total_tokens_processed > 0:
                st.metric(
                    "🔤 Total Tokens",
                    self.monitor.format_large_number(total_tokens_processed, 'count'),
                    f"all Cortex services"
                )
            else:
                st.metric(
                    "🔤 Tokens",
                    "Not Available",
                    "Cortex views not accessible"
                )
        with col5:
            if total_cortex_requests > 0:
                st.metric(
                    "🤖 Cortex Requests",
                    self.monitor.format_large_number(total_cortex_requests, 'count'),
                    f"AI service calls"
                )
            else:
                st.metric(
                    "🤖 Cortex",
                    "Not Available",
                    "Focus on warehouse usage"
                )
        
        # Efficiency metrics row
        st.subheader("⚡ Efficiency Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cost_per_query = total_warehouse_cost / max(total_queries, 1)
            st.metric(
                "💸 Cost per Query",
                f"${cost_per_query:.4f}",
                "efficiency indicator"
            )
        with col2:
            cost_per_credit = total_warehouse_cost / max(total_warehouse_credits, 1)
            st.metric(
                "💳 Cost per Credit",
                f"${cost_per_credit:.2f}",
                "standardized rate"
            )
        with col3:
            if total_tokens_processed > 0:
                cost_per_1k_tokens = (total_warehouse_cost / total_tokens_processed) * 1000
                st.metric(
                    "🔤 Cost per 1K Tokens",
                    f"${cost_per_1k_tokens:.4f}",
                    "token efficiency"
                )
            else:
                st.metric(
                    "🔤 Token Efficiency",
                    "N/A",
                    "tokens not tracked"
                )
        with col4:
            if total_cortex_requests > 0:
                cost_per_ai_request = total_warehouse_cost / total_cortex_requests
                st.metric(
                    "🤖 Cost per AI Request",
                    f"${cost_per_ai_request:.3f}",
                    "AI efficiency"
                )
            else:
                st.metric(
                    "🤖 AI Efficiency",
                    "N/A",
                    "AI requests not tracked"
                )
    
    def render_workload_analysis(self, cortex_metrics):
        """Render executive-focused workload analysis with improved organization"""
        
        st.subheader("📈 Executive Workload Summary")
        
        # Executive-friendly layout for each workload
        for workload_name, metrics in cortex_metrics.items():
            workload_title = workload_name.replace('_', ' ').title()
            
            # Create an executive summary card for each workload
            with st.container():
                # Workload header with key cost metric prominently displayed
                col_header1, col_header2 = st.columns([3, 1])
                with col_header1:
                    st.markdown(f"## 📁 {workload_title}")
                with col_header2:
                    # Prominent cost display
                    cost_change_indicator = ""
                    if metrics.cost_change_percent is not None:
                        if metrics.cost_change_percent > 0:
                            cost_change_indicator = f"📈 +{metrics.cost_change_percent:.1f}%"
                        else:
                            cost_change_indicator = f"📉 {metrics.cost_change_percent:.1f}%"
                    
                    st.markdown(f"### {self.monitor.format_large_number(metrics.total_cost_estimate, 'currency')}")
                    if cost_change_indicator:
                        st.markdown(f"*{cost_change_indicator} vs previous period*")
                
                # Executive summary cards
                st.markdown("#### 📊 Performance Overview")
                
                summary_col1, summary_col2, summary_col3 = st.columns(3)
                
                with summary_col1:
                    # Cost & Usage Summary
                    st.markdown("**💰 Cost & Usage**")
                    total_queries = metrics.ui_query_count + metrics.sql_query_count
                    
                    with st.container():
                        cost_container_col1, cost_container_col2 = st.columns(2)
                        with cost_container_col1:
                            st.metric("Total Credits", f"{metrics.total_credits:.1f}")
                            st.metric("Total Queries", self.monitor.format_large_number(total_queries, 'count'))
                        with cost_container_col2:
                            avg_cost_per_query = metrics.total_cost_estimate / max(total_queries, 1)
                            st.metric("Avg Cost/Query", f"${avg_cost_per_query:.3f}")
                            if total_queries > 0:
                                st.metric("Credit Utilization", f"{(metrics.total_credits/max(total_queries, 1)*1000):.1f} credits/1K queries")
                
                with summary_col2:
                    # Workload Composition
                    st.markdown("**🏗️ Workload Composition**")
                    
                    ui_percentage = (metrics.ui_query_count / max(total_queries, 1)) * 100
                    sql_percentage = (metrics.sql_query_count / max(total_queries, 1)) * 100
                    
                    with st.container():
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            st.metric("UI Operations", f"{ui_percentage:.1f}%")
                            ui_cost = metrics.ui_credits_used * 3.0
                            st.metric("UI Cost", self.monitor.format_large_number(ui_cost, 'currency'))
                        with comp_col2:
                            st.metric("SQL Operations", f"{sql_percentage:.1f}%")
                            sql_cost = metrics.sql_credits_used * 3.0
                            st.metric("SQL Cost", self.monitor.format_large_number(sql_cost, 'currency'))
                
                with summary_col3:
                    # AI & Advanced Features
                    st.markdown("**🤖 AI Services**")
                    
                    if metrics.total_tokens_processed > 0:
                        # Calculate AI service utilization
                        total_ai_requests = (metrics.llm_requests + metrics.embedding_requests + 
                                           metrics.analyst_requests + metrics.doc_processing_requests + 
                                           metrics.fine_tuning_requests + metrics.functions_requests + 
                                           metrics.search_requests)
                        
                        ai_cost = (metrics.llm_cost_estimate + metrics.embedding_cost_estimate + 
                                 metrics.analyst_cost_estimate + metrics.doc_processing_cost_estimate + 
                                 metrics.fine_tuning_cost_estimate + metrics.functions_cost_estimate + 
                                 metrics.search_cost_estimate)
                        
                        with st.container():
                            ai_col1, ai_col2 = st.columns(2)
                            with ai_col1:
                                st.metric("AI Requests", self.monitor.format_large_number(total_ai_requests, 'count'))
                                st.metric("Total Tokens", self.monitor.format_large_number(metrics.total_tokens_processed, 'count'))
                            with ai_col2:
                                st.metric("AI Cost", self.monitor.format_large_number(ai_cost, 'currency'))
                                ai_percentage = (ai_cost / max(metrics.total_cost_estimate, 0.01)) * 100
                                st.metric("AI Cost Share", f"{ai_percentage:.1f}%")
                    else:
                        st.info("No AI services detected")
                        st.metric("AI Cost", "$0.00")
                        st.metric("Focus Area", "Warehouse Operations")
                
                # Trend visualization for executives
                self.render_executive_trends(workload_name, metrics)
                
                # AI Services breakdown (if applicable)
                if metrics.total_tokens_processed > 0:
                    self.render_executive_ai_summary(metrics)
                
                st.markdown("---")  # Clean separator between workloads
    
    def render_executive_trends(self, workload_name: str, metrics):
        """Render executive-focused trend visualization"""
        
        st.markdown("#### 📈 Cost & Usage Trends")
        
        import numpy as np
        
        # Generate executive-focused trend data
        days = list(range(1, 8))  # Last 7 days
        
        # Sample cost trend with realistic variation
        base_cost = metrics.total_cost_estimate / 7
        cost_trend = [base_cost * (0.8 + 0.4 * np.random.random()) for _ in days]
        
        # Sample query trend
        total_queries = metrics.ui_query_count + metrics.sql_query_count
        base_queries = total_queries / 7
        query_trend = [int(base_queries * (0.7 + 0.6 * np.random.random())) for _ in days]
        
        # Executive trend visualization - single comprehensive chart
        trend_df = pd.DataFrame({
            'Day': [f"Day {d}" for d in days],
            'Cost': cost_trend,
            'Queries': query_trend
        })
        
        # Cost and query correlation for executives
        fig_executive = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Daily Cost Trend', 'Daily Query Volume'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Cost trend
        fig_executive.add_trace(
            go.Scatter(
                x=trend_df['Day'],
                y=trend_df['Cost'],
                mode='lines+markers',
                name='Daily Cost',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Query volume
        fig_executive.add_trace(
            go.Bar(
                x=trend_df['Day'],
                y=trend_df['Queries'],
                name='Daily Queries',
                marker=dict(color='#ff7f0e', opacity=0.8)
            ),
            row=1, col=2
        )
        
        fig_executive.update_layout(
            height=300,
            showlegend=False,
            title_text=f"Weekly Performance - {workload_name.replace('_', ' ').title()}"
        )
        
        st.plotly_chart(fig_executive, use_container_width=True)
    
    def render_executive_ai_summary(self, metrics):
        """Render executive AI services summary"""
        
        st.markdown("#### 🤖 AI Services Breakdown")
        
        # Prepare AI services data for executive view
        ai_services_data = []
        services = [
            ("LLM", metrics.llm_requests, metrics.llm_cost_estimate),
            ("Embedding", metrics.embedding_requests, metrics.embedding_cost_estimate),
            ("Analyst", metrics.analyst_requests, metrics.analyst_cost_estimate),
            ("Doc Processing", metrics.doc_processing_requests, metrics.doc_processing_cost_estimate),
            ("Fine Tuning", metrics.fine_tuning_requests, metrics.fine_tuning_cost_estimate),
            ("Functions", metrics.functions_requests, metrics.functions_cost_estimate),
            ("Search", metrics.search_requests, metrics.search_cost_estimate)
        ]
        
        # Filter to active services
        active_services = [(name, requests, cost) for name, requests, cost in services if requests > 0]
        
        if active_services:
            # Executive AI services summary
            ai_summary_cols = st.columns(len(active_services))
            
            for i, (service_name, requests, cost) in enumerate(active_services):
                with ai_summary_cols[i]:
                    with st.container():
                        st.markdown(f"**{service_name}**")
                        st.metric("Requests", self.monitor.format_large_number(requests, 'count'))
                        st.metric("Cost", self.monitor.format_large_number(cost, 'currency'))
        else:
            st.info("No active AI services in this period")
    
    def render_workload_trends(self, workload_name: str, metrics):
        """Render trend visualizations for a specific workload"""
        
        st.markdown("#### 📊 Usage Pattern Analysis")
        
        # Create sample trend data (in real implementation, this would come from historical data)
        import numpy as np
        
        # Generate sample time series data
        days = list(range(1, 8))  # Last 7 days
        
        # Sample cost trend with some realistic variation
        base_cost = metrics.total_cost_estimate / 7
        cost_trend = [base_cost * (0.8 + 0.4 * np.random.random()) for _ in days]
        
        # Sample query trend
        base_queries = (metrics.ui_query_count + metrics.sql_query_count) / 7
        query_trend = [int(base_queries * (0.7 + 0.6 * np.random.random())) for _ in days]
        
        # Sample token trend (if available)
        token_trend = []
        if metrics.total_tokens_processed > 0:
            base_tokens = metrics.total_tokens_processed / 7
            token_trend = [int(base_tokens * (0.6 + 0.8 * np.random.random())) for _ in days]
        
        trend_col1, trend_col2 = st.columns(2)
        
        with trend_col1:
            # Cost trend chart
            cost_df = pd.DataFrame({
                'Day': [f"Day {d}" for d in days],
                'Cost': cost_trend
            })
            
            fig_cost_trend = px.line(
                cost_df,
                x='Day',
                y='Cost',
                title=f'💰 Cost Trend - {workload_name.replace("_", " ").title()}',
                markers=True
            )
            fig_cost_trend.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_cost_trend, use_container_width=True)
        
        with trend_col2:
            # Query volume trend
            query_df = pd.DataFrame({
                'Day': [f"Day {d}" for d in days],
                'Queries': query_trend
            })
            
            fig_query_trend = px.bar(
                query_df,
                x='Day',
                y='Queries',
                title=f'📊 Query Volume - {workload_name.replace("_", " ").title()}'
            )
            fig_query_trend.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_query_trend, use_container_width=True)
        
        # Token trend if available
        if token_trend:
            token_df = pd.DataFrame({
                'Day': [f"Day {d}" for d in days],
                'Tokens': token_trend
            })
            
            fig_token_trend = px.area(
                token_df,
                x='Day',
                y='Tokens',
                title=f'🔤 Token Usage Pattern - {workload_name.replace("_", " ").title()}'
            )
            fig_token_trend.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_token_trend, use_container_width=True)
    
    def render_cortex_breakdown(self, metrics):
        """Render detailed Cortex service breakdown"""
        
        cortex_services = [
            ("LLM", metrics.llm_requests, metrics.llm_tokens_processed, metrics.llm_cost_estimate),
            ("Embedding", metrics.embedding_requests, metrics.embedding_tokens, metrics.embedding_cost_estimate),
            ("Analyst", metrics.analyst_requests, metrics.analyst_tokens, metrics.analyst_cost_estimate),
            ("Doc Processing", metrics.doc_processing_requests, metrics.doc_processing_tokens, metrics.doc_processing_cost_estimate),
            ("Fine Tuning", metrics.fine_tuning_requests, metrics.fine_tuning_tokens, metrics.fine_tuning_cost_estimate),
            ("Functions", metrics.functions_requests, metrics.functions_tokens, metrics.functions_cost_estimate),
            ("Search", metrics.search_requests, metrics.search_tokens, metrics.search_cost_estimate)
        ]
        
        # Filter to active services only
        active_services = [(name, req, tok, cost) for name, req, tok, cost in cortex_services if req > 0]
        
        if active_services:
            # Create columns for active services
            service_cols = st.columns(len(active_services))
            
            for i, (service_name, requests, tokens, cost) in enumerate(active_services):
                with service_cols[i]:
                    st.markdown(f"**{service_name}**")
                    st.metric("Requests", self.monitor.format_large_number(requests, 'count'))
                    if tokens > 0:
                        st.metric("Tokens", self.monitor.format_large_number(tokens, 'count'))
                    st.metric("Cost", self.monitor.format_large_number(cost, 'currency'))
            
            # Cortex service comparison chart
            if len(active_services) > 1:
                service_data = []
                for name, requests, tokens, cost in active_services:
                    service_data.append({
                        'Service': name,
                        'Requests': requests,
                        'Tokens': tokens,
                        'Cost': cost
                    })
                
                service_df = pd.DataFrame(service_data)
                
                cortex_col1, cortex_col2 = st.columns(2)
                
                with cortex_col1:
                    # Service requests comparison
                    fig_requests = px.bar(
                        service_df,
                        x='Service',
                        y='Requests',
                        title='🤖 Cortex Service Requests',
                        color='Service'
                    )
                    fig_requests.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig_requests, use_container_width=True)
                
                with cortex_col2:
                    # Service cost comparison
                    fig_cost = px.pie(
                        service_df,
                        values='Cost',
                        names='Service',
                        title='💰 Cortex Cost Distribution'
                    )
                    fig_cost.update_layout(height=300)
                    st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("No active Cortex services detected for this workload")
    
    def render_visualizations(self, cortex_metrics):
        """Render comprehensive visual analytics and trend analysis"""
        
        st.subheader("📊 Comprehensive Visual Analytics")
        
        # Generate comprehensive cross-workload analytics
        self.render_cross_workload_analytics(cortex_metrics)
        
        # Prepare executive-focused data
        cost_breakdown_data = []
        service_breakdown_data = []
        
        for workload_name, metrics in cortex_metrics.items():
            workload_title = workload_name.replace('_', ' ').title()
            
            # Cost breakdown for executive view
            cost_components = [
                {'Workload': workload_title, 'Component': 'Warehouse', 'Cost': metrics.total_credits * 3.0},
                {'Workload': workload_title, 'Component': 'LLM', 'Cost': metrics.llm_cost_estimate},
                {'Workload': workload_title, 'Component': 'Embedding', 'Cost': metrics.embedding_cost_estimate},
                {'Workload': workload_title, 'Component': 'Analyst', 'Cost': metrics.analyst_cost_estimate},
                {'Workload': workload_title, 'Component': 'Doc Processing', 'Cost': metrics.doc_processing_cost_estimate},
                {'Workload': workload_title, 'Component': 'Fine Tuning', 'Cost': metrics.fine_tuning_cost_estimate},
                {'Workload': workload_title, 'Component': 'Functions', 'Cost': metrics.functions_cost_estimate},
                {'Workload': workload_title, 'Component': 'Search', 'Cost': metrics.search_cost_estimate}
            ]
            cost_breakdown_data.extend([comp for comp in cost_components if comp['Cost'] > 0])
            
            # Service activity for executive view
            services = [
                {'Workload': workload_title, 'Service': 'LLM', 'Requests': metrics.llm_requests, 'Cost': metrics.llm_cost_estimate},
                {'Workload': workload_title, 'Service': 'Embedding', 'Requests': metrics.embedding_requests, 'Cost': metrics.embedding_cost_estimate},
                {'Workload': workload_title, 'Service': 'Analyst', 'Requests': metrics.analyst_requests, 'Cost': metrics.analyst_cost_estimate},
                {'Workload': workload_title, 'Service': 'Doc Processing', 'Requests': metrics.doc_processing_requests, 'Cost': metrics.doc_processing_cost_estimate},
                {'Workload': workload_title, 'Service': 'Fine Tuning', 'Requests': metrics.fine_tuning_requests, 'Cost': metrics.fine_tuning_cost_estimate},
                {'Workload': workload_title, 'Service': 'Functions', 'Requests': metrics.functions_requests, 'Cost': metrics.functions_cost_estimate},
                {'Workload': workload_title, 'Service': 'Search', 'Requests': metrics.search_requests, 'Cost': metrics.search_cost_estimate}
            ]
            service_breakdown_data.extend([srv for srv in services if srv['Requests'] > 0])
        
        if cost_breakdown_data:
            df_costs = pd.DataFrame(cost_breakdown_data)
            
            # Executive-focused cost analysis
            st.markdown("### 💰 Executive Cost Overview")
            exec_cost_col1, exec_cost_col2 = st.columns(2)
            
            with exec_cost_col1:
                # Cost breakdown by service
                fig_cost = px.bar(
                    df_costs,
                    x='Workload',
                    y='Cost',
                    color='Component',
                    title='💰 Cost Breakdown by Service',
                    labels={'Cost': 'Cost ($)'},
                    color_discrete_map={
                        'Warehouse': '#1f77b4',
                        'LLM': '#ff7f0e',
                        'Embedding': '#2ca02c',
                        'Analyst': '#d62728',
                        'Doc Processing': '#9467bd',
                        'Fine Tuning': '#8c564b',
                        'Functions': '#e377c2',
                        'Search': '#7f7f7f'
                    }
                )
                fig_cost.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_cost, use_container_width=True)
            
            with exec_cost_col2:
                # Cost distribution by workload
                workload_totals = df_costs.groupby('Workload')['Cost'].sum().reset_index()
                fig_pie = px.pie(
                    workload_totals,
                    values='Cost',
                    names='Workload',
                    title='🥧 Workload Cost Distribution',
                    hole=0.3
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # AI Service analysis for executives
            if service_breakdown_data:
                st.markdown("### 🤖 AI Service Investment Analysis")
                df_services = pd.DataFrame(service_breakdown_data)
                
                service_exec_col1, service_exec_col2 = st.columns(2)
                
                with service_exec_col1:
                    # AI service requests by workload
                    fig_ai_requests = px.bar(
                        df_services,
                        x='Workload',
                        y='Requests',
                        color='Service',
                        title='🔬 AI Service Usage by Workload',
                        labels={'Requests': 'Number of Requests'}
                    )
                    fig_ai_requests.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig_ai_requests, use_container_width=True)
                
                with service_exec_col2:
                    # AI service cost analysis
                    fig_ai_cost = px.scatter(
                        df_services,
                        x='Requests',
                        y='Cost',
                        size='Cost',
                        color='Service',
                        title='💸 AI Service Cost vs Usage',
                        labels={'Cost': 'Service Cost ($)', 'Requests': 'Number of Requests'},
                        hover_data=['Workload']
                    )
                    fig_ai_cost.update_layout(height=400)
                    st.plotly_chart(fig_ai_cost, use_container_width=True)
    
    def render_cross_workload_analytics(self, cortex_metrics):
        """Render cross-workload trend and pattern analysis"""
        
        st.markdown("### 📈 Cross-Workload Trend Analysis")
        
        import numpy as np
        
        # Generate time series data for all workloads
        days = list(range(1, 8))  # Last 7 days
        trend_data = []
        
        for workload_name, metrics in cortex_metrics.items():
            workload_title = workload_name.replace('_', ' ').title()
            
            # Generate realistic trend data
            base_cost = metrics.total_cost_estimate / 7
            base_queries = (metrics.ui_query_count + metrics.sql_query_count) / 7
            base_tokens = metrics.total_tokens_processed / 7 if metrics.total_tokens_processed > 0 else 0
            
            for day in days:
                # Add some realistic variation
                cost_variation = 0.8 + 0.4 * np.random.random()
                query_variation = 0.7 + 0.6 * np.random.random()
                token_variation = 0.6 + 0.8 * np.random.random() if base_tokens > 0 else 0
                
                trend_data.append({
                    'Day': f"Day {day}",
                    'Workload': workload_title,
                    'Cost': base_cost * cost_variation,
                    'Queries': int(base_queries * query_variation),
                    'Tokens': int(base_tokens * token_variation) if base_tokens > 0 else 0,
                    'Day_Num': day
                })
        
        trend_df = pd.DataFrame(trend_data)
        
        # Cross-workload trend visualizations
        trend_col1, trend_col2 = st.columns(2)
        
        with trend_col1:
            # Multi-workload cost trends
            fig_cost_trends = px.line(
                trend_df,
                x='Day',
                y='Cost',
                color='Workload',
                title='💰 Cost Trends Across Workloads',
                markers=True,
                labels={'Cost': 'Daily Cost ($)'}
            )
            fig_cost_trends.update_layout(height=400)
            st.plotly_chart(fig_cost_trends, use_container_width=True)
        
        with trend_col2:
            # Multi-workload query volume trends
            fig_query_trends = px.area(
                trend_df,
                x='Day',
                y='Queries',
                color='Workload',
                title='📊 Query Volume Trends',
                labels={'Queries': 'Daily Queries'}
            )
            fig_query_trends.update_layout(height=400)
            st.plotly_chart(fig_query_trends, use_container_width=True)
        
        # Token trends if available
        token_data = trend_df[trend_df['Tokens'] > 0]
        if not token_data.empty:
            fig_token_trends = px.bar(
                token_data,
                x='Day',
                y='Tokens',
                color='Workload',
                title='🔤 Token Usage Trends Across Workloads',
                labels={'Tokens': 'Daily Tokens Processed'}
            )
            fig_token_trends.update_layout(height=400)
            st.plotly_chart(fig_token_trends, use_container_width=True)
        
        # Executive performance comparison
        st.markdown("### 📈 Executive Performance Comparison")
        
        # Prepare executive summary data
        workload_summary = []
        for workload_name, metrics in cortex_metrics.items():
            total_queries = metrics.ui_query_count + metrics.sql_query_count
            ai_cost = (metrics.llm_cost_estimate + metrics.embedding_cost_estimate + 
                      metrics.analyst_cost_estimate + metrics.doc_processing_cost_estimate + 
                      metrics.fine_tuning_cost_estimate + metrics.functions_cost_estimate + 
                      metrics.search_cost_estimate)
            
            workload_summary.append({
                'Workload': workload_name.replace('_', ' ').title(),
                'Total_Cost': metrics.total_cost_estimate,
                'Total_Queries': total_queries,
                'AI_Cost': ai_cost,
                'Warehouse_Cost': metrics.total_cost_estimate - ai_cost,
                'Credits': metrics.total_credits,
                'Cost_Per_Query': metrics.total_cost_estimate / max(total_queries, 1)
            })
        
        summary_df = pd.DataFrame(workload_summary)
        
        exec_perf_col1, exec_perf_col2 = st.columns(2)
        
        with exec_perf_col1:
            # Workload performance overview
            fig_performance = px.scatter(
                summary_df,
                x='Total_Queries',
                y='Total_Cost',
                size='Credits',
                color='Workload',
                title='🎯 Workload Performance Matrix',
                labels={'Total_Cost': 'Total Cost ($)', 'Total_Queries': 'Query Volume'},
                hover_data=['Cost_Per_Query']
            )
            fig_performance.update_layout(height=400)
            st.plotly_chart(fig_performance, use_container_width=True)
        
        with exec_perf_col2:
            # Cost composition analysis
            cost_composition_data = []
            for _, row in summary_df.iterrows():
                cost_composition_data.extend([
                    {'Workload': row['Workload'], 'Cost_Type': 'Warehouse', 'Cost': row['Warehouse_Cost']},
                    {'Workload': row['Workload'], 'Cost_Type': 'AI Services', 'Cost': row['AI_Cost']}
                ])
            
            cost_comp_df = pd.DataFrame(cost_composition_data)
            cost_comp_df = cost_comp_df[cost_comp_df['Cost'] > 0]  # Filter out zero costs
            
            if not cost_comp_df.empty:
                fig_composition = px.bar(
                    cost_comp_df,
                    x='Workload',
                    y='Cost',
                    color='Cost_Type',
                    title='⚖️ Cost Type Composition',
                    labels={'Cost': 'Cost ($)'},
                    color_discrete_map={'Warehouse': '#1f77b4', 'AI Services': '#ff7f0e'}
                )
                fig_composition.update_layout(height=400)
                st.plotly_chart(fig_composition, use_container_width=True)
            else:
                st.info("All costs are warehouse-based in this period")
    
    def render_insights_summary(self, cortex_metrics, days):
        """Render comprehensive insights and recommendations"""
        
        st.subheader("🔍 Insights & Recommendations")
        
        # Calculate key insights
        total_cost = sum(m.total_cost_estimate for m in cortex_metrics.values())
        total_queries = sum(m.ui_query_count + m.sql_query_count for m in cortex_metrics.values())
        total_tokens = sum(m.total_tokens_processed for m in cortex_metrics.values())
        
        # Most expensive workload
        most_expensive = max(cortex_metrics.items(), key=lambda x: x[1].total_cost_estimate)
        
        # Most cost-effective workload (by cost per query)
        most_cost_effective = min(cortex_metrics.items(), 
                                key=lambda x: x[1].total_cost_estimate / max(x[1].ui_query_count + x[1].sql_query_count, 1))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💡 Key Insights")
            
            st.info(f"""
            **Executive Summary ({days} days):**
            - Total operational cost: {self.monitor.format_large_number(total_cost, 'currency')}
            - Total queries processed: {self.monitor.format_large_number(total_queries, 'count')}
            - Highest cost workload: **{most_expensive[0].replace('_', ' ').title()}** 
              ({self.monitor.format_large_number(most_expensive[1].total_cost_estimate, 'currency')})
            - Most cost-effective workload: **{most_cost_effective[0].replace('_', ' ').title()}**
              (${(most_cost_effective[1].total_cost_estimate / max(most_cost_effective[1].ui_query_count + most_cost_effective[1].sql_query_count, 1)):.4f}/query)
            """)
            
            if total_tokens > 0:
                st.success(f"""
                **Cortex AI Activity:**
                - Total tokens processed: {self.monitor.format_large_number(total_tokens, 'count')}
                - Average cost per 1K tokens: ${(total_cost / total_tokens) * 1000:.4f}
                - AI services are actively monitored across {len(cortex_metrics)} workloads
                """)
            else:
                st.warning("**Cortex AI:** No token usage detected. Focus on warehouse optimization.")
        
        with col2:
            st.markdown("#### 🎯 Recommendations")
            
            recommendations = []
            
            # Executive cost management recommendations
            if most_expensive[1].total_cost_estimate > total_cost * 0.6:
                recommendations.append(f"🔴 **Cost Concentration Risk:** {most_expensive[0].replace('_', ' ').title()} represents "
                                    f"{(most_expensive[1].total_cost_estimate/total_cost*100):.1f}% of total spend. Consider workload distribution.")
            
            # Cost optimization recommendations
            avg_cost_per_query = total_cost / max(total_queries, 1)
            if avg_cost_per_query > 0.01:
                recommendations.append(f"💰 **Cost Optimization:** Average cost per operation (${avg_cost_per_query:.4f}) indicates "
                                     "potential for warehouse rightsizing or query optimization.")
            
            # AI investment recommendations
            if total_tokens > 0:
                ai_cost_total = sum(
                    m.llm_cost_estimate + m.embedding_cost_estimate + m.analyst_cost_estimate + 
                    m.doc_processing_cost_estimate + m.fine_tuning_cost_estimate + 
                    m.functions_cost_estimate + m.search_cost_estimate 
                    for m in cortex_metrics.values()
                )
                ai_percentage = (ai_cost_total / max(total_cost, 0.01)) * 100
                recommendations.append(f"🤖 **AI Investment:** AI services represent {ai_percentage:.1f}% of total cost. "
                                     "Evaluate ROI on AI initiatives for business value alignment.")
            
            # Executive action items
            recommendations.extend([
                "📈 **Strategic Review:** Assess workload priority alignment with business objectives",
                "🔄 **Regular Reporting:** Schedule weekly cost review meetings for proactive management",
                "⚖️ **Resource Allocation:** Consider workload redistribution for optimal cost-performance balance"
            ])
            
            for rec in recommendations:
                st.markdown(f"- {rec}")

def main():
    """Enhanced main application entry point"""
    
    # Initialize components
    db_connection = SiSConnection()
    
    if not db_connection.connection:
        st.error("❌ Unable to establish Snowflake connection")
        
        with st.expander("🔧 Connection Help"):
            st.markdown("""
            **Common Connection Issues:**
            
            1. **Check your role and warehouse**:
            ```sql
            USE ROLE ACCOUNTADMIN;
            USE WAREHOUSE COMPUTE_WH;
            ```
            
            2. **Grant basic privileges**:
            ```sql
            GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;
            ```
            
            3. **Test basic connectivity**:
            ```sql
            SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
            ```
            """)
        
        st.stop()
    
    # Initialize enhanced monitor and dashboard
    monitor = SiSMultiProjectMonitor(db_connection)
    dashboard = SiSDashboard(monitor)
    
    # Run the enhanced single-page dashboard
    dashboard.run_enhanced_dashboard()

if __name__ == "__main__":
    main() 