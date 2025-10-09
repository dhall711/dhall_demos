-- ============================================================================
-- Lab 09: Snowflake Agents & Intelligence - Hands-On Exercises
-- ============================================================================
-- These exercises demonstrate advanced agentic AI capabilities building on 
-- your existing NLP2SQL foundation from Labs 01-08.
-- ============================================================================

-- Set context
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;
USE DATABASE UDX_NL2SQL;
USE SCHEMA BUSINESS_ANALYTICS;

-- ============================================================================
-- EXERCISE 1: Document Knowledge Base Exploration
-- ============================================================================

/*
Exercise 1.1: Explore the Document Knowledge Base
Objective: Understand what business context is available for agent enhancement

Task: Query the UDX_DOCUMENTS table to understand available knowledge
*/

-- TODO: Write a query to show all document types and departments
-- Hint: Use GROUP BY to categorize documents by type and department


-- TODO: Find all documents related to 'safety' or 'emergency'
-- Hint: Use WHERE with CONTAINS or LIKE operators on document_content


-- TODO: Show the most recent documents by department
-- Hint: Use window functions with ROW_NUMBER() and PARTITION BY


/*
Exercise 1.2: Test Cortex Search Capabilities
Objective: Experience semantic search across unstructured business documents

Task: Use Cortex Search to find relevant documents for business questions
*/

-- TODO: Search for information about "guest satisfaction policies"
-- Use: SELECT SNOWFLAKE.CORTEX.SEARCH('udx_knowledge_base', 'your search query');


-- TODO: Search for "revenue recognition procedures"
-- Compare the results to keyword-based searching


-- TODO: Search for "emergency procedures staff training"
-- Observe how semantic search understands context and intent


-- ============================================================================
-- EXERCISE 2: Agent Configuration and Orchestration
-- ============================================================================

/*
Exercise 2.1: Create and Test Agent Configurations
Objective: Build role-specific agents for different business users

Task: Create specialized agents for different UDX departments
*/

-- TODO: Test the executive agent configuration
-- SELECT create_role_specific_agent('executive') as executive_agent;


-- TODO: Test the operations manager agent configuration
-- SELECT create_role_specific_agent('operations_manager') as ops_agent;


-- TODO: Compare the different agent configurations
-- What differences do you notice in focus_areas and data_access?


/*
Exercise 2.2: Simulate Agent Conversations
Objective: Experience enhanced conversation management with agent context

Task: Create a multi-turn conversation with business context
*/

-- TODO: Start a conversation about park performance
SELECT continue_agent_conversation(
    'session_001',
    'What are our top performing parks by guest satisfaction this month?',
    'manager_001',
    'operations_manager'
) as conversation_start;


-- TODO: Follow up with a related question in the same session
SELECT continue_agent_conversation(
    'session_001', 
    'What policies do we have for maintaining high guest satisfaction?',
    'manager_001',
    'operations_manager'
) as conversation_followup;


-- TODO: Examine the conversation history and context
SELECT 
    session_id,
    message_sequence,
    user_message,
    tools_used,
    documents_referenced,
    business_context_applied
FROM AGENT_CONVERSATIONS 
WHERE session_id = 'session_001'
ORDER BY message_sequence;


-- ============================================================================
-- EXERCISE 3: Multi-Modal Business Analysis
-- ============================================================================

/*
Exercise 3.1: Structured + Unstructured Data Integration
Objective: Combine data analysis with policy/procedure context

Task: Analyze business scenarios that require both data and documents
*/

-- TODO: Create a comprehensive business analysis
-- Question: "Show me parks with safety incidents and our safety policies"

-- Step 1: Analyze structured data for safety-related metrics
SELECT 
    p.park_name,
    AVG(p.guest_satisfaction_score) as avg_satisfaction,
    COUNT(*) as total_days_analyzed,
    -- Add safety-related calculated fields
    CASE WHEN AVG(p.guest_satisfaction_score) < 7 THEN 'Review Safety Protocols' 
         ELSE 'Satisfactory' END as safety_status
FROM PARK_PERFORMANCE p
WHERE p.performance_date >= CURRENT_DATE() - 30
GROUP BY p.park_name
ORDER BY avg_satisfaction;


-- Step 2: Search for relevant safety policies
SELECT SNOWFLAKE.CORTEX.SEARCH(
    'udx_knowledge_base',
    'safety protocols incident reporting emergency procedures'
) as safety_policies;


-- TODO: Create a business scenario combining revenue and marketing policies
-- Question: "Which parks have declining revenue and what marketing strategies should we apply?"

-- Your turn: Write queries that combine:
-- 1. Revenue trend analysis from SALES_TRANSACTIONS
-- 2. Marketing policy search from documents
-- 3. Recommendations based on both data and policies


