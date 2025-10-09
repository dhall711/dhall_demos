-- =====================================================
-- UDX AI Hackathon: Unified Foundation Setup
-- =====================================================
-- This script creates the shared infrastructure for both
-- Track A (NLP2SQL) and Track B (Data Quality) learning paths

-- =====================================================
-- 1. ENVIRONMENT SETUP
-- =====================================================

-- Create main database for both tracks
CREATE DATABASE IF NOT EXISTS UDX_AI_HACKATHON;
USE DATABASE UDX_AI_HACKATHON;

-- Create schemas for different use cases
CREATE SCHEMA IF NOT EXISTS NLP2SQL_TRACK;           -- Track A: Natural Language to SQL
CREATE SCHEMA IF NOT EXISTS DATA_QUALITY_TRACK;      -- Track B: Data Quality & Monitoring
CREATE SCHEMA IF NOT EXISTS SHARED_FOUNDATION;       -- Shared components
CREATE SCHEMA IF NOT EXISTS BUSINESS_ANALYTICS;      -- Unified business data

-- Create optimized warehouse for AI workloads
CREATE WAREHOUSE IF NOT EXISTS UDX_AI_WAREHOUSE
  WITH WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  COMMENT = 'Unified warehouse for UDX AI Hackathon - both tracks';

USE WAREHOUSE UDX_AI_WAREHOUSE;

-- =====================================================
-- 2. ROLES AND PERMISSIONS
-- =====================================================

-- Create roles for different user types
CREATE ROLE IF NOT EXISTS UDX_AI_STUDENT;
CREATE ROLE IF NOT EXISTS UDX_AI_INSTRUCTOR;
CREATE ROLE IF NOT EXISTS UDX_AI_ADMIN;

-- Grant permissions
GRANT USAGE ON DATABASE UDX_AI_HACKATHON TO ROLE UDX_AI_STUDENT;
GRANT USAGE ON ALL SCHEMAS IN DATABASE UDX_AI_HACKATHON TO ROLE UDX_AI_STUDENT;
GRANT SELECT ON ALL TABLES IN DATABASE UDX_AI_HACKATHON TO ROLE UDX_AI_STUDENT;
GRANT USAGE ON WAREHOUSE UDX_AI_WAREHOUSE TO ROLE UDX_AI_STUDENT;

-- Additional permissions for instructors
GRANT ALL ON DATABASE UDX_AI_HACKATHON TO ROLE UDX_AI_INSTRUCTOR;
GRANT ALL ON WAREHOUSE UDX_AI_WAREHOUSE TO ROLE UDX_AI_INSTRUCTOR;

-- =====================================================
-- 3. SHARED BUSINESS CONTEXT
-- =====================================================

USE SCHEMA BUSINESS_ANALYTICS;

-- Business glossary for consistent terminology across both tracks
CREATE OR REPLACE TABLE BUSINESS_GLOSSARY (
    term STRING,
    definition STRING,
    context STRING,
    track_relevance STRING,
    examples ARRAY
);

INSERT INTO BUSINESS_GLOSSARY VALUES
    ('Guest', 'Theme park visitor or customer', 'UDX Operations', 'Both tracks', ['paying customer', 'park visitor', 'ticket holder']),
    ('Attraction', 'Ride or entertainment experience', 'UDX Operations', 'Both tracks', ['roller coaster', 'show', 'ride']),
    ('Capacity Utilization', 'Percentage of theoretical maximum capacity used', 'Operations', 'Both tracks', ['80% capacity', 'full capacity', 'under-utilized']),
    ('Guest Satisfaction', 'Rating of guest experience (1-10 scale)', 'Experience', 'Both tracks', ['satisfaction score', 'guest rating', 'experience rating']),
    ('Revenue per Guest', 'Average revenue generated per individual guest', 'Financial', 'Both tracks', ['per-guest revenue', 'guest spend', 'average spend']),
    ('Wait Time', 'Time guests spend waiting in line for attractions', 'Operations', 'Both tracks', ['queue time', 'line wait', 'waiting period']),
    ('Data Quality Issue', 'Problem with data accuracy, completeness, or consistency', 'Data Management', 'Track B focus', ['missing data', 'duplicate records', 'invalid values']),
    ('Natural Language Query', 'Business question asked in plain English', 'Analytics', 'Track A focus', ['plain English question', 'conversational query', 'business question']);

-- =====================================================
-- 4. CORTEX AI FOUNDATION
-- =====================================================

USE SCHEMA SHARED_FOUNDATION;

-- Test Cortex AI availability
SELECT TRY_CAST(
    SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Hello, AI! Respond with "Cortex AI is ready for UDX Hackathon"')
    AS STRING
) as cortex_test;

