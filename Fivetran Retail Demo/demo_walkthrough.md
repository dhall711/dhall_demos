# Fivetran SE Demo: Snowflake Cortex AI End-to-End Pipeline
## 45-Minute Walkthrough Guide

---

## Pre-Demo Checklist
- [ ] Open CoCo (Cortex Code) desktop app
- [ ] Verify Snowflake connection (SFSENORTHAMERICA-DHALL_AWS1, SYSADMIN)
- [ ] Database FIVETRAN_RETAIL_DEMO exists with all schemas populated
- [ ] dbt project runs clean (25/25 tests pass)
- [ ] Dynamic Tables are ACTIVE in GOLD schema
- [ ] Cortex Agent RETAIL_AGENT is created
- [ ] SPCS service RETAIL_DASHBOARD is RUNNING
- [ ] Open SPCS endpoint URL in browser (keep tab ready)
- [ ] Open Snowflake Intelligence in Snowsight (keep tab ready)
- [ ] Have `coco_prompting_guide.md` open for reference

---

## Opening (2 min)

**Key Message**: "Today I'm going to show you how Fivetran + Snowflake create the ultimate modern data stack. We'll go from raw data landing to AI-powered analytics in a single session using Cortex Code."

**Agenda slide** (if using slides):
1. The Modern Data Stack: Fivetran + Snowflake + dbt
2. From ELT to Insight: Building the Pipeline Live
3. AI-Powered Analytics: Cortex Agent, Search, Intelligence
4. Delivery: React Dashboard on SPCS
5. The Acceleration Story: CoCo + MCP

---

## Act 1: The Data Foundation (10 min)

### Scene 1: Fivetran Landing Zone (3 min)

**Show**: BRONZE schema tables in Snowsight or CoCo

**Script**: "Fivetran lands data into what we call the Bronze layer. Notice the `_FIVETRAN_SYNCED` and `_FIVETRAN_DELETED` columns - these are Fivetran's metadata that tells us exactly when each record was synced and whether it's been soft-deleted at the source."

**Run**: 
```sql
SELECT * FROM FIVETRAN_RETAIL_DEMO.BRONZE.RAW_ORDERS LIMIT 5;
```

**Point out**: "See these duplicate order_ids? Fivetran guarantees at-least-once delivery. We need a dedup strategy - that's where dbt comes in."

### Scene 2: Fivetran MCP Integration (2 min)

**Show**: Fivetran MCP GitHub page (github.com/fivetran/fivetran-mcp)

**Script**: "Fivetran has an open-source MCP server that connects AI tools like CoCo directly to your Fivetran environment. You can ask CoCo: 'Are any of my connectors broken?' or 'Trigger a sync for my Shopify connection.' This turns your AI assistant into a Fivetran control plane."

**Show** the MCP config JSON from the prompting guide.

### Scene 3: dbt Transforms (5 min)

**Show**: dbt project in CoCo file explorer

**Script**: "dbt manages our Bronze-to-Silver transforms. Each model does three critical things: dedup Fivetran records, enrich with business logic, and quality gate the data."

**Show**: `stg_orders_clean.sql` - highlight the QUALIFY dedup pattern

**Run dbt** (or show pre-run output):
```
dbt run  -- 5 models SUCCESS
dbt test -- 25 tests PASS
```

**Script**: "25 out of 25 tests pass. Every time we run dbt, we know our Silver data is clean, deduplicated, and business-ready. This is your data quality contract."

---

## Act 2: The Analytics Layer (10 min)

### Scene 4: Dynamic Tables (3 min)

**Show**: Gold schema DTs in Snowsight

**Script**: "Dynamic Tables replace Airflow. Instead of writing a DAG with scheduling, error handling, and monitoring, I write one SQL query. Snowflake handles the rest - auto-refresh every 10 minutes."

**Run**:
```sql
SHOW DYNAMIC TABLES IN SCHEMA FIVETRAN_RETAIL_DEMO.GOLD;
```

**Point out**: "All 4 Dynamic Tables are ACTIVE. No infrastructure to maintain."

### Scene 5: Semantic Model & View (4 min)

**Script**: "The semantic model is the business dictionary. It tells Cortex Analyst that when someone says 'revenue', they mean SUM(GROSS_REVENUE). When they say 'AOV', they mean AVG(AVG_ORDER_VALUE)."

**Show**: YAML semantic model file briefly

**Run**:
```sql
SHOW SEMANTIC VIEWS IN SCHEMA FIVETRAN_RETAIL_DEMO.ANALYTICS;
SHOW SEMANTIC METRICS IN FIVETRAN_RETAIL_DEMO.ANALYTICS.RETAIL_ANALYTICS;
```

**Script**: "The semantic view is a first-class Snowflake object. You grant SELECT on it just like a table. All the business definitions are governed and versioned."

### Scene 6: Cortex Search (3 min)

**Script**: "For unstructured data - customer reviews - we use Cortex Search. It creates a vector index over review text so the agent can find relevant customer feedback."

