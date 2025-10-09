# Lab 06: Snowflake Intelligence
## Conversational Data Analytics and Natural Language Insights

### 🎯 **Lab Objectives**

In this lab, you'll learn to leverage Snowflake Intelligence for conversational data analytics. You'll enable business users to interact with data using natural language, democratizing access to data insights without requiring SQL knowledge.

### 📚 **Learning Outcomes**

By the end of this lab, you will be able to:
- Configure Snowflake Intelligence for semantic views
- Enable natural language querying of business data
- Create intelligent dashboards with conversational interfaces
- Set up self-service analytics for business users
- Implement AI-powered data exploration and insights

### 🏗️ **Architecture Overview**

Snowflake Intelligence creates a conversational layer over your semantic views:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Business      │    │   Snowflake      │    │   Natural       │
│   Users         │───▶│   Intelligence   │───▶│   Language      │
│   (Natural      │    │   (AI Engine)    │    │   Understanding │
│   Language)     │    └──────────────────┘    └─────────────────┘
└─────────────────┘              │                        │
                                 │                        │
                                 ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Semantic       │    │   Governed      │
                       │   Views          │    │   SQL           │
                       │   (Business      │    │   Generation    │
                       │   Context)       │    └─────────────────┘
                       └──────────────────┘
```

### 🔍 **Intelligence Capabilities**

#### 1. **Natural Language Queries** - Ask questions in plain English
#### 2. **Contextual Understanding** - AI understands business terminology
#### 3. **Governed Access** - Respects existing security and permissions
#### 4. **Explainable Results** - Shows how answers were derived
#### 5. **Self-Service Analytics** - Empowers business users

### 🛠️ **Prerequisites**

- Completion of Labs 01-05
- Semantic views created in Lab 05
- Understanding of business intelligence concepts
- Access to theme park sample data

### 📝 **Lab Exercises**

#### **Exercise 1: Enabling Intelligence for Semantic Views (30 minutes)**

Configure your semantic views for conversational analytics:

1. **Enable Intelligence on Data Quality Semantic View**
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

2. **Configure Intelligence Settings**
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

3. **Test Basic Intelligence Queries**
   ```sql
   -- Test intelligence capability with sample queries
   SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
       'What is the current data quality status across all theme parks?',
       semantic_view => 'udx_data_quality_semantic_view'
   ) as intelligence_response;
   
   SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
       'Show me which parks have data quality issues that might impact guest safety',
       semantic_view => 'udx_data_quality_semantic_view'
   ) as safety_analysis;
   ```

#### **Exercise 2: Business User Conversations (45 minutes)**

Create natural language interfaces for different business personas:

1. **Executive Dashboard Conversations**
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
           semantic_view => 'udx_business_impact_semantic_view',
           audience => 'executive'
       ) as intelligence_response
   
   UNION ALL
   
   SELECT 
       'Strategic Recommendations',
       SNOWFLAKE.INTELLIGENCE.QUERY(
           'What are the top 3 data quality investments we should make to improve guest experience?',
           semantic_view => 'udx_data_quality_semantic_view',
           audience => 'executive'
       ) as intelligence_response;
   ```

2. **Operations Manager Conversations**
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
   
   -- Test operational queries
   SELECT ask_operations_question(
       'Which rides have concerning wait times that might need immediate attention?'
   ) as ride_analysis;
   
   SELECT ask_operations_question(
       'How is guest satisfaction trending and what operational changes should we consider?'
   ) as satisfaction_analysis;
   
   SELECT ask_operations_question(
       'What data quality issues are affecting our ability to optimize park operations?'
   ) as quality_operations_impact;
   ```

3. **Data Team Conversations**
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
       ) as intelligence_response
   
   UNION ALL
   
   SELECT 
       'System Health',
       SNOWFLAKE.INTELLIGENCE.QUERY(
           'Evaluate the health of our data systems. Which tables or data sources 
           have the most quality issues and need immediate technical intervention?',
           semantic_view => 'udx_data_quality_semantic_view',
           audience => 'technical'
       ) as intelligence_response;
   ```

#### **Exercise 3: Interactive Intelligence Dashboards (40 minutes)**

Create intelligent dashboards with conversational capabilities:

