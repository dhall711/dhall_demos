# UDX NLP2SQL Hackathon: Instructor Guide

## Welcome to Teaching the Future of Business Intelligence!

This comprehensive instructor guide provides everything you need to successfully deliver the UDX Natural Language to SQL Hackathon. Your students will build a revolutionary system that transforms how business users interact with data, moving from complex SQL to natural language queries.

### Instructor Objectives

By the end of this hackathon, your students will have:
• Mastered Snowflake Cortex AI for natural language processing
• Built production-ready NLP2SQL translation systems
• Gained hands-on experience with conversational AI interfaces
• Developed enterprise-grade analytics solutions with governance
• Acquired practical skills in AI-assisted business intelligence

### Teaching Timeline: 5-Hour Intensive Program

• **Lab 01**: Environment Setup (50 minutes) - Foundation critical for success

• **Lab 02**: Basic NLP2SQL (60 minutes) - Core concept mastery

• **Lab 03**: Advanced Features (90 minutes) - Professional development

• **Lab 04**: Final Challenge (90 minutes) - Real-world application

• **Lab 05**: Agents & Intelligence (60 minutes) - Cutting-edge AI


### Instructor Success Framework

**Pre-Hackathon Setup:** Environment testing, solution validation, troubleshooting preparation

**Teaching Strategy:** Demonstrate first, guide practice, independent work, collaborative review

**Support Framework:** Real-time monitoring, proactive assistance, peer learning

---

## PRE-HACKATHON INSTRUCTOR SETUP

### Technical Prerequisites Verification

#### Snowflake Account Requirements
• **Account Type**: Enterprise or Business Critical preferred
• **Cortex AI Access**: Must be enabled (contact Snowflake if needed)
• **User Roles**: ACCOUNTADMIN or sufficient privileges for students
• **Warehouse Credits**: Budget for 5+ hours of XS warehouse usage per student
• **Regional Availability**: Cortex AI must be available in your region

**🎯 INSTRUCTOR TIP**: Test Cortex AI availability 48 hours before the hackathon:
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Hello, AI!') as cortex_test;
```

#### Environment Validation Checklist
□ All SQL scripts execute without errors
□ Sample data loads successfully (500K+ records)
□ Cortex AI functions respond correctly
□ Student accounts have appropriate permissions
□ Warehouse auto-suspend is configured appropriately
□ Network connectivity is stable for all participants

### Student Account Management

#### Recommended Account Setup
• **Individual Accounts**: Preferred for hands-on learning
• **Shared Account Option**: Use different databases per student if needed
• **Role Strategy**: Create student-specific roles with controlled permissions
• **Resource Management**: Set warehouse auto-suspend to 1 minute

**Sample Student Account Setup:**
```sql
-- Create student role and user (run as ACCOUNTADMIN)
CREATE ROLE HACKATHON_STUDENT;
CREATE USER student_01 PASSWORD='TempPass123!' DEFAULT_ROLE=HACKATHON_STUDENT;

-- Grant necessary permissions
GRANT ROLE HACKATHON_STUDENT TO USER student_01;
GRANT USAGE ON WAREHOUSE UDX_ANALYTICS_WAREHOUSE TO ROLE HACKATHON_STUDENT;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE HACKATHON_STUDENT;
```

### Solution Environment Preparation

#### Master Solution Setup
1. **Complete Lab Walkthrough**: Execute all labs start-to-finish
2. **Solution Documentation**: Capture expected outputs for each exercise
3. **Performance Baselines**: Record query execution times
4. **Error Catalog**: Document common issues and solutions

**🖼️ SCREENSHOT PLACEHOLDER: Instructor Solution Environment**
*Caption: Instructor's Snowsight dashboard showing completed solutions for all labs with organized worksheets, successful results, and performance metrics visible.*

---

## LAB 01: FOUNDATION SETUP - INSTRUCTOR GUIDE (50 minutes)

### Teaching Objectives
• Ensure all students have working Snowflake environments
• Validate Cortex AI accessibility across all accounts
• Establish proper context management habits
• Build confidence with Snowsight interface

### Pre-Lab Instructor Checklist
□ Test setup.sql in clean environment
□ Verify load_business_data.sql creates expected row counts
□ Confirm all AI functions compile successfully
□ Prepare troubleshooting resources

### Lab 01 Teaching Flow

#### Opening Demonstration (10 minutes)

**🎯 INSTRUCTOR DEMO**: Live walkthrough of Snowsight interface

**🖼️ SCREENSHOT PLACEHOLDER: Instructor Demo Setup**
*Caption: Instructor screen showing Snowsight interface with clear navigation arrows, callouts for key features, and the complete setup process ready to demonstrate.*


**Key Teaching Points:**

• Emphasize context importance early and often

• Show keyboard shortcuts (Ctrl+Enter, Ctrl+S)

• Demonstrate both full script and section-by-section execution

• Point out common UI elements students will use frequently

#### Guided Practice Session (25 minutes)

**Student Activity**: Setup script execution with instructor monitoring

**🎯 INSTRUCTOR STRATEGY**: Circulate during execution, help with common issues

**Expected Timeline:**
- Minutes 0-5: Worksheet creation and script copying
- Minutes 5-15: Script execution (this is where most issues occur)
- Minutes 15-20: Validation and troubleshooting
- Minutes 20-25: Data loading completion and verification

### Common Setup Issues & Solutions

#### Issue #1: Cortex AI Not Available
**Symptoms:** Error message "Function SNOWFLAKE.CORTEX.COMPLETE does not exist"
**Solution:**
```sql
-- Verify Cortex availability in your region
SELECT CURRENT_REGION() as current_region;

-- If error persists, contact Snowflake support for Cortex enablement
```
**🎯 INSTRUCTOR ACTION**: Have backup exercises ready that don't require Cortex

#### Issue #2: Permissions Errors
**Symptoms:** "Insufficient privileges" when creating warehouse/database
**Solution:**
```sql
-- Check current role
SELECT CURRENT_ROLE();

