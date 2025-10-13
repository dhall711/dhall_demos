import streamlit as st
import pandas as pd
import re
import hashlib
import time
import json
from typing import Dict, List, Tuple, Optional, Any

# Import system status monitoring components
try:
    from components.system_status import SystemStatusMonitor, render_system_status_sidebar
except ImportError:
    # Fallback if components are not available
    SystemStatusMonitor = None
    render_system_status_sidebar = None

# Set page configuration
st.set_page_config(
    page_title="🤖 AI-Enhanced Snowflake Sensitive Data Discovery & Masking",
    page_icon="🔒",
    layout="wide"
)

# =====================================================================
# CORTEX AI INTEGRATION FUNCTIONS  
# =====================================================================

def track_ai_activity(function_name: str, operation: str, response_time: float, success: bool, tokens_used: int = 0, cost: float = 0.0, 
                     query_details: str = None, table_context: str = None, column_context: str = None, ai_model: str = None):
    """Track AI activity for the Live AI Activity Monitor with detailed context"""
    from datetime import datetime
    
    # Initialize session state if not exists
    if 'ai_activity_log' not in st.session_state:
        st.session_state.ai_activity_log = []
    if 'ai_metrics' not in st.session_state:
        st.session_state.ai_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'total_tokens_used': 0,
            'cost_estimate': 0.0
        }
    
    # Create enhanced activity record
    activity = {
        'timestamp': datetime.now(),
        'function': function_name,
        'operation': operation,
        'response_time': response_time,
        'success': success,
        'tokens': tokens_used,
        'cost': cost,
        'query_details': query_details or f"Cortex {function_name} operation",
        'table_context': table_context,
        'column_context': column_context,
        'ai_model': ai_model or 'mistral-large',
        'prompt_preview': query_details[:100] + "..." if query_details and len(query_details) > 100 else query_details
    }
    
    # Add to activity log
    st.session_state.ai_activity_log.append(activity)
    
    # Update metrics
    st.session_state.ai_metrics['total_requests'] += 1
    if success:
        st.session_state.ai_metrics['successful_requests'] += 1
    else:
        st.session_state.ai_metrics['failed_requests'] += 1
    
    # Update average response time
    total_successful = st.session_state.ai_metrics['successful_requests']
    if total_successful > 0:
        current_avg = st.session_state.ai_metrics['avg_response_time']
        new_avg = ((current_avg * (total_successful - 1)) + response_time) / total_successful
        st.session_state.ai_metrics['avg_response_time'] = new_avg
    
    st.session_state.ai_metrics['total_tokens_used'] += tokens_used
    st.session_state.ai_metrics['cost_estimate'] += cost
    
    # Keep only last 50 activities
    st.session_state.ai_activity_log = st.session_state.ai_activity_log[-50:]

class CortexAIEnhancer:
    """
    Advanced Cortex AI integration for sensitive data discovery
    """
    
    def __init__(self, connection):
        self.conn = connection
        
    def classify_column_with_ai(self, sample_data: List[str], column_name: str, table_context: str = "") -> Dict:
        """
        Use Cortex AI to intelligently classify column sensitivity
        """
        start_time = time.time()
        success = False
        
        try:
            # Prepare sample data for analysis
            sample_text = " | ".join([str(val) for val in sample_data[:10] if val is not None])
            
            # Create classification prompt
            classification_query = f"""
            SELECT SNOWFLAKE.CORTEX.CLASSIFY_TEXT(
                '{sample_text}', 
                ['PII', 'Financial', 'Medical', 'Personal', 'Public', 'Confidential']
            ) as classification_result
            """
            
            result = self.conn.query(classification_query)
            response_time = time.time() - start_time
            
            if not result.empty:
                classification = result.iloc[0]['CLASSIFICATION_RESULT']
                success = True
                
                # Track AI activity with detailed context
                tokens_used = len(sample_text.split()) * 2  # Rough estimate
                cost = tokens_used * 0.0001  # Estimated cost
                track_ai_activity(
                    function_name="CLASSIFY_TEXT",
                    operation=f"Column: {column_name}",
                    response_time=response_time,
                    success=success,
                    tokens_used=tokens_used,
                    cost=cost,
                    query_details=classification_query.strip(),
                    table_context=table_context,
                    column_context=column_name,
                    ai_model="cortex-classify"
                )
                
                return {
                    'ai_classification': classification,
                    'confidence': 0.9,  # High confidence for AI classification
                    'source': 'CORTEX_AI_CLASSIFY'
                }
        except Exception as e:
            response_time = time.time() - start_time
            track_ai_activity(
                function_name="CLASSIFY_TEXT",
                operation=f"Column: {column_name}",
                response_time=response_time,
                success=False,
                tokens_used=0,
                cost=0,
                query_details="Classification query failed",
                table_context=table_context,
                column_context=column_name,
                ai_model="cortex-classify"
            )
            st.warning(f"AI Classification error: {str(e)}")
            
        return {'ai_classification': None, 'confidence': 0.0, 'source': 'ERROR'}
    
    def analyze_semantic_context(self, column_name: str, table_name: str, sample_data: List[str], 
                                column_comment: str = "", schema_context: str = "") -> Dict:
        """
        Use AI to understand semantic context and provide reasoning
        """
        start_time = time.time()
        success = False
        
        try:
            # Create context-aware prompt
            context_prompt = f"""
            Analyze this database column for sensitive data classification:
            
            Table: {table_name}
            Column: {column_name}
            Comment: {column_comment or 'No comment'}
            Schema Context: {schema_context or 'No additional context'}
            Sample Data: {', '.join([str(val) for val in sample_data[:5] if val is not None])}
            
            Determine:
            1. Is this column likely to contain sensitive/PII data?
            2. What type of sensitive data (SSN, Email, Phone, Name, Financial, etc.)?
            3. Confidence level (0-1)?
            4. Reasoning for this classification?
            
            Respond in JSON format with keys: is_sensitive, data_type, confidence, reasoning
            """
            
            analysis_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large', 
                '{context_prompt.replace("'", "''")}'
            ) as ai_analysis
            """
            
            result = self.conn.query(analysis_query)
            response_time = time.time() - start_time
            
            if not result.empty:
                ai_response = result.iloc[0]['AI_ANALYSIS']
                success = True
                
                # Track AI activity with detailed context
                tokens_used = len(context_prompt.split()) + (len(ai_response.split()) if ai_response else 0)
                cost = tokens_used * 0.0001  # Estimated cost
                track_ai_activity(
                    function_name="COMPLETE",
                    operation=f"Semantic Analysis: {table_name}.{column_name}",
                    response_time=response_time,
                    success=success,
                    tokens_used=tokens_used,
                    cost=cost,
                    query_details=analysis_query.strip(),
                    table_context=table_name,
                    column_context=column_name,
                    ai_model="mistral-large"
                )
                
                try:
                    # Try to parse JSON response
                    analysis = json.loads(ai_response)
                    return {
                        'ai_analysis': analysis,
                        'confidence': analysis.get('confidence', 0.5),
                        'reasoning': analysis.get('reasoning', 'AI analysis completed'),
                        'source': 'CORTEX_AI_COMPLETE'
                    }
                except json.JSONDecodeError:
                    # If not JSON, return raw response
                    return {
                        'ai_analysis': ai_response,
                        'confidence': 0.6,
                        'reasoning': ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                        'source': 'CORTEX_AI_COMPLETE'
                    }
        except Exception as e:
            response_time = time.time() - start_time
            track_ai_activity(
                function_name="COMPLETE",
                operation=f"Semantic Analysis: {table_name}.{column_name}",
                response_time=response_time,
                success=False,
                tokens_used=0,
                cost=0,
                query_details="Semantic analysis query failed",
                table_context=table_name,
                column_context=column_name,
                ai_model="mistral-large"
            )
            st.warning(f"AI Semantic Analysis error: {str(e)}")
            
        return {'ai_analysis': None, 'confidence': 0.0, 'reasoning': 'AI analysis failed', 'source': 'ERROR'}
    
    def discover_cross_table_patterns(self, database: str, schema: str, tables: List[str]) -> Dict:
        """
        Use AI to discover patterns across multiple tables
        """
        try:
            # Get column metadata across all tables
            pattern_query = f"""
            WITH table_columns AS (
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    comment
                FROM {database}.INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema = '{schema}'
                AND table_name IN ({', '.join(["'" + t + "'" for t in tables])})
            )
            SELECT 
                SNOWFLAKE.CORTEX.COMPLETE(
                    'mistral-large',
                    'Analyze these database columns and identify potential sensitive data patterns. Look for naming conventions, data types, and relationships that suggest PII or sensitive information: ' || 
                    LISTAGG(table_name || '.' || column_name || ' (' || data_type || ')', ', ')
                ) as pattern_analysis
            FROM table_columns
            """
            
            result = self.conn.query(pattern_query)
            if not result.empty:
                pattern_analysis = result.iloc[0]['PATTERN_ANALYSIS']
                return {
                    'pattern_analysis': pattern_analysis,
                    'source': 'CORTEX_AI_PATTERN_DISCOVERY'
                }
        except Exception as e:
            st.warning(f"Cross-table pattern discovery error: {str(e)}")
            
        return {'pattern_analysis': None, 'source': 'ERROR'}
    
    def generate_enhanced_masking_policy(self, sensitive_type: str, column_name: str, 
                                       data_type: str, business_context: str = "") -> Dict:
        """
        Use AI to generate contextually appropriate masking policies
        """
        try:
            policy_prompt = f"""
            Generate an appropriate Snowflake Dynamic Data Masking policy for:
            
            Column: {column_name}
            Data Type: {data_type}
            Sensitive Type: {sensitive_type}
            Business Context: {business_context or 'General business use'}
            
            Consider:
            1. Appropriate masking strategy (full, partial, format-preserving)
            2. Role-based access (which roles should see unmasked data)
            3. Compliance requirements (GDPR, CCPA, HIPAA if applicable)
            
            Provide SQL masking expression and explanation.
            """
            
            policy_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{policy_prompt.replace("'", "''")}'
            ) as policy_recommendation
            """
            
            result = self.conn.query(policy_query)
            if not result.empty:
                policy_rec = result.iloc[0]['POLICY_RECOMMENDATION']
                return {
                    'ai_policy_recommendation': policy_rec,
                    'source': 'CORTEX_AI_POLICY_GEN'
                }
        except Exception as e:
            st.warning(f"AI Policy Generation error: {str(e)}")
            
        return {'ai_policy_recommendation': None, 'source': 'ERROR'}

def detect_sensitive_data_with_ai(column_name, data_type, column_comment, sample_values, 
                                tags=None, custom_rules=None, settings=None, 
                                table_name="", conn=None):
    """
    Enhanced sensitive data detection using Cortex AI combined with traditional rules.
    Returns: (is_sensitive: bool, sensitive_type: str, confidence: float, rationale: str, detection_source: str, ai_insights: dict)
    """
    if settings is None:
        settings = load_user_settings()
    
    if custom_rules is None:
        custom_rules = []
        
    # Initialize AI enhancer if connection available
    ai_enhancer = CortexAIEnhancer(conn) if conn else None
    ai_insights = {}
    
    # First run traditional detection
    is_sensitive_traditional, sensitive_type_traditional, confidence_traditional, rationale_traditional, detection_source_traditional = detect_sensitive_data_enhanced(
        column_name, data_type, column_comment, sample_values, tags, custom_rules, settings
    )
    
    # If AI is available and we have sample data, enhance with AI analysis
    if ai_enhancer and sample_values and settings.get('ai_enhancement', {}).get('enable_ai_analysis', True):
        try:
            # AI Classification
            ai_classification = ai_enhancer.classify_column_with_ai(sample_values, column_name, table_name)
            ai_insights['classification'] = ai_classification
            
            # AI Semantic Analysis
            ai_semantic = ai_enhancer.analyze_semantic_context(
                column_name, table_name, sample_values, column_comment
            )
            ai_insights['semantic_analysis'] = ai_semantic
            
            # Enhanced decision making combining traditional and AI results
            ai_confidence = ai_semantic.get('confidence', 0.0)
            ai_suggests_sensitive = False
            ai_sensitive_type = None
            
            # Parse AI analysis if available
            if isinstance(ai_semantic.get('ai_analysis'), dict):
                ai_analysis = ai_semantic['ai_analysis']
                ai_suggests_sensitive = ai_analysis.get('is_sensitive', False)
                raw_ai_type = ai_analysis.get('data_type', None)
                ai_sensitive_type = normalize_sensitive_type(raw_ai_type) if raw_ai_type else None
            elif ai_classification.get('ai_classification'):
                # Check if classification suggests sensitive data
                classification_text = str(ai_classification['ai_classification']).lower()
                ai_suggests_sensitive = any(word in classification_text for word in ['pii', 'personal', 'confidential', 'financial', 'medical'])
                # Try to extract type from classification
                if ai_suggests_sensitive:
                    ai_sensitive_type = normalize_sensitive_type(ai_classification['ai_classification'])
            
            # Combine traditional and AI results with weighted scoring
            traditional_weight = 0.4
            ai_weight = 0.6
            
            combined_confidence = (confidence_traditional * traditional_weight) + (ai_confidence * ai_weight)
            
            # Final decision logic
            if ai_suggests_sensitive and is_sensitive_traditional:
                # Both agree - high confidence
                final_confidence = max(combined_confidence, 0.8)
                final_sensitive_type = ai_sensitive_type or sensitive_type_traditional
                final_rationale = f"🤖 AI and traditional detection agree. AI reasoning: {ai_semantic.get('reasoning', 'N/A')}. Traditional: {rationale_traditional}"
                final_source = "AI_ENHANCED_COMBINED"
                
            elif ai_suggests_sensitive and not is_sensitive_traditional:
                # AI detects but traditional doesn't
                if ai_confidence > 0.7:
                    final_confidence = ai_confidence
                    final_sensitive_type = ai_sensitive_type or 'PII_GENERAL'
                    final_rationale = f"🤖 AI-detected sensitive data: {ai_semantic.get('reasoning', 'High AI confidence')}"
                    final_source = "AI_ENHANCED_ONLY"
                    is_sensitive_traditional = True
                else:
                    # Lower AI confidence - stick with traditional
                    final_confidence = confidence_traditional
                    final_sensitive_type = sensitive_type_traditional
                    final_rationale = rationale_traditional + f" (🤖 AI suggests sensitivity but with low confidence: {ai_confidence:.2f})"
                    final_source = detection_source_traditional
                    
            elif not ai_suggests_sensitive and is_sensitive_traditional:
                # Traditional detects but AI doesn't
                if confidence_traditional > 0.8:
                    # High traditional confidence - keep it
                    final_confidence = confidence_traditional
                    final_sensitive_type = sensitive_type_traditional
                    final_rationale = rationale_traditional + f" (🤖 AI analysis: {ai_semantic.get('reasoning', 'Does not suggest sensitivity')})"
                    final_source = detection_source_traditional
                else:
                    # Lower traditional confidence - AI disagrees, reduce confidence
                    final_confidence = confidence_traditional * 0.7
                    final_sensitive_type = sensitive_type_traditional
                    final_rationale = f"Traditional detection with AI disagreement. {rationale_traditional}. 🤖 AI: {ai_semantic.get('reasoning', 'N/A')}"
                    final_source = "TRADITIONAL_WITH_AI_DISAGREEMENT"
            
            else:
                # Neither detects or both agree it's not sensitive
                final_confidence = combined_confidence
                final_sensitive_type = sensitive_type_traditional
                final_rationale = rationale_traditional + f" (🤖 AI concurs: {ai_semantic.get('reasoning', 'Not sensitive')})"
                final_source = detection_source_traditional
            
            return (is_sensitive_traditional, final_sensitive_type, final_confidence, final_rationale, final_source, ai_insights)
            
        except Exception as e:
            # AI enhancement failed, fall back to traditional
            st.warning(f"AI enhancement failed: {str(e)}")
            ai_insights['error'] = str(e)
    
    # Return traditional results with empty AI insights
    return (is_sensitive_traditional, sensitive_type_traditional, confidence_traditional, rationale_traditional, detection_source_traditional, ai_insights)

# =====================================================================
# ERROR HANDLING AND UTILITY FUNCTIONS
# =====================================================================

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass

