# CoCo Prompting Guide: Fivetran + Snowflake Cortex AI Demo
## Replicable Step-by-Step Prompts for Live Demo

> **Purpose**: Use these exact prompts in Cortex Code (CoCo) to replicate the entire demo pipeline live. Each section includes the CoCo prompt, expected output, and talking points.

---

## Prerequisites
- Snowflake account with SYSADMIN role
- Docker installed locally (for SPCS deployment)
- Cortex Code (CoCo) running

---

## Section 1: Database & Synthetic Data Setup (5 min)

### CoCo Prompt:
```
Create a Snowflake database called FIVETRAN_RETAIL_DEMO with schemas: BRONZE, SILVER, SILVER_DBT, GOLD, and ANALYTICS. 

Generate synthetic e-commerce data in the BRONZE schema simulating Fivetran-landed tables. Include _FIVETRAN_SYNCED (TIMESTAMP_NTZ) and _FIVETRAN_DELETED (BOOLEAN) columns on every table. Add some duplicate records to demonstrate dedup.

Tables needed:
1. RAW_CUSTOMERS (~1000 rows) - customer_id, first_name, last_name, email, city, state, signup_date, customer_segment (New/Active/VIP/At-Risk/Churned), lifetime_value, preferred_category, marketing_channel
2. RAW_PRODUCTS (~56 rows) - product_id, product_name, category (Electronics/Apparel/Home & Garden/Sports/Beauty), subcategory, brand, unit_price, unit_cost, description
3. RAW_ORDERS (~5000 rows) - order_id, customer_id, product_id, order_date, quantity, total_amount, order_status, payment_method, shipping_zone, warehouse
4. RAW_INVENTORY (~2500 rows) - inventory_id, product_id, warehouse (East DC NJ/West DC CA/Central DC TX/Southeast DC GA), snapshot_date, units_on_hand, reorder_point
5. RAW_REVIEWS (~2000 rows) - review_id, product_id, customer_id, rating (1-5), review_title, review_text, review_date
```

**Talking Point**: "CoCo generates the complete DDL and synthetic data in one shot. Notice the Fivetran metadata columns - this is exactly what Fivetran lands in your warehouse."

---

## Section 2: Fivetran MCP Integration (5 min)

### Demo Steps (Manual - show the concept):
1. Open a browser to `github.com/fivetran/fivetran-mcp`
2. Show the README - MCP server that connects AI tools to Fivetran
3. Show the CoCo MCP configuration example:

```json
{
  "mcpServers": {
    "fivetran": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/fivetran/fivetran-mcp", "fivetran-mcp"],
      "env": {
        "FIVETRAN_API_KEY": "your-api-key",
        "FIVETRAN_API_SECRET": "your-api-secret"
      }
    }
  }
}
```

4. Explain: "With this configured, CoCo can ask Fivetran: 'Are any connectors broken?', 'When did Shopify last sync?', 'Update sync frequency to every 3 hours'"

**Talking Point**: "Fivetran's MCP server turns your AI coding assistant into a Fivetran control plane. Combined with Snowflake's MCP server for Cortex Agents, you get end-to-end AI-powered pipeline management."

---

## Section 3: dbt Project for Silver Transforms (7 min)

### CoCo Prompt:
```
Create a dbt project called fivetran_retail_transforms that transforms the Bronze tables into Silver. Target the SILVER_DBT schema in FIVETRAN_RETAIL_DEMO.

For each model:
- Use QUALIFY ROW_NUMBER() OVER (PARTITION BY primary_key ORDER BY _fivetran_synced DESC) = 1 to dedup Fivetran records
- Filter out _fivetran_deleted = TRUE
- Add calendar enrichment (day_of_week, is_weekend, season)
- Add business logic transforms

Models:
1. stg_customers_clean - Add tenure_days, tenure_bucket (New/Established/Loyal)
2. stg_products_clean - Add unit_margin, margin_pct, price_tier (Premium/Mid-Range/Budget)
3. stg_orders_clean - Add net_revenue, status_group (Fulfilled/In Progress/Cancelled/Returned), season
4. stg_inventory_clean - Add available_units, stock_status (Out of Stock/Low Stock/Healthy/Overstock), stockout_risk flag
5. stg_reviews_clean - Add sentiment (Positive/Neutral/Negative), review_depth (Detailed/Standard/Brief)

Include comprehensive dbt tests: unique, not_null on PKs, accepted_values on all derived categories. Then run dbt run and dbt test.
```

**Talking Point**: "dbt gives us version-controlled, tested transforms. The dedup pattern handles Fivetran's at-least-once delivery guarantee. All 25 tests pass - that's your data quality gate."

---

## Section 4: Dynamic Tables - Gold Layer (3 min)

