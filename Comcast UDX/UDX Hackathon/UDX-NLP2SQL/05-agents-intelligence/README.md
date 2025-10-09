# Lab 05: Snowflake Agents & Intelligence Integration

## 🎯 Learning Objectives

Transform your existing NLP2SQL system into an advanced agentic AI platform using:
- **Snowflake Agents (Cortex Agents)**: Orchestrate complex multi-step workflows
- **Snowflake Intelligence**: Provide ready-made conversational experiences
- **Advanced Integration**: Combine structured and unstructured data analysis

## 🧠 From Functions to Agents: The Evolution

### Current State (Your Project)
```sql
-- Individual AI function calls
SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', 'Convert to SQL: Show me revenue by park');
```

### Enhanced State (With Agents)
```sql
-- Orchestrated agent workflow that can:
-- 1. Understand intent
-- 2. Route to appropriate tools
-- 3. Execute multiple steps
-- 4. Provide comprehensive responses
```

## 🏗️ Architecture Enhancement

### 1. Cortex Agents Integration

Replace your individual AI functions with sophisticated agent workflows:

```sql
-- Create an enhanced UDX Business Intelligence Agent
CREATE OR REPLACE FUNCTION create_udx_business_agent()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    agent_config OBJECT;
BEGIN
    -- Configure agent with multiple tools
    SET agent_config = OBJECT_CONSTRUCT(
        'agent_name', 'UDX_Business_Intelligence_Agent',
        'tools', ARRAY_CONSTRUCT(
            OBJECT_CONSTRUCT(
                'tool_spec', OBJECT_CONSTRUCT(
                    'type', 'cortex_analyst_text_to_sql',
                    'name', 'udx_data_model'
                )
            ),
            OBJECT_CONSTRUCT(
                'tool_spec', OBJECT_CONSTRUCT(
                    'type', 'cortex_search',
                    'name', 'udx_document_search'
                )
            ),
            OBJECT_CONSTRUCT(
                'tool_spec', OBJECT_CONSTRUCT(
                    'type', 'sql_exec',
                    'name', 'sql_executor'
                )
            ),
            OBJECT_CONSTRUCT(
                'tool_spec', OBJECT_CONSTRUCT(
                    'type', 'data_to_chart',
                    'name', 'visualization_generator'
                )
            )
        ),
        'tool_resources', OBJECT_CONSTRUCT(
            'udx_data_model', OBJECT_CONSTRUCT(
                'semantic_model_file', '@BUSINESS_ANALYTICS.PUBLIC.udx_semantic_model.yaml'
            ),
            'udx_document_search', OBJECT_CONSTRUCT(
                'name', 'BUSINESS_ANALYTICS.PUBLIC.udx_knowledge_base',
                'max_results', 10,
                'title_column', 'DOCUMENT_TITLE',
                'id_column', 'DOCUMENT_ID'
            )
        )
    );
    
    RETURN agent_config::STRING;
END;
$$;
```

### 2. Enhanced Semantic Model for Agents

Upgrade your existing semantic model to work with Cortex Agents:

```yaml
# @BUSINESS_ANALYTICS.PUBLIC.udx_semantic_model.yaml
name: "UDX Theme Park Analytics"
description: "Comprehensive business analytics for UDX theme park operations"

tables:
  - name: "CUSTOMERS"
    description: "Guest information and demographics"
    columns:
      - name: "CUSTOMER_ID"
        description: "Unique customer identifier"
        semantic_type: "primary_key"
      - name: "TOTAL_SPENT"
        description: "Lifetime customer value"
        semantic_type: "measure"
        aggregation: "sum"
    
  - name: "SALES_TRANSACTIONS" 
    description: "All ticket and merchandise sales"
    columns:
      - name: "TRANSACTION_DATE"
        description: "When the purchase occurred"
        semantic_type: "date"
      - name: "REVENUE_AMOUNT"
        description: "Transaction value in USD"
        semantic_type: "measure"
        aggregation: "sum"

  - name: "PARK_PERFORMANCE"
    description: "Daily operational metrics by park"
    columns:
      - name: "PARK_NAME"
        description: "Theme park location"
        semantic_type: "dimension"
      - name: "GUEST_SATISFACTION_SCORE"
        description: "Daily average satisfaction rating (1-10)"
        semantic_type: "measure"
        aggregation: "avg"

# Business Context for Agents
business_context:
  - term: "VIP Experience"
    definition: "Premium park access with priority ride access and concierge service"
    related_tables: ["CUSTOMERS", "SALES_TRANSACTIONS"]
  
  - term: "Peak Season"
    definition: "Summer months (June-August) and holiday periods with highest attendance"
    related_tables: ["PARK_PERFORMANCE", "SALES_TRANSACTIONS"]
    
  - term: "Guest Satisfaction"
    definition: "Daily survey scores measuring overall park experience quality"
    related_tables: ["PARK_PERFORMANCE"]

# Agent-Specific Configurations
agent_behaviors:
  greeting: "Hello! I'm your UDX Business Intelligence Assistant. I can help you analyze park performance, customer data, and operational metrics."
  capabilities:
    - "Analyze revenue trends across all parks"
    - "Identify top-performing attractions"
    - "Generate customer satisfaction reports"
    - "Create operational efficiency dashboards"
    - "Search through policy documents and operational guides"
```

