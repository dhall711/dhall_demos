# Comcast GCS Cybersecurity - Certificate Compliance Demo

End-to-end Snowflake demo built for Sajit's cybersecurity team at Comcast (5/29 deep-dive session).

## Story

Comcast's cybersecurity group issues millions of X.509 certificates per day to IoT devices, streaming endpoints, gateways, partners, and internal services -- with billions in active inventory. They run on Postgres + DynamoDB today and want to know if Snowflake can:

1. Handle their ingestion scale with transformations
2. Power AI/RAG chat over both structured cert data and unstructured policy docs
3. Coexist with their OLTP world (Postgres)
4. Expose all of this via API (not just UI) -- they want to build their own front-ends

This demo proves all four in one platform.

## Architecture

```
                  +-----------------+
   Streaming  --> | RAW_CERT_EVENTS | (Snowpipe Streaming-ready, simulated via task)
   sources        +--------+--------+
                           |
                           v
                  +-----------------+
                  | DT_CERTS_CLEAN  | (Bronze->Silver: SCD Type 1 dedup via QUALIFY)
                  +--------+--------+
                           |
                           v
                  +-----------------+      +----------+
                  | DT_CERTS_ENRICH | <----+ PARTNERS |
                  +--------+--------+      +----------+
                           |
                           v
                  +-----------------+
                  | DT_DASHBOARD    | (Gold aggregations)
                  +--------+--------+
                           |
                           v
                  +-----------------+      +-----------------+
                  | CERT_COMPLIANCE | <--->| CORTEX_SEARCH   |
                  | _SV (semantic)  |      | (policy docs)   |
                  +--------+--------+      +--------+--------+
                           |                        |
                           +-----------+-----------+
                                       v
                            +---------------------+
                            | CERT_COMPLIANCE_AGT |
                            | (Cortex Agent)      |
                            +----------+----------+
                                       |
                            +----------v----------+
                            | React/Next.js on    |
                            | SPCS (public URL)   |
                            +---------------------+

   PARALLEL: CERT_OLTP_DB Postgres instance (OLTP) -- same platform as Snowflake OLAP
```

## Snowflake Objects

All in `COMCAST_CYBER_DEMO.CERT_SECURITY`:

| Object | Type | Purpose |
|---|---|---|
| `CERTIFICATES` | Table | 50M synthetic cert records (realistic distribution) |
| `PARTNERS` | Table | 50 partner dimension rows |
| `COMPLIANCE_RULES` | Table | 10 reference compliance policies |
| `COMPLIANCE_DOCUMENTS` | Table | 10 long-form policy/runbook/audit docs (RAG corpus) |
| `RAW_CERTIFICATE_EVENTS` | Table | Streaming landing zone |
| `SIMULATE_STREAMING_BATCH` | Procedure | Generates synthetic Kinesis-style events |
| `STREAMING_SIMULATOR_TASK` | Task | 1-min cadence; resume during demo for live ingestion |
| `DT_CERTS_CLEANED` | Dynamic Table | SCD Type 1 dedup, incremental refresh |
| `DT_CERTS_ENRICHED` | Dynamic Table | Joined to PARTNERS, base compliance flags |
| `DT_COMPLIANCE_DASHBOARD` | Dynamic Table | Gold aggregations, 5-min lag |
| `V_CERTIFICATES_FULL` | View | Time-aware compliance status over 50M base table |
| `V_CERTIFICATES_LIVE` | View | Time-aware view over enriched DT |
| `CERT_COMPLIANCE_SV` | Semantic View | Cortex Analyst entry point |
| `CERT_COMPLIANCE_SEARCH` | Cortex Search Service | RAG over compliance docs |
| `CERT_COMPLIANCE_AGENT` | Cortex Agent | Orchestrates both tools |
| `APP_REPO` | Image Repo | Hosts the React app container |
| `COMCAST_CERT_APP_POOL` | Compute Pool | Runs the SPCS service (CPU_X64_XS) |
| `CERT_OLTP_DB` | Postgres Instance | OLTP coexistence demo |

## Demo Flow (40-50 min, fits 1-hour slot)

