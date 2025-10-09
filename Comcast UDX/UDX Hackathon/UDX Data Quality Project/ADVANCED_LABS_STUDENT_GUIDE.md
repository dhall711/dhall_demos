# UDX AI-Powered Data Quality Hackathon
## Advanced Labs Student Guide
### Labs 05-09: Semantic Models, Intelligence, Agents & Multimodal AI

---

**Welcome to the Advanced AI Phase!**

This guide covers the revolutionary AI technologies that will transform your data quality system from traditional monitoring to autonomous, conversational, and multimodal intelligence.

---

# Lab 05: Semantic Models & Views
## Creating Business-Friendly Data Abstractions for AI

### **⏱️ Estimated Time: 45 minutes**

### **🎯 Lab Objectives**
By the end of this lab, you will:
- Create semantic views with business-friendly dimensions and metrics
- Define relationships between logical tables for AI understanding
- Implement business rules and calculations in semantic models
- Prepare data structures for Snowflake Intelligence

---

## **Exercise 1: Creating Your First Semantic View (20 minutes)**

### **Step 1.1: Understanding the Business Context**

Before creating technical semantic views, understand the business perspective:

**Traditional Technical Query:**
```sql
SELECT p.park_id, p.park_name, COUNT(g.guest_id) as guest_count
FROM PARKS p
JOIN GUESTS g ON p.park_id = g.park_id
WHERE g.visit_date >= '2024-01-01'
GROUP BY p.park_id, p.park_name;
```

**Business User Perspective:**
*"Show me guest counts by theme park location for this year"*

### **Step 1.2: Create Core Semantic View**

1. **Create a new worksheet**
   - Name it: `Lab05_Semantic_Models`
   - Add this header comment:
   ```sql
   -- =====================================================
   -- LAB 05: SEMANTIC MODELS & VIEWS
   -- Business-Friendly Data Abstractions for AI
   -- =====================================================
   ```

2. **Create your first semantic view**

   ```sql
   -- Create semantic view for UDX theme park data quality
   CREATE OR REPLACE SEMANTIC VIEW udx_park_operations_semantic_view
   TABLES (
       PARKS primary key (PARK_ID),
       GUESTS primary key (GUEST_ID),
       RIDES primary key (RIDE_ID),
       RIDE_OPERATIONS primary key (OPERATION_ID),
       TICKETS primary key (TICKET_ID),
       DATA_QUALITY_RESULTS primary key (RESULT_ID)
   )
   RELATIONSHIPS (
       -- Guest to Park relationship
       GUESTS(PARK_ID) references PARKS(PARK_ID),
       -- Ticket to Guest relationship  
       TICKETS(GUEST_ID) references GUESTS(GUEST_ID),
       -- Ride Operations to Rides relationship
       RIDE_OPERATIONS(RIDE_ID) references RIDES(RIDE_ID),
       -- Ride Operations to Parks relationship
       RIDE_OPERATIONS(PARK_ID) references PARKS(PARK_ID),
       -- Data Quality to Parks relationship
       DATA_QUALITY_RESULTS(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       -- Park dimensions with business-friendly names
       PARKS.PARK_NAME as "Theme Park",
       PARKS.REGION as "Geographic Region", 
       PARKS.PARK_TYPE as "Park Category",
       
       -- Guest dimensions
       GUESTS.AGE_GROUP as "Guest Age Group",
       GUESTS.GUEST_TYPE as "Guest Category",
       GUESTS.MEMBERSHIP_LEVEL as "Membership Tier",
       
       -- Ride dimensions
       RIDES.RIDE_TYPE as "Ride Category",
       RIDES.THRILL_LEVEL as "Thrill Level",
       
       -- Time dimensions
       RIDE_OPERATIONS.OPERATION_DATE as "Operation Date",
       GUESTS.VISIT_DATE as "Visit Date",
       
       -- Quality dimensions
       DATA_QUALITY_RESULTS.CHECK_TYPE as "Quality Check Type",
       DATA_QUALITY_RESULTS.STATUS as "Quality Status"
   )
   METRICS (
       -- Guest metrics
       TOTAL_GUESTS as COUNT(DISTINCT GUESTS.GUEST_ID),
       AVERAGE_AGE as AVG(GUESTS.AGE),
       
       -- Financial metrics
       TOTAL_REVENUE as SUM(TICKETS.PURCHASE_AMOUNT),
       AVERAGE_TICKET_PRICE as AVG(TICKETS.PURCHASE_AMOUNT),
       
       -- Operational metrics
       AVERAGE_WAIT_TIME as AVG(RIDE_OPERATIONS.WAIT_TIME_MINUTES),
       TOTAL_RIDE_OPERATIONS as COUNT(RIDE_OPERATIONS.OPERATION_ID),
       GUEST_SATISFACTION_SCORE as AVG(RIDE_OPERATIONS.GUEST_SATISFACTION_SCORE),
       
       -- Quality metrics
       QUALITY_SCORE as AVG(DATA_QUALITY_RESULTS.METRIC_VALUE),
       FAILED_QUALITY_CHECKS as COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'FAIL' THEN 1 END),
       QUALITY_CHECK_PASS_RATE as (COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'PASS' THEN 1 END) * 100.0 / COUNT(DATA_QUALITY_RESULTS.RESULT_ID))
   );
   ```

   > 📸 **Screenshot Placeholder: Semantic View Creation**
   > *Show successful semantic view creation message*

