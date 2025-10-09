# UDX NLP2SQL Hackathon: Student Guide

## Welcome to the Future of Business Intelligence!

Congratulations on joining the UDX Natural Language to SQL Hackathon! You're about to build a revolutionary system that transforms how business users interact with data. Instead of learning complex SQL, users will simply ask questions in plain English like "Show me our top performing parks this quarter" and get instant, accurate results.


### What You'll Build

By the end of this hackathon, you'll have created:

• **Natural Language to SQL Translation Engine** using Snowflake Cortex AI

• **Conversational Business Intelligence Assistant** with multi-turn dialogue

• **Advanced Agentic AI Platform** with document integration

• **Enterprise-Ready Analytics Solution** with governance and security


### Time Investment: 4-5 Hours

• **Lab 01**: Environment Setup (50 minutes)

• **Lab 02**: Basic NLP2SQL (60 minutes)

• **Lab 03**: Advanced Features (90 minutes)

• **Lab 04**: Final Challenge (90 minutes)

• **Lab 05**: Agents & Intelligence (60 minutes)

---

## LAB 01: FOUNDATION SETUP (50 minutes)

### Learning Objectives

• Set up Snowflake environment optimized for AI workloads

• Load comprehensive UDX theme park business data

• Create AI context and business metadata

• Validate Cortex AI functionality


### What You're Building

A complete business analytics environment with 6 UDX theme parks, 500K+ transactions, customer analytics, and operational metrics.


---

## Step 1: Snowsight Setup & Environment Preparation (15 minutes)

**🖼️ SCREENSHOT PLACEHOLDER: Snowflake Login Page**
*Caption: Snowflake login interface at app.snowflake.com showing username/password fields, account identifier, and login button. The modern Snowsight interface should be visible as an option.*


### Creating Your Snowflake SQL Worksheet

