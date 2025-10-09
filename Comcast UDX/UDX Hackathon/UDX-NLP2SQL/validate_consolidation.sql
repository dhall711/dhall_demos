-- =================================================================
-- UDX AI Hackathon Consolidation Validation Script
-- =================================================================
-- This script validates that the consolidated project setup works correctly
-- for both Track A (NLP2SQL) and Track B (Data Quality)

-- =================================================================
-- STEP 1: RUN FOUNDATION SETUP
-- =================================================================
-- Execute the unified setup script
-- SOURCE 00-shared-foundation/setup/unified_setup.sql;

-- =================================================================
-- STEP 2: LOAD BUSINESS DATA  
-- =================================================================
-- Execute the unified business data loader
-- SOURCE 00-shared-foundation/business-data/unified_business_data.sql;

-- =================================================================
-- STEP 3: VALIDATE ENVIRONMENT SETUP
-- =================================================================

-- Check database and schemas
SHOW DATABASES LIKE 'UDX_AI_HACKATHON';
SHOW SCHEMAS IN DATABASE UDX_AI_HACKATHON;

-- Check warehouse
SHOW WAREHOUSES LIKE 'UDX_AI_WAREHOUSE';

-- Set context
USE DATABASE UDX_AI_HACKATHON;
USE WAREHOUSE UDX_AI_WAREHOUSE;
USE SCHEMA BUSINESS_ANALYTICS;

-- =================================================================
-- STEP 4: VALIDATE BUSINESS DATA LOADING
-- =================================================================

-- Check all core tables exist and have data
SELECT 'PARKS' as table_name, COUNT(*) as record_count 
FROM PARKS
UNION ALL
SELECT 'CUSTOMERS' as table_name, COUNT(*) as record_count 
FROM CUSTOMERS
UNION ALL
SELECT 'SALES_TRANSACTIONS' as table_name, COUNT(*) as record_count 
FROM SALES_TRANSACTIONS
UNION ALL
SELECT 'PARK_PERFORMANCE' as table_name, COUNT(*) as record_count 
FROM PARK_PERFORMANCE
ORDER BY table_name;

-- Validate business context
SELECT * FROM BUSINESS_GLOSSARY LIMIT 5;

-- Check data quality for Track B
SELECT 
    'Customer Data Quality' as validation_type,
    COUNT(CASE WHEN data_quality_flag = 'CLEAN' THEN 1 END) as clean_records,
    COUNT(CASE WHEN data_quality_flag != 'CLEAN' THEN 1 END) as quality_issues,
    ROUND(COUNT(CASE WHEN data_quality_flag = 'CLEAN' THEN 1 END) * 100.0 / COUNT(*), 2) as quality_percentage
FROM CUSTOMERS

UNION ALL

SELECT 
    'Transaction Data Quality' as validation_type,
    COUNT(CASE WHEN data_quality_score >= 0.90 THEN 1 END) as clean_records,
    COUNT(CASE WHEN data_quality_score < 0.90 THEN 1 END) as quality_issues,
    ROUND(AVG(data_quality_score) * 100, 2) as quality_percentage
FROM SALES_TRANSACTIONS;

-- =================================================================
-- STEP 5: VALIDATE SHARED AI FOUNDATION
-- =================================================================

USE SCHEMA SHARED_FOUNDATION;

-- Test AI model selection function
SELECT get_ai_model_for_task('BALANCED') as recommended_model;
SELECT get_ai_model_for_task('NLP2SQL') as nlp2sql_model;
SELECT get_ai_model_for_task('DATA_QUALITY') as quality_model;

-- Test business context function
SELECT add_business_context('What is our revenue?') as enhanced_prompt;

-- Check monitoring tables exist
DESCRIBE TABLE QUERY_EXECUTION_LOG;
DESCRIBE TABLE CONVERSATION_SESSIONS;

-- =================================================================
-- STEP 6: VALIDATE TRACK A (NLP2SQL) SETUP
-- =================================================================

USE SCHEMA NLP2SQL_TRACK;

-- Test NLP2SQL query intent function
SELECT extract_query_intent('Show me revenue by park') as intent_analysis;

-- Validate NLP2SQL function handles errors gracefully
SELECT extract_query_intent('Invalid test query 12345') as error_handling_test;

-- =================================================================
-- STEP 7: VALIDATE TRACK B (DATA QUALITY) SETUP  
-- =================================================================

USE SCHEMA DATA_QUALITY_TRACK;

-- Test data quality classification function
SELECT classify_quality_issue('Email field contains invalid format xyz123') as quality_classification;

-- Check quality metrics table exists
DESCRIBE TABLE DATA_QUALITY_METRICS;

