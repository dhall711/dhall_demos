# Lab 07: AI Agents Basics
## Creating Your First Autonomous Data Quality Agents

### 🎯 **Lab Objectives**

In this lab, you'll create your first autonomous AI agents that can monitor data quality, detect issues, and take automated actions. These agents bridge the gap between passive monitoring and active, intelligent data management.

### 📚 **Learning Outcomes**

By the end of this lab, you will be able to:
- Create basic autonomous AI agents for data quality monitoring
- Implement agent triggers and scheduling
- Design agent workflows for common data quality tasks
- Set up agent-human collaboration patterns
- Build foundation for advanced agent orchestration

### 🏗️ **Architecture Overview**

AI Agents operate autonomously to monitor and manage data quality:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Quality  │    │   AI Agents      │    │   Autonomous    │
│   Events &      │───▶│   (Monitor,      │───▶│   Actions &     │
│   Triggers      │    │   Analyze,       │    │   Responses     │
└─────────────────┘    │   Act)           │    └─────────────────┘
                       └──────────────────┘              │
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Semantic       │    │   Human         │
                       │   Understanding  │    │   Escalation    │
                       └──────────────────┘    └─────────────────┘
```

### 🔍 **Agent Capabilities**

#### 1. **Autonomous Monitoring** - Continuously watch data quality metrics
#### 2. **Intelligent Analysis** - Use AI to understand issues and context
#### 3. **Automated Actions** - Take corrective actions without human intervention
#### 4. **Smart Escalation** - Know when to involve humans
#### 5. **Learning & Adaptation** - Improve performance over time

### 🛠️ **Prerequisites**

- Completion of Labs 01-06
- Semantic views with Intelligence enabled
- Understanding of AI concepts and automation
- Access to Snowflake Cortex AI functions

### 📝 **Lab Exercises**

#### **Exercise 1: Creating Your First Monitoring Agent (45 minutes)**

Build a basic agent that monitors data quality continuously:

1. **Create Data Quality Monitoring Agent**
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

2. **Define Agent Monitoring Logic**
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

3. **Test Agent Monitoring**
   ```sql
   -- Manually trigger agent to test monitoring
   EXECUTE AGENT data_quality_monitor_agent
   WITH CONTEXT = 'Check current data quality status and report any issues requiring attention';
   
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

#### **Exercise 2: Automated Response Agent (45 minutes)**

Create an agent that can take automated actions:

1. **Create Automated Response Agent**
   ```sql
   -- Agent that can automatically fix certain data quality issues
   CREATE OR REPLACE AGENT data_quality_auto_fix_agent
   WITH (
       INSTRUCTIONS = 'You are an automated data quality remediation agent.
                      When data quality issues are detected, analyze if they can be automatically fixed.
                      Only take action on pre-approved fix types. For complex issues, escalate to humans.
                      Always document what actions you take and why.',
       TOOLS = ['cortex_analyst', 'sql_execution', 'notification_system'],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view'],
       APPROVAL_REQUIRED = FALSE  -- For pre-approved fixes only
   );
   ```

2. **Define Auto-Fix Rules**
   ```sql
   -- Configure what the agent can automatically fix
   CREATE OR REPLACE TABLE AGENT_FIX_RULES (
       rule_id STRING DEFAULT UUID_STRING(),
       issue_type STRING NOT NULL,
       fix_description STRING NOT NULL,
       auto_fix_sql STRING,
       requires_approval BOOLEAN DEFAULT TRUE,
       max_records_affected INTEGER DEFAULT 100,
       confidence_threshold FLOAT DEFAULT 0.9,
       created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
   );
   
   -- Insert approved auto-fix rules
   INSERT INTO AGENT_FIX_RULES (issue_type, fix_description, auto_fix_sql, requires_approval, max_records_affected)
   VALUES 
   ('DUPLICATE_GUESTS', 'Remove exact duplicate guest records', 
    'DELETE FROM GUESTS WHERE guest_id IN (SELECT guest_id FROM duplicate_guest_analysis WHERE duplicate_confidence = ''EXACT_MATCH'')', 
    FALSE, 50),
   ('INVALID_EMAIL_FORMAT', 'Standardize email formats',
    'UPDATE GUESTS SET email = TRIM(LOWER(email)) WHERE email RLIKE ''.*[A-Z].*'' OR email LIKE '' %'' OR email LIKE ''% ''',
    FALSE, 100),
   ('FUTURE_DATES', 'Correct obviously wrong future dates',
    'UPDATE RIDE_OPERATIONS SET operation_date = CURRENT_DATE() WHERE operation_date > DATEADD(''day'', 1, CURRENT_DATE())',
    FALSE, 20);
   ```