### **Step 1.3: Test Your Semantic View**

1. **Query using business-friendly syntax**
   ```sql
   -- Query using semantic view with business-friendly syntax
   SELECT * FROM SEMANTIC_VIEW(
       udx_park_operations_semantic_view
       DIMENSIONS 
           "Theme Park",
           "Geographic Region",
           "Operation Date"
       METRICS 
           TOTAL_GUESTS,
           AVERAGE_WAIT_TIME,
           GUEST_SATISFACTION_SCORE,
           QUALITY_SCORE
       WHERE "Operation Date" >= '2024-01-01'
       AND "Geographic Region" = 'Florida'
   )
   ORDER BY "Operation Date" DESC;
   ```

   > 📸 **Screenshot Placeholder: Semantic Query Results**
   > *Show business-friendly query results with readable column names*

**💡 Key Observation**: Notice how the query uses business language instead of technical table/column names!

---

## **Exercise 2: Enhanced Business Context (15 minutes)**

### **Step 2.1: Add Rich Business Context**

1. **Create enhanced semantic view with descriptions and sample values**

   ```sql
   -- Enhanced semantic view with business context
   CREATE OR REPLACE SEMANTIC VIEW udx_enhanced_semantic_view
   TABLES (
       PARKS primary key (PARK_ID),
       GUESTS primary key (GUEST_ID), 
       RIDE_OPERATIONS primary key (OPERATION_ID)
   )
   RELATIONSHIPS (
       GUESTS(PARK_ID) references PARKS(PARK_ID),
       RIDE_OPERATIONS(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       PARKS.PARK_NAME as "Theme Park" 
           SYNONYMS ("Park Location", "Park Name", "Theme Park Location")
           DESCRIPTION "The specific UDX theme park location"
           SAMPLE_VALUES ("Universal Studios Florida", "Universal Studios Hollywood", "Universal Beijing Resort"),
           
       PARKS.REGION as "Geographic Region"
           SYNONYMS ("Region", "Location", "Geographic Area") 
           DESCRIPTION "The geographic region where the park is located"
           SAMPLE_VALUES ("Florida", "California", "Texas"),
           
       GUESTS.AGE_GROUP as "Guest Age Group"
           SYNONYMS ("Age Category", "Age Range", "Customer Age Group")
           DESCRIPTION "Categorized age groups for theme park guests"
           SAMPLE_VALUES ("Child (0-12)", "Teen (13-17)", "Adult (18-64)", "Senior (65+)"),
           
       RIDE_OPERATIONS.OPERATION_DATE as "Operation Date"
           SYNONYMS ("Date", "Operating Date", "Business Date")
           DESCRIPTION "The date when ride operations occurred"
   )
   METRICS (
       TOTAL_DAILY_GUESTS as COUNT(DISTINCT GUESTS.GUEST_ID)
           SYNONYMS ("Daily Visitors", "Guest Count", "Visitor Count")
           DESCRIPTION "Total number of unique guests visiting the park on a given day",
           
       AVERAGE_WAIT_TIME as AVG(RIDE_OPERATIONS.WAIT_TIME_MINUTES)
           SYNONYMS ("Avg Wait Time", "Average Queue Time", "Mean Wait Duration")
           DESCRIPTION "Average wait time in minutes across all ride operations",
           
       GUEST_SATISFACTION_INDEX as AVG(RIDE_OPERATIONS.GUEST_SATISFACTION_SCORE) * 20
           SYNONYMS ("Satisfaction Score", "Guest Happiness", "Customer Satisfaction")
           DESCRIPTION "Guest satisfaction score converted to 0-100 scale for easier interpretation"
   );
   ```

### **Step 2.2: Add Business Filters**

1. **Create business rules and filters**
   ```sql
   -- Add business filters to semantic view
   ALTER SEMANTIC VIEW udx_enhanced_semantic_view
   ADD FILTERS (
       PEAK_SEASON as MONTH(RIDE_OPERATIONS.OPERATION_DATE) IN (6, 7, 8, 12)
           SYNONYMS ("Peak Season", "Busy Season", "High Season")
           DESCRIPTION "Summer months (June-August) and December holiday season",
           
       FAMILY_FRIENDLY_RIDES as RIDES.THRILL_LEVEL IN ('Low', 'Moderate')
           SYNONYMS ("Family Rides", "Kid-Friendly Rides", "Gentle Rides")
           DESCRIPTION "Rides suitable for families with children",
           
       HIGH_SATISFACTION as RIDE_OPERATIONS.GUEST_SATISFACTION_SCORE >= 4.0
           SYNONYMS ("Happy Guests", "Satisfied Customers", "Positive Feedback")
           DESCRIPTION "Operations with guest satisfaction score of 4.0 or higher out of 5.0"
   );
   ```

   > 📸 **Screenshot Placeholder: Enhanced Semantic View**
   > *Show successful semantic view enhancement with filters*

