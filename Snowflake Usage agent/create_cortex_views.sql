-- ============================================================================
-- Cortex AI Cost Tracking & Usage Views  v2
-- ============================================================================
-- This script creates the infrastructure for comprehensive Cortex AI cost
-- tracking using 10 dedicated ACCOUNT_USAGE views (not QUERY_HISTORY text
-- matching). It creates:
--   1. Database, schema, and summary table
--   2. Summary view with backcharge JOIN
--   3. Stored procedure for data refresh (single-pass UNION ALL from 10 sources)
--   4. Scheduled task for daily refresh
--   5. A convenience view in PLATFORM_ANALYTICS for the semantic model
--
-- SOURCE VIEWS (10 ACCOUNT_USAGE views):
--   CORTEX_AISQL_USAGE_HISTORY          - LLM function token credits
--   CORTEX_ANALYST_USAGE_HISTORY        - Text-to-SQL inference credits
--   SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY - Intelligence / Agent API credits
--   CORTEX_AGENT_USAGE_HISTORY          - Dedicated Cortex Agent credits
--   CORTEX_SEARCH_DAILY_USAGE_HISTORY   - Search service daily credits
--   CORTEX_FINE_TUNING_USAGE_HISTORY    - Fine-tuning job credits
--   CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY - Document AI credits
--   CORTEX_REST_API_USAGE_HISTORY       - REST API inference (tokens, no credits)
--   CORTEX_CODE_CLI_USAGE_HISTORY       - Cortex Code CLI credits
--   CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY - PTU credits
--
-- PREREQUISITES:
-- - IMPORTED PRIVILEGES on the SNOWFLAKE database
-- - A warehouse for execution
-- ============================================================================

-- ============================================================
-- STEP 1: Configuration
-- ============================================================

SET CORTEX_DB = 'CORTEX_AI_USAGE';
SET CORTEX_SCHEMA = 'CORTEX_COST';
SET CORTEX_WH = 'DEFAULT_WH';
SET CORTEX_ROLE = 'SYSADMIN';

-- ============================================================
-- STEP 2: Grant Access to ACCOUNT_USAGE
-- ============================================================

USE ROLE ACCOUNTADMIN;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE IDENTIFIER($CORTEX_ROLE);

-- ============================================================
-- STEP 3: Create Database, Schema, Warehouse Context
-- ============================================================

USE ROLE IDENTIFIER($CORTEX_ROLE);
USE WAREHOUSE IDENTIFIER($CORTEX_WH);

CREATE DATABASE IF NOT EXISTS IDENTIFIER($CORTEX_DB);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($CORTEX_DB || '.' || $CORTEX_SCHEMA);

USE DATABASE IDENTIFIER($CORTEX_DB);
USE SCHEMA IDENTIFIER($CORTEX_SCHEMA);

-- ============================================================
-- STEP 4: Create Summary Table and Backcharge Mapping
-- ============================================================

CREATE TABLE IF NOT EXISTS CORTEX_AI_SUMMARY_COST (
    SERVICE_TYPE              VARCHAR,
    COST_COMPONENT            VARCHAR,
    COMPONENT_DESCRIPTION     VARCHAR,
    START_TIME                TIMESTAMP_LTZ,
    END_TIME                  TIMESTAMP_LTZ,
    QUERY_ID                  VARCHAR,
    END_USER_NAME             VARCHAR,
    END_USER_ROLE             VARCHAR,
    COMPONENT_OBJECT_NAME     VARCHAR,
    WAREHOUSE_NAME            VARCHAR,
    COMPONENT_CREDITS         FLOAT,
    INPUT_TOKENS              NUMBER DEFAULT 0,
    OUTPUT_TOKENS             NUMBER DEFAULT 0,
    TOTAL_TOKENS              NUMBER DEFAULT 0,
    BACKCHARGE_TEAM           VARCHAR,
    BACKCHARGE_BUSINESS_UNIT  VARCHAR,
    BACKCHARGE_DEPARTMENT     VARCHAR,
    BACKCHARGE_OWNER          VARCHAR,
    RECORD_KEY                VARCHAR(128)
);

ALTER TABLE CORTEX_AI_SUMMARY_COST ADD COLUMN IF NOT EXISTS INPUT_TOKENS NUMBER DEFAULT 0;
ALTER TABLE CORTEX_AI_SUMMARY_COST ADD COLUMN IF NOT EXISTS OUTPUT_TOKENS NUMBER DEFAULT 0;
ALTER TABLE CORTEX_AI_SUMMARY_COST ADD COLUMN IF NOT EXISTS TOTAL_TOKENS NUMBER DEFAULT 0;

