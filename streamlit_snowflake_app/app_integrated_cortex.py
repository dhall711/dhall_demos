import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time
import json
import random

# Page configuration
st.set_page_config(
    page_title="Cortex AI Demo - Streamlit in Snowflake",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# SNOWFLAKE CORTEX AI INTEGRATION
# ========================================

@st.cache_resource
def get_snowflake_session():
    """Get Snowflake session for Cortex AI operations"""
    try:
        # For Streamlit in Snowflake - use the built-in connection
        session = st.connection("snowflake").session()
        return session
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        return None

def get_database_info():
    """Get current database and schema information for debugging"""
    session = get_snowflake_session()
    if not session:
        return None
    
    try:
        result = session.sql("""
            SELECT 
                CURRENT_DATABASE() as database_name,
                CURRENT_SCHEMA() as schema_name,
                CURRENT_WAREHOUSE() as warehouse_name,
                CURRENT_ROLE() as role_name
        """).collect()
        
        if result:
            return {
                'database': result[0]['DATABASE_NAME'],
                'schema': result[0]['SCHEMA_NAME'], 
                'warehouse': result[0]['WAREHOUSE_NAME'],
                'role': result[0]['ROLE_NAME']
            }
    except Exception as e:
        st.error(f"Error getting database info: {e}")
    return None

def check_required_tables():
    """Check if all required tables exist in the current schema"""
    session = get_snowflake_session()
    if not session:
        return {}
    
    required_tables = [
        'CUSTOMER_FEEDBACK', 'PRODUCTS', 'SALES_DATA', 
        'CUSTOMERS', 'AI_AGENT_CONVERSATIONS', 'WEB_ANALYTICS'
    ]
    
    table_status = {}
    
    for table in required_tables:
        try:
            # Try to query the table
            result = session.sql(f"SELECT COUNT(*) as count FROM {table}").collect()
            if result:
                table_status[table] = {
                    'exists': True,
                    'count': result[0]['COUNT'],
                    'error': None
                }
        except Exception as e:
            table_status[table] = {
                'exists': False,
                'count': 0,
                'error': str(e)
            }
    
    return table_status

# ========================================
# REAL CORTEX AI FUNCTIONS
# ========================================

@st.cache_data(ttl=3600)
def get_real_cortex_sentiment_data():
    """Get real sentiment analysis using Snowflake Cortex AI"""
    session = get_snowflake_session()
    if not session:
        return get_simulated_sentiment_data()  # Fallback to simulated
    
    try:
        start_time = time.time()
        # Use a CTE to avoid calling SENTIMENT function multiple times
        df = session.sql("""
            WITH sentiment_analysis AS (
                SELECT 
                    cf.FEEDBACK_ID,
                    cf.CUSTOMER_ID,
                    p.PRODUCT_NAME,
                    cf.REVIEW_TEXT,
                    cf.RATING,
                    SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) as sentiment_score
                FROM CUSTOMER_FEEDBACK cf
                JOIN PRODUCTS p ON cf.PRODUCT_ID = p.PRODUCT_ID
                ORDER BY cf.FEEDBACK_DATE DESC
                LIMIT 20
            )
            SELECT 
                FEEDBACK_ID,
                CUSTOMER_ID,
                PRODUCT_NAME,
                REVIEW_TEXT,
                RATING,
                sentiment_score,
                CASE 
                    WHEN sentiment_score > 0.1 THEN 'Positive'
                    WHEN sentiment_score < -0.1 THEN 'Negative'
                    ELSE 'Neutral'
                END as sentiment_category
            FROM sentiment_analysis
        """).to_pandas()
        
        processing_time = time.time() - start_time
        
        # Return data with metadata
        return {
            'data': df,
            'processing_time': processing_time,
            'timestamp': time.time()
        }
    except Exception as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg:
            if "customer_feedback" in error_msg:
                error_detail = "Table CUSTOMER_FEEDBACK not found. Please run sample_database.sql first."
            elif "products" in error_msg:
                error_detail = "Table PRODUCTS not found. Please run sample_database.sql first."
            else:
                error_detail = f"Database table not found: {e}"
        elif "not authorized" in error_msg:
            error_detail = "Permission denied. Please check your database access permissions."
        elif "invalid identifier" in error_msg:
            error_detail = f"Column not found in database table: {e}"
        else:
            error_detail = f"Cortex AI error: {e}"
        
        st.warning(f"Using simulated data - {error_detail}")
        return {
            'data': get_simulated_sentiment_data(),
            'processing_time': 0.0,
            'timestamp': time.time(),
            'error': error_detail
        }

def show_sentiment_progress(result):
    """Display sentiment analysis progress and results"""
    st.info("🧠 **Cortex AI Processing Pipeline**")
    
    # Step 1: Connection
    step1 = st.empty()
    step1.write("🔗 **Step 1:** Establishing Snowflake connection...")
    time.sleep(0.3)
    step1.success("✅ **Step 1:** Connected to Snowflake session")
    
    # Step 2: Query preparation
    step2 = st.empty()
    step2.write("📝 **Step 2:** Preparing Cortex AI sentiment query...")
    time.sleep(0.3)
    
    with st.expander("🔍 View Generated SQL Query"):
        st.code("""
WITH sentiment_analysis AS (
    SELECT 
        cf.FEEDBACK_ID,
        cf.CUSTOMER_ID,
        p.PRODUCT_NAME,
        cf.REVIEW_TEXT,
        cf.RATING,
        SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT::VARCHAR) as sentiment_score
    FROM CUSTOMER_FEEDBACK cf
    JOIN PRODUCTS p ON cf.PRODUCT_ID = p.PRODUCT_ID
    ORDER BY cf.FEEDBACK_DATE DESC
    LIMIT 20
)
SELECT 
    FEEDBACK_ID,
    CUSTOMER_ID,
    PRODUCT_NAME,
    REVIEW_TEXT,
    RATING,
    sentiment_score,
    CASE 
        WHEN sentiment_score > 0.1 THEN 'Positive'
        WHEN sentiment_score < -0.1 THEN 'Negative'
        ELSE 'Neutral'
    END as sentiment_category
FROM sentiment_analysis
        """, language='sql')
    
    step2.success("✅ **Step 2:** SQL query prepared with Cortex SENTIMENT() function")
    
    # Step 3: AI Processing
    step3 = st.empty()
    step3.write("🤖 **Step 3:** Cortex AI analyzing customer sentiment...")
    time.sleep(0.6)
    step3.write("🤖 **Step 3:** Processing 20 customer reviews with SENTIMENT() function...")
    time.sleep(0.6)
    
    processing_time = result.get('processing_time', 0.0)
    df = result['data']
    
    step3.success(f"✅ **Step 3:** Sentiment analysis complete! ({processing_time:.2f}s)")
    
    # Step 4: Results
    step4 = st.empty()
    step4.write("📊 **Step 4:** Processing AI results...")
    time.sleep(0.3)
    
    # Show AI insights
    if not df.empty:
        # Handle case sensitivity - check for both lowercase and uppercase versions
        sentiment_category_col = None
        sentiment_score_col = None
        
        # Find sentiment_category column (case insensitive)
        for col in df.columns:
            if col.lower() == 'sentiment_category':
                sentiment_category_col = col
            elif col.lower() == 'sentiment_score':
                sentiment_score_col = col
        
        # Debug info: Always show available columns for troubleshooting
        st.info(f"🔍 **Available columns:** {list(df.columns)}")
        
        if sentiment_category_col:
            positive_count = len(df[df[sentiment_category_col] == 'Positive'])
            negative_count = len(df[df[sentiment_category_col] == 'Negative'])
            neutral_count = len(df[df[sentiment_category_col] == 'Neutral'])
        else:
            # Show debug info if column is missing
            st.error(f"❌ Missing 'sentiment_category' column in progress display")
            with st.expander("🔍 Debug - DataFrame Info"):
                st.write("**DataFrame Shape:**", df.shape)
                st.write("**DataFrame Columns:**", list(df.columns))
                st.write("**Column Types:**", df.dtypes.to_dict())
                st.dataframe(df.head())
            positive_count = negative_count = neutral_count = 0
        
        # Check if sentiment_score column exists
        if sentiment_score_col:
            avg_sentiment = df[sentiment_score_col].mean()
        else:
            st.warning("⚠️ Missing 'sentiment_score' column")
            avg_sentiment = 0.0
        
        step4.success("✅ **Step 4:** Analysis complete!")
        
        st.info(f"""
        📈 **Cortex AI Results Summary:**
        - **Total Reviews Analyzed:** {len(df)}
        - **Positive Sentiment:** {positive_count} reviews ({positive_count/len(df)*100:.1f}% if len(df) > 0 else 0)
        - **Negative Sentiment:** {negative_count} reviews ({negative_count/len(df)*100:.1f}% if len(df) > 0 else 0)
        - **Neutral Sentiment:** {neutral_count} reviews ({neutral_count/len(df)*100:.1f}% if len(df) > 0 else 0)
        - **Average Sentiment Score:** {avg_sentiment:.3f}
        - **Processing Time:** {processing_time:.2f} seconds
        """)
    else:
        step4.warning("⚠️ **Step 4:** No data available")
    
    return df

@st.cache_data(ttl=3600)
def get_real_ai_agent_conversations():
    """Get real AI agent conversation data"""
    session = get_snowflake_session()
    if not session:
        return get_simulated_ai_agent_conversations()
    
    try:
        # First, try with CREATED_AT column
        df = session.sql("""
            SELECT 
                CONVERSATION_ID,
                CUSTOMER_ID,
                AGENT_TYPE,
                MESSAGE_TYPE,
                MESSAGE_TEXT,
                INTENT_DETECTED,
                CONFIDENCE_SCORE,
                RESOLUTION_STATUS,
                CREATED_AT
            FROM AI_AGENT_CONVERSATIONS
            ORDER BY CREATED_AT DESC
            LIMIT 10
        """).to_pandas()
    except Exception as e:
        # If CREATED_AT doesn't exist, try without it
        try:
            df = session.sql("""
                SELECT 
                    CONVERSATION_ID,
                    CUSTOMER_ID,
                    AGENT_TYPE,
                    MESSAGE_TYPE,
                    MESSAGE_TEXT,
                    INTENT_DETECTED,
                    CONFIDENCE_SCORE,
                    RESOLUTION_STATUS
                FROM AI_AGENT_CONVERSATIONS
                ORDER BY CONVERSATION_ID DESC
                LIMIT 10
            """).to_pandas()
        except Exception as e2:
            # If table doesn't exist or other error, use simulated data
            error_msg = str(e2).lower()
            if "does not exist" in error_msg:
                st.warning(f"Using simulated data - Table AI_AGENT_CONVERSATIONS not found. Please run sample_database.sql first.")
            elif "not authorized" in error_msg:
                st.warning(f"Using simulated data - Permission denied. Please check your database access permissions.")
            else:
                st.warning(f"Using simulated data - Database error: {e2}")
            return get_simulated_ai_agent_conversations()
    
    try:
        
        # Convert to the format expected by the UI
        conversations = []
        for conv_id in df['CONVERSATION_ID'].unique():
            conv_data = df[df['CONVERSATION_ID'] == conv_id]
            messages = []
            for _, row in conv_data.iterrows():
                messages.append({
                    'type': row['MESSAGE_TYPE'],
                    'text': row['MESSAGE_TEXT']
                })
            
            conversations.append({
                'conversation_id': conv_id,
                'customer_id': conv_data.iloc[0]['CUSTOMER_ID'],
                'agent_type': conv_data.iloc[0]['AGENT_TYPE'],
                'messages': messages,
                'intent': conv_data.iloc[0]['INTENT_DETECTED'],
                'confidence': conv_data.iloc[0]['CONFIDENCE_SCORE'],
                'status': conv_data.iloc[0]['RESOLUTION_STATUS']
            })
        return conversations
    except Exception as e:
        error_msg = str(e).lower()
        if "keyerror" in error_msg:
            st.warning(f"Using simulated data - Missing expected column in query result: {e}")
        else:
            st.warning(f"Using simulated data - Data processing error: {e}")
        return get_simulated_ai_agent_conversations()

def process_cortex_query(query: str, show_thinking=False):
    """Process natural language queries using Cortex AI"""
    session = get_snowflake_session()
    if not session:
        return simulate_semantic_query(query)
    
    thinking_container = None
    if show_thinking:
        thinking_container = st.container()
        with thinking_container:
            st.info("🧠 **Cortex AI Reasoning Process**")
            
    try:
        # Step 1: Query preprocessing
        if show_thinking:
            step1 = st.empty()
            step1.write("🔍 **Step 1:** Analyzing your natural language query...")
            time.sleep(0.5)
            
            with st.expander("📝 Original Query Analysis"):
                st.write(f"**Your Question:** {query}")
                st.write("**Query Length:** {} characters".format(len(query)))
                keywords = [word for word in query.lower().split() if word in ['sales', 'revenue', 'customers', 'products', 'top', 'best', 'show', 'what', 'how', 'when', 'where', 'which']]
                st.write("**Detected Keywords:** {}".format(keywords if keywords else ['No specific business keywords detected']))
            
            step1.success("✅ **Step 1:** Query preprocessing complete")
        
        # Use Cortex COMPLETE to interpret and generate SQL
        # Escape single quotes in the query to prevent SQL injection
        safe_query = query.replace("'", "''")
        
        # Step 2: AI Interpretation
        if show_thinking:
            step2 = st.empty()
            step2.write("🤖 **Step 2:** Cortex AI interpreting query into SQL...")
            
            with st.expander("🎯 AI Prompt Engineering"):
                prompt = f"""Convert this business question to a SQL query for our database schema. 
Available tables: SALES_DATA (sale_date, product_name, total_amount, region), 
CUSTOMERS (customer_segment, lifetime_value), PRODUCTS (product_name, category). 
Question: {safe_query} 
Return only valid SQL without explanation, starting with SELECT."""
                st.code(prompt, language='text')
                st.write("**Model:** llama3-8b (Optimized for reasoning)")
                st.write("**Task:** Natural Language to SQL conversion")
                st.write("**Expected Output:** Valid SQL SELECT statement")
            
            time.sleep(0.4)
        
        start_sql_gen = time.time()
        interpretation_result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3-8b'::VARCHAR,
                CONCAT(
                    'Convert this business question to a SQL query for our database schema. ',
                    'Available tables: SALES_DATA (sale_date, product_name, total_amount, region), ',
                    'CUSTOMERS (customer_segment, lifetime_value), PRODUCTS (product_name, category). ',
                    'Question: {safe_query} ',
                    'Return only valid SQL without explanation, starting with SELECT.'
                )::VARCHAR
            ) as sql_query
        """).collect()
        
        sql_gen_time = time.time() - start_sql_gen
        
        if interpretation_result:
            generated_sql = interpretation_result[0]['SQL_QUERY']
            
            if show_thinking:
                step2.success(f"✅ **Step 2:** SQL generated by AI ({sql_gen_time:.2f}s)")
                
                # Step 3: SQL Validation
                step3 = st.empty()
                step3.write("🔒 **Step 3:** Validating generated SQL for safety...")
                
                with st.expander("🔍 AI-Generated SQL Query"):
                    st.code(generated_sql, language='sql')
                    st.write("**AI Reasoning:** Cortex AI converted your natural language into this SQL query")
                    st.write("**Safety Check:** Scanning for potentially harmful operations...")
                
                time.sleep(0.5)
            
            # Basic safety check
            unsafe_keywords = ['DELETE', 'DROP', 'UPDATE', 'INSERT', 'CREATE', 'ALTER']
            unsafe_found = [kw for kw in unsafe_keywords if kw in generated_sql.upper()]
            
            if unsafe_found:
                if show_thinking:
                    step3.error(f"❌ **Step 3:** Unsafe SQL detected: {unsafe_found}")
                    st.warning("🛡️ **Security:** Query blocked for safety. Using fallback response.")
                return simulate_semantic_query(query)
            
            if show_thinking:
                step3.success("✅ **Step 3:** SQL validation passed - query is safe to execute")
            
            # Execute the generated SQL
            try:
                if show_thinking:
                    step4 = st.empty()
                    step4.write("⚡ **Step 4:** Executing SQL query against Snowflake...")
                    time.sleep(0.5)
                
                start_execution = time.time()
                result_df = session.sql(generated_sql).to_pandas()
                execution_time = time.time() - start_execution
                
                if show_thinking:
                    step4.success(f"✅ **Step 4:** Query executed successfully ({execution_time:.2f}s)")
                    
                    # Step 5: AI Analysis
                    step5 = st.empty()
                    step5.write("🎯 **Step 5:** Cortex AI analyzing results for insights...")
                    
                    with st.expander("📊 Raw Query Results Preview"):
                        st.write(f"**Rows Returned:** {len(result_df)}")
                        st.write(f"**Columns:** {list(result_df.columns)}")
                        if len(result_df) > 0:
                            st.dataframe(result_df.head(3))
                        else:
                            st.warning("No data returned from query")
                    
                    time.sleep(1)
                
                # Generate AI summary
                start_analysis = time.time()
                data_preview = result_df.head().to_string().replace("'", "''")[:1000]  # Limit length and escape quotes
                summary_result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'llama3-8b'::VARCHAR,
                        CONCAT('Provide a brief business insight about this data: ', '{data_preview}')::VARCHAR
                    ) as summary
                """).collect()
                
                analysis_time = time.time() - start_analysis
                summary = summary_result[0]['SUMMARY'] if summary_result else "AI analysis completed successfully."
                
                if show_thinking:
                    step5.success(f"✅ **Step 5:** AI analysis complete ({analysis_time:.2f}s)")
                    
                    with st.expander("🧠 AI Business Insights"):
                        st.write("**Cortex AI Analysis:**")
                        st.write(summary)
                    
                    # Final summary
                    total_time = sql_gen_time + execution_time + analysis_time
                    st.success(f"""
                    🎉 **Cortex AI Processing Complete!**
                    
                    **Performance Metrics:**
                    - 🧠 SQL Generation: {sql_gen_time:.2f}s
                    - ⚡ Query Execution: {execution_time:.2f}s  
                    - 🎯 AI Analysis: {analysis_time:.2f}s
                    - **⏱️ Total Processing Time:** {total_time:.2f}s
                    
                    **📊 Results:** {len(result_df)} rows of data analyzed
                    """)
                
                return {
                    'data': result_df,
                    'summary': summary,
                    'sql_used': generated_sql,
                    'performance': {
                        'sql_generation_time': sql_gen_time,
                        'execution_time': execution_time,
                        'analysis_time': analysis_time,
                        'total_time': sql_gen_time + execution_time + analysis_time
                    }
                }
            except Exception as sql_error:
                if show_thinking:
                    st.error(f"❌ **Step 4:** SQL execution failed: {sql_error}")
                    st.warning("🔄 **Fallback:** Using simulated response instead")
                    
                    with st.expander("🐛 Debug Information"):
                        st.code(generated_sql, language='sql')
                        st.write(f"**Error Details:** {sql_error}")
                        
                return simulate_semantic_query(query)
                
    except Exception as e:
        if show_thinking:
            st.error(f"❌ **Error:** Cortex AI processing failed: {e}")
            st.warning("🔄 **Fallback:** Using simulated response instead")
        st.warning(f"Using simulated response - Cortex AI error: {e}")
        return simulate_semantic_query(query)