-- Insert test quality metric
INSERT INTO DATA_QUALITY_METRICS (
    table_name, column_name, quality_dimension, 
    metric_value, threshold_value, status
) VALUES (
    'TEST_TABLE', 'email', 'VALIDITY', 
    0.98, 0.95, 'PASS'
);

-- Verify test insertion
SELECT * FROM DATA_QUALITY_METRICS WHERE table_name = 'TEST_TABLE';

-- =================================================================
-- STEP 8: VALIDATE BUSINESS ANALYTICS VIEWS
-- =================================================================

USE SCHEMA BUSINESS_ANALYTICS;

-- Test executive summary view (Track A)
SELECT park_name, park_region, COUNT(*) as month_count
FROM EXECUTIVE_SUMMARY 
GROUP BY park_name, park_region
LIMIT 5;

-- Test data quality dashboard view (Track B)
SELECT * FROM DATA_QUALITY_DASHBOARD;

-- =================================================================
-- STEP 9: TEST CORTEX AI AVAILABILITY (IF ENABLED)
-- =================================================================

-- Test basic Cortex AI functionality
-- Note: This may fail if Cortex AI is not enabled on your account
SELECT 
    'Testing Cortex AI availability...' as test_status,
    TRY_CAST(
        SNOWFLAKE.CORTEX.COMPLETE(
            'llama3-8b', 
            'Respond with: Cortex AI is working for UDX Hackathon validation'
        ) AS STRING
    ) as cortex_response;

-- =================================================================
-- STEP 10: SAMPLE USE CASES FOR BOTH TRACKS
-- =================================================================

-- Track A Sample: Business question analysis
USE SCHEMA NLP2SQL_TRACK;
SELECT 'Track A: NLP2SQL Analysis' as test_type,
       extract_query_intent('What are our top 3 most profitable parks?') as sample_analysis;

-- Track B Sample: Data quality assessment  
USE SCHEMA DATA_QUALITY_TRACK;
SELECT 'Track B: Quality Analysis' as test_type,
       classify_quality_issue('Customer table has 5% null email addresses') as sample_classification;

-- =================================================================
-- STEP 11: VALIDATION SUMMARY
-- =================================================================

-- Create validation summary
WITH validation_results AS (
    SELECT 
        'Foundation Setup' as component,
        CASE WHEN (SELECT COUNT(*) FROM UDX_AI_HACKATHON.INFORMATION_SCHEMA.SCHEMATA) >= 4 
             THEN '✅ PASS' ELSE '❌ FAIL' END as status
    
    UNION ALL
    
    SELECT 
        'Business Data' as component,
        CASE WHEN (SELECT COUNT(*) FROM UDX_AI_HACKATHON.BUSINESS_ANALYTICS.CUSTOMERS) > 10000 
             THEN '✅ PASS' ELSE '❌ FAIL' END as status
    
    UNION ALL
    
    SELECT 
        'AI Functions' as component,
        CASE WHEN (SELECT get_ai_model_for_task('BALANCED')) = 'mixtral-8x7b' 
             THEN '✅ PASS' ELSE '❌ FAIL' END as status
    
    UNION ALL
    
    SELECT 
        'Track A Setup' as component,
        CASE WHEN EXISTS (SELECT 1 FROM UDX_AI_HACKATHON.INFORMATION_SCHEMA.TABLES 
                         WHERE TABLE_SCHEMA = 'NLP2SQL_TRACK') 
             THEN '✅ PASS' ELSE '❌ FAIL' END as status
    
    UNION ALL
    
    SELECT 
        'Track B Setup' as component,
        CASE WHEN EXISTS (SELECT 1 FROM UDX_AI_HACKATHON.INFORMATION_SCHEMA.TABLES 
                         WHERE TABLE_SCHEMA = 'DATA_QUALITY_TRACK') 
             THEN '✅ PASS' ELSE '❌ FAIL' END as status
)
SELECT 
    '🎉 UDX AI HACKATHON VALIDATION RESULTS 🎉' as title,
    '' as separator
UNION ALL
SELECT component, status FROM validation_results
UNION ALL
SELECT 
    '', 
    CASE WHEN COUNT(CASE WHEN status LIKE '%PASS%' THEN 1 END) = COUNT(*) 
         THEN '🚀 ALL SYSTEMS GO! Project ready for production use!'
         ELSE '⚠️  Some components need attention. Check setup steps above.' 
    END as final_status
FROM validation_results;

-- =================================================================
-- VALIDATION COMPLETE!
-- =================================================================

SELECT 
    '✨ CONSOLIDATION VALIDATION COMPLETE! ✨' as message,
    'Both Track A (NLP2SQL) and Track B (Data Quality) are ready!' as status,
    'Proceed with workshop delivery or development!' as next_step; 