3. **Implement Agent Fix Logic**
   ```sql
   -- Agent procedure for automated fixes
   CREATE OR REPLACE PROCEDURE execute_agent_fixes(agent_name STRING)
   RETURNS STRING
   LANGUAGE SQL
   AS
   $$
   DECLARE
       fix_results STRING DEFAULT '';
       fixes_applied INTEGER DEFAULT 0;
   BEGIN
       -- Get current data quality issues
       FOR issue_record IN (
           SELECT DISTINCT 
               dqr.check_type,
               dqr.table_name,
               COUNT(*) as issue_count
           FROM DATA_QUALITY_RESULTS dqr
           WHERE dqr.status = 'FAIL'
           AND dqr.check_timestamp >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
           GROUP BY dqr.check_type, dqr.table_name
       ) DO
           -- Check if we have an auto-fix rule
           FOR fix_rule IN (
               SELECT * FROM AGENT_FIX_RULES 
               WHERE issue_type = issue_record.check_type
               AND requires_approval = FALSE
               AND max_records_affected >= issue_record.issue_count
           ) DO
               -- Execute the fix
               EXECUTE IMMEDIATE fix_rule.auto_fix_sql;
               SET fixes_applied = fixes_applied + 1;
               
               -- Log the action
               INSERT INTO AGENT_ACTION_LOG (
                   agent_name, action_type, action_description, 
                   records_affected, confidence_score
               )
               VALUES (
                   agent_name, 'AUTO_FIX', fix_rule.fix_description,
                   issue_record.issue_count, 0.95
               );
           END FOR;
       END FOR;
       
       SET fix_results = 'Applied ' || fixes_applied || ' automated fixes';
       RETURN fix_results;
   END;
   $$;
   ```

#### **Exercise 3: Intelligent Alerting Agent (40 minutes)**

Create an agent that provides smart, contextual alerts:

1. **Create Smart Alerting Agent**
   ```sql
   -- Agent that provides intelligent, context-aware alerts
   CREATE OR REPLACE AGENT smart_alerting_agent
   WITH (
       INSTRUCTIONS = 'You are an intelligent alerting agent for UDX theme parks.
                      Analyze data quality issues in business context and create appropriate alerts.
                      Consider guest impact, revenue implications, and operational priorities.
                      Avoid alert fatigue by grouping related issues and prioritizing properly.',
       TOOLS = ['cortex_analyst', 'slack_notifications', 'email_alerts', 'sms_critical'],
       MODEL = 'anthropic.claude-3-5-sonnet',
       SEMANTIC_VIEWS = ['udx_data_quality_semantic_view', 'udx_business_impact_semantic_view'],
       SCHEDULE = 'EVERY 15 MINUTES'
   );
   ```

2. **Implement Intelligent Alert Logic**
   ```sql
   -- Smart alert generation procedure
   CREATE OR REPLACE FUNCTION generate_smart_alerts()
   RETURNS TABLE (
       alert_id STRING,
       alert_level STRING,
       alert_message STRING,
       business_impact STRING,
       recommended_actions STRING,
       target_audience STRING
   )
   LANGUAGE SQL
   AS
   $$
   WITH current_issues AS (
       SELECT * FROM SEMANTIC_VIEW(
           udx_data_quality_semantic_view
           DIMENSIONS "Theme Park", "Quality Check Type", "Quality Status"
           METRICS OVERALL_QUALITY_SCORE, CRITICAL_ANOMALIES, FAILED_CHECKS
           WHERE "Check Date" >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
           AND "Quality Status" = 'FAIL'
       )
   ),
   ai_alert_analysis AS (
       SELECT SNOWFLAKE.CORTEX.COMPLETE(
           'anthropic.claude-3-5-sonnet',
           CONCAT(
               'Analyze these data quality issues and create intelligent alerts: ',
               (SELECT LISTAGG(
                   CONCAT('"Theme Park": ', "Theme Park", 
                          ', "Quality Check Type": ', "Quality Check Type",
                          ', "Quality Score": ', OVERALL_QUALITY_SCORE,
                          ', "Critical Anomalies": ', CRITICAL_ANOMALIES), '; '
               ) FROM current_issues),
               '. For each issue, provide:
               1. Alert severity (CRITICAL/HIGH/MEDIUM/LOW)
               2. Business-friendly alert message
               3. Potential business impact
               4. Recommended immediate actions
               5. Target audience (Operations/Executive/Technical)
               
               Consider guest safety as highest priority, followed by revenue impact.'
           )
       ) as alert_analysis
   )
   SELECT 
       UUID_STRING() as alert_id,
       'INTELLIGENT' as alert_level,
       alert_analysis as alert_message,
       'Generated by AI analysis' as business_impact,
       'See alert details' as recommended_actions,
       'OPERATIONS' as target_audience
   FROM ai_alert_analysis
   $$;
   ```