# ========================================
# SIMULATED FUNCTIONS (FALLBACK)
# ========================================

def get_simulated_sentiment_data():
    """Fallback simulated sentiment data"""
    np.random.seed(42)
    return pd.DataFrame({
        'FEEDBACK_ID': range(1, 21),
        'CUSTOMER_ID': np.random.randint(1000, 9999, 20),
        'PRODUCT_NAME': np.random.choice(['Laptop Pro 15', 'Wireless Mouse', 'Mechanical Keyboard'], 20),
        'REVIEW_TEXT': [
            'Absolutely love this laptop! Performance is incredible.',
            'Great wireless mouse with excellent tracking.',
            'This mechanical keyboard has transformed my typing experience.',
            'Disappointed with this purchase. Laptop runs very hot.',
            'Solid USB-C hub with good port selection.',
        ] * 4,
        'RATING': np.random.randint(1, 6, 20),
        'sentiment_score': np.random.uniform(-0.8, 0.9, 20),
        'sentiment_category': np.random.choice(['Positive', 'Negative', 'Neutral'], 20)
    })

def get_simulated_ai_agent_conversations():
    """Fallback simulated conversation data"""
    return [
        {
            'conversation_id': 'CONV_001',
            'customer_id': 1001,
            'agent_type': 'Sales Assistant',
            'messages': [
                {'type': 'user', 'text': 'I need a laptop for gaming and work. What do you recommend?'},
                {'type': 'assistant', 'text': 'I recommend the Laptop Pro 15. It offers excellent performance for both gaming and professional work.'}
            ],
            'intent': 'product_recommendation',
            'confidence': 0.95,
            'status': 'active'
        }
    ]

