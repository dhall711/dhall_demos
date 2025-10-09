-- =====================================================
-- Lab 03: Basic NL2SQL Translation - Hands-On Exercises
-- =====================================================
-- Learn to translate business questions into SQL using Cortex AI

USE DATABASE UDX_NL2SQL;
USE SCHEMA BUSINESS_ANALYTICS;
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;

-- =====================================================
-- EXERCISE 1: Simple Business Aggregations
-- =====================================================

-- 1.1: Test Basic AI SQL Generation
-- Start with a simple business question to verify AI functionality
SELECT 
    'Testing Basic NL2SQL Translation' as exercise_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'You are a SQL expert for UDX theme park business analytics. Convert this natural language question to Snowflake SQL: "What is our total revenue from all ticket sales?" Use the SALES_TRANSACTIONS table. Return only the SQL code.'
    ) as generated_sql;

-- 1.2: Revenue Analytics - Total Revenue
-- Ask AI to generate SQL for total revenue calculation
WITH nl_query AS (
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'You are a SQL expert for UDX theme park business analytics. ',
            'Convert this question to optimized Snowflake SQL: "What is our total revenue this year?" ',
            'Use SALES_TRANSACTIONS table with total_revenue column and transaction_date for filtering. ',
            'Filter for current year only. Return only SQL code with appropriate column alias.'
        )
    ) as sql_query
)
-- Execute the AI-generated query (you would copy and run the generated SQL)
SELECT 
    'Total Revenue Analysis' as analysis_type,
    sql_query,
    'Copy the generated SQL above and execute it to see results' as instruction
FROM nl_query;

-- Manual example of what the AI should generate:
SELECT 
    'Total Revenue This Year' as metric,
    SUM(total_revenue) as total_annual_revenue,
    COUNT(*) as total_transactions
FROM SALES_TRANSACTIONS 
WHERE YEAR(transaction_date) = YEAR(CURRENT_DATE());

-- 1.3: Customer Analytics - Top Customers
-- Generate SQL to find top customers by lifetime value
SELECT 
    'Top Customers Analysis' as exercise_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Convert this business question to Snowflake SQL: "Who are our top 10 customers by total lifetime revenue?" ',
            'Use the CUSTOMERS table with customer_id, first_name, last_name, and total_lifetime_revenue columns. ',
            'Include proper ordering and limit. Return only the SQL code.'
        )
    ) as generated_sql;

-- Example result that AI should generate:
SELECT 
    customer_id,
    first_name,
    last_name,
    total_lifetime_revenue
FROM CUSTOMERS
ORDER BY total_lifetime_revenue DESC
LIMIT 10;

-- =====================================================
-- EXERCISE 2: Filtering and Business Logic
-- =====================================================

-- 2.1: Loyalty Tier Analysis
-- Ask AI to filter customers by loyalty tier
SELECT 
    'Loyalty Tier Filtering' as exercise_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Create SQL for this business question: "How many VIP customers do we have and what is their average lifetime revenue?" ',
            'Use CUSTOMERS table. VIP customers are those with is_vip = TRUE. ',
            'Return count and average revenue with meaningful column names.'
        )
    ) as ai_generated_query;

-- Manual example:
SELECT 
    'VIP Customer Analysis' as segment,
    COUNT(*) as vip_customer_count,
    ROUND(AVG(total_lifetime_revenue), 2) as avg_lifetime_revenue
FROM CUSTOMERS 
WHERE is_vip = TRUE;

-- 2.2: Park Performance Filtering
-- Generate SQL for park-specific analysis
SELECT 
    'Park Performance Query Generation' as exercise_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Convert to SQL: "Show me the average guest satisfaction and total revenue for Universal Studios Florida in the last 30 days" ',
            'Use PARK_PERFORMANCE table with park_id = ''UDX-FL'' and performance_date filtering. ',
            'Include appropriate date filtering and column aliases.'
        )
    ) as generated_query;

-- Expected result example:
SELECT 
    'Universal Studios Florida - Last 30 Days' as park_analysis,
    ROUND(AVG(average_guest_satisfaction), 2) as avg_satisfaction,
    SUM(daily_revenue) as total_revenue,
    COUNT(*) as days_analyzed
