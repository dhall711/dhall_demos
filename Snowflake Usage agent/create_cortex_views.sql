-- ============================================================================
-- Cortex AI Usage Monitoring - Complete View Creation Script
-- ============================================================================
-- This script creates all necessary views for comprehensive Cortex AI monitoring:
--   1. Query-level views (from QUERY_HISTORY) - detailed per-query tracking
--   2. Token-level view (from CORTEX_FUNCTIONS_USAGE_HISTORY) - aggregated token metrics
--
-- Documentation: See Cortex_AI_Semantic_Model_Documentation.md
-- ============================================================================

-- Set your database and schema context
USE DATABASE PLATFORM_ANALYTICS;
USE SCHEMA PUBLIC;

-- ============================================================================
-- PART 1: QUERY-LEVEL VIEWS (Detailed Per-Query Tracking)
-- Source: SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
-- Use For: User attribution, query tags, individual query debugging
-- ============================================================================

-- 1. LLM Usage View (COMPLETE, CLASSIFY_TEXT, EXTRACT_ANSWER, PARSE_DOCUMENT)
CREATE OR REPLACE VIEW CORTEX_LLM_USAGE_VIEW AS
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.COMPLETE%' 
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.CLASSIFY_TEXT%'
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.EXTRACT_ANSWER%'
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.PARSE_DOCUMENT%';

-- 2. Embedding Usage View (EMBED_TEXT)
CREATE OR REPLACE VIEW CORTEX_EMBEDDING_USAGE_VIEW AS
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.EMBED_TEXT%';

-- 3. Search Usage View (CORTEX.SEARCH)
CREATE OR REPLACE VIEW CORTEX_SEARCH_USAGE_VIEW AS
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.SEARCH%' 
   OR QUERY_TEXT ILIKE '%CORTEX SEARCH SERVICE%';

-- 4. Other Functions View (SENTIMENT, TRANSLATE, SUMMARIZE, FILTER, TRANSCRIBE)
CREATE OR REPLACE VIEW CORTEX_OTHER_FUNCTIONS_VIEW AS
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.SENTIMENT%'
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.TRANSLATE%'
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.SUMMARIZE%'
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.FILTER%'
   OR QUERY_TEXT ILIKE '%SNOWFLAKE.CORTEX.TRANSCRIBE%';

-- ============================================================================
-- PART 2: TOKEN-LEVEL VIEW (Aggregated Token Metrics)
-- Source: SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
-- Use For: Token consumption, model efficiency, forecasting
-- Documentation: https://docs.snowflake.com/en/sql-reference/account-usage/cortex_functions_usage_history
-- ============================================================================

-- 5. Token Usage View (Aggregated by Hour + Function + Model)
CREATE OR REPLACE VIEW CORTEX_TOKEN_USAGE_VIEW AS
SELECT 
  *,
  -- Calculate average tokens per hour
  TOKENS / NULLIF(DATEDIFF('minute', START_TIME, END_TIME) / 60.0, 0) AS AVG_TOKENS_PER_HOUR,
  -- Calculate token efficiency (tokens per credit)
  TOKENS / NULLIF(TOKEN_CREDITS, 0) AS TOKENS_PER_CREDIT
FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
WHERE START_TIME >= DATEADD(DAY, -90, CURRENT_TIMESTAMP());  -- Last 90 days

-- ============================================================================
-- PART 3: UNIFIED CROSS-SERVICE VIEW (NEW!)
-- Purpose: Enable cross-service queries and comparisons
-- Use For: Total AI spend, service comparison, unified reporting
-- ============================================================================