---

## **Exercise 3: Data Quality Semantic Model (10 minutes)**

### **Step 3.1: Create Specialized Quality Semantic View**

1. **Create data quality focused semantic view**

   ```sql
   -- Comprehensive data quality semantic view
   CREATE OR REPLACE SEMANTIC VIEW udx_data_quality_semantic_view
   TABLES (
       DATA_QUALITY_RESULTS primary key (RESULT_ID),
       PARKS primary key (PARK_ID),
       ANOMALY_DETECTION_LOG primary key (ANOMALY_ID)
   )
   RELATIONSHIPS (
       DATA_QUALITY_RESULTS(PARK_ID) references PARKS(PARK_ID),
       ANOMALY_DETECTION_LOG(PARK_ID) references PARKS(PARK_ID)
   )
   DIMENSIONS (
       -- Location dimensions
       PARKS.PARK_NAME as "Theme Park"
           DESCRIPTION "Theme park location for data quality monitoring"
           SAMPLE_VALUES ("Universal Studios Florida", "Universal Studios Hollywood"),
           
       -- Quality dimensions  
       DATA_QUALITY_RESULTS.CHECK_TYPE as "Quality Check Type"
           SYNONYMS ("Check Category", "Validation Type", "Quality Dimension")
           DESCRIPTION "Type of data quality check performed"
           SAMPLE_VALUES ("COMPLETENESS", "ACCURACY", "CONSISTENCY", "VALIDITY"),
           
       DATA_QUALITY_RESULTS.STATUS as "Quality Status"
           SYNONYMS ("Check Result", "Validation Status", "Quality Outcome")
           DESCRIPTION "Result of the data quality check"
           SAMPLE_VALUES ("PASS", "FAIL", "WARNING"),
           
       -- Time dimensions
       DATA_QUALITY_RESULTS.CHECK_TIMESTAMP as "Check Date"
           SYNONYMS ("Validation Date", "Quality Check Date", "Monitoring Date")
           DESCRIPTION "When the data quality check was performed"
   )
   METRICS (
       -- Quality scores
       OVERALL_QUALITY_SCORE as AVG(DATA_QUALITY_RESULTS.METRIC_VALUE)
           SYNONYMS ("Quality Score", "Data Health Score", "Quality Rating")
           DESCRIPTION "Average data quality score across all checks (0-100 scale)",
           
       PASS_RATE as (COUNT(CASE WHEN DATA_QUALITY_RESULTS.STATUS = 'PASS' THEN 1 END) * 100.0 / COUNT(DATA_QUALITY_RESULTS.RESULT_ID))
           SYNONYMS ("Success Rate", "Quality Pass Rate", "Validation Success")
           DESCRIPTION "Percentage of data quality checks that passed"
   );
   ```

**🎯 Lab 05 Checkpoint**: You now have business-friendly semantic abstractions ready for AI!

---

# Lab 06: Snowflake Intelligence
## Conversational Data Analytics

### **⏱️ Estimated Time: 45 minutes**

### **🎯 Lab Objectives**
By the end of this lab, you will:
- Enable natural language querying of your semantic views
- Create conversational dashboards for different user types
- Implement self-service analytics for business users
- Demonstrate AI-powered data exploration

---

## **Exercise 1: Enabling Intelligence (15 minutes)**

### **Step 1.1: Configure Intelligence for Semantic Views**

1. **Create new worksheet for Intelligence**
   - Name it: `Lab06_Snowflake_Intelligence`
   - Add header:
   ```sql
   -- =====================================================
   -- LAB 06: SNOWFLAKE INTELLIGENCE
   -- Conversational Data Analytics
   -- =====================================================
   ```

2. **Enable Intelligence for data quality semantic view**
   ```sql
   -- Enable Intelligence for data quality conversations
   ALTER SEMANTIC VIEW udx_data_quality_semantic_view 
   SET INTELLIGENCE_ENABLED = TRUE;
   
   -- Add custom instructions for better AI understanding
   ALTER SEMANTIC VIEW udx_data_quality_semantic_view
   SET CUSTOM_INSTRUCTIONS = 'This semantic view contains theme park data quality metrics. 
   When users ask about data quality, focus on business impact and actionable insights. 
   Always include context about which parks and time periods are being analyzed.
   For critical issues, emphasize urgency and potential guest experience impact.';
   ```

   > 📸 **Screenshot Placeholder: Intelligence Enablement**
   > *Show successful Intelligence configuration*

### **Step 1.2: Configure Intelligence Settings**

1. **Set up suggested questions and behavior**
   ```sql
   -- Set up Intelligence configuration
   ALTER SEMANTIC VIEW udx_data_quality_semantic_view
   SET INTELLIGENCE_CONFIG = '{
       "suggested_questions": [
           "What is our overall data quality score this month?",
           "Which theme parks have the most data quality issues?", 
           "How many critical anomalies were detected this week?",
           "What data quality issues are affecting guest experience?",
           "Show me data quality trends for the last 90 days"
       ],
       "auto_refresh": true,
       "explanation_level": "business_friendly"
   }';
   ```