FROM PARK_PERFORMANCE 
WHERE park_id = 'UDX-FL' 
AND performance_date >= DATEADD(day, -30, CURRENT_DATE());

-- =====================================================
-- EXERCISE 3: Grouping and Comparisons
-- =====================================================

-- 3.1: Revenue by Ticket Type
-- Generate GROUP BY analysis for ticket types
SELECT 
    'Revenue by Ticket Type Analysis' as exercise_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Create SQL to answer: "What is the total revenue and average transaction value for each ticket type?" ',
            'Use SALES_TRANSACTIONS table, group by ticket_type, include count of transactions. ',
            'Order by total revenue descending. Use clear column aliases.'
        )
    ) as ai_sql_generation;

-- Expected output example:
SELECT 
    ticket_type,
    SUM(total_revenue) as total_revenue,
    ROUND(AVG(total_revenue), 2) as avg_transaction_value,
    COUNT(*) as transaction_count
FROM SALES_TRANSACTIONS
GROUP BY ticket_type
ORDER BY total_revenue DESC;

-- 3.2: Customer Segmentation Analysis
-- Generate demographic grouping queries
SELECT 
    'Customer Demographics Grouping' as analysis_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Convert this question to SQL: "Show me customer count and average lifetime revenue by age group and loyalty tier" ',
            'Use CUSTOMERS table, group by age_group and loyalty_tier. ',
            'Include count and average revenue calculations with proper aliases.'
        )
    ) as demographic_sql;

-- Manual example:
SELECT 
    age_group,
    loyalty_tier,
    COUNT(*) as customer_count,
    ROUND(AVG(total_lifetime_revenue), 2) as avg_lifetime_revenue
FROM CUSTOMERS
GROUP BY age_group, loyalty_tier
ORDER BY age_group, loyalty_tier;

-- =====================================================
-- EXERCISE 4: Time-Based Analysis
-- =====================================================

-- 4.1: Monthly Revenue Trends
-- Generate time-series analysis SQL
SELECT 
    'Monthly Revenue Trends' as exercise_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Create SQL for: "Show me monthly revenue trends for the last 12 months" ',
            'Use SALES_TRANSACTIONS table, extract month and year from transaction_date. ',
            'Group by month/year, sum revenue, order chronologically. Use DATE_TRUNC function.'
        )
    ) as time_series_sql;

-- Expected result pattern:
SELECT 
    DATE_TRUNC('month', transaction_date) as revenue_month,
    SUM(total_revenue) as monthly_revenue,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM SALES_TRANSACTIONS
WHERE transaction_date >= DATEADD(month, -12, CURRENT_DATE())
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY revenue_month;

-- 4.2: Seasonal Analysis
-- Generate seasonal performance queries
SELECT 
    'Seasonal Performance Analysis' as exercise_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Convert to SQL: "Compare average daily attendance and revenue by season across all parks" ',
            'Use PARK_PERFORMANCE table. Define seasons by month: Winter (12,1,2), Spring (3,4,5), Summer (6,7,8), Fall (9,10,11). ',
            'Group by season, calculate averages, include park count.'
        )
    ) as seasonal_analysis_sql;

-- =====================================================
-- EXERCISE 5: Multi-Table Joins and Complex Analysis
-- =====================================================

-- 5.1: Customer Transaction History
-- Generate JOIN queries combining customer and transaction data
SELECT 
    'Customer Transaction Join Analysis' as exercise_title,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Create SQL for: "Show me customer details with their total spent, transaction count, and last purchase date" ',
            'Join CUSTOMERS and SALES_TRANSACTIONS tables on customer_id. ',
            'Include first_name, last_name, loyalty_tier from customers and aggregated transaction data. ',
            'Group by customer details and order by total spent descending.'
        )
    ) as customer_join_sql;

-- Expected pattern:
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.loyalty_tier,
    SUM(s.total_revenue) as total_spent,
    COUNT(s.transaction_id) as transaction_count,
    MAX(s.transaction_date) as last_purchase_date
FROM CUSTOMERS c
JOIN SALES_TRANSACTIONS s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.loyalty_tier
ORDER BY total_spent DESC;