CREATE TABLE IF NOT EXISTS USER_CUSTOM_BACKCHARGES_MAPPING (
    RECORD_KEY                VARCHAR,
    BACKCHARGE_TEAM           VARCHAR,
    BACKCHARGE_BUSINESS_UNIT  VARCHAR,
    BACKCHARGE_DEPARTMENT     VARCHAR,
    BACKCHARGE_OWNER          VARCHAR,
    CREATED_AT                TIMESTAMP_LTZ,
    UPDATED_AT                TIMESTAMP_LTZ
);

-- ============================================================
-- STEP 5: Create Summary View (with backcharge JOIN)
-- ============================================================

CREATE OR REPLACE VIEW CORTEX_AI_SUMMARY_COST_VIEW AS
SELECT
    s.SERVICE_TYPE,
    s.COST_COMPONENT,
    s.COMPONENT_DESCRIPTION,
    s.START_TIME,
    s.END_TIME,
    s.QUERY_ID,
    s.END_USER_NAME,
    s.END_USER_ROLE,
    s.COMPONENT_OBJECT_NAME,
    s.WAREHOUSE_NAME,
    s.COMPONENT_CREDITS,
    s.INPUT_TOKENS,
    s.OUTPUT_TOKENS,
    s.TOTAL_TOKENS,
    COALESCE(m.BACKCHARGE_TEAM, s.BACKCHARGE_TEAM)                   AS BACKCHARGE_TEAM,
    COALESCE(m.BACKCHARGE_BUSINESS_UNIT, s.BACKCHARGE_BUSINESS_UNIT) AS BACKCHARGE_BUSINESS_UNIT,
    COALESCE(m.BACKCHARGE_DEPARTMENT, s.BACKCHARGE_DEPARTMENT)       AS BACKCHARGE_DEPARTMENT,
    COALESCE(m.BACKCHARGE_OWNER, s.BACKCHARGE_OWNER)                 AS BACKCHARGE_OWNER,
    s.RECORD_KEY
FROM CORTEX_AI_SUMMARY_COST s
LEFT JOIN USER_CUSTOM_BACKCHARGES_MAPPING m
    ON s.RECORD_KEY = m.RECORD_KEY;

-- ============================================================
-- STEP 6: Create Stored Procedure - REFRESH_CORTEX_COST_DATA()
-- ============================================================
-- Architecture v2: Single-pass UNION ALL directly into summary table.
-- No staging tables. 10 source views consolidated in one procedure.
-- NOTE: Run this procedure using: snow sql -f create_cortex_views.sql
-- or paste into a Snowsight worksheet (the $$ delimiter is needed).

