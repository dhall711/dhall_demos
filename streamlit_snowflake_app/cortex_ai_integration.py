# ========================================
# SNOWFLAKE CORTEX AI INTEGRATION
# ========================================
# This file demonstrates how to integrate Streamlit with Snowflake Cortex AI
# Replace the simulated functions in app.py with these real implementations

import streamlit as st
import pandas as pd
import snowflake.connector
from snowflake.snowpark import Session
import os
from typing import Dict, List, Any

# ========================================
# CONNECTION SETUP
# ========================================

@st.cache_resource
def create_snowpark_session():
    """Create a Snowpark session for Cortex AI operations"""
    try:
        # For Streamlit in Snowflake, use:
        # session = st.connection("snowflake").session()
        
        # For external Streamlit apps, use:
        session = Session.builder.configs({
            "account": os.getenv('SNOWFLAKE_ACCOUNT'),
            "user": os.getenv('SNOWFLAKE_USER'),
            "password": os.getenv('SNOWFLAKE_PASSWORD'),
            "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
            "database": "STREAMLIT_DEMO",
            "schema": "SAMPLE_DATA"
        }).create()
        return session
    except Exception as e:
        st.error(f"Failed to create Snowpark session: {e}")
        return None

# ========================================
# CORTEX AI SENTIMENT ANALYSIS
# ========================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_real_sentiment_analysis():
    """Get real sentiment analysis using Snowflake Cortex AI"""
    session = create_snowpark_session()
    if not session:
        return pd.DataFrame()
    
    try:
        # Use actual Cortex AI sentiment function
        df = session.sql("""
            SELECT 
                cf.*,
                SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) as sentiment_score,
                CASE 
                    WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) > 0.1 THEN 'Positive'
                    WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) < -0.1 THEN 'Negative'
                    ELSE 'Neutral'
                END as sentiment_category,
                SNOWFLAKE.CORTEX.SUMMARIZE(cf.REVIEW_TEXT) as ai_summary
            FROM CUSTOMER_FEEDBACK cf
            ORDER BY cf.FEEDBACK_DATE DESC
            LIMIT 100
        """).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error fetching sentiment analysis: {e}")
        return pd.DataFrame()
    finally:
        session.close()

@st.cache_data(ttl=3600)
def get_product_sentiment_insights(product_id: str = None):
    """Get AI-powered product sentiment insights"""
    session = create_snowpark_session()
    if not session:
        return {}
    
    try:
        where_clause = f"WHERE p.PRODUCT_ID = '{product_id}'" if product_id else ""
        
        query = f"""
        SELECT 
            p.PRODUCT_ID,
            p.PRODUCT_NAME,
            COUNT(cf.FEEDBACK_ID) as total_reviews,
            AVG(cf.RATING) as avg_rating,
            AVG(SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT)) as avg_sentiment_score,
            SNOWFLAKE.CORTEX.SUMMARIZE(
                LISTAGG(cf.REVIEW_TEXT, ' | ') WITHIN GROUP (ORDER BY cf.FEEDBACK_DATE DESC)
            ) as overall_feedback_summary,
            COUNT(CASE WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) > 0.1 THEN 1 END) as positive_reviews,
            COUNT(CASE WHEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) < -0.1 THEN 1 END) as negative_reviews
        FROM PRODUCTS p
        LEFT JOIN CUSTOMER_FEEDBACK cf ON p.PRODUCT_ID = cf.PRODUCT_ID
        {where_clause}
        GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME
        ORDER BY avg_sentiment_score DESC
        """
        
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error fetching product sentiment insights: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# ========================================
# CORTEX AI NATURAL LANGUAGE QUERIES
# ========================================