### CoCo Prompt:
```
Create 4 Dynamic Tables in the GOLD schema of FIVETRAN_RETAIL_DEMO with a 10-minute target lag:

1. DT_DAILY_SALES - Aggregate orders + products by date, category, shipping_zone, warehouse. Include order_count, gross_revenue, net_revenue, avg_order_value, return_rate_pct
2. DT_CUSTOMER_SEGMENTS - Aggregate customers + orders by segment, tenure, channel. Include customer_count, avg_lifetime_value, total_revenue, avg_orders_per_customer  
3. DT_PRODUCT_PERFORMANCE - Products + orders + reviews. Include total_orders, total_revenue, avg_rating, review_count, margin_pct
4. DT_INVENTORY_HEALTH - Inventory + products by warehouse, category, stock_status. Include units_on_hand, stockout_risk_count, inventory_value (30-min lag)
```

**Talking Point**: "Dynamic Tables replace 4 Airflow DAGs with pure SQL. No scheduler, no orchestration code, no monitoring setup. Snowflake handles refresh automatically."

---

## Section 5: Semantic Model & Semantic View (5 min)

### CoCo Prompt:
```
Create a Cortex Analyst semantic model YAML for the 4 Gold Dynamic Tables in FIVETRAN_RETAIL_DEMO. Include dimensions with synonyms, measures with aggregation types, and 6 verified queries for common retail questions like "What are our top selling categories?" and "Which products are at risk of stockout?". 

Then create a Semantic View from the YAML using SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML in the ANALYTICS schema.
```

**Talking Point**: "The semantic model is the bridge between business language and SQL. When someone asks 'What are our sales?', Cortex Analyst knows that maps to SUM(GROSS_REVENUE). The verified queries serve as ground truth for common questions."

---

## Section 6: Cortex Search Service (3 min)

### CoCo Prompt:
```
Create a Cortex Search Service called PRODUCT_REVIEW_SEARCH in FIVETRAN_RETAIL_DEMO.ANALYTICS. Index the product reviews from SILVER_DBT joined with product names. Use the concatenated review text + product name + category as the search content. Add filterable attributes for product_category, sentiment, and brand.
```

**Talking Point**: "Cortex Search gives us RAG over unstructured data - customer reviews. The agent can now answer 'What are customers saying about our electronics?' by searching across thousands of reviews."

---

## Section 7: Cortex Agent (5 min)

### CoCo Prompt:
```
Create a Cortex Agent called RETAIL_AGENT in FIVETRAN_RETAIL_DEMO.ANALYTICS that combines:
1. Cortex Analyst tool using the RETAIL_ANALYTICS semantic view for structured data queries
2. Cortex Search tool using PRODUCT_REVIEW_SEARCH for customer review analysis
3. data_to_chart tool for automatic visualizations

Add orchestration instructions: "Use Analyst for sales/revenue/customer/inventory metrics. Use Search for customer feedback and product reviews."

Add sample questions like "What are our top selling categories?", "What are customers saying about electronics?", "Which products are at risk of stockout?"
```

**Talking Point**: "The Cortex Agent is the orchestrator. It decides whether to query structured data (Analyst) or search reviews (Search) based on the question. It can even chain both tools for complex questions like 'Show me our worst-rated products and their sales impact'."

---

## Section 8: React SPCS Dashboard (7 min)

### CoCo Prompt:
```
Build a React dashboard app with Vite + Tailwind CSS + Recharts that has two tabs:

Tab 1 - Analytics Dashboard: KPI cards (Total Revenue $5.37M, Orders 5,675, AOV $946, Customers 1,000), bar chart for revenue by category, line chart for monthly trend, top products table, customer segment pie chart, and a pipeline status banner showing the full data flow.

Tab 2 - AI Assistant: Chat interface with sample question buttons that demonstrates the Cortex Agent interaction. Include formatted table responses and tool attribution badges.

Then create a Dockerfile using nginx-alpine to serve the built app on port 8080. Deploy to SPCS using the CPU_X64_XS compute pool.
```

**Talking Point**: "The React app runs in Snowflake's Snowpark Container Services - no external hosting needed. The entire stack lives inside Snowflake's security perimeter."

---

## Section 9: Snowflake Intelligence (3 min)

### Demo Steps (Manual in Snowsight):
1. Navigate to AI & ML > Agents
2. Show the RETAIL_AGENT configuration
3. Open Snowflake Intelligence
4. Select the Retail Analytics Assistant agent
5. Ask: "What are our top selling categories this month?"
6. Ask: "What are customers saying about our electronics products?"
7. Show the chart auto-generation

**Talking Point**: "Snowflake Intelligence is the consumer experience. Business users don't need SQL or a custom app - they just ask questions. The same agent powers both the React app and Snowflake Intelligence."