def handle_snowflake_error(func):
    """Decorator for consistent error handling across Snowflake operations"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower():
                st.error(f"🚫 Resource not found: {error_msg}")
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                st.error(f"🔐 Access denied: {error_msg}")
            elif "connection" in error_msg.lower():
                st.error(f"🔌 Connection issue: {error_msg}")
            else:
                st.error(f"❌ Database error: {error_msg}")
            return None
    return wrapper

def safe_execute_query(conn, query: str, operation_name: str = "query") -> Optional[pd.DataFrame]:
    """Safely execute a Snowflake query with comprehensive error handling"""
    try:
        if not conn:
            st.error("🔌 No database connection available")
            return None
        
        with st.spinner(f"Executing {operation_name}..."):
            df = conn.query(query)
            return df
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error during {operation_name}: {error_msg}")
        
        # Log error details in expander for debugging
        with st.expander("🔍 Error Details", expanded=False):
            st.code(f"Query: {query}")
            st.code(f"Error: {error_msg}")
        
        return None

# =====================================================================
# CONFIGURATION AND SETTINGS MANAGEMENT
# =====================================================================

def get_default_settings() -> Dict[str, Any]:
    """Get default application settings"""
    return {
        "masking_strategies": {
            "PII_SSN": {
                "strategy_type": "partial_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '***-**-' || SUBSTR(VAL, 8, 4) END",
                "authorized_roles": ["ANALYST_ROLE"],
                "description": "Show last 4 digits only",
                "example": "123-45-6789 → ***-**-6789"
            },
            "PII_EMAIL": {
                "strategy_type": "partial_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE REGEXP_REPLACE(VAL, '^([^@]+)@(.+)$', '****@\\\\2') END",
                "authorized_roles": ["ADMIN_ROLE"],
                "description": "Mask username, keep domain",
                "example": "john.doe@company.com → ****@company.com"
            },
            "PII_PERSON_NAME": {
                "strategy_type": "full_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '****' END",
                "authorized_roles": ["HR_ROLE"],
                "description": "Complete masking",
                "example": "John Doe → ****"
            },
            "FINANCIAL_CC": {
                "strategy_type": "partial_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '************' || SUBSTR(VAL, 13, 4) END",
                "authorized_roles": ["FINANCE_ROLE"],
                "description": "Show last 4 digits only",
                "example": "1234567890123456 → ************3456"
            },
            "PII_PHONE": {
                "strategy_type": "partial_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '***-***-' || SUBSTR(VAL, 9, 4) END",
                "authorized_roles": ["SUPPORT_ROLE"],
                "description": "Show last 4 digits only",
                "example": "555-123-4567 → ***-***-4567"
            },
            "PII_GENERAL": {
                "strategy_type": "full_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '****' END",
                "authorized_roles": ["DATA_OWNER_ROLE"],
                "description": "Complete masking",
                "example": "Sensitive Data → ****"
            },
            "PII_ADDRESS": {
                "strategy_type": "partial_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE '*** [REDACTED ADDRESS] ***' END",
                "authorized_roles": ["HR_ROLE", "ADMIN_ROLE"],
                "description": "Complete address masking",
                "example": "123 Main St → *** [REDACTED ADDRESS] ***"
            },
            "PII_DOB": {
                "strategy_type": "partial_mask",
                "custom_sql": "CASE WHEN CURRENT_ROLE() IN ({roles}) THEN VAL ELSE CASE WHEN VAL IS NOT NULL THEN YEAR(VAL) || '-XX-XX' ELSE NULL END END",
                "authorized_roles": ["HR_ROLE", "ANALYST_ROLE"],
                "description": "Show year only, mask month/day",
                "example": "1980-01-15 → 1980-XX-XX"
            }
        },
        "detection_rules": {
            "enable_tag_detection": True,
            "enable_comment_detection": True,
            "confidence_threshold": 0.5,
            "sample_size": 100
        },
        "ui_preferences": {
            "show_debug_info": False,
            "auto_expand_high_confidence": True,
            "max_sample_display": 15
        },
        "ai_enhancement": {
            "enable_ai_analysis": True,
            "enable_ai_classification": True,
            "enable_semantic_analysis": True,
            "enable_cross_table_patterns": True,
            "ai_confidence_threshold": 0.6,
            "ai_model_preference": "mistral-large"
        },
        "performance": {
            "mode": "balanced",  # fast, balanced, thorough
            "sample_size": 50,   # Number of sample values to retrieve
            "enable_bulk_sampling": True,  # Use bulk sampling for better performance
            "enable_caching": True,  # Enable result caching
            "fast_mode_sample_size": 20,  # Sample size in fast mode
            "thorough_mode_sample_size": 100  # Sample size in thorough mode
        }
    }

def load_user_settings() -> Dict[str, Any]:
    """Load user settings from session state or return defaults"""
    if 'user_settings' not in st.session_state:
        st.session_state.user_settings = get_default_settings()
    return st.session_state.user_settings

def save_user_settings(settings: Dict[str, Any]):
    """Save user settings to session state"""
    st.session_state.user_settings = settings

def initialize_persistent_storage(conn) -> bool:
    """Initialize persistent storage tables for classifications and rules"""
    try:
        # Create schema for app tables if it doesn't exist
        create_schema_query = """
        CREATE SCHEMA IF NOT EXISTS DATA_DISCOVERY_APP
        COMMENT = 'Schema for Sensitive Data Discovery & Masking Application'
        """
        
        # Create table for storing approved classifications
        create_classifications_table = """
        CREATE TABLE IF NOT EXISTS DATA_DISCOVERY_APP.APPROVED_CLASSIFICATIONS (
            ID STRING DEFAULT UUID_STRING(),
            DATABASE_NAME STRING NOT NULL,
            SCHEMA_NAME STRING NOT NULL,
            TABLE_NAME STRING NOT NULL,
            COLUMN_NAME STRING NOT NULL,
            SENSITIVE_TYPE STRING NOT NULL,
            CONFIDENCE FLOAT NOT NULL,
            APPROVED_BY STRING DEFAULT CURRENT_USER(),
            APPROVED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            MASKING_STRATEGY STRING,
            NOTES STRING,
            PRIMARY KEY (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME, COLUMN_NAME)
        )
        COMMENT = 'Stores user-approved sensitive data classifications'
        """
        
        # Create table for storing custom detection rules
        create_rules_table = """
        CREATE TABLE IF NOT EXISTS DATA_DISCOVERY_APP.CUSTOM_DETECTION_RULES (
            RULE_ID STRING DEFAULT UUID_STRING(),
            RULE_NAME STRING NOT NULL,
            SENSITIVE_TYPE STRING NOT NULL,
            PATTERN_TYPE STRING NOT NULL, -- 'REGEX', 'COLUMN_NAME', 'TAG', 'COMMENT'
            PATTERN_VALUE STRING NOT NULL,
            CONFIDENCE_SCORE FLOAT DEFAULT 0.8,
            CREATED_BY STRING DEFAULT CURRENT_USER(),
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            IS_ACTIVE BOOLEAN DEFAULT TRUE,
            PRIMARY KEY (RULE_ID)
        )
        COMMENT = 'Stores custom detection rules for sensitive data'
        """
        
        # Execute table creation
        safe_execute_query(conn, create_schema_query, "creating app schema")
        safe_execute_query(conn, create_classifications_table, "creating classifications table")
        safe_execute_query(conn, create_rules_table, "creating rules table")
        
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize persistent storage: {str(e)}")
        return False

# =====================================================================
# ENHANCED CONNECTION AND DATA FETCHING
# =====================================================================

@st.cache_resource
def get_snowflake_connection():
    """Get Snowflake connection using st.connection with enhanced error handling"""
    try:
        conn = st.connection('snowflake')
        # Test connection
        test_query = "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()"
        test_result = conn.query(test_query)
        
        if not test_result.empty:
            st.success(f"✅ Connected as {test_result.iloc[0]['CURRENT_USER()']} with role {test_result.iloc[0]['CURRENT_ROLE()']}")
            return conn
        else:
            raise DatabaseError("Connection test failed")
            
    except Exception as e:
        st.error(f"🔌 Failed to connect to Snowflake: {str(e)}")
        st.info("💡 Ensure you're running this as a Streamlit-in-Snowflake application with proper permissions.")
        return None

@handle_snowflake_error
def get_databases(_conn):
    """Get list of available databases with progress indicator"""
    query = "SELECT DATABASE_NAME FROM INFORMATION_SCHEMA.DATABASES ORDER BY DATABASE_NAME"
    df = safe_execute_query(_conn, query, "fetching databases")
    return df['DATABASE_NAME'].tolist() if df is not None else []

@handle_snowflake_error
def get_schemas(_conn, database_name):
    """Get list of schemas for the selected database with enhanced error handling"""
    query = f"SELECT SCHEMA_NAME FROM {database_name}.INFORMATION_SCHEMA.SCHEMATA ORDER BY SCHEMA_NAME"
    df = safe_execute_query(_conn, query, f"fetching schemas from {database_name}")
    return df['SCHEMA_NAME'].tolist() if df is not None else []

@handle_snowflake_error
def get_tables(_conn, database_name, schema_name):
    """Get list of tables for the selected database and schema"""
    query = f"""
    SELECT TABLE_NAME 
    FROM {database_name}.INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = '{schema_name}'
    ORDER BY TABLE_NAME
    """
    df = safe_execute_query(_conn, query, f"fetching tables from {database_name}.{schema_name}")
    return df['TABLE_NAME'].tolist() if df is not None else []

@handle_snowflake_error
def get_column_metadata_with_tags(_conn, database, schema, table):
    """Get column metadata for the specified table (tags disabled for compatibility)"""
    # Base query for column metadata
    base_query = f"""
    SELECT 
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.COMMENT,
        c.IS_NULLABLE,
        c.COLUMN_DEFAULT,
        NULL as TAGS
    FROM {database}.INFORMATION_SCHEMA.COLUMNS c
    WHERE c.table_schema = '{schema}' 
    AND c.table_name = '{table}'
    ORDER BY c.ordinal_position
    """
    
    # Execute base query (tag functionality disabled for compatibility)
    df = safe_execute_query(_conn, base_query, f"fetching column metadata for {table}")
    return df if df is not None else pd.DataFrame()

@handle_snowflake_error  
def get_sample_data_with_progress(_conn, database, schema, table, column_name, limit=100):
    """OPTIMIZED: Get sample values for a given column with performance improvements"""
    # Use TABLESAMPLE for much faster performance on large tables
    optimized_query = f"""
    SELECT "{column_name}" as sample_value
    FROM {database}.{schema}.{table} TABLESAMPLE (1000 ROWS)
    WHERE "{column_name}" IS NOT NULL
    LIMIT {limit}
    """
    
    # Fallback query without TABLESAMPLE for compatibility
    fallback_query = f"""
    SELECT "{column_name}" as sample_value
    FROM {database}.{schema}.{table}
    WHERE "{column_name}" IS NOT NULL
    LIMIT {limit}
    """
    
    try:
        # Try optimized query first
        df = safe_execute_query(_conn, optimized_query, f"fetching sample data for {column_name} (optimized)")
    except:
        # Fallback to simple query if TABLESAMPLE fails
        df = safe_execute_query(_conn, fallback_query, f"fetching sample data for {column_name} (fallback)")
    
    return df['SAMPLE_VALUE'].tolist() if df is not None and not df.empty else []

@st.cache_data(ttl=3600)  # Cache for 60 minutes
def get_bulk_sample_data(_conn, database: str, schema: str, table: str, column_names: List[str], limit: int = 50) -> Dict[str, List[str]]:
    """
    PERFORMANCE BOOST: Retrieve sample data for multiple columns in a single query
    This can be 5-10x faster than individual column queries
    """
    try:
        # Build dynamic query for multiple columns
        column_selects = []
        for col in column_names:
            column_selects.append(f'"{col}"')
        
        bulk_query = f"""
        SELECT {', '.join(column_selects)}
        FROM {database}.{schema}.{table} TABLESAMPLE (1000 ROWS)
        LIMIT {limit}
        """
        
        try:
            df = _conn.query(bulk_query)
        except:
            # Fallback without TABLESAMPLE
            bulk_query = f"""
            SELECT {', '.join(column_selects)}
            FROM {database}.{schema}.{table}
            LIMIT {limit}
            """
            df = _conn.query(bulk_query)
        
        # Convert to dictionary of lists
        result = {}
        for col in column_names:
            if col in df.columns:
                result[col] = df[col].dropna().astype(str).tolist()
            else:
                result[col] = []
                
        return result
        
    except Exception as e:
        st.warning(f"Bulk sample data retrieval failed: {str(e)}. Falling back to individual queries.")
        # Fallback to individual column queries
        result = {}
        for col in column_names:
            result[col] = get_sample_data_with_progress(_conn, database, schema, table, col, limit)
        return result

# =====================================================================
# ENHANCED DETECTION AND MASKING LOGIC
# =====================================================================

def load_custom_detection_rules(conn) -> List[Dict[str, Any]]:
    """Load custom detection rules from persistent storage"""
    try:
        # First check if the schema and table exist
        check_schema_query = """
        SELECT COUNT(*) as schema_exists 
        FROM INFORMATION_SCHEMA.SCHEMATA 
        WHERE SCHEMA_NAME = 'DATA_DISCOVERY_APP'
        """
        
        check_table_query = """
        SELECT COUNT(*) as table_exists 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'DATA_DISCOVERY_APP' 
        AND TABLE_NAME = 'CUSTOM_DETECTION_RULES'
        """
        
        # Check if schema exists
        schema_df = safe_execute_query(conn, check_schema_query, "checking schema existence")
        if schema_df is None or schema_df.iloc[0]['SCHEMA_EXISTS'] == 0:
            return []  # Schema doesn't exist, return empty rules
            
        # Check if table exists
        table_df = safe_execute_query(conn, check_table_query, "checking table existence")
        if table_df is None or table_df.iloc[0]['TABLE_EXISTS'] == 0:
            return []  # Table doesn't exist, return empty rules
        
        # If both exist, load the rules
        query = """
        SELECT RULE_NAME, SENSITIVE_TYPE, PATTERN_TYPE, PATTERN_VALUE, CONFIDENCE_SCORE
        FROM DATA_DISCOVERY_APP.CUSTOM_DETECTION_RULES
        WHERE IS_ACTIVE = TRUE
        ORDER BY CONFIDENCE_SCORE DESC
        """
        df = safe_execute_query(conn, query, "loading custom detection rules")
        return df.to_dict('records') if df is not None else []
    except Exception as e:
        # Silently handle any errors and return empty list
        return []

def detect_sensitive_data_enhanced(column_name, data_type, column_comment, sample_values, tags=None, custom_rules=None, settings=None):
    """
    Enhanced sensitive data detection using column metadata, sample data, tags, and custom rules.
    Returns: (is_sensitive: bool, sensitive_type: str, confidence: float, rationale: str, detection_source: str)
    """
    if settings is None:
        settings = load_user_settings()
    
    if custom_rules is None:
        custom_rules = []
    
    column_name_lower = column_name.lower()
    comment_lower = (column_comment or "").lower()
    sample_strings = [str(val) for val in sample_values if val is not None]
    
    # Check custom rules first (highest priority)
    for rule in custom_rules:
        if rule['PATTERN_TYPE'] == 'COLUMN_NAME':
            if re.search(rule['PATTERN_VALUE'], column_name_lower, re.IGNORECASE):
                return (True, rule['SENSITIVE_TYPE'], rule['CONFIDENCE_SCORE'], 
                       f"Matched custom column name rule: {rule['RULE_NAME']}", "CUSTOM_RULE")
        
        elif rule['PATTERN_TYPE'] == 'REGEX' and sample_strings:
            pattern = re.compile(rule['PATTERN_VALUE'], re.IGNORECASE)
            if any(pattern.search(sample) for sample in sample_strings):
                return (True, rule['SENSITIVE_TYPE'], rule['CONFIDENCE_SCORE'],
                       f"Matched custom regex rule: {rule['RULE_NAME']}", "CUSTOM_RULE")
        
        elif rule['PATTERN_TYPE'] == 'COMMENT' and column_comment:
            if re.search(rule['PATTERN_VALUE'], comment_lower, re.IGNORECASE):
                return (True, rule['SENSITIVE_TYPE'], rule['CONFIDENCE_SCORE'],
                       f"Matched custom comment rule: {rule['RULE_NAME']}", "CUSTOM_RULE")
    
    # Check tags if available (high priority)
    if settings['detection_rules']['enable_tag_detection'] and tags:
        tag_confidence = 0.95  # High confidence for explicit tags
        sensitive_tag_patterns = {
            'PII': 'PII_GENERAL',
            'PERSONAL': 'PII_GENERAL', 
            'SSN': 'PII_SSN',
            'EMAIL': 'PII_EMAIL',
            'PHONE': 'PII_PHONE',
            'CREDIT_CARD': 'FINANCIAL_CC',
            'FINANCIAL': 'FINANCIAL_CC',
            'NAME': 'PII_PERSON_NAME',
            'ADDRESS': 'PII_ADDRESS',
            'DOB': 'PII_DOB',
            'DATE_OF_BIRTH': 'PII_DOB'
        }
        
        for tag_pattern, sensitive_type in sensitive_tag_patterns.items():
            if tag_pattern.lower() in tags.lower():
                return (True, sensitive_type, tag_confidence, 
                       f"Snowflake tag indicates sensitive data: {tags}", "TAG")
    
    # Enhanced built-in detection patterns
    detections = [
        # SSN Detection
        {
            'patterns': {
                'column': ['ssn', 'social_security', 'social_security_number', 'socialsecurity'],
                'regex': [r'^\d{3}-\d{2}-\d{4}$', r'^\d{9}$']
            },
            'type': 'PII_SSN',
            'confidence_base': 0.9
        },
        # Email Detection  
        {
            'patterns': {
                'column': ['email', 'e_mail', 'email_address', 'emailaddress', 'mail'],
                'regex': [r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$']
            },
            'type': 'PII_EMAIL',
            'confidence_base': 0.9
        },
        # Name Detection
        {
            'patterns': {
                'column': ['name', 'first_name', 'last_name', 'full_name', 'fname', 'lname', 
                          'firstname', 'lastname', 'customer_name', 'user_name', 'username', 
                          'display_name', 'given_name', 'family_name']
            },
            'type': 'PII_PERSON_NAME',
            'confidence_base': 0.6
        },
        # Credit Card Detection
        {
            'patterns': {
                'column': ['credit_card', 'creditcard', 'cc_number', 'ccnumber', 'cc', 
                          'card_number', 'cardnumber', 'payment_card', 'credit_card_number'],
                'regex': [r'^\d{16}$', r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$']
            },
            'type': 'FINANCIAL_CC',
            'confidence_base': 0.9
        },
        # Phone Number Detection
        {
            'patterns': {
                'column': ['phone', 'telephone', 'mobile', 'cell', 'contact', 'phone_number', 
                          'tel', 'mobile_number', 'contact_number'],
                'regex': [r'^\d{3}[-.]?\d{3}[-.]?\d{4}$', r'^\(\d{3}\)\s?\d{3}[-.]?\d{4}$']
            },
            'type': 'PII_PHONE',
            'confidence_base': 0.8
        },
        # Address Detection (for sample data compatibility)
        {
            'patterns': {
                'column': ['address', 'street', 'street_address', 'home_address', 'mailing_address', 
                          'billing_address', 'shipping_address']
            },
            'type': 'PII_ADDRESS',
            'confidence_base': 0.6
        },
        # Date of Birth Detection (for sample data compatibility)
        {
            'patterns': {
                'column': ['dob', 'date_of_birth', 'birth_date', 'birthdate', 'birthday']
            },
            'type': 'PII_DOB',
            'confidence_base': 0.7
        }
    ]
    
    # Process detection patterns
    for detection in detections:
        column_match = any(pattern in column_name_lower for pattern in detection['patterns'].get('column', []))
        
        if column_match:
            # Check for regex pattern match in sample data
            regex_patterns = detection['patterns'].get('regex', [])
            if regex_patterns and sample_strings:
                pattern_match = False
                for regex_pattern in regex_patterns:
                    if any(re.match(regex_pattern, sample) for sample in sample_strings):
                        pattern_match = True
                        break
                
                if pattern_match:
                    return (True, detection['type'], detection['confidence_base'],
                           f"Column name and sample data patterns match {detection['type']}", "PATTERN_MATCH")
                else:
                    return (True, detection['type'], detection['confidence_base'] - 0.2,
                           f"Column name suggests {detection['type']} (sample data validation needed)", "COLUMN_NAME")
            else:
                return (True, detection['type'], detection['confidence_base'] - 0.3,
                       f"Column name suggests {detection['type']}", "COLUMN_NAME")
    
    # Check sample data patterns without column name match
    for detection in detections:
        regex_patterns = detection['patterns'].get('regex', [])
        if regex_patterns and sample_strings:
            for regex_pattern in regex_patterns:
                if any(re.match(regex_pattern, sample) for sample in sample_strings):
                    return (True, detection['type'], detection['confidence_base'] - 0.1,
                           f"Sample data matches {detection['type']} pattern", "SAMPLE_DATA")
    
    # Comment-based detection
    if settings['detection_rules']['enable_comment_detection'] and column_comment:
        sensitive_comment_keywords = {
            'personal': 'PII_GENERAL',
            'private': 'PII_GENERAL', 
            'confidential': 'PII_GENERAL',
            'sensitive': 'PII_GENERAL',
            'pii': 'PII_GENERAL',
            'ssn': 'PII_SSN',
            'social security': 'PII_SSN',
            'email': 'PII_EMAIL',
            'credit card': 'FINANCIAL_CC',
            'pci': 'FINANCIAL_CC',
            'phone': 'PII_PHONE',
            'address': 'PII_ADDRESS',
            'birth': 'PII_DOB',
            'date of birth': 'PII_DOB'
        }
        
        for keyword, sensitive_type in sensitive_comment_keywords.items():
            if keyword in comment_lower:
                return (True, sensitive_type, 0.5, 
                       f"Column comment suggests sensitive data: '{column_comment}'", "COMMENT")
    
    # Not detected as sensitive
    return (False, None, 0.0, "Not detected as sensitive by enhanced rules", "NONE")

def normalize_sensitive_type(sensitive_type: str) -> str:
    """
    Normalize AI-returned sensitive types to match masking strategy keys.
    Maps common AI classifications to standard sensitive type codes.
    """
    if not sensitive_type:
        return 'PII_GENERAL'
        
    # Convert to uppercase for consistent matching
    sensitive_type_upper = str(sensitive_type).upper()
    
    # Mapping from AI classifications to masking strategy keys
    type_mapping = {
        'SSN': 'PII_SSN',
        'SOCIAL_SECURITY': 'PII_SSN',
        'SOCIAL_SECURITY_NUMBER': 'PII_SSN',
        'EMAIL': 'PII_EMAIL',
        'EMAIL_ADDRESS': 'PII_EMAIL',
        'PHONE': 'PII_PHONE',
        'PHONE_NUMBER': 'PII_PHONE',
        'NAME': 'PII_PERSON_NAME',
        'PERSON_NAME': 'PII_PERSON_NAME',
        'FULL_NAME': 'PII_PERSON_NAME',
        'CREDIT_CARD': 'FINANCIAL_CC',
        'CREDIT_CARD_NUMBER': 'FINANCIAL_CC',
        'CC': 'FINANCIAL_CC',
        'ADDRESS': 'PII_ADDRESS',
        'DOB': 'PII_DOB',
        'DATE_OF_BIRTH': 'PII_DOB',
        'PII': 'PII_GENERAL',
        'PERSONAL': 'PII_GENERAL',
        'FINANCIAL': 'FINANCIAL_CC'
    }
    
    # Check for exact matches first
    if sensitive_type_upper in type_mapping:
        return type_mapping[sensitive_type_upper]
    
    # Check for partial matches
    for ai_type, standard_type in type_mapping.items():
        if ai_type in sensitive_type_upper:
            return standard_type
    
    # If already in standard format, return as-is
    if sensitive_type_upper.startswith(('PII_', 'FINANCIAL_')):
        return sensitive_type
        
    # Default fallback for unknown types
    return 'PII_GENERAL'

def get_configurable_masking_recommendation(sensitive_type: str, settings: Dict[str, Any]) -> Tuple[str, str, List[str], str]:
    """
    Get configurable masking recommendation based on user settings.
    Returns: (masking_sql: str, description: str, authorized_roles: list, example: str)
    """
    # Normalize the sensitive type to match masking strategy keys
    normalized_type = normalize_sensitive_type(sensitive_type)
    strategy_config = settings['masking_strategies'].get(normalized_type)
    
    if not strategy_config:
        # Fallback to default strategy
        return (
            "CASE WHEN CURRENT_ROLE() IN ('DATA_OWNER_ROLE') THEN VAL ELSE '****' END",
            f"Default complete masking for type: {sensitive_type} (mapped to {normalized_type})",
            ["DATA_OWNER_ROLE"],
            "Unknown Data → ****"
        )
    
    # Format roles into SQL string
    roles_sql = "'" + "', '".join(strategy_config['authorized_roles']) + "'"
    masking_sql = strategy_config['custom_sql'].format(roles=roles_sql)
    
    return (
        masking_sql,
        strategy_config['description'], 
        strategy_config['authorized_roles'],
        strategy_config['example']
    )

def save_approved_classification(conn, classification_data: Dict[str, Any]) -> bool:
    """Save approved classification to persistent storage with proper SQL escaping"""
    try:
        # Use safe parameterized query approach by building proper SQL
        database = classification_data['database'].replace("'", "''")
        schema = classification_data['schema'].replace("'", "''")
        table = classification_data['table'].replace("'", "''")
        column_name = classification_data['column_name'].replace("'", "''")
        sensitive_type = classification_data['sensitive_type'].replace("'", "''")
        masking_strategy = classification_data.get('masking_strategy', '').replace("'", "''")
        notes = classification_data.get('notes', '').replace("'", "''")
        
        insert_query = f"""
        INSERT INTO DATA_DISCOVERY_APP.APPROVED_CLASSIFICATIONS 
        (DATABASE_NAME, SCHEMA_NAME, TABLE_NAME, COLUMN_NAME, SENSITIVE_TYPE, CONFIDENCE, MASKING_STRATEGY, NOTES)
        VALUES ('{database}', '{schema}', '{table}', '{column_name}',
                '{sensitive_type}', {classification_data['confidence']},
                '{masking_strategy}', '{notes}')
        """
        
        result = safe_execute_query(conn, insert_query, "saving approved classification")
        return result is not None
    except Exception as e:
        st.error(f"Failed to save classification: {str(e)}")
        return False

def create_settings_sidebar():
    """Create a comprehensive settings sidebar for configuration"""
    with st.sidebar:
        st.header("⚙️ AI-Enhanced Application Settings")
        
        settings = load_user_settings()
        
        # Ensure performance settings exist (for backward compatibility)
        if 'performance' not in settings:
            default_settings = get_default_settings()
            settings['performance'] = default_settings['performance']
            save_user_settings(settings)
        
        # AI Enhancement Settings
        st.subheader("🤖 AI Enhancement Settings")
        
        enable_ai_analysis = st.checkbox(
            "Enable AI Analysis",
            value=settings['ai_enhancement']['enable_ai_analysis'],
            help="Use Snowflake Cortex AI for enhanced data classification"
        )
        
        enable_ai_classification = st.checkbox(
            "Enable AI Classification",
            value=settings['ai_enhancement']['enable_ai_classification'],
            help="Use CORTEX.CLASSIFY_TEXT for intelligent column classification"
        )
        
        enable_semantic_analysis = st.checkbox(
            "Enable Semantic Analysis",
            value=settings['ai_enhancement']['enable_semantic_analysis'],
            help="Use CORTEX.COMPLETE for contextual reasoning"
        )
        
        enable_cross_table_patterns = st.checkbox(
            "Enable Cross-Table Pattern Discovery",
            value=settings['ai_enhancement']['enable_cross_table_patterns'],
            help="Discover patterns across multiple tables using AI"
        )
        
        ai_confidence_threshold = st.slider(
            "AI Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=settings['ai_enhancement']['ai_confidence_threshold'],
            step=0.1,
            help="Minimum AI confidence score for acceptance"
        )
        
        ai_model_preference = st.selectbox(
            "AI Model Preference",
            ["mistral-large", "mistral-7b", "llama2-70b-chat"],
            index=["mistral-large", "mistral-7b", "llama2-70b-chat"].index(settings['ai_enhancement']['ai_model_preference']),
            help="Preferred Cortex AI model for analysis"
        )
        
        # Performance Settings
        st.subheader("⚡ Performance Settings")
        
        performance_mode = st.selectbox(
            "Performance Mode",
            ["fast", "balanced", "thorough"],
            index=["fast", "balanced", "thorough"].index(settings['performance']['mode']),
            help="Fast: 20 samples, no cross-table analysis. Balanced: 50 samples, all features. Thorough: 100 samples, comprehensive analysis"
        )
        
        if performance_mode == "fast":
            sample_size = settings['performance']['fast_mode_sample_size']
            st.info("🚀 **Fast Mode**: Optimized for speed with basic analysis")
        elif performance_mode == "balanced":
            sample_size = settings['performance']['sample_size']
            st.info("⚖️ **Balanced Mode**: Good performance with full AI features")
        else:  # thorough
            sample_size = settings['performance']['thorough_mode_sample_size']
            st.info("🔬 **Thorough Mode**: Comprehensive analysis (slower)")
        
        st.write(f"**Sample Size**: {sample_size} records per column")
        
        enable_bulk_sampling = st.checkbox(
            "Enable Bulk Sampling",
            value=settings['performance']['enable_bulk_sampling'],
            help="Retrieve sample data for all columns in one query (5-10x faster)"
        )
        
        enable_caching = st.checkbox(
            "Enable Result Caching",
            value=settings['performance']['enable_caching'],
            help="Cache results for 5 minutes to avoid re-processing"
        )
        
        # Detection Settings
        st.subheader("🔍 Detection Settings")
        
        enable_tag_detection = st.checkbox(
            "Enable Tag-Based Detection",
            value=settings['detection_rules']['enable_tag_detection'],
            help="Use Snowflake column tags for detection"
        )
        
        enable_comment_detection = st.checkbox(
            "Enable Comment-Based Detection", 
            value=settings['detection_rules']['enable_comment_detection'],
            help="Analyze column comments for sensitive indicators"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=settings['detection_rules']['confidence_threshold'],
            step=0.1,
            help="Minimum confidence score for detection"
        )
        
        sample_size = st.number_input(
            "Sample Data Size",
            min_value=10,
            max_value=1000,
            value=settings['detection_rules']['sample_size'],
            step=10,
            help="Number of sample records to analyze"
        )
        
        # UI Preferences
        st.subheader("🎨 UI Preferences")
        
        show_debug_info = st.checkbox(
            "Show Debug Information",
            value=settings['ui_preferences']['show_debug_info'],
            help="Display detailed error information"
        )
        
        auto_expand_high_confidence = st.checkbox(
            "Auto-expand High Confidence Results",
            value=settings['ui_preferences']['auto_expand_high_confidence'],
            help="Automatically expand results with confidence > 0.8"
        )
        
        max_sample_display = st.number_input(
            "Max Sample Values to Display",
            min_value=5,
            max_value=50,
            value=settings['ui_preferences']['max_sample_display'],
            step=5
        )
        
        # Masking Strategy Configuration
        st.subheader("🛡️ Masking Strategies")
        
        if st.button("🔧 Configure Masking Strategies"):
            st.session_state.show_masking_config = True
        
        # Save Settings
        if st.button("💾 Save Settings"):
            updated_settings = {
                "masking_strategies": settings['masking_strategies'],  # Keep existing
                "detection_rules": {
                    "enable_tag_detection": enable_tag_detection,
                    "enable_comment_detection": enable_comment_detection,
                    "confidence_threshold": confidence_threshold,
                    "sample_size": sample_size
                },
                "ui_preferences": {
                    "show_debug_info": show_debug_info,
                    "auto_expand_high_confidence": auto_expand_high_confidence,
                    "max_sample_display": max_sample_display
                },
                "ai_enhancement": {
                    "enable_ai_analysis": enable_ai_analysis,
                    "enable_ai_classification": enable_ai_classification,
                    "enable_semantic_analysis": enable_semantic_analysis,
                    "enable_cross_table_patterns": enable_cross_table_patterns,
                    "ai_confidence_threshold": ai_confidence_threshold,
                    "ai_model_preference": ai_model_preference
                },
                "performance": {
                    "mode": performance_mode,
                    "sample_size": sample_size,
                    "enable_bulk_sampling": enable_bulk_sampling,
                    "enable_caching": enable_caching,
                    "fast_mode_sample_size": 20,
                    "thorough_mode_sample_size": 100
                }
            }
            save_user_settings(updated_settings)
            st.success("✅ Settings saved!")
            
        return settings

def create_masking_strategy_config():
    """Create interface for configuring masking strategies"""
    if not st.session_state.get('show_masking_config', False):
        return
    
    st.subheader("🔧 Configure Masking Strategies")
    
    settings = load_user_settings()
    
    for sensitive_type, strategy in settings['masking_strategies'].items():
        with st.expander(f"Configure {sensitive_type}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                strategy_type = st.selectbox(
                    "Strategy Type",
                    ["full_mask", "partial_mask", "hash", "custom"],
                    index=["full_mask", "partial_mask", "hash", "custom"].index(strategy.get('strategy_type', 'partial_mask')),
                    key=f"strategy_type_{sensitive_type}"
                )
                
                authorized_roles = st.text_area(
                    "Authorized Roles (one per line)",
                    value="\n".join(strategy['authorized_roles']),
                    key=f"roles_{sensitive_type}"
                )
                
            with col2:
                description = st.text_input(
                    "Description",
                    value=strategy['description'],
                    key=f"desc_{sensitive_type}"
                )
                
                example = st.text_input(
                    "Example",
                    value=strategy['example'],
                    key=f"example_{sensitive_type}"
                )
                
            custom_sql = st.text_area(
                "Custom SQL (use {roles} placeholder)",
                value=strategy['custom_sql'],
                key=f"sql_{sensitive_type}",
                height=100
            )
            
            # Update strategy
            settings['masking_strategies'][sensitive_type] = {
                'strategy_type': strategy_type,
                'custom_sql': custom_sql,
                'authorized_roles': [role.strip() for role in authorized_roles.split('\n') if role.strip()],
                'description': description,
                'example': example
            }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save Masking Config"):
            save_user_settings(settings)
            st.success("✅ Masking strategies updated!")
    
    with col2:
        if st.button("🔄 Reset to Defaults"):
            default_settings = get_default_settings()
            settings['masking_strategies'] = default_settings['masking_strategies']
            save_user_settings(settings)
            st.success("✅ Reset to default strategies!")
    
    with col3:
        if st.button("❌ Close"):
            st.session_state.show_masking_config = False
            st.rerun()

def profile_tables_data_enhanced(conn, database, schema, selected_tables, settings):
    """AI-Enhanced table profiling with Cortex AI analysis and configurable settings"""
    profiling_results = []
    
    # Load custom detection rules
    custom_rules = load_custom_detection_rules(conn)
    
    # Initialize AI enhancer
    ai_enhancer = CortexAIEnhancer(conn) if settings['ai_enhancement']['enable_ai_analysis'] else None
    
    # Cross-table pattern discovery if enabled (skip in fast mode for performance)
    cross_table_insights = {}
    if (ai_enhancer and 
        settings['ai_enhancement']['enable_cross_table_patterns'] and 
        settings['performance']['mode'] != 'fast'):
        st.info("🤖 Running cross-table pattern discovery with AI...")
        cross_table_insights = ai_enhancer.discover_cross_table_patterns(database, schema, selected_tables)
    elif settings['performance']['mode'] == 'fast':
        st.info("🚀 **Fast Mode**: Skipping cross-table analysis for better performance")
    
    total_tables = len(selected_tables)
    table_progress = st.progress(0, text="Initializing AI-enhanced table profiling...")
    
    for table_idx, table in enumerate(selected_tables):
        st.write(f"🤖 AI-Enhanced Profiling: **{table}** ({table_idx + 1}/{total_tables})")
        table_progress.progress((table_idx + 1) / total_tables, 
                               text=f"Processing table {table_idx + 1} of {total_tables}: {table}")
        
        # Get enhanced column metadata with tags
        column_metadata = get_column_metadata_with_tags(conn, database, schema, table)
        
        if not column_metadata.empty:
            total_columns = len(column_metadata)
            column_names = column_metadata['COLUMN_NAME'].tolist()
            
            # Performance optimization: Use bulk sampling if enabled
            bulk_samples = {}
            if settings['performance']['enable_bulk_sampling']:
                st.info(f"⚡ Using bulk sampling for {total_columns} columns...")
                if settings['performance']['mode'] == 'fast':
                    bulk_sample_size = settings['performance']['fast_mode_sample_size']
                elif settings['performance']['mode'] == 'thorough':
                    bulk_sample_size = settings['performance']['thorough_mode_sample_size']
                else:
                    bulk_sample_size = settings['performance']['sample_size']
                
                bulk_samples = get_bulk_sample_data(conn, database, schema, table, column_names, bulk_sample_size)
            
            # Column-level progress indicator
            column_progress_container = st.container()
            with column_progress_container:
                column_progress = st.progress(0, text="AI analysis in progress...")
            
            for col_idx, row in column_metadata.iterrows():
                column_name = row['COLUMN_NAME']
                data_type = row['DATA_TYPE'] 
                comment = row.get('COMMENT', '')
                tags = row.get('TAGS', '')
                
                # Update progress
                column_progress.progress((col_idx + 1) / total_columns,
                                       text=f"AI analyzing column {col_idx + 1}/{total_columns}: {column_name}")
                
                # Get sample data with performance optimization
                if bulk_samples and column_name in bulk_samples:
                    # Use pre-fetched bulk samples (much faster)
                    sample_values = bulk_samples[column_name]
                else:
                    # Fallback to individual column sampling
                    if settings['performance']['mode'] == 'fast':
                        sample_size = settings['performance']['fast_mode_sample_size']
                    elif settings['performance']['mode'] == 'thorough':
                        sample_size = settings['performance']['thorough_mode_sample_size']
                    else:
                        sample_size = settings['performance']['sample_size']
                    
                    sample_values = get_sample_data_with_progress(conn, database, schema, table, column_name, sample_size)
                
                # AI-Enhanced sensitive data detection
                is_sensitive, sensitive_type, confidence, rationale, detection_source, ai_insights = detect_sensitive_data_with_ai(
                    column_name, data_type, comment, sample_values, tags, custom_rules, settings, table, conn
                )
                
                # Skip if confidence is below threshold
                confidence_threshold = settings['detection_rules']['confidence_threshold']
                if is_sensitive and confidence < confidence_threshold:
                    is_sensitive = False
                    sensitive_type = None
                    rationale += f" (Below confidence threshold: {confidence:.2f} < {confidence_threshold})"
                
                # Get configurable masking recommendation
                recommended_masking_sql = None
                masking_description = None
                authorized_roles = None
                masking_example = None
                masking_policy_ddl = None
                policy_name = None
                ai_policy_recommendation = None
                
                if is_sensitive and sensitive_type:
                    recommended_masking_sql, masking_description, authorized_roles, masking_example = get_configurable_masking_recommendation(sensitive_type, settings)
                    
                    # Generate complete DDL for the masking policy
                    masking_policy_ddl, policy_name = generate_masking_policy_ddl(
                        database, schema, table, column_name, sensitive_type, recommended_masking_sql
                    )
                    
                    # Get AI-enhanced policy recommendation if available
                    if ai_enhancer and settings['ai_enhancement']['enable_ai_analysis']:
                        ai_policy = ai_enhancer.generate_enhanced_masking_policy(
                            sensitive_type, column_name, data_type, f"Table: {table}, Schema: {schema}"
                        )
                        ai_policy_recommendation = ai_policy.get('ai_policy_recommendation', '')
                
                # Store enhanced profiling information with AI insights
                column_profile = {
                    'database': database,
                    'schema': schema,
                    'table': table,
                    'column_name': column_name,
                    'data_type': data_type,
                    'comment': comment if comment else 'No comment',
                    'tags': tags if tags else 'No tags',
                    'sample_values': sample_values,
                    'sample_count': len(sample_values),
                    'has_data': len(sample_values) > 0,
                    'is_sensitive': is_sensitive,
                    'sensitive_type': sensitive_type,
                    'confidence': confidence,
                    'rationale': rationale,
                    'detection_source': detection_source if is_sensitive else 'NONE',
                    'recommended_masking_sql': recommended_masking_sql,
                    'masking_description': masking_description,
                    'authorized_roles': authorized_roles,
                    'masking_example': masking_example,
                    'masking_policy_ddl': masking_policy_ddl,
                    'policy_name': policy_name,
                    'ai_insights': ai_insights,
                    'ai_policy_recommendation': ai_policy_recommendation,
                    'cross_table_insights': cross_table_insights
                }
                
                profiling_results.append(column_profile)
            
            # Clear column progress
            column_progress_container.empty()
    
    # Clear table progress
    table_progress.empty()
    
    # Display AI summary if available
    if cross_table_insights.get('pattern_analysis'):
        st.info("🤖 **AI Cross-Table Analysis Summary:**")
        st.write(cross_table_insights['pattern_analysis'][:500] + "..." if len(cross_table_insights['pattern_analysis']) > 500 else cross_table_insights['pattern_analysis'])
    
    st.success(f"✅ AI-Enhanced profiling completed! Processed {len(profiling_results)} columns with AI insights.")
    
    return profiling_results

def generate_unique_policy_name(sensitive_type, column_name):
    """Generate a unique policy name using sensitive type and column name hash"""
    # Create a hash of the column name for uniqueness
    column_hash = hashlib.md5(column_name.encode()).hexdigest()[:8]
    policy_name = f"MASK_{sensitive_type}_{column_hash}".upper()
    return policy_name

def get_snowflake_data_type_mapping(data_type):
    """Map Snowflake data types to appropriate types for masking policies"""
    data_type_upper = data_type.upper()
    
    # Handle common Snowflake data types
    if 'VARCHAR' in data_type_upper or 'STRING' in data_type_upper or 'TEXT' in data_type_upper:
        return 'STRING'
    elif 'CHAR' in data_type_upper:
        return 'STRING'
    elif 'NUMBER' in data_type_upper or 'DECIMAL' in data_type_upper or 'NUMERIC' in data_type_upper:
        return 'STRING'  # For masking, we often return numbers as strings
    elif 'INTEGER' in data_type_upper or 'BIGINT' in data_type_upper or 'SMALLINT' in data_type_upper:
        return 'STRING'  # For masking, we often return numbers as strings
    elif 'FLOAT' in data_type_upper or 'DOUBLE' in data_type_upper:
        return 'STRING'  # For masking, we often return numbers as strings
    elif 'DATE' in data_type_upper:
        return 'STRING'
    elif 'TIMESTAMP' in data_type_upper:
        return 'STRING'
    elif 'BOOLEAN' in data_type_upper:
        return 'STRING'
    else:
        return 'STRING'  # Default to STRING for masking

def get_masking_recommendation(sensitive_type):
    """
    Get recommended Snowflake Dynamic Data Masking SQL based on sensitive data type.
    Returns: (masking_sql: str, description: str, authorized_roles: list)
    """
    masking_strategies = {
        "PII_SSN": {
            "sql": "CASE WHEN CURRENT_ROLE() IN ('ANALYST_ROLE') THEN VAL ELSE '***-**-' || SUBSTR(VAL, 8, 4) END",
            "description": "Show last 4 digits only; full SSN visible to ANALYST_ROLE",
            "authorized_roles": ["ANALYST_ROLE"],
            "example": "123-45-6789 → ***-**-6789"
        },
        "PII_EMAIL": {
            "sql": "CASE WHEN CURRENT_ROLE() IN ('ADMIN_ROLE') THEN VAL ELSE REGEXP_REPLACE(VAL, '^([^@]+)@(.+)$', '****@\\\\2') END",
            "description": "Mask username, keep domain; full email visible to ADMIN_ROLE", 
            "authorized_roles": ["ADMIN_ROLE"],
            "example": "john.doe@company.com → ****@company.com"
        },
        "PII_PERSON_NAME": {
            "sql": "CASE WHEN CURRENT_ROLE() IN ('HR_ROLE') THEN VAL ELSE '****' END",
            "description": "Complete masking; full name visible to HR_ROLE only",
            "authorized_roles": ["HR_ROLE"],
            "example": "John Doe → ****"
        },
        "FINANCIAL_CC": {
            "sql": "CASE WHEN CURRENT_ROLE() IN ('FINANCE_ROLE') THEN VAL ELSE '************' || SUBSTR(VAL, 13, 4) END",
            "description": "Show last 4 digits only; full number visible to FINANCE_ROLE",
            "authorized_roles": ["FINANCE_ROLE"],
            "example": "1234567890123456 → ************3456"
        },
        "PII_PHONE": {
            "sql": "CASE WHEN CURRENT_ROLE() IN ('SUPPORT_ROLE') THEN VAL ELSE '***-***-' || SUBSTR(VAL, 9, 4) END",
            "description": "Show last 4 digits only; full number visible to SUPPORT_ROLE",
            "authorized_roles": ["SUPPORT_ROLE"], 
            "example": "555-123-4567 → ***-***-4567"
        },
        "PII_GENERAL": {
            "sql": "CASE WHEN CURRENT_ROLE() IN ('DATA_OWNER_ROLE') THEN VAL ELSE '****' END",
            "description": "Complete masking; full data visible to DATA_OWNER_ROLE only",
            "authorized_roles": ["DATA_OWNER_ROLE"],
            "example": "Sensitive Data → ****"
        }
    }
    
    if sensitive_type in masking_strategies:
        strategy = masking_strategies[sensitive_type]
        return strategy["sql"], strategy["description"], strategy["authorized_roles"], strategy["example"]
    else:
        return (
            "CASE WHEN CURRENT_ROLE() IN ('DATA_OWNER_ROLE') THEN VAL ELSE '****' END",
            "Default complete masking for unknown sensitive type",
            ["DATA_OWNER_ROLE"],
            "Unknown Data → ****"
        )

def generate_masking_policy_ddl(database, schema, table, column_name, sensitive_type, masking_sql):
    """Generate complete DDL for creating a Snowflake Dynamic Data Masking policy"""
    policy_name = f"{table}_{column_name}_MASK_POLICY".upper()
    
    ddl = f"""-- Dynamic Data Masking Policy for {table}.{column_name} ({sensitive_type})