CREATE OR REPLACE PROCEDURE REFRESH_CORTEX_COST_DATA()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    TRUNCATE TABLE CORTEX_AI_SUMMARY_COST;

    INSERT INTO CORTEX_AI_SUMMARY_COST (
        SERVICE_TYPE, COST_COMPONENT, COMPONENT_DESCRIPTION,
        START_TIME, END_TIME, QUERY_ID,
        END_USER_NAME, END_USER_ROLE, COMPONENT_OBJECT_NAME,
        WAREHOUSE_NAME, COMPONENT_CREDITS,
        INPUT_TOKENS, OUTPUT_TOKENS, TOTAL_TOKENS,
        BACKCHARGE_TEAM, BACKCHARGE_BUSINESS_UNIT, BACKCHARGE_DEPARTMENT, BACKCHARGE_OWNER,
        RECORD_KEY
    )
    SELECT
        SERVICE_TYPE, COST_COMPONENT, COMPONENT_DESCRIPTION,
        START_TIME, END_TIME, QUERY_ID,
        END_USER_NAME, END_USER_ROLE, COMPONENT_OBJECT_NAME,
        WAREHOUSE_NAME, COMPONENT_CREDITS,
        INPUT_TOKENS, OUTPUT_TOKENS, TOTAL_TOKENS,
        NULL, NULL, NULL, NULL,
        SHA2(CONCAT(
            COALESCE(SERVICE_TYPE, ''), '|',
            COALESCE(COST_COMPONENT, ''), '|',
            COALESCE(START_TIME::VARCHAR, ''), '|',
            COALESCE(END_TIME::VARCHAR, ''), '|',
            COALESCE(QUERY_ID, ''), '|',
            COALESCE(END_USER_NAME, ''), '|',
            COALESCE(COMPONENT_OBJECT_NAME, ''), '|',
            COALESCE(COMPONENT_CREDITS::VARCHAR, '')
        ), 256) AS RECORD_KEY
    FROM (
        -- 1. CORTEX AISQL
        SELECT
            'CORTEX AISQL'                                              AS SERVICE_TYPE,
            'LLM Inference'                                             AS COST_COMPONENT,
            COALESCE(a.FUNCTION_NAME, '') || ' (' || COALESCE(a.MODEL_NAME, '') || ', '
                || COALESCE(a.TOKENS::VARCHAR, '0') || ' tokens)'      AS COMPONENT_DESCRIPTION,
            a.USAGE_TIME::TIMESTAMP_LTZ                                 AS START_TIME,
            a.USAGE_TIME::TIMESTAMP_LTZ                                 AS END_TIME,
            a.QUERY_ID,
            COALESCE(u.NAME, q.USER_NAME, 'USER_' || a.USER_ID::VARCHAR) AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            COALESCE(a.FUNCTION_NAME, a.MODEL_NAME)                     AS COMPONENT_OBJECT_NAME,
            COALESCE(q.WAREHOUSE_NAME, '')                              AS WAREHOUSE_NAME,
            a.TOKEN_CREDITS                                             AS COMPONENT_CREDITS,
            COALESCE(a.TOKENS_GRANULAR:input::NUMBER, 0) + COALESCE(a.TOKENS_GRANULAR:cache_read_input::NUMBER, 0) + COALESCE(a.TOKENS_GRANULAR:cache_write_input::NUMBER, 0) AS INPUT_TOKENS,
            COALESCE(a.TOKENS_GRANULAR:output::NUMBER, 0)               AS OUTPUT_TOKENS,
            COALESCE(a.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AISQL_USAGE_HISTORY a
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON a.USER_ID = u.USER_ID
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q ON a.QUERY_ID = q.QUERY_ID

        UNION ALL

        -- 2. CORTEX ANALYST
        SELECT
            'CORTEX ANALYST'                                            AS SERVICE_TYPE,
            'Text-to-SQL Inference'                                     AS COST_COMPONENT,
            'Analyst API inference (' || COALESCE(a.REQUEST_COUNT::VARCHAR, '0')
                || ' requests)'                                         AS COMPONENT_DESCRIPTION,
            a.START_TIME,
            a.END_TIME,
            ''                                                          AS QUERY_ID,
            a.USERNAME                                                  AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            'Cortex Analyst'                                            AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            a.CREDITS                                                   AS COMPONENT_CREDITS,
            0                                                           AS INPUT_TOKENS,
            0                                                           AS OUTPUT_TOKENS,
            0                                                           AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY a

        UNION ALL

        -- 3. CORTEX ANALYST (Intelligence / Agent API)
        SELECT
            'CORTEX ANALYST'                                            AS SERVICE_TYPE,
            CASE
                WHEN i.SNOWFLAKE_INTELLIGENCE_NAME IS NOT NULL AND i.SNOWFLAKE_INTELLIGENCE_NAME != ''
                THEN 'Snowflake Intelligence'
                ELSE 'Agent API Inference'
            END                                                         AS COST_COMPONENT,
            'Tokens processed via Intelligence/Agent API'               AS COMPONENT_DESCRIPTION,
            i.START_TIME,
            i.END_TIME,
            i.REQUEST_ID                                                AS QUERY_ID,
            i.USER_NAME                                                 AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            CASE
                WHEN i.AGENT_DATABASE_NAME IS NOT NULL AND i.AGENT_NAME IS NOT NULL AND i.AGENT_NAME != ''
                THEN i.AGENT_DATABASE_NAME || '.' || i.AGENT_SCHEMA_NAME || '.' || i.AGENT_NAME
                WHEN i.SNOWFLAKE_INTELLIGENCE_NAME IS NOT NULL AND i.SNOWFLAKE_INTELLIGENCE_NAME != ''
                THEN i.SNOWFLAKE_INTELLIGENCE_NAME
                ELSE 'Intelligence (unnamed)'
            END                                                         AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            i.TOKEN_CREDITS                                             AS COMPONENT_CREDITS,
            COALESCE(t.INPUT_TOKENS, 0)                                 AS INPUT_TOKENS,
            COALESCE(t.OUTPUT_TOKENS, 0)                                AS OUTPUT_TOKENS,
            COALESCE(i.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY i
        LEFT JOIN (
            SELECT i2.REQUEST_ID,
                SUM(COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"input":([0-9]+)', 1, 1, 'e'), '0')::NUMBER
                  + COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"cache_read_input":([0-9]+)', 1, 1, 'e'), '0')::NUMBER
                  + COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"cache_write_input":([0-9]+)', 1, 1, 'e'), '0')::NUMBER) AS INPUT_TOKENS,
                SUM(COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"output":([0-9]+)', 1, 1, 'e'), '0')::NUMBER) AS OUTPUT_TOKENS
            FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY i2,
                LATERAL FLATTEN(input => PARSE_JSON(i2.TOKENS_GRANULAR::VARCHAR)) f
            WHERE i2.TOKENS_GRANULAR IS NOT NULL
            GROUP BY i2.REQUEST_ID
        ) t ON i.REQUEST_ID = t.REQUEST_ID

        UNION ALL

        -- 4. CORTEX AGENT
        SELECT
            'CORTEX AGENT'                                              AS SERVICE_TYPE,
            'Agent Inference'                                           AS COST_COMPONENT,
            'Cortex Agent token processing'                             AS COMPONENT_DESCRIPTION,
            a.START_TIME::TIMESTAMP_LTZ                                 AS START_TIME,
            a.END_TIME::TIMESTAMP_LTZ                                   AS END_TIME,
            a.REQUEST_ID                                                AS QUERY_ID,
            COALESCE(a.USER_NAME, 'USER_' || a.USER_ID::VARCHAR)       AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            CASE
                WHEN a.AGENT_DATABASE_NAME IS NOT NULL AND a.AGENT_NAME IS NOT NULL AND a.AGENT_NAME != ''
                THEN a.AGENT_DATABASE_NAME || '.' || a.AGENT_SCHEMA_NAME || '.' || a.AGENT_NAME
                ELSE 'CORTEX AGENT (unnamed)'
            END                                                         AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            a.TOKEN_CREDITS                                             AS COMPONENT_CREDITS,
            COALESCE(t.INPUT_TOKENS, 0)                                 AS INPUT_TOKENS,
            COALESCE(t.OUTPUT_TOKENS, 0)                                AS OUTPUT_TOKENS,
            COALESCE(a.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY a
        LEFT JOIN (
            SELECT a2.REQUEST_ID,
                SUM(COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"input":([0-9]+)', 1, 1, 'e'), '0')::NUMBER
                  + COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"cache_read_input":([0-9]+)', 1, 1, 'e'), '0')::NUMBER
                  + COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"cache_write_input":([0-9]+)', 1, 1, 'e'), '0')::NUMBER) AS INPUT_TOKENS,
                SUM(COALESCE(REGEXP_SUBSTR(f.value::VARCHAR, '"output":([0-9]+)', 1, 1, 'e'), '0')::NUMBER) AS OUTPUT_TOKENS
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY a2,
                LATERAL FLATTEN(input => PARSE_JSON(a2.TOKENS_GRANULAR::VARCHAR)) f
            WHERE a2.TOKENS_GRANULAR IS NOT NULL
            GROUP BY a2.REQUEST_ID
        ) t ON a.REQUEST_ID = t.REQUEST_ID

        UNION ALL

        -- 5. CORTEX SEARCH
        SELECT
            'CORTEX SEARCH'                                             AS SERVICE_TYPE,
            COALESCE(s.CONSUMPTION_TYPE, 'Search') || ' Credits'        AS COST_COMPONENT,
            s.DATABASE_NAME || '.' || s.SCHEMA_NAME || '.' || s.SERVICE_NAME
                || ' (' || COALESCE(s.CONSUMPTION_TYPE, '') || ')'      AS COMPONENT_DESCRIPTION,
            s.USAGE_DATE::TIMESTAMP_LTZ                                 AS START_TIME,
            DATEADD('SECOND', -1, DATEADD('DAY', 1, s.USAGE_DATE))::TIMESTAMP_LTZ AS END_TIME,
            ''                                                          AS QUERY_ID,
            '(service - no user)'                                       AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            s.DATABASE_NAME || '.' || s.SCHEMA_NAME || '.' || s.SERVICE_NAME AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            s.CREDITS                                                   AS COMPONENT_CREDITS,
            0                                                           AS INPUT_TOKENS,
            0                                                           AS OUTPUT_TOKENS,
            COALESCE(s.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY s

        UNION ALL

        -- 6. FINE TUNING
        SELECT
            'FINE TUNING'                                               AS SERVICE_TYPE,
            'Fine-Tuning Job'                                           AS COST_COMPONENT,
            'Fine-tuning: ' || COALESCE(f.MODEL_NAME, 'unknown') || ' ('
                || COALESCE(f.TOKENS::VARCHAR, '0') || ' tokens)'      AS COMPONENT_DESCRIPTION,
            f.START_TIME,
            f.END_TIME,
            ''                                                          AS QUERY_ID,
            '(service - no user)'                                       AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            f.MODEL_NAME                                                AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            f.TOKEN_CREDITS                                             AS COMPONENT_CREDITS,
            0                                                           AS INPUT_TOKENS,
            0                                                           AS OUTPUT_TOKENS,
            COALESCE(f.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FINE_TUNING_USAGE_HISTORY f

        UNION ALL

        -- 7. DOCUMENT AI
        SELECT
            'DOCUMENT AI'                                               AS SERVICE_TYPE,
            'Document Processing'                                       AS COST_COMPONENT,
            COALESCE(d.OPERATION_NAME, '') || ': ' || COALESCE(d.MODEL_NAME, '')
                || ' (' || COALESCE(d.PAGE_COUNT::VARCHAR, '0') || ' pages, '
                || COALESCE(d.DOCUMENT_COUNT::VARCHAR, '0') || ' docs)' AS COMPONENT_DESCRIPTION,
            d.START_TIME,
            d.END_TIME,
            d.QUERY_ID,
            COALESCE(q.USER_NAME, '')                                   AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            COALESCE(d.FUNCTION_NAME, d.MODEL_NAME)                     AS COMPONENT_OBJECT_NAME,
            COALESCE(q.WAREHOUSE_NAME, '')                              AS WAREHOUSE_NAME,
            d.CREDITS_USED                                              AS COMPONENT_CREDITS,
            0                                                           AS INPUT_TOKENS,
            0                                                           AS OUTPUT_TOKENS,
            0                                                           AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY d
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY q ON d.QUERY_ID = q.QUERY_ID

        UNION ALL

        -- 8. CORTEX REST API (tokens only, no credits column)
        SELECT
            'CORTEX REST API'                                           AS SERVICE_TYPE,
            'REST API Inference'                                        AS COST_COMPONENT,
            'REST API: ' || COALESCE(r.MODEL_NAME, 'unknown') || ' ('
                || COALESCE(r.TOKENS::VARCHAR, '0') || ' tokens, '
                || COALESCE(r.INFERENCE_REGION, 'default') || ')'       AS COMPONENT_DESCRIPTION,
            r.START_TIME::TIMESTAMP_LTZ                                 AS START_TIME,
            r.END_TIME::TIMESTAMP_LTZ                                   AS END_TIME,
            r.REQUEST_ID                                                AS QUERY_ID,
            COALESCE(u.NAME, 'USER_' || r.USER_ID::VARCHAR)            AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            r.MODEL_NAME                                                AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            NULL                                                        AS COMPONENT_CREDITS,
            COALESCE(r.TOKENS_GRANULAR:input::NUMBER, 0) + COALESCE(r.TOKENS_GRANULAR:cache_read_input::NUMBER, 0) + COALESCE(r.TOKENS_GRANULAR:cache_write_input::NUMBER, 0) AS INPUT_TOKENS,
            COALESCE(r.TOKENS_GRANULAR:output::NUMBER, 0)               AS OUTPUT_TOKENS,
            COALESCE(r.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_REST_API_USAGE_HISTORY r
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON r.USER_ID = u.USER_ID

        UNION ALL

        -- 9. CORTEX CODE CLI
        SELECT
            'CORTEX CODE CLI'                                           AS SERVICE_TYPE,
            'Code CLI Inference'                                        AS COST_COMPONENT,
            'Cortex Code CLI token processing'                          AS COMPONENT_DESCRIPTION,
            c.USAGE_TIME::TIMESTAMP_LTZ                                 AS START_TIME,
            c.USAGE_TIME::TIMESTAMP_LTZ                                 AS END_TIME,
            c.REQUEST_ID                                                AS QUERY_ID,
            COALESCE(u.NAME, 'USER_' || c.USER_ID::VARCHAR)            AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            'Cortex Code CLI'                                           AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            c.TOKEN_CREDITS                                             AS COMPONENT_CREDITS,
            COALESCE(c.TOKENS_GRANULAR:input::NUMBER, 0) + COALESCE(c.TOKENS_GRANULAR:cache_read_input::NUMBER, 0) + COALESCE(c.TOKENS_GRANULAR:cache_write_input::NUMBER, 0) AS INPUT_TOKENS,
            COALESCE(c.TOKENS_GRANULAR:output::NUMBER, 0)               AS OUTPUT_TOKENS,
            COALESCE(c.TOKENS, 0)                                       AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_CODE_CLI_USAGE_HISTORY c
        LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.USERS u ON c.USER_ID = u.USER_ID

        UNION ALL

        -- 10. PROVISIONED THROUGHPUT
        SELECT
            'PROVISIONED THROUGHPUT'                                    AS SERVICE_TYPE,
            'PTU Credits'                                               AS COST_COMPONENT,
            'Provisioned throughput: ' || COALESCE(p.AI_SERVICE, '') || ' / '
                || COALESCE(p.MODEL_NAME, '') || ' ('
                || COALESCE(p.PTU_COUNT::VARCHAR, '0') || ' PTUs)'     AS COMPONENT_DESCRIPTION,
            p.INTERVAL_START_TIME::TIMESTAMP_LTZ                        AS START_TIME,
            p.INTERVAL_END_TIME::TIMESTAMP_LTZ                          AS END_TIME,
            p.PROVISIONED_THROUGHPUT_ID                                 AS QUERY_ID,
            '(service - no user)'                                       AS END_USER_NAME,
            ''                                                          AS END_USER_ROLE,
            COALESCE(p.MODEL_NAME, p.AI_SERVICE)                        AS COMPONENT_OBJECT_NAME,
            ''                                                          AS WAREHOUSE_NAME,
            p.PTU_CREDITS                                               AS COMPONENT_CREDITS,
            0                                                           AS INPUT_TOKENS,
            0                                                           AS OUTPUT_TOKENS,
            0                                                           AS TOTAL_TOKENS
        FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY p
    ) combined;

    RETURN 'SUCCESS: Cortex AI cost summary refreshed from 10 source views. Rows loaded: ' || (SELECT COUNT(*) FROM CORTEX_AI_SUMMARY_COST)::VARCHAR;
END;
$$;

-- ============================================================
-- STEP 7: Run Initial Data Load
-- ============================================================

CALL REFRESH_CORTEX_COST_DATA();

-- ============================================================
-- STEP 8: Create Scheduled Task (Daily at 6 AM Pacific)
-- ============================================================

CREATE OR REPLACE TASK REFRESH_COST_DATA_TASK
    WAREHOUSE = IDENTIFIER($CORTEX_WH)
    SCHEDULE = 'USING CRON 0 6 * * * America/Los_Angeles'
AS
    CALL REFRESH_CORTEX_COST_DATA();

ALTER TASK REFRESH_COST_DATA_TASK RESUME;

-- ============================================================
-- STEP 9: Create Convenience View in PLATFORM_ANALYTICS
-- ============================================================
-- This view allows the semantic model to reference PLATFORM_ANALYTICS.PUBLIC
-- while the actual data lives in CORTEX_AI_USAGE.CORTEX_COST.

USE DATABASE PLATFORM_ANALYTICS;
USE SCHEMA PUBLIC;

CREATE OR REPLACE VIEW CORTEX_AI_COST_VIEW AS
SELECT * FROM CORTEX_AI_USAGE.CORTEX_COST.CORTEX_AI_SUMMARY_COST_VIEW;

-- ============================================================
-- STEP 10: Verification
-- ============================================================

SELECT
    SERVICE_TYPE,
    COUNT(*) AS ROW_CNT,
    ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 4) AS TOTAL_CREDITS,
    SUM(INPUT_TOKENS)  AS TOTAL_INPUT_TOKENS,
    SUM(OUTPUT_TOKENS) AS TOTAL_OUTPUT_TOKENS,
    SUM(TOTAL_TOKENS)  AS TOTAL_ALL_TOKENS,
    COUNT(DISTINCT END_USER_NAME) AS UNIQUE_USERS
FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_AI_COST_VIEW
GROUP BY 1
ORDER BY 3 DESC;

SELECT COUNT(*) AS TOTAL_ROWS FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_AI_COST_VIEW;