1. **Access Snowsight**

   • Log into your Snowflake account at [app.snowflake.com](https://app.snowflake.com)
   
   • Click on "Snowsight" in the left navigation (or it may load automatically)
   
   • Ensure you're in the modern Snowsight interface (not Classic Console)

**🖼️ SCREENSHOT PLACEHOLDER: Snowsight Main Interface**
*Caption: Main Snowsight dashboard showing the left navigation panel with "Worksheets", "Databases", "Warehouses" options. The main content area should show the worksheet listing with the "+" button visible in the top-left corner.*

2. **Create New SQL Worksheet**

   • Click the "+" button in the top-left corner
   
   • Select "SQL Worksheet"
   
   • Name your worksheet: "UDX NLP2SQL Hackathon - Setup"

**🖼️ SCREENSHOT PLACEHOLDER: New Worksheet Creation**
*Caption: Dropdown menu from the "+" button showing options like "SQL Worksheet", "Dashboard", etc. The worksheet naming dialog should be visible with the text field for entering "UDX NLP2SQL Hackathon - Setup".*


3. **Configure Worksheet Context**

   • In the top-right corner, set your context:
   
     - **Role**: Select "ACCOUNTADMIN" (or ask instructor which role to use)
     
     - **Warehouse**: Leave blank for now (we'll create our own)
     
     - **Database**: Leave blank for now
     
     - **Schema**: Leave blank for now

**🖼️ SCREENSHOT PLACEHOLDER: Context Configuration**
*Caption: Top-right corner of Snowsight worksheet showing the context dropdowns for Role, Warehouse, Database, and Schema. The Role dropdown should be open showing ACCOUNTADMIN and other available roles.*


### Recommended Worksheet Organization

Create separate worksheets for each lab:

• "Lab 01 - Environment Setup"

• "Lab 02 - Basic NLP2SQL"

• "Lab 03 - Advanced Features"

• "Lab 04 - Final Challenge"

• "Lab 05 - Agents & Intelligence"

**🖼️ SCREENSHOT PLACEHOLDER: Worksheet Organization**
*Caption: Left sidebar in Snowsight showing multiple worksheets organized with descriptive names for each lab. Each worksheet should be clearly visible in a clean, organized list.*


### Snowsight Best Practices

**Worksheet Management:**

• Use descriptive names for each worksheet

• Keep related queries together in the same worksheet

• Use comments (--) to organize your code sections

• Save frequently (Ctrl+S or Cmd+S)


**Running SQL Code:**

• Highlight specific queries to run individual statements

• Use Ctrl+Enter (or Cmd+Enter) to run highlighted code

• Use Ctrl+A + Ctrl+Enter to run entire worksheet

• Watch the Results panel for output and errors

**🖼️ SCREENSHOT PLACEHOLDER: Query Execution Interface**
*Caption: Snowsight worksheet showing SQL code in the editor with a portion highlighted. The Results panel at the bottom should show successful query execution with data results displayed in a clean table format.*


**Context Management:**

• Always verify your warehouse/database/schema context before running queries

• Use explicit USE statements when switching contexts

• The context shows in the top-right corner of the worksheet


### Verify Your Setup

**Test basic functionality:**

```sql
-- Test basic Snowflake connectivity
SELECT CURRENT_USER() as current_user, 
       CURRENT_ROLE() as current_role,
       CURRENT_TIMESTAMP() as current_time;
```

**🖼️ SCREENSHOT PLACEHOLDER: Basic Connectivity Test**
*Caption: Query results showing successful execution of the connectivity test with three columns displaying current user, role, and timestamp information in a formatted table.*


**Test Cortex AI availability:**

```sql
-- Test Cortex AI availability
SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Hello, AI!') as cortex_test;
```

If the Cortex test fails, contact your instructor for Cortex AI access.

**🖼️ SCREENSHOT PLACEHOLDER: Cortex AI Test Results**
*Caption: Query results showing successful Cortex AI response with the generated text visible in the cortex_test column. The AI response should be clearly visible and properly formatted.*


### Troubleshooting Common Issues

• **Worksheets don't load**: Refresh browser or try incognito mode

• **Queries hang**: Check if warehouse is running (may need to resume)

• **Permission errors**: Verify you're using the correct role

• **Cortex unavailable**: Contact instructor for account enablement

---

## Step 2: Execute Core Setup Script (15 minutes)

### Running the Setup Script in Snowsight

1. **Access the Setup File**

   • Navigate to your project folder: `/UDX Hackathon/UDX-NLP2SQL/01-setup/`
   
   • Open `setup.sql` in a text editor (VS Code, Notepad++, or any editor)

**🖼️ SCREENSHOT PLACEHOLDER: Setup File in Text Editor**
*Caption: Text editor (VS Code or similar) showing the setup.sql file open with the complete script visible. The file should show the database creation commands, warehouse setup, and Cortex AI function definitions.*


2. **Copy Script to Snowsight**

   • Select all content from `setup.sql` (Ctrl+A / Cmd+A)
   
   • Copy the entire script (Ctrl+C / Cmd+C)
   
   • Switch to your "Lab 01 - Environment Setup" worksheet in Snowsight
   
   • Paste the script (Ctrl+V / Cmd+V)

**🖼️ SCREENSHOT PLACEHOLDER: Script Pasted in Snowsight**
*Caption: Snowsight worksheet showing the complete setup.sql script pasted in the editor. The script should be properly formatted with syntax highlighting and clear section divisions.*


3. **Execute the Setup Script**

   • **Option A - Run All**: Select all (Ctrl+A) then execute (Ctrl+Enter)
   
   • **Option B - Section by Section**: Run each major section separately by highlighting specific parts

**🖼️ SCREENSHOT PLACEHOLDER: Script Execution Progress**
*Caption: Snowsight showing the setup script running with progress indicators or completion messages visible. The Results panel should show successful creation of databases, warehouses, and tables.*


### Monitor Progress and Verify Setup

**Watch for these key confirmations:**

• Database and schemas created

• Warehouse created and active

• Tables and functions created successfully

• AI test query responds correctly

**🖼️ SCREENSHOT PLACEHOLDER: Setup Completion Results**
*Caption: Results panel showing successful completion messages for all setup components: warehouse creation, database setup, schema creation, and function deployment confirmations.*


**Verify your context shows:**

• **Warehouse**: UDX_ANALYTICS_WAREHOUSE

• **Database**: UDX_NL2SQL

• **Schema**: BUSINESS_ANALYTICS

**🖼️ SCREENSHOT PLACEHOLDER: Verified Context**
*Caption: Top-right corner of Snowsight showing the context dropdowns populated with UDX_ANALYTICS_WAREHOUSE, UDX_NL2SQL, and BUSINESS_ANALYTICS, confirming successful setup.*


### What the Setup Script Creates

✓ UDX_NL2SQL database

✓ BUSINESS_ANALYTICS schema 

✓ UDX_ANALYTICS_WAREHOUSE

✓ Business glossary and metadata

✓ AI helper functions

✓ Security roles and permissions

**Pro Tips:**
• Read the comments in setup.sql to understand each section
• If any step fails, check the error message and retry that section
• Save your worksheet after successful execution (Ctrl+S / Cmd+S)

#### Step 3: Load Business Data (15 minutes)

##### Running the Data Loading Script

1. **Access the Data Loading File**
   • Navigate to: `/UDX Hackathon/UDX-NLP2SQL/sample-data/`
   • Open `load_business_data.sql` in your text editor

2. **Execute in Snowsight**
   • Create a new worksheet: "Lab 01 - Data Loading"
   • Copy the entire `load_business_data.sql` script
   • Paste into your Snowsight worksheet
   • **Important**: Verify your context is set correctly:
     - **Warehouse**: UDX_ANALYTICS_WAREHOUSE
     - **Database**: UDX_NL2SQL
     - **Schema**: BUSINESS_ANALYTICS

3. **Execute the Data Loading Script**
   • **Recommended**: Run section by section (each table separately)
   • Watch for successful INSERT statements in the Results panel
   • **Note**: This script may take 2-3 minutes to complete due to data volume

4. **Monitor Data Loading Progress**
   • Look for successful creation of these tables:
     - PARKS (6 records)
     - CUSTOMERS (50,000 records)
     - SALES_TRANSACTIONS (500,000 records)
     - PARK_PERFORMANCE (2,000+ records)
     - ATTRACTION_ANALYTICS (100,000+ records)
     - MARKETING_CAMPAIGNS (200 records)
     - FINANCIAL_SUMMARY (365+ records)

**What Gets Loaded:**
✓ 50,000 customers with demographics
✓ 500,000 sales transactions
✓ 2,000 daily park performance records
✓ 100,000 attraction analytics records
✓ Marketing campaign data
✓ Financial summary data

**Pro Tips:**
• If loading fails, check warehouse is running (may auto-suspend)
• Large data loads may take a few minutes - be patient
• Use separate worksheet for data loading to keep setup clean

#### Step 4: Validation (5 minutes)

Verify your setup with these queries:

```sql
SELECT 
    'Setup Validation' as check_type,
    (SELECT COUNT(*) FROM CUSTOMERS) as customers,
    (SELECT COUNT(*) FROM SALES_TRANSACTIONS) as transactions,
    (SELECT SUM(total_revenue) FROM SALES_TRANSACTIONS) as total_revenue;

-- Test AI functionality:
SELECT extract_query_intent('Show me top customers by revenue') as ai_test;
```

### Success Criteria
□ All tables loaded with realistic data
□ AI functions responding correctly
□ No error messages in setup scripts
□ Sample queries returning business-realistic results

### Troubleshooting
• Error: "Cortex function does not exist" → Contact instructor for Cortex AI enablement
• Error: "Insufficient privileges" → Ensure you're using ACCOUNTADMIN role
• Error: "Object already exists" → Add IF NOT EXISTS or OR REPLACE to create statements

### Snowsight Worksheet Management Throughout the Hackathon

Now that you have your foundation set up, here are best practices for managing your Snowsight worksheets throughout the remaining labs:

#### Worksheet Organization Strategy

**Create Dedicated Worksheets for Each Lab:**
• Lab 02: "Basic NLP2SQL Translation"
• Lab 03: "Advanced Query Translation"
• Lab 04: "Final Challenge Implementation"
• Lab 05: "Agents & Intelligence"

**Worksheet Naming Conventions:**
• Use descriptive names: "Lab 05 - Conversation Context"
• Include version numbers if iterating: "Final Challenge v2"
• Mark completed work: "Lab 03 - COMPLETED"

#### Code Organization Within Worksheets

**Use Section Headers:**
```sql
-- =====================================================
-- EXERCISE 1: Simple Business Questions
-- =====================================================

-- Exercise 1.1: Revenue Analytics
SELECT ...

-- Exercise 1.2: Customer Analysis  
SELECT ...
```

**Comment Your Experiments:**
```sql
-- Testing different AI models for accuracy
-- mixtral-8x7b version:
SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', '...');

-- llama3-70b version (more complex queries):
SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', '...');
```

#### Context Management Best Practices

**Always Verify Context Before Running:**
• Check warehouse/database/schema in top-right corner
• Use explicit USE statements when switching contexts
• Add context verification at the top of each worksheet:

```sql
-- Context verification
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;
USE DATABASE UDX_NL2SQL;
USE SCHEMA BUSINESS_ANALYTICS;

-- Verify context is correct
SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
```

#### Debugging and Troubleshooting

**Common Snowsight Issues:**
• **Query hanging**: Check if warehouse needs to resume
• **Permission errors**: Verify you're using correct role
• **Object not found**: Check context (database/schema)
• **Syntax errors**: Check for typos in function names

**Debugging Strategies:**
• Run queries section by section to isolate issues
• Use DESCRIBE TABLE to verify table structure
• Test simple queries before complex ones
• Save working versions before experimenting

#### Performance Optimization

**For Large Queries:**
• Use LIMIT clauses when testing
• Run during off-peak hours if possible
• Monitor warehouse usage in Account > Usage tab
• Consider using smaller warehouse for development

**Query Result Management:**
• Download large result sets as CSV if needed
• Use Result Set cache for repeated queries
• Clear old results to improve worksheet performance

#### Collaboration and Sharing

**If Working in Teams:**
• Share worksheet URLs with team members
• Use descriptive comments for handoffs
• Create "TEAM" worksheets for shared work
• Document decisions and approach in comments

**Version Control:**
• Save important milestones with version numbers
• Export working solutions as .sql files
• Keep backup copies of complex queries
• Document what works and what doesn't

#### Snowsight Productivity Tips

**Essential Keyboard Shortcuts:**
• **Ctrl+Enter** (Cmd+Enter): Execute selected query
• **Ctrl+A** (Cmd+A): Select all in worksheet
• **Ctrl+S** (Cmd+S): Save worksheet
• **Ctrl+Z** (Cmd+Z): Undo last change
• **Ctrl+F** (Cmd+F): Find and replace in worksheet
• **F5**: Refresh results
• **Escape**: Cancel running query

**Result Management:**
• Click column headers to sort results
• Use the filter icon to filter result columns
• Download results as CSV, JSON, or copy to clipboard
• Use the Chart tab to create quick visualizations
• Pin important results for easy reference

**Query Performance Tips:**
• Use LIMIT when testing large queries
• Check query profile for optimization insights
• Monitor warehouse utilization in real-time
• Use query history to rerun successful queries

#### Ready for Labs 02-09!

With your Snowsight environment properly configured and these best practices in mind, you're ready to tackle the advanced NLP2SQL features. Remember to:
• Keep worksheets organized by lab
• Save frequently and comment your work
• Verify context before running queries
• Use keyboard shortcuts for efficiency
• Ask for help if Snowsight isn't behaving as expected

---

## LAB 02: BASIC NLP2SQL TRANSLATION (60 minutes)

### Learning Objectives
• Master natural language to SQL translation patterns
• Understand prompt engineering for business queries
• Practice with real UDX business scenarios
• Build confidence in AI-assisted query development

### Business Context

You're building for UDX theme park stakeholders:

• **Executives**: Want high-level KPIs and trends

• **Operations**: Need daily performance and guest satisfaction

• **Marketing**: Require customer analytics and campaign ROI

• **Finance**: Focus on revenue analysis and cost optimization

### Step-by-Step Learning Path

#### Setting Up Your NLP2SQL Workspace

**Create New Worksheet:**
• Name: "Lab 02 - Basic NLP2SQL Translation"
• Verify context: UDX_ANALYTICS_WAREHOUSE / UDX_NL2SQL / BUSINESS_ANALYTICS
• Add context verification at the top:

```sql
-- Lab 02: Basic NLP2SQL Translation
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;
USE DATABASE UDX_NL2SQL; 
USE SCHEMA BUSINESS_ANALYTICS;
```

**🖼️ SCREENSHOT PLACEHOLDER: NLP2SQL Worksheet Setup**
*Caption: New Snowsight worksheet named "Lab 02 - Basic NLP2SQL Translation" with the context properly set and the USE statements visible in the editor. The worksheet should show the correct warehouse, database, and schema in the context dropdowns.*

---

## Exercise 1: Simple Business Questions (15 minutes)

Start with basic aggregations that executives might ask:

**File:** 03-basic-nl2sql/exercises.sql

**Try this example:**

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Convert to SQL: "What is our total revenue this year?" 
     Use SALES_TRANSACTIONS table with total_revenue column. 
     Filter for current year only.'
) as generated_sql;
```

**🖼️ SCREENSHOT PLACEHOLDER: Cortex Query Generation**
*Caption: Snowsight showing the Cortex AI query with the business question input and the generated SQL response visible in the results panel. The generated SQL should be clearly displayed and properly formatted.*

Copy the generated SQL and execute it!

**🖼️ SCREENSHOT PLACEHOLDER: Generated SQL Execution**
*Caption: Snowsight showing the copied generated SQL query being executed in a new query block, with the actual business results (revenue numbers) displayed in the results table.*

**Practice Questions:**

• "Who are our top 10 customers by lifetime value?"

• "What is the average guest satisfaction by park?"

• "Show me total revenue by ticket type"


---

## Exercise 2: Filtering and Business Logic (15 minutes)

Learn to add business rules and constraints:

Example: VIP customer analysis

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mixtral-8x7b',
    'Create SQL: "How many VIP customers do we have and what is their average revenue?"
     Use CUSTOMERS table where is_vip = TRUE'
) as vip_analysis_sql;
```

**🖼️ SCREENSHOT PLACEHOLDER: VIP Customer Analysis**
*Caption: Results showing VIP customer count and average revenue in a formatted table. The query should display both the count of VIP customers and their average revenue clearly labeled.*

**Practice Scenarios:**

• Filter by date ranges (last 30 days, current quarter)

• Customer segmentation (age groups, loyalty tiers)

• Park-specific performance analysis


---

## Exercise 3: Time-Based Analysis (15 minutes)

Master temporal queries for trend analysis:

Example: Monthly revenue trends

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-70b',
    'Create SQL: "Show me monthly revenue trends for the last 12 months"
     Use DATE_TRUNC function and order chronologically'
) as trend_analysis_sql;
```

**🖼️ SCREENSHOT PLACEHOLDER: Revenue Trends Analysis**
*Caption: Time-based query results showing monthly revenue data in chronological order with clear month and revenue columns. Should display 12 months of data with visible trends.*

**Time Patterns to Master:**

• Month-over-month growth

• Seasonal analysis

• Year-over-year comparisons

• Peak vs. off-peak performance


---

## Exercise 4: Multi-Table Analysis (15 minutes)

Combine data from multiple business entities:

Example: Customer transaction analysis

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3-70b',
    'Create SQL: "Show customer names with their total spent and transaction count"
     Join CUSTOMERS and SALES_TRANSACTIONS on customer_id'
) as customer_analysis_sql;
```