-- Switch to appropriate role
USE ROLE ACCOUNTADMIN;
-- OR
USE ROLE SYSADMIN;
```

#### Issue #3: Warehouse Creation Fails
**Symptoms:** Timeout or resource limit exceeded
**Solution:**
```sql
-- Try smaller warehouse size
CREATE WAREHOUSE UDX_ANALYTICS_WAREHOUSE 
WITH WAREHOUSE_SIZE = 'XSMALL'
     AUTO_SUSPEND = 60;
```

### Lab 01 Success Validation

#### Expected Results Verification

**🖼️ SCREENSHOT PLACEHOLDER: Lab 01 Success Indicators**
*Caption: Snowsight showing all Lab 01 success indicators - correct context in dropdowns, successful table creation results, working Cortex test, and proper data row counts.*

**Validation Queries for Instructors:**
```sql
-- Verify environment setup
SELECT 
    COUNT(*) as customer_count 
FROM UDX_NL2SQL.BUSINESS_ANALYTICS.CUSTOMERS;
-- Expected: 50,000 rows

SELECT 
    COUNT(*) as transaction_count 
FROM UDX_NL2SQL.BUSINESS_ANALYTICS.SALES_TRANSACTIONS;
-- Expected: 500,000+ rows

-- Test AI functionality
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b', 
    'Convert to SQL: "Count total customers"'
) as ai_response;
-- Expected: Valid SQL response
```

### Assessment Criteria - Lab 01
□ **Environment (25%)**: Warehouse, database, and schema created successfully
□ **Data Loading (25%)**: All tables populated with expected row counts  
□ **AI Functions (25%)**: Cortex AI responding correctly
□ **Context Management (25%)**: Student demonstrates proper context switching

---

## LAB 02: BASIC NLP2SQL - INSTRUCTOR GUIDE (60 minutes)

### Teaching Objectives
• Students master natural language to SQL translation patterns
• Develop effective prompt engineering skills
• Build confidence with business scenario analysis
• Establish query validation and results interpretation habits

### Lab 02 Teaching Strategy

#### Concept Introduction (15 minutes)

**🎯 INSTRUCTOR DEMO**: Live NLP2SQL translation example


**Teaching Flow:** Show Question → Craft Prompt → Execute AI Query → Review Generated SQL → Run Generated Query → Validate Results

**Demo Script for Instructors:**

"Let's start with a simple executive question: 'What is our total revenue this year?'"

```sql
-- INSTRUCTOR DEMO: Step-by-step NLP2SQL
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'You are a SQL expert for UDX theme parks. Convert this to Snowflake SQL: 
    "What is our total revenue this year?" 
    Use SALES_TRANSACTIONS table with transaction_date and total_revenue columns.
    Filter for current year (2024).
    Return only SQL code.'
) as generated_sql;
```

**🖼️ SCREENSHOT PLACEHOLDER: Instructor Demo Results**
*Caption: Instructor's screen showing the demo query execution with the AI-generated SQL clearly visible and properly formatted. Students should see both the prompt and the clean SQL response.*

#### Exercise Solutions & Expected Results

#### Exercise 1 Solutions: Simple Business Questions

**Question**: "What is our total revenue this year?"
**Expected AI-Generated SQL**:
```sql
SELECT SUM(total_revenue) as total_revenue_2024
FROM SALES_TRANSACTIONS 
WHERE YEAR(transaction_date) = 2024;
```
**Expected Result**: Approximately $45,000,000 - $55,000,000

**Question**: "Who are our top 10 customers by lifetime value?"
**Expected AI-Generated SQL**:
```sql
SELECT 
    c.customer_id,
    c.full_name,
    SUM(s.total_revenue) as lifetime_value
FROM CUSTOMERS c
JOIN SALES_TRANSACTIONS s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY lifetime_value DESC
LIMIT 10;
```
**Expected Results**: Top customer should have $15,000+ lifetime value

#### Exercise 2 Solutions: Filtering and Business Logic

**Question**: "How many VIP customers do we have and what is their average revenue?"
**Expected AI-Generated SQL**:
```sql
SELECT 
    COUNT(*) as vip_customer_count,
    AVG(lifetime_value) as avg_vip_revenue
FROM (
    SELECT 
        c.customer_id,
        SUM(s.total_revenue) as lifetime_value
    FROM CUSTOMERS c
    JOIN SALES_TRANSACTIONS s ON c.customer_id = s.customer_id
    WHERE c.is_vip = TRUE
    GROUP BY c.customer_id
);
```
**Expected Results**: ~2,500 VIP customers, ~$2,800 average revenue

### Advanced Teaching Techniques

#### Prompt Engineering Masterclass

**🎯 INSTRUCTOR TEACHING MOMENT**: Show prompt evolution

**Bad Prompt Example:**
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'revenue by park') as bad_example;
```