3. **Configure Alert Routing**
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
   ('MEDIUM', 'DATA_QUALITY', 'EMAIL', 'DATA_TEAM', 120),
   ('LOW', 'INFORMATIONAL', 'DASHBOARD', 'ANALYSTS', 480);
   ```

#### **Exercise 4: Agent Coordination and Workflows (40 minutes)**

Create agents that work together in coordinated workflows:

1. **Create Agent Coordinator**
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
           'data_quality_auto_fix_agent', 
           'smart_alerting_agent'
       ]
   );
   ```

2. **Define Agent Workflow**
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
       fix_result STRING;
       alert_result STRING;
   BEGIN
       -- Step 1: Run monitoring agent
       SET monitoring_result = (
           SELECT EXECUTE_AGENT('data_quality_monitor_agent', 
                               'Perform comprehensive data quality monitoring')
       );
       
       -- Step 2: If issues found, attempt auto-fixes
       IF (monitoring_result LIKE '%ISSUES_DETECTED%') THEN
           SET fix_result = (
               SELECT execute_agent_fixes('data_quality_auto_fix_agent')
           );
           
           -- Step 3: Send intelligent alerts for remaining issues
           SET alert_result = (
               SELECT EXECUTE_AGENT('smart_alerting_agent',
                                   'Generate alerts for unresolved data quality issues')
           );
       END IF;
       
       -- Log workflow completion
       INSERT INTO AGENT_WORKFLOW_LOG (
           workflow_id, coordinator_agent, execution_summary
       )
       VALUES (
           UUID_STRING(), 'agent_coordinator',
           CONCAT('Monitoring: ', monitoring_result, 
                  ', Fixes: ', COALESCE(fix_result, 'None needed'),
                  ', Alerts: ', COALESCE(alert_result, 'None sent'))
       );
       
       SET workflow_status = 'COMPLETED';
       RETURN workflow_status;
   END;
   $$;
   ```

3. **Set Up Agent Triggers**
   ```sql
   -- Create triggers for agent automation
   CREATE OR REPLACE TASK agent_workflow_scheduler
       WAREHOUSE = UDX_AI_WAREHOUSE
       SCHEDULE = 'USING CRON 0 */2 * * * UTC'  -- Every 2 hours
   AS
   CALL orchestrate_agent_workflow();
   
   -- Enable the task
   ALTER TASK agent_workflow_scheduler RESUME;
   
   -- Create stream-based trigger for immediate response
   CREATE OR REPLACE STREAM data_quality_changes 
   ON TABLE DATA_QUALITY_RESULTS;
   
   CREATE OR REPLACE TASK immediate_response_trigger
       WAREHOUSE = UDX_AI_WAREHOUSE
       SCHEDULE = '1 MINUTE'
       WHEN SYSTEM$STREAM_HAS_DATA('data_quality_changes')
   AS
   EXECUTE AGENT data_quality_monitor_agent
   WITH CONTEXT = 'Immediate response to new data quality changes detected';
   
   ALTER TASK immediate_response_trigger RESUME;
   ```

### 🧠 **Agent Monitoring and Management**

Monitor your agents' performance and behavior:

```sql
-- Agent performance dashboard
CREATE OR REPLACE VIEW AGENT_PERFORMANCE_DASHBOARD AS
SELECT 
    agent_name,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN execution_status = 'SUCCESS' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN actions_taken > 0 THEN 1 END) as actionable_executions,
    AVG(execution_time_seconds) as avg_execution_time,
    MAX(execution_timestamp) as last_execution,
    COUNT(CASE WHEN escalation_level = 'CRITICAL' THEN 1 END) as critical_escalations