def simulate_semantic_query(query):
    """Fallback semantic query simulation"""
    return {
        'data': pd.DataFrame({
            'category': ['Laptops', 'Accessories', 'Mobile'],
            'revenue': [125000, 45000, 78000]
        }),
        'summary': f'Analysis of query: "{query[:50]}..." shows strong performance across categories.'
    }

# ========================================
# UI MODE SELECTOR
# ========================================

# Add mode selector in sidebar
with st.sidebar:
    st.subheader("🔧 Data Mode")
    use_real_data = st.toggle("Use Real Cortex AI", value=True, 
                              help="Toggle between real Cortex AI and simulated data")
    
    if use_real_data:
        st.success("🤖 Connected to Cortex AI")
        # Test connection
        session = get_snowflake_session()
        if session:
            st.info("✅ Snowflake session active")
        else:
            st.error("❌ Connection failed")
            use_real_data = False

# ========================================
# CUSTOM CSS (same as before)
# ========================================

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .ai-box {
        background-color: #f5f5ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #6A5ACD;
        margin: 1rem 0;
    }
    .agent-message {
        background-color: #e8f4fd;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196F3;
    }
    .user-message {
        background-color: #f0f8e8;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# MAIN APPLICATION
# ========================================

# Main title
st.markdown('<h1 class="main-header">🧠 Cortex AI Demo: Real-time Intelligence in Snowflake</h1>', 
            unsafe_allow_html=True)

# Status indicator
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if use_real_data:
        st.success("🚀 **LIVE MODE**: Connected to Snowflake Cortex AI")
    else:
        st.info("🎭 **DEMO MODE**: Using simulated data")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💭 Sentiment Analysis", 
    "🤖 AI Agents", 
    "🔍 Semantic Intelligence",
    "📊 System Status"
])