**Good Prompt Template:**
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'You are a SQL expert for UDX theme parks. Convert this business question to Snowflake SQL: 
    
    QUESTION: "[SPECIFIC BUSINESS QUESTION]"
    
    CONTEXT:
    - Use table: [TABLE_NAME]
    - Key columns: [COLUMN_LIST]
    - Business rules: [ANY_CONSTRAINTS]
    - Output format: [REQUIREMENTS]
    
    Return only valid Snowflake SQL code.'
) as improved_sql;
```

#### Common Student Challenges & Instructor Responses

##### Challenge 1: "The AI generated wrong SQL"
**Instructor Response Strategy:**
1. **Validate the prompt**: "Let's look at how we phrased the question"
2. **Check business logic**: "Does this match what we're actually asking?"
3. **Iterate together**: "How can we make the prompt more specific?"

**🖼️ SCREENSHOT PLACEHOLDER: Prompt Refinement Process**
*Caption: Split screen showing original vague prompt with poor results, then refined prompt with accurate SQL generation. Clear before/after comparison for teaching.*

##### Challenge 2: "I don't understand the generated SQL"
**Instructor Response Strategy:**
1. **Break down the query**: Walk through each part step-by-step
2. **Connect to business logic**: Relate SQL components to business requirements
3. **Encourage experimentation**: "Try modifying one part and see what changes"

#### Real-Time Assessment Techniques

**🎯 INSTRUCTOR MONITORING**: Watch for these success indicators

□ Students asking specific questions about business logic
□ Iterative prompt refinement without prompting
□ Successful query modification and re-execution
□ Peer collaboration and knowledge sharing
□ Proactive result validation and interpretation

### Exercise Progression Monitoring

#### 15-Minute Check-in Questions:
1. "Has everyone generated at least one working SQL query?"
2. "What's the most interesting result you've found so far?"
3. "Any patterns you're noticing in effective prompts?"

#### 30-Minute Milestone Assessment:
□ All students completed Exercise 1 successfully
□ At least 80% completed Exercise 2
□ Students demonstrate prompt refinement skills
□ Most students interpreting results correctly

#### 45-Minute Advanced Guidance:
- Challenge fast learners with complex multi-table queries
- Provide additional scaffolding for struggling students
- Introduce bonus exercises for early finishers

### Troubleshooting Guide - Labs 02-03

#### Issue: AI Returns Non-SQL Response
**Cause**: Prompt lacks clear instruction to return only SQL
**Solution**: Add "Return only valid Snowflake SQL code" to prompt

#### Issue: Generated SQL Has Syntax Errors
**Cause**: AI model confusion or incomplete context
**Solution**: 
```sql
-- More specific prompt template
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-70b',  -- Try different model
    'Generate syntactically correct Snowflake SQL for: [QUESTION]
     Schema: UDX_NL2SQL.BUSINESS_ANALYTICS
     Return executable SQL only.'
) as corrected_sql;
```

#### Issue: Results Don't Make Business Sense
**Instructor Debugging Process:**
1. Check table joins are correct
2. Verify date filters are appropriate
3. Confirm aggregation logic matches business question
4. Validate data quality in source tables

### Lab 02 Success Metrics

**Individual Student Assessment:**
□ **Query Generation (30%)**: Successfully generates working SQL from natural language
□ **Prompt Engineering (25%)**: Demonstrates iterative prompt refinement
□ **Result Validation (25%)**: Correctly interprets and validates query results  
□ **Business Application (20%)**: Connects technical results to business insights

**Class-Level Success Indicators:**
□ 90%+ students complete all basic exercises
□ 75%+ students successfully modify generated queries
□ 60%+ students create original business questions and solutions
□ High engagement and collaborative problem-solving

---

## LAB 03: ADVANCED FEATURES - INSTRUCTOR GUIDE (90 minutes)

### Teaching Objectives
• Guide students through complex multi-step business logic
• Facilitate conversational context management implementation
• Support creation of reusable query patterns and templates
• Ensure robust enterprise-grade error handling

### Advanced Lab Teaching Framework

**Part A: Complex Business Logic** - Multi-step calculations, advanced aggregations, window functions, performance optimization

**Part B: Context & Conversation** - Session state management, multi-turn dialogue, query history integration, context-aware responses

**Part C: Enterprise Features** - Query templates, error recovery systems, performance monitoring, security integration

### Part A: Complex Business Logic Solutions

#### Customer Lifetime Value Calculation Solution

**Business Requirement**: Calculate sophisticated CLV with recency, frequency, and monetary analysis

**Complete Solution**:
```sql
CREATE OR REPLACE FUNCTION calculate_customer_clv()
RETURNS TABLE(
    customer_id STRING, 
    clv_score NUMBER(10,2), 
    segment STRING,
    recency_score NUMBER,
    frequency_score NUMBER,
    monetary_score NUMBER
)
AS
$$
WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.full_name,
        DATEDIFF('days', MAX(s.transaction_date), CURRENT_DATE()) as days_since_last_purchase,
        COUNT(DISTINCT s.transaction_id) as transaction_frequency,
        SUM(s.total_revenue) as total_monetary_value,
        AVG(s.total_revenue) as avg_transaction_value
    FROM customers c
    JOIN sales_transactions s ON c.customer_id = s.customer_id
    GROUP BY c.customer_id, c.full_name
),
rfm_scores AS (
    SELECT *,
        -- Recency Score (lower days = higher score)
        CASE 
            WHEN days_since_last_purchase <= 30 THEN 5
            WHEN days_since_last_purchase <= 90 THEN 4
            WHEN days_since_last_purchase <= 180 THEN 3
            WHEN days_since_last_purchase <= 365 THEN 2
            ELSE 1
        END as recency_score,
        
        -- Frequency Score
        NTILE(5) OVER (ORDER BY transaction_frequency) as frequency_score,
        
        -- Monetary Score  
        NTILE(5) OVER (ORDER BY total_monetary_value) as monetary_score
    FROM customer_metrics
)
SELECT 
    customer_id,
    ROUND(
        (recency_score * 0.3 + frequency_score * 0.3 + monetary_score * 0.4) * 
        total_monetary_value / 100, 2
    ) as clv_score,
    CASE 
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal Customers'
        WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New Customers'
        WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'At Risk'
        ELSE 'Hibernating'
    END as segment,
    recency_score,
    frequency_score,
    monetary_score
