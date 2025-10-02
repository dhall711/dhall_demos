-- =====================================================================================
-- Snowflake Semantic Views for Comcast Revenue Intelligence Platform
-- Converted from ude_comcast_revenue.yaml semantic model
-- 
-- Description: Business-Centric Revenue Intelligence Platform - AI-powered anticipatory 
-- billing issue detection, customer risk clustering, promotion stacking prevention, 
-- and revenue protection analytics optimized for executive decision-making and operational excellence
--
-- CORTEX ANALYST COMPATIBILITY NOTES:
-- - These are structured views designed as the semantic layer for Cortex Analyst
-- - Used in conjunction with the YAML semantic model for optimal Cortex integration
-- - Provide business intelligence views optimized for natural language queries
-- - Complement the YAML semantic model with complex business logic and calculations
-- =====================================================================================

-- =====================================================================================
-- Set Database and Schema Context
-- =====================================================================================

USE DATABASE COMCAST_DEMO;
USE SCHEMA RECONCILIATION;

-- =====================================================================================
-- Cleanup: Drop any previously created regular views before creating semantic views
-- =====================================================================================

DROP VIEW IF EXISTS COMCAST_REVENUE_INTELLIGENCE;
DROP VIEW IF EXISTS EXECUTIVE_REVENUE_DASHBOARD;
DROP VIEW IF EXISTS CUSTOMER_RISK_CLUSTERS;
DROP VIEW IF EXISTS CUSTOMER_RISK_CLUSTERS_LEGACY;
DROP VIEW IF EXISTS ANTICIPATORY_BILLING_ISSUES;
DROP VIEW IF EXISTS REGIONAL_PERFORMANCE_ANALYSIS;
DROP VIEW IF EXISTS FIRST_BILL_ACCURACY_ANALYSIS;
DROP VIEW IF EXISTS MOBILE_LINE_CONFLICTS;

-- =====================================================================================
-- Main Semantic View: Comcast Revenue Intelligence Hub
-- Structured semantic view for Cortex Analyst with proper table/dimension/fact definitions
-- =====================================================================================