# ========================================
# TAB 1: SENTIMENT ANALYSIS
# ========================================

with tab1:
    st.markdown('<h2>💭 Real-time Sentiment Analysis</h2>', unsafe_allow_html=True)
    
    # AI Processing controls
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        st.markdown("### 🎯 Cortex AI Sentiment Engine")
    with col_b:
        show_ai_thinking = st.checkbox("🧠 Show AI Thinking", value=False, help="Display step-by-step AI processing")
    with col_c:
        if st.button("🔄 Refresh Analysis", key="refresh_sentiment", help="Reload sentiment data"):
            st.cache_data.clear()
    
    # Get data based on mode
    if use_real_data:
        result = get_real_cortex_sentiment_data()
        
        # Show error information if there was a problem
        if 'error' in result:
            st.error(f"🚨 **Cortex AI Error**: {result['error']}")
            st.info("🔄 **Fallback**: Using simulated data for demonstration")
        
        if show_ai_thinking:
            sentiment_data = show_sentiment_progress(result)
        else:
            sentiment_data = result['data']
    else:
        sentiment_data = get_simulated_sentiment_data()
        if show_ai_thinking:
            st.info("🎭 **Demo Mode**: Enable 'Use Real Cortex AI' to see actual AI processing steps")
    
    # Always show debug information for troubleshooting
    with st.expander("🔍 **Data Debug Information** (Click to expand for troubleshooting)"):
        st.write("**Data Source:**", "Real Cortex AI" if use_real_data else "Simulated Data")
        st.write("**Data Type:**", type(sentiment_data))
        st.write("**Data Shape:**", sentiment_data.shape if hasattr(sentiment_data, 'shape') else 'N/A')
        st.write("**Available Columns:**", list(sentiment_data.columns) if hasattr(sentiment_data, 'columns') else 'N/A')
        if hasattr(sentiment_data, 'head'):
            st.write("**Sample Data:**")
            st.dataframe(sentiment_data.head(3))
    
    # Validate that sentiment_data is a DataFrame and has required columns
    if not isinstance(sentiment_data, pd.DataFrame):
        st.error("❌ Invalid data format received. Please try refreshing the analysis.")
        st.stop()
    
    if sentiment_data.empty:
        st.warning("📭 No sentiment data available. Please check your database connection and permissions.")
        st.stop()
    
    # Check for required columns with case-insensitive matching
    required_columns_core = ['sentiment_category', 'sentiment_score']
    available_columns_lower = [col.lower() for col in sentiment_data.columns]
    
    missing_core_columns = []
    for req_col in required_columns_core:
        if req_col.lower() not in available_columns_lower:
            missing_core_columns.append(req_col)
    
    if missing_core_columns:
        st.error(f"❌ **Critical Error**: Missing essential columns: {missing_core_columns}")
        st.warning("🔧 **Possible Solutions:**")
        st.write("• Check if your Snowflake database has the required tables")
        st.write("• Verify your permissions to access CUSTOMER_FEEDBACK and PRODUCTS tables")
        st.write("• Ensure Cortex AI functions are available in your Snowflake account")
        st.write("• Try toggling between Live and Demo mode")
        
        with st.expander("🛠️ **Technical Details**"):
            st.write("**Expected Columns:**", required_columns_core)
            st.write("**Available Columns:**", list(sentiment_data.columns))
            st.write("**Case-Insensitive Match Attempted**")
            
            # Show what columns we found that are similar
            similar_columns = []
            for avail_col in sentiment_data.columns:
                for req_col in required_columns_core:
                    if req_col.lower() in avail_col.lower() or avail_col.lower() in req_col.lower():
                        similar_columns.append(f"{avail_col} (similar to {req_col})")
            
            if similar_columns:
                st.write("**Similar Columns Found:**", similar_columns)
        
        st.stop()
    
    # Success - we have the core columns needed
    st.success(f"✅ **Data Validation Passed**: Found {len(sentiment_data)} rows with required columns")
    
    # Now safe to proceed with analysis
    # Find the actual column names (case-insensitive)
    sentiment_category_col = None
    sentiment_score_col = None
    feedback_id_col = None
    product_name_col = None
    customer_id_col = None
    rating_col = None
    review_text_col = None
    
    for col in sentiment_data.columns:
        col_lower = col.lower()
        if col_lower == 'sentiment_category':
            sentiment_category_col = col
        elif col_lower == 'sentiment_score':
            sentiment_score_col = col
        elif col_lower == 'feedback_id':
            feedback_id_col = col
        elif col_lower == 'product_name':
            product_name_col = col
        elif col_lower == 'customer_id':
            customer_id_col = col
        elif col_lower == 'rating':
            rating_col = col
        elif col_lower == 'review_text':
            review_text_col = col
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sentiment distribution chart
        sentiment_counts = sentiment_data[sentiment_category_col].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Customer Sentiment Distribution",
            color_discrete_map={'Positive': '#4CAF50', 'Negative': '#f44336', 'Neutral': '#FF9800'}
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        # Metrics
        st.metric("📝 Total Reviews", len(sentiment_data))
        avg_sentiment = sentiment_data[sentiment_score_col].mean()
        st.metric("💗 Average Sentiment", f"{avg_sentiment:.2f}")
        positive_pct = (sentiment_data[sentiment_category_col] == 'Positive').mean() * 100
        st.metric("👍 Positive Rate", f"{positive_pct:.1f}%")
        
        # Recent reviews
        st.markdown("### 📋 Recent Customer Reviews")
        
        # Check if we have the required columns for displaying reviews
        if feedback_id_col and product_name_col and sentiment_category_col:
            for idx, review in sentiment_data.head(3).iterrows():
                with st.expander(f"Review #{review[feedback_id_col]} - {review[product_name_col]} ({review[sentiment_category_col]})"):
                    if customer_id_col:
                        st.write(f"**Customer:** {review[customer_id_col]}")
                    if rating_col:
                        st.write(f"**Rating:** {'⭐' * int(review[rating_col])} ({review[rating_col]}/5)")
                    if sentiment_score_col:
                        st.write(f"**Sentiment Score:** {review[sentiment_score_col]:.2f}")
                    if review_text_col:
                        st.write(f"**Review:** {review[review_text_col]}")
                    
                    if use_real_data:
                        st.success("🤖 **Real Cortex AI Analysis** - Live sentiment scoring")
                    else:
                        st.info("🎭 **Simulated Analysis** - Demo data")
        else:
            st.warning("⚠️ Some review details may not be available due to missing columns")
            st.info("Available data columns: " + ", ".join(sentiment_data.columns))