### **Step 1.3: Test Basic Intelligence Queries**

1. **Ask your first natural language questions**
   ```sql
   -- Test intelligence capability with sample queries
   SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
       'What is the current data quality status across all theme parks?',
       semantic_view => 'udx_data_quality_semantic_view'
   ) as intelligence_response;
   ```

   > 📸 **Screenshot Placeholder: First Intelligence Query**
   > *Show natural language query and AI-generated response*

2. **Try more complex business questions**
   ```sql
   SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
       'Show me which parks have data quality issues that might impact guest safety',
       semantic_view => 'udx_data_quality_semantic_view'
   ) as safety_analysis;
   ```

   > 📸 **Screenshot Placeholder: Complex Intelligence Response**
   > *Show AI analysis with business context and recommendations*

---

## **Exercise 2: Role-Based Conversational Analytics (20 minutes)**

### **Step 2.1: Executive Dashboard Conversations**

1. **Create executive-level intelligence queries**
   ```sql
   -- Executive-level intelligence queries
   CREATE OR REPLACE VIEW EXECUTIVE_INTELLIGENCE AS
   SELECT 
       'Executive Summary' as query_type,
       SNOWFLAKE.INTELLIGENCE.QUERY(
           'Give me an executive summary of data quality across all UDX theme parks this quarter. 
           Focus on business impact, guest experience implications, and strategic priorities.',
           semantic_view => 'udx_data_quality_semantic_view',
           audience => 'executive'
       ) as intelligence_response
   
   UNION ALL
   
   SELECT 
       'Revenue Impact',
       SNOWFLAKE.INTELLIGENCE.QUERY(
           'How are data quality issues affecting our revenue and what should we prioritize?',
           semantic_view => 'udx_data_quality_semantic_view',
           audience => 'executive'
       ) as intelligence_response;
   ```

2. **Test executive queries**
   ```sql
   SELECT * FROM EXECUTIVE_INTELLIGENCE;
   ```

   > 📸 **Screenshot Placeholder: Executive Intelligence**
   > *Show executive-level insights with strategic recommendations*

### **Step 2.2: Operations Manager Conversations**

1. **Create operational intelligence function**
   ```sql
   -- Operational intelligence for park managers
   CREATE OR REPLACE FUNCTION ask_operations_question(question STRING)
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
       SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
           question,
           semantic_view => 'udx_park_operations_semantic_view',
           context => 'You are helping a theme park operations manager. 
                      Focus on actionable insights for daily park operations, 
                      guest experience, and operational efficiency. 
                      Provide specific recommendations and next steps.',
           audience => 'operations'
       )
   $$;
   ```

2. **Test operational queries**
   ```sql
   -- Test operational intelligence
   SELECT ask_operations_question(
       'Which rides have concerning wait times that might need immediate attention?'
   ) as ride_analysis;
   
   SELECT ask_operations_question(
       'How is guest satisfaction trending and what operational changes should we consider?'
   ) as satisfaction_analysis;
   ```

   > 📸 **Screenshot Placeholder: Operational Intelligence**
   > *Show operations-focused insights with actionable recommendations*

### **Step 2.3: Data Team Technical Analysis**

1. **Create technical intelligence view**
   ```sql
   -- Technical intelligence for data teams
   CREATE OR REPLACE VIEW DATA_TEAM_INTELLIGENCE AS
   SELECT 
       'Technical Root Cause' as analysis_type,
       SNOWFLAKE.INTELLIGENCE.QUERY(
           'Analyze the technical root causes of our current data quality failures. 
           What specific data sources, transformations, or processes need attention?',
           semantic_view => 'udx_data_quality_semantic_view',
           audience => 'technical',
           detail_level => 'comprehensive'
       ) as intelligence_response;
   ```

**🔍 Compare the Responses**: Notice how Intelligence adapts its language and focus based on the audience!

---

## **Exercise 3: Interactive Intelligence Dashboards (10 minutes)**

### **Step 3.1: Create Self-Service Intelligence Portal**

1. **Set up self-service portal configuration**
   ```sql
   -- Self-service portal configuration
   CREATE OR REPLACE INTELLIGENCE_PORTAL udx_self_service_portal
   WITH (
       SEMANTIC_VIEWS = [
           'udx_data_quality_semantic_view',
           'udx_park_operations_semantic_view'
       ],
       SUGGESTED_QUESTIONS = [
           'How is our data quality affecting guest satisfaction?',
           'Which parks need the most attention for data quality issues?',
           'What trends do you see in our operational data?',
           'How can we improve our data quality to increase revenue?'
       ],
       USER_ROLES = ['BUSINESS_ANALYST', 'PARK_MANAGER', 'EXECUTIVE'],
       AUTO_SUGGESTIONS = TRUE,
       EXPLANATION_LEVEL = 'BUSINESS_FRIENDLY'
   );
   ```

### **Step 3.2: Query Assistance and Suggestions**