def process_natural_language_query(query: str) -> Dict[str, Any]:
    """Process natural language queries using Cortex AI"""
    session = create_snowpark_session()
    if not session:
        return {"error": "No session available"}
    
    try:
        # Use Cortex COMPLETE function to interpret the query
        interpretation_query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b',
            'Convert this business question to a SQL query for our database schema. 
            Available tables: SALES_DATA, CUSTOMERS, PRODUCTS, CUSTOMER_FEEDBACK.
            Question: {query}
            Return only the SQL query without explanation.'
        ) as sql_query
        """
        
        result = session.sql(interpretation_query).collect()
        if result:
            generated_sql = result[0]['SQL_QUERY']
            
            # Execute the generated SQL (with safety checks)
            if "DELETE" in generated_sql.upper() or "DROP" in generated_sql.upper():
                return {"error": "Unsafe query detected"}
            
            data_result = session.sql(generated_sql).to_pandas()
            
            # Generate insights about the results
            insight_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3-8b',
                'Analyze these query results and provide business insights: {data_result.to_string()[:1000]}'
            ) as insights
            """
            
            insight_result = session.sql(insight_query).collect()
            insights = insight_result[0]['INSIGHTS'] if insight_result else "No insights available"
            
            return {
                "data": data_result,
                "sql_query": generated_sql,
                "insights": insights,
                "success": True
            }
        
        return {"error": "Failed to generate SQL query"}
    
    except Exception as e:
        return {"error": f"Query processing failed: {str(e)}"}
    finally:
        session.close()

# ========================================
# CORTEX AI CUSTOMER INTELLIGENCE
# ========================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def generate_customer_ai_profiles():
    """Generate AI-powered customer profiles"""
    session = create_snowpark_session()
    if not session:
        return pd.DataFrame()
    
    try:
        df = session.sql("""
            SELECT 
                c.CUSTOMER_ID,
                CONCAT(c.FIRST_NAME, ' ', c.LAST_NAME) as customer_name,
                c.CUSTOMER_SEGMENT,
                c.LIFETIME_VALUE,
                COUNT(sd.SALE_ID) as total_purchases,
                AVG(sd.TOTAL_AMOUNT) as avg_order_value,
                SUM(sd.TOTAL_AMOUNT) as total_spent,
                AVG(CASE WHEN cf.REVIEW_TEXT IS NOT NULL 
                    THEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) 
                    ELSE NULL END) as avg_sentiment,
                SNOWFLAKE.CORTEX.COMPLETE(
                    'llama3-8b',
                    CONCAT(
                        'Create a customer profile summary: ',
                        'Segment: ', c.CUSTOMER_SEGMENT, ', ',
                        'Total Purchases: ', COUNT(sd.SALE_ID), ', ',
                        'Average Order: $', ROUND(AVG(sd.TOTAL_AMOUNT), 2), ', ',
                        'Preferred Categories: ', LISTAGG(DISTINCT sd.CATEGORY, ', ')
                    )
                ) as ai_customer_profile,
                CASE 
                    WHEN c.LIFETIME_VALUE < 500 AND COUNT(sd.SALE_ID) < 2 THEN 'High Churn Risk'
                    WHEN AVG(CASE WHEN cf.REVIEW_TEXT IS NOT NULL 
                             THEN SNOWFLAKE.CORTEX.SENTIMENT(cf.REVIEW_TEXT) 
                             ELSE NULL END) < -0.2 THEN 'Satisfaction Risk'
                    ELSE 'Healthy'
                END as risk_assessment
            FROM CUSTOMERS c
            LEFT JOIN SALES_DATA sd ON c.CUSTOMER_ID = sd.CUSTOMER_ID
            LEFT JOIN CUSTOMER_FEEDBACK cf ON c.CUSTOMER_ID = cf.CUSTOMER_ID
            WHERE c.IS_ACTIVE = TRUE
            GROUP BY c.CUSTOMER_ID, c.FIRST_NAME, c.LAST_NAME, c.CUSTOMER_SEGMENT, c.LIFETIME_VALUE
            ORDER BY total_spent DESC
            LIMIT 50
        """).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error generating customer profiles: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# ========================================
# CORTEX AI ANOMALY DETECTION
# ========================================