**🖼️ SCREENSHOT PLACEHOLDER: Multi-Table Join Results**
*Caption: Results showing customer names, total spending, and transaction counts from the joined CUSTOMERS and SALES_TRANSACTIONS tables. Clear columns for customer_name, total_spent, and transaction_count.*

**Join Patterns to Practice:**

• Customer + Transaction data

• Park + Performance metrics

• Marketing + Sales attribution

• Operations + Financial impact


---

## Prompt Engineering Best Practices

#### Effective Prompts ✓

```sql
'You are a SQL expert for UDX theme parks. Convert this to Snowflake SQL: 
"[BUSINESS QUESTION]" 
Use tables: [TABLE NAMES]
Business context: [RELEVANT RULES]
Return only SQL code.'
```

**🖼️ SCREENSHOT PLACEHOLDER: Effective Prompt Example**
*Caption: Snowsight showing a well-structured Cortex prompt with clear business context and the high-quality SQL response generated. The prompt should show good structure and the response should be properly formatted SQL.*

#### Ineffective Prompts ✗

```sql
'Write SQL for revenue'  -- Too vague and lacks context
```

**🖼️ SCREENSHOT PLACEHOLDER: Ineffective Prompt Results**
*Caption: Snowsight showing a vague prompt and the poor or unclear SQL response it generates. This should demonstrate why context is important for good AI-generated queries.*