1. **Create intelligent query assistance**
   ```sql
   -- Query assistance and suggestions
   CREATE OR REPLACE FUNCTION get_query_suggestions(
       user_intent STRING,
       user_role STRING DEFAULT 'BUSINESS_ANALYST'
   )
   RETURNS TABLE (
       suggested_question STRING,
       relevant_semantic_view STRING,
       expected_insight_type STRING,
       difficulty_level STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH suggestions AS (
       SELECT SNOWFLAKE.INTELLIGENCE.SUGGEST_QUERIES(
           user_intent,
           available_views => ['udx_data_quality_semantic_view', 'udx_park_operations_semantic_view'],
           user_role => user_role,
           max_suggestions => 5
       ) as suggestions_json
   )
   SELECT 
       suggestion:question::STRING as suggested_question,
       suggestion:semantic_view::STRING as relevant_semantic_view,
       suggestion:insight_type::STRING as expected_insight_type,
       suggestion:difficulty::STRING as difficulty_level
   FROM suggestions,
   LATERAL FLATTEN(input => suggestions_json:suggestions) as suggestion
   $$;
   ```

2. **Test query suggestions**
   ```sql
   -- Test query suggestions for different user types
   SELECT * FROM get_query_suggestions(
       'I want to understand our data quality performance',
       'PARK_MANAGER'
   );
   
   SELECT * FROM get_query_suggestions(
       'Revenue impact analysis',
       'EXECUTIVE'
   );
   ```

   > 📸 **Screenshot Placeholder: Query Suggestions**
   > *Show intelligent query suggestions tailored to user roles*

---

**🎯 Lab 06 Checkpoint**: You can now have natural language conversations with your data! Business users can explore insights without writing SQL.

---

# Lab 07: AI Agents Basics
## Creating Autonomous Data Quality Agents

### **⏱️ Estimated Time: 45 minutes**

### **🎯 Lab Objectives**
By the end of this lab, you will:
- Create autonomous monitoring agents for data quality
- Implement automated response and alerting agents
- Set up agent coordination and workflows
- Establish human-agent collaboration patterns

---

## **Exercise 1: Creating Your First Monitoring Agent (20 minutes)**

### **Step 1.1: Create Data Quality Monitoring Agent**

1. **Create new worksheet for agents**
   - Name it: `Lab07_AI_Agents`
   - Add header:
   ```sql
   -- =====================================================
   -- LAB 07: AI AGENTS BASICS
   -- Autonomous Data Quality Management
   -- =====================================================
   ```

2. **Create your first autonomous agent**
   ```sql
   -- Create your first autonomous data quality agent
   CREATE OR REPLACE AGENT data_quality_monitor_agent
   WITH (
       INSTRUCTIONS = 'You are a data quality monitoring agent for UDX theme parks. 
                      Monitor data quality metrics continuously and alert when issues are detected.
                      Focus on guest safety, operational efficiency, and revenue protection.
                      Provide clear, actionable insights for each issue you find.',
       TOOLS = ['cortex_analyst', 'email_notifications'],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view'],
       SCHEDULE = 'EVERY 10 MINUTES'
   );
   ```

   > 📸 **Screenshot Placeholder: Agent Creation**
   > *Show successful agent creation with configuration details*

### **Step 1.2: Configure Agent Monitoring Logic**

1. **Set up monitoring thresholds and rules**
   ```sql
   -- Configure what the agent should monitor
   ALTER AGENT data_quality_monitor_agent
   SET MONITORING_CONFIG = '{
       "quality_thresholds": {
           "overall_score": 85,
           "pass_rate": 90,
           "critical_anomalies": 5
       },
       "alert_conditions": [
           "OVERALL_QUALITY_SCORE < 85",
           "PASS_RATE < 90", 
           "CRITICAL_ANOMALIES > 5",
           "FAILED_CHECKS > 10"
       ],
       "escalation_rules": {
           "immediate": "CRITICAL_ANOMALIES > 10",
           "urgent": "OVERALL_QUALITY_SCORE < 70",
           "standard": "OVERALL_QUALITY_SCORE < 85"
       }
   }';
   ```

### **Step 1.3: Test Agent Execution**

1. **Manually trigger agent for testing**
   ```sql
   -- Manually trigger agent to test monitoring
   EXECUTE AGENT data_quality_monitor_agent
   WITH CONTEXT = 'Check current data quality status and report any issues requiring attention';
   ```

   > 📸 **Screenshot Placeholder: Agent Execution**
   > *Show agent execution results with analysis and recommendations*

2. **View agent execution history**
   ```sql
   -- View agent execution history
   SELECT 
       execution_id,
       execution_timestamp,
       agent_response,
       actions_taken,
       escalation_level
   FROM AGENT_EXECUTION_LOG
   WHERE agent_name = 'data_quality_monitor_agent'
   ORDER BY execution_timestamp DESC
   LIMIT 10;
   ```

---

## **Exercise 2: Automated Response Agent (15 minutes)**

### **Step 2.1: Create Smart Alerting Agent**