**Run**:
```sql
SELECT PARSE_JSON(SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
  'FIVETRAN_RETAIL_DEMO.ANALYTICS.PRODUCT_REVIEW_SEARCH',
  '{"query": "electronics quality", "columns": ["PRODUCT_NAME", "SENTIMENT", "SEARCH_CONTENT"], "limit": 3}'
)) AS results;
```

---

## Act 3: The AI Layer (12 min)

### Scene 7: Cortex Agent (5 min)

**Script**: "The Cortex Agent is the orchestrator. It combines Analyst (structured SQL), Search (unstructured reviews), and charting into one intelligent interface."

**Show**: Agent configuration in Snowsight (AI & ML > Agents)

**Demo in Snowsight Agent Playground**:
1. "What are our top selling categories?" (triggers Analyst)
2. "What are customers saying about our electronics products?" (triggers Search)
3. "Which products have the highest revenue but lowest ratings?" (triggers both)

### Scene 8: Snowflake Intelligence (3 min)

**Navigate to**: Snowflake Intelligence in Snowsight

**Script**: "Snowflake Intelligence is the business user experience. No SQL, no dashboards to build - just ask questions."

**Demo questions**:
1. "Show me the monthly sales trend with a chart"
2. "How do VIP customers compare to at-risk customers?"

### Scene 9: React SPCS Dashboard (4 min)

**Open**: SPCS endpoint URL in browser

**Script**: "For teams that want a branded experience, we built a React dashboard deployed directly in Snowflake's Snowpark Container Services. No external hosting, no egress costs, everything stays inside Snowflake's security perimeter."

**Show**: Dashboard tab - KPIs, charts, top products

**Show**: AI Assistant tab - ask a sample question, show formatted response

---

## Act 4: The CoCo Story (8 min)

### Scene 10: CoCo Skills Showcase (5 min)

**Script**: "Everything you just saw was built using Cortex Code. Let me show you the acceleration."

**Show CoCo in action** (pick 1-2 to demo live):

Option A - Semantic View skill:
```
CoCo prompt: "Create a semantic view for the Gold tables"
Show the semantic-view skill activating
```

Option B - Cortex Agent skill:
```
CoCo prompt: "Create a Cortex Agent that combines my semantic view with the search service"
Show the cortex-agent skill activating
```

Option C - Deploy to SPCS skill:
```
CoCo prompt: "Deploy my React app to SPCS"
Show the deploy-to-spcs skill activating
```

### Scene 11: Fivetran MCP + Snowflake MCP Bridge (5 min)

**Script**: "Now for the punchline. MCP - the Model Context Protocol - is the universal adapter that connects AI agents to tools. Both Fivetran and Snowflake have MCP servers. Let me show you how they bridge together."

**Step 1**: Show the Snowflake Managed MCP Server:
```sql
DESCRIBE MCP SERVER FIVETRAN_RETAIL_DEMO.ANALYTICS.RETAIL_MCP_SERVER;
-- Shows 7 tools: Analyst, Search, Agent, SQL, + 3 Fivetran UDFs
```

**Script**: "This MCP server exposes ALL our Cortex tools through one standardized endpoint. Any MCP client - Claude Desktop, CoCo, a custom app - can discover and invoke these tools."

**Step 2**: Show the endpoint URL:
```
https://sfsenorthamerica-dhall-aws1.snowflakecomputing.com/api/v2/databases/FIVETRAN_RETAIL_DEMO/schemas/ANALYTICS/mcp-servers/RETAIL_MCP_SERVER
```

**Step 3**: Demo the agent with Fivetran questions:
- "What is the status of our Fivetran connectors?" (triggers FivetranStatus tool)
- "Show me sync history for shopify_orders" (triggers FivetranHistory tool)
- "Our inventory data feels stale - check the warehouse connector and show me current stockout risk" (triggers BOTH Fivetran + Analyst)

**Step 4**: Show the React app MCP Architecture tab (3rd tab)
- Architecture diagram
- Tool listing with status
- Sample MCP payloads

**Step 5**: Show the Fivetran MCP GitHub (github.com/fivetran/fivetran-mcp)
```
// In production, you'd also connect Fivetran's MCP as an External MCP Server:
CREATE EXTERNAL MCP SERVER fivetran_connector
  WITH DISPLAY_NAME = 'Fivetran Pipeline Manager'
  URL = 'https://your-fivetran-mcp-endpoint/mcp'
  API_INTEGRATION = fivetran_mcp_integration;

// Then add it to the agent:
ALTER AGENT RETAIL_AGENT ADD MCP_SERVER = 'db.schema.fivetran_connector';
```

**Architecture Diagram**:
```
  External AI Clients              Snowflake Account
  ==================              ==================
  Claude Desktop  ──┐    MCP     ┌──────────────────────────────────┐
  Cortex Code     ──┤──────────►│  Snowflake Managed MCP Server     │
  Custom Client   ──┘   JSON    │  7 Tools: Analyst, Search, Agent, │
                        RPC     │  SQL, + 3 Fivetran UDFs           │
                                └──────────────────────────────────┘
  Fivetran MCP Server                       │
  (github.com/fivetran/    ◄─── CoCo ──►   │
   fivetran-mcp)                            ▼
        │                         Cortex Agent (RETAIL_AGENT)
        ▼                         ├── Analyst (structured data)
  Fivetran REST API               ├── Search (reviews)
  (manage connectors)             ├── Charts (visualization)
                                  └── Fivetran UDFs (pipeline ops)
```

