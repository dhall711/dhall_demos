# Snowflake Platform Health, Governance & AI Cost Agent

A comprehensive AI-powered analytics solution for Snowflake platform monitoring, cost optimization, Cortex AI spending analysis, and governance using Cortex Analyst and Cortex Search Service.

## Overview

This project provides production-ready semantic models that transform Snowflake's `ACCOUNT_USAGE` schema into an intelligent analytics platform. It combines:

- **Platform Health & Governance** - warehouse costs, query performance, user activity, security governance (12 core tables from ACCOUNT_USAGE)
- **Cortex AI Cost & Usage** - comprehensive tracking of all Cortex AI service costs using 10 dedicated ACCOUNT_USAGE views with token-level granularity
- **Semantic Search** - find specific queries by business context using Cortex Search Service

### Key Features

- **AI-Powered Analytics**: Natural language queries using Cortex Analyst
- **Cortex AI Cost Tracking**: Credits and token usage across 10 Cortex services (AISQL, Analyst, Agent, Search, Document AI, REST API, Code CLI, Fine Tuning, Provisioned Throughput)
- **Token Granularity**: Input, output, and total token tracking for LLM, Agent, Intelligence, REST API, and Code CLI services
- **Semantic Search**: Find specific queries by business context using Cortex Search Service
- **Cost Attribution**: Per-query compute costs via `QUERY_ATTRIBUTION_HISTORY` + Cortex AI costs via dedicated views
- **Performance Insights**: Query optimization recommendations and performance trending
- **Governance & Security**: User access patterns, role analysis, and compliance monitoring
- **Backcharge Support**: Optional cost allocation via `USER_CUSTOM_BACKCHARGES_MAPPING`

## Architecture

```
+-------------------------+    +---------------------------+    +---------------------+
|  ACCOUNT_USAGE          |    |  DATABASES                |    |  AI SERVICES        |
|                         |    |                           |    |                     |
|  QUERY_HISTORY          |--->|  PLATFORM_ANALYTICS       |--->|  Cortex Analyst     |
|  WAREHOUSE_*            |    |    Materialized Tables    |    |    Platform Health   |
|  USERS, ROLES           |    |    Search Service         |    |    AI Cost Model    |
|  DATABASES, etc.        |    |    CORTEX_AI_COST_VIEW    |    |  Cortex Search      |
|                         |    |                           |    |  Cortex Agent       |
|  10 CORTEX_* Views:     |--->|  CORTEX_AI_USAGE          |    |  Snowflake          |
|    AISQL, Analyst,      |    |    CORTEX_AI_SUMMARY_COST |    |    Intelligence     |
|    Agent, Search,       |    |    Summary Cost View      |    |                     |
|    Fine Tuning, etc.    |    |    Refresh Procedure      |    |                     |
+-------------------------+    +---------------------------+    +---------------------+
```

## Prerequisites

- Snowflake account with `ACCOUNTADMIN` privileges for setup
- Access to `SNOWFLAKE.ACCOUNT_USAGE` schema
- Warehouse for compute operations
- Cortex Analyst and Cortex Search Service enabled in your region

## Setup Guide

### Step 1: Create Database Infrastructure

Execute `Database_Context_Setup.sql`:
- Creates `PLATFORM_ANALYTICS` database (semantic models, materialized tables)
- Creates `CORTEX_AI_USAGE` database (AI cost tracking)
- Creates `CORTEX_COST` schema and semantic model stage
- Grants `IMPORTED PRIVILEGES` on SNOWFLAKE database

### Step 2: Deploy Cortex AI Cost Tracking

Execute `create_cortex_views.sql`:
- Creates the `CORTEX_AI_SUMMARY_COST` table and `CORTEX_AI_SUMMARY_COST_VIEW`
- Creates `USER_CUSTOM_BACKCHARGES_MAPPING` for cost allocation
- Creates `REFRESH_CORTEX_COST_DATA()` stored procedure (10-source UNION ALL)
- Runs initial data load from all 10 ACCOUNT_USAGE Cortex views
- Creates `REFRESH_COST_DATA_TASK` (daily at 6 AM Pacific)
- Creates `CORTEX_AI_COST_VIEW` in `PLATFORM_ANALYTICS.PUBLIC` for semantic model access

**10 Source ACCOUNT_USAGE Views:**

| # | Source View | SERVICE_TYPE | Token Detail |
|---|---|---|---|
| 1 | CORTEX_AISQL_USAGE_HISTORY | CORTEX AISQL | Input/Output/Total |
| 2 | CORTEX_ANALYST_USAGE_HISTORY | CORTEX ANALYST | None |
| 3 | SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY | CORTEX ANALYST | Input/Output/Total |
| 4 | CORTEX_AGENT_USAGE_HISTORY | CORTEX AGENT | Input/Output/Total |
| 5 | CORTEX_SEARCH_DAILY_USAGE_HISTORY | CORTEX SEARCH | Total only |
| 6 | CORTEX_FINE_TUNING_USAGE_HISTORY | FINE TUNING | Total only |
| 7 | CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY | DOCUMENT AI | None |
| 8 | CORTEX_REST_API_USAGE_HISTORY | CORTEX REST API | Input/Output/Total |
| 9 | CORTEX_CODE_CLI_USAGE_HISTORY | CORTEX CODE CLI | Input/Output/Total |
| 10 | CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY | PROVISIONED THROUGHPUT | None |

### Step 3: Materialize Query History Data

Run `materialize_query_history.sql`:
- Creates `QUERY_HISTORY_MATERIALIZED` table (60-day rolling window)
- Adds search-optimized fields (SEARCH_METADATA, QUERY_SUMMARY, categories)
- Creates indexes for performance