-- 6. Unified View combining all Cortex AI services
CREATE OR REPLACE VIEW CORTEX_ALL_USAGE_VIEW AS
SELECT 
  *,
  'LLM' AS SERVICE_TYPE,
  CASE 
    WHEN QUERY_TEXT ILIKE '%mistral-large%' THEN 'mistral-large'
    WHEN QUERY_TEXT ILIKE '%llama3.1-70b%' THEN 'llama3.1-70b'
    WHEN QUERY_TEXT ILIKE '%llama3.1-405b%' THEN 'llama3.1-405b'
    WHEN QUERY_TEXT ILIKE '%llama3-70b%' THEN 'llama3-70b'
    WHEN QUERY_TEXT ILIKE '%llama3-8b%' THEN 'llama3-8b'
    WHEN QUERY_TEXT ILIKE '%mistral-7b%' THEN 'mistral-7b'
    WHEN QUERY_TEXT ILIKE '%mixtral-8x7b%' THEN 'mixtral-8x7b'
    WHEN QUERY_TEXT ILIKE '%reka-flash%' THEN 'reka-flash'
    WHEN QUERY_TEXT ILIKE '%reka-core%' THEN 'reka-core'
    WHEN QUERY_TEXT ILIKE '%gemma-7b%' THEN 'gemma-7b'
    WHEN QUERY_TEXT ILIKE '%jamba-instruct%' THEN 'jamba-instruct'
    WHEN QUERY_TEXT ILIKE '%snowflake-arctic%' THEN 'snowflake-arctic'
    ELSE 'custom-or-other'
  END AS MODEL_NAME,
  CASE
    WHEN QUERY_TEXT ILIKE '%mistral-large%' OR QUERY_TEXT ILIKE '%llama3.1-405b%' THEN 'Premium'
    WHEN QUERY_TEXT ILIKE '%llama3.1-70b%' OR QUERY_TEXT ILIKE '%llama3-70b%' OR QUERY_TEXT ILIKE '%reka-core%' THEN 'Standard'
    WHEN QUERY_TEXT ILIKE '%mistral-7b%' OR QUERY_TEXT ILIKE '%llama3-8b%' OR QUERY_TEXT ILIKE '%reka-flash%' THEN 'Economy'
    ELSE 'Custom'
  END AS MODEL_TIER,
  CASE
    WHEN QUERY_TEXT ILIKE '%mistral%' THEN 'Mistral'
    WHEN QUERY_TEXT ILIKE '%llama%' THEN 'LLaMA'
    WHEN QUERY_TEXT ILIKE '%reka%' THEN 'Reka'
    WHEN QUERY_TEXT ILIKE '%gemma%' THEN 'Gemma'
    WHEN QUERY_TEXT ILIKE '%jamba%' THEN 'Jamba'
    WHEN QUERY_TEXT ILIKE '%arctic%' THEN 'Arctic'
    ELSE 'Other'
  END AS MODEL_FAMILY,
  CASE
    WHEN QUERY_TEXT NOT ILIKE '%mistral-large%' 
     AND QUERY_TEXT NOT ILIKE '%llama3%'
     AND QUERY_TEXT NOT ILIKE '%mistral-7b%'
     AND QUERY_TEXT NOT ILIKE '%mixtral%'
     AND QUERY_TEXT NOT ILIKE '%reka%'
     AND QUERY_TEXT NOT ILIKE '%gemma%'
     AND QUERY_TEXT NOT ILIKE '%jamba%'
     AND QUERY_TEXT NOT ILIKE '%arctic%'
    THEN TRUE
    ELSE FALSE
  END AS IS_CUSTOM_MODEL
FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_LLM_USAGE_VIEW

UNION ALL

SELECT 
  *,
  'Embedding' AS SERVICE_TYPE,
  CASE
    WHEN QUERY_TEXT ILIKE '%snowflake-arctic-embed-m%' THEN 'snowflake-arctic-embed-m'
    WHEN QUERY_TEXT ILIKE '%snowflake-arctic-embed-l%' THEN 'snowflake-arctic-embed-l'
    WHEN QUERY_TEXT ILIKE '%e5-base-v2%' THEN 'e5-base-v2'
    WHEN QUERY_TEXT ILIKE '%multilingual-e5-large%' THEN 'multilingual-e5-large'
    ELSE 'custom-or-other'
  END AS MODEL_NAME,
  'Standard' AS MODEL_TIER,
  CASE
    WHEN QUERY_TEXT ILIKE '%arctic%' THEN 'Arctic'
    WHEN QUERY_TEXT ILIKE '%e5%' THEN 'E5'
    ELSE 'Other'
  END AS MODEL_FAMILY,
  CASE
    WHEN QUERY_TEXT NOT ILIKE '%arctic%' AND QUERY_TEXT NOT ILIKE '%e5%'
    THEN TRUE
    ELSE FALSE
  END AS IS_CUSTOM_MODEL
FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_EMBEDDING_USAGE_VIEW

UNION ALL