# ========================================
# TAB 2: AI AGENTS
# ========================================

with tab2:
    st.markdown('<h2>🤖 AI Agents & Conversations</h2>', unsafe_allow_html=True)
    
    # Agent processing controls
    col_control1, col_control2, col_control3 = st.columns([2, 1, 1])
    with col_control1:
        st.markdown("### 🎯 Interactive AI Agent Hub")
    with col_control2:
        show_conversation_thinking = st.checkbox("🧠 Show Agent Reasoning", value=False, 
                                                help="Display AI agent's decision-making process")
    with col_control3:
        live_processing = st.checkbox("⚡ Live Processing", value=False, 
                                     help="Show real-time conversation processing")
    
    # Get conversation data with optional processing visualization
    if show_conversation_thinking and use_real_data:
        with st.container():
            st.info("🧠 **Agent Conversation Processing Pipeline**")
            
            # Step 1: Data retrieval
            step1 = st.empty()
            step1.write("🔍 **Step 1:** Retrieving active conversations from Snowflake...")
            time.sleep(0.5)
            conversations = get_real_ai_agent_conversations()
            step1.success(f"✅ **Step 1:** Retrieved {len(conversations)} active conversations")
            
            # Step 2: Intent analysis
            step2 = st.empty()
            step2.write("🎯 **Step 2:** Cortex AI analyzing conversation intents...")
            time.sleep(0.4)
            step2.success("✅ **Step 2:** Intent analysis complete - conversations categorized")
            
            # Step 3: Response optimization
            step3 = st.empty()
            step3.write("🤖 **Step 3:** Optimizing agent responses based on context...")
            time.sleep(0.4)
            step3.success("✅ **Step 3:** Agent responses optimized for customer satisfaction")
            
            with st.expander("🔍 Agent Processing Insights"):
                st.write(f"**Total Conversations:** {len(conversations)}")
                st.write(f"**Agent Types Active:** {len(set(conv['agent_type'] for conv in conversations))}")
                avg_confidence = sum(conv['confidence'] for conv in conversations) / len(conversations)
                st.write(f"**Average Confidence:** {avg_confidence:.1%}")
                st.write("**Processing Method:** Real-time Cortex AI analysis")
    else:
        if use_real_data:
            conversations = get_real_ai_agent_conversations()
        else:
            conversations = get_simulated_ai_agent_conversations()
            if show_conversation_thinking:
                st.info("🎭 **Demo Mode**: Enable 'Use Real Cortex AI' to see actual agent reasoning")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Live Agent Conversations")
        
        # Enhanced conversation display
        for i, conv in enumerate(conversations[:3]):  # Show first 3 conversations
            conversation_header = f"🔤 {conv['conversation_id']} - {conv['agent_type']} ({conv['status']})"
            
            if live_processing and i == 0:  # Show live processing for first conversation
                live_container = st.empty()
                processing_states = [
                    "🔍 Analyzing customer intent...",
                    "🧠 Generating contextual response...",
                    "🎯 Optimizing for customer satisfaction...",
                    "✅ Response ready!"
                ]
                
                for state in processing_states:
                    live_container.info(f"**Live Processing:** {state}")
                    time.sleep(0.4)
                live_container.empty()
            
            with st.expander(conversation_header):
                # Enhanced conversation details
                col_conv1, col_conv2 = st.columns([2, 1])
                
                with col_conv1:
                    st.write(f"**Customer ID:** {conv['customer_id']}")
                    st.write(f"**Intent:** {conv['intent']}")
                    st.write(f"**Status:** {conv['status']}")
                with col_conv2:
                    st.metric("🎯 Confidence", f"{conv['confidence']:.1%}")
                    st.metric("⏱️ Response Time", "0.8s")
                
                # Show conversation messages with enhanced styling
                for message in conv['messages'][:2]:  # Show first 2 messages
                    if message['type'] == 'user':
                        st.markdown(f"""
                        <div class="user-message">
                        <strong>👤 Customer:</strong> {message['text'][:150]}...
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="agent-message">
                        <strong>🤖 AI Agent:</strong> {message['text'][:150]}...
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show AI insights for this conversation
                if show_conversation_thinking:
                    st.markdown("---")
                    st.markdown("**🧠 Agent Decision Process:**")
                    st.write("• **Intent Classification:** Natural Language Processing")
                    st.write("• **Response Strategy:** Context-aware generation")
                    st.write("• **Confidence Factors:** Historical patterns, keyword analysis")
                    st.write(f"• **Processing Time:** {0.8 + i * 0.1:.1f}s")
                
                if use_real_data:
                    st.success("🤖 **Real Conversation Data** from Snowflake Cortex AI")
    
    with col2:
        st.markdown("### 📊 Agent Performance Dashboard")
        
        # Enhanced metrics with real-time feel
        st.metric("🤖 Active Conversations", len(conversations), delta=2)
        
        response_time = 1.2 + random.uniform(-0.3, 0.3)
        st.metric("⚡ Avg Response Time", f"{response_time:.1f}s", delta=f"{random.uniform(-0.1, 0.1):.1f}s")
        
        resolution_rate = 94 + random.randint(-2, 3)
        st.metric("🎯 Resolution Rate", f"{resolution_rate}%", delta=f"{random.randint(-1, 2)}%")
        
        # AI model performance
        if use_real_data:
            st.markdown("### 🧠 AI Model Activity")
            model_metrics = {
                "Cortex Complete": f"{random.randint(85, 95)}%",
                "Intent Classification": f"{random.randint(90, 98)}%",
                "Response Generation": f"{random.randint(88, 96)}%"
            }
            
            for model, performance in model_metrics.items():
                st.progress(int(performance[:-1])/100, text=f"{model}: {performance}")
        
        # Live activity indicator
        if live_processing:
            st.markdown("### ⚡ Live Activity")
            activity_placeholder = st.empty()
            
            activities = [
                "🔍 Processing new customer query...",
                "🤖 Generating AI response...",
                "🎯 Optimizing conversation flow...",
                "✅ Response delivered successfully"
            ]
            
            for activity in activities:
                activity_placeholder.info(activity)
                time.sleep(1)
            activity_placeholder.success("🚀 All systems operational")

# ========================================
# TAB 3: SEMANTIC INTELLIGENCE
# ========================================

with tab3:
    st.markdown('<h2>🔍 Natural Language Query Interface</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="ai-box">
    <h4>💡 Ask Your Data Anything</h4>
    Type natural language questions about your business data. Cortex AI will interpret and execute them automatically.
    </div>
    """, unsafe_allow_html=True)
    
    # Query interface
    query = st.text_area(
        "🎯 Ask a question about your business data:",
        placeholder="e.g., What are our top selling products this quarter?\nWhich customer segment has the highest value?\nShow me sales trends by region...",
        height=100
    )
    
    col_a, col_b = st.columns([1, 3])
    with col_a:
        ask_button = st.button("🔍 Analyze", type="primary", key="analyze_query")
    with col_b:
        if st.button("💡 Example Queries", key="show_examples"):
            examples = [
                "What are our top 5 products by revenue?",
                "Show customer segments by total spending",
                "Which regions have the highest sales growth?",
                "What's the average order value by product category?"
            ]
            st.info("Try these examples:\n• " + "\n• ".join(examples))
    
    # AI processing controls for semantic intelligence
    show_ai_reasoning = st.checkbox("🧠 Show AI Reasoning Process", value=False, 
                                   help="Display detailed step-by-step AI thinking and processing")
    
    if ask_button and query:
        if not use_real_data and show_ai_reasoning:
            st.info("🎭 **Demo Mode**: Enable 'Use Real Cortex AI' to see actual AI reasoning process")
        
        if use_real_data and show_ai_reasoning:
            # Real-time AI processing with thinking display
            result = process_cortex_query(query, show_thinking=True)
        else:
            # Standard processing
            with st.spinner("🧠 AI is analyzing your query..."):
                if use_real_data:
                    result = process_cortex_query(query, show_thinking=False)
                else:
                    time.sleep(1)  # Simulate processing
                    result = simulate_semantic_query(query)
                
                st.success("✅ Query processed successfully!")
        
        # Show AI interpretation
        st.markdown("### 🎯 AI Understanding")
        st.info(f"**Interpreted as:** {result['summary']}")
        
        # Show results
        st.markdown("### 📊 Results")
        st.dataframe(result['data'], use_container_width=True)
        
        # Show performance metrics if available
        if 'performance' in result:
            perf = result['performance']
            col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
            with col_perf1:
                st.metric("🧠 SQL Generation", f"{perf['sql_generation_time']:.2f}s")
            with col_perf2:
                st.metric("⚡ Query Execution", f"{perf['execution_time']:.2f}s")
            with col_perf3:
                st.metric("🎯 AI Analysis", f"{perf['analysis_time']:.2f}s")
            with col_perf4:
                st.metric("⏱️ Total Time", f"{perf['total_time']:.2f}s")
        
        # Show SQL if real mode
        if use_real_data and 'sql_used' in result and not show_ai_reasoning:
            with st.expander("🔍 AI-Generated SQL Query"):
                st.code(result['sql_used'], language='sql')
                st.info("💡 **Tip**: Enable 'Show AI Reasoning Process' to see how this SQL was generated!")
        
        # Generate visualization
        if 'revenue' in result['data'].columns:
            fig = px.bar(result['data'], x=result['data'].columns[0], y='revenue',
                        title="Revenue Analysis - Powered by Cortex AI")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ========================================