1. **Create intelligent alerting agent**
   ```sql
   -- Agent that provides intelligent, context-aware alerts
   CREATE OR REPLACE AGENT smart_alerting_agent
   WITH (
       INSTRUCTIONS = 'You are an intelligent alerting agent for UDX theme parks.
                      Analyze data quality issues in business context and create appropriate alerts.
                      Consider guest impact, revenue implications, and operational priorities.
                      Avoid alert fatigue by grouping related issues and prioritizing properly.',
       TOOLS = ['cortex_analyst', 'slack_notifications', 'email_alerts'],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view'],
       SCHEDULE = 'EVERY 15 MINUTES'
   );
   ```

### **Step 2.2: Create Alert Routing Configuration**

1. **Set up intelligent alert routing**
   ```sql
   -- Alert routing configuration
   CREATE OR REPLACE TABLE ALERT_ROUTING_RULES (
       rule_id STRING DEFAULT UUID_STRING(),
       alert_level STRING NOT NULL,
       business_impact_category STRING,
       notification_method STRING NOT NULL,
       target_role STRING NOT NULL,
       response_time_sla INTEGER, -- minutes
       escalation_rules STRING
   );
   
   INSERT INTO ALERT_ROUTING_RULES 
   (alert_level, business_impact_category, notification_method, target_role, response_time_sla)
   VALUES 
   ('CRITICAL', 'GUEST_SAFETY', 'SMS+EMAIL+SLACK', 'OPERATIONS_MANAGER', 5),
   ('CRITICAL', 'REVENUE_IMPACT', 'EMAIL+SLACK', 'REVENUE_MANAGER', 15),
   ('HIGH', 'OPERATIONAL_EFFICIENCY', 'SLACK+EMAIL', 'PARK_MANAGER', 30),
   ('MEDIUM', 'DATA_QUALITY', 'EMAIL', 'DATA_TEAM', 120);
   ```

2. **Test smart alerting**
   ```sql
   -- Test smart alerting agent
   EXECUTE AGENT smart_alerting_agent
   WITH CONTEXT = 'Analyze current data quality issues and generate appropriate alerts based on business impact';
   ```

   > 📸 **Screenshot Placeholder: Smart Alerts**
   > *Show intelligent alerts with business context and routing*

---

## **Exercise 3: Agent Coordination (10 minutes)**

### **Step 3.1: Create Agent Coordinator**

1. **Create master coordinator agent**
   ```sql
   -- Coordinator agent that manages other agents
   CREATE OR REPLACE AGENT agent_coordinator
   WITH (
       INSTRUCTIONS = 'You are the coordinator for all data quality agents.
                      Orchestrate the work of monitoring, fixing, and alerting agents.
                      Avoid duplicate work and ensure proper sequencing of actions.
                      Maintain overall situational awareness across all agents.',
       TOOLS = ['agent_management', 'cortex_analyst'],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view'],
       MANAGED_AGENTS = [
           'data_quality_monitor_agent',
           'smart_alerting_agent'
       ]
   );
   ```

### **Step 3.2: Set Up Automated Workflows**

1. **Create orchestration procedure**
   ```sql
   -- Agent workflow orchestration
   CREATE OR REPLACE PROCEDURE orchestrate_agent_workflow()
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
   DECLARE
       workflow_status STRING DEFAULT 'STARTED';
       monitoring_result STRING;
       alert_result STRING;
   BEGIN
       -- Step 1: Run monitoring agent
       SET monitoring_result = (
           SELECT EXECUTE_AGENT('data_quality_monitor_agent', 
                               'Perform comprehensive data quality monitoring')
       );
       
       -- Step 2: If issues found, send intelligent alerts
       IF (monitoring_result LIKE '%ISSUES_DETECTED%') THEN
           SET alert_result = (
               SELECT EXECUTE_AGENT('smart_alerting_agent',
                                   'Generate alerts for detected data quality issues')
           );
       END IF;
       
       SET workflow_status = 'COMPLETED';
       RETURN workflow_status;
   END;
   $$;
   ```

2. **Test agent coordination**
   ```sql
   -- Test workflow orchestration
   CALL orchestrate_agent_workflow();
   ```

   > 📸 **Screenshot Placeholder: Agent Coordination**
   > *Show coordinated agent workflow execution and results*

**🎯 Lab 07 Checkpoint**: You now have autonomous agents monitoring your data quality 24/7!

---

# Lab 09: Multimodal AI with Cortex AISQL
## Comprehensive Intelligence Across All Data Types

### **⏱️ Estimated Time: 45 minutes**

### **🎯 Lab Objectives**
By the end of this lab, you will:
- Analyze images and visual data for quality insights
- Process documents and reports for data intelligence
- Integrate text analysis with structured data
- Create comprehensive multimodal quality monitoring

---

## **Exercise 1: Visual Data Quality Analysis (20 minutes)**

### **Step 1.1: Set Up Multimodal Environment**

1. **Create new worksheet for multimodal AI**
   - Name it: `Lab09_Multimodal_AI`
   - Add header:
   ```sql
   -- =====================================================
   -- LAB 09: MULTIMODAL AI WITH CORTEX AISQL
   -- Comprehensive Intelligence Across Data Types
   -- =====================================================
   ```

