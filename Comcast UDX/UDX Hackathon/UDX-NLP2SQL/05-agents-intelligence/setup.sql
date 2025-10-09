-- ============================================================================
-- Lab 09: Snowflake Agents & Intelligence Setup
-- ============================================================================
-- This lab enhances your existing NLP2SQL system with advanced agentic AI
-- capabilities, building on the solid foundation from Labs 01-08.
-- ============================================================================

-- Set context
USE WAREHOUSE UDX_ANALYTICS_WAREHOUSE;
USE DATABASE UDX_NL2SQL;
USE SCHEMA BUSINESS_ANALYTICS;

-- ============================================================================
-- SECTION 1: Document Knowledge Base for Cortex Search
-- ============================================================================

-- Create enhanced document storage table
CREATE OR REPLACE TABLE UDX_DOCUMENTS (
    document_id STRING PRIMARY KEY,
    document_title STRING NOT NULL,
    document_content STRING NOT NULL,
    document_type STRING NOT NULL,  -- POLICY, PROCEDURE, TRAINING, GUIDE
    department STRING NOT NULL,     -- OPERATIONS, FINANCE, HR, MARKETING, GUEST_SERVICES
    effective_date DATE,
    classification STRING DEFAULT 'INTERNAL', -- PUBLIC, INTERNAL, CONFIDENTIAL
    last_updated TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    created_by STRING DEFAULT 'SYSTEM',
    document_url STRING,
    keywords ARRAY,
    related_tables ARRAY
) COMMENT = 'Document repository for UDX knowledge base and agent context';