### Business Question Categories

| Category | Example Questions | Tables Used |
|----------|------------------|-------------|
| Revenue Analytics | "Total revenue by park" | SALES_TRANSACTIONS, PARK_PERFORMANCE |
| Customer Insights | "Top loyal customers" | CUSTOMERS, SALES_TRANSACTIONS |
| Operations | "Guest satisfaction trends" | PARK_PERFORMANCE, ATTRACTION_ANALYTICS |
| Marketing | "Campaign ROI analysis" | MARKETING_CAMPAIGNS, SALES_TRANSACTIONS |

**🖼️ SCREENSHOT PLACEHOLDER: Business Categories Dashboard**
*Caption: Results showing examples from each business category - revenue numbers, customer rankings, satisfaction scores, and ROI calculations displayed in separate result tabs or panels.*

### Success Criteria

□ Generate accurate SQL for simple business questions

□ Understand and modify AI-generated queries

□ Apply business context to improve accuracy

□ Validate results for business reasonableness


---

## Results Analysis and Validation Guide

#### Result Quality Checklist

**🖼️ SCREENSHOT PLACEHOLDER: Quality Results Example**
*Caption: Snowsight results panel showing well-formatted query results with proper column headers, reasonable data types, and business-meaningful values. The results should demonstrate good data quality.*

**Data Quality Indicators:**
□ Column headers are descriptive and business-friendly
□ Data types match expectations (numbers, dates, text)
□ No unexpected NULL values in key columns
□ Row counts are reasonable for the business question
□ Calculations appear mathematically correct
□ Date ranges align with filter criteria

**🖼️ SCREENSHOT PLACEHOLDER: Results Validation Process**
*Caption: Split screen showing original business question, generated SQL query, and results side-by-side to demonstrate the complete validation process from question to answer.*

#### Common Result Patterns to Recognize

**Revenue Analysis Results:**
• Total values should be positive numbers
• Percentages should be between 0-100%
• Growth rates can be positive or negative
• Date ranges should match query filters

**Customer Analysis Results:**
• Customer IDs should be unique where expected
• Counts should be whole numbers
• Average values should be reasonable for the metric
• Top N lists should be properly ordered

**🖼️ SCREENSHOT PLACEHOLDER: Multiple Result Types**
*Caption: Snowsight showing different types of query results - revenue totals, customer rankings, time-based trends, and operational metrics displayed in separate result tabs.*


### Troubleshooting Common Issues

**🖼️ SCREENSHOT PLACEHOLDER: Error Messages Guide**
*Caption: Snowsight showing common error messages (syntax error, permission denied, table not found) with clear error highlighting and suggested solutions visible.*

**Common Error Solutions:**
• **Syntax Error**: Check SQL formatting, missing commas, unmatched quotes
• **Table/Column Not Found**: Verify context (warehouse/database/schema)
• **Permission Denied**: Check role permissions or switch to appropriate role
• **Query Timeout**: Add LIMIT clause or increase warehouse size
• **Cortex Error**: Verify Cortex AI is enabled for your account