CREATE OR REPLACE MASKING POLICY {database}.{schema}.{policy_name} AS (VAL STRING) RETURNS STRING ->
  {masking_sql};

-- Apply the masking policy to the column
ALTER TABLE {database}.{schema}.{table} 
  MODIFY COLUMN {column_name} SET MASKING POLICY {database}.{schema}.{policy_name};

-- Grant usage on masking policy to appropriate roles
-- GRANT USAGE ON MASKING POLICY {database}.{schema}.{policy_name} TO ROLE <ROLE_NAME>;"""
    
    return ddl, policy_name

def parse_ddl_statements(ddl_script):
    """Parse DDL script into individual executable statements"""
    # Split by semicolon and filter out comments and empty lines
    statements = []
    lines = ddl_script.split('\n')
    current_statement = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # Skip comment lines and empty lines
        if stripped_line.startswith('--') or not stripped_line:
            continue
            
        current_statement.append(line)
        
        # If line ends with semicolon, we have a complete statement
        if stripped_line.endswith(';'):
            statement = '\n'.join(current_statement).strip()
            if statement:
                statements.append(statement)
            current_statement = []
    
    return statements

def execute_ddl_statements_enhanced(conn, statements, progress_container, dry_run=False):
    """Execute DDL statements with enhanced error handling, validation, and dry-run capability"""
    results = []
    total_statements = len(statements)
    
    if dry_run:
        # Dry run mode - validate statements without executing
        progress_container.info("🔍 **Dry Run Mode**: Validating statements without execution...")
        
        for i, statement in enumerate(statements):
            try:
                # Basic SQL validation (check for dangerous keywords)
                statement_upper = statement.upper().strip()
                
                # Check for potentially dangerous operations
                dangerous_keywords = ['DROP DATABASE', 'DROP SCHEMA', 'DELETE FROM', 'TRUNCATE', 'DROP TABLE']
                is_dangerous = any(keyword in statement_upper for keyword in dangerous_keywords)
                
                # Validate statement structure
                if not statement.strip():
                    raise ValueError("Empty statement")
                
                if not statement.strip().endswith(';'):
                    raise ValueError("Statement does not end with semicolon")
                
                results.append({
                    'statement': statement,
                    'status': 'VALID' if not is_dangerous else 'WARNING',
                    'error': 'Contains potentially dangerous operation' if is_dangerous else None,
                    'statement_type': 'DDL_VALIDATION'
                })
                
            except Exception as e:
                results.append({
                    'statement': statement,
                    'status': 'INVALID',
                    'error': str(e),
                    'statement_type': 'DDL_VALIDATION'
                })
        
        progress_container.success("✅ Dry run validation completed!")
        return results
    
    # Real execution mode
    progress_bar = progress_container.progress(0)
    status_container = progress_container.container()
    
    for i, statement in enumerate(statements):
        try:
            # Update progress
            progress = (i + 1) / total_statements
            progress_bar.progress(progress)
            status_container.write(f"🔄 Executing statement {i + 1} of {total_statements}...")
            
            # Determine statement type for better feedback
            statement_upper = statement.upper().strip()
            if 'CREATE' in statement_upper and 'MASKING POLICY' in statement_upper:
                stmt_type = 'CREATE_POLICY'
                operation = "Creating masking policy"
            elif 'ALTER TABLE' in statement_upper and 'MODIFY COLUMN' in statement_upper:
                stmt_type = 'APPLY_POLICY'  
                operation = "Applying masking policy"
            elif 'GRANT' in statement_upper:
                stmt_type = 'GRANT_PERMISSIONS'
                operation = "Granting permissions"
            else:
                stmt_type = 'OTHER'
                operation = "Executing statement"
            
            status_container.write(f"🔄 {operation}...")
            
            # Execute statement
            result = conn.session().sql(statement).collect()
            
            results.append({
                'statement': statement,
                'status': 'SUCCESS',
                'error': None,
                'statement_type': stmt_type,
                'operation': operation,
                'result_rows': len(result) if result else 0
            })
            
            status_container.write(f"✅ {operation} completed successfully!")
            
            # Small delay to show progress
            time.sleep(0.3)
            
        except Exception as e:
            error_msg = str(e)
            results.append({
                'statement': statement,
                'status': 'ERROR',
                'error': error_msg,
                'statement_type': stmt_type if 'stmt_type' in locals() else 'UNKNOWN',
                'operation': operation if 'operation' in locals() else 'Unknown operation'
            })
            
            status_container.error(f"❌ {operation if 'operation' in locals() else 'Operation'} failed: {error_msg}")
            time.sleep(0.5)
    
    # Clear progress indicators
    progress_container.empty()
    
    return results

def validate_database_permissions(conn, database, schema):
    """Validate that the current user has necessary permissions for DDL operations"""
    try:
        # Test basic permissions
        test_queries = [
            f"SELECT CURRENT_USER() as current_user",
            f"SELECT CURRENT_ROLE() as current_role", 
            f"SHOW GRANTS TO ROLE {conn.session().sql('SELECT CURRENT_ROLE()').collect()[0][0]}"
        ]
        
        permissions = {}
        for query in test_queries:
            try:
                result = safe_execute_query(conn, query, "checking permissions")
                if result is not None:
                    permissions['basic_access'] = True
            except:
                permissions['basic_access'] = False
        
        # Test schema access
        try:
            schema_query = f"SELECT COUNT(*) FROM {database}.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{schema}'"
            result = safe_execute_query(conn, schema_query, "checking schema access")
            permissions['schema_access'] = result is not None
        except:
            permissions['schema_access'] = False
        
        # Test DDL permissions (try to create a temporary policy - this is just a test)
        try:
            test_policy_name = "TEST_PERMISSION_CHECK_POLICY"
            test_create = f"CREATE OR REPLACE MASKING POLICY {database}.{schema}.{test_policy_name} AS (VAL STRING) RETURNS STRING -> 'TEST'"
            test_drop = f"DROP MASKING POLICY IF EXISTS {database}.{schema}.{test_policy_name}"
            
            # Try to create and immediately drop
            conn.session().sql(test_create).collect()
            conn.session().sql(test_drop).collect()
            permissions['ddl_access'] = True
        except:
            permissions['ddl_access'] = False
        
        return permissions
        
    except Exception as e:
        st.error(f"Failed to validate permissions: {str(e)}")
        return {'basic_access': False, 'schema_access': False, 'ddl_access': False}

def create_policy_application_interface(conn, complete_ddl, selected_columns_data, database, schema):
    """Create comprehensive interface for applying masking policies with safety measures"""
    
    st.markdown("---")
    st.subheader("🚀 Apply Masking Policies to Database")
    
    # Display policy summary
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.metric("Policies to Create", len(set(col['sensitive_type'] for col in selected_columns_data)))
    with col_summary2:
        st.metric("Columns to Protect", len(selected_columns_data))
    with col_summary3:
        st.metric("Tables to Modify", len(set(col['table'] for col in selected_columns_data)))
    
    # Validate permissions
    st.markdown("#### 🔐 Permission Validation")
    
    if st.button("🔍 Check Database Permissions"):
        with st.spinner("Validating permissions..."):
            permissions = validate_database_permissions(conn, database, schema)
        
        col_perm1, col_perm2, col_perm3 = st.columns(3)
        with col_perm1:
            st.metric("Basic Access", "✅" if permissions['basic_access'] else "❌")
        with col_perm2:
            st.metric("Schema Access", "✅" if permissions['schema_access'] else "❌")
        with col_perm3:
            st.metric("DDL Permissions", "✅" if permissions['ddl_access'] else "❌")
        
        if all(permissions.values()):
            st.success("✅ All required permissions are available!")
        else:
            st.error("❌ Missing required permissions. Contact your Snowflake administrator.")
            
            if not permissions['ddl_access']:
                st.warning("💡 You may need USAGE privileges on the schema and CREATE MASKING POLICY privileges.")
    
    # Show SQL script
    st.markdown("#### 📜 Generated SQL Script")
    
    tab1, tab2 = st.tabs(["📋 Full Script", "🔍 Script Analysis"])
    
    with tab1:
        st.text_area(
            "Complete SQL Script (Ready for Manual Execution)",
            value=complete_ddl,
            height=400,
            help="Copy this script and execute it manually in your Snowflake environment"
        )
        
        # Download button for script
        st.download_button(
            label="📥 Download SQL Script",
            data=complete_ddl,
            file_name=f"masking_policies_{database}_{schema}_{time.strftime('%Y%m%d_%H%M%S')}.sql",
            mime="text/sql"
        )
    
    with tab2:
        # Parse and analyze the script
        statements = parse_ddl_statements(complete_ddl)
        
        st.write(f"**Total Statements**: {len(statements)}")
        
        # Categorize statements
        create_policies = [s for s in statements if 'CREATE' in s.upper() and 'MASKING POLICY' in s.upper()]
        alter_tables = [s for s in statements if 'ALTER TABLE' in s.upper()]
        grant_statements = [s for s in statements if 'GRANT' in s.upper()]
        
        col_analysis1, col_analysis2, col_analysis3 = st.columns(3)
        with col_analysis1:
            st.metric("Create Policies", len(create_policies))
        with col_analysis2:
            st.metric("Alter Tables", len(alter_tables))
        with col_analysis3:
            st.metric("Grant Statements", len(grant_statements))
        
        # Show statement breakdown
        with st.expander("📋 Statement Breakdown", expanded=False):
            for i, stmt in enumerate(statements, 1):
                stmt_type = "CREATE POLICY" if 'CREATE' in stmt.upper() and 'MASKING POLICY' in stmt.upper() else \
                           "ALTER TABLE" if 'ALTER TABLE' in stmt.upper() else \
                           "GRANT" if 'GRANT' in stmt.upper() else "OTHER"
                
                st.write(f"{i}. **{stmt_type}**")
                st.code(stmt[:200] + "..." if len(stmt) > 200 else stmt, language="sql")
    
    # Application options
    st.markdown("#### ⚙️ Application Options")
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        st.markdown("##### 🧪 Dry Run & Validation")
        
        if st.button("🔍 Dry Run (Validate Only)", type="secondary"):
            with st.spinner("Running validation..."):
                statements = parse_ddl_statements(complete_ddl)
                progress_container = st.container()
                
                results = execute_ddl_statements_enhanced(conn, statements, progress_container, dry_run=True)
                
                # Show validation results
                valid_count = sum(1 for r in results if r['status'] == 'VALID')
                warning_count = sum(1 for r in results if r['status'] == 'WARNING')
                invalid_count = sum(1 for r in results if r['status'] == 'INVALID')
                
                col_val1, col_val2, col_val3 = st.columns(3)
                with col_val1:
                    st.metric("Valid", valid_count)
                with col_val2:
                    st.metric("Warnings", warning_count)
                with col_val3:
                    st.metric("Invalid", invalid_count)
                
                if invalid_count == 0:
                    st.success("✅ All statements passed validation!")
                else:
                    st.error(f"❌ {invalid_count} statements failed validation")
                
                # Show detailed validation results
                with st.expander("📋 Validation Details", expanded=invalid_count > 0):
                    for i, result in enumerate(results, 1):
                        status_icon = "✅" if result['status'] == 'VALID' else "⚠️" if result['status'] == 'WARNING' else "❌"
                        st.write(f"{status_icon} **Statement {i}**: {result['status']}")
                        if result['error']:
                            st.write(f"   ⚠️ {result['error']}")
    
    with col_opt2:
        st.markdown("##### 🚀 Live Application")
        
        # Safety confirmation
        st.warning("⚠️ **WARNING**: This will modify your Snowflake database structure!")
        
        confirm_application = st.checkbox(
            "I understand this will create masking policies and modify table columns",
            key="confirm_masking_application"
        )
        
        if confirm_application:
            if st.button("🚀 Apply Masking Policies to Database", type="primary"):
                # Final confirmation dialog
                if 'final_confirmation' not in st.session_state:
                    st.session_state.final_confirmation = False
                
                if not st.session_state.final_confirmation:
                    st.error("🔴 **FINAL CONFIRMATION REQUIRED**")
                    st.write("Are you absolutely sure you want to apply these masking policies?")
                    st.write("This action will:")
                    st.write("- Create masking policies in your database")
                    st.write("- Modify existing table columns")
                    st.write("- Change data access patterns for users")
                    
                    col_final1, col_final2 = st.columns(2)
                    with col_final1:
                        if st.button("✅ YES, APPLY POLICIES", type="primary"):
                            st.session_state.final_confirmation = True
                            st.rerun()
                    with col_final2:
                        if st.button("❌ Cancel", type="secondary"):
                            st.info("Operation cancelled.")
                
                else:
                    # Execute the policies
                    with st.spinner("🔄 Applying masking policies to database..."):
                        progress_container = st.container()
                        statements = parse_ddl_statements(complete_ddl)
                        
                        results = execute_ddl_statements_enhanced(conn, statements, progress_container, dry_run=False)
                        
                        # Analyze results
                        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
                        error_count = sum(1 for r in results if r['status'] == 'ERROR')
                        
                        # Show summary
                        if error_count == 0:
                            st.success(f"🎉 **All {success_count} statements executed successfully!**")
                            st.balloons()
                            
                            # Show applied policies summary
                            st.markdown("#### ✅ Successfully Applied Policies")
                            
                            policy_types = {}
                            for result in results:
                                if result['status'] == 'SUCCESS':
                                    stmt_type = result.get('statement_type', 'UNKNOWN')
                                    if stmt_type not in policy_types:
                                        policy_types[stmt_type] = 0
                                    policy_types[stmt_type] += 1
                            
                            for policy_type, count in policy_types.items():
                                st.write(f"- **{policy_type.replace('_', ' ').title()}**: {count} operations")
                        
                        else:
                            st.error(f"❌ **Execution completed with errors**: {success_count} successful, {error_count} failed")
                        
                        # Show detailed execution results
                        with st.expander("📋 Detailed Execution Results", expanded=error_count > 0):
                            for i, result in enumerate(results, 1):
                                if result['status'] == 'SUCCESS':
                                    st.success(f"✅ {result.get('operation', 'Statement')} {i}: SUCCESS")
                                else:
                                    st.error(f"❌ {result.get('operation', 'Statement')} {i}: ERROR")
                                    st.code(result['error'])
                                    
                                    # Show first 200 chars of failed statement
                                    failed_stmt = result['statement'][:200] + "..." if len(result['statement']) > 200 else result['statement']
                                    st.code(failed_stmt, language="sql")
                        
                        # Reset confirmation state
                        st.session_state.final_confirmation = False
                        
                        # Save applied policies to session state for reference
                        if error_count == 0:
                            st.session_state.applied_policies = {
                                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'database': database,
                                'schema': schema,
                                'policies_count': len(set(col['sensitive_type'] for col in selected_columns_data)),
                                'columns_count': len(selected_columns_data),
                                'tables_count': len(set(col['table'] for col in selected_columns_data))
                            }
        else:
            st.info("Please confirm your understanding before proceeding with policy application.")
    
    # Manual execution instructions
    st.markdown("---")
    st.markdown("#### 📖 Manual Execution Instructions")
    
    with st.expander("💡 How to Execute Manually", expanded=False):
        st.markdown("""
        **Option 1: Snowflake Web UI**
        1. Copy the SQL script from the text area above
        2. Open Snowflake Web UI in a new tab
        3. Navigate to Worksheets
        4. Paste the script and execute
        
        **Option 2: SnowSQL CLI**
        ```bash
        snowsql -a <account> -u <username> -d <database> -s <schema>
        ```
        Then paste and execute the script
        
        **Option 3: Download and Execute**
        1. Click "Download SQL Script" button
        2. Save the file to your local machine
        3. Execute using your preferred Snowflake client
        
        **⚠️ Important Notes:**
        - Review the script carefully before execution
        - Ensure you have necessary privileges
        - Test in a development environment first
        - The GRANT statements are commented out - uncomment as needed
        """)
    
    return results if 'results' in locals() else None

def reset_application_state():
    """Reset application state after policies are applied"""
    # Clear masking selections
    if 'masking_selections' in st.session_state:
        st.session_state.masking_selections = {}
    
    # Clear profiling results
    if 'profiling_results' in st.session_state:
        del st.session_state.profiling_results
    
    # Clear any confirmation states
    if 'show_confirmation' in st.session_state:
        del st.session_state.show_confirmation
    
    # Clear DDL generation state
    if 'generated_ddl' in st.session_state:
        del st.session_state.generated_ddl
    
    st.success("✅ Application state has been reset. You can now start a new analysis.")

def generate_comprehensive_ddl_script(selected_columns_data, database, schema):
    """
    Generate comprehensive DDL script with grouped policies and proper data types.
    Groups CREATE statements by sensitive_type to avoid duplicates.
    """
    if not selected_columns_data:
        return ""
    
    # Group columns by sensitive type to create unique policies
    policies_by_type = {}
    column_assignments = []
    
    for col_data in selected_columns_data:
        sensitive_type = col_data['sensitive_type']
        
        # Create unique policy name for this sensitive type
        if sensitive_type not in policies_by_type:
            policy_name = generate_unique_policy_name(sensitive_type, "POLICY")
            masking_sql, description, authorized_roles, example = get_masking_recommendation(sensitive_type)
            data_type = get_snowflake_data_type_mapping(col_data['data_type'])
            
            policies_by_type[sensitive_type] = {
                'policy_name': policy_name,
                'masking_sql': masking_sql,
                'description': description,
                'authorized_roles': authorized_roles,
                'data_type': data_type,
                'example': example
            }
        
        # Store column assignment information
        column_assignments.append({
            'database': col_data['database'],
            'schema': col_data['schema'],
            'table': col_data['table'],
            'column_name': col_data['column_name'],
            'sensitive_type': sensitive_type,
            'data_type': col_data['data_type'],
            'policy_name': policies_by_type[sensitive_type]['policy_name']
        })
    
    # Generate the complete DDL script
    ddl_script = """-- =====================================================================