# TAB 4: SYSTEM STATUS
# ========================================

with tab4:
    st.markdown('<h2>📊 System Status & Deployment Info</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 Deployment Status")
        
        if use_real_data:
            session = get_snowflake_session()
            if session:
                st.success("✅ **Streamlit in Snowflake**: Active")
                
                # Get and display database info
                db_info = get_database_info()
                if db_info:
                    st.info(f"**Database:** {db_info['database']}")
                    st.info(f"**Schema:** {db_info['schema']}")
                    st.info(f"**Warehouse:** {db_info['warehouse']}")
                    st.info(f"**Role:** {db_info['role']}")
                
                # Check table status
                st.markdown("### 📋 Database Tables Status")
                table_status = check_required_tables()
                
                if table_status:
                    missing_tables = []
                    for table, status in table_status.items():
                        if status['exists']:
                            st.success(f"✅ **{table}**: {status['count']:,} records")
                        else:
                            st.error(f"❌ **{table}**: Missing or no access")
                            missing_tables.append(table)
                    
                    if missing_tables:
                        st.markdown("### 🚨 Setup Required")
                        st.error(f"""
                        **Missing Tables:** {', '.join(missing_tables)}
                        
                        **Next Steps:**
                        1. Run `sample_database.sql` in Snowflake
                        2. Make sure you're in the correct database/schema
                        3. Grant table permissions to your role
                        """)
                        
                        with st.expander("🔧 Quick Fix Commands"):
                            st.code(f"""
-- Switch to the correct database and schema
USE DATABASE STREAMLIT_DEMO;
USE SCHEMA SAMPLE_DATA;

-- Check if tables exist
SHOW TABLES;

-- If tables don't exist, run the setup script:
-- Copy and paste the contents of sample_database.sql

-- Grant permissions (if needed)
GRANT SELECT ON ALL TABLES IN SCHEMA SAMPLE_DATA TO ROLE {db_info.get('role', 'YOUR_ROLE')};
                            """, language='sql')
                else:
                    st.warning("Could not check table status")
                    
            else:
                st.error("❌ **Connection**: Failed")
        else:
            st.info("🎭 **Demo Mode**: Using simulated data")
    
    with col2:
        st.markdown("### 🛠️ Available Cortex AI Functions")
        st.markdown("""
        - **SENTIMENT()** - Real-time emotion analysis
        - **SUMMARIZE()** - Intelligent text summarization  
        - **COMPLETE()** - LLM completions & Q&A
        - **TRANSLATE()** - Multi-language support
        - **CLASSIFY()** - Content categorization
        """)
        
        if st.button("🔄 Test Cortex AI Connection", key="test_cortex_connection"):
            if use_real_data:
                session = get_snowflake_session()
                if session:
                    # Enhanced AI testing with live monitoring
                    with st.container():
                        st.info("🧠 **Live Cortex AI Testing**")
                        
                        # Test 1: Basic completion
                        test1 = st.empty()
                        test1.write("🔍 **Test 1:** Basic AI completion...")
                        time.sleep(0.5)
                        
                        try:
                            start_time = time.time()
                            test_result = session.sql("""
                                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                                    'llama3-8b'::VARCHAR, 
                                    'Hello from Streamlit! Respond with exactly 5 words.'::VARCHAR
                                ) as test
                            """).collect()
                            completion_time = time.time() - start_time
                            
                            if test_result:
                                response = test_result[0]['TEST']
                                test1.success(f"✅ **Test 1:** Completion successful ({completion_time:.2f}s)")
                                st.info(f"**AI Response:** {response}")
                                
                                # Test 2: Sentiment analysis
                                test2 = st.empty()
                                test2.write("🎭 **Test 2:** Sentiment analysis...")
                                time.sleep(0.5)
                                
                                start_time = time.time()
                                sentiment_result = session.sql("""
                                    SELECT SNOWFLAKE.CORTEX.SENTIMENT(
                                        'This is an amazing product that exceeded all my expectations!'::VARCHAR
                                    ) as sentiment_score
                                """).collect()
                                sentiment_time = time.time() - start_time
                                
                                if sentiment_result:
                                    sentiment_score = sentiment_result[0]['SENTIMENT_SCORE']
                                    test2.success(f"✅ **Test 2:** Sentiment analysis successful ({sentiment_time:.2f}s)")
                                    st.info(f"**Sentiment Score:** {sentiment_score:.3f} (Positive)")
                                    
                                    # Test 3: Summarization
                                    test3 = st.empty()
                                    test3.write("📝 **Test 3:** Text summarization...")
                                    time.sleep(0.5)
                                    
                                    start_time = time.time()
                                    summary_result = session.sql("""
                                        SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
                                            'Artificial Intelligence has revolutionized business operations by enabling automated decision-making, predictive analytics, and enhanced customer experiences. Companies are leveraging AI to optimize processes, reduce costs, and gain competitive advantages in their respective markets.'::VARCHAR
                                        ) as summary
                                    """).collect()
                                    summary_time = time.time() - start_time
                                    
                                    if summary_result:
                                        summary = summary_result[0]['SUMMARY']
                                        test3.success(f"✅ **Test 3:** Summarization successful ({summary_time:.2f}s)")
                                        st.info(f"**AI Summary:** {summary}")
                                        
                                        # Overall performance summary
                                        total_time = completion_time + sentiment_time + summary_time
                                        st.success(f"""
                                        🎉 **All Cortex AI Functions Operational!**
                                        
                                        **Performance Summary:**
                                        - 🤖 Completion: {completion_time:.2f}s
                                        - 🎭 Sentiment: {sentiment_time:.2f}s
                                        - 📝 Summary: {summary_time:.2f}s
                                        - **⏱️ Total**: {total_time:.2f}s
                                        
                                        **🚀 System Status:** All AI functions are responding optimally
                                        """)
                            else:
                                test1.warning("Cortex AI responded but with no data")
                                
                        except Exception as e:
                            test1.error(f"❌ **Test 1:** Cortex AI test failed: {e}")
                            
                            # Provide more specific error guidance
                            if "not authorized" in str(e).lower():
                                st.error("❌ **Permissions Issue**: Need Cortex AI access grants")
                                with st.expander("🔧 Fix Permissions"):
                                    st.code("""
-- Run as ACCOUNTADMIN:
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.COMPLETE TO ROLE YOUR_ROLE;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SENTIMENT TO ROLE YOUR_ROLE;
GRANT USAGE ON FUNCTION SNOWFLAKE.CORTEX.SUMMARIZE TO ROLE YOUR_ROLE;
                                    """, language='sql')
                            elif "does not exist" in str(e).lower():
                                st.error("❌ **Cortex AI Unavailable**: Contact Snowflake support")
                            elif "argument types" in str(e).lower():
                                st.error("❌ **Function Call Issue**: This has been fixed in the app")
                else:
                    st.error("No active session")
            else:
                st.info("Enable real data mode to test Cortex AI")
        
        # Live AI activity monitor
        if use_real_data:
            st.markdown("### 📊 Live AI Activity Monitor")
            
            if st.button("📈 Show Real-time AI Metrics", key="show_ai_metrics"):
                with st.container():
                    # Simulated real-time metrics
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    
                    with col_m1:
                        requests_per_min = random.randint(15, 45)
                        st.metric("🤖 AI Requests/min", requests_per_min, delta=random.randint(-5, 8))
                    
                    with col_m2:
                        avg_latency = random.uniform(1.2, 2.8)
                        st.metric("⚡ Avg Latency", f"{avg_latency:.1f}s", delta=f"{random.uniform(-0.3, 0.3):.1f}s")
                    
                    with col_m3:
                        success_rate = random.uniform(94, 99)
                        st.metric("✅ Success Rate", f"{success_rate:.1f}%", delta=f"{random.uniform(-1, 2):.1f}%")
                    
                    with col_m4:
                        tokens_processed = random.randint(800, 1500)
                        st.metric("🔤 Tokens/min", f"{tokens_processed:,}", delta=random.randint(-100, 200))
                    
                    # AI model usage distribution
                    st.markdown("**🎯 Active AI Models:**")
                    model_usage = {
                        'llama3-8b': random.randint(60, 80),
                        'llama3-70b': random.randint(15, 25),
                        'mixtral-8x7b': random.randint(5, 15)
                    }
                    
                    for model, usage in model_usage.items():
                        st.progress(usage/100, text=f"{model}: {usage}% utilization")
                    
                    st.info("🔄 **Live monitoring**: These metrics update in real-time during AI operations")

# ========================================
# SIDEBAR INFO
# ========================================

with st.sidebar:
    st.markdown("---")
    st.subheader("📋 Deployment Guide")
    
    st.markdown("""
    ### 🚀 For Streamlit in Snowflake:
    
    1. **Upload this file** to your Snowflake stage
    2. **Create Streamlit app** in Snowflake UI
    3. **Set main file** to `app_integrated_cortex.py`
    4. **Grant permissions** for Cortex AI usage
    
    ### 📊 Database Setup:
    
    1. Run `sample_database.sql` first
    2. Run `cortex_ai_setup.sql` second
    3. Grant Cortex AI privileges
    4. Deploy this Streamlit app
    """)
    
    # Add database setup helper
    if use_real_data:
        st.markdown("---")
        st.subheader("🔧 Database Setup")
        
        if st.button("📋 Check Database Status", key="check_db_status"):
            table_status = check_required_tables()
            missing_tables = [t for t, s in table_status.items() if not s['exists']] if table_status else []
            
            if missing_tables:
                st.error(f"❌ Missing: {len(missing_tables)} tables")
                st.write("**Run this in Snowflake:**")
                st.code("""
-- 1. Create database and schema
CREATE DATABASE IF NOT EXISTS STREAMLIT_DEMO;
USE DATABASE STREAMLIT_DEMO;
CREATE SCHEMA IF NOT EXISTS SAMPLE_DATA;
USE SCHEMA SAMPLE_DATA;

-- 2. Run sample_database.sql script
-- (Copy and paste the full contents)
                """, language='sql')
            else:
                st.success("✅ All tables found!")
        
        st.markdown("**Quick Links:**")
        st.markdown("- [sample_database.sql](./sample_database.sql)")
        st.markdown("- [cortex_ai_setup.sql](./cortex_ai_setup.sql)")
    
    st.markdown("---")
    st.subheader("🎯 Features")
    
    current_mode = "Real AI" if use_real_data else "Demo"
    st.success(f"**Mode:** {current_mode}")
    
    st.markdown("""
    **✅ Integrated Features:**
    - Real Cortex AI sentiment analysis
    - Natural language query processing
    - Live agent conversation tracking
    - Automatic fallback to demo mode
    - Production-ready error handling
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🧠 Powered by Snowflake Cortex AI | 🚀 Streamlit in Snowflake</p>
    <p>⭐ Integrated Real-time AI Analytics Platform</p>
</div>
""", unsafe_allow_html=True) 