**🖼️ SCREENSHOT PLACEHOLDER: Successful Error Resolution**
*Caption: Before/after view showing an error message being resolved - the error state and then the successful query execution with proper results.*

---

## LAB 03: ADVANCED QUERY TRANSLATION (90 minutes)

### Learning Objectives

• Handle complex multi-step business logic

• Implement conversational context management

• Create reusable query patterns and templates

• Build enterprise-grade error handling

### Advanced Features Development

#### Part A: Complex Business Logic (25 minutes)

Focus: Multi-step calculations and business rules

**🖼️ SCREENSHOT PLACEHOLDER: Complex Logic Worksheet**
*Caption: New Snowsight worksheet for Lab 03 showing complex business logic functions and multi-step calculations. The editor should display sophisticated SQL with CTEs and window functions.*

Example: Customer Lifetime Value calculation

```sql
CREATE OR REPLACE FUNCTION calculate_customer_clv(customer_segments ARRAY)
RETURNS TABLE(customer_id STRING, clv_score NUMBER, segment STRING)
LANGUAGE SQL
AS
$$
    SELECT 
        c.customer_id,
        (c.total_lifetime_revenue * 0.4) + 
        (c.visit_frequency * 50) + 
        (c.loyalty_points * 0.01) as clv_score,
        CASE 
            WHEN clv_score > 1000 THEN 'VIP'
            WHEN clv_score > 500 THEN 'Premium'
            ELSE 'Standard'
        END as segment
    FROM CUSTOMERS c
    WHERE ARRAY_CONTAINS(customer_segments, c.age_group)
$$;
```

Skills to Master:
• Window functions for rankings and trends
• CASE statements for business categorization
• Subqueries for complex filtering
• Common Table Expressions (CTEs) for readability

#### Part B: Conversational Context (25 minutes)

Focus: Multi-turn dialogue management

Build conversation memory:

```sql
CREATE OR REPLACE FUNCTION continue_conversation(
    session_id STRING,
    user_question STRING,
    context_depth INTEGER DEFAULT 3
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    conversation_history STRING;
    enhanced_prompt STRING;
    ai_response VARIANT;
BEGIN
    -- Get recent conversation context
    SET conversation_history = (
        SELECT LISTAGG(
            CONCAT('Q: ', user_question, ' | A: ', generated_sql),
            ' || '
        )
        FROM CONVERSATION_HISTORY 
        WHERE session_id = session_id
        ORDER BY created_at DESC
        LIMIT context_depth
    );
    
    -- Build context-aware prompt
    SET enhanced_prompt = CONCAT(
        'Previous conversation: ', COALESCE(conversation_history, 'None'),
        ' | Current question: ', user_question,
        ' | Generate SQL for UDX theme park analytics'
    );
    
    -- Get AI response with context
    SET ai_response = PARSE_JSON(
        SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', enhanced_prompt)
    );
    
    RETURN ai_response;
END;
$$;
```

Conversation Patterns:
• Follow-up questions: "Show me the details for those customers"
• Refinements: "Actually, just show the last 30 days"
• Drill-downs: "What about by individual park?"

#### Part C: Query Templates & Patterns (20 minutes)

Focus: Reusable business intelligence patterns

Create template library:

```sql
INSERT INTO QUERY_PATTERNS VALUES
('TREND_ANALYSIS', 
 'Show {metric} trends over {time_period}',
 'SELECT DATE_TRUNC({period}, {date_column}), {aggregation}({metric}) 
  FROM {table} 
  WHERE {date_column} >= {start_date} 
  GROUP BY DATE_TRUNC({period}, {date_column}) 
  ORDER BY 1',
 'Time series analysis for business metrics'),
 
('TOP_N_ANALYSIS',
 'Show top {N} {entity} by {metric}',
 'SELECT {entity_columns}, {metric}
  FROM {table}
  ORDER BY {metric} DESC
  LIMIT {N}',
 'Ranking analysis for performance metrics');
```

#### Part D: Error Handling & Validation (20 minutes)

Focus: Enterprise-grade reliability

```sql
CREATE OR REPLACE FUNCTION safe_ai_query_generation(
    user_question STRING,
    max_retries INTEGER DEFAULT 3
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    attempt INTEGER := 1;
    result VARIANT;
    error_msg STRING;
BEGIN
    WHILE attempt <= max_retries DO
        TRY
            SELECT PARSE_JSON(
                SNOWFLAKE.CORTEX.COMPLETE(
                    'mixtral-8x7b',
                    CONCAT('Generate valid Snowflake SQL for: ', user_question)
                )
            ) INTO result;
            
            -- Validate the generated SQL
            IF result:sql IS NOT NULL THEN
                RETURN OBJECT_CONSTRUCT(
                    'success', TRUE,
                    'sql', result:sql,
                    'attempts', attempt
                );
            END IF;
            
        EXCEPTION
            WHEN statement_error THEN
                SET error_msg = SQLERRM;
                SET attempt = attempt + 1;
        END;
    END WHILE;
    
    RETURN OBJECT_CONSTRUCT(
        'success', FALSE,
        'error', error_msg,
        'attempts', attempt - 1
    );
END;
$$;
```

### Success Criteria
□ Handle complex multi-table business scenarios
□ Maintain conversation context across multiple queries
□ Create reusable query patterns for common questions
□ Implement robust error handling and validation

---

## LAB 04: FINAL CHALLENGE (90 minutes)

### The Ultimate Challenge

Build a complete, production-ready Natural Language to SQL Assistant that democratizes data access across UDX theme park operations.

### Your Mission: Choose Your Focus

#### Option A: Executive Dashboard Assistant 
(Recommended for Business-Focused Students)

Build: AI-powered executive dashboard with natural language querying

```sql
CREATE OR REPLACE FUNCTION executive_assistant(user_question STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    executive_context STRING := 'You are an executive business intelligence assistant for UDX theme parks. 
                                Focus on high-level KPIs, strategic insights, and actionable recommendations.';
    enhanced_prompt STRING;
    response VARIANT;
BEGIN
    SET enhanced_prompt = CONCAT(
        executive_context,
        ' User question: ', user_question,
        ' Provide: 1) SQL query, 2) Business interpretation, 3) Strategic recommendations'
    );
    
    SET response = PARSE_JSON(
        SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', enhanced_prompt)
    );
    
    RETURN response;
END;
$$;
```