1. **Create Intelligence-Powered Dashboard**
   ```sql
   -- Intelligent data quality dashboard
   CREATE OR REPLACE VIEW INTELLIGENT_QUALITY_DASHBOARD AS
   WITH current_metrics AS (
       SELECT * FROM SEMANTIC_VIEW(
           udx_data_quality_semantic_view
           DIMENSIONS "Theme Park", "Geographic Region", "Quality Check Type"
           METRICS OVERALL_QUALITY_SCORE, PASS_RATE, CRITICAL_ANOMALIES
           WHERE "Check Date" >= DATEADD('day', -30, CURRENT_DATE())
       )
   ),
   intelligence_insights AS (
       SELECT SNOWFLAKE.INTELLIGENCE.ANALYZE(
           'Analyze these data quality metrics and provide insights about trends, 
           concerning patterns, and recommended actions for each theme park.',
           data_context => (SELECT OBJECT_CONSTRUCT(*) FROM current_metrics),
           analysis_type => 'trend_analysis'
       ) as ai_insights
   )
   SELECT 
       cm.*,
       ii.ai_insights,
       SNOWFLAKE.INTELLIGENCE.RECOMMEND_ACTIONS(
           CONCAT('Based on quality score of ', cm.OVERALL_QUALITY_SCORE, 
                  ' and ', cm.CRITICAL_ANOMALIES, ' critical anomalies for ', 
                  cm."Theme Park", ', what immediate actions should we take?'),
           semantic_view => 'udx_data_quality_semantic_view'
       ) as recommended_actions
   FROM current_metrics cm
   CROSS JOIN intelligence_insights ii;
   ```

2. **Conversational Drill-Down Analysis**
   ```sql
   -- Enable conversational drill-down capabilities
   CREATE OR REPLACE FUNCTION drill_down_analysis(
       initial_finding STRING,
       drill_down_question STRING
   )
   RETURNS TABLE (
       analysis_level STRING,
       question STRING,
       intelligence_response STRING,
       follow_up_suggestions ARRAY
   )
   LANGUAGE SQL
   AS
   $$
   WITH analysis_response AS (
       SELECT SNOWFLAKE.INTELLIGENCE.DRILL_DOWN(
           initial_finding,
           drill_down_question,
           semantic_view => 'udx_data_quality_semantic_view',
           max_depth => 3
       ) as response
   )
   SELECT 
       'detailed_analysis' as analysis_level,
       drill_down_question as question,
       response:explanation::STRING as intelligence_response,
       response:follow_up_questions::ARRAY as follow_up_suggestions
   FROM analysis_response
   $$;
   
   -- Example drill-down conversation
   SELECT * FROM drill_down_analysis(
       'Orlando park has 15% lower quality score than other parks',
       'What specific data quality issues are causing Orlando park to underperform?'
   );
   ```

3. **Predictive Intelligence Insights**
   ```sql
   -- Predictive analytics with natural language explanations
   CREATE OR REPLACE VIEW PREDICTIVE_QUALITY_INTELLIGENCE AS
   SELECT 
       'Quality Forecast' as prediction_type,
       SNOWFLAKE.INTELLIGENCE.FORECAST(
           'Predict data quality trends for the next 30 days based on historical patterns. 
           Identify potential risks and suggest preventive measures.',
           semantic_view => 'udx_data_quality_semantic_view',
           forecast_period => '30 days',
           confidence_level => 0.85
       ) as prediction_analysis
   
   UNION ALL
   
   SELECT 
       'Anomaly Prediction',
       SNOWFLAKE.INTELLIGENCE.PREDICT_ANOMALIES(
           'Based on current data patterns, when and where are we most likely 
           to see data quality issues in the next two weeks?',
           semantic_view => 'udx_data_quality_semantic_view',
           prediction_window => '14 days'
       ) as prediction_analysis;
   ```

#### **Exercise 4: Self-Service Analytics Setup (35 minutes)**

Enable business users to explore data independently:

1. **Create Self-Service Intelligence Portal**
   ```sql
   -- Self-service portal configuration
   CREATE OR REPLACE INTELLIGENCE_PORTAL udx_self_service_portal
   WITH (
       SEMANTIC_VIEWS = [
           'udx_data_quality_semantic_view',
           'udx_park_operations_semantic_view', 
           'udx_business_impact_semantic_view'
       ],
       SUGGESTED_QUESTIONS = [
           'How is our data quality affecting guest satisfaction?',
           'Which parks need the most attention for data quality issues?',
           'What trends do you see in our operational data?',
           'How can we improve our data quality to increase revenue?',
           'What are the biggest risks to guest experience from data issues?'
       ],
       USER_ROLES = ['BUSINESS_ANALYST', 'PARK_MANAGER', 'EXECUTIVE'],
       AUTO_SUGGESTIONS = TRUE,
       EXPLANATION_LEVEL = 'BUSINESS_FRIENDLY'
   );
   ```