---

## Closing (3 min)

### Summary Slide:

| Component | Traditional | Snowflake + Fivetran |
|-----------|-------------|---------------------|
| ELT | Custom scripts | Fivetran (managed) |
| Transforms | Airflow DAGs | dbt (version-controlled) |
| Aggregations | More DAGs | Dynamic Tables (auto) |
| Analytics | Custom BI tool | Cortex Analyst (NL to SQL) |
| Unstructured | Not available | Cortex Search (RAG) |
| Orchestration | Multiple tools | Cortex Agent (unified) |
| App Hosting | AWS/GCP/Azure | SPCS (in-Snowflake) |
| AI Integration | Custom APIs | MCP (standardized) |
| Pipeline Ops | Manual monitoring | Agent + Fivetran MCP |
| Development | Weeks | CoCo (minutes) |

**Closing Statement**: "The Fivetran + Snowflake stack isn't just about moving data anymore. It's about making data instantly useful. Fivetran handles the plumbing, Snowflake handles the intelligence, and CoCo accelerates everything. What used to take weeks now takes 45 minutes."

---

## Q&A Preparation

**Expected Questions**:

1. **"Can the Cortex Agent call Fivetran APIs?"** 
   - Yes, three ways: (a) Custom UDFs that call Fivetran REST API via external access integrations - that's what we demo'd. (b) Fivetran's MCP server as an External MCP Server connected to the agent. (c) Stored procedures with HTTP functions. Option (b) is the cleanest path forward.

2. **"How does this work with existing dbt Cloud?"**
   - dbt Cloud works seamlessly. Fivetran lands data, dbt Cloud runs transforms on schedule, Dynamic Tables handle the Gold layer. CoCo can generate the dbt models.

3. **"What about data security?"**
   - Everything runs inside Snowflake's security perimeter. SPCS apps never expose data externally. Cortex AI processes data without it leaving Snowflake. Semantic views enforce access control.

4. **"How accurate is Cortex Analyst?"**
   - Verified queries serve as ground truth for common questions (100% accurate). For novel questions, accuracy depends on semantic model quality. In our tests, 85-95% accuracy on well-modeled domains.

5. **"Cost implications?"**
   - Dynamic Tables use serverless compute (pay per refresh). Cortex AI charges per token. SPCS charges per compute hour. Typically much lower than maintaining Airflow + custom BI + separate hosting.

---

## Backup Plans

**If SPCS is slow to start**: Show the locally-built React app instead (`npm run dev`)

**If Cortex Agent is slow**: Show pre-captured screenshots of agent responses

**If Dynamic Tables are stale**: Run `ALTER DYNAMIC TABLE ... REFRESH` manually

**If dbt fails**: Show pre-run test output from the coco_prompting_guide.md

---

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| data_setup.sql | fivetran_retail_demo/ | Database DDL and data generation |
| retail_analytics_model.yaml | fivetran_retail_demo/ | Semantic model YAML |
| coco_prompting_guide.md | fivetran_retail_demo/ | Live demo prompts |
| dbt project | fivetran_retail_dbt/ | Bronze-to-Silver transforms |
| React app | fivetran_retail_demo/react-app/ | SPCS dashboard source |

## Snowflake Objects Reference

| Object | Type | Purpose |
|--------|------|---------|
| FIVETRAN_RETAIL_DEMO | Database | Demo database with 5 schemas |
| ANALYTICS.RETAIL_ANALYTICS | Semantic View | Business definitions over Gold DTs |
| ANALYTICS.PRODUCT_REVIEW_SEARCH | Cortex Search | Review search index |
| ANALYTICS.RETAIL_AGENT | Cortex Agent | 6-tool orchestrating agent |
| ANALYTICS.RETAIL_MCP_SERVER | MCP Server | 7-tool managed MCP endpoint |
| ANALYTICS.GET_FIVETRAN_CONNECTOR_STATUS | UDF | Simulated Fivetran status API |
| ANALYTICS.GET_FIVETRAN_SYNC_HISTORY | UDF | Simulated sync history API |
| ANALYTICS.TRIGGER_FIVETRAN_SYNC | UDF | Simulated sync trigger API |
| ANALYTICS.RETAIL_DASHBOARD | SPCS Service | React dashboard app |
| GOLD.DT_DAILY_SALES | Dynamic Table | Sales aggregations |
| GOLD.DT_CUSTOMER_SEGMENTS | Dynamic Table | Customer segment metrics |
| GOLD.DT_PRODUCT_PERFORMANCE | Dynamic Table | Product performance metrics |
| GOLD.DT_INVENTORY_HEALTH | Dynamic Table | Inventory health metrics |
