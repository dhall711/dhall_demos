# Cortex AI Cost Tracking & Backcharge Solution

Centralized tracking, visualization, and backcharge allocation of Snowflake Cortex AI credit and token consumption. Consolidates usage from 10 ACCOUNT_USAGE views into a single summary table with interactive dashboards.

## Prerequisites

| Requirement | Details |
|---|---|
| Snowflake Account | Enterprise edition or higher |
| Role | ACCOUNTADMIN (for initial setup) or a role with IMPORTED PRIVILEGES on the SNOWFLAKE database |
| Warehouse | Any X-Small or larger warehouse |
| Docker Desktop | Required only for SPCS React dashboard deployment |
| Node.js 20+ | Required only for local React dashboard development |
| Snowflake CLI (`snow`) | Required only for SPCS image push |

## Package Contents

| File | Purpose |
|---|---|
| `setup.sql` | Complete DDL: database, schema, tables, view, stored procedure, task, image repository |
| `ARCHITECTURE.md` | Technical architecture documentation |
| `README.md` | This file |
| `snowsight_dashboard_queries.sql` | SQL queries for native Snowsight dashboard tiles |
| `cortex-cost-dashboard/` | React dashboard source (Next.js + SPCS) |

## Quick Start

### Step 1: Configure and Run setup.sql

Open `setup.sql` and update the configuration variables at the top:

```sql
SET CORTEX_DB = 'CORTEX_AI_USAGE';       -- Target database name
SET CORTEX_SCHEMA = 'CORTEX_COST';        -- Target schema name
SET CORTEX_WH = 'MY_WAREHOUSE';           -- Warehouse for procedure/task execution
SET CORTEX_ROLE = 'SYSADMIN';             -- Role that owns the objects
```

Run the entire script in a Snowsight worksheet or SnowSQL as ACCOUNTADMIN. The script is idempotent and safe to re-run.

**What it creates:**

| Object | Type | Purpose |
|---|---|---|
| `CORTEX_AI_SUMMARY_COST` | Table | Unified summary of all Cortex AI usage with credit and token tracking |
| `USER_CUSTOM_BACKCHARGES_MAPPING` | Table | Customer-populated cost center allocations (joins via RECORD_KEY) |
| `CORTEX_AI_SUMMARY_COST_VIEW` | View | Read-through view with backcharge LEFT JOIN |
| `REFRESH_CORTEX_COST_DATA()` | Procedure | Truncate + reload from 10 source views (single-pass UNION ALL) |
| `REFRESH_COST_DATA_TASK` | Task | CRON-scheduled daily refresh at 6 AM Pacific |
| `DASHBOARD_REPO` | Image Repository | Docker image storage for SPCS dashboard |

### Step 2: Verify Data

```sql
USE <your_database>.<your_schema>;

-- Check row counts by service type
SELECT SERVICE_TYPE, COUNT(*) AS ROW_CNT,
       ROUND(SUM(COMPONENT_CREDITS), 2) AS TOTAL_CREDITS,
       SUM(TOTAL_TOKENS) AS TOTAL_TOKENS
FROM CORTEX_AI_SUMMARY_COST
GROUP BY SERVICE_TYPE
ORDER BY TOTAL_CREDITS DESC;

-- Verify the view works
SELECT COUNT(*) FROM CORTEX_AI_SUMMARY_COST_VIEW;

-- Check task status
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME = 'REFRESH_COST_DATA_TASK'
ORDER BY SCHEDULED_TIME DESC
LIMIT 5;
```

### Step 3: Resume the Task

The task is created in a resumed state by default. To manage it:

```sql
-- Suspend the task
ALTER TASK REFRESH_COST_DATA_TASK SUSPEND;

-- Resume the task
ALTER TASK REFRESH_COST_DATA_TASK RESUME;

-- Trigger a manual refresh at any time
EXECUTE TASK REFRESH_COST_DATA_TASK;
```

## Dashboard Deployment

### Option A: Snowsight SQL Tiles

1. In Snowsight, create a new **Dashboard**
2. For each tile, click **+ New Tile > From SQL Worksheet**
3. Paste each query from `snowsight_dashboard_queries.sql`
4. Set the chart type as indicated in the SQL comments

### Option B: React Dashboard on SPCS

This deploys a full interactive React dashboard (Next.js + shadcn/ui + Recharts) to Snowpark Container Services.