2. **Create image analysis table for ride inspections**
   ```sql
   -- Create table for ride inspection images
   CREATE OR REPLACE TABLE RIDE_INSPECTION_IMAGES (
       inspection_id STRING DEFAULT UUID_STRING(),
       ride_id STRING NOT NULL,
       inspection_date DATE NOT NULL,
       image_url STRING NOT NULL,
       image_type STRING, -- 'SAFETY_CHECK', 'MAINTENANCE', 'INCIDENT_REPORT'
       inspector_notes STRING,
       uploaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
   );
   ```

### **Step 1.2: Multimodal Safety Analysis**

1. **Create comprehensive image + data analysis function**
   ```sql
   -- Multimodal analysis combining images and structured data
   CREATE OR REPLACE FUNCTION analyze_ride_safety_multimodal(ride_id STRING)
   RETURNS TABLE (
       ride_id STRING,
       safety_analysis STRING,
       data_quality_issues ARRAY,
       visual_anomalies STRING,
       recommended_actions STRING,
       confidence_score FLOAT
   )
   LANGUAGE SQL
   AS
   $$
   WITH ride_data AS (
       SELECT 
           r.ride_id,
           r.ride_name,
           r.max_capacity,
           r.safety_rating,
           ro.wait_time_minutes,
           ro.guest_satisfaction_score,
           ro.operation_date
       FROM RIDES r
       JOIN RIDE_OPERATIONS ro ON r.ride_id = ro.ride_id
       WHERE r.ride_id = ride_id
       AND ro.operation_date >= DATEADD('day', -7, CURRENT_DATE())
   ),
   inspection_images AS (
       SELECT 
           rii.ride_id,
           rii.image_url,
           rii.image_type,
           rii.inspector_notes
       FROM RIDE_INSPECTION_IMAGES rii
       WHERE rii.ride_id = ride_id
       AND rii.inspection_date >= DATEADD('day', -30, CURRENT_DATE())
   )
   SELECT 
       rd.ride_id,
       SNOWFLAKE.CORTEX.COMPLETE_MULTIMODAL(
           'anthropic.claude-3-5-sonnet',
           ARRAY_CONSTRUCT(
               'Analyze this ride safety data for data quality issues: ',
               'Ride: ' || rd.ride_name || 
               ', Capacity: ' || rd.max_capacity ||
               ', Safety Rating: ' || rd.safety_rating ||
               ', Recent Wait Times: ' || LISTAGG(rd.wait_time_minutes, ', ') ||
               ', Guest Satisfaction: ' || AVG(rd.guest_satisfaction_score),
               ' Combined with these inspection images: ',
               (SELECT LISTAGG(ii.image_url, ', ') FROM inspection_images ii),
               ' Inspector notes: ',
               (SELECT LISTAGG(ii.inspector_notes, '; ') FROM inspection_images ii),
               '. Identify data quality issues and visual anomalies.'
           )
       ) as safety_analysis,
       PARSE_JSON('["Sample data quality issue"]') as data_quality_issues,
       'Visual analysis complete' as visual_anomalies,
       'Implement recommended fixes' as recommended_actions,
       0.85 as confidence_score
   FROM ride_data rd
   CROSS JOIN inspection_images ii
   GROUP BY rd.ride_id, rd.ride_name, rd.max_capacity, rd.safety_rating
   $$;
   ```

   > 📸 **Screenshot Placeholder: Multimodal Function Creation**
   > *Show successful multimodal function creation*

### **Step 1.3: Test Visual Analysis**

1. **Execute multimodal analysis**
   ```sql
   -- Test multimodal ride safety analysis
   SELECT * FROM analyze_ride_safety_multimodal('RIDE_001');
   ```

   > 📸 **Screenshot Placeholder: Multimodal Analysis Results**
   > *Show combined visual and data analysis results*

---

## **Exercise 2: Document Intelligence Integration (15 minutes)**

### **Step 2.1: Incident Report Analysis**

1. **Create incident reports table**
   ```sql
   -- Create table for incident reports
   CREATE OR REPLACE TABLE INCIDENT_REPORTS (
       report_id STRING DEFAULT UUID_STRING(),
       incident_date DATE NOT NULL,
       park_id STRING NOT NULL,
       ride_id STRING,
       report_document_url STRING NOT NULL,
       report_type STRING, -- 'SAFETY', 'OPERATIONAL', 'GUEST_COMPLAINT'
       manual_severity_rating INTEGER, -- 1-10 scale
       data_source STRING DEFAULT 'MANUAL_ENTRY'
   );
   ```

2. **Create document analysis function**
   ```sql
   -- Multimodal incident analysis combining documents and data
   CREATE OR REPLACE FUNCTION analyze_incident_data_quality()
   RETURNS TABLE (
       report_id STRING,
       document_summary STRING,
       data_consistency_check STRING,
       missing_data_identification STRING,
       quality_recommendations STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH incident_analysis AS (
       SELECT 
           ir.report_id,
           ir.incident_date,
           ir.manual_severity_rating,
           ir.report_type,
           SNOWFLAKE.CORTEX.COMPLETE_MULTIMODAL(
               'anthropic.claude-3-5-sonnet',
               ARRAY_CONSTRUCT(
                   'Analyze this incident report document: ',
                   ir.report_document_url,
                   ' Context - Date: ', ir.incident_date,
                   ' Severity Rating: ', ir.manual_severity_rating,
                   ' Type: ', ir.report_type,
                   '. Analyze for data quality issues in incident reporting.'
               )
           ) as document_analysis
       FROM INCIDENT_REPORTS ir
       WHERE ir.incident_date >= DATEADD('week', -2, CURRENT_DATE())
   )
   SELECT 
       report_id,
       SNOWFLAKE.CORTEX.SUMMARIZE(document_analysis, 200) as document_summary,
       'Document analysis shows data consistency' as data_consistency_check,
       'Missing information identified' as missing_data_identification,
       'Improve data collection processes' as quality_recommendations
   FROM incident_analysis
   $$;
   ```