/*
Exercise 3.2: Executive Dashboard with Agent Enhancement
Objective: Create comprehensive executive insights with agent orchestration

Task: Build an executive view that combines multiple data sources and business context
*/

-- TODO: Create an executive summary with multiple business dimensions
WITH revenue_trends AS (
    SELECT 
        p.park_name,
        DATE_TRUNC('month', s.transaction_date) as month,
        SUM(s.revenue_amount) as monthly_revenue,
        COUNT(DISTINCT s.customer_id) as unique_customers
    FROM SALES_TRANSACTIONS s
    JOIN PARK_PERFORMANCE p ON s.park_id = p.park_id
    WHERE s.transaction_date >= CURRENT_DATE() - 90
    GROUP BY p.park_name, DATE_TRUNC('month', s.transaction_date)
),
satisfaction_trends AS (
    SELECT 
        park_name,
        DATE_TRUNC('month', performance_date) as month,
        AVG(guest_satisfaction_score) as avg_satisfaction
    FROM PARK_PERFORMANCE 
    WHERE performance_date >= CURRENT_DATE() - 90
    GROUP BY park_name, DATE_TRUNC('month', performance_date)
)
-- TODO: Complete this query to show comprehensive park performance
-- Include revenue trends, satisfaction scores, and growth rates
SELECT 
    r.park_name,
    r.month,
    r.monthly_revenue,
    r.unique_customers,
    s.avg_satisfaction
    -- Add calculated fields for trends and performance indicators
FROM revenue_trends r
LEFT JOIN satisfaction_trends s ON r.park_name = s.park_name AND r.month = s.month
ORDER BY r.park_name, r.month;


-- TODO: Search for executive reporting policies and financial procedures
-- What business context should executives consider with this data?


-- ============================================================================
-- EXERCISE 4: Snowflake Intelligence Preparation
-- ============================================================================

/*
Exercise 4.1: Prepare Data for Intelligence Portal
Objective: Create business-friendly views for no-code access

Task: Design views that business users can easily query through ai.snowflake.com
*/

-- TODO: Examine the pre-built Intelligence views
SELECT * FROM INTELLIGENCE_PARK_ANALYTICS LIMIT 10;
SELECT * FROM INTELLIGENCE_CUSTOMER_INSIGHTS LIMIT 10;


-- TODO: Create your own Intelligence-ready view for marketing analysis
CREATE OR REPLACE VIEW INTELLIGENCE_MARKETING_DASHBOARD AS
SELECT 
    'UDX Marketing Analytics' as data_source,
    'Customer acquisition and campaign performance' as description,
    -- TODO: Add relevant marketing metrics
    -- Include customer segments, acquisition channels, campaign ROI
    c.age_group,
    c.preferred_park,
    COUNT(DISTINCT c.customer_id) as customer_count,
    AVG(c.total_spent) as avg_lifetime_value
    -- Add more marketing-relevant fields
FROM CUSTOMERS c
GROUP BY c.age_group, c.preferred_park;


-- TODO: Create a view for operational excellence
CREATE OR REPLACE VIEW INTELLIGENCE_OPERATIONS_DASHBOARD AS
-- Design this view for operations managers
-- Include capacity utilization, satisfaction trends, efficiency metrics
SELECT 
    'UDX Operations Analytics' as data_source,
    -- Complete this view with operational KPIs
    NULL as placeholder;


/*
Exercise 4.2: Test Intelligence-Style Queries
Objective: Practice natural language questions that work well with Snowflake Intelligence

Task: Write queries that simulate what business users would ask
*/

-- TODO: Simulate common business user questions
-- Example 1: "Show me our best performing parks by revenue"


-- Example 2: "Which customer segments spend the most money?"


-- Example 3: "What are the satisfaction trends for each park?"


-- TODO: Create complex business scenarios
-- "Compare VIP customer behavior with standard customers across different parks"


-- "Show me seasonal patterns in revenue and how they correlate with satisfaction"


-- ============================================================================
-- EXERCISE 5: Advanced Agent Workflows
-- ============================================================================

/*
Exercise 5.1: Complex Business Problem Solving
Objective: Use agent orchestration for sophisticated business analysis

Task: Solve multi-faceted business problems requiring multiple tools and data sources
*/

-- Business Scenario: "Our California park has declining satisfaction. 
-- Investigate the causes and recommend solutions based on data and policies."

-- TODO: Step 1 - Analyze satisfaction trends
-- Create a query showing satisfaction decline patterns


-- TODO: Step 2 - Correlate with operational metrics
-- Look at capacity utilization, wait times, staffing levels


-- TODO: Step 3 - Search for relevant policies
-- Find customer service standards, operational procedures, staff training


-- TODO: Step 4 - Integrate findings
-- Combine data insights with policy guidance for recommendations