---

## Section 10: Wrap-Up (2 min)

### Key Takeaways:
1. **Fivetran** handles ELT - land data reliably with built-in schemas
2. **dbt** handles transforms - version-controlled, tested, documented  
3. **Dynamic Tables** handle aggregation - no DAGs, auto-refresh
4. **Cortex AI** handles analytics - natural language over structured + unstructured
5. **SPCS** handles delivery - apps run inside Snowflake's perimeter
6. **CoCo** accelerated everything - from weeks to 45 minutes

### Architecture Diagram to Draw:
```
Fivetran (ELT) → Bronze → dbt (Silver) → Dynamic Tables (Gold) → Semantic View → Cortex Agent → React SPCS / Snowflake Intelligence
                                                                      ↑                ↑
                                                              Cortex Search     Fivetran UDFs
                                                              (Reviews)         (Pipeline Ops)
```

---

## BONUS Section 11: MCP Bridge - Fivetran to Snowflake (5 min)

### CoCo Prompt - Snowflake Managed MCP Server:
```
Create a Snowflake Managed MCP Server called RETAIL_MCP_SERVER in FIVETRAN_RETAIL_DEMO.ANALYTICS that exposes the following tools:

1. CORTEX_ANALYST_MESSAGE tool pointing to the RETAIL_ANALYTICS semantic view
2. CORTEX_SEARCH_SERVICE_QUERY tool pointing to PRODUCT_REVIEW_SEARCH
3. CORTEX_AGENT_RUN tool pointing to RETAIL_AGENT
4. SYSTEM_EXECUTE_SQL tool with read_only=true and query_timeout=60
5. Three GENERIC (UDF) tools for Fivetran operations: connector status, sync history, and trigger sync

The MCP Server should be accessible via the standard MCP protocol endpoint.
```

**Talking Point**: "The Snowflake Managed MCP Server exposes all our Cortex AI tools - Analyst, Search, Agent, SQL, and custom UDFs - through a single standardized endpoint. Claude Desktop, CoCo, or any MCP-compatible client can discover and invoke these tools. No custom API to build."

### CoCo Prompt - Fivetran Simulator UDFs:
```
Create 3 Python UDFs in FIVETRAN_RETAIL_DEMO.ANALYTICS that simulate Fivetran API operations:

1. GET_FIVETRAN_CONNECTOR_STATUS(connector_name VARCHAR) - Returns VARIANT with connector health, sync state, last sync time, rows synced, and data freshness. Support 'all' to get all 5 connectors (shopify_orders, stripe_payments, zendesk_reviews, warehouse_inventory, erp_products).

2. GET_FIVETRAN_SYNC_HISTORY(connector_name VARCHAR) - Returns VARIANT with last 10 syncs including timestamps, row counts, duration, and status.

3. TRIGGER_FIVETRAN_SYNC(connector_name VARCHAR) - Returns VARIANT with sync confirmation, sync ID, and estimated completion time.

Then add these as custom tools to the RETAIL_AGENT and the MCP Server.
```

**Talking Point**: "In production, these UDFs would call Fivetran's REST API using external access integrations. For this demo, they simulate realistic responses. The key insight: the Cortex Agent can now answer 'Are my pipelines healthy?' alongside 'What are my top selling categories?' - analytics AND operations in one conversational interface."

### Demo Flow for MCP Bridge:
1. Show the MCP Server: `DESCRIBE MCP SERVER FIVETRAN_RETAIL_DEMO.ANALYTICS.RETAIL_MCP_SERVER`
2. Show the endpoint URL format: `https://<account>/api/v2/databases/FIVETRAN_RETAIL_DEMO/schemas/ANALYTICS/mcp-servers/RETAIL_MCP_SERVER`
3. Ask the agent: "What is the status of our Fivetran connectors?"
4. Ask the agent: "Show me the sync history for shopify_orders"
5. Ask a cross-domain question: "Is our data fresh enough to trust the revenue numbers?"
6. Show the React app MCP Architecture tab
7. Show the Fivetran MCP GitHub: `github.com/fivetran/fivetran-mcp`

**Key Talking Points**:
- "MCP is the universal adapter for AI agents. Fivetran has one, Snowflake has one, and they can talk to each other."
- "The Snowflake MCP Server is a first-class managed object with RBAC. You grant USAGE on the server and SELECT/USAGE on individual tools."
- "In production, you'd also create an EXTERNAL MCP SERVER that connects Cortex Agents directly to Fivetran's MCP endpoint - so the agent can manage real Fivetran connectors, not simulated ones."
- "This is the future: AI agents that span the entire data stack, from ingestion (Fivetran) through transformation (dbt) to analytics (Cortex AI)."
