USE ROLE ACCOUNTADMIN;

-- 1. Create PLATFORM_ANALYTICS database (for semantic models and materialized tables)
CREATE DATABASE IF NOT EXISTS PLATFORM_ANALYTICS
  COMMENT = 'Database for platform-level analytics, governance models, and operational monitoring.';

-- 2. Create schema for semantic model YAML files
CREATE SCHEMA IF NOT EXISTS PLATFORM_ANALYTICS.SEMANTIC_MODELS
  COMMENT = 'Schema to store semantic model YAML specification files.';

-- 3. Create stage for YAML specification files
CREATE STAGE IF NOT EXISTS PLATFORM_ANALYTICS.SEMANTIC_MODELS.SEMANTIC_MODEL_SPECS
  DIRECTORY = ( ENABLE = true )
  COMMENT = 'Stage for storing semantic model YAML specification files.';

-- 4. Create CORTEX_AI_USAGE database (for Cortex AI cost tracking)
CREATE DATABASE IF NOT EXISTS CORTEX_AI_USAGE
  COMMENT = 'Database for Cortex AI cost tracking, usage monitoring, and backcharge allocation.';

-- 5. Create CORTEX_COST schema
CREATE SCHEMA IF NOT EXISTS CORTEX_AI_USAGE.CORTEX_COST
  COMMENT = 'Schema for Cortex AI summary cost tables, views, and refresh procedures.';

-- 6. Grant IMPORTED PRIVILEGES on SNOWFLAKE database for ACCOUNT_USAGE access
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE SYSADMIN;