FROM rfm_scores
ORDER BY clv_score DESC
$$;
```

**🖼️ SCREENSHOT PLACEHOLDER: Complex CLV Function Results**
*Caption: Snowsight showing the CLV function execution results with customer segments, scores, and the detailed RFM analysis clearly visible in a well-formatted table.*

**Expected Results:**
- Champions segment: ~500 customers, CLV $3,000+
- Loyal Customers: ~2,000 customers, CLV $1,500-$3,000
- At Risk customers: ~800 customers requiring intervention

#### Advanced Time-Series Analysis Solution

**Business Requirement**: Seasonal trend analysis with growth calculations

```sql
-- Advanced seasonal revenue analysis with growth metrics
WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', transaction_date) as month,
        park_id,
        SUM(total_revenue) as monthly_revenue,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(*) as transaction_count
    FROM sales_transactions
    WHERE transaction_date >= '2023-01-01'
    GROUP BY 1, 2
),
revenue_with_growth AS (
    SELECT *,
        LAG(monthly_revenue, 1) OVER (PARTITION BY park_id ORDER BY month) as prev_month_revenue,
        LAG(monthly_revenue, 12) OVER (PARTITION BY park_id ORDER BY month) as prev_year_revenue,
        
        -- Month-over-month growth
        ROUND(
            ((monthly_revenue - LAG(monthly_revenue, 1) OVER (PARTITION BY park_id ORDER BY month)) / 
             LAG(monthly_revenue, 1) OVER (PARTITION BY park_id ORDER BY month)) * 100, 2
        ) as mom_growth_pct,
        
        -- Year-over-year growth
        ROUND(
            ((monthly_revenue - LAG(monthly_revenue, 12) OVER (PARTITION BY park_id ORDER BY month)) / 
             LAG(monthly_revenue, 12) OVER (PARTITION BY park_id ORDER BY month)) * 100, 2
        ) as yoy_growth_pct,
        
        -- 3-month moving average
        ROUND(
            AVG(monthly_revenue) OVER (
                PARTITION BY park_id 
                ORDER BY month 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 2
        ) as three_month_avg
    FROM monthly_revenue
)
SELECT 
    month,
    park_id,
    monthly_revenue,
    mom_growth_pct,
    yoy_growth_pct,
    three_month_avg,
    CASE 
        WHEN mom_growth_pct > 10 THEN 'Strong Growth'
        WHEN mom_growth_pct > 0 THEN 'Moderate Growth'
        WHEN mom_growth_pct > -5 THEN 'Slight Decline'
        ELSE 'Concerning Decline'
    END as growth_category
FROM revenue_with_growth
WHERE month >= '2023-02-01'  -- Exclude first month due to LAG
ORDER BY park_id, month;
```

### Part B: Conversational Context Solutions

#### Multi-Turn Conversation Implementation

**🎯 INSTRUCTOR FOCUS**: This is where students often struggle - provide extra support

```sql
CREATE OR REPLACE PROCEDURE handle_conversation(
    user_question STRING,
    conversation_history VARIANT
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    context_prompt STRING;
    sql_query STRING;
    final_response STRING;
BEGIN
    -- Build context from conversation history
    context_prompt := 'You are a UDX theme park analytics assistant. 
    
    Previous conversation context: ' || IFNULL(conversation_history::STRING, 'None') || '
    
    Current question: ' || user_question || '
    
    Generate appropriate Snowflake SQL considering the conversation context.
    Available tables: CUSTOMERS, SALES_TRANSACTIONS, PARK_PERFORMANCE, ATTRACTION_ANALYTICS
    
    Return only SQL code.';
    
    -- Generate SQL using Cortex
    SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', context_prompt) INTO sql_query;
    
    -- Execute and format response (simplified for demo)
    final_response := 'Generated SQL: ' || sql_query;
    
    RETURN final_response;
END;
$$;
```

**Test Conversation Flow**:
```sql
-- Turn 1
CALL handle_conversation('Show me total revenue by park', NULL);

-- Turn 2 (with context)
CALL handle_conversation(
    'Now show me which parks had the highest growth', 
    PARSE_JSON('{"previous_query": "revenue_by_park", "context": "analyzing park performance"}')
);
```

### Advanced Troubleshooting Scenarios

#### Performance Issues in Complex Queries

**🎯 INSTRUCTOR GUIDANCE**: When students encounter slow queries

**Issue**: Student's CLV query takes 5+ minutes
**Diagnostic Process**:
```sql
-- Check query profile in Snowsight
-- Look for these performance killers:
-- 1. Missing warehouse resize
-- 2. Cartesian joins
-- 3. Inefficient window functions

-- Quick fix: Add query hints
SELECT /*+ USE_CACHED_RESULT */ 
    customer_id,
    clv_score
FROM TABLE(calculate_customer_clv())
LIMIT 100;
```

#### Memory Errors with Large Datasets

**Issue**: "Memory limit exceeded" errors
**Instructor Solution Strategy**:
```sql
-- Break down large operations
CREATE TEMPORARY TABLE customer_summary AS
SELECT 
    customer_id,
    SUM(total_revenue) as lifetime_value
FROM sales_transactions
GROUP BY customer_id;

-- Then perform complex calculations on smaller dataset
SELECT * FROM customer_summary WHERE lifetime_value > 5000;
```

### Lab Assessment Framework - Advanced Labs

#### Part A Assessment Criteria
□ **Complex Logic (40%)**: Successfully implements multi-step business calculations
□ **Code Quality (30%)**: Functions are well-structured and reusable
□ **Performance (20%)**: Queries execute efficiently 
□ **Business Value (10%)**: Results provide actionable business insights

#### Part B Assessment Criteria  
□ **Context Management (35%)**: Maintains conversation state effectively
□ **Multi-turn Logic (30%)**: Handles follow-up questions appropriately
□ **Integration (25%)**: Smoothly combines with existing query patterns
□ **User Experience (10%)**: Creates intuitive conversational flow

#### Part C Assessment Criteria
□ **Error Handling (40%)**: Robust exception management and recovery
□ **Template Design (30%)**: Reusable, maintainable query patterns
□ **Enterprise Features (20%)**: Security, monitoring, and governance
□ **Documentation (10%)**: Clear code comments and usage instructions

---

## LAB 04: FINAL CHALLENGE - INSTRUCTOR GUIDE (90 minutes)

### Challenge Overview & Assessment Strategy

The Final Challenge tests students' ability to integrate all learned concepts into a comprehensive business intelligence solution. Students choose from three executive scenarios, each requiring different technical approaches.

### Executive Challenge Scenarios

#### Scenario A: Executive Dashboard Solution

**Business Context**: CEO needs real-time visibility into park performance
**Technical Requirements**: 
- Multi-park revenue comparisons
- Customer satisfaction integration
- Predictive trend analysis
- Executive-friendly visualizations

**Complete Solution Template**:
```sql
-- Executive Dashboard: Comprehensive Park Performance
CREATE OR REPLACE VIEW executive_dashboard AS
WITH park_performance AS (
    SELECT 
        p.park_name,
        DATE_TRUNC('month', s.transaction_date) as month,
        SUM(s.total_revenue) as monthly_revenue,
        COUNT(DISTINCT s.customer_id) as unique_visitors,
        AVG(pf.guest_satisfaction_score) as avg_satisfaction,
        COUNT(s.transaction_id) as total_transactions
    FROM sales_transactions s
    JOIN park_performance pf ON s.park_id = pf.park_id 
        AND DATE_TRUNC('day', s.transaction_date) = pf.performance_date
    JOIN (
        SELECT DISTINCT park_id, 
        CASE park_id
            WHEN 'PARK001' THEN 'Universal Studios Florida'
            WHEN 'PARK002' THEN 'Islands of Adventure'  
            WHEN 'PARK003' THEN 'Universal Studios Atlanta'
            WHEN 'PARK004' THEN 'Universal Studios Houston'
            WHEN 'PARK005' THEN 'Universal Studios Phoenix'
            WHEN 'PARK006' THEN 'Universal Studios Hollywood'
        END as park_name
        FROM sales_transactions
    ) p ON s.park_id = p.park_id
    WHERE s.transaction_date >= DATEADD('month', -13, CURRENT_DATE())
    GROUP BY 1, 2
),
growth_metrics AS (
    SELECT *,
        LAG(monthly_revenue, 1) OVER (PARTITION BY park_name ORDER BY month) as prev_month_revenue,
        LAG(monthly_revenue, 12) OVER (PARTITION BY park_name ORDER BY month) as prev_year_revenue,
        
        ROUND(
            ((monthly_revenue - LAG(monthly_revenue, 1) OVER (PARTITION BY park_name ORDER BY month)) / 
             NULLIF(LAG(monthly_revenue, 1) OVER (PARTITION BY park_name ORDER BY month), 0)) * 100, 2
        ) as mom_growth_pct,
        
        ROUND(
            ((monthly_revenue - LAG(monthly_revenue, 12) OVER (PARTITION BY park_name ORDER BY month)) / 
             NULLIF(LAG(monthly_revenue, 12) OVER (PARTITION BY park_name ORDER BY month), 0)) * 100, 2
        ) as yoy_growth_pct
    FROM park_performance
)
SELECT 
    park_name,
    month,
    monthly_revenue,
    unique_visitors,
    ROUND(monthly_revenue / unique_visitors, 2) as revenue_per_visitor,
    avg_satisfaction,
    mom_growth_pct,
    yoy_growth_pct,
    CASE 
        WHEN yoy_growth_pct > 15 THEN '🚀 Exceptional'
        WHEN yoy_growth_pct > 5 THEN '📈 Strong'
        WHEN yoy_growth_pct > 0 THEN '✅ Positive'
        WHEN yoy_growth_pct > -5 THEN '⚠️ Caution'
        ELSE '🚨 Critical'
    END as performance_status
FROM growth_metrics
WHERE month >= DATEADD('month', -12, CURRENT_DATE())
ORDER BY park_name, month DESC;
```

**🖼️ SCREENSHOT PLACEHOLDER: Executive Dashboard Results**
*Caption: Comprehensive executive dashboard showing multi-park performance metrics, growth indicators, and status categories with clear visual hierarchy and executive-friendly formatting.*

#### Scenario B: Operations Analytics Solution

**Business Context**: Operations team needs daily performance optimization insights
**Technical Requirements**:
- Real-time capacity analysis  
- Staff efficiency metrics
- Attraction performance correlation
- Operational bottleneck identification

**Complete Solution**:
```sql
-- Operations Analytics: Daily Performance Optimization
CREATE OR REPLACE PROCEDURE daily_operations_report(report_date DATE)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    capacity_analysis STRING;
    efficiency_metrics STRING;
    bottleneck_report STRING;
    recommendations STRING;
BEGIN
    -- Capacity Analysis
    CREATE OR REPLACE TEMPORARY TABLE capacity_metrics AS
    WITH hourly_capacity AS (
        SELECT 
            park_id,
            DATE_TRUNC('hour', transaction_date) as hour_bucket,
            COUNT(*) as transactions_per_hour,
            COUNT(DISTINCT customer_id) as unique_visitors_per_hour,
            SUM(total_revenue) as hourly_revenue
        FROM sales_transactions 
        WHERE DATE(transaction_date) = report_date
        GROUP BY park_id, hour_bucket
    ),
    capacity_with_limits AS (
        SELECT *,
            CASE park_id
                WHEN 'PARK001' THEN 2000  -- Universal Studios Florida capacity/hour
                WHEN 'PARK002' THEN 1500  -- Islands of Adventure
                WHEN 'PARK003' THEN 1800  -- Universal Studios Atlanta
                WHEN 'PARK004' THEN 1600  -- Universal Studios Houston
                WHEN 'PARK005' THEN 1400  -- Universal Studios Phoenix
                WHEN 'PARK006' THEN 1700  -- Universal Studios Hollywood
            END as max_capacity_per_hour,
            
            ROUND((unique_visitors_per_hour / 
                CASE park_id
                    WHEN 'PARK001' THEN 2000.0
                    WHEN 'PARK002' THEN 1500.0  
                    WHEN 'PARK003' THEN 1800.0
                    WHEN 'PARK004' THEN 1600.0
                    WHEN 'PARK005' THEN 1400.0
                    WHEN 'PARK006' THEN 1700.0
                END) * 100, 2) as capacity_utilization_pct
        FROM hourly_capacity
    )
    SELECT 
        park_id,
        EXTRACT(hour FROM hour_bucket) as hour_of_day,
        unique_visitors_per_hour,
        capacity_utilization_pct,
        CASE 
            WHEN capacity_utilization_pct > 90 THEN 'OVERCAPACITY'
            WHEN capacity_utilization_pct > 75 THEN 'HIGH_UTILIZATION' 
            WHEN capacity_utilization_pct > 50 THEN 'MODERATE_UTILIZATION'
            ELSE 'LOW_UTILIZATION'
        END as capacity_status,
        hourly_revenue
    FROM capacity_with_limits
    ORDER BY park_id, hour_of_day;
    
    -- Staff Efficiency Analysis
    CREATE OR REPLACE TEMPORARY TABLE staff_efficiency AS
    WITH transaction_efficiency AS (
        SELECT 
            park_id,
            EXTRACT(hour FROM transaction_date) as hour_of_day,
            COUNT(*) as total_transactions,
            SUM(total_revenue) as total_revenue,
            AVG(total_revenue) as avg_transaction_value,
            
            -- Efficiency metrics (transactions per estimated staff)
            ROUND(COUNT(*) / 
                CASE 
                    WHEN EXTRACT(hour FROM transaction_date) BETWEEN 9 AND 17 THEN 50 -- Peak staff
                    WHEN EXTRACT(hour FROM transaction_date) BETWEEN 18 AND 21 THEN 40 -- Evening staff
                    ELSE 20 -- Off-peak staff
                END, 2) as transactions_per_staff_member
        FROM sales_transactions
        WHERE DATE(transaction_date) = report_date
        GROUP BY park_id, hour_of_day
    )
    SELECT 
        park_id,
        hour_of_day,
        total_transactions,
        transactions_per_staff_member,
        CASE 
            WHEN transactions_per_staff_member > 25 THEN 'HIGH_EFFICIENCY'
            WHEN transactions_per_staff_member > 15 THEN 'MODERATE_EFFICIENCY'
            ELSE 'LOW_EFFICIENCY'
        END as efficiency_rating,
        total_revenue
    FROM transaction_efficiency
    ORDER BY park_id, hour_of_day;
    
    -- Generate summary recommendations
    SELECT 
        'Operations Report Generated Successfully - Check capacity_metrics and staff_efficiency temp tables' 
    INTO recommendations;
    
    RETURN recommendations;
END;
$$;
```

### Teaching Strategy for Final Challenge

#### Time Management Framework

**🎯 INSTRUCTOR TIMELINE**:

**Minutes 0-15: Challenge Introduction**
- Present all three scenarios with business context
- Allow students to choose based on interests/strengths
- Form small groups (2-3 students) for collaboration

**Minutes 15-60: Development Phase**
- Active instructor circulation and support
- Mini-checkpoints every 15 minutes
- Provide hints and guidance without giving solutions

**Minutes 60-75: Integration and Testing**
- Students finalize solutions and test thoroughly
- Instructor helps with debugging and optimization
- Prepare presentation materials

**Minutes 75-90: Presentations and Assessment**
- 5-minute presentations per group
- Peer feedback and instructor evaluation
- Discussion of different approaches and solutions

#### Real-Time Support Strategy

**Student Progress Check:** On Track → Minimal Guidance | Struggling → Targeted Support | Ahead → Advanced Challenges

**Support Options:** Technical Help, Conceptual Clarification, Alternative Approach, Extension Activities

### Common Challenge Issues & Solutions

#### Issue: Students Overwhelmed by Complexity
**Instructor Response**: Break down into smaller components
```sql
-- Instead of building entire dashboard at once:
-- Step 1: Basic revenue by park
SELECT park_id, SUM(total_revenue) FROM sales_transactions GROUP BY park_id;

-- Step 2: Add time dimension  
-- Step 3: Add growth calculations
-- Step 4: Add executive formatting
```

#### Issue: Performance Problems with Large Queries
**Instructor Guidance**: 
```sql
-- Use sampling for development
SELECT * FROM sales_transactions SAMPLE (10) -- 10% sample
WHERE transaction_date >= '2024-01-01';

-- Then scale to full dataset when logic is proven
```

#### Issue: AI-Generated SQL Not Working
**Debugging Process**:
1. Check table/column names match schema
2. Verify date formats and filters
3. Test query components individually
4. Use simpler prompts and build complexity gradually

### Assessment Rubric - Final Challenge

#### Technical Excellence (40%)
□ **Query Complexity (15%)**: Uses advanced SQL features appropriately
□ **Code Quality (10%)**: Well-structured, readable, maintainable
□ **Performance (10%)**: Executes efficiently, appropriate optimizations
□ **Error Handling (5%)**: Robust exception management

#### Business Value (35%)
□ **Requirements Fulfillment (20%)**: Addresses all scenario requirements
□ **Executive Readiness (10%)**: Results formatted for business stakeholders  
□ **Actionable Insights (5%)**: Provides clear, valuable business intelligence

#### Innovation and Creativity (25%)
□ **Advanced Features (15%)**: Goes beyond basic requirements
□ **Creative Problem Solving (10%)**: Novel approaches to challenges

**🖼️ SCREENSHOT PLACEHOLDER: Assessment Dashboard**
*Caption: Instructor evaluation interface showing rubric scores, student solutions comparison, and assessment notes for efficient grading and feedback.*

---

## LAB 05: AGENTS & INTELLIGENCE - INSTRUCTOR GUIDE (60 minutes)

### Advanced AI Orchestration Teaching

Lab 05 represents the cutting edge of AI-assisted analytics, introducing students to agent-based systems and autonomous business intelligence. This lab requires the highest level of instructor expertise and preparation.

### Pre-Lab Technical Validation

**🚨 CRITICAL**: Verify Cortex Agents availability in your Snowflake account
```sql
-- Test agent creation capability
CREATE OR REPLACE CORTEX SEARCH SERVICE test_search_service
ON search_data
WAREHOUSE = UDX_ANALYTICS_WAREHOUSE;

-- If this fails, Lab 05 may need to be modified for your account
```

### Agent Architecture Solutions

#### Complete Document Integration Agent

```sql
-- Advanced Document Processing Agent
CREATE OR REPLACE CORTEX SEARCH SERVICE udx_business_docs
ON business_documents  -- Table with park policies, procedures, FAQs
WAREHOUSE = UDX_ANALYTICS_WAREHOUSE
TARGET_LAG = '1 hour';

-- Intelligent Query Router Function
CREATE OR REPLACE FUNCTION intelligent_query_router(
    user_question STRING,
    query_type STRING DEFAULT 'AUTO'
)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    query_classification STRING;
    response_strategy STRING;
    final_answer STRING;
BEGIN
    -- Classify the query type using AI
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'Classify this UDX theme park question into one of these categories:
        DATA_QUERY, POLICY_QUESTION, OPERATIONAL_HELP, GENERAL_INFO
        
        Question: ' || user_question || '
        
        Return only the category name.'
    ) INTO query_classification;
    
    -- Route based on classification
    CASE UPPER(TRIM(query_classification))
        WHEN 'DATA_QUERY' THEN
            -- Generate and execute SQL query
            SELECT generate_sql_from_question(user_question) INTO final_answer;
            
        WHEN 'POLICY_QUESTION' THEN  
            -- Search document knowledge base
            SELECT search_business_documents(user_question) INTO final_answer;
            
        WHEN 'OPERATIONAL_HELP' THEN
            -- Provide operational guidance
            SELECT provide_operational_guidance(user_question) INTO final_answer;
            
        ELSE
            -- General information response
            final_answer := 'I can help you with data queries, policy questions, and operational guidance for UDX theme parks. How can I assist you today?';
    END CASE;
    
    RETURN final_answer;
END;
$$;

-- Document Search Integration
CREATE OR REPLACE FUNCTION search_business_documents(question STRING)
RETURNS STRING
LANGUAGE SQL  
AS
$$
DECLARE
    search_results STRING;
    formatted_response STRING;
BEGIN
    -- Use Cortex Search to find relevant documents
    SELECT SNOWFLAKE.CORTEX.SEARCH(
        'udx_business_docs',
        question,
        5  -- Return top 5 results
    ) INTO search_results;
    
    -- Generate contextual response using search results
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama3-70b',
        'Based on these UDX theme park documents: ' || search_results || '
        
        Answer this question: ' || question || '
        
        Provide a helpful, accurate response based on the document content.'
    ) INTO formatted_response;
    
    RETURN formatted_response;