SELECT 
  *,
  'Search' AS SERVICE_TYPE,
  NULL AS MODEL_NAME,
  'Standard' AS MODEL_TIER,
  'Search' AS MODEL_FAMILY,
  FALSE AS IS_CUSTOM_MODEL
FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_SEARCH_USAGE_VIEW

UNION ALL

SELECT 
  *,
  'Other' AS SERVICE_TYPE,
  NULL AS MODEL_NAME,
  'Standard' AS MODEL_TIER,
  'Utility' AS MODEL_FAMILY,
  FALSE AS IS_CUSTOM_MODEL
FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_OTHER_FUNCTIONS_VIEW;

-- ============================================================================
-- VERIFICATION: Check that all views were created successfully
-- ============================================================================

SHOW VIEWS LIKE 'CORTEX_%';

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Validate Query-Level Views (should show data from recent activity)
SELECT 
  'CORTEX_LLM_USAGE_VIEW' AS view_name,
  COUNT(*) AS row_count,
  COUNT(DISTINCT USER_NAME) AS unique_users,
  MIN(START_TIME) AS oldest_data,
  MAX(START_TIME) AS newest_data,
  SUM(CREDITS_USED_CLOUD_SERVICES) AS total_credits
FROM CORTEX_LLM_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())

UNION ALL

SELECT 
  'CORTEX_EMBEDDING_USAGE_VIEW',
  COUNT(*),
  COUNT(DISTINCT USER_NAME),
  MIN(START_TIME),
  MAX(START_TIME),
  SUM(CREDITS_USED_CLOUD_SERVICES)
FROM CORTEX_EMBEDDING_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())

UNION ALL

SELECT 
  'CORTEX_SEARCH_USAGE_VIEW',
  COUNT(*),
  COUNT(DISTINCT USER_NAME),
  MIN(START_TIME),
  MAX(START_TIME),
  SUM(CREDITS_USED_CLOUD_SERVICES)
FROM CORTEX_SEARCH_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())

UNION ALL

SELECT 
  'CORTEX_OTHER_FUNCTIONS_VIEW',
  COUNT(*),
  COUNT(DISTINCT USER_NAME),
  MIN(START_TIME),
  MAX(START_TIME),
  SUM(CREDITS_USED_CLOUD_SERVICES)
FROM CORTEX_OTHER_FUNCTIONS_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP());

-- Validate Token-Level View
SELECT 
  'CORTEX_TOKEN_USAGE_VIEW' AS view_name,
  COUNT(*) AS row_count,
  SUM(TOKENS) AS total_tokens,
  SUM(TOKEN_CREDITS) AS total_token_credits,
  MIN(START_TIME) AS oldest_data,
  MAX(END_TIME) AS newest_data,
  COUNT(DISTINCT FUNCTION_NAME) AS unique_functions,
  COUNT(DISTINCT MODEL_NAME) AS unique_models
FROM CORTEX_TOKEN_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP());

-- ============================================================================
-- SAMPLE ANALYTICS QUERIES
-- ============================================================================

-- Query-Level: Usage by User (Last 7 Days)
SELECT 
  USER_NAME,
  COUNT(*) AS total_requests,
  SUM(CREDITS_USED_CLOUD_SERVICES) AS total_credits,
  ROUND(AVG(TOTAL_ELAPSED_TIME), 2) AS avg_latency_ms
FROM CORTEX_LLM_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
GROUP BY USER_NAME
ORDER BY total_credits DESC
LIMIT 10;

-- Query-Level: Usage by Warehouse (Last 7 Days)
SELECT 
  WAREHOUSE_NAME,
  COUNT(*) AS total_requests,
  SUM(CREDITS_USED_CLOUD_SERVICES) AS total_credits
FROM CORTEX_LLM_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_NAME
ORDER BY total_credits DESC;

-- Token-Level: Token Usage by Function (Last 7 Days)
SELECT 
  FUNCTION_NAME,
  COUNT(*) AS time_periods,
  SUM(TOKENS) AS total_tokens,
  SUM(TOKEN_CREDITS) AS total_credits,
  ROUND(AVG(TOKENS), 2) AS avg_tokens_per_period,
  ROUND(SUM(TOKENS) / NULLIF(SUM(TOKEN_CREDITS), 0), 2) AS tokens_per_credit
FROM CORTEX_TOKEN_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
GROUP BY FUNCTION_NAME
ORDER BY total_tokens DESC;