FROM AGENT_EXECUTION_LOG
WHERE execution_timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY agent_name;

-- Agent interaction analysis
CREATE OR REPLACE VIEW AGENT_INTERACTION_ANALYSIS AS
WITH agent_interactions AS (
    SELECT 
        ael1.agent_name as agent_1,
        ael2.agent_name as agent_2,
        ABS(DATEDIFF('minute', ael1.execution_timestamp, ael2.execution_timestamp)) as time_gap_minutes,
        CASE 
            WHEN time_gap_minutes <= 5 THEN 'COORDINATED'
            WHEN time_gap_minutes <= 30 THEN 'RELATED' 
            ELSE 'INDEPENDENT'
        END as interaction_type
    FROM AGENT_EXECUTION_LOG ael1
    JOIN AGENT_EXECUTION_LOG ael2 
        ON ael1.execution_timestamp != ael2.execution_timestamp
        AND ael1.agent_name != ael2.agent_name
    WHERE ael1.execution_timestamp >= DATEADD('day', -1, CURRENT_TIMESTAMP())
)
SELECT 
    agent_1,
    agent_2,
    interaction_type,
    COUNT(*) as interaction_count,
    AVG(time_gap_minutes) as avg_time_gap
FROM agent_interactions
GROUP BY agent_1, agent_2, interaction_type
ORDER BY interaction_count DESC;
```

### 🎯 **Success Criteria**

By the end of this lab, you should have:

✅ **Created** autonomous monitoring agents for data quality  
✅ **Implemented** automated response agents with fix capabilities  
✅ **Built** intelligent alerting with business context  
✅ **Configured** agent coordination and workflows  
✅ **Established** monitoring and performance tracking  
✅ **Set up** triggers and scheduling for agent automation  

### 📊 **Testing Your Agents**

Validate your agent setup with these tests:

```sql
-- Test 1: Manual agent execution
EXECUTE AGENT data_quality_monitor_agent
WITH CONTEXT = 'Test execution - analyze current data quality status';

-- Test 2: Workflow orchestration
CALL orchestrate_agent_workflow();

-- Test 3: Agent performance check
SELECT * FROM AGENT_PERFORMANCE_DASHBOARD;

-- Test 4: Alert generation
SELECT * FROM generate_smart_alerts();

-- Test 5: Agent coordination analysis
SELECT * FROM AGENT_INTERACTION_ANALYSIS;
```

### 🔄 **Common Issues and Troubleshooting**

#### **Issue**: Agent executions failing with permissions errors
**Solution**: Ensure agents have proper role assignments and semantic view access
```sql
-- Grant necessary permissions to agent roles
GRANT USAGE ON SEMANTIC VIEW udx_data_quality_semantic_view TO ROLE AGENT_ROLE;
GRANT EXECUTE ON AGENT data_quality_monitor_agent TO ROLE UDX_DATA_TEAM;
```

#### **Issue**: Too many alerts being generated
**Solution**: Implement alert throttling and consolidation
```sql
-- Add alert throttling logic
ALTER AGENT smart_alerting_agent
SET THROTTLING_CONFIG = '{
    "max_alerts_per_hour": 5,
    "consolidate_similar": true,
    "cooldown_period_minutes": 30
}';
```

### 🚀 **Next Steps**

In **Lab 08: Advanced Agent Orchestration**, you'll learn:
- Multi-agent collaboration patterns
- Complex workflow orchestration
- Agent learning and adaptation
- Enterprise-scale agent management

Your basic agents will evolve into sophisticated autonomous systems!

### 📚 **Additional Resources**

- [AI Agent Design Patterns](link-to-resource)
- [Autonomous System Best Practices](link-to-resource)
- [Agent Monitoring and Governance](link-to-resource)

---

**Continue to Lab 08 to build advanced agent orchestration and collaborative AI systems!** 