Key Features to Build:
• Revenue trend analysis with forecasting
• Cross-park performance comparisons
• Customer segment profitability analysis
• Operational efficiency metrics
• Strategic recommendation engine

#### Option B: Operations Command Center 
(Recommended for Technical Students)

Build: Real-time operational analytics with alerting

```sql
CREATE OR REPLACE FUNCTION operations_monitor(metric_type STRING, threshold NUMBER)
RETURNS TABLE(alert_type STRING, park_name STRING, current_value NUMBER, threshold_value NUMBER)
LANGUAGE SQL
AS
$$
    SELECT 
        CASE 
            WHEN guest_satisfaction_score < threshold THEN 'SATISFACTION_ALERT'
            WHEN capacity_utilization > threshold THEN 'CAPACITY_ALERT'
            ELSE 'NORMAL'
        END as alert_type,
        park_name,
        CASE metric_type
            WHEN 'satisfaction' THEN guest_satisfaction_score
            WHEN 'capacity' THEN capacity_utilization
        END as current_value,
        threshold as threshold_value
    FROM PARK_PERFORMANCE
    WHERE performance_date = CURRENT_DATE()
    AND (
        (metric_type = 'satisfaction' AND guest_satisfaction_score < threshold) OR
        (metric_type = 'capacity' AND capacity_utilization > threshold)
    )
$$;
```

#### Option C: Marketing Intelligence Platform 
(Recommended for Analytics Students)

Build: Customer analytics and campaign optimization system

```sql
CREATE OR REPLACE FUNCTION marketing_insights(analysis_type STRING, time_period INTEGER)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    insights VARIANT;
BEGIN
    SET insights = CASE analysis_type
        WHEN 'customer_segments' THEN (
            SELECT OBJECT_CONSTRUCT(
                'total_customers', COUNT(*),
                'segments', OBJECT_CONSTRUCT(
                    'vip_customers', COUNT(CASE WHEN is_vip THEN 1 END),
                    'average_clv', AVG(total_lifetime_revenue),
                    'top_age_group', MODE(age_group)
                )
            )
            FROM CUSTOMERS
        )
        WHEN 'campaign_performance' THEN (
            SELECT OBJECT_CONSTRUCT(
                'roi', AVG(return_on_ad_spend),
                'conversion_rate', AVG(conversions / impressions * 100),
                'best_channel', (
                    SELECT channel 
                    FROM MARKETING_CAMPAIGNS 
                    WHERE campaign_start_date >= CURRENT_DATE() - time_period
                    ORDER BY return_on_ad_spend DESC 
                    LIMIT 1
                )
            )
            FROM MARKETING_CAMPAIGNS
            WHERE campaign_start_date >= CURRENT_DATE() - time_period
        )
    END;
    
    RETURN insights;
END;
$$;
```

### Implementation Roadmap (90 minutes)

#### Snowsight Setup for Final Challenge

**Create Dedicated Workspace:**
• New worksheet: "Lab 04 - Final Challenge - [Your Focus Area]"
• Example: "Lab 04 - Final Challenge - Executive Dashboard"
• Ensure proper context is set and verified
• Consider creating multiple worksheets if building different components

**Organization Strategy:**
• Use clear section headers for each phase
• Comment your architectural decisions
• Save milestone versions (e.g., "Phase 1 Complete")
• Keep working code separate from experimental code

#### Phase 1: Architecture & Planning (20 minutes)
1. Choose your focus area (Executive/Operations/Marketing)
2. Design system architecture:
   User Input → Intent Recognition → Context Management → 
   SQL Generation → Query Execution → Result Explanation → 
   Visualization Suggestions → Follow-up Questions
3. Plan your data model integration
4. Define success metrics

#### Phase 2: Core Engine Development (40 minutes)
1. Build intent recognition system
2. Implement context-aware SQL generation
3. Create result explanation system

#### Phase 3: Integration & Enhancement (20 minutes)
1. Add conversation memory
2. Implement error handling and fallbacks
3. Create role-based customization
4. Add visualization recommendations

#### Phase 4: Testing & Validation (10 minutes)
1. Test with business scenarios
2. Validate business logic
3. Check error handling
4. Verify role-based responses

### Evaluation Criteria

#### Functionality (40%)
• Query Accuracy: >90% success rate for business questions
• Conversation Flow: Natural multi-turn dialogues
• Business Logic: Correct calculations and business rules
• Error Handling: Graceful failure and recovery

#### Technical Excellence (25%)
• Code Quality: Clean, documented, maintainable
• Performance: Sub-3-second response times
• Security: Role-based access and data governance
• Scalability: Handles increasing query complexity

#### Innovation (20%)
• Creative AI Usage: Novel applications of Cortex capabilities
• User Experience: Intuitive and helpful interactions
• Business Value: Clear ROI and productivity gains
• Future-Proofing: Extensible architecture

#### Business Impact (15%)
• Real-World Applicability: Solves actual UDX challenges
• User Adoption Potential: Appeals to target personas
• Change Management: Considers training and adoption
• Measurable Benefits: Quantifiable business improvements

### Success Criteria
□ Complete NLP2SQL engine with >90% accuracy
□ Conversational interface with context memory
□ Role-based customization (Executive/Operations/Marketing)
□ Error handling and graceful failures
□ Business-friendly result explanations
□ Demonstration with real UDX scenarios

---

## LAB 05: AGENTS & INTELLIGENCE (60 minutes)

### Learning Objectives
• Transform individual AI functions into orchestrated agent workflows
• Integrate structured data analysis with unstructured document search
• Prepare data for Snowflake Intelligence portal access
• Build advanced conversational experiences with multi-tool coordination

### From Functions to Agents: The Evolution

#### What You've Built So Far
```sql
-- Individual AI function calls
SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Convert to SQL: ...');
```