CREATE OR REPLACE SEMANTIC VIEW COMCAST_REVENUE_INTELLIGENCE
  TABLES (
    promotion_reconciliation AS COMCAST_DEMO.RECONCILIATION.PROMOTION_RECONCILIATION PRIMARY KEY (record_id),
    order_system_data AS COMCAST_DEMO.RECONCILIATION.ORDER_SYSTEM_DATA PRIMARY KEY (order_id),
    billing_system_data AS COMCAST_DEMO.RECONCILIATION.BILLING_SYSTEM_DATA PRIMARY KEY (billing_id),
    products AS COMCAST_DEMO.RECONCILIATION.PRODUCTS PRIMARY KEY (product_id),
    promotion_types AS COMCAST_DEMO.RECONCILIATION.PROMOTION_TYPES PRIMARY KEY (promo_code)
  )
  RELATIONSHIPS (
    order_system_data (product_id) REFERENCES products,
    billing_system_data (product_id) REFERENCES products,
    promotion_reconciliation (product_id) REFERENCES products,
    promotion_reconciliation (promo_code) REFERENCES promotion_types
  )
  FACTS (
    promotion_reconciliation.discount_variance AS promotion_reconciliation.discount_variance,
    promotion_reconciliation.final_amount_variance AS promotion_reconciliation.final_amount_variance,
    promotion_reconciliation.order_base_amount AS promotion_reconciliation.order_base_amount,
    promotion_reconciliation.order_discount_amount AS promotion_reconciliation.order_discount_amount,
    promotion_reconciliation.order_final_amount AS promotion_reconciliation.order_final_amount,
    promotion_reconciliation.billing_base_amount AS promotion_reconciliation.billing_base_amount,
    promotion_reconciliation.billing_discount_amount AS promotion_reconciliation.billing_discount_amount,
    promotion_reconciliation.billing_final_amount AS promotion_reconciliation.billing_final_amount,
    order_system_data.base_amount AS order_system_data.base_amount,
    order_system_data.discount_amount AS order_system_data.discount_amount,
    order_system_data.final_amount AS order_system_data.final_amount,
    billing_system_data.base_amount AS billing_system_data.base_amount,
    billing_system_data.discount_amount AS billing_system_data.discount_amount,
    billing_system_data.final_amount AS billing_system_data.final_amount
  )
  DIMENSIONS (
    promotion_reconciliation.record_id AS promotion_reconciliation.record_id,
    promotion_reconciliation.customer_id AS promotion_reconciliation.customer_id,
    promotion_reconciliation.transaction_date AS promotion_reconciliation.transaction_date,
    promotion_reconciliation.product_id AS promotion_reconciliation.product_id,
    promotion_reconciliation.product_name AS promotion_reconciliation.product_name,
    promotion_reconciliation.product_category AS promotion_reconciliation.product_category,
    promotion_reconciliation.promo_code AS promotion_reconciliation.promo_code,
    promotion_reconciliation.promo_name AS promotion_reconciliation.promo_name,
    promotion_reconciliation.reconciliation_status AS promotion_reconciliation.reconciliation_status,
    promotion_reconciliation.risk_level AS promotion_reconciliation.risk_level,
    products.product_name AS products.product_name,
    products.product_category AS products.product_category,
    products.service_type AS products.service_type,
    promotion_types.promo_name AS promotion_types.promo_name,
    promotion_types.discount_type AS promotion_types.discount_type,
    order_system_data.customer_id AS order_system_data.customer_id,
    order_system_data.order_date AS order_system_data.order_date,
    order_system_data.product_id AS order_system_data.product_id,
    order_system_data.promo_code AS order_system_data.promo_code,
    order_system_data.order_status AS order_system_data.order_status,
    billing_system_data.customer_id AS billing_system_data.customer_id,
    billing_system_data.billing_date AS billing_system_data.billing_date,
    billing_system_data.product_id AS billing_system_data.product_id,
    billing_system_data.promo_code AS billing_system_data.promo_code
  )
  METRICS (
    promotion_reconciliation.match_rate_percent AS (COUNT(CASE WHEN promotion_reconciliation.reconciliation_status = 'MATCHED' THEN 1 END) * 100.0) / COUNT(promotion_reconciliation.record_id),
    promotion_reconciliation.revenue_protection_value AS SUM(CASE WHEN promotion_reconciliation.risk_level = 'HIGH' THEN ABS(promotion_reconciliation.discount_variance) ELSE 0 END),
    promotion_reconciliation.average_variance_per_record AS SUM(ABS(promotion_reconciliation.discount_variance)) / NULLIF(COUNT(promotion_reconciliation.record_id), 0),
    promotion_reconciliation.total_discount_variance AS SUM(promotion_reconciliation.discount_variance),
    promotion_reconciliation.total_amount_variance AS SUM(promotion_reconciliation.final_amount_variance),
    promotion_reconciliation.total_records AS COUNT(promotion_reconciliation.record_id),
    order_system_data.total_order_base_amount AS SUM(order_system_data.base_amount),
    order_system_data.total_order_discount AS SUM(order_system_data.discount_amount),
    order_system_data.total_order_final_amount AS SUM(order_system_data.final_amount),
    billing_system_data.total_billing_base_amount AS SUM(billing_system_data.base_amount),
    billing_system_data.total_billing_discount AS SUM(billing_system_data.discount_amount),
    billing_system_data.total_billing_final_amount AS SUM(billing_system_data.final_amount),
    promotion_reconciliation.high_risk_count AS COUNT(CASE WHEN promotion_reconciliation.risk_level = 'HIGH' THEN 1 END),
    promotion_reconciliation.medium_risk_count AS COUNT(CASE WHEN promotion_reconciliation.risk_level = 'MEDIUM' THEN 1 END),
    promotion_reconciliation.low_risk_count AS COUNT(CASE WHEN promotion_reconciliation.risk_level = 'LOW' THEN 1 END)
  )
  COMMENT = 'Business-Centric Revenue Intelligence Platform for AI-powered anticipatory billing issue detection, customer risk clustering, promotion stacking prevention, and revenue protection analytics';

-- =====================================================================================
-- Executive Dashboard View: Key Business Metrics
-- Provides executive-level KPIs and summary metrics
-- =====================================================================================