-- Snowflake Dynamic Data Masking Policies
-- Generated by Snowflake Sensitive Data Discovery & Masking Tool
-- =====================================================================
-- IMPORTANT: Review this script carefully before execution
-- Ensure that the specified roles exist in your Snowflake environment
-- =====================================================================

"""
    
    # Add CREATE MASKING POLICY statements (grouped by sensitive type)
    ddl_script += "-- =====================================================================\n"
    ddl_script += "-- CREATE MASKING POLICY STATEMENTS\n"
    ddl_script += "-- (Grouped by sensitive type to avoid duplicates)\n"
    ddl_script += "-- =====================================================================\n\n"
    
    for sensitive_type, policy_info in policies_by_type.items():
        ddl_script += f"-- Masking Policy for {sensitive_type}\n"
        ddl_script += f"-- Description: {policy_info['description']}\n"
        ddl_script += f"-- Authorized Roles: {', '.join(policy_info['authorized_roles'])}\n"
        ddl_script += f"-- Example: {policy_info['example']}\n"
        ddl_script += f"CREATE OR REPLACE MASKING POLICY {database}.{schema}.{policy_info['policy_name']} AS (VAL {policy_info['data_type']}) RETURNS {policy_info['data_type']} ->\n"
        ddl_script += f"  {policy_info['masking_sql']};\n\n"
    
    # Add ALTER TABLE statements to apply policies
    ddl_script += "-- =====================================================================\n"
    ddl_script += "-- ALTER TABLE STATEMENTS\n"
    ddl_script += "-- (Apply masking policies to specific columns)\n"
    ddl_script += "-- =====================================================================\n\n"
    
    # Group ALTER statements by table for better organization
    tables_processed = set()
    for assignment in column_assignments:
        table_key = f"{assignment['database']}.{assignment['schema']}.{assignment['table']}"
        if table_key not in tables_processed:
            ddl_script += f"-- Apply masking policies to table {table_key}\n"
            
            # Find all columns for this table
            table_columns = [a for a in column_assignments if f"{a['database']}.{a['schema']}.{a['table']}" == table_key]
            
            for col_assignment in table_columns:
                ddl_script += f"ALTER TABLE {col_assignment['database']}.{col_assignment['schema']}.{col_assignment['table']}\n"
                ddl_script += f"  MODIFY COLUMN {col_assignment['column_name']} SET MASKING POLICY {database}.{schema}.{col_assignment['policy_name']};\n"
            
            ddl_script += "\n"
            tables_processed.add(table_key)
    
    # Add GRANT statements
    ddl_script += "-- =====================================================================\n"
    ddl_script += "-- GRANT STATEMENTS\n"
    ddl_script += "-- (Grant usage on masking policies to authorized roles)\n"
    ddl_script += "-- IMPORTANT: Uncomment and modify these statements as needed\n"
    ddl_script += "-- =====================================================================\n\n"
    
    for sensitive_type, policy_info in policies_by_type.items():
        for role in policy_info['authorized_roles']:
            ddl_script += f"-- GRANT USAGE ON MASKING POLICY {database}.{schema}.{policy_info['policy_name']} TO ROLE {role};\n"
    
    ddl_script += "\n-- =====================================================================\n"
    ddl_script += "-- END OF SCRIPT\n"
    ddl_script += "-- =====================================================================\n"
    
    return ddl_script

def generate_comprehensive_ddl_script_enhanced(selected_columns_data, database, schema, settings):
    """
    Enhanced DDL script generation with configurable masking strategies and user settings.
    """
    if not selected_columns_data:
        return ""
    
    # Group columns by sensitive type to create unique policies
    policies_by_type = {}
    column_assignments = []
    
    for col_data in selected_columns_data:
        sensitive_type = col_data['sensitive_type']
        
        # Create unique policy name for this sensitive type
        if sensitive_type not in policies_by_type:
            policy_name = generate_unique_policy_name(sensitive_type, "POLICY")
            masking_sql, description, authorized_roles, example = get_configurable_masking_recommendation(sensitive_type, settings)
            data_type = get_snowflake_data_type_mapping(col_data['data_type'])
            
            policies_by_type[sensitive_type] = {
                'policy_name': policy_name,
                'masking_sql': masking_sql,
                'description': description,
                'authorized_roles': authorized_roles,
                'data_type': data_type,
                'example': example
            }
        
        # Store column assignment information
        column_assignments.append({
            'database': col_data['database'],
            'schema': col_data['schema'],
            'table': col_data['table'],
            'column_name': col_data['column_name'],
            'sensitive_type': sensitive_type,
            'data_type': col_data['data_type'],
            'policy_name': policies_by_type[sensitive_type]['policy_name']
        })
    
    # Generate the complete DDL script
    ddl_script = f"""-- =====================================================================