#### What You're Building Now
```sql
-- Orchestrated agent workflows that can:
-- 1. Understand complex intent
-- 2. Route to appropriate tools  
-- 3. Execute multi-step analysis
-- 4. Provide comprehensive responses
```

### Step-by-Step Agent Development

#### Snowsight Setup for Agents Lab

**Create Agent Development Workspace:**
• New worksheet: "Lab 05 - Agents & Intelligence"
• **Important**: This lab uses files from `05-agents-intelligence/` folder
• Verify context matches your existing setup
• You'll be executing: `setup.sql`, `exercises.sql`, and `solutions.sql`

#### Step 1: Document Knowledge Base (15 minutes)

Create a comprehensive knowledge repository for business context

File: 05-agents-intelligence/setup.sql

Load UDX business documents:

```sql
INSERT INTO UDX_DOCUMENTS VALUES
('POLICY_SAFETY_001', 'Guest Safety Protocols', 
 'All rides must undergo daily safety inspections...', 
 'SAFETY_POLICY', 'OPERATIONS'),
('PROC_REVENUE_001', 'Revenue Recognition Standards',
 'Ticket sales recognized at point of entry...', 
 'FINANCIAL_PROCEDURE', 'FINANCE');

-- Create Cortex Search service
CREATE OR REPLACE CORTEX SEARCH SERVICE udx_knowledge_base
ON table_name = 'UDX_NL2SQL.BUSINESS_ANALYTICS.UDX_DOCUMENTS'
ATTRIBUTES = ('DOCUMENT_CONTENT', 'DOCUMENT_TYPE', 'DEPARTMENT')
WAREHOUSE = 'UDX_ANALYTICS_WAREHOUSE';
```

#### Step 2: Agent Configuration (15 minutes)

Build role-specific agents for different business users

```sql
-- Create executive agent
SELECT create_role_specific_agent('executive') as executive_agent_config;

-- Create operations agent  
SELECT create_role_specific_agent('operations_manager') as ops_agent_config;

-- Create marketing agent
SELECT create_role_specific_agent('marketing_team') as marketing_agent_config;
```

Agent Capabilities by Role:

| Role | Focus Areas | Data Access | Response Style |
|------|-------------|-------------|----------------|
| Executive | Revenue trends, strategic KPIs | All parks | Executive summary |
| Operations | Guest satisfaction, efficiency | Assigned park | Operational detail |
| Marketing | Customer analytics, campaigns | Customer data | Campaign-focused |
| Finance | Revenue recognition, costs | Financial data | Financial analysis |

#### Step 3: Multi-Modal Analysis (15 minutes)

Combine structured data with unstructured documents

Example: Comprehensive business analysis
Question: "Show me parks with safety issues and our safety policies"

Step 1: Analyze structured data

```sql
SELECT 
    park_name,
    AVG(guest_satisfaction_score) as avg_satisfaction,
    CASE WHEN AVG(guest_satisfaction_score) < 7 THEN 'Review Safety Protocols' 
         ELSE 'Satisfactory' END as safety_status
FROM PARK_PERFORMANCE 
WHERE performance_date >= CURRENT_DATE() - 30
GROUP BY park_name;
```

Step 2: Search relevant policies

```sql
SELECT SNOWFLAKE.CORTEX.SEARCH(
    'udx_knowledge_base',
    'safety protocols incident reporting emergency procedures'
) as safety_policies;
```

Step 3: Generate integrated recommendations
(Agent orchestrates both data analysis and document search)

#### Step 4: Enhanced Conversations (15 minutes)

Build sophisticated dialogue management

```sql
-- Start enhanced conversation
SELECT continue_agent_conversation(
    'session_001',
    'What are our top performing parks by guest satisfaction this month?',
    'manager_001', 
    'operations_manager'
) as conversation_start;

-- Follow up with context
SELECT continue_agent_conversation(
    'session_001',
    'What policies do we have for maintaining high guest satisfaction?',
    'manager_001',
    'operations_manager' 
) as conversation_followup;

-- Examine conversation context
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
```

### Snowflake Intelligence Integration

#### Prepare Data for Intelligence Portal

```sql
-- Create Intelligence-ready views
CREATE OR REPLACE VIEW INTELLIGENCE_PARK_ANALYTICS AS
SELECT 
    'UDX Theme Parks' as data_source,
    p.park_name,
    s.transaction_date,
    SUM(s.revenue_amount) as daily_revenue,
    COUNT(DISTINCT s.customer_id) as unique_visitors,
    AVG(p.guest_satisfaction_score) as avg_satisfaction
FROM SALES_TRANSACTIONS s
JOIN PARK_PERFORMANCE p ON s.park_id = p.park_id 
GROUP BY p.park_name, s.transaction_date;

-- Grant access for Intelligence portal
GRANT SELECT ON VIEW INTELLIGENCE_PARK_ANALYTICS TO ROLE INTELLIGENCE_USER;
```

### Business Scenarios to Test

#### Scenario 1: Executive Multi-Modal Query
"Our California park has declining satisfaction. What's causing it and what policies should guide our response?"

Expected Agent Workflow:
1. Data Analysis: Query satisfaction trends and operational metrics
2. Document Search: Find customer service policies and operational procedures  
3. Integration: Combine insights for comprehensive recommendations
4. Visualization: Suggest charts and dashboards
5. Follow-up: Propose specific action items

#### Scenario 2: Operations Cross-Reference
"Show me attractions with high wait times and our capacity management policies"

Expected Agent Workflow:
1. Structured Query: Analyze current wait times and capacity utilization
2. Policy Search: Find capacity management and guest flow procedures
3. Correlation: Match operational issues with policy guidance
4. Recommendations: Suggest specific operational adjustments

### Advanced Agent Features

#### A/B Testing Framework

```sql
-- Compare traditional vs agent approaches
INSERT INTO APPROACH_COMPARISON VALUES
('TEST_001', 
 'What is our revenue trend by park this quarter?',
 '{"method": "traditional", "accuracy": 0.85, "time": 1200}',
 '{"method": "agent", "accuracy": 0.95, "time": 1800}',
 'Agent more accurate but slower',
 'Agent provides richer context');
```