CREATE OR REPLACE SEMANTIC VIEW EXECUTIVE_REVENUE_DASHBOARD
  TABLES (
    promotion_reconciliation AS COMCAST_DEMO.RECONCILIATION.PROMOTION_RECONCILIATION PRIMARY KEY (record_id)
  )
  FACTS (
    promotion_reconciliation.discount_variance AS promotion_reconciliation.discount_variance,
    promotion_reconciliation.final_amount_variance AS promotion_reconciliation.final_amount_variance,
    promotion_reconciliation.order_base_amount AS promotion_reconciliation.order_base_amount,
    promotion_reconciliation.billing_base_amount AS promotion_reconciliation.billing_base_amount
  )
  DIMENSIONS (
    promotion_reconciliation.reconciliation_status AS promotion_reconciliation.reconciliation_status,
    promotion_reconciliation.risk_level AS promotion_reconciliation.risk_level,
    promotion_reconciliation.product_category AS promotion_reconciliation.product_category,
    promotion_reconciliation.customer_id AS promotion_reconciliation.customer_id,
    promotion_reconciliation.product_name AS promotion_reconciliation.product_name
  )
  METRICS (
    promotion_reconciliation.match_rate_pct AS (COUNT(CASE WHEN promotion_reconciliation.reconciliation_status = 'MATCHED' THEN 1 END) * 100.0) / COUNT(promotion_reconciliation.record_id),
    promotion_reconciliation.total_transactions AS COUNT(promotion_reconciliation.record_id),
    promotion_reconciliation.matched_records AS COUNT(CASE WHEN promotion_reconciliation.reconciliation_status = 'MATCHED' THEN 1 END),
    promotion_reconciliation.exception_records AS COUNT(CASE WHEN promotion_reconciliation.reconciliation_status != 'MATCHED' THEN 1 END),
    promotion_reconciliation.high_risk_count AS COUNT(CASE WHEN promotion_reconciliation.risk_level = 'HIGH' THEN 1 END),
    promotion_reconciliation.medium_risk_count AS COUNT(CASE WHEN promotion_reconciliation.risk_level = 'MEDIUM' THEN 1 END),
    promotion_reconciliation.low_risk_count AS COUNT(CASE WHEN promotion_reconciliation.risk_level = 'LOW' THEN 1 END),
    promotion_reconciliation.total_variance AS SUM(ABS(promotion_reconciliation.discount_variance)),
    promotion_reconciliation.revenue_protection_value AS SUM(CASE WHEN promotion_reconciliation.risk_level = 'HIGH' THEN ABS(promotion_reconciliation.discount_variance) ELSE 0 END)
  )
  COMMENT = 'Executive dashboard metrics for revenue assurance performance and business impact measurement';

-- =====================================================================================
-- Note: Additional semantic views can be created using the same pattern
-- For brevity, showing the main semantic views above. Additional views would follow
-- the same TABLES/RELATIONSHIPS/DIMENSIONS/FACTS/METRICS structure.
-- =====================================================================================

-- Example: Customer Risk Clustering Semantic View would be:
-- CREATE OR REPLACE SEMANTIC VIEW CUSTOMER_RISK_CLUSTERS
--   TABLES (CUSTOMER_PROFILES, PROMOTION_RECONCILIATION)  
--   RELATIONSHIPS (CUSTOMER_PROFILES.CUSTOMER_ID = PROMOTION_RECONCILIATION.CUSTOMER_ID)
--   DIMENSIONS (CUSTOMER_PROFILES.CUSTOMER_SEGMENT, CUSTOMER_PROFILES.PROMOTION_USAGE_FREQUENCY)
--   FACTS (COUNT(*), AVG(CUSTOMER_PROFILES.CHURN_RISK_SCORE), SUM(PROMOTION_RECONCILIATION.ABS_VARIANCE))
--   METRICS (high_risk_customers = COUNT(CASE WHEN CUSTOMER_PROFILES.CHURN_RISK_SCORE > 0.3 THEN 1 END))