#### 1. Authenticate Docker with Snowflake Image Registry

```bash
snow spcs image-registry token --connection <your_connection> --format json | \
  docker login <orgname>-<acctname>.registry.snowflakecomputing.com \
  -u 0sessiontoken --password-stdin
```

Replace `<your_connection>` with your Snowflake CLI connection name, and `<orgname>-<acctname>` with your account identifier.

#### 2. Build the Docker Image

```bash
cd cortex-cost-dashboard
docker build --platform linux/amd64 -t cortex-cost-dashboard .
```

#### 3. Tag and Push to Snowflake Registry

```bash
# Set your registry path (replace with your account values)
REGISTRY=<orgname>-<acctname>.registry.snowflakecomputing.com
REPO_PATH=<database>/<schema>/dashboard_repo

docker tag cortex-cost-dashboard $REGISTRY/$REPO_PATH/cortex-cost-dashboard:latest
docker push $REGISTRY/$REPO_PATH/cortex-cost-dashboard:latest
```

#### 4. Create the SPCS Service

Run the following in Snowsight or SnowSQL. Update the environment variables to match your configuration:

```sql
USE <your_database>.<your_schema>;

CREATE SERVICE CORTEX_USAGE_DASHBOARD
  IN COMPUTE POOL <your_compute_pool>
  FROM SPECIFICATION $$
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
  $$
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1;
```

> **IMPORTANT:** Do NOT set `SNOWFLAKE_HOST` or `SNOWFLAKE_ACCOUNT` in the service spec. SPCS auto-injects these at runtime via the OAuth token at `/snowflake/session/token`.

#### 5. Get the Dashboard URL

```sql
SHOW ENDPOINTS IN SERVICE CORTEX_USAGE_DASHBOARD;
```

The `ingress_url` value is your public dashboard URL.

#### 6. Grant Access to Other Users

```sql
GRANT USAGE ON SERVICE CORTEX_USAGE_DASHBOARD TO ROLE <role_name>;
```

## Updating the SPCS Dashboard

> **CRITICAL:** SPCS caches Docker images. Suspending and resuming a service does NOT pull a new image. You must drop and recreate the service to deploy updated code.

```bash
# Build, tag, and push the new image
cd cortex-cost-dashboard
docker build --platform linux/amd64 -t cortex-cost-dashboard .
docker tag cortex-cost-dashboard $REGISTRY/$REPO_PATH/cortex-cost-dashboard:latest
docker push $REGISTRY/$REPO_PATH/cortex-cost-dashboard:latest
```

```sql
-- Drop and recreate the service to pull the new image
DROP SERVICE CORTEX_USAGE_DASHBOARD;
-- Then re-run the CREATE SERVICE statement from Step 4 above
```

## Local Development (React Dashboard)

```bash
cd cortex-cost-dashboard
npm install
```

Create a `.env.local` file (see `.env.example` for reference):

```env
SNOWFLAKE_ACCOUNT=<orgname>-<acctname>
SNOWFLAKE_USER=<your_username>
SNOWFLAKE_WAREHOUSE=<your_warehouse>
SNOWFLAKE_DATABASE=<your_database>
SNOWFLAKE_SCHEMA=<your_schema>
```

```bash
npm run dev
```

The app starts at `http://localhost:3000`. It uses External Browser SSO for authentication in local mode.

A static fallback dataset placeholder is included in `public/data.json` for offline development. Replace it with your own data export if needed.

## Token Tracking

The solution tracks input and output token usage across all Cortex services that expose token data:

| Token Extraction | Services | Method |
|---|---|---|
| Full input/output split | AISQL, REST API, Code CLI | Flat `TOKENS_GRANULAR` JSON parse |
| Full input/output split | Agent, Intelligence | LATERAL FLATTEN on nested array `TOKENS_GRANULAR` |
| Total tokens only | Search, Fine Tuning | `TOKENS` column (no input/output split) |
| No token data | Analyst, Document AI, Provisioned Throughput | Zeros |

**Token formula:** `INPUT_TOKENS = input + cache_read_input + cache_write_input`

The dashboard displays:
- Total Tokens KPI card
- Tokens by Service stacked bar chart (input vs output)
- Token columns in the detail table

## Backcharge Mapping

To allocate costs to teams, departments, or business units, populate the `USER_CUSTOM_BACKCHARGES_MAPPING` table:

```sql
INSERT INTO USER_CUSTOM_BACKCHARGES_MAPPING (
    RECORD_KEY, BACKCHARGE_TEAM, BACKCHARGE_BUSINESS_UNIT,
    BACKCHARGE_DEPARTMENT, BACKCHARGE_OWNER
)
SELECT RECORD_KEY, 'Engineering', 'Product', 'Data Science', 'jsmith'
FROM CORTEX_AI_SUMMARY_COST
WHERE END_USER_NAME = 'JSMITH';
```

The `RECORD_KEY` is a deterministic SHA2 hash that survives table refreshes, so your mappings persist across daily reloads.

## Customization

### Change the Refresh Schedule

```sql
ALTER TASK REFRESH_COST_DATA_TASK SET SCHEDULE = 'USING CRON 0 */4 * * * America/Los_Angeles';
ALTER TASK REFRESH_COST_DATA_TASK RESUME;
```

### Change the Credit Rate

The default cost rate is **$3.00/credit**, configured client-side in the React dashboard. Update the rate using the $/credit input in the dashboard header.

## Covered Cortex Services

| # | Service | ACCOUNT_USAGE View | Credits Column | Token Extraction |
|---|---|---|---|---|
| 1 | Cortex AISQL | CORTEX_AISQL_USAGE_HISTORY | TOKEN_CREDITS | Flat JSON (input/output) |
| 2 | Cortex Analyst | CORTEX_ANALYST_USAGE_HISTORY | CREDITS | None |
| 3 | Snowflake Intelligence | SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY | TOKEN_CREDITS | Nested array (input/output) |
| 4 | Cortex Agent | CORTEX_AGENT_USAGE_HISTORY | TOKEN_CREDITS | Nested array (input/output) |
| 5 | Cortex Search | CORTEX_SEARCH_DAILY_USAGE_HISTORY | CREDITS | Total only |
| 6 | Fine Tuning | CORTEX_FINE_TUNING_USAGE_HISTORY | TOKEN_CREDITS | Total only |
| 7 | Document AI | CORTEX_DOCUMENT_PROCESSING_USAGE_HISTORY | CREDITS_USED | None |
| 8 | REST API | CORTEX_REST_API_USAGE_HISTORY | (tokens only, no credits) | Flat JSON (input/output) |
| 9 | Cortex Code CLI | CORTEX_CODE_CLI_USAGE_HISTORY | TOKEN_CREDITS | Flat JSON (input/output) |
| 10 | Provisioned Throughput | CORTEX_PROVISIONED_THROUGHPUT_USAGE_HISTORY | PTU_CREDITS | None |

> **Note:** CORTEX_REST_API_USAGE_HISTORY tracks tokens but has no credits column. These rows appear in the dashboard with 0 credits for visibility.

## Troubleshooting

| Issue | Solution |
|---|---|
| Procedure returns 0 rows | Verify IMPORTED PRIVILEGES: `SHOW GRANTS ON DATABASE SNOWFLAKE` |
| Task not running | Check task is resumed: `SHOW TASKS LIKE 'REFRESH_COST_DATA_TASK'` |
| SPCS dashboard shows old data | The dashboard queries live data. Run `EXECUTE TASK REFRESH_COST_DATA_TASK` to refresh. |
| SPCS shows old code after image push | Must DROP SERVICE and CREATE SERVICE. Suspend/resume does NOT pull new images. |
| NULL credits in dashboard | Expected for REST API rows. All queries use COALESCE to handle NULLs. |
| USER_0 appears as username | USER_ID not found in SNOWFLAKE.ACCOUNT_USAGE.USERS view. This is a fallback display name. |
| `$$` delimiter errors in worksheets | Some SQL tools don't support `$$`. Use SnowSQL or Snowsight worksheets which handle `$$` correctly. |

## Security Notes

- The stored procedure runs as `EXECUTE AS CALLER` -- the caller must have IMPORTED PRIVILEGES on the SNOWFLAKE database.
- SPCS authentication uses auto-injected OAuth tokens. No credentials are stored in the container image.
- The React dashboard does not store or cache any Snowflake credentials.
- All dashboard queries read from `CORTEX_AI_SUMMARY_COST_VIEW` -- users need only SELECT access on this view plus USAGE on the warehouse.
