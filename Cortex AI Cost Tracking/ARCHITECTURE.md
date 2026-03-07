# Cortex AI Cost Tracking & Backcharge Solution - Architecture Document v2.1

## Table of Contents

1. [Solution Overview](#1-solution-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Source Views - SNOWFLAKE.ACCOUNT_USAGE](#3-source-views---snowflakeaccount_usage)
4. [Target Schema - Tables and View](#4-target-schema---tables-and-view)
5. [Stored Procedure - REFRESH_CORTEX_COST_DATA()](#5-stored-procedure---refresh_cortex_cost_data)
6. [Task Scheduling](#6-task-scheduling)
7. [Dashboard Architecture](#7-dashboard-architecture)
8. [Security Model](#8-security-model)
9. [Data Freshness and Latency](#9-data-freshness-and-latency)
10. [Object Inventory](#10-object-inventory)

---

## 1. Solution Overview

This solution provides centralized tracking, visualization, and backcharge allocation of Snowflake Cortex AI credit and token consumption across ALL Cortex services. It consolidates usage data from 10 SNOWFLAKE.ACCOUNT_USAGE views into a single normalized summary table, calculates estimated costs, tracks input/output token usage, and presents the data through interactive dashboards.

### Capabilities

| Capability | Description |
|---|---|
| Complete Cortex coverage | Tracks all 10 active Cortex AI ACCOUNT_USAGE views including Agents, REST API, Code CLI, and Provisioned Throughput |
| Unified credit model | All services normalized to a common schema with COMPONENT_CREDITS as the standard unit |
| Token tracking | INPUT_TOKENS, OUTPUT_TOKENS, and TOTAL_TOKENS tracked per row with service-specific extraction logic |
| Single-pass architecture | No staging tables -- stored procedure builds summary directly from source views via UNION ALL |
| Backcharge mapping | USER_CUSTOM_BACKCHARGES_MAPPING table for cost center / department allocation |
| Deterministic keys | SHA2-based RECORD_KEY survives table refreshes, enabling stable backcharge joins |
| Interactive dashboard | React (SPCS) with full filtering, time granularity, credit/cost toggle, and token visualization |
| Snowsight tiles | SQL queries for native Snowsight dashboard tiles |
| Configurable cost rate | Client-side $/credit rate (default $3.00/credit) |
| Automated refresh | Snowflake Task with CRON scheduling (default daily at 6 AM Pacific) |

### Technology Stack

| Layer | Technology |
|---|---|
| Data source | SNOWFLAKE.ACCOUNT_USAGE (10 views) |
| Data storage | Single summary table + read-through view |
| Refresh logic | SQL stored procedure (EXECUTE AS CALLER) |
| Scheduling | Snowflake Task (CRON) |
| Dashboard (Snowsight) | Native Snowsight SQL tiles |
| Dashboard (SPCS) | Next.js + React + shadcn/ui + Recharts |
| Container | Docker multi-stage (Node 20 Alpine), standalone output |
| Hosting | Snowpark Container Services (SPCS) |
| Authentication | SPCS OAuth token (auto-injected) / External Browser SSO (local) |

---

## 2. High-Level Architecture

### Data Flow

The solution follows a streamlined two-tier data flow: source and presentation.

**Tier 1: Source + Processing (SNOWFLAKE.ACCOUNT_USAGE --> Summary Table)**

Ten ACCOUNT_USAGE views provide raw Cortex AI consumption data. The stored procedure reads all 10 in a single UNION ALL and writes directly to the summary table. No intermediate staging tables.

| # | Source View | SERVICE_TYPE | Credits Column | Token Extraction |
|---|---|---|---|---|
| 1 | CORTEX_AISQL_USAGE_HISTORY | CORTEX AISQL | TOKEN_CREDITS | Flat TOKENS_GRANULAR JSON |
| 2 | CORTEX_ANALYST_USAGE_HISTORY | CORTEX ANALYST | CREDITS | None (0s) |
| 3 | SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY | CORTEX ANALYST | TOKEN_CREDITS | LATERAL FLATTEN on nested array |
| 4 | CORTEX_AGENT_USAGE_HISTORY | CORTEX AGENT | TOKEN_CREDITS | LATERAL FLATTEN on nested array |
| 5 | CORTEX_SEARCH_DAILY_USAGE_HISTORY | CORTEX SEARCH | CREDITS | Total only (TOKENS column) |
| 6 | CORTEX_FINE_TUNING_USAGE_HISTORY | FINE TUNING | TOKEN_CREDITS | Total only (TOKENS column) |
| 7 | CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY | DOCUMENT AI | CREDITS_USED | None (0s) |
| 8 | CORTEX_REST_API_USAGE_HISTORY | CORTEX REST API | (tokens only) | Flat TOKENS_GRANULAR JSON |
| 9 | CORTEX_CODE_CLI_USAGE_HISTORY | CORTEX CODE CLI | TOKEN_CREDITS | Flat TOKENS_GRANULAR JSON |
| 10 | CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY | PROVISIONED THROUGHPUT | PTU_CREDITS | None (0s) |

**Tier 2: Presentation (Dashboard)**

All dashboards query the CORTEX_AI_SUMMARY_COST_VIEW (which reads from the summary table with LEFT JOIN to backcharge mappings).

### Component Interaction

```
ACCOUNT_USAGE views (10)
        |
        | (Single-pass UNION ALL with transforms + token extraction)
        v
Stored Procedure: REFRESH_CORTEX_COST_DATA()
        |
        | (TRUNCATE + INSERT)
        v
CORTEX_AI_SUMMARY_COST (summary table with credit + token columns)
        |
        | (LEFT JOIN to backcharge mapping)
        v
CORTEX_AI_SUMMARY_COST_VIEW
        |
        +---> React Dashboard (SPCS / local)
        +---> Snowsight SQL Tiles
```

### Views NOT Included (and Why)

| View | Reason Excluded |
|---|---|
| CORTEX_AI_FUNCTIONS_USAGE_HISTORY | Subset of CORTEX_AISQL_USAGE_HISTORY. AISQL is more comprehensive. |
| CORTEX_FUNCTIONS_USAGE_HISTORY | Legacy view (Oct 2024), superseded by CORTEX_AISQL_USAGE_HISTORY |
| CORTEX_FUNCTIONS_QUERY_USAGE_HISTORY | Legacy view (Nov 2024), per-query granularity superseded by CORTEX_AISQL |
| CORTEX_SEARCH_SERVING_USAGE_HISTORY | Hourly granularity of same data in CORTEX_SEARCH_DAILY. Daily is sufficient for cost tracking. |

---

## 3. Source Views - SNOWFLAKE.ACCOUNT_USAGE

All source views reside in the shared SNOWFLAKE database under the ACCOUNT_USAGE schema. Access requires IMPORTED PRIVILEGES on the SNOWFLAKE database.

### 3.1 CORTEX_AISQL_USAGE_HISTORY

Tracks per-query LLM token credit consumption for Cortex AISQL functions (COMPLETE, EXTRACT_ANSWER, SENTIMENT, SUMMARIZE, TRANSLATE, EMBED_TEXT, etc.).

| Column | Type | Used |
|---|---|---|
| USAGE_TIME | TIMESTAMP_LTZ | --> START_TIME, END_TIME |
| FUNCTION_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| MODEL_NAME | VARCHAR | --> COMPONENT_DESCRIPTION, fallback COMPONENT_OBJECT_NAME |
| TOKEN_CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| TOKENS | NUMBER | --> TOTAL_TOKENS |
| TOKENS_GRANULAR | VARIANT | --> INPUT_TOKENS, OUTPUT_TOKENS (flat JSON) |
| QUERY_ID | VARCHAR | --> QUERY_ID |
| USER_ID | NUMBER | --> END_USER_NAME (resolved via USERS view) |

### 3.2 CORTEX_ANALYST_USAGE_HISTORY

Tracks Cortex Analyst (text-to-SQL) inference credit consumption at an aggregated level.

| Column | Type | Used |
|---|---|---|
| START_TIME | TIMESTAMP_LTZ | --> START_TIME |
| END_TIME | TIMESTAMP_LTZ | --> END_TIME |
| USERNAME | VARCHAR | --> END_USER_NAME |
| CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| REQUEST_COUNT | NUMBER | --> COMPONENT_DESCRIPTION |

### 3.3 SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY

Tracks Intelligence and Agent API usage. ZERO REQUEST_ID overlap with CORTEX_AGENT_USAGE_HISTORY (completely separate data).

| Column | Type | Used |
|---|---|---|
| START_TIME | TIMESTAMP_LTZ | --> START_TIME |
| END_TIME | TIMESTAMP_LTZ | --> END_TIME |
| USER_NAME | VARCHAR | --> END_USER_NAME |
| REQUEST_ID | VARCHAR | --> QUERY_ID |
| SNOWFLAKE_INTELLIGENCE_NAME | VARCHAR | --> COST_COMPONENT classification |
| AGENT_DATABASE_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| AGENT_SCHEMA_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| AGENT_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| TOKEN_CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| TOKENS | NUMBER | --> TOTAL_TOKENS |
| TOKENS_GRANULAR | VARIANT | --> INPUT_TOKENS, OUTPUT_TOKENS (nested array, LATERAL FLATTEN) |

### 3.4 CORTEX_AGENT_USAGE_HISTORY

Dedicated Cortex Agent per-request tracking. 19 columns including agent identity, tokens, and metadata.

| Column | Type | Used |
|---|---|---|
| START_TIME | TIMESTAMP_LTZ(6) | --> START_TIME |
| END_TIME | TIMESTAMP_LTZ(6) | --> END_TIME |
| USER_ID | NUMBER | (fallback for END_USER_NAME) |
| USER_NAME | VARCHAR | --> END_USER_NAME |
| REQUEST_ID | VARCHAR | --> QUERY_ID |
| AGENT_DATABASE_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| AGENT_SCHEMA_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| AGENT_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| TOKEN_CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| TOKENS | NUMBER | --> TOTAL_TOKENS |
| TOKENS_GRANULAR | VARIANT | --> INPUT_TOKENS, OUTPUT_TOKENS (nested array, LATERAL FLATTEN) |

### 3.5 CORTEX_SEARCH_DAILY_USAGE_HISTORY

Tracks daily credit consumption for Cortex Search services.

| Column | Type | Used |
|---|---|---|
| USAGE_DATE | TIMESTAMP_LTZ | --> START_TIME (+ 1 day - 1 second for END_TIME) |
| DATABASE_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME, COMPONENT_DESCRIPTION |
| SCHEMA_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME, COMPONENT_DESCRIPTION |
| SERVICE_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME, COMPONENT_DESCRIPTION |
| CONSUMPTION_TYPE | VARCHAR | --> COST_COMPONENT |
| CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| TOKENS | NUMBER | --> TOTAL_TOKENS |

### 3.6 CORTEX_FINE_TUNING_USAGE_HISTORY

Tracks credit consumption for Cortex Fine-Tuning jobs.

| Column | Type | Used |
|---|---|---|
| START_TIME | TIMESTAMP_LTZ | --> START_TIME |
| END_TIME | TIMESTAMP_LTZ | --> END_TIME |
| MODEL_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME, COMPONENT_DESCRIPTION |
| TOKEN_CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| TOKENS | NUMBER | --> TOTAL_TOKENS |

### 3.7 CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY

Tracks credit consumption for Document AI.

| Column | Type | Used |
|---|---|---|
| START_TIME | TIMESTAMP_LTZ | --> START_TIME |
| END_TIME | TIMESTAMP_LTZ | --> END_TIME |
| QUERY_ID | VARCHAR | --> QUERY_ID |
| CREDITS_USED | FLOAT | --> COMPONENT_CREDITS |
| FUNCTION_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME |
| MODEL_NAME | VARCHAR | --> COMPONENT_DESCRIPTION, fallback COMPONENT_OBJECT_NAME |
| OPERATION_NAME | VARCHAR | --> COMPONENT_DESCRIPTION |
| PAGE_COUNT | NUMBER | --> COMPONENT_DESCRIPTION |
| DOCUMENT_COUNT | NUMBER | --> COMPONENT_DESCRIPTION |

### 3.8 CORTEX_REST_API_USAGE_HISTORY

Tracks REST API inference calls. NOTE: This view has TOKENS but NO credits column. Rows are tracked for visibility but COMPONENT_CREDITS will be NULL.

| Column | Type | Used |
|---|---|---|
| START_TIME | TIMESTAMP_TZ | --> START_TIME (cast to LTZ) |
| END_TIME | TIMESTAMP_TZ | --> END_TIME (cast to LTZ) |
| REQUEST_ID | VARCHAR | --> QUERY_ID |
| MODEL_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME, COMPONENT_DESCRIPTION |
| TOKENS | NUMBER | --> TOTAL_TOKENS |
| TOKENS_GRANULAR | VARIANT | --> INPUT_TOKENS, OUTPUT_TOKENS (flat JSON) |
| USER_ID | NUMBER | --> END_USER_NAME (resolved via USERS view) |
| INFERENCE_REGION | VARCHAR | --> COMPONENT_DESCRIPTION |

### 3.9 CORTEX_CODE_CLI_USAGE_HISTORY

Tracks Cortex Code CLI (IDE assistant) usage.

| Column | Type | Used |
|---|---|---|
| USAGE_TIME | TIMESTAMP_TZ | --> START_TIME, END_TIME (cast to LTZ) |
| REQUEST_ID | VARCHAR | --> QUERY_ID |
| USER_ID | NUMBER | --> END_USER_NAME (resolved via USERS view) |
| TOKEN_CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |
| TOKENS | NUMBER | --> TOTAL_TOKENS |
| TOKENS_GRANULAR | VARIANT | --> INPUT_TOKENS, OUTPUT_TOKENS (flat JSON) |

### 3.10 CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY

Tracks Provisioned Throughput Unit (PTU) consumption for dedicated capacity contracts.

| Column | Type | Used |
|---|---|---|
| INTERVAL_START_TIME | TIMESTAMP_TZ | --> START_TIME (cast to LTZ) |
| INTERVAL_END_TIME | TIMESTAMP_TZ | --> END_TIME (cast to LTZ) |
| PROVISIONED_THROUGHPUT_ID | VARCHAR | --> QUERY_ID |
| AI_SERVICE | VARCHAR | --> COMPONENT_DESCRIPTION, fallback COMPONENT_OBJECT_NAME |
| MODEL_NAME | VARCHAR | --> COMPONENT_OBJECT_NAME, COMPONENT_DESCRIPTION |
| PTU_COUNT | NUMBER | --> COMPONENT_DESCRIPTION |
| PTU_CREDITS | NUMBER(38,9) | --> COMPONENT_CREDITS |

---

## 4. Target Schema - Tables and View

All target objects are created in a configurable database and schema (set via session variables in setup.sql).

### 4.1 Common Column Schema

The summary table uses a normalized column structure:

| Column | Type | Description |
|---|---|---|
| SERVICE_TYPE | VARCHAR | Service category (CORTEX AISQL, CORTEX ANALYST, CORTEX AGENT, CORTEX SEARCH, FINE TUNING, DOCUMENT AI, CORTEX REST API, CORTEX CODE CLI, PROVISIONED THROUGHPUT) |
| COST_COMPONENT | VARCHAR | Specific cost category within the service |
| COMPONENT_DESCRIPTION | VARCHAR | Human-readable description |
| START_TIME | TIMESTAMP_LTZ | Event start timestamp (normalized) |
| END_TIME | TIMESTAMP_LTZ | Event end timestamp (normalized) |
| QUERY_ID | VARCHAR | Query ID, Request ID, or identifier |
| END_USER_NAME | VARCHAR | User responsible for the usage |
| END_USER_ROLE | VARCHAR | Role used (where available) |
| COMPONENT_OBJECT_NAME | VARCHAR | Object associated (model, service, function, agent FQN) |
| WAREHOUSE_NAME | VARCHAR | Warehouse used (empty for serverless) |
| COMPONENT_CREDITS | FLOAT | Credit amount (NULL for REST API which lacks credits) |
| INPUT_TOKENS | NUMBER | Input tokens consumed (includes cache_read and cache_write) |
| OUTPUT_TOKENS | NUMBER | Output tokens generated |
| TOTAL_TOKENS | NUMBER | Total tokens (from source TOKENS column where available) |
| BACKCHARGE_TEAM | VARCHAR | Backcharge team (populated by mapping) |
| BACKCHARGE_BUSINESS_UNIT | VARCHAR | Backcharge business unit |
| BACKCHARGE_DEPARTMENT | VARCHAR | Backcharge department |
| BACKCHARGE_OWNER | VARCHAR | Backcharge owner |
| RECORD_KEY | VARCHAR(128) | SHA2 deterministic hash key |

### 4.2 Token Extraction Logic

Two distinct TOKENS_GRANULAR JSON structures exist across ACCOUNT_USAGE views:

**Flat JSON** (AISQL, REST API, Code CLI):
```json
{"input": 150, "output": 50, "cache_read_input": 10, "cache_write_input": 5}
```
Extraction: Direct semi-structured notation (e.g., `TOKENS_GRANULAR:input::NUMBER`)

**Nested Array JSON** (Agent, Intelligence):
```json
[{"uuid": {"service": {"model": {"input": 150, "output": 50, "cache_read_input": 10}, "start_time": "..."}}}]
```
Extraction: `LATERAL FLATTEN` on the parsed array + `REGEXP_SUBSTR` per element to extract token counts, then `SUM` grouped by `REQUEST_ID`.

**Token formula:**
- `INPUT_TOKENS = input + cache_read_input + cache_write_input`
- `OUTPUT_TOKENS = output`
- `TOTAL_TOKENS = TOKENS column` (from source view, where available)

### 4.3 RECORD_KEY Design

Each row gets a deterministic RECORD_KEY via SHA2 of concatenated fields:

```
SHA2(SERVICE_TYPE|COST_COMPONENT|START_TIME|END_TIME|QUERY_ID|END_USER_NAME|COMPONENT_OBJECT_NAME|COMPONENT_CREDITS, 256)
```

This ensures: same source record always produces the same key, keys survive truncate-and-reload cycles, and USER_CUSTOM_BACKCHARGES_MAPPING joins persist across refreshes.

### 4.4 Summary View: CORTEX_AI_SUMMARY_COST_VIEW

A read-through view over CORTEX_AI_SUMMARY_COST with LEFT JOIN to USER_CUSTOM_BACKCHARGES_MAPPING. COALESCE logic prefers custom backcharge values over any defaults. Exposes all columns including INPUT_TOKENS, OUTPUT_TOKENS, and TOTAL_TOKENS.

### 4.5 Backcharge Mapping Table: USER_CUSTOM_BACKCHARGES_MAPPING

Empty table for customers to populate with cost center / department allocations. Joins via RECORD_KEY.

---

## 5. Stored Procedure - REFRESH_CORTEX_COST_DATA()

### 5.1 Execution Model

- **Language:** SQL
- **Privileges:** EXECUTE AS CALLER
- **Requirement:** Caller must have IMPORTED PRIVILEGES on the SNOWFLAKE database
- **Architecture:** Single-pass UNION ALL (no staging tables)

### 5.2 Refresh Sequence

| Step | Action |
|---|---|
| 1 | TRUNCATE CORTEX_AI_SUMMARY_COST |
| 2 | INSERT via UNION ALL of 10 source view transforms with SHA2 RECORD_KEY generation and token extraction |
| 3 | RETURN success message with row count |

### 5.3 User Name Resolution

Views that only provide USER_ID (CORTEX_AISQL, CORTEX_REST_API, CORTEX_CODE_CLI) resolve usernames via LEFT JOIN to SNOWFLAKE.ACCOUNT_USAGE.USERS. Fallback: 'USER_' || USER_ID.

### 5.4 Warehouse Name Resolution

CORTEX_AISQL_USAGE_HISTORY and CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY resolve warehouse names via LEFT JOIN to SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY on QUERY_ID.

### 5.5 Design Rationale

**Why single-pass instead of staging tables?**
- Eliminates intermediate tables and their DDL
- Reduces procedure from multiple steps to 1 INSERT
- Same performance (single warehouse scan)
- Simpler maintenance and customer deployment

**Why truncate + reload instead of incremental merge?**
- ACCOUNT_USAGE data can be retroactively updated by Snowflake
- Full reload eliminates change detection complexity
- Current data volumes (typically < 50K rows) complete in seconds
- SHA2 RECORD_KEY ensures backcharge mappings survive the reload

---

## 6. Task Scheduling

### REFRESH_COST_DATA_TASK

| Property | Value |
|---|---|
| Schedule | CRON: 0 6 * * * America/Los_Angeles (daily at 6:00 AM Pacific) |
| Warehouse | Configurable via session variable |
| Action | CALL REFRESH_CORTEX_COST_DATA() |

### Customization

- Modify the CRON expression for different frequency (e.g., 0 */4 * * * for every 4 hours)
- Manual trigger: EXECUTE TASK REFRESH_COST_DATA_TASK
- Monitor: SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY()) WHERE NAME = 'REFRESH_COST_DATA_TASK' ORDER BY SCHEDULED_TIME DESC

---

## 7. Dashboard Architecture

### 7.1 React App (SPCS)

The React dashboard (cortex-cost-dashboard/) provides a full interactive experience:

| Feature | Implementation |
|---|---|
| Multi-select filters | Service Type, User, Warehouse, Component, Cortex Agent |
| Date range picker | From/to date inputs |
| Time granularity toggle | Daily, Weekly, Monthly, Yearly |
| Credits/Cost toggle | Switch between raw credits and estimated cost |
| Configurable $/credit | Input field (default $3.00) |
| Token visualization | Stacked bar chart (input vs output by service), token KPI card |
| Server-side aggregation | Pre-aggregated trend queries for all 4 time granularities |
| Client-side filtering | Re-aggregates from detail rows when filters active |

### 7.2 API Route (route.ts)

The /api/cost-data route fires 13 parallel SQL queries against CORTEX_AI_SUMMARY_COST_VIEW:

| Query | Purpose |
|---|---|
| Monthly trend | Credits over time (DATE_TRUNC MONTH) with cumulative |
| Daily trend | Credits over time (DATE_TRUNC DAY) with cumulative |
| Weekly trend | Credits over time (DATE_TRUNC WEEK) with cumulative |
| Yearly trend | Credits over time (DATE_TRUNC YEAR) with cumulative |
| By service type | Credits by SERVICE_TYPE |
| By cost component | Credits by COST_COMPONENT |
| Top 10 users | Highest credit consumers |
| Top 10 warehouses | Highest warehouse usage (excluding NULL/empty/N/A) |
| Top 10 objects | Highest objects by credits |
| By Cortex Agent | Agent-specific credits (SERVICE_TYPE = 'CORTEX AGENT') |
| Detail rows | Most recent 200 records (with token columns) |
| Totals | Summary KPI metrics (credits, users, queries, service types, tokens) |
| Tokens by service | Input/output/total tokens grouped by SERVICE_TYPE |

### 7.3 Snowsight SQL Tiles

The `snowsight_dashboard_queries.sql` file contains 10 standalone SQL queries for native Snowsight dashboards with date range filter support (`:date_start`, `:date_end`).

### 7.4 SPCS Service Configuration

```yaml
spec:
  containers:
  - name: dashboard
    image: /<database>/<schema>/dashboard_repo/cortex-cost-dashboard:latest
    env:
      NODE_ENV: production
      HOSTNAME: "0.0.0.0"
      PORT: "3000"
      SNOWFLAKE_WAREHOUSE: <your_warehouse>
      SNOWFLAKE_DATABASE: <your_database>
      SNOWFLAKE_SCHEMA: <your_schema>
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1000m
    readinessProbe:
      port: 3000
      path: /
  endpoints:
  - name: dashboard
    port: 3000
    public: true
```

IMPORTANT: Do NOT set SNOWFLAKE_HOST or SNOWFLAKE_ACCOUNT in the SPCS service spec. These are auto-injected by the container runtime.

---

## 8. Security Model

### Access Requirements

| Requirement | Scope |
|---|---|
| IMPORTED PRIVILEGES on SNOWFLAKE database | Required for stored procedure to read ACCOUNT_USAGE views |
| USAGE on warehouse | Required for procedure execution and dashboard queries |
| SELECT on target tables/view | Required for dashboards to query CORTEX_AI_SUMMARY_COST_VIEW |
| SPCS BIND SERVICE ENDPOINT | Required to expose React dashboard publicly |

### Authentication

| Mode | Mechanism |
|---|---|
| SPCS (production) | OAuth token at /snowflake/session/token (auto-injected) |
| Local (development) | External Browser SSO |

---

## 9. Data Freshness and Latency

| Stage | Latency |
|---|---|
| Cortex AI usage event occurs | 0 min |
| ACCOUNT_USAGE views reflect the event | Up to 45 min |
| Stored procedure runs (scheduled) | Default: daily at 6 AM PT |
| Dashboard queries the summary view | Real-time after refresh |

Worst-case freshness with daily scheduling: up to 24 hours + 45 minutes.

---

## 10. Object Inventory

### Snowflake Objects Created by setup.sql

| Object Type | Name | Purpose |
|---|---|---|
| Database | Configurable (default: CORTEX_AI_USAGE) | Container database |
| Schema | Configurable (default: CORTEX_COST) | Container schema |
| Table | CORTEX_AI_SUMMARY_COST | Single summary table (all services, credits + tokens) |
| Table | USER_CUSTOM_BACKCHARGES_MAPPING | Backcharge allocation (user-populated) |
| View | CORTEX_AI_SUMMARY_COST_VIEW | Read-through with backcharge JOIN + token columns |
| Procedure | REFRESH_CORTEX_COST_DATA() | Single-pass refresh from 10 source views |
| Task | REFRESH_COST_DATA_TASK | CRON-scheduled procedure execution |
| Image Repository | DASHBOARD_REPO | Docker image storage for SPCS |

### SERVICE_TYPE Values

| SERVICE_TYPE | Source View(s) | Description |
|---|---|---|
| CORTEX AISQL | CORTEX_AISQL_USAGE_HISTORY | LLM function token credits |
| CORTEX ANALYST | CORTEX_ANALYST_USAGE_HISTORY + SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY | Text-to-SQL and Intelligence credits |
| CORTEX AGENT | CORTEX_AGENT_USAGE_HISTORY | Dedicated Cortex Agent per-request credits |
| CORTEX SEARCH | CORTEX_SEARCH_DAILY_USAGE_HISTORY | Search service daily credits |
| FINE TUNING | CORTEX_FINE_TUNING_USAGE_HISTORY | Fine-tuning job credits |
| DOCUMENT AI | CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY | Document processing credits |
| CORTEX REST API | CORTEX_REST_API_USAGE_HISTORY | REST API inference (tokens only) |
| CORTEX CODE CLI | CORTEX_CODE_CLI_USAGE_HISTORY | Code assistant credits |
| PROVISIONED THROUGHPUT | CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY | PTU capacity credits |

### Customer Package Files

| File | Purpose |
|---|---|
| setup.sql | Complete DDL + stored procedure + task creation |
| ARCHITECTURE.md | This document |
| README.md | Deployment guide |
| snowsight_dashboard_queries.sql | Snowsight SQL tile queries |
| cortex-cost-dashboard/ | React dashboard source (Next.js + SPCS) |