-- Legacy view format for reference (convert to semantic view as needed):
CREATE OR REPLACE VIEW CUSTOMER_RISK_CLUSTERS_LEGACY AS
SELECT 
    pr.customer_id,
    pr.product_category,
    pr.reconciliation_status,
    pr.risk_level,
    
    -- Aggregate Metrics
    COUNT(*) AS TOTAL_RECONCILIATION_RECORDS,
    SUM(CASE WHEN pr.risk_level = 'HIGH' THEN 1 ELSE 0 END) AS HIGH_RISK_ISSUES,
    SUM(CASE WHEN pr.risk_level = 'MEDIUM' THEN 1 ELSE 0 END) AS MEDIUM_RISK_ISSUES,
    SUM(CASE WHEN pr.risk_level = 'LOW' THEN 1 ELSE 0 END) AS LOW_RISK_ISSUES,
    
    -- Financial Impact
    SUM(ABS(pr.discount_variance)) AS TOTAL_VARIANCE_IMPACT,
    SUM(CASE WHEN pr.risk_level = 'HIGH' THEN ABS(pr.discount_variance) ELSE 0 END) AS REVENUE_PROTECTED,
    AVG(ABS(pr.discount_variance)) AS AVG_VARIANCE_PER_RECORD,
    
    -- Match Rate Analysis
    SUM(CASE WHEN pr.reconciliation_status = 'MATCHED' THEN 1 ELSE 0 END) AS MATCHED_RECORDS,
    ROUND(SUM(CASE WHEN pr.reconciliation_status = 'MATCHED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS MATCH_RATE_PCT,
    
    -- Product Analysis
    COUNT(DISTINCT pr.product_id) AS UNIQUE_PRODUCTS,
    COUNT(DISTINCT pr.promo_code) AS UNIQUE_PROMOTIONS

FROM PROMOTION_RECONCILIATION pr
WHERE pr.customer_id IS NOT NULL
GROUP BY pr.customer_id, pr.product_category, pr.reconciliation_status, pr.risk_level
ORDER BY HIGH_RISK_ISSUES DESC, TOTAL_VARIANCE_IMPACT DESC;

-- =====================================================================================
-- Anticipatory Billing Issues View: Proactive Issue Detection
-- Identifies potential billing issues before invoice generation
-- =====================================================================================

CREATE OR REPLACE VIEW ANTICIPATORY_BILLING_ISSUES AS
SELECT 
    CUSTOMER_ID,
    CUSTOMER_SEGMENT,
    CHURN_RISK_SCORE,
    BUSINESS_ISSUE_CLASSIFICATION,
    BUSINESS_PRIORITY,
    NEXT_BILL_DATE,
    CYCLE_MISS_REASON,
    CYCLE_TIMING_VARIANCE,
    PROMO_CODE,
    PROMO_NAME,
    PRODUCT_CATEGORY,
    RISK_LEVEL,
    ABS_VARIANCE,
    
    -- Days until next billing
    DATEDIFF(day, CURRENT_DATE(), NEXT_BILL_DATE) AS DAYS_UNTIL_BILLING,
    
    -- Recommended Action
    CASE 
        WHEN CYCLE_MISS_REASON = 'LATE_ACTIVATION' AND CHURN_RISK_SCORE > 0.3 THEN 'URGENT_INTERVENTION'
        WHEN CYCLE_MISS_REASON = 'LATE_ACTIVATION' THEN 'PROACTIVE_REVIEW'
        WHEN PRORATION_APPLIED = TRUE THEN 'MONITOR_BILLING'
        WHEN BUSINESS_ISSUE_CLASSIFICATION = 'STACKING_VIOLATION' THEN 'BLOCK_PROMOTION'
        WHEN BUSINESS_ISSUE_CLASSIFICATION = 'FIRST_BILL_ISSUE' THEN 'FIRST_BILL_REVIEW'
        ELSE 'STANDARD_PROCESSING'
    END AS RECOMMENDED_ACTION,
    
    -- Priority Score (higher = more urgent)
    CASE 
        WHEN BUSINESS_PRIORITY = 'CHURN_RISK' THEN 100
        WHEN BUSINESS_PRIORITY = 'CUSTOMER_EXPERIENCE' THEN 90
        WHEN BUSINESS_PRIORITY = 'MOBILE_PRIORITY' THEN 80
        ELSE 50
    END + 
    CASE 
        WHEN RISK_LEVEL = 'HIGH' THEN 50
        WHEN RISK_LEVEL = 'MEDIUM' THEN 25
        ELSE 0
    END +
    CASE 
        WHEN ABS_VARIANCE > 50 THEN 30
        WHEN ABS_VARIANCE > 20 THEN 20
        WHEN ABS_VARIANCE > 10 THEN 10
        ELSE 0
    END AS PRIORITY_SCORE

FROM COMCAST_REVENUE_INTELLIGENCE
WHERE BUSINESS_ISSUE_CLASSIFICATION IN ('STACKING_VIOLATION', 'PROMO_TIMING_MISMATCH', 'FIRST_BILL_ISSUE', 'DUPLICATE_LINE_NUMBER')
  AND NEXT_BILL_DATE > CURRENT_DATE()
  AND NEXT_BILL_DATE <= CURRENT_DATE() + 30  -- Focus on next 30 days
ORDER BY PRIORITY_SCORE DESC, DAYS_UNTIL_BILLING ASC;

-- =====================================================================================
-- Regional Performance View: Geographic Analysis
-- Provides regional performance metrics for operational routing
-- =====================================================================================

CREATE OR REPLACE VIEW REGIONAL_PERFORMANCE_ANALYSIS AS
SELECT 
    SERVICE_REGION,
    SERVICE_STATE,
    COUNT(DISTINCT SERVICE_CITY) AS CITIES_COUNT,
    
    -- Volume Metrics
    COUNT(*) AS TOTAL_TRANSACTIONS,
    COUNT(DISTINCT CUSTOMER_ID) AS UNIQUE_CUSTOMERS,
    
    -- Performance Metrics
    SUM(CASE WHEN RECONCILIATION_STATUS = 'MATCHED' THEN 1 ELSE 0 END) AS MATCHED_RECORDS,
    ROUND(SUM(CASE WHEN RECONCILIATION_STATUS = 'MATCHED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS MATCH_RATE_PCT,
    
    -- Risk Distribution
    SUM(CASE WHEN RISK_LEVEL = 'HIGH' THEN 1 ELSE 0 END) AS HIGH_RISK_COUNT,
    SUM(CASE WHEN RISK_LEVEL = 'MEDIUM' THEN 1 ELSE 0 END) AS MEDIUM_RISK_COUNT,
    SUM(CASE WHEN RISK_LEVEL = 'LOW' THEN 1 ELSE 0 END) AS LOW_RISK_COUNT,
    
    -- Business Issues by Region
    SUM(CASE WHEN BUSINESS_ISSUE_CLASSIFICATION = 'FIRST_BILL_ISSUE' THEN 1 ELSE 0 END) AS FIRST_BILL_ISSUES,
    SUM(CASE WHEN BUSINESS_ISSUE_CLASSIFICATION = 'STACKING_VIOLATION' THEN 1 ELSE 0 END) AS STACKING_VIOLATIONS,
    SUM(CASE WHEN BUSINESS_ISSUE_CLASSIFICATION = 'PROMO_TIMING_MISMATCH' THEN 1 ELSE 0 END) AS TIMING_ISSUES,
    SUM(CASE WHEN BUSINESS_ISSUE_CLASSIFICATION = 'DUPLICATE_LINE_NUMBER' THEN 1 ELSE 0 END) AS MOBILE_CONFLICTS,
    
    -- Financial Impact
    SUM(ABS_VARIANCE) AS TOTAL_VARIANCE,
    AVG(ABS_VARIANCE) AS AVG_VARIANCE,
    SUM(REVENUE_PROTECTION_VALUE) AS REVENUE_PROTECTED,
    
    -- Customer Risk
    AVG(CHURN_RISK_SCORE) AS AVG_CHURN_RISK,
    SUM(CASE WHEN HIGH_CHURN_RISK_FLAG = 1 THEN 1 ELSE 0 END) AS HIGH_CHURN_CUSTOMERS,
    
    -- Product Mix
    COUNT(CASE WHEN PRODUCT_CATEGORY = 'Internet' THEN 1 END) AS INTERNET_TRANSACTIONS,
    COUNT(CASE WHEN PRODUCT_CATEGORY = 'Television' THEN 1 END) AS TV_TRANSACTIONS,
    COUNT(CASE WHEN PRODUCT_CATEGORY = 'Mobile' THEN 1 END) AS MOBILE_TRANSACTIONS,
    COUNT(CASE WHEN PRODUCT_CATEGORY = 'Security' THEN 1 END) AS SECURITY_TRANSACTIONS,
    COUNT(CASE WHEN PRODUCT_CATEGORY = 'Business' THEN 1 END) AS BUSINESS_TRANSACTIONS

FROM COMCAST_REVENUE_INTELLIGENCE
GROUP BY SERVICE_REGION, SERVICE_STATE
ORDER BY TOTAL_VARIANCE DESC, HIGH_RISK_COUNT DESC;

-- =====================================================================================
-- Specialized Semantic Views: Business-Specific Analytics
-- Pre-validated semantic views for specific business use cases
-- =====================================================================================

-- First Bill Accuracy Analysis
CREATE OR REPLACE VIEW FIRST_BILL_ACCURACY_ANALYSIS AS
SELECT 
    'FIRST_BILL_ACCURACY' AS METRIC_TYPE,
    COUNT(*) AS TOTAL_FIRST_BILLS,
    SUM(CASE WHEN RECONCILIATION_STATUS = 'MATCHED' THEN 1 ELSE 0 END) AS ACCURATE_BILLS,
    ROUND(
        SUM(CASE WHEN RECONCILIATION_STATUS = 'MATCHED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS ACCURACY_PERCENTAGE,
    95.0 AS TARGET_PERCENTAGE,
    SUM(CASE WHEN RECONCILIATION_STATUS != 'MATCHED' THEN 1 ELSE 0 END) AS FAILURE_CASES,
    SUM(CASE WHEN RECONCILIATION_STATUS != 'MATCHED' THEN ABS_VARIANCE ELSE 0 END) AS FAILURE_IMPACT
FROM COMCAST_REVENUE_INTELLIGENCE
WHERE FIRST_BILL_FLAG = 1;

-- Mobile Line Conflict Detection
CREATE OR REPLACE VIEW MOBILE_LINE_CONFLICTS AS
SELECT 
    ORDER_LINE_NUMBER AS LINE_NUMBER,
    COUNT(DISTINCT CUSTOMER_ID) AS CUSTOMER_COUNT,
    COUNT(DISTINCT ORDER_ACCOUNT_ID) AS ACCOUNT_COUNT,
    COUNT(*) AS TRANSACTION_COUNT,
    LISTAGG(DISTINCT CUSTOMER_ID, ', ') AS CUSTOMER_LIST,
    LISTAGG(DISTINCT SERVICE_REGION, ', ') AS REGIONS_AFFECTED,
    SUM(CASE WHEN RISK_LEVEL = 'HIGH' THEN 1 ELSE 0 END) AS HIGH_RISK_CONFLICTS,
    SUM(ABS_VARIANCE) AS TOTAL_VARIANCE_IMPACT
FROM COMCAST_REVENUE_INTELLIGENCE
WHERE ORDER_LINE_NUMBER IS NOT NULL
  AND PRODUCT_CATEGORY = 'Mobile'
GROUP BY ORDER_LINE_NUMBER
HAVING COUNT(DISTINCT CUSTOMER_ID) > 1
ORDER BY CUSTOMER_COUNT DESC, TOTAL_VARIANCE_IMPACT DESC;

-- =====================================================================================
-- Comments and Usage Instructions
-- =====================================================================================

/*
SNOWFLAKE SEMANTIC VIEWS USAGE INSTRUCTIONS:

1. PROPER SEMANTIC VIEW SYNTAX:
   - Uses CREATE SEMANTIC VIEW with TABLES, RELATIONSHIPS, DIMENSIONS, FACTS, METRICS
   - Native Snowflake semantic layer for Cortex Analyst integration
   - Structured metadata enables intelligent AI query understanding

2. MAIN SEMANTIC VIEWS CREATED:
   - COMCAST_REVENUE_INTELLIGENCE: Comprehensive revenue analytics semantic view
   - EXECUTIVE_REVENUE_DASHBOARD: Executive KPI and metrics semantic view
   - Additional views can be created following the same pattern

3. SEMANTIC VIEW STRUCTURE:
   - TABLES: Physical tables that participate in the semantic view
   - RELATIONSHIPS: How tables are joined together
   - DIMENSIONS: Categorical attributes for grouping and filtering
   - FACTS: Aggregated measures for analysis
   - METRICS: Calculated KPIs and business metrics

4. CORTEX ANALYST BENEFITS:
   - Native integration with Snowflake Intelligence
   - Optimized for natural language query generation
   - Automatic query optimization for AI/ML workloads
   - Rich metadata for intelligent business context understanding

5. SEMANTIC VIEW vs YAML MODEL:
   - Semantic Views: SQL-based semantic layer in Snowflake
   - YAML Models: Configuration-based semantic model for Cortex
   - Both approaches: Can be used together or independently
   - Best Practice: Use semantic views for complex business logic, YAML for simpler structures

EXAMPLE SEMANTIC VIEW SYNTAX:
CREATE SEMANTIC VIEW my_view
  TABLES (table1, table2)
  RELATIONSHIPS (table1.id = table2.id)
  DIMENSIONS (table1.category, table2.status)
  FACTS (COUNT(*), SUM(table1.amount))
  METRICS (avg_amount = SUM(table1.amount) / COUNT(*))

CORTEX ANALYST COMPATIBILITY:
- Full native support for semantic views
- Enhanced natural language query capabilities
- Automatic SQL generation from business questions
- Optimized for analytical and ML workloads
*/