@st.cache_data(ttl=900)  # Cache for 15 minutes
def detect_sales_anomalies():
    """Detect sales anomalies using Cortex AI"""
    session = create_snowpark_session()
    if not session:
        return pd.DataFrame()
    
    try:
        df = session.sql("""
            WITH daily_stats AS (
                SELECT 
                    SALE_DATE,
                    SUM(TOTAL_AMOUNT) as daily_revenue,
                    COUNT(*) as daily_transactions,
                    AVG(TOTAL_AMOUNT) as avg_transaction_value
                FROM SALES_DATA
                WHERE SALE_DATE >= DATEADD(day, -90, CURRENT_DATE())
                GROUP BY SALE_DATE
            ),
            stats_with_moving_avg AS (
                SELECT *,
                    AVG(daily_revenue) OVER (ORDER BY SALE_DATE ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) as moving_avg_revenue,
                    STDDEV(daily_revenue) OVER (ORDER BY SALE_DATE ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) as moving_stddev_revenue
                FROM daily_stats
            )
            SELECT 
                SALE_DATE,
                daily_revenue,
                daily_transactions,
                avg_transaction_value,
                moving_avg_revenue,
                CASE 
                    WHEN ABS(daily_revenue - moving_avg_revenue) > 2 * moving_stddev_revenue 
                    THEN 'ANOMALY_DETECTED'
                    ELSE 'NORMAL'
                END as anomaly_flag,
                CASE 
                    WHEN ABS(daily_revenue - moving_avg_revenue) > 2 * moving_stddev_revenue 
                    THEN SNOWFLAKE.CORTEX.COMPLETE(
                        'llama3-8b',
                        CONCAT(
                            'Analyze this sales anomaly and suggest possible causes: ',
                            'Date: ', SALE_DATE, ', ',
                            'Revenue: $', ROUND(daily_revenue, 2), ', ',
                            '7-day average: $', ROUND(moving_avg_revenue, 2), ', ',
                            'Transactions: ', daily_transactions
                        )
                    )
                    ELSE NULL
                END as ai_anomaly_explanation
            FROM stats_with_moving_avg
            WHERE moving_avg_revenue IS NOT NULL
            ORDER BY SALE_DATE DESC
        """).to_pandas()
        return df
    except Exception as e:
        st.error(f"Error detecting anomalies: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# ========================================
# CORTEX AI AGENT SIMULATION
# ========================================

def simulate_ai_agent_response(user_message: str, agent_type: str) -> str:
    """Simulate AI agent response using Cortex COMPLETE"""
    session = create_snowpark_session()
    if not session:
        return "Sorry, I'm unable to connect to the AI service right now."
    
    try:
        # Create context based on agent type
        context_prompts = {
            "Sales Assistant": "You are a helpful sales assistant for a technology company. Help customers find the right products based on their needs. Be friendly and knowledgeable about our product lineup.",
            "Support Agent": "You are a technical support agent. Help customers troubleshoot issues with their purchases. Be empathetic and provide step-by-step solutions.",
            "Product Expert": "You are a product specialist with deep technical knowledge. Provide detailed product information and comparisons to help customers make informed decisions."
        }
        
        prompt = f"""
        {context_prompts.get(agent_type, "You are a helpful customer service representative.")}
        
        Customer message: {user_message}
        
        Provide a helpful and professional response:
        """
        
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3-8b',
                '{prompt}'
            ) as response
        """).collect()
        
        if result:
            return result[0]['RESPONSE']
        else:
            return "I apologize, but I'm unable to process your request at the moment."
    
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
    finally:
        session.close()

# ========================================
# CORTEX AI TEXT PROCESSING FUNCTIONS
# ========================================

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment of given text"""
    session = create_snowpark_session()
    if not session:
        return {"error": "No session available"}
    
    try:
        result = session.sql(f"""
            SELECT 
                SNOWFLAKE.CORTEX.SENTIMENT('{text}') as sentiment_score,
                CASE 
                    WHEN SNOWFLAKE.CORTEX.SENTIMENT('{text}') > 0.1 THEN 'Positive'
                    WHEN SNOWFLAKE.CORTEX.SENTIMENT('{text}') < -0.1 THEN 'Negative'
                    ELSE 'Neutral'
                END as sentiment_category
        """).collect()
        
        if result:
            return {
                "sentiment_score": result[0]['SENTIMENT_SCORE'],
                "sentiment_category": result[0]['SENTIMENT_CATEGORY'],
                "success": True
            }
        return {"error": "No result returned"}
    
    except Exception as e:
        return {"error": f"Sentiment analysis failed: {str(e)}"}
    finally:
        session.close()