### 3. Cortex Search Service for Documents

Create a comprehensive knowledge base for unstructured data:

```sql
-- Create Cortex Search service for UDX documents
CREATE OR REPLACE CORTEX SEARCH SERVICE udx_knowledge_base
ON table_name = 'BUSINESS_ANALYTICS.PUBLIC.UDX_DOCUMENTS'
ATTRIBUTES = (
    'DOCUMENT_CONTENT',  -- Main text content
    'DOCUMENT_TYPE',     -- Policy, procedure, training, etc.
    'DEPARTMENT',        -- Operations, HR, Finance, etc.
    'LAST_UPDATED'       -- Document version control
)
WAREHOUSE = 'BUSINESS_ANALYTICS_WH';

-- Sample document data for knowledge base
INSERT INTO BUSINESS_ANALYTICS.PUBLIC.UDX_DOCUMENTS VALUES
('DOC_001', 'UDX Guest Safety Protocols', 'All rides must undergo daily safety inspections before opening. Emergency procedures must be reviewed monthly with all operators...', 'POLICY', 'OPERATIONS', '2024-01-15'),
('DOC_002', 'Customer Service Standards', 'Every guest interaction should exceed expectations. Staff should greet guests within 30 seconds and resolve issues within 15 minutes...', 'PROCEDURE', 'GUEST_SERVICES', '2024-02-01'),
('DOC_003', 'Revenue Recognition Guidelines', 'Ticket sales are recognized at point of entry. Merchandise sales recorded at transaction time. Season passes amortized over usage period...', 'POLICY', 'FINANCE', '2024-01-20');
```

## 🌟 Advanced Agent Workflows

### 1. Multi-Modal Business Analysis

```sql
-- Enhanced business analysis function using Cortex Agents
CREATE OR REPLACE FUNCTION analyze_business_performance_with_agent(
    user_question STRING,
    analysis_depth STRING DEFAULT 'comprehensive'
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    agent_response VARIANT;
    context_prompt STRING;
BEGIN
    -- Build enhanced context for agent
    SET context_prompt = CONCAT(
        'You are a UDX Business Intelligence Agent with access to both structured data and document knowledge. ',
        'For the question: "', user_question, '", please: ',
        '1. Analyze relevant structured data using SQL queries ',
        '2. Search documents for additional context and policies ',
        '3. Provide comprehensive insights with data visualizations ',
        '4. Suggest actionable recommendations ',
        'Analysis depth: ', analysis_depth
    );
    
    -- Call Cortex Agents API (when available)
    SET agent_response = SNOWFLAKE.CORTEX.AGENTS.RUN(
        'llama3.1-70b',
        ARRAY_CONSTRUCT(
            OBJECT_CONSTRUCT(
                'role', 'user',
                'content', ARRAY_CONSTRUCT(
                    OBJECT_CONSTRUCT(
                        'type', 'text',
                        'text', context_prompt
                    )
                )
            )
        ),
        OBJECT_CONSTRUCT(
            'tools', ARRAY_CONSTRUCT(
                OBJECT_CONSTRUCT(
                    'tool_spec', OBJECT_CONSTRUCT(
                        'type', 'cortex_analyst_text_to_sql',
                        'name', 'udx_data_model'
                    )
                ),
                OBJECT_CONSTRUCT(
                    'tool_spec', OBJECT_CONSTRUCT(
                        'type', 'cortex_search', 
                        'name', 'udx_document_search'
                    )
                )
            ),
            'tool_resources', OBJECT_CONSTRUCT(
                'udx_data_model', OBJECT_CONSTRUCT(
                    'semantic_model_file', '@BUSINESS_ANALYTICS.PUBLIC.udx_semantic_model.yaml'
                ),
                'udx_document_search', OBJECT_CONSTRUCT(
                    'name', 'BUSINESS_ANALYTICS.PUBLIC.udx_knowledge_base'
                )
            )
        )
    );
    
    RETURN agent_response;
END;
$$;
```

### 2. Conversational Context Management

```sql
-- Enhanced conversation management for agents
CREATE OR REPLACE TABLE AGENT_CONVERSATIONS (
    session_id STRING,
    user_id STRING,
    message_sequence INTEGER,
    user_message STRING,
    agent_response VARIANT,
    tools_used ARRAY,
    response_time_ms INTEGER,
    satisfaction_rating INTEGER,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Agent conversation function
CREATE OR REPLACE FUNCTION continue_agent_conversation(
    session_id STRING,
    user_message STRING,
    user_id STRING DEFAULT 'anonymous'
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    conversation_history STRING;
    enhanced_response VARIANT;
    next_sequence INTEGER;
BEGIN
    -- Get conversation context
    SET conversation_history = (
        SELECT LISTAGG(
            CONCAT('User: ', user_message, ' | Agent: ', agent_response:content),
            ' || '
        ) WITHIN GROUP (ORDER BY message_sequence)
        FROM AGENT_CONVERSATIONS 
        WHERE session_id = session_id
        ORDER BY message_sequence DESC
        LIMIT 5
    );
    
    -- Get next sequence number
    SET next_sequence = (
        SELECT COALESCE(MAX(message_sequence), 0) + 1 
        FROM AGENT_CONVERSATIONS 
        WHERE session_id = session_id
    );
    
    -- Enhanced agent call with conversation context
    SET enhanced_response = analyze_business_performance_with_agent(
        CONCAT(
            'Previous conversation: ', COALESCE(conversation_history, 'None'), 
            ' | Current question: ', user_message
        )
    );
    
    -- Store conversation
    INSERT INTO AGENT_CONVERSATIONS VALUES (
        session_id, user_id, next_sequence, user_message, 
        enhanced_response, ['cortex_analyst', 'cortex_search'], 
        NULL, NULL, CURRENT_TIMESTAMP()
    );
    
    RETURN enhanced_response;
END;
$$;
```