#### Performance Monitoring

```sql
-- Track agent effectiveness
SELECT calculate_agent_performance(CURRENT_DATE()) as performance_metrics;

-- Analyze conversation patterns  
SELECT 
    user_role,
    AVG(response_time_ms) as avg_response_time,
    AVG(response_confidence) as avg_confidence,
    COUNT(*) as total_conversations
FROM AGENT_CONVERSATIONS
GROUP BY user_role;
```

### Success Criteria
□ Document knowledge base with semantic search
□ Role-specific agent configurations
□ Multi-modal analysis combining data + documents
□ Enhanced conversation management with context
□ Intelligence-ready data views
□ Performance monitoring and optimization

---

## PROJECT COMPLETION & DEMONSTRATION

### Final Deliverables Checklist

#### Core System ✓
□ Complete NLP2SQL Engine: Accurate translation for business questions
□ Conversational Interface: Multi-turn dialogue with context memory
□ Business Integration: Domain-specific terminology and calculations
□ Error Handling: Graceful failures and helpful error messages
□ Role-Based Access: Customized responses for different user types

#### Advanced Features ✓
□ Agent Orchestration: Multi-tool workflows for complex analysis
□ Document Integration: Combine structured data with business policies
□ Intelligence Preparation: Ready for Snowflake Intelligence portal
□ Performance Monitoring: Track accuracy, speed, and user satisfaction
□ Governance Framework: Security, audit trails, and compliance

### Demonstration Script (10 minutes)

#### Opening (2 minutes)
"Today I'll demonstrate how we've transformed UDX's data accessibility using Snowflake Cortex AI. Business users can now ask questions in plain English and get instant, accurate insights."

#### Core Functionality Demo (4 minutes)
```sql
-- Executive Question
"Show me our Q3 revenue performance compared to last year across all parks"

-- Operations Question  
"Which attractions have guest satisfaction below 7.5 this week?"

-- Marketing Question
"What's the ROI of our summer social media campaigns by customer segment?"
```

#### Advanced Features Demo (3 minutes)
```sql
-- Multi-Modal Analysis
"Our Florida park has declining satisfaction. What policies should guide our response?"

-- Conversational Context
"Show me the details for that park"
"What about just the last 30 days?"
"How does this compare to our other parks?"
```

#### Business Impact Summary (1 minute)
• Productivity: 10x faster than traditional BI tools
• Accessibility: 95% of business questions answerable by non-technical users
• Accuracy: >90% success rate with business context integration
• Adoption: Ready for enterprise deployment with governance

### Success Metrics

#### Technical Performance
• Query Accuracy: >90% for common business patterns
• Response Time: <3 seconds for typical questions
• Conversation Flow: Natural multi-turn dialogues
• Error Recovery: Helpful suggestions when queries fail

#### Business Value
• User Productivity: 10x improvement in time-to-insight
• Data Democratization: Non-technical users can access complex analytics
• Decision Speed: Real-time insights for operational decisions
• ROI: Measurable reduction in analyst workload

#### Innovation Factors
• AI Integration: Creative use of Cortex capabilities
• User Experience: Intuitive and helpful interactions
• Scalability: Handles increasing query complexity
• Future-Proofing: Ready for agent and intelligence evolution

---

## LEARNING OUTCOMES & NEXT STEPS

### What You've Accomplished

By completing this hackathon, you've built expertise in:

#### Technical Skills
✓ Snowflake Cortex AI: Master prompt engineering and AI orchestration
✓ SQL Generation: Translate business logic into optimized queries
✓ Conversation Management: Build context-aware dialogue systems
✓ Agent Architecture: Orchestrate multi-tool workflows
✓ Enterprise Integration: Security, governance, and scalability

#### Business Skills
✓ Requirements Analysis: Understand stakeholder needs across departments
✓ Data Storytelling: Explain complex analytics in business terms
✓ Change Management: Design systems for user adoption
✓ ROI Calculation: Quantify business value of AI implementations

#### Innovation Mindset
✓ AI-First Thinking: Leverage AI to solve traditional problems differently
✓ User-Centric Design: Build technology that serves business users
✓ Future Readiness: Prepare for the next wave of AI capabilities

### Career Applications

#### For Data Engineers
• Apply these patterns to build AI-enhanced data platforms
• Create conversational interfaces for data pipelines
• Implement intelligent data quality and monitoring systems

#### For Business Analysts
• Democratize analytics across your organization
• Build self-service BI tools for non-technical stakeholders
• Create domain-specific AI assistants for your industry

#### For Product Managers
• Design AI-powered user experiences
• Understand the art of the possible with conversational AI
• Build roadmaps for AI integration in existing products

#### For Consultants
• Offer AI transformation services to clients
• Demonstrate ROI of modern data stack investments
• Build reusable accelerators for multiple industries

### Future Learning Paths

#### Advanced Snowflake AI
• Explore Snowflake ML and advanced Cortex features
• Build real-time streaming analytics with AI
• Implement federated learning across data clouds

#### Conversational AI Systems
• Study dialogue state management
• Learn about intent recognition and entity extraction
• Explore voice interfaces and multimodal interactions

#### AI Engineering
• Master prompt engineering and model fine-tuning
• Learn about AI governance and responsible AI practices
• Explore agentic AI and autonomous systems

#### Business Intelligence Evolution
• Study the future of self-service analytics
• Learn about augmented analytics and automated insights
• Explore real-time decision support systems

---

## CONGRATULATIONS!

You've successfully built a revolutionary Natural Language to SQL system that transforms how business users interact with data. Your solution demonstrates the power of AI to democratize analytics and create more intuitive, efficient ways of working with data.

### Key Achievements
• Technical Excellence: Built a production-ready AI system
• Business Impact: Created genuine value for UDX stakeholders  
• Innovation: Pushed the boundaries of conversational analytics
• Future Readiness: Prepared for the next generation of AI capabilities

### What's Next?
Take your skills and apply them to real-world challenges. The future of business intelligence is conversational, intelligent, and accessible to everyone. You're now equipped to lead that transformation.

Keep building the future! 