-- =====================================================
-- Lab 03: Advanced Query Translation - Exercises
-- =====================================================
-- This lab covers complex business logic, conversational context,
-- query templates, and error handling

USE DATABASE UDX_NL2SQL;
USE SCHEMA BUSINESS_ANALYTICS;
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;

-- =====================================================
-- PART A: COMPLEX BUSINESS LOGIC (25 minutes)
-- =====================================================

-- Exercise A1: Multi-Table Complex Analysis
-- Business Question: "Show me customer lifetime value analysis with park preferences"

SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Create SQL for customer lifetime value analysis. Join CUSTOMERS, SALES_TRANSACTIONS, and PARKS tables. 
     Include: customer details, total lifetime revenue, visit frequency, preferred park, 
     average transaction amount, and loyalty tier impact.
     
     Business rules:
     - Calculate visit frequency as transactions per month since registration
     - Identify preferred park as location with most transactions
     - Include only active customers with at least 3 transactions
     
     Use these tables:
     - CUSTOMERS (customer_id, total_lifetime_revenue, loyalty_tier, registration_date)
     - SALES_TRANSACTIONS (customer_id, park_id, total_revenue, transaction_date)
     - PARKS (park_id, park_name, park_region)
     
     Return SQL only.'
) as complex_customer_analysis;

-- Exercise A2: Advanced Time-Series Analysis
-- Business Question: "Analyze seasonal trends with year-over-year growth patterns"

SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-70b',
    'Generate SQL for advanced seasonal analysis with these requirements:
     
     1. Monthly revenue aggregation by park
     2. Year-over-year growth calculations
     3. Seasonal trend identification (quarters)
     4. Rolling 3-month averages
     5. Growth rate categorization (High >15%, Medium 5-15%, Low <5%)
     
     Use window functions (LAG, LEAD, AVG OVER) and CTEs.
     Include parks with at least 12 months of data.
     
     Tables: SALES_TRANSACTIONS (park_id, total_revenue, transaction_date)
             PARKS (park_id, park_name)
             
     Format as: park_name, month, current_revenue, yoy_growth_pct, trend_category'
) as seasonal_analysis_sql;

-- =====================================================
-- PART B: CONVERSATIONAL CONTEXT (25 minutes)
-- =====================================================

-- Create conversation state management table
CREATE OR REPLACE TABLE CONVERSATION_CONTEXT (
    session_id STRING,
    conversation_turn INTEGER,
    user_question STRING,
    generated_sql STRING,
    execution_status STRING,
    result_summary STRING,
    business_context STRING,
    timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Exercise B1: Context-Aware Query Generation
-- Scenario: Multi-turn conversation about park performance

-- Turn 1: Initial question
INSERT INTO CONVERSATION_CONTEXT VALUES (
    'SESS_001', 1, 
    'Show me revenue for all parks last month',
    'SELECT park_name, SUM(total_revenue) FROM sales_transactions s JOIN parks p ON s.park_id = p.park_id WHERE MONTH(transaction_date) = MONTH(DATEADD(month, -1, CURRENT_DATE())) GROUP BY park_name',
    'SUCCESS',
    'Universal Studios Florida: $2.1M, Islands of Adventure: $1.8M, Universal Studios Hollywood: $1.9M',
    'Monthly revenue comparison',
    CURRENT_TIMESTAMP()
);

-- Turn 2: Follow-up with context
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Previous conversation context:
     User asked: "Show me revenue for all parks last month"
     Results showed: Universal Studios Florida: $2.1M, Islands of Adventure: $1.8M, Universal Studios Hollywood: $1.9M
     
     New question: "Which one had the highest growth compared to the previous month?"
     
     Generate SQL that:
     1. Uses the previous context about monthly revenue
     2. Calculates month-over-month growth for each park
     3. Identifies the park with highest growth rate
     4. Shows both absolute and percentage growth
     
     Return only the SQL query.'
) as contextual_growth_query;

-- Exercise B2: Conversation Memory Integration
CREATE OR REPLACE FUNCTION continue_conversation(
    session_id STRING,
    new_question STRING
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        'Conversation history: ' || 
        LISTAGG(
            'Turn ' || conversation_turn || ': Q: ' || user_question || 
            ' | A: ' || result_summary, 
            ' || '
        ) WITHIN GROUP (ORDER BY conversation_turn) ||
        ' || New question: ' || new_question ||
        ' || Generate appropriate SQL considering the conversation context.'
    )
    FROM CONVERSATION_CONTEXT 
    WHERE session_id = session_id
$$;

-- =====================================================
-- PART C: QUERY TEMPLATES & PATTERNS (20 minutes)
-- =====================================================

-- Exercise C1: Revenue Analysis Template
CREATE OR REPLACE FUNCTION revenue_analysis_template(
    time_period STRING,
    grouping_dimension STRING,
    filter_condition STRING DEFAULT ''
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'Generate SQL template for revenue analysis with these parameters:
         - Time period: ' || time_period || ' (daily, weekly, monthly, quarterly)
         - Group by: ' || grouping_dimension || ' (park, customer_segment, ticket_type, etc.)
         - Additional filters: ' || COALESCE(filter_condition, 'none') || '
         
         Include:
         - Total revenue
         - Transaction count
         - Average transaction value
         - Unique customer count
         - Growth vs previous period
         
         Use proper date functions and aggregations for Snowflake.
         Return clean, executable SQL.'
    )