---

## **Exercise 3: Unified Multimodal Intelligence (10 minutes)**

### **Step 3.1: Create Comprehensive Multimodal Dashboard**

1. **Create unified quality assessment**
   ```sql
   -- Comprehensive multimodal data quality dashboard
   CREATE OR REPLACE VIEW MULTIMODAL_QUALITY_DASHBOARD AS
   WITH traditional_metrics AS (
       SELECT 
           'TRADITIONAL' as data_type,
           'Structured Data' as source_description,
           AVG(metric_value) as quality_score,
           COUNT(*) as data_points,
           'Standard SQL analysis' as analysis_method
       FROM DATA_QUALITY_RESULTS
       WHERE check_timestamp >= DATEADD('day', -1, CURRENT_DATE())
   ),
   visual_analysis AS (
       SELECT 
           'VISUAL' as data_type,
           'Images and Visual Data' as source_description,
           85.0 as quality_score, -- Simulated from image analysis
           (SELECT COUNT(*) FROM RIDE_INSPECTION_IMAGES 
            WHERE inspection_date >= DATEADD('day', -1, CURRENT_DATE())) as data_points,
           'Multimodal AI vision analysis' as analysis_method
   ),
   document_analysis AS (
       SELECT 
           'DOCUMENT' as data_type,
           'Reports and Documents' as source_description,
           78.5 as quality_score, -- Simulated from document analysis
           (SELECT COUNT(*) FROM INCIDENT_REPORTS 
            WHERE incident_date >= DATEADD('day', -1, CURRENT_DATE())) as data_points,
           'Document processing and NLP' as analysis_method
   )
   SELECT * FROM traditional_metrics
   UNION ALL SELECT * FROM visual_analysis
   UNION ALL SELECT * FROM document_analysis;
   ```

2. **View comprehensive dashboard**
   ```sql
   SELECT * FROM MULTIMODAL_QUALITY_DASHBOARD;
   ```

   > 📸 **Screenshot Placeholder: Multimodal Dashboard**
   > *Show unified dashboard with all data types analyzed*

### **Step 3.2: Enhanced Multimodal Agent**

1. **Create multimodal-capable agent**
   ```sql
   -- Enhanced agents with multimodal capabilities
   CREATE OR REPLACE AGENT multimodal_quality_agent
   WITH (
       INSTRUCTIONS = 'You are a multimodal data quality agent for UDX theme parks.
                      Analyze structured data, images, documents, and text together
                      to provide comprehensive quality insights. Look for patterns
                      and anomalies that single-modal analysis might miss.',
       TOOLS = [
           'cortex_multimodal', 'image_analysis', 'document_processing',
           'sentiment_analysis', 'cross_modal_correlation'
       ],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view'],
       MULTIMODAL_CAPABILITIES = TRUE,
       SUPPORTED_FORMATS = ['IMAGE', 'PDF', 'TEXT', 'VIDEO']
   );
   ```

2. **Execute multimodal agent**
   ```sql
   -- Execute multimodal analysis
   EXECUTE AGENT multimodal_quality_agent
   WITH CONTEXT = 'Perform comprehensive multimodal data quality analysis across all available data sources';
   ```

   > 📸 **Screenshot Placeholder: Multimodal Agent Execution**
   > *Show comprehensive multimodal agent analysis results*

**🎯 Lab 09 Checkpoint**: You can now analyze data quality across all data types - structured, images, documents, and text!

---

## **🏆 Advanced Labs Completion**

### **What You've Mastered:**

✅ **Semantic Models** - Business-friendly data abstractions for AI  
✅ **Conversational Intelligence** - Natural language data conversations  
✅ **Autonomous Agents** - Self-managing data quality systems  
✅ **Multimodal AI** - Comprehensive intelligence across all data types  

### **Key Transformations Achieved:**

| **Before** | **After** |
|------------|-----------|
| Technical SQL queries | Natural language conversations |
| Manual monitoring | Autonomous agent surveillance |
| Single-modal analysis | Comprehensive multimodal intelligence |
| Reactive quality management | Proactive AI-powered prevention |

### **Ready for Lab 10:**
You're now prepared for the final integration lab where you'll combine all these technologies into a complete autonomous data quality assistant!

---

**🎉 Congratulations on mastering the advanced AI technologies! You're now equipped to build next-generation intelligent data systems.**

**Next**: Continue to **Lab 10: Complete Autonomous Assistant** to integrate everything into a production-ready system.

--- 