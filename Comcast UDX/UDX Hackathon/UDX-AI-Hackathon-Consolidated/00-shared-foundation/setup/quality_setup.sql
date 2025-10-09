-- =====================================================
-- UDX Data Quality Project: Environment Setup
-- =====================================================
-- This script creates the foundational Snowflake environment
-- for the GenAI Data Quality Assistant project

-- Set context (adjust role as needed)
USE ROLE ACCOUNTADMIN; -- or SYSADMIN

-- =====================================================
-- 1. CREATE DATABASE AND SCHEMA
-- =====================================================

-- Create main database for the project
CREATE DATABASE IF NOT EXISTS UDX_DATA_QUALITY_PROJECT 
    COMMENT = 'Comcast UDX Data Quality Project - GenAI Data Quality Assistant';

-- Create schema for data quality operations
CREATE SCHEMA IF NOT EXISTS UDX_DATA_QUALITY_PROJECT.DATA_QUALITY
    COMMENT = 'Schema for data quality monitoring and AI operations';

-- Create schema for raw theme park data
CREATE SCHEMA IF NOT EXISTS UDX_DATA_QUALITY_PROJECT.THEME_PARK_OPS
    COMMENT = 'Schema for theme park operational data';

-- Set working context
USE DATABASE UDX_DATA_QUALITY_PROJECT;
USE SCHEMA DATA_QUALITY;

-- =====================================================
-- 2. CREATE VIRTUAL WAREHOUSE
-- =====================================================

-- Create warehouse optimized for AI workloads
CREATE WAREHOUSE IF NOT EXISTS UDX_AI_WAREHOUSE
    WITH 
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 300  -- 5 minutes
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for AI and data quality operations';

-- Use the warehouse
USE WAREHOUSE UDX_AI_WAREHOUSE;

-- =====================================================
-- 3. DATA QUALITY MONITORING TABLES
-- =====================================================

-- Table to track data quality rules and thresholds
CREATE OR REPLACE TABLE DATA_QUALITY_RULES (
    rule_id STRING,
    table_name STRING,
    column_name STRING,
    rule_type STRING, -- 'completeness', 'uniqueness', 'validity', 'consistency'
    rule_description STRING,
    threshold_value FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Table to store data quality check results
CREATE OR REPLACE TABLE DATA_QUALITY_RESULTS (
    check_id STRING DEFAULT UUID_STRING(),
    rule_id STRING,
    table_name STRING,
    column_name STRING,
    check_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    metric_value FLOAT,
    threshold_value FLOAT,
    status STRING, -- 'PASS', 'FAIL', 'WARNING'
    issue_count INTEGER,
    total_records INTEGER,
    ai_analysis VARIANT, -- JSON containing AI insights
    recommendations VARIANT -- JSON containing AI recommendations
);

-- Table to store anomaly detection results
CREATE OR REPLACE TABLE ANOMALY_DETECTION_LOG (
    anomaly_id STRING DEFAULT UUID_STRING(),
    detection_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    table_name STRING,
    column_name STRING,
    anomaly_type STRING, -- 'outlier', 'drift', 'pattern_break', 'missing_spike'
    severity STRING, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    anomaly_description STRING,
    affected_records INTEGER,
    confidence_score FLOAT, -- 0.0 to 1.0
    ai_explanation VARIANT,
    suggested_actions VARIANT,
    is_resolved BOOLEAN DEFAULT FALSE
);

-- Table to store AI-generated insights and summaries
CREATE OR REPLACE TABLE AI_INSIGHTS (
    insight_id STRING DEFAULT UUID_STRING(),
    generation_timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    insight_type STRING, -- 'summary', 'trend', 'recommendation', 'alert'
    context_tables ARRAY,
    insight_text STRING,
    confidence_level STRING, -- 'LOW', 'MEDIUM', 'HIGH'
    business_impact STRING, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    recommended_actions VARIANT,
    expiry_date DATE -- When this insight becomes stale
);

-- =====================================================
-- 4. HELPER FUNCTIONS AND PROCEDURES
-- =====================================================

-- Function to calculate data quality score
CREATE OR REPLACE FUNCTION calculate_quality_score(
    completeness_pct FLOAT,
    uniqueness_pct FLOAT,
    validity_pct FLOAT
)
RETURNS FLOAT
LANGUAGE SQL
AS
$$
    -- Weighted average of quality dimensions
    (completeness_pct * 0.4 + uniqueness_pct * 0.3 + validity_pct * 0.3)
$$;

-- =====================================================
-- 5. INITIAL DATA QUALITY RULES
-- =====================================================

-- Insert foundational data quality rules
INSERT INTO DATA_QUALITY_RULES VALUES
    ('R001', 'GUESTS', 'guest_id', 'uniqueness', 'Guest IDs must be unique', 100.0, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('R002', 'GUESTS', 'email', 'completeness', 'Email addresses should be present', 95.0, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('R003', 'GUESTS', 'age', 'validity', 'Guest age should be between 0 and 120', 99.0, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('R004', 'TICKETS', 'ticket_id', 'uniqueness', 'Ticket IDs must be unique', 100.0, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('R005', 'TICKETS', 'purchase_amount', 'validity', 'Purchase amount should be positive', 99.5, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('R006', 'RIDE_OPERATIONS', 'wait_time_minutes', 'validity', 'Wait times should be reasonable (0-180 min)', 98.0, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('R007', 'RIDE_OPERATIONS', 'hourly_capacity', 'consistency', 'Capacity should align with ride specifications', 95.0, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

-- =====================================================
-- 6. GRANT PERMISSIONS
-- =====================================================

-- Grant usage on database and schemas
GRANT USAGE ON DATABASE UDX_DATA_QUALITY_PROJECT TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA UDX_DATA_QUALITY_PROJECT.DATA_QUALITY TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA UDX_DATA_QUALITY_PROJECT.THEME_PARK_OPS TO ROLE PUBLIC;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA UDX_DATA_QUALITY_PROJECT.DATA_QUALITY TO ROLE PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA UDX_DATA_QUALITY_PROJECT.THEME_PARK_OPS TO ROLE PUBLIC;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE UDX_AI_WAREHOUSE TO ROLE PUBLIC;

-- =====================================================
-- 7. ENABLE CORTEX AI FEATURES
-- =====================================================

-- Test Cortex AI availability
SELECT 'Cortex AI Setup Complete!' as status,
       SNOWFLAKE.CORTEX.COMPLETE('llama3-8b', 'Hello! Can you help with data quality?') as ai_test;

-- Display setup summary
SELECT 
    'Setup completed successfully!' as message,
    CURRENT_DATABASE() as database_name,
    CURRENT_SCHEMA() as schema_name,
    CURRENT_WAREHOUSE() as warehouse_name,
    CURRENT_TIMESTAMP() as setup_timestamp; 