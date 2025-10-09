-- =====================================================
-- UDX NLP2SQL Hackathon: Environment Setup
-- =====================================================
-- This script creates the foundational Snowflake environment
-- for the Natural Language to SQL Assistant hackathon

-- Set context (adjust role as needed)
USE ROLE ACCOUNTADMIN; -- or SYSADMIN

-- =====================================================
-- 1. CREATE DATABASE AND SCHEMAS
-- =====================================================

-- Create main database for the NLP2SQL hackathon
CREATE DATABASE IF NOT EXISTS UDX_NL2SQL 
    COMMENT = 'Comcast UDX Hackathon - Natural Language to SQL Assistant';

-- Create schema for business analytics data
CREATE SCHEMA IF NOT EXISTS UDX_NL2SQL.BUSINESS_ANALYTICS
    COMMENT = 'Schema for business analytics and reporting data';

-- Create schema for AI metadata and context
CREATE SCHEMA IF NOT EXISTS UDX_NL2SQL.METADATA
    COMMENT = 'Schema for AI context, business glossary, and query patterns';

-- Create schema for NL2SQL system components
CREATE SCHEMA IF NOT EXISTS UDX_NL2SQL.NL2SQL_SYSTEM
    COMMENT = 'Schema for natural language processing and query generation';

-- Set working context
USE DATABASE UDX_NL2SQL;
USE SCHEMA NL2SQL_SYSTEM;

-- =====================================================
-- 2. CREATE VIRTUAL WAREHOUSE
-- =====================================================

-- Create warehouse optimized for analytics and AI workloads
CREATE WAREHOUSE IF NOT EXISTS UDX_ANALYTICS_WAREHOUSE
    WITH 
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300  -- 5 minutes
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for business analytics and NL2SQL operations';

-- Use the warehouse
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;

-- =====================================================
-- 3. BUSINESS GLOSSARY AND TERMINOLOGY
-- =====================================================