END;
$$;
```

#### Multi-Agent Orchestration System

**🎯 INSTRUCTOR DEMO**: Show agent collaboration in action

```sql
-- Master Orchestration Function
CREATE OR REPLACE FUNCTION business_intelligence_agent(
    user_request STRING,
    context VARIANT DEFAULT NULL
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    agent_response VARIANT;
    data_insights STRING;
    document_insights STRING; 
    operational_recommendations STRING;
    final_synthesis STRING;
BEGIN
    -- Agent 1: Data Analytics Agent
    SELECT OBJECT_CONSTRUCT(
        'agent', 'data_analytics',
        'response', intelligent_query_router(user_request, 'DATA_QUERY'),
        'confidence', 0.9
    ) INTO data_insights;
    
    -- Agent 2: Knowledge Base Agent  
    SELECT OBJECT_CONSTRUCT(
        'agent', 'knowledge_base',
        'response', search_business_documents(user_request),
        'confidence', 0.8
    ) INTO document_insights;
    
    -- Agent 3: Operations Agent
    SELECT OBJECT_CONSTRUCT(
        'agent', 'operations',
        'response', provide_operational_guidance(user_request),
        'confidence', 0.7
    ) INTO operational_recommendations;
    
    -- Master Agent: Synthesize all responses
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mixtral-8x7b',
        'You are a master business intelligence agent for UDX theme parks.
        
        User request: ' || user_request || '
        
        Agent responses:
        Data Analytics: ' || data_insights || '
        Knowledge Base: ' || document_insights || '
        Operations: ' || operational_recommendations || '
        
        Synthesize these insights into a comprehensive, actionable response that addresses the user request.'
    ) INTO final_synthesis;
    
    -- Return structured response
    agent_response := OBJECT_CONSTRUCT(
        'user_request', user_request,
        'master_response', final_synthesis,
        'contributing_agents', ARRAY_CONSTRUCT(data_insights, document_insights, operational_recommendations),
        'response_timestamp', CURRENT_TIMESTAMP()
    );
    
    RETURN agent_response;