## 🎨 Snowflake Intelligence Integration

### 1. Direct Intelligence Portal Access

Your users can now access a no-code interface at `ai.snowflake.com` that connects directly to your UDX data:

```sql
-- Configure your data for Snowflake Intelligence
CREATE OR REPLACE VIEW INTELLIGENCE_READY_DATA AS
SELECT 
    'UDX Theme Parks' as data_source,
    'Revenue by park and date' as description,
    p.park_name,
    s.transaction_date,
    SUM(s.revenue_amount) as total_revenue,
    AVG(p.guest_satisfaction_score) as avg_satisfaction
FROM BUSINESS_ANALYTICS.SALES_TRANSACTIONS s
JOIN BUSINESS_ANALYTICS.PARK_PERFORMANCE p 
    ON s.park_id = p.park_id AND s.transaction_date = p.performance_date
GROUP BY p.park_name, s.transaction_date;

-- Grant access for Intelligence
GRANT SELECT ON VIEW INTELLIGENCE_READY_DATA TO ROLE INTELLIGENCE_USER;
```

### 2. Custom Intelligence Agents

```sql
-- Configure specialized agents for different user roles
CREATE OR REPLACE FUNCTION create_role_specific_agent(user_role STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    agent_config VARIANT;
BEGIN
    SET agent_config = CASE user_role
        WHEN 'executive' THEN PARSE_JSON('{
            "response_style": "executive_summary",
            "focus_areas": ["revenue_trends", "strategic_kpis", "competitive_analysis"],
            "data_access": "all_parks",
            "visualization_level": "high_level_dashboards"
        }')
        WHEN 'operations_manager' THEN PARSE_JSON('{
            "response_style": "operational_detail", 
            "focus_areas": ["guest_satisfaction", "ride_performance", "staff_efficiency"],
            "data_access": "assigned_park_only",
            "visualization_level": "detailed_metrics"
        }')
        WHEN 'marketing_team' THEN PARSE_JSON('{
            "response_style": "campaign_focused",
            "focus_areas": ["customer_demographics", "sales_conversion", "seasonal_trends"], 
            "data_access": "customer_analytics",
            "visualization_level": "marketing_charts"
        }')
        ELSE PARSE_JSON('{
            "response_style": "general_business",
            "focus_areas": ["basic_metrics"],
            "data_access": "summary_only", 
            "visualization_level": "simple_charts"
        }')
    END;
    
    RETURN agent_config;
END;
$$;
```

## 🔗 Integration with Existing Labs

### Enhanced Lab Progression

Update your hackathon structure to include agents:

1. **Labs 01-05**: Your existing foundation (keep as-is)
2. **Lab 03**: Enhanced with advanced translation features
3. **Lab 04**: Complete traditional NLP2SQL solution
4. **Lab 05**: Complete agentic AI platform (this lab)

### Migration Strategy

```sql
-- Migrate existing functions to agent-compatible format
CREATE OR REPLACE FUNCTION migrate_to_agents()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Your existing custom functions become agent tools
    -- Your conversation history becomes agent context
    -- Your business glossary becomes agent knowledge
    
    RETURN 'Migration completed: Traditional functions → Agent workflows';
END;
$$;
```

## 🎯 Business Impact Enhancement

With Agents and Intelligence, your project now provides:

### **For Business Users**
- **Zero-code data access** through Snowflake Intelligence portal
- **Conversational analytics** that understand business context
- **Multi-source insights** combining data tables and documents

### **For Technical Teams** 
- **Sophisticated agent orchestration** for complex workflows
- **Enhanced accuracy** through multi-step reasoning
- **Unified governance** across all AI interactions

### **For the Organization**
- **Scalable AI adoption** without technical barriers
- **Enterprise-grade security** inherited from Snowflake
- **Comprehensive audit trails** of all AI interactions

## 🚀 Next Steps

1. **Request access** to Cortex Agents (public preview soon)
2. **Set up** Snowflake Intelligence portal access
3. **Migrate** your existing semantic models to agent format
4. **Create** role-specific agent configurations
5. **Test** the enhanced conversational experiences

This evolution transforms your excellent NLP2SQL foundation into a comprehensive agentic AI platform that can handle any business question through intelligent orchestration! 