-- Table to store business terminology and definitions
CREATE OR REPLACE TABLE METADATA.BUSINESS_GLOSSARY (
    term STRING,
    definition STRING,
    category STRING, -- 'metric', 'dimension', 'process', 'kpi'
    synonyms ARRAY,
    table_references ARRAY,
    calculation_logic STRING,
    business_owner STRING,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert core business terminology
INSERT INTO METADATA.BUSINESS_GLOSSARY VALUES
    ('Guest', 'A customer visiting UDX theme parks', 'dimension', ['Customer', 'Visitor', 'Patron'], ['CUSTOMERS'], NULL, 'Guest Experience Team', CURRENT_TIMESTAMP()),
    ('Attraction', 'Rides and entertainment experiences in the parks', 'dimension', ['Ride', 'Experience', 'Entertainment'], ['ATTRACTION_ANALYTICS'], NULL, 'Operations Team', CURRENT_TIMESTAMP()),
    ('Revenue Per Guest', 'Total revenue divided by unique visitors', 'kpi', ['RPG', 'ADR', 'Average Daily Revenue'], ['SALES_TRANSACTIONS', 'CUSTOMERS'], 'SUM(revenue) / COUNT(DISTINCT customer_id)', 'Finance Team', CURRENT_TIMESTAMP()),
    ('Guest Satisfaction', 'Average satisfaction rating across all touchpoints', 'kpi', ['NPS', 'CSAT', 'Satisfaction Score'], ['PARK_PERFORMANCE', 'ATTRACTION_ANALYTICS'], 'AVG(satisfaction_score)', 'Guest Experience Team', CURRENT_TIMESTAMP()),
    ('Throughput', 'Number of guests served per hour by attraction', 'metric', ['Capacity', 'Volume', 'Guests per Hour'], ['ATTRACTION_ANALYTICS'], 'SUM(guests_served) / COUNT(DISTINCT hour)', 'Operations Team', CURRENT_TIMESTAMP()),
    ('Market Penetration', 'Ticket sales by demographic segments', 'metric', ['Segment Performance', 'Demographics'], ['CUSTOMERS', 'SALES_TRANSACTIONS'], 'COUNT(*) / total_segment_population', 'Marketing Team', CURRENT_TIMESTAMP()),
    ('Seasonal Index', 'Performance relative to annual average', 'metric', ['Seasonality', 'Trends'], ['FINANCIAL_SUMMARY'], 'current_period_value / annual_average', 'Analytics Team', CURRENT_TIMESTAMP()),
    ('FastPass', 'Premium line-skipping service', 'dimension', ['Express Pass', 'Skip the Line', 'VIP Access'], ['SALES_TRANSACTIONS'], NULL, 'Operations Team', CURRENT_TIMESTAMP());

-- =====================================================
-- 4. SCHEMA DOCUMENTATION FOR AI
-- =====================================================

-- Table to document database schema for AI understanding
CREATE OR REPLACE TABLE METADATA.TABLE_DOCUMENTATION (
    table_name STRING,
    schema_name STRING,
    business_purpose STRING,
    primary_key STRING,
    foreign_keys ARRAY,
    common_joins ARRAY,
    typical_filters ARRAY,
    business_rules ARRAY,
    sample_questions ARRAY,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert table documentation (will be populated after data loading)
INSERT INTO METADATA.TABLE_DOCUMENTATION VALUES
    ('CUSTOMERS', 'BUSINESS_ANALYTICS', 'Guest demographics, loyalty status, and customer segmentation', 'customer_id', [], [], ['loyalty_tier', 'age_group', 'region'], ['One customer can have multiple transactions', 'VIP customers get special pricing'], ['Who are our most valuable customers?', 'Show me customer demographics by park'], CURRENT_TIMESTAMP()),
    ('SALES_TRANSACTIONS', 'BUSINESS_ANALYTICS', 'All ticket sales and revenue transactions', 'transaction_id', ['customer_id->CUSTOMERS'], ['JOIN CUSTOMERS ON customer_id'], ['transaction_date', 'park_id', 'ticket_type'], ['Revenue must be positive', 'Transaction date cannot be in future'], ['What is our total revenue this quarter?', 'Show me best selling ticket types'], CURRENT_TIMESTAMP()),
    ('PARK_PERFORMANCE', 'BUSINESS_ANALYTICS', 'Daily operational metrics and KPIs by park', 'performance_id', ['park_id'], [], ['performance_date', 'park_id'], ['Daily metrics aggregated from hourly data'], ['Which park performed best last month?', 'Show me guest satisfaction trends'], CURRENT_TIMESTAMP()),
    ('ATTRACTION_ANALYTICS', 'BUSINESS_ANALYTICS', 'Ride popularity, efficiency, and guest experience metrics', 'analytics_id', ['park_id', 'attraction_id'], ['JOIN PARK_PERFORMANCE ON park_id'], ['attraction_type', 'date_recorded'], ['Capacity cannot exceed theoretical maximum'], ['What are our most popular attractions?', 'Show me wait time trends'], CURRENT_TIMESTAMP()),
    ('MARKETING_CAMPAIGNS', 'BUSINESS_ANALYTICS', 'Campaign performance and attribution data', 'campaign_id', [], [], ['campaign_start_date', 'channel', 'status'], ['Campaign end date must be after start date'], ['Which campaigns drive the most sales?', 'Show me marketing ROI'], CURRENT_TIMESTAMP()),
    ('FINANCIAL_SUMMARY', 'BUSINESS_ANALYTICS', 'Daily financial rollups and performance metrics', 'summary_id', ['park_id'], [], ['summary_date', 'park_id'], ['Daily totals must match transaction details'], ['Show me revenue trends', 'What is our year over year growth?'], CURRENT_TIMESTAMP());

-- =====================================================
-- 5. QUERY PATTERN TEMPLATES
-- =====================================================

-- Table to store common NL2SQL patterns and templates
CREATE OR REPLACE TABLE NL2SQL_SYSTEM.QUERY_PATTERNS (
    pattern_id STRING,
    pattern_name STRING,
    natural_language_pattern STRING,
    sql_template STRING,
    business_context STRING,
    complexity_level STRING, -- 'simple', 'medium', 'complex'
    required_tables ARRAY,
    example_question STRING,
    example_sql STRING,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert common query patterns
INSERT INTO NL2SQL_SYSTEM.QUERY_PATTERNS VALUES
    ('TOP_N', 'Top N Records', 'Show me the top {N} {entity} by {metric}', 'SELECT {columns} FROM {table} ORDER BY {metric} DESC LIMIT {N}', 'Ranking and top performers', 'simple', ['varies'], 'Show me the top 10 customers by revenue', 'SELECT customer_id, total_revenue FROM CUSTOMERS ORDER BY total_revenue DESC LIMIT 10', CURRENT_TIMESTAMP()),
    ('TIME_TREND', 'Time Series Analysis', 'Show me {metric} trends over {time_period}', 'SELECT {date_column}, {aggregation}({metric}) FROM {table} WHERE {date_column} >= {start_date} GROUP BY {date_column} ORDER BY {date_column}', 'Temporal analysis and trends', 'medium', ['time_dimension_table'], 'Show me revenue trends over the last quarter', 'SELECT transaction_date, SUM(revenue) FROM SALES_TRANSACTIONS WHERE transaction_date >= DATEADD(month, -3, CURRENT_DATE()) GROUP BY transaction_date ORDER BY transaction_date', CURRENT_TIMESTAMP()),
    ('COMPARISON', 'Comparative Analysis', 'Compare {metric} between {dimension1} and {dimension2}', 'SELECT {dimension}, {aggregation}({metric}) FROM {table} WHERE {dimension} IN ({values}) GROUP BY {dimension}', 'Side-by-side comparisons', 'medium', ['dimension_table'], 'Compare revenue between Florida and California parks', 'SELECT park_region, SUM(revenue) FROM SALES_TRANSACTIONS s JOIN PARKS p ON s.park_id = p.park_id WHERE park_region IN (''Florida'', ''California'') GROUP BY park_region', CURRENT_TIMESTAMP()),
    ('CORRELATION', 'Cross-Metric Analysis', 'How does {metric1} relate to {metric2}', 'SELECT {metric1}, {metric2}, CORR({metric1}, {metric2}) FROM {table}', 'Understanding relationships between metrics', 'complex', ['fact_table'], 'How does guest satisfaction relate to wait times?', 'SELECT guest_satisfaction, avg_wait_time, CORR(guest_satisfaction, avg_wait_time) FROM ATTRACTION_ANALYTICS', CURRENT_TIMESTAMP());

-- =====================================================
-- 6. NL2SQL PROCESSING FUNCTIONS
-- =====================================================

-- Function to extract business intent from natural language
CREATE OR REPLACE FUNCTION extract_query_intent(user_question STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    result VARIANT;
BEGIN
    TRY
        SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.COMPLETE(
                'mixtral-8x7b',
                CONCAT(
                    'Analyze this business question and extract the query intent in JSON format: "', user_question, '". ',
                    'Return JSON with fields: entity (what data), metric (what measure), dimension (how to group), time_filter (when), aggregation (how to calculate), complexity (simple/medium/complex). ',
                    'Context: This is for UDX theme park business analytics with tables for customers, sales, attractions, and performance.'
                )
            )
        ) INTO result;
        RETURN result;
    EXCEPTION
        WHEN statement_error THEN
            RETURN PARSE_JSON('{"error": "Cortex AI not available", "entity": "unknown", "metric": "count", "dimension": "none", "time_filter": "none", "aggregation": "count", "complexity": "simple"}');
    END;
END;
$$;

-- Function to generate SQL from natural language with business context
CREATE OR REPLACE FUNCTION generate_business_sql(
    user_question STRING,
    schema_context STRING DEFAULT 'BUSINESS_ANALYTICS'
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    business_context STRING;
    sql_query STRING;
BEGIN
    -- Get business context from glossary and table documentation
    SET business_context = (
        SELECT LISTAGG(
            CONCAT(term, ': ', definition, ' (Tables: ', ARRAY_TO_STRING(table_references, ', '), ')'),
            '; '
        ) WITHIN GROUP (ORDER BY term)
        FROM METADATA.BUSINESS_GLOSSARY
        WHERE ARRAY_SIZE(table_references) > 0
    );
    
    -- Generate SQL using Cortex AI with business context
    SET sql_query = SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'You are a SQL expert for UDX theme park business analytics. ',
            'Convert this natural language question to optimized Snowflake SQL: "', user_question, '". ',
            'Business Context: ', business_context, '. ',
            'Available tables in BUSINESS_ANALYTICS schema: CUSTOMERS, SALES_TRANSACTIONS, PARK_PERFORMANCE, ATTRACTION_ANALYTICS, MARKETING_CAMPAIGNS, FINANCIAL_SUMMARY. ',
            'Use proper table aliases, include appropriate WHERE clauses, and optimize for performance. ',
            'Return only the SQL query without explanation.'
        )
    );
    
    RETURN sql_query;
END;
$$;

-- =====================================================
-- 7. CONVERSATION CONTEXT MANAGEMENT
-- =====================================================

-- Table to store conversation history for context-aware queries
CREATE OR REPLACE TABLE NL2SQL_SYSTEM.CONVERSATION_HISTORY (
    session_id STRING,
    user_id STRING,
    question_sequence INTEGER,
    user_question STRING,
    generated_sql STRING,
    query_results_summary STRING,
    context_used VARIANT,
    feedback_score INTEGER, -- 1-5 rating from user
    timestamp_utc TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Function to get conversation context for follow-up questions
CREATE OR REPLACE FUNCTION get_conversation_context(session_id STRING, lookback_questions INTEGER DEFAULT 3)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT LISTAGG(
        CONCAT('Q: ', user_question, ' | SQL: ', generated_sql),
        ' ; '
    ) WITHIN GROUP (ORDER BY question_sequence DESC)
    FROM NL2SQL_SYSTEM.CONVERSATION_HISTORY
    WHERE session_id = session_id
    ORDER BY question_sequence DESC
    LIMIT lookback_questions
$$;

-- =====================================================
-- 8. SECURITY AND GOVERNANCE
-- =====================================================

-- Create roles for different user types
CREATE ROLE IF NOT EXISTS NL2SQL_BUSINESS_USER COMMENT = 'Role for business users with governed data access';
CREATE ROLE IF NOT EXISTS NL2SQL_ANALYST COMMENT = 'Role for analysts with broader data access';
CREATE ROLE IF NOT EXISTS NL2SQL_ADMIN COMMENT = 'Role for administrators managing the NL2SQL system';

-- Grant appropriate permissions
GRANT USAGE ON DATABASE UDX_NL2SQL TO ROLE NL2SQL_BUSINESS_USER;
GRANT USAGE ON SCHEMA UDX_NL2SQL.BUSINESS_ANALYTICS TO ROLE NL2SQL_BUSINESS_USER;
GRANT SELECT ON ALL TABLES IN SCHEMA UDX_NL2SQL.BUSINESS_ANALYTICS TO ROLE NL2SQL_BUSINESS_USER;

GRANT USAGE ON DATABASE UDX_NL2SQL TO ROLE NL2SQL_ANALYST;
GRANT USAGE ON ALL SCHEMAS IN DATABASE UDX_NL2SQL TO ROLE NL2SQL_ANALYST;
GRANT SELECT ON ALL TABLES IN DATABASE UDX_NL2SQL TO ROLE NL2SQL_ANALYST;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE UDX_ANALYTICS_WAREHOUSE TO ROLE NL2SQL_BUSINESS_USER;
GRANT USAGE ON WAREHOUSE UDX_ANALYTICS_WAREHOUSE TO ROLE NL2SQL_ANALYST;

-- Table to track query governance and resource usage
CREATE OR REPLACE TABLE NL2SQL_SYSTEM.QUERY_GOVERNANCE (
    query_id STRING DEFAULT UUID_STRING(),
    user_id STRING,
    user_role STRING,
    natural_language_query STRING,
    generated_sql STRING,
    execution_time_ms INTEGER,
    rows_returned INTEGER,
    credits_consumed DECIMAL(10,4),
    query_complexity STRING, -- 'low', 'medium', 'high'
    approved_status STRING, -- 'auto_approved', 'requires_review', 'blocked'
    executed_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- 9. SAMPLE QUERY VALIDATION
-- =====================================================

-- Test basic AI functionality (requires Cortex AI to be enabled)
-- NOTE: If this fails, contact your Snowflake administrator to enable Cortex AI
SELECT 'NL2SQL Setup Complete!' as status,
       TRY_CAST(
           SNOWFLAKE.CORTEX.COMPLETE(
               'mixtral-8x7b', 
               'Hello! I am setting up a natural language to SQL system for UDX theme park business analytics. Can you help me convert business questions to SQL?'
           ) AS STRING
       ) as ai_test;

-- Test business context function
SELECT 'Business Context Test' as test_type,
       extract_query_intent('Show me the top 10 customers by total revenue this year') as intent_extraction;

-- Display setup summary
SELECT 
    'NL2SQL Environment Setup Completed!' as message,
    CURRENT_DATABASE() as database_name,
    CURRENT_SCHEMA() as schema_name,
    CURRENT_WAREHOUSE() as warehouse_name,
    (SELECT COUNT(*) FROM METADATA.BUSINESS_GLOSSARY) as business_terms_loaded,
    (SELECT COUNT(*) FROM METADATA.TABLE_DOCUMENTATION) as tables_documented,
    (SELECT COUNT(*) FROM NL2SQL_SYSTEM.QUERY_PATTERNS) as query_patterns_loaded,
    CURRENT_TIMESTAMP() as setup_timestamp; 