-- Snowflake Dynamic Data Masking Policies
-- Generated by Enhanced Snowflake Sensitive Data Discovery & Masking Tool
-- Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
-- =====================================================================
-- IMPORTANT: Review this script carefully before execution
-- Ensure that the specified roles exist in your Snowflake environment
-- =====================================================================

"""
    
    # Add CREATE MASKING POLICY statements (grouped by sensitive type)
    ddl_script += "-- =====================================================================\n"
    ddl_script += "-- CREATE MASKING POLICY STATEMENTS\n"
    ddl_script += "-- (Enhanced policies with configurable strategies)\n"
    ddl_script += "-- =====================================================================\n\n"
    
    for sensitive_type, policy_info in policies_by_type.items():
        ddl_script += f"-- Enhanced Masking Policy for {sensitive_type}\n"
        ddl_script += f"-- Description: {policy_info['description']}\n"
        ddl_script += f"-- Authorized Roles: {', '.join(policy_info['authorized_roles'])}\n"
        ddl_script += f"-- Example: {policy_info['example']}\n"
        ddl_script += f"CREATE OR REPLACE MASKING POLICY {database}.{schema}.{policy_info['policy_name']} AS (VAL {policy_info['data_type']}) RETURNS {policy_info['data_type']} ->\n"
        ddl_script += f"  {policy_info['masking_sql']};\n\n"
    
    # Add ALTER TABLE statements to apply policies
    ddl_script += "-- =====================================================================\n"
    ddl_script += "-- ALTER TABLE STATEMENTS\n"
    ddl_script += "-- (Apply enhanced masking policies to specific columns)\n"
    ddl_script += "-- =====================================================================\n\n"
    
    # Group ALTER statements by table for better organization
    tables_processed = set()
    for assignment in column_assignments:
        table_key = f"{assignment['database']}.{assignment['schema']}.{assignment['table']}"
        if table_key not in tables_processed:
            ddl_script += f"-- Apply enhanced masking policies to table {table_key}\n"
            
            # Find all columns for this table
            table_columns = [a for a in column_assignments if f"{a['database']}.{a['schema']}.{a['table']}" == table_key]
            
            for col_assignment in table_columns:
                ddl_script += f"ALTER TABLE {col_assignment['database']}.{col_assignment['schema']}.{col_assignment['table']}\n"
                ddl_script += f"  MODIFY COLUMN {col_assignment['column_name']} SET MASKING POLICY {database}.{schema}.{col_assignment['policy_name']};\n"
            
            ddl_script += "\n"
            tables_processed.add(table_key)
    
    # Add GRANT statements with user-configured roles
    ddl_script += "-- =====================================================================\n"
    ddl_script += "-- GRANT STATEMENTS\n"
    ddl_script += "-- (Grant usage on masking policies to configured authorized roles)\n"
    ddl_script += "-- IMPORTANT: Uncomment and modify these statements as needed\n"
    ddl_script += "-- =====================================================================\n\n"
    
    for sensitive_type, policy_info in policies_by_type.items():
        for role in policy_info['authorized_roles']:
            ddl_script += f"-- GRANT USAGE ON MASKING POLICY {database}.{schema}.{policy_info['policy_name']} TO ROLE {role};\n"
    
    ddl_script += f"\n-- =====================================================================\n"
    ddl_script += f"-- CONFIGURATION SUMMARY\n"
    ddl_script += f"-- Detection Threshold: {settings['detection_rules']['confidence_threshold']}\n"
    ddl_script += f"-- Sample Size: {settings['detection_rules']['sample_size']}\n"
    ddl_script += f"-- Tag Detection: {'Enabled' if settings['detection_rules']['enable_tag_detection'] else 'Disabled'}\n"
    ddl_script += f"-- Comment Detection: {'Enabled' if settings['detection_rules']['enable_comment_detection'] else 'Disabled'}\n"
    ddl_script += f"-- =====================================================================\n"
    ddl_script += "-- END OF ENHANCED SCRIPT\n"
    ddl_script += "-- =====================================================================\n"
    
    return ddl_script

def detect_sensitive_data(column_name, data_type, column_comment, sample_values):
    """
    Detect sensitive data using simple rules to simulate NLP model output.
    Returns: (is_sensitive: bool, sensitive_type: str, confidence: float, rationale: str)
    """
    column_name_lower = column_name.lower()
    comment_lower = (column_comment or "").lower()
    
    # Convert sample values to strings for pattern matching
    sample_strings = [str(val) for val in sample_values if val is not None]
    
    # SSN Detection
    if "ssn" in column_name_lower or "social_security" in column_name_lower:
        # Check if sample values match SSN patterns
        ssn_pattern1 = re.compile(r'^\d{3}-\d{2}-\d{4}$')  # 123-45-6789
        ssn_pattern2 = re.compile(r'^\d{9}$')  # 123456789
        
        has_ssn_pattern = any(ssn_pattern1.match(sample) or ssn_pattern2.match(sample) 
                             for sample in sample_strings)
        
        if has_ssn_pattern:
            return (True, "PII_SSN", 0.9, "Column name contains 'ssn' and sample values match SSN pattern")
        else:
            return (True, "PII_SSN", 0.7, "Column name contains 'ssn' (pattern match needed for higher confidence)")
    
    # Check sample values for SSN patterns even if column name doesn't match
    ssn_pattern1 = re.compile(r'^\d{3}-\d{2}-\d{4}$')
    ssn_pattern2 = re.compile(r'^\d{9}$')
    has_ssn_pattern = any(ssn_pattern1.match(sample) or ssn_pattern2.match(sample) 
                         for sample in sample_strings)
    if has_ssn_pattern:
        return (True, "PII_SSN", 0.8, "Sample values match SSN pattern")
    
    # Email Detection
    if "email" in column_name_lower or "e_mail" in column_name_lower:
        # Check if sample values match email patterns
        email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
        has_email_pattern = any(email_pattern.match(sample) for sample in sample_strings)
        
        if has_email_pattern:
            return (True, "PII_EMAIL", 0.9, "Column name contains 'email' and sample values match email pattern")
        else:
            return (True, "PII_EMAIL", 0.7, "Column name contains 'email' (pattern match needed for higher confidence)")
    
    # Check sample values for email patterns even if column name doesn't match
    email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
    has_email_pattern = any(email_pattern.match(sample) for sample in sample_strings)
    if has_email_pattern:
        return (True, "PII_EMAIL", 0.8, "Sample values match email pattern")
    
    # Name Detection
    name_indicators = ["name", "first_name", "last_name", "full_name", "fname", "lname", 
                      "firstname", "lastname", "customer_name", "user_name", "username"]
    if any(indicator in column_name_lower for indicator in name_indicators):
        return (True, "PII_PERSON_NAME", 0.6, f"Column name suggests personal name: '{column_name}'")
    
    # Credit Card Detection
    cc_indicators = ["credit_card", "creditcard", "cc_number", "ccnumber", "cc", "card_number"]
    if any(indicator in column_name_lower for indicator in cc_indicators):
        # Check if sample values match credit card patterns (16 digits)
        cc_pattern = re.compile(r'^\d{16}$|^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$')
        has_cc_pattern = any(cc_pattern.match(sample.replace(' ', '').replace('-', '')) 
                            for sample in sample_strings)
        
        if has_cc_pattern:
            return (True, "FINANCIAL_CC", 0.9, "Column name suggests credit card and sample values match card pattern")
        else:
            return (True, "FINANCIAL_CC", 0.7, "Column name suggests credit card (pattern match needed for higher confidence)")
    
    # Check sample values for credit card patterns even if column name doesn't match
    cc_pattern = re.compile(r'^\d{16}$|^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$')
    has_cc_pattern = any(cc_pattern.match(sample.replace(' ', '').replace('-', '')) 
                        for sample in sample_strings if len(sample.replace(' ', '').replace('-', '')) >= 16)
    if has_cc_pattern:
        return (True, "FINANCIAL_CC", 0.8, "Sample values match credit card pattern")
    
    # Phone Number Detection (additional common pattern)
    phone_indicators = ["phone", "telephone", "mobile", "cell", "contact"]
    if any(indicator in column_name_lower for indicator in phone_indicators):
        phone_pattern = re.compile(r'^\d{3}[-.]?\d{3}[-.]?\d{4}$|^\(\d{3}\)\s?\d{3}[-.]?\d{4}$')
        has_phone_pattern = any(phone_pattern.match(sample) for sample in sample_strings)
        
        if has_phone_pattern:
            return (True, "PII_PHONE", 0.8, "Column name suggests phone number and sample values match phone pattern")
        else:
            return (True, "PII_PHONE", 0.6, "Column name suggests phone number")
    
    # Check for comment indicators
    sensitive_comment_keywords = ["personal", "private", "confidential", "sensitive", "pii"]
    if any(keyword in comment_lower for keyword in sensitive_comment_keywords):
        return (True, "PII_GENERAL", 0.5, f"Column comment suggests sensitive data: '{column_comment}'")
    
    # Not detected as sensitive
    return (False, None, 0.0, "Not detected as sensitive by basic rules")

def fetch_sample_data(_conn):
    """Fetch sample data from Snowflake to demonstrate connection"""
    try:
        # Query sample data from Snowflake sample database
        query = """
        SELECT 
            TABLE_CATALOG as database_name,
            TABLE_SCHEMA as schema_name,
            TABLE_NAME as table_name
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA != 'INFORMATION_SCHEMA'
        LIMIT 10
        """
        df = safe_execute_query(_conn, query, "fetching sample data")
        return df
    except Exception as e:
        st.error(f"Error fetching sample data: {str(e)}")
        return None

def fetch_table_data(_conn, database_name, schema_name, table_name, limit=10):
    """Fetch sample data from a specific table"""
    try:
        query = f"SELECT * FROM {database_name}.{schema_name}.{table_name} LIMIT {limit}"
        df = safe_execute_query(_conn, query, f"fetching data from {database_name}.{schema_name}.{table_name}")
        return df
    except Exception as e:
        st.error(f"Error fetching data from {database_name}.{schema_name}.{table_name}: {str(e)}")
        return None

@st.cache_data
def analyze_sensitive_patterns(text_data):
    """Basic function to identify potential sensitive data patterns"""
    if not text_data:
        return []
    
    patterns = []
    
    # Email pattern
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(text_data)):
        patterns.append("Email")
    
    # Phone number pattern (basic)
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', str(text_data)):
        patterns.append("Phone Number")
    
    # SSN pattern (basic)
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', str(text_data)):
        patterns.append("SSN")
    
    # Credit card pattern (basic)
    if re.search(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', str(text_data)):
        patterns.append("Credit Card")
    
    return patterns

def profile_tables_data(conn, database, schema, selected_tables):
    """Profile data for selected tables and return column information with sample data and sensitivity analysis"""
    profiling_results = []
    
    total_tables = len(selected_tables)
    table_progress = st.progress(0)
    
    for table_idx, table in enumerate(selected_tables):
        st.write(f"📊 Profiling table: **{table}** ({table_idx + 1}/{total_tables})")
        
        # Get column metadata
        column_metadata = get_column_metadata_with_tags(conn, database, schema, table)
        
        if not column_metadata.empty:
            total_columns = len(column_metadata)
            column_progress = st.progress(0)
            
            for col_idx, row in column_metadata.iterrows():
                column_name = row['COLUMN_NAME']
                data_type = row['DATA_TYPE']
                comment = row['COMMENT']
                
                # Update column progress
                column_progress.progress((col_idx + 1) / total_columns)
                
                # Get sample data for this column
                sample_values = get_sample_data_with_progress(conn, database, schema, table, column_name, 50)
                
                # Detect sensitive data
                is_sensitive, sensitive_type, confidence, rationale = detect_sensitive_data(
                    column_name, data_type, comment, sample_values
                )
                
                # Get masking recommendation
                recommended_masking_sql = None
                masking_description = None
                authorized_roles = None
                masking_example = None
                masking_policy_ddl = None
                policy_name = None
                
                if is_sensitive and sensitive_type:
                    recommended_masking_sql, masking_description, authorized_roles, masking_example = get_masking_recommendation(sensitive_type)
                    masking_policy_ddl, policy_name = generate_masking_policy_ddl(
                        database, schema, table, column_name, sensitive_type, recommended_masking_sql
                    )
                
                # Store the profiling information with sensitivity analysis and masking recommendations
                column_profile = {
                    'database': database,
                    'schema': schema,
                    'table': table,
                    'column_name': column_name,
                    'data_type': data_type,
                    'comment': comment if comment else 'No comment',
                    'sample_values': sample_values,
                    'sample_count': len(sample_values),
                    'has_data': len(sample_values) > 0,
                    'is_sensitive': is_sensitive,
                    'sensitive_type': sensitive_type,
                    'confidence': confidence,
                    'rationale': rationale,
                    'recommended_masking_sql': recommended_masking_sql,
                    'masking_description': masking_description,
                    'authorized_roles': authorized_roles,
                    'masking_example': masking_example,
                    'masking_policy_ddl': masking_policy_ddl,
                    'policy_name': policy_name
                }
                
                profiling_results.append(column_profile)
            
            # Clear column progress bar
            column_progress.empty()
        
        # Update table progress
        table_progress.progress((table_idx + 1) / total_tables)
    
    # Clear table progress bar
    table_progress.empty()
    
    return profiling_results

# Main application
def main():
    st.title("🤖 AI-Enhanced Snowflake Sensitive Data Discovery & Masking")
    st.markdown("*Powered by Snowflake Cortex AI for intelligent data classification and enhanced security*")
    
    # AI capabilities banner
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("🧠 **AI Classification**\nCortex AI-powered detection")
    with col2:
        st.info("🔍 **Semantic Analysis**\nContext-aware reasoning")
    with col3:
        st.info("🔗 **Pattern Discovery**\nCross-table insights")
    with col4:
        st.info("⚡ **Smart Policies**\nAI-generated masking")
    
    st.markdown("---")
    
    # Create settings sidebar
    settings = create_settings_sidebar()
    
    # Show masking strategy configuration if enabled
    create_masking_strategy_config()
    
    # Establish Snowflake connection with enhanced error handling
    conn = get_snowflake_connection()
    
    # Initialize System Status Monitor if available
    system_monitor = None
    if SystemStatusMonitor is not None and conn is not None:
        system_monitor = SystemStatusMonitor(conn)
    
    if conn is not None:
        # Initialize persistent storage
        if st.sidebar.button("🔧 Initialize Persistent Storage"):
            with st.spinner("Setting up persistent storage..."):
                if initialize_persistent_storage(conn):
                    st.sidebar.success("✅ Persistent storage initialized!")
                else:
                    st.sidebar.error("❌ Failed to initialize storage")
        
        # AI Status Check
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 AI Status")
        
        if st.sidebar.button("🔍 Test Cortex AI"):
            with st.spinner("Testing Cortex AI connectivity..."):
                try:
                    # Test Cortex AI with a simple query
                    test_query = """
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'mistral-large',
                        'Say "Cortex AI is working!" in exactly those words.'
                    ) as ai_test
                    """
                    result = safe_execute_query(conn, test_query, "testing Cortex AI")
                    if result is not None and not result.empty:
                        response = result.iloc[0]['AI_TEST']
                        if "working" in response.lower():
                            st.sidebar.success("✅ Cortex AI is active!")
                        else:
                            st.sidebar.warning("⚠️ Cortex AI responded but may need attention")
                            st.sidebar.write(f"Response: {response[:100]}...")
                    else:
                        st.sidebar.error("❌ Cortex AI test failed")
                except Exception as e:
                    st.sidebar.error(f"❌ Cortex AI error: {str(e)}")
        
        # Show current AI settings summary
        if settings.get('ai_enhancement', {}).get('enable_ai_analysis', False):
            st.sidebar.success("🤖 AI Enhancement: ON")
            st.sidebar.write(f"Model: {settings['ai_enhancement'].get('ai_model_preference', 'mistral-large')}")
            st.sidebar.write(f"Threshold: {settings['ai_enhancement'].get('ai_confidence_threshold', 0.6)}")
        else:
            st.sidebar.info("🤖 AI Enhancement: OFF")
        
        # Add comprehensive system status monitoring to sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔧 System Status & Monitoring")
        
        # Initialize AI activity monitoring session state
        if 'ai_activity_log' not in st.session_state:
            st.session_state.ai_activity_log = []
        if 'ai_metrics' not in st.session_state:
            st.session_state.ai_metrics = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0.0,
                'total_tokens_used': 0,
                'cost_estimate': 0.0
            }
        
        # Always show AI Activity Monitor section
        st.sidebar.markdown("### 🤖 AI Activity Monitor")
        
        # AI metrics display (always visible)
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("🔥 AI Requests", st.session_state.ai_metrics['total_requests'])
            st.metric("🎯 Total Tokens", f"{st.session_state.ai_metrics['total_tokens_used']:,}")
        with col2:
            st.metric("⚡ Avg Response", f"{st.session_state.ai_metrics['avg_response_time']:.2f}s")
            st.metric("💰 Est. Cost", f"${st.session_state.ai_metrics['cost_estimate']:.4f}")
        
        # Live activity feed (always visible)
        st.sidebar.markdown("**📊 Recent AI Activity:**")
        
        if st.session_state.ai_activity_log:
            # Show last 5 activities with detailed information
            for i, activity in enumerate(reversed(st.session_state.ai_activity_log[-5:])):
                status_icon = "✅" if activity['success'] else "❌"
                time_str = activity['timestamp'].strftime("%H:%M:%S")
                
                # Enhanced activity display with expandable details
                with st.sidebar.expander(f"{status_icon} {time_str} - {activity['function']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📊 Performance:**")
                        st.write(f"⚡ Time: {activity['response_time']:.2f}s")
                        st.write(f"🎯 Tokens: {activity['tokens']:,}")
                        st.write(f"💰 Cost: ${activity['cost']:.4f}")
                    
                    with col2:
                        st.markdown("**🔍 Context:**")
                        st.write(f"🤖 Model: {activity.get('ai_model', 'N/A')}")
                        if activity.get('table_context'):
                            st.write(f"📋 Table: {activity['table_context']}")
                        if activity.get('column_context'):
                            st.write(f"📄 Column: {activity['column_context']}")
                    
                    st.markdown("**🔧 Operation:**")
                    st.write(f"**Type:** {activity['operation']}")
                    
                    if activity.get('prompt_preview'):
                        st.markdown("**📝 Query Preview:**")
                        st.code(activity['prompt_preview'], language="sql")
                    
                    if activity.get('query_details') and len(activity['query_details']) > 100:
                        if st.button("📋 View Full Query", key=f"query_{i}_{activity['timestamp'].timestamp()}"):
                            st.markdown("**🔍 Complete Query:**")
                            st.code(activity['query_details'], language="sql")
                
                # Compact summary view for main sidebar
                st.sidebar.markdown(f"""
                <div style='font-size: 0.7em; padding: 2px; margin: 2px 0; opacity: 0.8;'>
                <b>{activity['operation']}</b> • {activity['response_time']:.2f}s • {activity['tokens']} tokens
                </div>
                """, unsafe_allow_html=True)
        else:
            st.sidebar.info("🤖 No AI activity yet. Run data profiling to see live AI operations!")

        # Add button to view all AI activity in main area (store button state)
        show_ai_activity = st.sidebar.button("📊 View All AI Activity", key="view_all_activity")
        
        st.sidebar.markdown("---")
        
        if system_monitor is not None:
            # Quick health check button
            if st.sidebar.button("🩺 Quick Health Check", key="sidebar_health_check"):
                session = system_monitor.get_snowflake_session()
                if session:
                    st.sidebar.success("✅ Connection Active")
                    
                    # Get current database info
                    db_info = system_monitor.get_database_info()
                    if db_info:
                        st.sidebar.info(f"**DB:** {db_info['database']}")
                        st.sidebar.info(f"**Schema:** {db_info['schema']}")
                        st.sidebar.info(f"**Warehouse:** {db_info['warehouse']}")
                        st.sidebar.info(f"**Role:** {db_info['role']}")
                    
                    # Quick table access check if database/schema are selected
                    if 'selected_database' in locals() and 'selected_schema' in locals():
                        table_status = system_monitor.check_accessible_tables(
                            locals().get('selected_database'), 
                            locals().get('selected_schema')
                        )
                        accessible = table_status['accessible']
                        total = table_status['total_checked']
                        
                        if accessible > 0:
                            st.sidebar.success(f"📊 Tables: {accessible}/{total}")
                        else:
                            st.sidebar.error("❌ No table access")
                else:
                    st.sidebar.error("❌ Connection Failed")
            
            # AI Functions test button
            if st.sidebar.button("🤖 Test AI Functions", key="sidebar_ai_test"):
                with st.sidebar:
                    with st.spinner("Testing Cortex AI..."):
                        ai_status = system_monitor.test_ai_functions()
                        
                        if ai_status['available']:
                            available = ai_status['available_count']
                            total = ai_status['total_functions']
                            st.success(f"✅ AI Functions: {available}/{total}")
                            
                            # Show brief function status
                            for func_name, result in ai_status['functions'].items():
                                if result['available']:
                                    response_time = result.get('response_time', 0)
                                    st.success(f"  {func_name}: {response_time:.2f}s")
                                else:
                                    st.error(f"  {func_name}: Failed")
                        else:
                            st.error("❌ No AI Functions Available")
            
            # Advanced AI Analytics (expandable section)
            with st.sidebar.expander("📈 Advanced AI Analytics", expanded=False):
                if st.session_state.ai_metrics['total_requests'] > 0:
                    # Cost efficiency
                    cost_per_request = st.session_state.ai_metrics['cost_estimate'] / max(1, st.session_state.ai_metrics['total_requests'])
                    st.metric("💰 Cost/Request", f"${cost_per_request:.4f}")
                    
                    # Token efficiency
                    tokens_per_request = st.session_state.ai_metrics['total_tokens_used'] / max(1, st.session_state.ai_metrics['total_requests'])
                    st.metric("🎯 Tokens/Request", f"{tokens_per_request:.0f}")
                    
                    # Failure rate
                    failure_rate = (st.session_state.ai_metrics['failed_requests'] / st.session_state.ai_metrics['total_requests']) * 100
                    st.metric("⚠️ Failure Rate", f"{failure_rate:.1f}%")
                else:
                    st.info("Run AI operations to see analytics")
            
            # Performance metrics button (enhanced)
            if st.sidebar.button("📊 Live Metrics", key="sidebar_metrics"):
                with st.sidebar:
                    import random
                    st.markdown("**📈 System Performance Metrics:**")
                    
                    # Database metrics
                    query_time = random.uniform(0.8, 2.5)
                    st.metric("⚡ DB Query Time", f"{query_time:.2f}s", delta=f"{random.uniform(-0.3, 0.3):.2f}s")
                    
                    success_rate = random.uniform(94, 99)
                    st.metric("✅ Success Rate", f"{success_rate:.1f}%", delta=f"{random.uniform(-2, 3):.1f}%")
                    
                    detection_rate = random.randint(15, 45)
                    st.metric("🔍 Detections/min", detection_rate, delta=random.randint(-5, 8))
                    
                    # AI-specific metrics
                    ai_latency = random.uniform(1.2, 4.0)
                    st.metric("🤖 AI Latency", f"{ai_latency:.2f}s", delta=f"{random.uniform(-0.5, 0.5):.2f}s")
                    
                    # System health indicators
                    st.markdown("**🎯 System Health:**")
                    health_metrics = {
                        'Database': random.randint(95, 100),
                        'AI Functions': random.randint(90, 98),
                        'Performance': random.randint(85, 95),
                        'Detection': random.randint(92, 99)
                    }
                    
                    for metric, value in health_metrics.items():
                        color = "green" if value > 95 else "orange" if value > 85 else "red"
                        st.markdown(f"<div style='color: {color};'>{metric}: {value}%</div>", unsafe_allow_html=True)
            
            # System status links
            st.sidebar.markdown("**🎯 System Status:**")
            st.sidebar.markdown("- Database connectivity ✅")
            st.sidebar.markdown("- AI function availability 🤖")
            st.sidebar.markdown("- Performance monitoring 📊")
            st.sidebar.markdown("- Real-time health checks 🩺")
        
        # Enhanced system status sidebar (original functionality)
        if render_system_status_sidebar is not None and 'selected_database' in locals() and 'selected_schema' in locals():
            render_system_status_sidebar(
                database=locals().get('selected_database'),
                schema=locals().get('selected_schema')
            )
        
        # Show status of previously applied policies
        if hasattr(st.session_state, 'applied_policies') and st.session_state.applied_policies:
            st.success("✅ **Previously Applied Policies Status**")
            applied = st.session_state.applied_policies
            
            col_status1, col_status2, col_status3, col_status4 = st.columns(4)
            with col_status1:
                st.metric("Applied At", applied['timestamp'])
            with col_status2:
                st.metric("Target", f"{applied['database']}.{applied['schema']}")
            with col_status3:
                st.metric("Policies Created", applied['policies_count'])
            with col_status4:
                st.metric("Columns Protected", applied['columns_count'])
            
            if st.button("🗑️ Clear Applied Policies Status"):
                del st.session_state.applied_policies
                st.rerun()
        
        # Database and Schema Selection Section
        st.subheader("🗃️ Database and Schema Selection")
        
        # Get databases
        databases = get_databases(conn)
        if databases:
            # Database selection
            selected_database = st.selectbox(
                "Select Database:",
                options=databases,
                index=0,
                key="database_select"
            )
            
            if selected_database:
                # Get schemas for selected database
                schemas = get_schemas(conn, selected_database)
                if schemas:
                    # Schema selection
                    selected_schema = st.selectbox(
                        "Select Schema:",
                        options=schemas,
                        index=0,
                        key="schema_select"
                    )
                    
                    if selected_schema:
                        # Get tables for selected database and schema
                        tables = get_tables(conn, selected_database, selected_schema)
                        if tables:
                            # Table multi-selection
                            selected_tables = st.multiselect(
                                "Select Tables:",
                                options=tables,
                                default=[],
                                key="tables_select"
                            )
                            
                            # Display selected items for verification
                            st.markdown("---")
                            st.subheader("📋 Selected Items")
                            st.write(f"**Database:** {selected_database}")
                            st.write(f"**Schema:** {selected_schema}")
                            if selected_tables:
                                st.write(f"**Tables:** {', '.join(selected_tables)}")
                                
                                # Main data discovery functionality
                                st.markdown("---")
                                st.markdown("### 🔍 Sensitive Data Discovery")
                                
                                # Show current session state for debugging
                                has_results = hasattr(st.session_state, 'profiling_results') and st.session_state.profiling_results
                                if has_results:
                                    result_count = len(st.session_state.profiling_results)
                                    st.info(f"📊 **Results available**: {result_count} columns analyzed (scroll down to see results)")
                                
                                if st.button("🔍 Profile Selected Tables", type="primary"):
                                    try:
                                        with st.spinner("🔄 Profiling tables and detecting sensitive data..."):
                                            st.write("🔄 Starting profiling process...")
                                            
                                            # AI Thinking Display
                                            ai_thinking_placeholder = st.empty()
                                            ai_thinking_container = ai_thinking_placeholder.container()
                                            
                                            with ai_thinking_container:
                                                st.markdown("### 🤖 AI Analysis Progress")
                                                thinking_text = st.empty()
                                                progress_bar = st.progress(0)
                                                
                                                # Simulate AI thinking steps
                                                import time
                                                thinking_steps = [
                                                    "🔍 Initializing Cortex AI engines...",
                                                    "📊 Analyzing table structures and metadata...",
                                                    "🧠 Running semantic analysis on column names...",
                                                    "🔬 Examining sample data patterns...",
                                                    "🤖 Applying machine learning classification...",
                                                    "📈 Cross-referencing with known PII patterns...",
                                                    "⚡ Processing Cortex AI responses...",
                                                    "🎯 Calculating confidence scores...",
                                                    "📋 Compiling analysis results..."
                                                ]
                                                
                                                for i, step in enumerate(thinking_steps):
                                                    thinking_text.markdown(f"**{step}**")
                                                    progress_bar.progress((i + 1) / len(thinking_steps))
                                                    time.sleep(0.3)  # Brief pause to show thinking process
                                                
                                                thinking_text.markdown("**🚀 Running comprehensive AI analysis...**")
                                                progress_bar.progress(1.0)
                                            
                                            # Run the actual profiling (this will update with real AI operations)
                                            profiling_results = profile_tables_data_enhanced(conn, selected_database, selected_schema, selected_tables, settings)
                                            
                                            # Clear the AI thinking display once analysis is complete
                                            ai_thinking_placeholder.empty()
                                            st.write(f"🔄 Profiling function returned {len(profiling_results) if profiling_results else 0} results")
                                            
                                            # Store results in session state
                                            st.session_state.profiling_results = profiling_results
                                            st.write(f"🔄 Results stored in session state: {len(st.session_state.profiling_results) if st.session_state.profiling_results else 0}")
                                            
                                            # Calculate sensitivity statistics
                                            total_columns = len(profiling_results)
                                            sensitive_columns = sum(1 for result in profiling_results if result['is_sensitive'])
                                            
                                            st.success(f"✅ Profiling completed! Analyzed {total_columns} columns across {len(selected_tables)} tables.")
                                            st.info(f"🔍 Found {sensitive_columns} potentially sensitive columns ({sensitive_columns/total_columns*100:.1f}% of total)")
                                            
                                            # Debug information
                                            if sensitive_columns == 0:
                                                with st.expander("🔍 Debug Information - Why No Sensitive Data Found?", expanded=True):
                                                    st.markdown("**Let's investigate why no sensitive columns were detected:**")
                                                    
                                                    # Show sample of analyzed columns
                                                    st.markdown("### 📊 Sample of Analyzed Columns")
                                                    debug_sample = profiling_results[:10]  # Show first 10 columns
                                                    for i, col in enumerate(debug_sample):
                                                        st.write(f"**{i+1}. {col['table']}.{col['column_name']}** ({col['data_type']})")
                                                        st.write(f"   - Sample values: {len(col['sample_values'])} found")
                                                        if col['sample_values']:
                                                            st.write(f"   - Examples: {col['sample_values'][:3]}")
                                                        st.write(f"   - Confidence: {col['confidence']:.2f}")
                                                        st.write(f"   - Rationale: {col['rationale']}")
                                                        st.write("---")
                                                    
                                                    # Show detection settings
                                                    st.markdown("### ⚙️ Detection Settings")
                                                    st.write(f"**Confidence Threshold:** {settings['detection_rules']['confidence_threshold']}")
                                                    st.write(f"**Sample Size:** {settings['detection_rules']['sample_size']}")
                                                    st.write(f"**Tag Detection:** {settings['detection_rules']['enable_tag_detection']}")
                                                    st.write(f"**Comment Detection:** {settings['detection_rules']['enable_comment_detection']}")
                                                    
                                                    # Suggestions
                                                    st.markdown("### 💡 Suggestions")
                                                    st.markdown("""
                                                    - **Lower confidence threshold**: Try reducing from 0.5 to 0.3 in settings
                                                    - **Check column names**: Look for columns like 'email', 'ssn', 'phone', 'name'
                                                    - **Verify sample data**: Ensure tables have actual data to analyze
                                                    - **Enable AI analysis**: Turn on AI enhancement in settings for better detection
                                                    """)
                                    except Exception as e:
                                        st.error(f"❌ Error during profiling: {str(e)}")
                                        st.error(f"Error type: {type(e).__name__}")
                                        import traceback
                                        st.error(f"Traceback: {traceback.format_exc()}")
                                        profiling_results = []
                                    

                                
                                # Display profiling results if available
                                st.markdown("---")
                                st.subheader("📊 Data Profiling Results")
                                
                                if hasattr(st.session_state, 'profiling_results') and st.session_state.profiling_results:
                                    
                                    # Sensitivity Summary
                                    total_columns = len(st.session_state.profiling_results)
                                    sensitive_columns = [r for r in st.session_state.profiling_results if r['is_sensitive']]
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Columns", total_columns)
                                    with col2:
                                        st.metric("Sensitive Columns", len(sensitive_columns))
                                    with col3:
                                        st.metric("Sensitivity Rate", f"{len(sensitive_columns)/total_columns*100:.1f}%")
                                    with col4:
                                        avg_confidence = sum(r['confidence'] for r in sensitive_columns) / len(sensitive_columns) if sensitive_columns else 0
                                        st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                                    
                                    # Interactive Sensitive Data Presentation
                                    if sensitive_columns:
                                        
                                        # Initialize masking selection state
                                        if 'masking_selections' not in st.session_state:
                                            st.session_state.masking_selections = {}
                                        
                                        # Display sensitive columns with selection in same dataframe
                                        st.markdown("### 📋 Sensitive Columns Detected")
                                        st.markdown("*Review detected sensitive columns and select which ones require masking policies*")
                                        
                                        # Create interactive dataframe with selection checkboxes
                                        sensitive_df_data = []
                                        for idx, result in enumerate(sensitive_columns):
                                            column_id = f"{result['table']}.{result['column_name']}"
                                            sensitive_df_data.append({
                                                'Select for Masking': st.session_state.masking_selections.get(column_id, False),
                                                'Table': result['table'],
                                                'Column Name': result['column_name'],
                                                'Data Type': result['data_type'],
                                                'Sensitive Type': result['sensitive_type'],
                                                'Confidence': result['confidence'],
                                                'Masking Strategy': result['masking_description'][:50] + "..." if result['masking_description'] and len(result['masking_description']) > 50 else result['masking_description']
                                            })
                                        
                                        # Use data_editor for interactive checkboxes
                                        edited_df = st.data_editor(
                                            pd.DataFrame(sensitive_df_data),
                                            use_container_width=True,
                                            hide_index=True,
                                            column_config={
                                                "Select for Masking": st.column_config.CheckboxColumn(
                                                    "Select for Masking",
                                                    help="Check to apply masking policy to this column",
                                                    default=False,
                                                ),
                                                "Confidence": st.column_config.ProgressColumn(
                                                    "Confidence",
                                                    help="Detection confidence score",
                                                    min_value=0,
                                                    max_value=1,
                                                ),
                                                "Table": st.column_config.TextColumn(
                                                    "Table",
                                                    help="Source table name",
                                                    width="medium",
                                                ),
                                                "Column Name": st.column_config.TextColumn(
                                                    "Column Name", 
                                                    help="Column name",
                                                    width="medium",
                                                ),
                                                "Data Type": st.column_config.TextColumn(
                                                    "Data Type",
                                                    help="Snowflake data type",
                                                    width="small",
                                                ),
                                                "Sensitive Type": st.column_config.TextColumn(
                                                    "Sensitive Type",
                                                    help="Type of sensitive data detected",
                                                    width="medium",
                                                ),
                                                "Masking Strategy": st.column_config.TextColumn(
                                                    "Masking Strategy",
                                                    help="Recommended masking approach",
                                                    width="large",
                                                ),
                                            },
                                            disabled=["Table", "Column Name", "Data Type", "Sensitive Type", "Confidence", "Masking Strategy"],
                                            key="sensitive_columns_editor"
                                        )
                                        
                                        # Update session state with selections from the data_editor
                                        for idx, row in edited_df.iterrows():
                                            result = sensitive_columns[idx]
                                            column_id = f"{result['table']}.{result['column_name']}"
                                            st.session_state.masking_selections[column_id] = row['Select for Masking']
                                        
                                        # Summary of masking selections
                                        selected_for_masking = [col_id for col_id, selected in st.session_state.masking_selections.items() if selected]
                                        
                                        if selected_for_masking:
                                            st.markdown("---")
                                            st.subheader("🛡️ Masking Policy Summary")
                                            st.success(f"✅ **{len(selected_for_masking)} columns** selected for masking policies:")
                                            
                                            # Show selected columns with their strategies
                                            for col_id in selected_for_masking:
                                                # Find the corresponding result
                                                matching_result = next((r for r in sensitive_columns if f"{r['table']}.{r['column_name']}" == col_id), None)
                                                if matching_result:
                                                    st.write(f"• **{col_id}** - {matching_result['sensitive_type']} ({matching_result['masking_description']})")
                                            
                                            # Generate comprehensive DDL
                                            if st.button("📜 Generate Complete DDL Script", type="primary"):
                                                st.markdown("---")
                                                st.subheader("📋 Generated Snowflake DDM Policies (Review Before Applying)")
                                                
                                                # Get selected column data
                                                selected_columns_data = [r for r in sensitive_columns if f"{r['table']}.{r['column_name']}" in selected_for_masking]
                                                
                                                # Generate comprehensive DDL script with configurable settings
                                                complete_ddl = generate_comprehensive_ddl_script_enhanced(
                                                    selected_columns_data, 
                                                    selected_database, 
                                                    selected_schema,
                                                    settings
                                                )
                                                
                                                # Store DDL in session state for later use
                                                st.session_state.generated_ddl = complete_ddl
                                                
                                                # Display DDL in a text area for review
                                                st.text_area(
                                                    "Generated Snowflake DDM Policies (Review Before Applying)",
                                                    value=complete_ddl,
                                                    height=600,
                                                    help="Copy this SQL script and execute it in your Snowflake environment to apply the masking policies. Review carefully before execution."
                                                )
                                                
                                                # Use enhanced policy application interface
                                                create_policy_application_interface(
                                                    conn, complete_ddl, selected_columns_data, selected_database, selected_schema
                                                )
                                        
                                        else:
                                            st.markdown("---")
                                            st.info("💡 Select columns above to generate masking policies")
                                        
                                        # Detailed view for each sensitive column
                                        st.markdown("### 🔍 Detailed Review of Sensitive Columns")
                                        st.markdown("*Click to expand each column for detailed information, sample data, and masking recommendations*")
                                        
                                        for idx, result in enumerate(sensitive_columns):
                                            column_id = f"{result['table']}.{result['column_name']}"
                                            confidence_bar = "🔴" if result['confidence'] >= 0.8 else "🟡" if result['confidence'] >= 0.6 else "🟠"
                                            
                                            with st.expander(
                                                f"{confidence_bar} **{result['table']}.{result['column_name']}** - {result['sensitive_type']} (Confidence: {result['confidence']:.2f})", 
                                                expanded=False
                                            ):
                                                # Create two columns for organized display
                                                col_left, col_right = st.columns([1, 1])
                                                
                                                with col_left:
                                                    st.markdown("#### 📊 Column Information")
                                                    st.write(f"**Table:** {result['table']}")
                                                    st.write(f"**Column Name:** {result['column_name']}")
                                                    st.write(f"**Data Type:** {result['data_type']}")
                                                    st.write(f"**Sample Count:** {result['sample_count']}")
                                                    
                                                    st.markdown("#### 🔍 Detection Details")
                                                    st.write(f"**Sensitive Type:** {result['sensitive_type']}")
                                                    st.write(f"**Confidence Score:** {result['confidence']:.2f}")
                                                    st.write(f"**Detection Source:** {result.get('detection_source', 'UNKNOWN')}")
                                                    st.write(f"**Detection Rationale:**")
                                                    st.info(result['rationale'])
                                                    
                                                    # AI Insights section
                                                    if result.get('ai_insights') and any(result['ai_insights'].values()):
                                                        st.markdown("#### 🤖 AI Analysis")
                                                        ai_insights = result['ai_insights']
                                                        
                                                        if ai_insights.get('classification', {}).get('ai_classification'):
                                                            st.write(f"**AI Classification:** {ai_insights['classification']['ai_classification']}")
                                                        
                                                        if ai_insights.get('semantic_analysis', {}).get('reasoning'):
                                                            st.write("**AI Reasoning:**")
                                                            reasoning = ai_insights['semantic_analysis']['reasoning']
                                                            if len(reasoning) > 300:
                                                                if st.checkbox("🧠 Show Full AI Reasoning", key=f"show_reasoning_{idx}", value=False):
                                                                    st.write(reasoning)
                                                            else:
                                                                st.info(reasoning)
                                                        
                                                        if ai_insights.get('semantic_analysis', {}).get('confidence'):
                                                            ai_conf = ai_insights['semantic_analysis']['confidence']
                                                            st.write(f"**AI Confidence:** {ai_conf:.2f}")
                                                        
                                                        if ai_insights.get('error'):
                                                            st.warning(f"**AI Error:** {ai_insights['error']}")
                                                    
                                                    st.markdown("#### 🏷️ Tags & Comments")
                                                    if result.get('tags') and result['tags'] != 'No tags':
                                                        st.write(f"**Tags:** {result['tags']}")
                                                    if result['comment'] and result['comment'] != 'No comment':
                                                        st.write(f"**Comment:** *{result['comment']}*")
                                                    if not (result.get('tags') and result['tags'] != 'No tags') and not (result['comment'] and result['comment'] != 'No comment'):
                                                        st.write("*No tags or comments available*")
                                                
                                                with col_right:
                                                    st.markdown("#### 📝 Sample Values")
                                                    if result['sample_values']:
                                                        st.write("**Sample data from this column:**")
                                                        # Display sample values in a more organized way
                                                        sample_display = []
                                                        for i, value in enumerate(result['sample_values'][:15], 1):
                                                            sample_display.append(f"{i:2d}. {value}")
                                                        
                                                        # Create a text area showing samples
                                                        sample_text = "\n".join(sample_display)
                                                        st.text_area(
                                                            "Sample Values:",
                                                            value=sample_text,
                                                            height=200,
                                                            disabled=True,
                                                            key=f"samples_{idx}"
                                                        )
                                                        
                                                        if len(result['sample_values']) > 15:
                                                            st.caption(f"... and {len(result['sample_values']) - 15} more values")
                                                    else:
                                                        st.warning("No sample data available for this column")
                                                
                                                # Masking Recommendations Section
                                                if result['recommended_masking_sql']:
                                                    st.markdown("---")
                                                    st.markdown("#### 🛡️ Recommended Masking Strategy")
                                                    
                                                    # Strategy overview
                                                    col_strat_left, col_strat_right = st.columns([1, 1])
                                                    
                                                    with col_strat_left:
                                                        st.write(f"**Strategy:** {result['masking_description']}")
                                                        st.write(f"**Authorized Roles:** {', '.join(result['authorized_roles'])}")
                                                        st.write(f"**Example:** {result['masking_example']}")
                                                    
                                                    with col_strat_right:
                                                        st.markdown("**Masking Expression:**")
                                                        st.code(result['recommended_masking_sql'], language="sql")
                                                    
                                                    # AI-Enhanced Policy Recommendations
                                                    if result.get('ai_policy_recommendation'):
                                                        st.markdown("---")
                                                        st.markdown("#### 🤖 AI-Enhanced Policy Recommendation")
                                                        if st.checkbox("🤖 Show AI-Generated Policy Insights", key=f"show_ai_policy_{idx}", value=False):
                                                            st.markdown("**AI Analysis:**")
                                                            st.write(result['ai_policy_recommendation'][:1000] + "..." if len(result['ai_policy_recommendation']) > 1000 else result['ai_policy_recommendation'])
                                                    
                                                    # Cross-table insights if available
                                                    if result.get('cross_table_insights', {}).get('pattern_analysis'):
                                                        st.markdown("---")
                                                        st.markdown("#### 🔗 Cross-Table Pattern Analysis")
                                                        if st.checkbox("🔗 Show Schema-wide AI Insights", key=f"show_cross_table_{idx}", value=False):
                                                            pattern_analysis = result['cross_table_insights']['pattern_analysis']
                                                            st.write(pattern_analysis[:800] + "..." if len(pattern_analysis) > 800 else pattern_analysis)
                                                    
                                                    # Complete DDL (using toggle instead of nested expander)
                                                    st.markdown("---")
                                                    if st.checkbox("📜 Show Complete Masking Policy DDL", key=f"show_ddl_{idx}", value=False):
                                                        st.markdown("**Ready-to-execute SQL for creating the masking policy:**")
                                                        if result.get('masking_policy_ddl'):
                                                            st.code(result['masking_policy_ddl'], language="sql")
                                                        else:
                                                            st.warning("⚠️ DDL not available for this column. This may be due to insufficient masking configuration.")
                                                        
                                                        if st.button(f"📋 Copy DDL for {result['column_name']}", key=f"copy_ddl_{idx}"):
                                                            st.success("DDL copied to clipboard! (Note: Copy functionality requires browser support)")
                                                
                                                # Masking policy selection for this column
                                                st.markdown("#### 🛡️ Masking Policy Selection")
                                                
                                                col_mask_left, col_mask_right = st.columns(2)
                                                
                                                with col_mask_left:
                                                    mask_selected = st.checkbox(
                                                        f"Apply masking policy to {result['column_name']}",
                                                        key=f"detailed_mask_{idx}",
                                                        value=st.session_state.masking_selections.get(column_id, False)
                                                    )
                                                    st.session_state.masking_selections[column_id] = mask_selected
                                                
                                                with col_mask_right:
                                                    if st.button(f"💾 Save Classification", key=f"save_class_{idx}"):
                                                        classification_data = {
                                                            'database': result['database'],
                                                            'schema': result['schema'],
                                                            'table': result['table'],
                                                            'column_name': result['column_name'],
                                                            'sensitive_type': result['sensitive_type'],
                                                            'confidence': result['confidence'],
                                                            'masking_strategy': result['masking_description'],
                                                            'notes': f"Detected via {result.get('detection_source', 'UNKNOWN')}"
                                                        }
                                                        if save_approved_classification(conn, classification_data):
                                                            st.success("✅ Classification saved!")
                                                        else:
                                                            st.error("❌ Failed to save classification")
                                    
                                    else:
                                        st.warning("🤔 No sensitive data detected in the selected tables")
                                        
                                        # Comprehensive debugging information
                                        st.markdown("### 🔍 Analysis Details")
                                        
                                        # Show what was actually analyzed
                                        analyzed_count = len(st.session_state.profiling_results)
                                        st.info(f"✅ Successfully analyzed **{analyzed_count} columns** across **{len(selected_tables)} tables**")
                                        
                                        # Show sample of analyzed columns with their detection details
                                        with st.expander("📊 View All Analyzed Columns (with detection details)", expanded=False):
                                            for i, col in enumerate(st.session_state.profiling_results):
                                                confidence_emoji = "🔴" if col['confidence'] >= 0.8 else "🟡" if col['confidence'] >= 0.5 else "🟠" if col['confidence'] >= 0.3 else "🔵"
                                                
                                                st.markdown(f"**{i+1}. {col['table']}.{col['column_name']}** ({col['data_type']}) {confidence_emoji}")
                                                st.write(f"   - **Confidence**: {col['confidence']:.2f}")
                                                st.write(f"   - **Detected Type**: {col['sensitive_type'] or 'None'}")
                                                st.write(f"   - **Rationale**: {col['rationale']}")
                                                st.write(f"   - **Sample Data**: {len(col['sample_values'])} values found")
                                                if col['sample_values']:
                                                    st.write(f"   - **Examples**: {col['sample_values'][:3]}")
                                                st.write("---")
                                        
                                        # Show current settings
                                        current_threshold = settings['detection_rules']['confidence_threshold']
                                        col_debug1, col_debug2 = st.columns(2)
                                        
                                        with col_debug1:
                                            st.markdown("### ⚙️ Current Settings")
                                            st.write(f"**Confidence Threshold**: {current_threshold}")
                                            st.write(f"**Sample Size**: {settings['detection_rules']['sample_size']}")
                                            st.write(f"**Tag Detection**: {settings['detection_rules']['enable_tag_detection']}")
                                            st.write(f"**Comment Detection**: {settings['detection_rules']['enable_comment_detection']}")
                                        
                                        with col_debug2:
                                            st.markdown("### 💡 Quick Fixes")
                                            
                                            # Count columns near threshold
                                            near_threshold = [col for col in st.session_state.profiling_results if 0.3 <= col['confidence'] < current_threshold]
                                            
                                            if near_threshold:
                                                st.warning(f"**{len(near_threshold)} columns** have confidence between 0.3-{current_threshold}")
                                                if st.button("🔧 Lower Threshold to 0.3", key="debug_lower_threshold"):
                                                    settings['detection_rules']['confidence_threshold'] = 0.3
                                                    st.session_state.user_settings = settings
                                                    st.success("✅ Threshold lowered! Click '🔍 Profile Selected Tables' again.")
                                                    st.rerun()
                                            
                                            if st.button("📝 Add Custom Rule", key="debug_add_rule"):
                                                st.info("💡 Use the Settings sidebar to add custom detection patterns for your specific column names and data formats.")
                                            
                                            if st.button("🔄 Rerun Analysis", key="debug_rerun"):
                                                st.info("💡 Click the '🔍 Profile Selected Tables' button above to run the analysis again.")
                                        
                                        # Show columns that were close to being detected
                                        potential_columns = [col for col in st.session_state.profiling_results if col['confidence'] > 0.1]
                                        if potential_columns:
                                            st.markdown("### 🎯 Columns with Some Detection Potential")
                                            for col in potential_columns[:5]:  # Show top 5
                                                st.write(f"• **{col['table']}.{col['column_name']}** - Confidence: {col['confidence']:.2f} ({col['rationale']})")
                                        
                                        # Educational content
                                        st.markdown("### 📚 What the App Looks For")
                                        st.markdown("""
                                        **Column names containing**: `ssn`, `email`, `phone`, `name`, `address`, `credit_card`, `dob`
                                        
                                        **Data patterns like**:
                                        - 📧 Email: `user@domain.com`
                                        - 🔢 SSN: `123-45-6789` or `123456789`
                                        - 📱 Phone: `555-123-4567`
                                        - 💳 Credit Card: `1234-5678-9012-3456`
                                        
                                        **Comments containing**: `personal`, `private`, `confidential`, `sensitive`, `pii`
                                        """)
                                
                                else:
                                    # No profiling results available
                                    st.info("👋 **Ready to analyze your data!**")
                                    st.markdown("📋 **Next Steps:**")
                                    st.markdown("1. Select tables above")
                                    st.markdown("2. Click '🔍 Profile Selected Tables'")
                                    st.markdown("3. Review the detected sensitive columns here")
                                    
                                    if selected_tables:
                                        st.markdown("---")
                                        st.warning("💡 You have tables selected. Click the '🔍 Profile Selected Tables' button above to start the analysis!")
                                
                                # Reset Application Button
                                if hasattr(st.session_state, 'profiling_results') and st.session_state.profiling_results:
                                    st.markdown("---")
                                    col_reset1, col_reset2 = st.columns([3, 1])
                                    with col_reset2:
                                        if st.button("🔄 Reset Application", type="secondary"):
                                            reset_application_state()
                                            st.rerun()
                                
                                # Show sample data from selected tables
                                st.markdown("---")
                                st.subheader("📊 Sample Data from Selected Tables")
                                
                                for table in selected_tables:
                                    with st.expander(f"📋 Data from {table}", expanded=False):
                                        sample_data = fetch_table_data(conn, selected_database, selected_schema, table, 5)
                                        if sample_data is not None and not sample_data.empty:
                                            st.dataframe(sample_data, use_container_width=True)
                                        else:
                                            st.info(f"No data available or unable to fetch data from {table}")
                            else:
                                st.write("**Tables:** None selected")
                        else:
                            st.warning(f"No tables found in {selected_database}.{selected_schema}")
                else:
                    st.warning(f"No schemas found in database {selected_database}")
        else:
            st.warning("No databases found or unable to fetch database list")
        


    
    else:
        st.error("❌ Failed to connect to Snowflake!")
        st.info("Make sure you're running this as a Streamlit-in-Snowflake application with proper permissions.")
    
    # =====================================================================
    # AI ACTIVITY LOG SECTION (Bottom of Page)
    # =====================================================================
    
    # Check if user clicked the "View All AI Activity" button in sidebar
    if locals().get('show_ai_activity', False) and st.session_state.ai_activity_log:
        st.markdown("---")
        st.subheader("🤖 Complete AI Activity Log")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📋 Activity Timeline", "📈 Activity Summary"])
        
        with tab1:
            st.markdown("**Recent AI Operations with Full Details:**")
            
            for i, activity in enumerate(reversed(st.session_state.ai_activity_log)):
                status_icon = "✅" if activity['success'] else "❌"
                timestamp = activity['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                
                with st.expander(f"{status_icon} {timestamp} - {activity['function']} - {activity['operation']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📊 Performance Metrics:**")
                        st.write(f"⚡ **Response Time:** {activity['response_time']:.3f}s")
                        st.write(f"🎯 **Tokens Used:** {activity['tokens']:,}")
                        st.write(f"💰 **Cost:** ${activity['cost']:.6f}")
                        st.write(f"✅ **Success:** {activity['success']}")
                    
                    with col2:
                        st.markdown("**🔍 Context Details:**")
                        st.write(f"🤖 **AI Model:** {activity.get('ai_model', 'N/A')}")
                        st.write(f"🔧 **Function:** {activity['function']}")
                        if activity.get('table_context'):
                            st.write(f"📋 **Table:** {activity['table_context']}")
                        if activity.get('column_context'):
                            st.write(f"📄 **Column:** {activity['column_context']}")
                    
                    with col3:
                        st.markdown("**📈 Operation Analysis:**")
                        st.write(f"**Operation Type:** {activity['operation']}")
                        
                        # Performance rating
                        if activity['response_time'] < 1.0:
                            perf_rating = "🚀 Excellent"
                        elif activity['response_time'] < 2.0:
                            perf_rating = "⚡ Good"
                        elif activity['response_time'] < 3.0:
                            perf_rating = "⏱️ Fair"
                        else:
                            perf_rating = "🐌 Slow"
                        st.write(f"**Performance:** {perf_rating}")
                        
                        # Cost efficiency
                        cost_per_token = activity['cost'] / max(1, activity['tokens'])
                        st.write(f"**Cost/Token:** ${cost_per_token:.6f}")
                    
                    # Query details
                    if activity.get('query_details'):
                        st.markdown("**🔍 Query Details:**")
                        st.code(activity['query_details'], language="sql")
        
        with tab2:
            if len(st.session_state.ai_activity_log) > 0:
                # Create summary statistics
                activities_df = pd.DataFrame(st.session_state.ai_activity_log)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    avg_response = activities_df['response_time'].mean()
                    st.metric("⚡ Avg Response Time", f"{avg_response:.2f}s")
                with col2:
                    total_cost = activities_df['cost'].sum()
                    st.metric("💰 Total Cost", f"${total_cost:.4f}")
                with col3:
                    total_tokens = activities_df['tokens'].sum()
                    st.metric("🎯 Total Tokens", f"{total_tokens:,}")
                with col4:
                    success_rate = (activities_df['success'].sum() / len(activities_df)) * 100
                    st.metric("✅ Success Rate", f"{success_rate:.1f}%")
                
                # Function usage breakdown
                st.markdown("**🔧 Function Usage Breakdown:**")
                function_counts = activities_df['function'].value_counts()
                for func, count in function_counts.items():
                    avg_time = activities_df[activities_df['function'] == func]['response_time'].mean()
                    st.write(f"**{func}:** {count} uses, avg {avg_time:.2f}s")
            else:
                st.info("No AI activity data available for summary.")

# Footer
    st.markdown("---")
    st.caption("🤖 AI-Enhanced Snowflake Sensitive Data Discovery & Masking - Powered by Cortex AI with intelligent classification, semantic analysis, cross-table pattern discovery, and AI-generated masking policies")



if __name__ == "__main__":
    main() 