$$;

-- Test the template
SELECT revenue_analysis_template(
    'monthly',
    'park_name',
    'loyalty_tier = Gold'
) as template_result;

-- Exercise C2: Customer Segmentation Pattern
CREATE OR REPLACE FUNCTION customer_segmentation_pattern(
    segmentation_criteria STRING
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        'Create customer segmentation SQL based on: ' || segmentation_criteria || '
         
         Generate segments like:
         - High Value (top 20% by revenue)
         - Regular (middle 60%)
         - Occasional (bottom 20%)
         
         Include for each segment:
         - Customer count
         - Average lifetime value
         - Average visit frequency
         - Preferred parks
         
         Use NTILE or CASE statements for segmentation logic.'
    )
$$;

-- =====================================================
-- PART D: ERROR HANDLING & VALIDATION (20 minutes)
-- =====================================================

-- Exercise D1: Query Validation Function
CREATE OR REPLACE FUNCTION validate_and_execute_query(
    user_question STRING,
    generated_sql STRING
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    validation_result VARIANT;
    execution_result VARIANT;
    error_message STRING;
BEGIN
    -- Basic SQL validation
    IF (UPPER(generated_sql) NOT LIKE '%SELECT%') THEN
        error_message := 'Generated query must be a SELECT statement';
        RETURN OBJECT_CONSTRUCT('status', 'ERROR', 'message', error_message);
    END IF;
    
    -- Check for required table references
    IF (UPPER(generated_sql) NOT LIKE '%SALES_TRANSACTIONS%' 
        AND UPPER(generated_sql) NOT LIKE '%CUSTOMERS%' 
        AND UPPER(generated_sql) NOT LIKE '%PARKS%') THEN
        error_message := 'Query must reference at least one business table';
        RETURN OBJECT_CONSTRUCT('status', 'ERROR', 'message', error_message);
    END IF;
    
    -- Try to execute (in real implementation, use TRY/CATCH)
    BEGIN
        -- This would execute the query in practice
        RETURN OBJECT_CONSTRUCT(
            'status', 'SUCCESS',
            'query', generated_sql,
            'validation', 'PASSED'
        );
    EXCEPTION
        WHEN OTHER THEN
            error_message := 'Query execution failed: ' || SQLERRM;
            RETURN OBJECT_CONSTRUCT('status', 'ERROR', 'message', error_message);
    END;
END;
$$;

-- Exercise D2: Smart Error Recovery
CREATE OR REPLACE FUNCTION recover_from_query_error(
    original_question STRING,
    failed_sql STRING,
    error_message STRING
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'The user asked: "' || original_question || '"
         
         The generated SQL failed: ' || failed_sql || '
         Error: ' || error_message || '
         
         Available tables: CUSTOMERS, SALES_TRANSACTIONS, PARKS, PARK_PERFORMANCE
         
         Generate a corrected SQL query that:
         1. Addresses the error
         2. Answers the original question
         3. Uses simpler logic if the original was too complex
         4. Includes proper error prevention (NULL checks, etc.)
         
         Return only the corrected SQL.'
    )
$$;

-- Test error recovery
SELECT recover_from_query_error(
    'Show me average customer satisfaction by park',
    'SELECT park_name, AVG(satisfaction) FROM wrong_table GROUP BY park_name',
    'Table "wrong_table" does not exist'
) as recovered_query;

-- =====================================================
-- ADVANCED EXERCISES
-- =====================================================

-- Challenge: Create a comprehensive business intelligence function
CREATE OR REPLACE FUNCTION business_intelligence_assistant(
    question STRING,
    context STRING DEFAULT '',
    require_validation BOOLEAN DEFAULT TRUE
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    generated_sql STRING;
    validation_result VARIANT;
BEGIN
    -- Generate SQL with context
    generated_sql := (
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mixtral-8x7b',
            CASE 
                WHEN context != '' THEN 
                    'Previous context: ' || context || ' | New question: ' || question
                ELSE question
            END || 
            ' | Use UDX theme park business tables. Return only SQL.'
        )
    );
    
    -- Validate if required
    IF (require_validation) THEN
        validation_result := validate_and_execute_query(question, generated_sql);
        RETURN validation_result;
    END IF;
    
    RETURN OBJECT_CONSTRUCT(
        'status', 'SUCCESS',
        'sql', generated_sql,
        'question', question
    );
END;
$$;

-- =====================================================
-- SUCCESS CRITERIA
-- =====================================================

/*
After completing this lab, you should be able to:

□ Generate complex multi-table analytical queries
□ Implement conversational context in query generation
□ Create reusable query templates and patterns
□ Build robust error handling and validation systems
□ Optimize query performance for enterprise workloads

Key Skills Demonstrated:
- Advanced Cortex AI prompt engineering
- Complex SQL pattern development
- State management for conversations
- Enterprise error handling strategies
- Template-based query generation
*/ 