### 1. Open with scale (3 min)
```sql
SELECT COUNT(*) FROM COMCAST_CYBER_DEMO.CERT_SECURITY.CERTIFICATES;
-- 50,000,000

SELECT compliance_status, COUNT(*)
FROM COMCAST_CYBER_DEMO.CERT_SECURITY.V_CERTIFICATES_FULL
GROUP BY 1;
```
Talk to: this represents a snapshot of their billion-cert estate; shows immediate distribution by compliance.

### 2. Live streaming ingestion (5 min)
```sql
ALTER TASK COMCAST_CYBER_DEMO.CERT_SECURITY.STREAMING_SIMULATOR_TASK RESUME;
SELECT COUNT(*), MAX(event_timestamp)
FROM COMCAST_CYBER_DEMO.CERT_SECURITY.RAW_CERTIFICATE_EVENTS;
-- Re-run every 30s to show growth
```
Talk to: in production this would be Snowpipe Streaming SDK from Kinesis -- 10 GB/s throughput, 5-second latency, exactly-once delivery, in-flight transformations via PIPE objects.

### 3. Dynamic Table pipeline (8 min)
```sql
SHOW DYNAMIC TABLES IN SCHEMA COMCAST_CYBER_DEMO.CERT_SECURITY;
SELECT * FROM COMCAST_CYBER_DEMO.CERT_SECURITY.DT_COMPLIANCE_DASHBOARD LIMIT 20;
```
Talk to: medallion architecture, incremental refresh, no orchestrator needed, declarative SQL replaces their Postgres ETL.

### 4. AI chat over data (12 min) -- THE MONEY SHOT
Open the React app's public URL. Ask in this order:
1. "How many certificates are expiring in the next 30 days?" -- shows Cortex Analyst, generated SQL, real numbers
2. "Which partners have the most non-compliant certificates?" -- shows aggregation, partner names
3. "What is our policy for self-signed certificates?" -- shows Cortex Search citing DOC-001 and DOC-003
4. "How do I remediate one?" -- multi-turn, builds on prior context, returns runbook
5. "Show me streaming-region compliance and the relevant standard" -- combined Analyst+Search

Show the "Generated SQL" expander -- proves transparency.

### 5. API access (5 min)
Show the `/api/chat/route.ts` server-side code calling `agents/{name}:run` REST endpoint with the SPCS-mounted OAuth token. Same call works from any app -- React, Slack, Teams, Salesforce, anything they can wire up.

### 6. Postgres coexistence (5 min)
```sql
SHOW POSTGRES INSTANCES;
DESCRIBE POSTGRES INSTANCE CERT_OLTP_DB;
```
Show the connection string. Mention: OLTP transactional cert lookups + OLAP analytics + AI all on one platform, no cross-vendor data movement.

### 7. Roadmap (2 min)
- Phase 1 (now): Set up trial account, ingest a sample of cert data, prove AI chat works for leadership
- Phase 2 (90 days): Full streaming ingestion, more verified queries, integrate into existing tools
- Phase 3 (6 mo): Migrate Postgres workload to Snowflake Postgres, unified platform

## Deployment Steps (already executed except SPCS image push)

```bash
# All Snowflake objects: see /sql/setup.sql (run in DHALL_AWS1)

# React app (run from app/):
cd app/
./deploy.sh   # builds image, pushes to APP_REPO, creates SPCS service
```

After SPCS service starts, get the public URL:
```sql
SHOW ENDPOINTS IN SERVICE COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_CHAT_SERVICE;
```

## Pre-demo Checklist

- [ ] Resume `STREAMING_SIMULATOR_TASK` ~10 min before the call (so there's data already arriving)
- [ ] Test the React app URL from a fresh browser
- [ ] Test 2-3 sample questions through the agent to warm models / verify
- [ ] Have Snowsight tabs open: Cortex Analyst playground on the semantic view, Search playground on the search service, Agent details page
- [ ] Have a backup tab with raw SQL examples in case the chat app misbehaves

## Notes on Production Hardening (talking points if asked)

- Streaming simulator -> real Snowpipe Streaming Java/Python SDK driven from Kinesis Firehose subscriber
- Add row access policies on `CERTIFICATES` for partner data isolation
- Add masking policies for `serial_number`, `subject_cn` if PII concerns
- Wrap agent in a custom role with `CORTEX_AGENT_USER` only -- no broad table access needed
- Tag-based classification for sensitive fields, surface in Trust Center
- Add CT log integration via external function for live cert lookups