-- Insert comprehensive UDX business documents
INSERT INTO UDX_DOCUMENTS VALUES
(
    'POLICY_SAFETY_001', 
    'Guest Safety and Emergency Procedures',
    'GUEST SAFETY PROTOCOLS: All rides and attractions must undergo comprehensive daily safety inspections before opening to guests. Inspection checklist includes: mechanical systems check, safety barriers verification, emergency stop system testing, and staff training verification. EMERGENCY PROCEDURES: Each park location must have designated emergency assembly points clearly marked with illuminated signs. Emergency evacuation drills must be conducted monthly for all operational staff. Staff-to-guest ratios during peak hours must maintain minimum 1:25 ratio for safety coverage. INCIDENT REPORTING: All safety incidents, regardless of severity, must be reported within 15 minutes using the UDX Safety Incident Management System. Medical emergencies require immediate notification to on-site medical staff and local emergency services. WEATHER PROTOCOLS: Operations must cease when wind speeds exceed 35 mph or during severe weather warnings. Lightning detection system triggers automatic ride shutdown when strikes detected within 5-mile radius.',
    'SAFETY_POLICY',
    'OPERATIONS',
    '2024-01-15',
    'INTERNAL',
    CURRENT_TIMESTAMP(),
    'OPERATIONS_MANAGER',
    'https://udx-internal.com/safety-protocols',
    ['safety', 'emergency', 'evacuation', 'inspection', 'weather'],
    ['PARK_PERFORMANCE', 'ATTRACTION_ANALYTICS']
),
(
    'PROC_REVENUE_001',
    'Revenue Recognition and Financial Reporting Standards',
    'REVENUE RECOGNITION PRINCIPLES: Ticket sales are recognized as revenue at the point of park entry, not at the time of purchase. This aligns with GAAP standards for service delivery. Season pass revenue must be amortized over the expected usage period based on historical attendance patterns. Merchandise sales are recorded as revenue at the point of transaction completion. Gift card sales are recorded as deferred revenue until redemption. FINANCIAL REPORTING TIMELINES: Daily revenue reports must be completed by 6 AM following the operating day. Weekly consolidated reports due every Tuesday by noon. Monthly financial statements must be completed within 5 business days of month-end. COST ALLOCATION: Operating costs should be allocated across parks based on guest attendance weighted by average spend per guest. Capital expenditures for new attractions are depreciated over 15-year useful life. Marketing costs are allocated based on regional campaign targeting.',
    'FINANCIAL_PROCEDURE',
    'FINANCE',
    '2024-01-20',
    'INTERNAL',
    CURRENT_TIMESTAMP(),
    'CFO',
    'https://udx-internal.com/finance-procedures',
    ['revenue', 'recognition', 'reporting', 'gaap', 'depreciation'],
    ['SALES_TRANSACTIONS', 'FINANCIAL_SUMMARY']
),
(
    'TRAINING_CS_001',
    'Customer Service Excellence Standards',
    'GUEST INTERACTION STANDARDS: Every guest interaction should exceed expectations and reinforce the magical UDX experience. Staff must greet guests with genuine enthusiasm within 30 seconds of approach. All guest questions must be answered accurately and completely, with follow-up to ensure satisfaction. SERVICE RECOVERY: Guest issues must be resolved within 15 minutes whenever possible. For complex issues requiring escalation, guests should be provided with regular updates every 5 minutes. Service recovery gestures should be proportional to the inconvenience experienced. UPSELLING GUIDELINES: Staff should identify natural opportunities to enhance the guest experience through appropriate recommendations. Focus on value-added services that genuinely improve the guest visit rather than purely transactional upselling. VIP EXPERIENCE PROTOCOLS: VIP guests receive dedicated concierge service with 1:10 staff ratio. VIP amenities include express lane access, reserved seating areas, and complimentary refreshments. All VIP interactions logged for personalization in future visits.',
    'TRAINING_MANUAL',
    'GUEST_SERVICES',
    '2024-02-01',
    'INTERNAL',
    CURRENT_TIMESTAMP(),
    'GUEST_SERVICES_DIRECTOR',
    'https://udx-internal.com/training-customer-service',
    ['customer service', 'guest experience', 'vip', 'training'],
    ['CUSTOMERS', 'SALES_TRANSACTIONS']
),
(
    'GUIDE_MARKETING_001',
    'Seasonal Marketing Campaign Guidelines',
    'SEASONAL CAMPAIGN STRATEGY: Peak season campaigns (June-August, December holidays) should focus on capacity management and premium experience positioning. Off-peak campaigns emphasize value propositions and special event programming. DIGITAL MARKETING: Social media campaigns must maintain consistent UDX brand voice while adapting to platform-specific best practices. Influencer partnerships require approval for partnerships exceeding $10,000 value. Email marketing campaigns should be personalized based on guest visit history and preferences. PROMOTIONAL PRICING: Discount offers should not exceed 25% of standard pricing to maintain brand premium positioning. Group sales discounts can reach 35% for groups exceeding 100 guests. CAMPAIGN MEASUREMENT: All campaigns must include trackable UTM parameters for attribution analysis. ROI measurement should include both direct sales attribution and brand awareness metrics. Campaign performance reviewed weekly during peak seasons, monthly during off-peak periods.',
    'MARKETING_GUIDE',
    'MARKETING',
    '2024-02-15',
    'INTERNAL',
    CURRENT_TIMESTAMP(),
    'MARKETING_DIRECTOR',
    'https://udx-internal.com/marketing-guidelines',
    ['marketing', 'campaigns', 'seasonal', 'digital', 'roi'],
    ['MARKETING_CAMPAIGNS', 'CUSTOMERS', 'SALES_TRANSACTIONS']
),
(
    'POLICY_HR_001',
    'Employee Performance and Recognition Programs',
    'PERFORMANCE EVALUATION: All employees receive quarterly performance reviews with specific measurable goals aligned to departmental objectives. Performance ratings use 5-point scale: Exceptional (5), Exceeds (4), Meets (3), Below (2), Unsatisfactory (1). Employees rating 4 or 5 eligible for merit increases and bonus programs. RECOGNITION PROGRAMS: Employee of the Month program recognizes outstanding service with $500 bonus and preferred parking. Annual Excellence Awards include categories for Safety Leadership, Guest Service Champion, Innovation, and Team Collaboration. Recognition should be timely, specific, and tied to UDX core values. PROFESSIONAL DEVELOPMENT: All full-time employees eligible for $2,000 annual education reimbursement for job-relevant training. Leadership development program available for high-performers with management potential. Cross-training opportunities encouraged to improve operational flexibility and employee growth.',
    'HR_POLICY',
    'HR',
    '2024-03-01',
    'INTERNAL',
    CURRENT_TIMESTAMP(),
    'HR_DIRECTOR',
    'https://udx-internal.com/hr-policies',
    ['hr', 'performance', 'recognition', 'development', 'training'],
    ['PARK_PERFORMANCE']
);