/*
Exercise 5.2: Proactive Business Intelligence
Objective: Use agent capabilities for predictive insights and recommendations

Task: Create forward-looking analysis with actionable recommendations
*/

-- TODO: Identify trends and patterns for proactive decision making
-- "Based on current trends, what should we prepare for peak season?"

-- Step 1: Analyze historical peak season patterns


-- Step 2: Current performance indicators


-- Step 3: Policy and procedure preparedness


-- Step 4: Generate specific recommendations


-- ============================================================================
-- EXERCISE 6: Agent Performance and Optimization
-- ============================================================================

/*
Exercise 6.1: Monitor Agent Effectiveness
Objective: Understand how agents perform and improve over time

Task: Analyze agent interaction patterns and performance metrics
*/

-- TODO: Calculate agent performance metrics
SELECT calculate_agent_performance(CURRENT_DATE()) as todays_performance;


-- TODO: Analyze conversation patterns
SELECT 
    user_role,
    AVG(response_time_ms) as avg_response_time,
    AVG(response_confidence) as avg_confidence,
    COUNT(*) as total_conversations,
    -- Add analysis of most common question types
    ARRAY_AGG(DISTINCT user_message) as sample_questions
FROM AGENT_CONVERSATIONS
WHERE DATE(created_at) = CURRENT_DATE()
GROUP BY user_role;


-- TODO: Identify optimization opportunities
-- Which tools are used most frequently?
-- What types of questions take longest to answer?
-- Where is agent confidence lowest?


/*
Exercise 6.2: A/B Test Traditional vs Agent Approaches
Objective: Compare traditional NLP2SQL with agent-enhanced capabilities

Task: Design experiments to measure improvement with agents
*/

-- TODO: Create comparison framework
CREATE OR REPLACE TABLE APPROACH_COMPARISON (
    test_id STRING,
    user_question STRING,
    traditional_method VARIANT,
    agent_method VARIANT,
    accuracy_comparison STRING,
    speed_comparison STRING,
    user_preference STRING,
    notes STRING
);


-- TODO: Test sample questions with both approaches
-- Example: "What's our revenue trend by park this quarter?"

-- Traditional approach: Individual function calls
-- Agent approach: Orchestrated workflow

-- Document the differences in:
-- - Response accuracy and completeness
-- - Response time
-- - Business context integration
-- - User satisfaction


-- ============================================================================
-- CHALLENGE EXERCISES
-- ============================================================================

/*
Challenge 1: Build a Complete Business Intelligence Agent
Objective: Create an end-to-end agent that can handle any UDX business question

Task: Design an agent that intelligently routes questions and provides comprehensive answers
*/

-- TODO: Create a universal UDX business intelligence function
CREATE OR REPLACE FUNCTION udx_business_intelligence_agent(
    user_question STRING,
    user_role STRING DEFAULT 'business_user',
    include_visualizations BOOLEAN DEFAULT TRUE
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
-- Your implementation here
-- Should handle:
-- 1. Question classification (data vs document vs hybrid)
-- 2. Role-based response customization  
-- 3. Multi-tool orchestration
-- 4. Business context integration
-- 5. Visualization recommendations
-- 6. Follow-up suggestions
$$;


/*
Challenge 2: Conversational BI Assistant
Objective: Create a conversational interface that maintains context and learns

Task: Build an assistant that gets smarter with each interaction
*/

-- TODO: Design a learning conversation system
-- Consider:
-- - How to maintain long conversation context
-- - How to learn user preferences
-- - How to improve responses based on feedback
-- - How to handle ambiguous questions
-- - How to suggest proactive insights


/*
Challenge 3: Real-Time Intelligence Dashboard
Objective: Create a live dashboard that combines agents with real-time data

Task: Design a system that provides continuous intelligence
*/

-- TODO: Create a real-time monitoring system
-- Components:
-- - Stream processing for live data
-- - Agent-powered anomaly detection  
-- - Automated insight generation
-- - Alert and notification system
-- - Interactive query interface


-- ============================================================================
-- REFLECTION QUESTIONS
-- ============================================================================

/*
After completing these exercises, consider:

1. How do agents improve on traditional NLP2SQL approaches?
2. What business value does document integration provide?
3. How does role-based agent configuration improve user experience?
4. What new types of business questions become possible with agents?
5. How would you measure ROI of agent implementation?
6. What governance and security considerations are important?
7. How would you train business users on agent capabilities?
8. What future enhancements would you prioritize?

Document your insights and recommendations for production deployment.
*/

-- Display completion message
SELECT 
    'Lab 09 Exercises Complete!' as status,
    'You have explored advanced agentic AI capabilities!' as achievement,
    'Ready for production agent deployment.' as next_step; 