2. **Intelligent Query Assistance**
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
   
   -- Test query suggestions
   SELECT * FROM get_query_suggestions(
       'I want to understand our data quality performance',
       'PARK_MANAGER'
   );
   
   SELECT * FROM get_query_suggestions(
       'Revenue impact analysis',
       'EXECUTIVE'
   );
   ```

3. **Guided Analytics Experience**
   ```sql
   -- Guided analytics for new users
   CREATE OR REPLACE PROCEDURE guided_analytics_session(
       user_question STRING,
       user_experience_level STRING DEFAULT 'BEGINNER'
   )
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
   DECLARE
       guided_response STRING;
       follow_up_questions STRING;
       explanation STRING;
   BEGIN
       -- Get intelligent response with guidance
       SET guided_response = SNOWFLAKE.INTELLIGENCE.GUIDED_QUERY(
           user_question,
           semantic_view => 'udx_data_quality_semantic_view',
           guidance_level => user_experience_level,
           include_explanation => TRUE,
           suggest_follow_ups => TRUE
       );
       
       RETURN guided_response;
   END;
   $$;
   
   -- Test guided analytics
   CALL guided_analytics_session(
       'Show me our worst data quality problems',
       'BEGINNER'
   );
   ```

### 🤖 **Advanced Intelligence Features**

Explore cutting-edge Intelligence capabilities:

```sql
-- Multi-turn conversations with context awareness
CREATE OR REPLACE TABLE CONVERSATION_CONTEXT (
    conversation_id STRING DEFAULT UUID_STRING(),
    user_id STRING,
    question_sequence INTEGER,
    user_question STRING,
    intelligence_response STRING,
    context_data VARIANT,
    timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Contextual conversation function
CREATE OR REPLACE FUNCTION continue_conversation(
    conversation_id STRING,
    new_question STRING
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    WITH conversation_history AS (
        SELECT LISTAGG(
            CONCAT('Q: ', user_question, ' A: ', intelligence_response), 
            ' | '
        ) as context
        FROM CONVERSATION_CONTEXT
        WHERE conversation_id = conversation_id
        ORDER BY question_sequence
    )
    SELECT SNOWFLAKE.INTELLIGENCE.CONTEXTUAL_QUERY(
        new_question,
        semantic_view => 'udx_data_quality_semantic_view',
        conversation_context => (SELECT context FROM conversation_history),
        maintain_context => TRUE
    )
$$;
```

### 🎯 **Success Criteria**

By the end of this lab, you should have:

✅ **Enabled** Intelligence on your semantic views  
✅ **Created** natural language query interfaces for different user types  
✅ **Built** intelligent dashboards with conversational capabilities  
✅ **Implemented** self-service analytics for business users  
✅ **Configured** guided analytics experiences  
✅ **Tested** multi-turn conversational analytics  

### 📊 **Testing Your Intelligence Setup**

Validate your Intelligence configuration with these tests:

```sql
-- Test 1: Basic natural language query
SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
    'What is our data quality performance summary for this month?',
    semantic_view => 'udx_data_quality_semantic_view'
) as basic_query_test;

-- Test 2: Complex business question
SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
    'Which theme park should we prioritize for data quality improvements 
     to have the biggest impact on guest satisfaction?',
    semantic_view => 'udx_data_quality_semantic_view'
) as complex_analysis_test;

-- Test 3: Predictive question
SELECT SNOWFLAKE.INTELLIGENCE.QUERY(
    'Based on current trends, what data quality challenges should we 
     prepare for during the summer peak season?',
    semantic_view => 'udx_data_quality_semantic_view'
) as predictive_test;

-- Test 4: Verify explanation capability
SELECT SNOWFLAKE.INTELLIGENCE.EXPLAIN_QUERY(
    'Show me critical data quality issues by park',
    semantic_view => 'udx_data_quality_semantic_view',
    include_sql => TRUE,
    include_reasoning => TRUE
) as explanation_test;
```

### 🔄 **Common Issues and Troubleshooting**

#### **Issue**: Intelligence responses are too technical
**Solution**: Adjust audience settings and custom instructions
```sql
ALTER SEMANTIC VIEW udx_data_quality_semantic_view
SET CUSTOM_INSTRUCTIONS = 'Always provide business-friendly explanations. 
Avoid technical jargon and focus on actionable business insights.';
```

#### **Issue**: Users getting irrelevant suggestions
**Solution**: Improve semantic view context and sample values
```sql
-- Add more specific sample values and synonyms
ALTER SEMANTIC VIEW udx_data_quality_semantic_view
MODIFY DIMENSION "Quality Check Type"
ADD SAMPLE_VALUES ("Guest Data Completeness", "Ride Safety Validation", "Revenue Data Accuracy");
```

### 🚀 **Next Steps**

In **Lab 07: AI Agents Basics**, you'll learn:
- Creating simple autonomous AI agents
- Automated monitoring and alerting
- Basic agent workflows and triggers
- Agent-human collaboration patterns

Your Intelligence setup will provide the foundation for AI agents to understand business context!

### 📚 **Additional Resources**

- [Snowflake Intelligence Documentation](link-to-resource)
- [Natural Language Query Best Practices](link-to-resource)
- [Conversational Analytics Patterns](link-to-resource)

---

**Continue to Lab 07 to create your first autonomous AI agents for data quality monitoring!** 