-- ============================================================================
-- SECTION 2: Create Cortex Search Service
-- ============================================================================

-- Create the Cortex Search service for document knowledge base
CREATE OR REPLACE CORTEX SEARCH SERVICE udx_knowledge_base
ON table_name = 'UDX_NL2SQL.BUSINESS_ANALYTICS.UDX_DOCUMENTS'
ATTRIBUTES = (
    'DOCUMENT_CONTENT',    -- Primary searchable content
    'DOCUMENT_TYPE',       -- Filter by document category
    'DEPARTMENT',          -- Filter by organizational unit
    'EFFECTIVE_DATE',      -- Temporal relevance
    'KEYWORDS'             -- Enhanced search targeting
)
WAREHOUSE = 'UDX_ANALYTICS_WAREHOUSE'
COMMENT = 'UDX comprehensive knowledge base for agent-enhanced business intelligence';

-- ============================================================================
-- SECTION 3: Enhanced Semantic Model for Agents
-- ============================================================================

-- Create stage for semantic model files
CREATE OR REPLACE STAGE udx_semantic_models
COMMENT = 'Storage for UDX semantic model configurations';

-- Note: In practice, you would upload the semantic model YAML file to this stage
-- For this demo, we'll create a table to store the model configuration
CREATE OR REPLACE TABLE SEMANTIC_MODEL_CONFIG (
    model_name STRING,
    model_version STRING,
    configuration VARIANT,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert the enhanced semantic model configuration
INSERT INTO SEMANTIC_MODEL_CONFIG VALUES (
    'udx_theme_park_analytics_v2',
    '2.0.0',
    PARSE_JSON('{
        "name": "UDX Theme Park Analytics - Agent Ready",
        "description": "Comprehensive business analytics for UDX theme park operations with agent orchestration support",
        "tables": [
            {
                "name": "CUSTOMERS",
                "description": "Guest information, demographics, and lifetime value",
                "columns": [
                    {"name": "CUSTOMER_ID", "description": "Unique customer identifier", "semantic_type": "primary_key"},
                    {"name": "CUSTOMER_NAME", "description": "Guest full name", "semantic_type": "dimension"},
                    {"name": "AGE_GROUP", "description": "Customer age category", "semantic_type": "dimension"},
                    {"name": "TOTAL_SPENT", "description": "Lifetime customer value in USD", "semantic_type": "measure", "aggregation": "sum"},
                    {"name": "VISIT_COUNT", "description": "Number of park visits", "semantic_type": "measure", "aggregation": "sum"},
                    {"name": "PREFERRED_PARK", "description": "Most frequently visited park", "semantic_type": "dimension"}
                ]
            },
            {
                "name": "SALES_TRANSACTIONS", 
                "description": "All ticket and merchandise sales with detailed transaction information",
                "columns": [
                    {"name": "TRANSACTION_DATE", "description": "When the purchase occurred", "semantic_type": "date"},
                    {"name": "REVENUE_AMOUNT", "description": "Transaction value in USD", "semantic_type": "measure", "aggregation": "sum"},
                    {"name": "TICKET_TYPE", "description": "Type of admission purchased", "semantic_type": "dimension"},
                    {"name": "PARK_ID", "description": "Location where purchase occurred", "semantic_type": "dimension"},
                    {"name": "CUSTOMER_ID", "description": "Guest making purchase", "semantic_type": "foreign_key"}
                ]
            },
            {
                "name": "PARK_PERFORMANCE",
                "description": "Daily operational metrics and guest satisfaction by park location",
                "columns": [
                    {"name": "PARK_NAME", "description": "Theme park location", "semantic_type": "dimension"},
                    {"name": "PERFORMANCE_DATE", "description": "Date of operational metrics", "semantic_type": "date"},
                    {"name": "GUEST_SATISFACTION_SCORE", "description": "Daily average satisfaction rating (1-10)", "semantic_type": "measure", "aggregation": "avg"},
                    {"name": "TOTAL_ATTENDANCE", "description": "Number of guests in park", "semantic_type": "measure", "aggregation": "sum"},
                    {"name": "CAPACITY_UTILIZATION", "description": "Percentage of park capacity used", "semantic_type": "measure", "aggregation": "avg"}
                ]
            }
        ],
        "business_context": [
            {
                "term": "VIP Experience",
                "definition": "Premium park access with priority ride access, dedicated concierge service, and exclusive amenities",
                "related_tables": ["CUSTOMERS", "SALES_TRANSACTIONS"],
                "agent_guidance": "When discussing VIP experiences, always include service level metrics and revenue impact"
            },
            {
                "term": "Peak Season",
                "definition": "Summer months (June-August) and holiday periods with highest attendance and revenue",
                "related_tables": ["PARK_PERFORMANCE", "SALES_TRANSACTIONS"],
                "sql_pattern": "WHERE EXTRACT(MONTH FROM transaction_date) IN (6,7,8,12)",
                "agent_guidance": "Peak season analysis should include capacity utilization and pricing strategy context"
            },
            {
                "term": "Guest Satisfaction",
                "definition": "Daily survey scores measuring overall park experience quality on 1-10 scale",
                "related_tables": ["PARK_PERFORMANCE"],
                "agent_guidance": "Always correlate satisfaction scores with operational metrics like wait times and staff ratios"
            }
        ],
        "agent_behaviors": {
            "greeting": "Hello! I\'m your UDX Business Intelligence Assistant. I can help you analyze park performance, customer data, operational metrics, and search through our knowledge base of policies and procedures.",
            "capabilities": [
                "Analyze revenue trends across all UDX parks",
                "Identify top-performing attractions and customer segments", 
                "Generate comprehensive guest satisfaction reports",
                "Search through operational policies and procedures",
                "Create executive dashboards with actionable insights",
                "Provide operational recommendations based on data and policies"
            ],
            "response_style": "business_professional",
            "include_visualizations": true,
            "suggest_follow_ups": true
        }
    }'),
    CURRENT_TIMESTAMP()
);

-- ============================================================================
-- SECTION 4: Agent Configuration Functions
-- ============================================================================

-- Create the UDX Business Intelligence Agent configuration
CREATE OR REPLACE FUNCTION create_udx_business_agent()
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    agent_config VARIANT;
BEGIN
    SET agent_config = PARSE_JSON('{
        "agent_name": "UDX_Business_Intelligence_Agent",
        "model": "claude-3-5-sonnet",
        "tools": [
            {
                "tool_spec": {
                    "type": "cortex_analyst_text_to_sql",
                    "name": "udx_data_model"
                }
            },
            {
                "tool_spec": {
                    "type": "cortex_search",
                    "name": "udx_document_search"
                }
            },
            {
                "tool_spec": {
                    "type": "sql_exec",
                    "name": "sql_executor"
                }
            },
            {
                "tool_spec": {
                    "type": "data_to_chart",
                    "name": "visualization_generator"
                }
            }
        ],
        "tool_resources": {
            "udx_data_model": {
                "semantic_model_file": "@UDX_NL2SQL.BUSINESS_ANALYTICS.udx_semantic_models/udx_semantic_model_v2.yaml"
            },
            "udx_document_search": {
                "name": "UDX_NL2SQL.BUSINESS_ANALYTICS.udx_knowledge_base",
                "max_results": 10,
                "title_column": "DOCUMENT_TITLE",
                "id_column": "DOCUMENT_ID",
                "filter": {"@ne": {"CLASSIFICATION": "CONFIDENTIAL"}}
            }
        },
        "response_instruction": "You are the UDX Business Intelligence Assistant. Provide comprehensive, actionable insights that combine data analysis with relevant business context from our knowledge base. Always include data visualizations when appropriate and suggest follow-up questions."
    }');
    
    RETURN agent_config;
END;
$$;

-- Role-specific agent configurations
CREATE OR REPLACE FUNCTION create_role_specific_agent(user_role STRING)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    agent_config VARIANT;
    role_config VARIANT;
BEGIN
    SET role_config = CASE user_role
        WHEN 'executive' THEN PARSE_JSON('{
            "response_style": "executive_summary",
            "focus_areas": ["revenue_trends", "strategic_kpis", "competitive_analysis", "roi_metrics"],
            "data_access": "all_parks",
            "visualization_level": "high_level_dashboards",
            "include_recommendations": true,
            "time_horizon": "strategic"
        }')
        WHEN 'operations_manager' THEN PARSE_JSON('{
            "response_style": "operational_detail", 
            "focus_areas": ["guest_satisfaction", "ride_performance", "staff_efficiency", "safety_metrics"],
            "data_access": "assigned_park_only",
            "visualization_level": "detailed_metrics",
            "include_recommendations": true,
            "time_horizon": "tactical"
        }')
        WHEN 'marketing_team' THEN PARSE_JSON('{
            "response_style": "campaign_focused",
            "focus_areas": ["customer_demographics", "sales_conversion", "seasonal_trends", "channel_performance"], 
            "data_access": "customer_analytics",
            "visualization_level": "marketing_charts",
            "include_recommendations": true,
            "time_horizon": "campaign_cycle"
        }')
        WHEN 'finance_team' THEN PARSE_JSON('{
            "response_style": "financial_analysis",
            "focus_areas": ["revenue_recognition", "cost_analysis", "profitability", "budget_variance"],
            "data_access": "financial_data",
            "visualization_level": "financial_reports",
            "include_recommendations": true,
            "time_horizon": "fiscal_reporting"
        }')
        ELSE PARSE_JSON('{
            "response_style": "general_business",
            "focus_areas": ["basic_metrics", "overview_reporting"],
            "data_access": "summary_only", 
            "visualization_level": "simple_charts",
            "include_recommendations": false,
            "time_horizon": "current_period"
        }')
    END;
    
    SET agent_config = OBJECT_INSERT(create_udx_business_agent(), 'role_configuration', role_config);
    
    RETURN agent_config;
END;
$$;

-- ============================================================================
-- SECTION 5: Enhanced Conversation Management
-- ============================================================================

-- Create enhanced conversation table for agent interactions
CREATE OR REPLACE TABLE AGENT_CONVERSATIONS (
    session_id STRING,
    user_id STRING,
    user_role STRING DEFAULT 'business_user',
    message_sequence INTEGER,
    user_message STRING,
    agent_response VARIANT,
    tools_used ARRAY,
    data_sources_accessed ARRAY,
    documents_referenced ARRAY,
    response_confidence NUMBER,
    response_time_ms INTEGER,
    business_context_applied VARIANT,
    visualization_generated BOOLEAN DEFAULT FALSE,
    follow_up_suggestions ARRAY,
    user_satisfaction_rating INTEGER,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_agent_conversations PRIMARY KEY (session_id, message_sequence)
) COMMENT = 'Enhanced conversation tracking with agent orchestration details';

-- Agent conversation orchestration function
CREATE OR REPLACE FUNCTION continue_agent_conversation(
    session_id STRING,
    user_message STRING,
    user_id STRING DEFAULT 'anonymous',
    user_role STRING DEFAULT 'business_user'
)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    conversation_context STRING;
    enhanced_response VARIANT;
    next_sequence INTEGER;
    start_time TIMESTAMP_LTZ;
    response_time INTEGER;
BEGIN
    SET start_time = CURRENT_TIMESTAMP();
    
    -- Get conversation context with agent-specific details
    SET conversation_context = (
        SELECT LISTAGG(
            CONCAT(
                'User: ', user_message, 
                ' | Agent: ', COALESCE(agent_response:content::STRING, 'No response'),
                ' | Tools: ', ARRAY_TO_STRING(COALESCE(tools_used, ARRAY_CONSTRUCT()), ', '),
                ' | Business Context: ', COALESCE(business_context_applied:summary::STRING, 'None')
            ), ' || '
        ) WITHIN GROUP (ORDER BY message_sequence DESC)
        FROM AGENT_CONVERSATIONS 
        WHERE session_id = session_id
        ORDER BY message_sequence DESC
        LIMIT 3
    );
    
    -- Get next sequence number
    SET next_sequence = (
        SELECT COALESCE(MAX(message_sequence), 0) + 1 
        FROM AGENT_CONVERSATIONS 
        WHERE session_id = session_id
    );
    
    -- Build comprehensive prompt for agent
    SET enhanced_response = PARSE_JSON(CONCAT('{
        "content": "Enhanced agent response for: ', REPLACE(user_message, '"', '\\"'), '",
        "tools_used": ["cortex_analyst", "cortex_search"],
        "data_sources": ["CUSTOMERS", "SALES_TRANSACTIONS", "PARK_PERFORMANCE"],
        "documents": ["POLICY_SAFETY_001", "PROC_REVENUE_001"],
        "confidence": 0.92,
        "business_context": {
            "summary": "Applied UDX theme park business context and policies",
            "relevant_policies": ["Guest Safety", "Revenue Recognition"]
        },
        "has_visualization": true,
        "suggestions": ["What are the safety compliance trends?", "How does satisfaction correlate with revenue?"]
    }'));
    
    -- Calculate response time
    SET response_time = DATEDIFF('millisecond', start_time, CURRENT_TIMESTAMP());
    
    -- Store enhanced conversation record
    INSERT INTO AGENT_CONVERSATIONS VALUES (
        session_id, user_id, user_role, next_sequence, user_message, 
        enhanced_response,
        enhanced_response:tools_used::ARRAY,
        enhanced_response:data_sources::ARRAY,
        enhanced_response:documents::ARRAY,
        enhanced_response:confidence::NUMBER,
        response_time,
        enhanced_response:business_context::VARIANT,
        enhanced_response:has_visualization::BOOLEAN,
        enhanced_response:suggestions::ARRAY,
        NULL, -- user_satisfaction_rating to be filled later
        CURRENT_TIMESTAMP()
    );
    
    RETURN enhanced_response;
END;
$$;

-- ============================================================================
-- SECTION 6: Snowflake Intelligence Preparation
-- ============================================================================

-- Create Intelligence-ready views for business users
CREATE OR REPLACE VIEW INTELLIGENCE_PARK_ANALYTICS AS
SELECT 
    'UDX Theme Parks' as data_source,
    'Comprehensive park performance and revenue analytics' as description,
    p.park_name,
    p.performance_date as analysis_date,
    SUM(s.revenue_amount) as daily_revenue,
    COUNT(DISTINCT s.customer_id) as unique_visitors,
    AVG(p.guest_satisfaction_score) as avg_satisfaction,
    AVG(p.capacity_utilization) as avg_capacity_utilization,
    COUNT(s.transaction_id) as total_transactions
FROM BUSINESS_ANALYTICS.SALES_TRANSACTIONS s
RIGHT JOIN BUSINESS_ANALYTICS.PARK_PERFORMANCE p 
    ON s.park_id = p.park_id AND s.transaction_date = p.performance_date
GROUP BY p.park_name, p.performance_date
COMMENT = 'Intelligence-ready view combining revenue and operational metrics';

-- Customer insights view for Intelligence
CREATE OR REPLACE VIEW INTELLIGENCE_CUSTOMER_INSIGHTS AS
SELECT 
    'UDX Customer Analytics' as data_source,
    'Customer behavior and lifetime value analysis' as description,
    c.customer_name,
    c.age_group,
    c.preferred_park,
    c.total_spent as lifetime_value,
    c.visit_count,
    s.avg_transaction_value,
    s.last_visit_date,
    CASE 
        WHEN c.total_spent > 1000 THEN 'VIP'
        WHEN c.total_spent > 500 THEN 'Premium'
        ELSE 'Standard'
    END as customer_tier
FROM BUSINESS_ANALYTICS.CUSTOMERS c
LEFT JOIN (
    SELECT 
        customer_id,
        AVG(revenue_amount) as avg_transaction_value,
        MAX(transaction_date) as last_visit_date
    FROM BUSINESS_ANALYTICS.SALES_TRANSACTIONS
    GROUP BY customer_id
) s ON c.customer_id = s.customer_id
COMMENT = 'Customer segmentation and behavior analysis for business intelligence';

-- ============================================================================
-- SECTION 7: Agent Performance Monitoring
-- ============================================================================

-- Agent performance metrics table
CREATE OR REPLACE TABLE AGENT_PERFORMANCE_METRICS (
    metric_date DATE,
    agent_type STRING,
    total_queries INTEGER,
    successful_responses INTEGER,
    avg_response_time_ms NUMBER,
    avg_confidence_score NUMBER,
    user_satisfaction_avg NUMBER,
    tools_usage_breakdown VARIANT,
    popular_question_types ARRAY,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Performance monitoring for agent interactions and effectiveness';

-- Function to calculate daily agent performance
CREATE OR REPLACE FUNCTION calculate_agent_performance(analysis_date DATE DEFAULT CURRENT_DATE())
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    performance_summary VARIANT;
BEGIN
    SELECT OBJECT_CONSTRUCT(
        'date', analysis_date,
        'total_conversations', COUNT(*),
        'avg_response_time', AVG(response_time_ms),
        'avg_confidence', AVG(response_confidence),
        'satisfaction_score', AVG(user_satisfaction_rating),
        'tools_used', OBJECT_CONSTRUCT(
            'cortex_analyst', SUM(CASE WHEN ARRAY_CONTAINS('cortex_analyst'::VARIANT, tools_used) THEN 1 ELSE 0 END),
            'cortex_search', SUM(CASE WHEN ARRAY_CONTAINS('cortex_search'::VARIANT, tools_used) THEN 1 ELSE 0 END),
            'visualization', SUM(CASE WHEN visualization_generated THEN 1 ELSE 0 END)
        )
    ) INTO performance_summary
    FROM AGENT_CONVERSATIONS
    WHERE DATE(created_at) = analysis_date;
    
    RETURN performance_summary;
END;
$$;

-- ============================================================================
-- SECTION 8: Access Control for Agents
-- ============================================================================

-- Create roles for different agent access levels
CREATE OR REPLACE ROLE AGENT_ORCHESTRATOR
COMMENT = 'Role for agent system operations and orchestration';

CREATE OR REPLACE ROLE INTELLIGENCE_USER
COMMENT = 'Role for Snowflake Intelligence portal access';

CREATE OR REPLACE ROLE AGENT_ADMIN
COMMENT = 'Administrative role for agent configuration and monitoring';

-- Grant permissions for agent operations
GRANT USAGE ON WAREHOUSE UDX_ANALYTICS_WAREHOUSE TO ROLE AGENT_ORCHESTRATOR;
GRANT USAGE ON DATABASE UDX_NL2SQL TO ROLE AGENT_ORCHESTRATOR;
GRANT USAGE ON SCHEMA UDX_NL2SQL.BUSINESS_ANALYTICS TO ROLE AGENT_ORCHESTRATOR;
GRANT SELECT ON ALL TABLES IN SCHEMA UDX_NL2SQL.BUSINESS_ANALYTICS TO ROLE AGENT_ORCHESTRATOR;
GRANT USAGE ON CORTEX SEARCH SERVICE udx_knowledge_base TO ROLE AGENT_ORCHESTRATOR;

-- Grant Intelligence user permissions
GRANT USAGE ON WAREHOUSE UDX_ANALYTICS_WAREHOUSE TO ROLE INTELLIGENCE_USER;
GRANT USAGE ON DATABASE UDX_NL2SQL TO ROLE INTELLIGENCE_USER;
GRANT USAGE ON SCHEMA UDX_NL2SQL.BUSINESS_ANALYTICS TO ROLE INTELLIGENCE_USER;
GRANT SELECT ON VIEW UDX_NL2SQL.BUSINESS_ANALYTICS.INTELLIGENCE_PARK_ANALYTICS TO ROLE INTELLIGENCE_USER;
GRANT SELECT ON VIEW UDX_NL2SQL.BUSINESS_ANALYTICS.INTELLIGENCE_CUSTOMER_INSIGHTS TO ROLE INTELLIGENCE_USER;

-- Grant admin permissions
GRANT ALL ON SCHEMA UDX_NL2SQL.BUSINESS_ANALYTICS TO ROLE AGENT_ADMIN;
GRANT AGENT_ORCHESTRATOR TO ROLE AGENT_ADMIN;
GRANT INTELLIGENCE_USER TO ROLE AGENT_ADMIN;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify document knowledge base
SELECT 
    COUNT(*) as total_documents,
    department,
    document_type
FROM UDX_DOCUMENTS 
GROUP BY department, document_type
ORDER BY department, document_type;

-- Test Cortex Search service
SELECT 
    SNOWFLAKE.CORTEX.SEARCH(
        'udx_knowledge_base',
        'guest safety emergency procedures'
    ) as search_results;

-- Verify agent configuration
SELECT create_udx_business_agent() as agent_config;

-- Check Intelligence views
SELECT COUNT(*) as records FROM INTELLIGENCE_PARK_ANALYTICS;
SELECT COUNT(*) as records FROM INTELLIGENCE_CUSTOMER_INSIGHTS;

-- Display setup completion
SELECT 'Lab 09 Setup Complete! Ready for Snowflake Agents and Intelligence.' as status; 