def summarize_text(text: str) -> str:
    """Summarize text using Cortex AI"""
    session = create_snowpark_session()
    if not session:
        return "Summary unavailable"
    
    try:
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.SUMMARIZE('{text}') as summary
        """).collect()
        
        if result:
            return result[0]['SUMMARY']
        return "Summary unavailable"
    
    except Exception as e:
        return f"Summarization failed: {str(e)}"
    finally:
        session.close()

def translate_text(text: str, target_language: str) -> str:
    """Translate text using Cortex AI"""
    session = create_snowpark_session()
    if not session:
        return "Translation unavailable"
    
    try:
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.TRANSLATE('{text}', 'en', '{target_language}') as translation
        """).collect()
        
        if result:
            return result[0]['TRANSLATION']
        return "Translation unavailable"
    
    except Exception as e:
        return f"Translation failed: {str(e)}"
    finally:
        session.close()

def classify_text(text: str) -> Dict[str, Any]:
    """Classify text using Cortex AI"""
    session = create_snowpark_session()
    if not session:
        return {"error": "No session available"}
    
    try:
        # Use COMPLETE function for classification
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3-8b',
                'Classify this customer message into one of these categories: Customer Service, Product Inquiry, Technical Support, Billing, General. Return only the category name. Message: {text}'
            ) as classification
        """).collect()
        
        if result:
            classification = result[0]['CLASSIFICATION'].strip()
            confidence = 0.85  # Simulated confidence
            return {
                "category": classification,
                "confidence": confidence,
                "success": True
            }
        return {"error": "No result returned"}
    
    except Exception as e:
        return {"error": f"Classification failed: {str(e)}"}
    finally:
        session.close()

# ========================================
# USAGE INSTRUCTIONS
# ========================================

"""
To use these functions in your Streamlit app, replace the simulated functions with these real implementations:

1. Replace get_cortex_sentiment_data() with get_real_sentiment_analysis()
2. Replace simulate_semantic_query() with process_natural_language_query()
3. Replace the AI agent simulator with simulate_ai_agent_response()
4. Use the text processing functions for real-time AI features

Example usage in app.py:

# Instead of:
sentiment_data = get_cortex_sentiment_data()

# Use:
from cortex_ai_integration import get_real_sentiment_analysis
sentiment_data = get_real_sentiment_analysis()

Make sure to set these environment variables:
- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_USER
- SNOWFLAKE_PASSWORD
- SNOWFLAKE_WAREHOUSE

Or if running in Streamlit in Snowflake, use:
session = st.connection("snowflake").session()
"""

# ========================================
# TESTING FUNCTIONS
# ========================================

def test_cortex_functions():
    """Test all Cortex AI functions"""
    st.subheader("🧪 Cortex AI Function Tests")
    
    # Test sentiment analysis
    if st.button("Test Sentiment Analysis"):
        test_text = "This product is absolutely amazing! I love it."
        result = analyze_sentiment(test_text)
        st.write("**Test Text:**", test_text)
        st.write("**Result:**", result)
    
    # Test summarization
    if st.button("Test Text Summarization"):
        test_text = "This is a long review about a product that discusses various features, performance characteristics, and user experience details that could be summarized into key points."
        result = summarize_text(test_text)
        st.write("**Original Text:**", test_text)
        st.write("**Summary:**", result)
    
    # Test translation
    if st.button("Test Translation"):
        test_text = "Hello, how are you today?"
        result = translate_text(test_text, "es")
        st.write("**Original:**", test_text)
        st.write("**Spanish Translation:**", result)
    
    # Test classification
    if st.button("Test Text Classification"):
        test_text = "I need help with my order, it hasn't arrived yet."
        result = classify_text(test_text)
        st.write("**Test Text:**", test_text)
        st.write("**Classification:**", result)

if __name__ == "__main__":
    st.title("🧠 Cortex AI Integration Test")
    test_cortex_functions() 