-- 5.2: Park Performance with Weather Correlation
-- Generate complex analysis combining operational and environmental data
SELECT 
    'Weather Impact Analysis' as complex_analysis,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Convert this question: "How does weather condition affect daily attendance and guest satisfaction by park?" ',
            'Use PARK_PERFORMANCE table with weather_condition, daily_attendance, and average_guest_satisfaction. ',
            'Group by park_id and weather_condition, calculate averages, include record count for statistical significance.'
        )
    ) as weather_impact_sql;

-- =====================================================
-- EXERCISE 6: Advanced Business Metrics
-- =====================================================

-- 6.1: Customer Lifetime Value Analysis
-- Generate sophisticated customer analytics
SELECT 
    'Customer Lifetime Value Calculation' as advanced_exercise,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        CONCAT(
            'Create SQL for: "Calculate customer lifetime value metrics: total revenue, average order value, purchase frequency, and days since last purchase" ',
            'Join CUSTOMERS and SALES_TRANSACTIONS. Calculate: total spent, avg transaction amount, transaction frequency, days since last purchase. ',
            'Include only customers with at least 2 transactions. Order by total spent.'
        )
    ) as clv_calculation_sql;

-- 6.2: Marketing Campaign ROI Analysis
-- Generate marketing effectiveness queries
SELECT 
    'Marketing Campaign ROI Analysis' as marketing_exercise,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Convert to SQL: "Show me marketing campaign performance: budget spent, revenue attributed, ROI, and conversion rate by channel" ',
            'Use MARKETING_CAMPAIGNS table with budget_spent, revenue_attributed, conversions, and clicks columns. ',
            'Calculate ROI as revenue/budget, conversion rate as conversions/clicks. Group by channel.'
        )
    ) as marketing_roi_sql;

-- =====================================================
-- EXERCISE 7: Conversational AI Context
-- =====================================================

-- 7.1: Follow-up Questions with Context
-- Simulate a conversation with context awareness
WITH first_question AS (
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'Convert to SQL: "What are our top 5 performing parks by total revenue?" Use PARK_PERFORMANCE table, sum daily_revenue by park_id, order descending, limit 5.'
    ) as initial_query
),
context_setup AS (
    SELECT 
        'session_001' as session_id,
        'user_001' as user_id,
        1 as question_sequence,
        'What are our top 5 performing parks by total revenue?' as user_question,
        initial_query as generated_sql
    FROM first_question
)
-- Now ask a follow-up question with context
SELECT 
    'Conversational Follow-up Question' as exercise_type,
    SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        CONCAT(
            'Previous context: User asked "What are our top 5 performing parks by total revenue?" ',
            'Now they ask: "Show me the guest satisfaction scores for those same parks" ',
            'Generate SQL to get average guest satisfaction for the top 5 revenue parks. ',
            'Use PARK_PERFORMANCE table with revenue and satisfaction data.'
        )
    ) as followup_sql
FROM context_setup;

-- =====================================================
-- EXERCISE VALIDATION AND TESTING
-- =====================================================

-- Test the AI-generated SQL functions we created in setup
SELECT 
    'Testing Custom NL2SQL Functions' as test_type,
    extract_query_intent('Show me the top 10 customers by revenue') as intent_analysis;

-- Test business SQL generation function
SELECT 
    'Custom Business SQL Generation Test' as test_type,
    generate_business_sql('What is the average guest satisfaction by park?') as business_sql;

-- =====================================================
-- EXERCISE COMPLETION SUMMARY
-- =====================================================

-- Summary of NL2SQL capabilities demonstrated
SELECT 
    'Lab 03 Completion Summary' as lab_status,
    'Congratulations! You have successfully learned:' as achievements,
    '✅ Basic natural language to SQL translation' as achievement_1,
    '✅ Business context integration in AI prompts' as achievement_2,
    '✅ Query pattern recognition and generation' as achievement_3,
    '✅ Multi-table join query creation' as achievement_4,
    '✅ Time-series and trend analysis queries' as achievement_5,
    '✅ Complex business metrics calculation' as achievement_6,
    'Ready for Lab 04: Advanced Query Translation!' as next_step;

-- Final validation query
SELECT 
    'NL2SQL Translation Skills Acquired' as validation_result,
    CURRENT_TIMESTAMP() as completion_time,
    USER() as completed_by,
    'You can now help business users query data with natural language!' as business_impact; 