-- Token-Level: Token Usage by Model (Last 7 Days)
SELECT 
  FUNCTION_NAME,
  MODEL_NAME,
  SUM(TOKENS) AS total_tokens,
  SUM(TOKEN_CREDITS) AS total_credits,
  ROUND(AVG(TOKENS), 2) AS avg_tokens_per_period,
  ROUND(SUM(TOKENS) / NULLIF(SUM(TOKEN_CREDITS), 0), 2) AS tokens_per_credit
FROM CORTEX_TOKEN_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
  AND MODEL_NAME IS NOT NULL
GROUP BY FUNCTION_NAME, MODEL_NAME
ORDER BY total_tokens DESC;

-- Token-Level: Daily Token Trend (Last 30 Days)
SELECT 
  DATE_TRUNC('DAY', START_TIME) AS usage_date,
  FUNCTION_NAME,
  SUM(TOKENS) AS daily_tokens,
  SUM(TOKEN_CREDITS) AS daily_credits,
  COUNT(DISTINCT WAREHOUSE_ID) AS warehouses_used
FROM CORTEX_TOKEN_USAGE_VIEW
WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY usage_date DESC, daily_tokens DESC;

-- Combined Analysis: Credits vs Tokens (Last 7 Days)
-- Compare query-level credits with token-level credits
WITH query_credits AS (
  SELECT 
    'LLM' AS service,
    SUM(CREDITS_USED_CLOUD_SERVICES) AS query_based_credits
  FROM CORTEX_LLM_USAGE_VIEW
  WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
),
token_credits AS (
  SELECT 
    CASE 
      WHEN FUNCTION_NAME IN ('COMPLETE', 'CLASSIFY_TEXT', 'EXTRACT_ANSWER', 'PARSE_DOCUMENT') THEN 'LLM'
      WHEN FUNCTION_NAME = 'EMBED_TEXT' THEN 'Embedding'
      WHEN FUNCTION_NAME IN ('SENTIMENT', 'TRANSLATE', 'SUMMARIZE') THEN 'Other'
      ELSE 'Unknown'
    END AS service,
    SUM(TOKEN_CREDITS) AS token_based_credits,
    SUM(TOKENS) AS total_tokens
  FROM CORTEX_TOKEN_USAGE_VIEW
  WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
  GROUP BY 1
)
SELECT 
  COALESCE(q.service, t.service) AS service,
  q.query_based_credits,
  t.token_based_credits,
  t.total_tokens,
  ROUND(t.total_tokens / NULLIF(t.token_based_credits, 0), 2) AS tokens_per_credit
FROM query_credits q
FULL OUTER JOIN token_credits t ON q.service = t.service
ORDER BY service;

-- ============================================================================
-- SETUP COMPLETE!
-- ============================================================================
-- 
-- Next Steps:
-- 1. Upload Cortex_AI_usage_semantic_model.yaml to Snowflake
-- 2. Test queries via Cortex Analyst
-- 3. Build dashboards using these views
--
-- View Summary:
-- - Query-Level (4 views): Per-query detail with user attribution
--   * CORTEX_LLM_USAGE_VIEW, CORTEX_EMBEDDING_USAGE_VIEW
--   * CORTEX_SEARCH_USAGE_VIEW, CORTEX_OTHER_FUNCTIONS_VIEW
-- - Token-Level (1 view): Hourly aggregates with token counts
--   * CORTEX_TOKEN_USAGE_VIEW
-- - Unified (1 view): Cross-service with model classification ⭐ NEW
--   * CORTEX_ALL_USAGE_VIEW (SERVICE_TYPE, MODEL_TIER, MODEL_FAMILY, IS_CUSTOM_MODEL)
-- - Total: 6 views for comprehensive Cortex AI monitoring (100% functional!)
--
-- NEW in v1.4:
-- - CORTEX_ALL_USAGE_VIEW enables cross-service queries ("What's total AI spend?")
-- - Custom model tracking (IS_CUSTOM_MODEL dimension)
-- - Model tier comparisons (Premium, Standard, Economy, Custom)
-- - Model family analytics (Mistral, LLaMA, Reka, Arctic, etc.)
--
-- Documentation: Cortex_AI_Semantic_Model_Documentation.md
-- ============================================================================