-- Core AI helper function for both tracks
CREATE OR REPLACE FUNCTION get_ai_model_for_task(task_type STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
    CASE UPPER(task_type)
        WHEN 'FAST_ANALYSIS' THEN 'llama3-8b'        -- Quick responses
        WHEN 'BALANCED' THEN 'mixtral-8x7b'          -- Recommended default
        WHEN 'DETAILED' THEN 'llama3-70b'            -- Complex analysis
        WHEN 'TRANSLATION' THEN 'mixtral-8x7b'       -- NLP2SQL focus
        WHEN 'QUALITY_ANALYSIS' THEN 'llama3-70b'    -- Data quality focus
        ELSE 'mixtral-8x7b'                          -- Safe default
    END
$$;

-- Enhanced AI context function for business questions
CREATE OR REPLACE FUNCTION add_business_context(user_question STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
    'You are an AI assistant for UDX theme park business analytics. ' ||
    'Context: UDX operates Universal Studios theme parks with attractions, guests, tickets, merchandise, and food sales. ' ||
    'Business tables include: PARKS, CUSTOMERS, SALES_TRANSACTIONS, PARK_PERFORMANCE, ATTRACTION_ANALYTICS. ' ||
    'Current question: ' || user_question || 
    ' Provide helpful, business-focused responses using UDX operational context.'
$$;

-- =====================================================
-- 5. SHARED MONITORING TABLES
-- =====================================================

-- Query execution tracking for both tracks
CREATE OR REPLACE TABLE QUERY_EXECUTION_LOG (
    execution_id STRING DEFAULT UUID_STRING(),
    track_type STRING,                    -- 'NLP2SQL' or 'DATA_QUALITY'
    user_question STRING,
    generated_sql STRING,
    execution_status STRING,
    execution_time_ms INTEGER,
    result_count INTEGER,
    ai_model_used STRING,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Conversation state management (useful for both tracks)
CREATE OR REPLACE TABLE CONVERSATION_SESSIONS (
    session_id STRING,
    track_type STRING,
    user_id STRING,
    conversation_turn INTEGER,
    user_input STRING,
    ai_response STRING,
    context_data VARIANT,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- 6. TRACK-SPECIFIC SETUP
-- =====================================================

-- Track A: NLP2SQL specific setup
USE SCHEMA NLP2SQL_TRACK;

-- NLP2SQL query intent extraction
CREATE OR REPLACE FUNCTION extract_query_intent(natural_language_question STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    intent_analysis VARIANT;
BEGIN
    TRY
        SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.COMPLETE(
                'mixtral-8x7b',
                'Analyze this business question and return JSON with query_type, tables_needed, business_intent: ' || 
                natural_language_question
            )
        ) INTO intent_analysis;
        
        RETURN intent_analysis;
    EXCEPTION
        WHEN OTHER THEN
            RETURN PARSE_JSON('{"error": "Intent analysis failed", "query_type": "unknown"}');
    END;
END;
$$;

-- Track B: Data Quality specific setup
USE SCHEMA DATA_QUALITY_TRACK;

-- Data quality issue classification
CREATE OR REPLACE FUNCTION classify_quality_issue(issue_description STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        'Classify this data quality issue into one of: COMPLETENESS, ACCURACY, CONSISTENCY, VALIDITY, TIMELINESS, UNIQUENESS. ' ||
        'Issue: ' || issue_description ||
        ' Return only the classification category.'
    )
$$;

-- Quality monitoring metrics table
CREATE OR REPLACE TABLE DATA_QUALITY_METRICS (
    metric_id STRING DEFAULT UUID_STRING(),
    table_name STRING,
    column_name STRING,
    quality_dimension STRING,      -- COMPLETENESS, ACCURACY, etc.
    metric_value DECIMAL(10,4),
    threshold_value DECIMAL(10,4),
    status STRING,                 -- PASS, WARN, FAIL
    check_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- 7. VALIDATION AND TESTING
-- =====================================================

-- Test basic functionality
SELECT 'Unified Setup Complete!' as status;

-- Test AI functionality
SELECT get_ai_model_for_task('BALANCED') as recommended_model;

-- Test business context
SELECT add_business_context('What is our total revenue?') as enhanced_question;

-- =====================================================
-- 8. NEXT STEPS
-- =====================================================

/*
Setup Complete! Next steps:

FOR TRACK A (NLP2SQL):
1. Load business data: Execute load_business_data.sql
2. Start with: TRACK-A-NLP2SQL/01-basic-translation/

FOR TRACK B (DATA QUALITY):  
1. Load business data: Execute load_all_data.sql (includes quality issues)
2. Start with: TRACK-B-DATA-QUALITY/01-quality-fundamentals/

FOR BOTH TRACKS:
- Business data will be loaded into BUSINESS_ANALYTICS schema
- All AI functions are ready in SHARED_FOUNDATION schema
- Track-specific functions are in respective schemas
*/

-- Set default context for users
USE WAREHOUSE UDX_AI_WAREHOUSE;
USE DATABASE UDX_AI_HACKATHON;
USE SCHEMA BUSINESS_ANALYTICS; 