END;
$$;
```

### Lab 05 Teaching Challenges & Solutions

#### Challenge: Cortex Agents Not Available
**Instructor Backup Plan**: Simulate agent behavior with functions
```sql
-- Alternative implementation without Cortex Agents
CREATE OR REPLACE FUNCTION simulate_agent_orchestration(question STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    sql_response STRING;
    knowledge_response STRING; 
    combined_response STRING;
BEGIN
    -- Simulate data agent
    SELECT generate_sql_from_question(question) INTO sql_response;
    
    -- Simulate knowledge agent with static responses
    knowledge_response := 'Based on UDX policies and procedures...';
    
    -- Combine responses
    combined_response := 'Data Insights: ' || sql_response || 
                        '\n\nPolicy Guidance: ' || knowledge_response;
    
    RETURN combined_response;
END;
$$;
```

#### Challenge: Complex Agent Logic Confuses Students  
**Instructor Strategy**: Progressive complexity building
1. **Step 1**: Simple function calls
2. **Step 2**: Basic routing logic
3. **Step 3**: Multi-agent coordination
4. **Step 4**: Full orchestration system

### Advanced Assessment Strategies

#### Lab 05 Evaluation Framework

**🎯 INSTRUCTOR ASSESSMENT**: Multi-dimensional evaluation


**Technical Implementation (70%):**

• Code Quality (25%)

• Functionality (25%)

• Performance (15%)

• Error Handling (10%)


**Business Integration (45%):**

• Business Value (20%)

• User Experience (15%)

• Integration (10%)


**Innovation & Enterprise (30%):**

• Creative Features (15%)

• Advanced Techniques (10%)

• Scalability (10%)

• Security (5%)

• Maintainability (5%)

#### Portfolio Assessment Rubric

**Exceptional (90-100%)**:
□ Implements complete multi-agent orchestration
□ Seamless integration of all system components
□ Innovative features beyond requirements
□ Production-ready code quality
□ Clear business value demonstration

**Proficient (80-89%)**:
□ Functional agent system with minor limitations  
□ Good integration of most components
□ Meets all core requirements
□ Solid code quality with some optimization opportunities
□ Demonstrates clear understanding of concepts

**Developing (70-79%)**:
□ Basic agent functionality with significant limitations
□ Partial component integration
□ Meets most requirements with gaps
□ Functional code that needs refinement
□ Shows understanding but lacks depth

**🖼️ SCREENSHOT PLACEHOLDER: Portfolio Assessment Interface**
*Caption: Instructor dashboard showing comprehensive student portfolio assessment with technical scores, business value ratings, and detailed feedback sections for efficient evaluation.*

---

## COMPREHENSIVE INSTRUCTOR RESOURCES

### Troubleshooting Master Guide

#### Account-Level Issues

**Issue**: Cortex AI Functions Not Available
**Diagnosis**:
```sql
-- Check account region and Cortex availability
SELECT CURRENT_REGION() as region;
SELECT SYSTEM$GET_CORTEX_FUNCTIONS() as available_functions;
```
**Solutions**:
1. Contact Snowflake support for Cortex enablement
2. Use alternative region if available
3. Implement backup exercises without AI features

**Issue**: Performance Problems During Hackathon
**Real-time Monitoring**:
```sql
-- Monitor warehouse utilization
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
WHERE START_TIME >= CURRENT_DATE()
ORDER BY START_TIME DESC;

-- Check for hanging queries
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
WHERE START_TIME >= CURRENT_DATE() 
AND EXECUTION_STATUS = 'RUNNING'
AND ELAPSED_TIME > 300000; -- 5+ minutes
```

#### Student Progress Monitoring Dashboard

```sql
-- Create instructor monitoring view
CREATE OR REPLACE VIEW instructor_progress_dashboard AS
WITH student_activity AS (
    SELECT 
        user_name,
        warehouse_name,
        database_name,
        COUNT(*) as queries_executed,
        MAX(start_time) as last_activity,
        SUM(CASE WHEN execution_status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_queries,
        SUM(CASE WHEN execution_status != 'SUCCESS' THEN 1 ELSE 0 END) as failed_queries
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE start_time >= CURRENT_DATE()
    AND warehouse_name = 'UDX_ANALYTICS_WAREHOUSE'
    GROUP BY user_name, warehouse_name, database_name
)
SELECT 
    user_name,
    queries_executed,
    successful_queries,
    failed_queries,
    ROUND((successful_queries::FLOAT / queries_executed) * 100, 1) as success_rate_pct,
    last_activity,
    CASE 
        WHEN last_activity < DATEADD('minute', -30, CURRENT_TIMESTAMP()) THEN '🚨 Inactive'
        WHEN success_rate_pct < 60 THEN '⚠️ Struggling'
        WHEN success_rate_pct > 90 THEN '🌟 Excelling'
        ELSE '✅ On Track'
    END as status
FROM student_activity
ORDER BY last_activity DESC;
```

### Emergency Backup Plans

#### Scenario 1: Cortex AI Complete Failure
**Backup Exercise Set**:
```sql
-- Pre-built queries for manual execution
-- Revenue Analysis Without AI
SELECT 
    park_id,
    SUM(total_revenue) as total_revenue,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales_transactions 
WHERE transaction_date >= '2024-01-01'
GROUP BY park_id
ORDER BY total_revenue DESC;

-- Customer Segmentation Without AI  
SELECT 
    CASE 
        WHEN total_spending > 5000 THEN 'High Value'
        WHEN total_spending > 2000 THEN 'Medium Value'
        ELSE 'Standard'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spending) as avg_spending
FROM (
    SELECT 
        customer_id,
        SUM(total_revenue) as total_spending
    FROM sales_transactions
    GROUP BY customer_id
) 
GROUP BY customer_segment;
```

#### Scenario 2: Network/Performance Issues
**Reduced Scope Alternative**:
- Focus on Labs 01-03 only
- Use smaller data samples (LIMIT 1000)
- Simplified business scenarios
- Local SQL development practice

### Post-Hackathon Resources

#### Student Continuation Path
1. **Next Steps Guide**: Advanced Snowflake and AI features to explore
2. **Portfolio Development**: How to showcase hackathon work to employers
3. **Community Resources**: Snowflake user groups, AI communities
4. **Certification Paths**: Relevant Snowflake and AI certifications

#### Instructor Feedback Collection
```sql
-- Anonymous feedback collection table
CREATE TABLE hackathon_feedback (
    feedback_id STRING DEFAULT UUID_STRING(),
    lab_section STRING,
    difficulty_rating NUMBER(1,0), -- 1-5 scale
    time_spent_minutes NUMBER,
    most_valuable_aspect STRING,
    improvement_suggestions STRING,
    would_recommend BOOLEAN,
    technical_issues_encountered STRING,
    submission_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Professional Development Outcomes

#### Skills Assessment Framework
Students who complete this hackathon successfully demonstrate:

**Technical Competencies**:
□ Advanced SQL query development and optimization
□ AI/ML integration with business intelligence systems  
□ Cloud data warehouse administration (Snowflake)
□ Natural language processing implementation
□ Complex analytics and business logic development

**Business Competencies**:
□ Requirements analysis and translation to technical solutions
□ Business intelligence dashboard development
□ Data-driven decision making and insight generation
□ Cross-functional collaboration and communication
□ Problem-solving with emerging AI technologies

**Career Relevance**:
□ Data Analyst/Business Intelligence Analyst roles
□ AI Engineer/Machine Learning Engineer positions
□ Data Architect/Analytics Engineer careers
□ Business Intelligence Developer opportunities
□ Emerging AI Product Manager roles

This instructor guide provides comprehensive support for delivering a world-class AI-powered business intelligence hackathon that prepares students for the future of data analytics careers.

**🖼️ SCREENSHOT PLACEHOLDER: Hackathon Success Celebration**
*Caption: Students and instructor celebrating successful completion of the UDX NLP2SQL hackathon, with Snowsight screens showing completed projects and achievement certificates or awards visible.*

---

## FINAL INSTRUCTOR CHECKLIST

### Pre-Event (1 Week Before)
□ All student accounts created and tested
□ Complete instructor walkthrough completed
□ Backup plans prepared and tested
□ Troubleshooting resources assembled
□ Assessment rubrics finalized

### Event Day Setup (1 Hour Before)  
□ Instructor solutions environment ready
□ Student progress monitoring dashboard active
□ Emergency contact information distributed
□ Backup exercises prepared
□ Network and system performance verified

### During Event Monitoring
□ Real-time student progress tracking
□ Proactive issue identification and resolution
□ Collaborative learning facilitation
□ Individual student support as needed
□ Timeline management and pacing

### Post-Event Follow-up
□ Student feedback collection
□ Performance analytics review
□ Curriculum improvement identification
□ Student portfolio guidance provided
□ Professional development resources shared

**Congratulations on delivering an exceptional AI-powered business intelligence learning experience!** 🎉 