### Step 4: Set Up Automated Data Refresh

Execute `create_refresh_task.sql`:
- Creates `REFRESH_QUERY_HISTORY_PROC()` for incremental loading
- Creates `REFRESH_QUERY_HISTORY_TASK` (daily at 2 AM UTC)

### Step 5: Create the Search Service

Run `create_search_service.sql`:
- Creates `QUERY_HISTORY_SEARCH_SERVICE` Cortex Search Service
- 1-hour refresh interval
- Wait 10-15 minutes after creation for initial indexing

### Step 6: Deploy Semantic Models

Upload both YAML files to Snowflake:

1. **`Snowflake_usage_semantic_model.yaml`** - Platform Health & Governance (12 core tables)
2. **`Cortex_AI_usage_semantic_model.yaml`** - Cortex AI Cost & Usage (single unified cost table)

Upload via Snowsight:
1. Navigate to **Projects** > **Cortex Analyst**
2. Create/update semantic models with each YAML file
3. Validate and publish

### Step 7: Create the Cortex Agent

Build an integrated agent combining all capabilities:
1. Navigate to **Projects** > **Cortex Agents** in Snowsight
2. Create a new agent with these tools:
   - **Cortex Analyst #1**: Platform Health semantic model (Step 6, file 1)
   - **Cortex Analyst #2**: Cortex AI Cost semantic model (Step 6, file 2)
   - **Cortex Search Service**: `QUERY_HISTORY_SEARCH_SERVICE` (Step 5)
3. Configure agent instructions from `LLM_Instructions.md`
4. Test with sample questions

### Step 8: Deploy to Snowflake Intelligence

1. Navigate to **Snowflake Intelligence** in Snowsight
2. Add your Cortex Agent from Step 7
3. Configure user access permissions
4. End users can now ask questions about platform health AND Cortex AI costs

## Usage Examples

### Platform Health Queries
```
"Show me the top 10 most expensive queries by user"
"Which warehouses are consuming the most credits?"
"What are the peak usage hours for our warehouses?"
"Show me users who haven't logged in for 90 days"
```

### Cortex AI Cost Queries
```
"What is my total Cortex AI spend by service?"
"Show me daily AI cost trends for the last 30 days"
"Which users are consuming the most AI credits?"
"How many tokens are we using for LLM functions?"
"Show me Cortex Agent usage and costs"
"What are my Cortex Search costs?"
"Compare this week's AI costs to last week"
"Show me input vs output token breakdown by service"
```

### Semantic Search Queries
```
"Find queries related to ETL transformation pipeline"
"Search for expensive queries that spilled to disk"
"Find failed queries with error messages"
```

## Data Refresh

### Automated
- **Query History**: Daily at 2 AM UTC (60-day rolling window)
- **Cortex AI Costs**: Daily at 6 AM Pacific (full refresh from 10 source views)
- **Search Index**: Auto-refreshes every 1 hour

### Manual
```sql
-- Refresh query history
CALL PLATFORM_ANALYTICS.PUBLIC.REFRESH_QUERY_HISTORY_PROC();

-- Refresh Cortex AI costs
CALL CORTEX_AI_USAGE.CORTEX_COST.REFRESH_CORTEX_COST_DATA();

-- Refresh search index
ALTER CORTEX SEARCH SERVICE PLATFORM_ANALYTICS.PUBLIC.QUERY_HISTORY_SEARCH_SERVICE REFRESH;
```

### Verification
```sql
-- Cortex AI cost summary
SELECT SERVICE_TYPE, COUNT(*) AS EVENTS,
       ROUND(SUM(COALESCE(COMPONENT_CREDITS, 0)), 4) AS TOTAL_CREDITS,
       SUM(TOTAL_TOKENS) AS TOTAL_TOKENS
FROM PLATFORM_ANALYTICS.PUBLIC.CORTEX_AI_COST_VIEW
GROUP BY 1 ORDER BY 3 DESC;

-- Query history freshness
SELECT MAX(START_TIME) FROM PLATFORM_ANALYTICS.PUBLIC.QUERY_HISTORY_MATERIALIZED;

-- Search service status
SHOW CORTEX SEARCH SERVICES LIKE 'QUERY_HISTORY_SEARCH_SERVICE';
```

## Known Limitations

- ACCOUNT_USAGE has 45 minutes to 3 hours latency (not real-time)
- QUERY_ATTRIBUTION_HISTORY available from mid-August 2024 with 8-hour latency
- CORTEX REST API has tokens but NO credits column (COMPONENT_CREDITS is NULL)
- Search, Fine Tuning, and Provisioned Throughput have no user attribution
- Backcharge fields are NULL by default; populate `USER_CUSTOM_BACKCHARGES_MAPPING` for cost allocation
- Materialized query history limited to 60 days

## File Reference

| File | Purpose |
|---|---|
| `Database_Context_Setup.sql` | Creates databases, schemas, stage |
| `create_cortex_views.sql` | Cortex AI cost tracking: table, view, stored proc, task, convenience view |
| `materialize_query_history.sql` | Materializes 60 days of QUERY_HISTORY for search |
| `create_refresh_task.sql` | Daily refresh task for materialized query history |
| `create_search_service.sql` | Cortex Search Service on query history |
| `Snowflake_usage_semantic_model.yaml` | Semantic model: Platform Health & Governance (12 tables) |
| `Cortex_AI_usage_semantic_model.yaml` | Semantic model: Cortex AI Cost & Usage (1 unified table) |
| `LLM_Instructions.md` | Agent/Analyst instructions, SQL guidance, response rules |
