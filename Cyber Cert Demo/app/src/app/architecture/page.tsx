'use client';
import { useState } from 'react';
import { X } from 'lucide-react';

const LAYERS = [
  {
    id: 'sources',
    title: 'SOURCES',
    badge: 'Millions/day',
    color: '#7c3aed',
    items: ['Snowflake Postgres (OLTP)', 'Kinesis IoT Stream', 'DynamoDB CDC', 'Scanner API', 'ACME Auto-Renewal'],
    detail: {
      summary: 'Operational data sources feeding certificate telemetry into the Snowflake platform. Comcast manages over 1 billion X.509 certificates across IoT devices, streaming infrastructure, gateways, and partner networks. Certificates are issued at a rate of millions per day from multiple sources.',
      workflow: 'In this demo, the primary OLTP source is a Snowflake Postgres instance (CERT_OLTP_DB) handling active certificate management — CSR queues, real-time revocation requests, and certificate lifecycle operations. IoT devices emit certificate events via Kinesis at 5M events/minute, while network scanners continuously discover certificates across the infrastructure.',
      sql: `-- Snowflake Postgres instance (STANDARD_M, PostgreSQL 18)
CREATE POSTGRES INSTANCE CERT_OLTP_DB
  COMPUTE_FAMILY = STANDARD_M
  STORAGE_SIZE = 10;

-- Tables in Postgres: active_certificates, csr_queue, revocation_log`,
      features: [
        { name: 'Snowflake Postgres', desc: 'Fully managed PostgreSQL 18 instance running inside Snowflake with full SQL compatibility and extensions (pg_lake, PostGIS).', fab: { feature: 'Native PostgreSQL inside Snowflake', advantage: 'No migration required — your existing Postgres code, ORMs, and tools work unchanged', benefit: 'Run OLTP certificate operations (<5ms) and OLAP analytics on one platform, eliminating data movement and infrastructure management' }, link: 'https://docs.snowflake.com/en/sql-reference/sql/create-postgres-instance' },
        { name: 'Snowpipe Streaming', desc: 'High-performance streaming ingestion SDK delivering 10 GB/s throughput with exactly-once delivery and sub-5-second latency.', fab: { feature: 'Channel-based streaming with insertRows() API', advantage: 'No staging files, no Kafka cluster, no custom ETL — direct SDK integration', benefit: 'Replace your Kinesis → Lambda → S3 → COPY INTO pipeline with a single API call at millions of events/minute' }, link: 'https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-overview' },
        { name: 'Openflow CDC Connector', desc: 'Managed connector for continuous Change Data Capture from external Postgres/DynamoDB via WAL replication.', fab: { feature: 'Managed CDC with WAL-based logical replication', advantage: 'Schema evolution, soft-delete semantics, and exactly-once delivery without custom code', benefit: 'Continuously replicate external Aurora/RDS changes to Snowflake without maintaining replication infrastructure' }, link: 'https://docs.snowflake.com/en/user-guide/data-integration/openflow/' },
      ]
    }
  },
  {
    id: 'mirror',
    title: 'MIRROR',
    badge: '~30s lag',
    color: '#0066cc',
    items: ['Shared Iceberg (pg_lake)', 'Catalog Integration', 'Zero-infra CDC', 'Auto-refresh 30s', 'Vended credentials'],
    detail: {
      summary: 'The mirroring layer provides zero-infrastructure data movement from Postgres to Snowflake using pg_lake\'s Shared Iceberg pattern. Postgres writes Apache Iceberg tables that Snowflake reads through a catalog integration with approximately 30-second lag. No S3 buckets, IAM roles, or external connectors needed.',
      workflow: 'When data changes in Postgres, the pg_lake extension writes Iceberg metadata and Parquet data files to Snowflake-managed storage. Snowflake polls the catalog every 30 seconds (configurable via REFRESH_INTERVAL_SECONDS) to detect new snapshots. The catalog integration uses vended credentials — Snowflake automatically handles authentication without any customer-managed IAM configuration.',
      sql: `-- In Postgres: enable pg_lake and create Iceberg table
CREATE EXTENSION pg_lake CASCADE;
CREATE TABLE cert_events (...) USING iceberg;

-- In Snowflake: create catalog integration
CREATE CATALOG INTEGRATION CERT_POSTGRES_CATALOG
  CATALOG_SOURCE = SNOWFLAKE_POSTGRES
  TABLE_FORMAT = ICEBERG
  REST_CONFIG = (
    POSTGRES_INSTANCE = 'CERT_OLTP_DB'
    ACCESS_DELEGATION_MODE = VENDED_CREDENTIALS
  )
  ENABLED = TRUE;

-- Create Iceberg table reference (auto-refreshes every 30s)
CREATE ICEBERG TABLE CERT_EVENTS_MIRROR
  CATALOG = 'CERT_POSTGRES_CATALOG'
  CATALOG_TABLE_NAME = 'cert_events'
  AUTO_REFRESH = TRUE;`,
      features: [
        { name: 'pg_lake Extension', desc: 'Postgres extension that creates Apache Iceberg tables directly inside Postgres, stored in Snowflake-managed object storage.', fab: { feature: 'Postgres writes Iceberg; Snowflake reads Iceberg', advantage: 'Zero infrastructure — no S3 buckets, no IAM roles, no external connectors to configure', benefit: 'Your OLTP Postgres data appears in Snowflake within 30 seconds with zero operational overhead' }, link: 'https://docs.snowflake.com/en/user-guide/snowflake-postgres/postgres-pg_lake' },
        { name: 'Catalog Integration (SNOWFLAKE_POSTGRES)', desc: 'Catalog integration connecting Snowflake to Postgres Iceberg tables with vended credentials and auto-refresh.', fab: { feature: 'Auto-refresh catalog polling every 30 seconds', advantage: 'Snowflake handles all storage access automatically — no credential rotation or IAM management', benefit: 'Always-current analytical views of OLTP data without any pipeline code or scheduling' }, link: 'https://docs.snowflake.com/en/sql-reference/sql/create-catalog-integration-snowflake-postgres' },
        { name: 'Databricks Unity Catalog (Coexistence)', desc: 'Same Iceberg REST catalog pattern works with Databricks Unity Catalog for bidirectional table access.', fab: { feature: 'Catalog-linked databases with auto-discovery from Unity Catalog', advantage: 'Read AND write Databricks-managed Iceberg tables — no migration required', benefit: 'Run Snowflake AI/analytics alongside existing Databricks workloads without duplicating data' }, link: 'https://docs.snowflake.com/en/user-guide/tutorials/tables-iceberg-set-up-bidirectional-access-to-unity-catalog' },
      ]
    }
  },
  {
    id: 'interactive-table',
    title: 'INTERACTIVE TABLE',
    badge: '1-min refresh',
    color: '#059669',
    items: ['CLUSTER BY (region, status)', 'Auto-refresh 1-min lag', 'Pre-aggregated 50M→21K', 'Incremental processing', 'Medallion architecture'],
    detail: {
      summary: 'Interactive Tables are purpose-built for sub-second analytical queries. In this demo, 50 million raw certificates are pre-aggregated into ~21,000 grouped rows (by region, device type, partner, algorithm, and compliance status), clustered by the two most common filter columns for optimal partition pruning.',
      workflow: 'The raw CERTIFICATES table (50M rows) feeds through a medallion architecture: Dynamic Tables clean and deduplicate the data (bronze→silver), then enrich it with partner dimensions (silver→gold). The Interactive Table sources from this pipeline with a 1-minute TARGET_LAG — Snowflake automatically refreshes it using the designated warehouse, keeping data fresh within 60 seconds of any upstream change.',
      sql: `-- Create Interactive Table (pre-aggregated for sub-second queries)
CREATE INTERACTIVE TABLE CERT_COMPLIANCE_INTERACTIVE
  CLUSTER BY (region, compliance_status)
  TARGET_LAG = '1 minute'
  WAREHOUSE = COMCAST_DEMO_WH
AS
  SELECT region, device_type, partner_name, key_algorithm,
    compliance_status, COUNT(*) AS cert_count,
    SUM(CASE WHEN is_self_signed THEN 1 ELSE 0 END) AS self_signed_count
  FROM CERTIFICATES c
  LEFT JOIN PARTNERS p ON c.partner_name = p.partner_name
  GROUP BY ALL;

-- Result: 50M rows → 21K pre-aggregated rows
-- Clustered by (region, compliance_status) for pruning`,
      features: [
        { name: 'CREATE INTERACTIVE TABLE', desc: 'Table optimized for low-latency, high-concurrency workloads with mandatory CLUSTER BY and automatic refresh.', fab: { feature: 'Declarative clustered table with TARGET_LAG auto-refresh', advantage: 'No materialized view maintenance, no cron jobs, no manual refresh — Snowflake handles it all', benefit: '50M raw rows → 21K pre-aggregated rows, always fresh within 60 seconds, queried in under 100ms' }, link: 'https://docs.snowflake.com/en/sql-reference/sql/create-interactive-table' },
        { name: 'Clustering & Partition Pruning', desc: 'CLUSTER BY (region, compliance_status) sorts data for optimal partition pruning on common filter patterns.', fab: { feature: 'Automatic micro-partition organization by specified keys', advantage: 'Queries only scan relevant partitions — not full table scans', benefit: 'WHERE region = "NA" AND status = "NON_COMPLIANT" touches <1% of data → sub-100ms response' }, link: 'https://docs.snowflake.com/en/user-guide/tables-clustering-keys' },
        { name: 'Dynamic Tables (Medallion)', desc: 'Declarative SQL pipelines with TARGET_LAG for automatic scheduling and dependency resolution.', fab: { feature: 'Write SQL once — Snowflake manages scheduling, ordering, and incremental refresh', advantage: 'No Airflow, no dbt scheduling, no dependency DAG configuration', benefit: 'Bronze → Silver → Gold pipeline that self-heals, auto-retries, and requires zero operational maintenance' }, link: 'https://docs.snowflake.com/en/user-guide/dynamic-tables-about' },
      ]
    }
  },
  {
    id: 'iwh',
    title: 'INTERACTIVE WH',
    badge: '<100ms',
    color: '#0891b2',
    items: ['CERT_COMPLIANCE_IWH', 'Sub-second queries', '5s hard timeout', 'Fallback warehouse', 'Cache warming'],
    detail: {
      summary: 'The Interactive Warehouse is an always-on, pre-cached compute resource that delivers sub-100ms query responses by keeping the Interactive Table\'s data in local SSD cache. It enforces a 5-second hard timeout to prevent long-running queries from degrading latency, with automatic fallback to a standard warehouse for complex queries.',
      workflow: 'When the Interactive Warehouse resumes, it begins cache warming — loading the CERT_COMPLIANCE_INTERACTIVE table into local storage at ~300-400 MB/s. Once warm, queries hit 0% remote read. The dashboard API routes KPI queries through CERT_COMPLIANCE_IWH for sub-second responses. If any query exceeds 5 seconds (complex joins, non-clustered filters), it automatically retries on COMCAST_DEMO_WH (standard LARGE warehouse) transparently.',
      sql: `-- Create Interactive Warehouse with table association
CREATE INTERACTIVE WAREHOUSE CERT_COMPLIANCE_IWH
  TABLES (CERT_COMPLIANCE_INTERACTIVE)
  WAREHOUSE_SIZE = 'XSMALL';

-- Resume (starts cache warming)
ALTER WAREHOUSE CERT_COMPLIANCE_IWH RESUME;

-- Set fallback for queries exceeding 5s timeout
ALTER WAREHOUSE CERT_COMPLIANCE_IWH
  SET FALLBACK_WAREHOUSE = COMCAST_DEMO_WH;

-- Sub-second query example:
USE WAREHOUSE CERT_COMPLIANCE_IWH;
SELECT region, compliance_status, SUM(cert_count)
FROM CERT_COMPLIANCE_INTERACTIVE
WHERE region = 'NA'
GROUP BY 1, 2; -- < 100ms`,
      features: [
        { name: 'CREATE INTERACTIVE WAREHOUSE', desc: 'Always-on compute dedicated to serving Interactive Tables with data pre-loaded into local SSD cache.', fab: { feature: 'SSD-cached compute with 24-hour minimum suspend and multi-cluster scaling', advantage: 'Data stays hot — no cold-start latency, no cache misses on first query', benefit: 'Every dashboard refresh returns in <100ms regardless of concurrency (10+ simultaneous users)' }, link: 'https://docs.snowflake.com/en/sql-reference/sql/create-interactive-warehouse' },
        { name: 'Fallback Warehouse', desc: 'Automatic transparent retry on a standard warehouse when queries exceed the 5-second Interactive timeout.', fab: { feature: 'SET FALLBACK_WAREHOUSE provides automatic overflow handling', advantage: 'No application code changes — complex queries seamlessly route to larger compute', benefit: 'Fast queries stay fast; complex ad-hoc queries still work without errors or timeouts' }, link: 'https://docs.snowflake.com/en/user-guide/interactive#automatically-handling-statement-timeouts' },
        { name: 'Cache Warming & Performance', desc: 'XS warehouse warms at ~300-400 MB/s, keeping working set fully cached on local SSD.', fab: { feature: '0% remote reads when fully warmed — all data served from local NVMe SSD', advantage: 'Eliminates network latency to remote storage on every query', benefit: 'Consistent sub-100ms P99 latency for dashboard KPIs serving leadership in real-time' }, link: 'https://docs.snowflake.com/en/user-guide/interactive#choosing-a-size-for-an-interactive-warehouse' },
      ]
    }
  },
  {
    id: 'cortex',
    title: 'CORTEX AI',
    badge: '5 tools',
    color: '#d97706',
    items: ['Cortex Agent (orchestrator)', '3 Semantic Views', 'Cortex Search (RAG)', 'ML Forecast model', 'Verified Queries'],
    detail: {
      summary: 'The AI layer uses a Cortex Agent that orchestrates 5 tools: three Cortex Analyst semantic views (fast dashboard, detailed analytics, policy rules), a Cortex Search service for RAG over compliance documents, and a chain resolution tool. The agent plans which tools to use based on the question, executes SQL, and synthesizes a natural language response.',
      workflow: 'User asks a question → Agent analyzes intent → Selects tool(s): cert_dashboard (IWH, sub-second) for KPI questions, cert_analytics (50M rows) for drill-downs, policy_rules for compliance definitions, cert_chains for trust chain queries, compliance_docs_search for policy documents → Executes query → Synthesizes response with data + narrative.',
      sql: `-- Agent with 5 tools
CREATE AGENT CERT_COMPLIANCE_AGENT
  COMMENT = 'Certificate compliance AI agent';

-- Tool 1: cert_dashboard (Interactive Table via IWH)
--   Semantic View: CERT_DASHBOARD_SV + 5 Verified Queries
--   Execution: CERT_COMPLIANCE_IWH (sub-second)

-- Tool 2: cert_analytics (Full 50M inventory)
--   Semantic View: CERT_COMPLIANCE_SV (18 dims, 11 metrics)
--   Execution: COMCAST_DEMO_WH

-- Tool 3: policy_rules (Compliance definitions)
--   Semantic View: CERT_POLICY_RULES_SV

-- Tool 4: cert_chains (Trust chain resolution)
--   Semantic View: CERT_CHAIN_SV (3 tables joined)

-- Tool 5: compliance_docs_search (RAG)
--   Cortex Search over 10 compliance documents`,
      features: [
        { name: 'Cortex Agent', desc: 'AI orchestrator that plans tool usage, executes queries, reflects on results, and generates comprehensive responses.', fab: { feature: 'Multi-tool orchestrator with session context, streaming SSE, and REST/MCP access', advantage: 'One agent handles SQL generation, policy lookup, and chain analysis — no prompt chaining required', benefit: 'Leadership asks plain English questions; engineers get API access — both get accurate, governed answers from the same agent' }, link: 'https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents' },
        { name: 'Semantic Views + Verified Queries', desc: 'Business-friendly schema (dimensions, metrics, synonyms) with pre-validated SQL for common questions.', fab: { feature: 'Declarative semantic layer with VQRs that bypass LLM generation for known patterns', advantage: 'Verified queries return in <1s (no LLM call); unverified questions still work via generation', benefit: 'Consistent, accurate SQL for your most important questions — with flexibility for ad-hoc exploration' }, link: 'https://docs.snowflake.com/en/user-guide/views-semantic/sql' },
        { name: 'Cortex Search (RAG)', desc: 'Hybrid vector + keyword search over compliance documents, runbooks, and audit findings.', fab: { feature: 'Built-in embedding, indexing, and retrieval — no external vector DB needed', advantage: 'Documents stay inside Snowflake governance — no data leaving the security perimeter', benefit: 'Questions about policies, procedures, and remediation get accurate answers grounded in your actual documentation' }, link: 'https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview' },
      ]
    }
  },
  {
    id: 'app',
    title: 'APP (SPCS)',
    badge: 'Public URL',
    color: '#dc2626',
    items: ['React/Next.js (standalone)', 'SSE streaming UI', '11 interactive pages', 'OAuth (SPCS-mounted)', 'Docker on CPU_X64_XS'],
    detail: {
      summary: 'A Next.js 14 React application deployed to Snowpark Container Services (SPCS). Runs as a Docker container with a public HTTPS endpoint, Snowflake-managed OAuth authentication, and direct access to all Snowflake APIs. Every data element is clickable for AI-powered drill-down investigation.',
      workflow: 'User opens the public URL → Snowflake authenticates via OAuth → App loads dashboard from Interactive Table (sub-second) → User clicks a data element → DrilldownPanel sends question to Agent via /api/chat → Agent streams response via SSE → Text appears incrementally → User clicks drill-down pills for follow-up analysis.',
      sql: `-- SPCS Service Deployment
CREATE SERVICE CERT_CHAT_SERVICE
  IN COMPUTE POOL COMCAST_CERT_APP_POOL
  FROM SPECIFICATION $$
spec:
  containers:
    - name: web
      image: .../cert-chat:v5
      resources:
        limits: { cpu: 2, memory: 2G }
  endpoints:
    - name: app
      port: 3000
      public: true
$$;

-- Key: HOSTNAME=0.0.0.0 in Dockerfile (Next.js standalone)
-- Auth: /snowflake/session/token (auto-mounted OAuth)
-- Host: SNOWFLAKE_HOST env var (injected by SPCS)`,
      features: [
        { name: 'Snowpark Container Services (SPCS)', desc: 'Run any Docker container directly inside Snowflake with public HTTPS endpoints and auto-managed OAuth.', fab: { feature: 'Full Docker containers with public endpoints, GPU/CPU pools, and injected credentials', advantage: 'No AWS/GCP infrastructure to manage — your app runs inside Snowflake\'s security perimeter', benefit: 'Deploy a production React app with AI chat in minutes — zero DevOps, automatic auth, direct API access to all Snowflake services' }, link: 'https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview' },
        { name: 'Streaming Agent UI', desc: 'SSE streaming for token-by-token response rendering with pre-cached seed responses for instant demo flow.', fab: { feature: 'Server-Sent Events streaming with seed cache + background prefetch', advantage: 'First-click responses render instantly; follow-up drilldowns prefetch in background', benefit: 'Users perceive instant AI responses — no 10-second wait for the first answer, maintaining engagement' }, link: 'https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents' },
        { name: 'SQL API + Interactive Warehouse', desc: 'Dashboard KPI queries route through SQL API to CERT_COMPLIANCE_IWH for sub-second latency.', fab: { feature: 'REST SQL API with intelligent warehouse routing per query type', advantage: 'KPIs via IWH (<100ms), complex joins via standard WH — automatic selection', benefit: 'Every page loads instantly without users knowing which compute serves which query' }, link: 'https://docs.snowflake.com/en/developer-guide/sql-api/reference' },
      ]
    }
  },
];

export default function ArchitecturePage() {
  const [selected, setSelected] = useState<string | null>(null);
  const activeLayer = LAYERS.find(l => l.id === selected);

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease', overflowX: 'auto' }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Platform Architecture</h1>
      <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 32 }}>End-to-end data flow • <span style={{ color: '#0066cc' }}>Click any layer for detailed explanation</span></p>

      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 0, minWidth: 1400, paddingBottom: 16 }}>
        {LAYERS.map((layer, idx) => (
          <div key={layer.id} style={{ display: 'flex', alignItems: 'flex-start' }}>
            <LayerCard layer={layer} active={selected === layer.id} onClick={() => setSelected(selected === layer.id ? null : layer.id)} />
            {idx < LAYERS.length - 1 && <FlowArrow />}
          </div>
        ))}
      </div>

      {activeLayer && (
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, padding: 28, marginTop: 20, boxShadow: '0 4px 12px rgba(0,0,0,0.06)', animation: 'fadeIn 0.2s ease', position: 'relative', borderTop: `4px solid ${activeLayer.color}` }}>
          <button onClick={() => setSelected(null)} style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af' }}><X size={18} /></button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <span style={{ fontSize: 10, padding: '3px 10px', borderRadius: 10, background: activeLayer.color, color: '#fff', fontWeight: 600, letterSpacing: '0.5px' }}>{activeLayer.title}</span>
            <span style={{ fontSize: 10, color: '#9ca3af' }}>{activeLayer.badge}</span>
          </div>

          <p style={{ fontSize: 14, color: '#374151', lineHeight: 1.7, marginBottom: 16 }}>{activeLayer.detail.summary}</p>

          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: 16, marginBottom: 20 }}>
            <h4 style={{ fontSize: 12, fontWeight: 600, color: '#0066cc', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>How It Works in This Demo</h4>
            <p style={{ fontSize: 13, color: '#4b5563', lineHeight: 1.7 }}>{activeLayer.detail.workflow}</p>
          </div>

          {activeLayer.detail.sql && (
            <details style={{ marginBottom: 20 }}>
              <summary style={{ fontSize: 12, color: '#0066cc', cursor: 'pointer', fontWeight: 600, marginBottom: 8 }}>View SQL / Configuration</summary>
              <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: 16, borderRadius: 8, fontSize: 11, overflow: 'auto', maxHeight: 300, lineHeight: 1.6 }}>{activeLayer.detail.sql}</pre>
            </details>
          )}

          <h4 style={{ fontSize: 13, fontWeight: 600, color: '#111827', marginBottom: 12 }}>Snowflake Capabilities — Feature, Advantage, Benefit</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14 }}>
            {activeLayer.detail.features.map((f: any, i: number) => (
              <div key={i} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: 16 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: activeLayer.color, marginBottom: 6 }}>{f.name}</div>
                <p style={{ fontSize: 12, color: '#4b5563', lineHeight: 1.6, marginBottom: 10 }}>{f.desc}</p>
                {f.fab && (
                  <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: 10, marginTop: 8 }}>
                    <div style={{ fontSize: 11, lineHeight: 1.7 }}>
                      <div style={{ marginBottom: 4 }}><span style={{ fontWeight: 700, color: '#0066cc', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Feature:</span> <span style={{ color: '#374151' }}>{f.fab.feature}</span></div>
                      <div style={{ marginBottom: 4 }}><span style={{ fontWeight: 700, color: '#059669', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Advantage:</span> <span style={{ color: '#374151' }}>{f.fab.advantage}</span></div>
                      <div><span style={{ fontWeight: 700, color: '#d97706', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Benefit:</span> <span style={{ color: '#374151' }}>{f.fab.benefit}</span></div>
                    </div>
                  </div>
                )}
                <a href={f.link} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-block', marginTop: 10, fontSize: 11, color: '#0066cc', textDecoration: 'none', fontWeight: 500 }}>Documentation →</a>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 32, padding: 20, background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
        <h3 style={{ fontSize: 15, color: '#374151', marginBottom: 12, fontWeight: 600 }}>Key Snowflake Objects</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, fontSize: 13 }}>
          {[
            ['CERT_OLTP_DB', 'Postgres OLTP instance', '#7c3aed'],
            ['CERT_POSTGRES_CATALOG', 'Catalog integration (pg_lake)', '#0066cc'],
            ['CERT_COMPLIANCE_INTERACTIVE', 'Interactive Table (clustered)', '#059669'],
            ['CERT_COMPLIANCE_IWH', 'Interactive Warehouse', '#0891b2'],
            ['CERT_COMPLIANCE_AGENT', 'Cortex Agent (5 tools)', '#d97706'],
            ['CERT_CHAT_SERVICE', 'SPCS React app (v5)', '#dc2626'],
          ].map(([obj, desc, color], i) => (
            <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <div style={{ width: 9, height: 9, borderRadius: '50%', background: color, flexShrink: 0 }} />
              <code style={{ background: '#f8fafc', padding: '4px 10px', borderRadius: 5, color: '#334155', fontSize: 12, border: '1px solid #e2e8f0', fontWeight: 500 }}>{obj}</code>
              <span style={{ color: '#6b7280', fontSize: 12 }}>{desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function LayerCard({ layer, active, onClick }: { layer: typeof LAYERS[0]; active: boolean; onClick: () => void }) {
  return (
    <div onClick={onClick} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 200, flexShrink: 0, cursor: 'pointer', transition: 'all 0.15s' }}>
      <div style={{
        width: 78, height: 78, borderRadius: 20, background: active ? `${layer.color}15` : `${layer.color}06`, border: `2.5px solid ${active ? layer.color : layer.color + '30'}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10, transition: 'all 0.15s', boxShadow: active ? `0 6px 16px ${layer.color}25` : '0 2px 6px rgba(0,0,0,0.03)'
      }}>
        <LayerIcon id={layer.id} color={layer.color} />
      </div>
      <div style={{ fontSize: 14, fontWeight: 700, color: active ? layer.color : '#374151', marginBottom: 5, letterSpacing: '0.5px' }}>{layer.title}</div>
      <div style={{ fontSize: 10, color: '#fff', background: layer.color, borderRadius: 12, padding: '3px 10px', marginBottom: 10, fontWeight: 600 }}>{layer.badge}</div>
      <div style={{
        background: active ? '#eff6ff' : '#fff', border: `1px solid ${active ? '#0066cc' : '#e2e8f0'}`, borderRadius: 10, padding: '12px 14px',
        width: '100%', boxShadow: active ? '0 2px 8px rgba(0,102,204,0.08)' : '0 1px 3px rgba(0,0,0,0.04)', borderTop: `3px solid ${layer.color}`, transition: 'all 0.15s'
      }}>
        {layer.items.map((item, i) => (
          <div key={i} style={{ fontSize: 12, color: '#374151', padding: '4px 0', display: 'flex', alignItems: 'center', gap: 6, borderBottom: i < layer.items.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
            <div style={{ width: 5, height: 5, borderRadius: 3, background: layer.color, flexShrink: 0 }} />
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function FlowArrow() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', paddingTop: 30, flexShrink: 0, width: 44 }}>
      <svg width="44" height="20" viewBox="0 0 44 20">
        <path d="M4 10 L30 10" stroke="#94a3b8" strokeWidth="2" fill="none" strokeDasharray="4 3" />
        <path d="M28 5 L38 10 L28 15" fill="#0066cc" opacity="0.7" />
      </svg>
    </div>
  );
}

function LayerIcon({ id, color }: { id: string; color: string }) {
  const s = 38;
  switch (id) {
    case 'sources': return (
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
        <ellipse cx="20" cy="10" rx="12" ry="4" stroke={color} strokeWidth="1.8" fill={color} fillOpacity="0.08" />
        <path d="M8 10 L8 30 C8 32.2 13.4 34 20 34 C26.6 34 32 32.2 32 30 L32 10" stroke={color} strokeWidth="1.8" fill="none" />
        <ellipse cx="20" cy="30" rx="12" ry="4" stroke={color} strokeWidth="1.2" strokeDasharray="2 2" fill="none" />
        <path d="M8 17 C8 19.2 13.4 21 20 21 C26.6 21 32 19.2 32 17" stroke={color} strokeWidth="1.2" fill="none" />
        <path d="M8 24 C8 26.2 13.4 28 20 28 C26.6 28 32 26.2 32 24" stroke={color} strokeWidth="1.2" fill="none" />
        <circle cx="30" cy="10" r="3" fill={color} fillOpacity="0.3" stroke={color} strokeWidth="1" />
        <path d="M29 10 L30 11 L32 9" stroke={color} strokeWidth="1" strokeLinecap="round" />
      </svg>
    );
    case 'mirror': return (
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
        <path d="M8 14 L20 6 L32 14 L32 26 L20 34 L8 26 Z" stroke={color} strokeWidth="1.8" fill={color} fillOpacity="0.06" />
        <path d="M20 6 L20 34" stroke={color} strokeWidth="1" strokeDasharray="2 2" />
        <path d="M8 14 L32 14" stroke={color} strokeWidth="1" strokeDasharray="2 2" />
        <path d="M8 26 L32 26" stroke={color} strokeWidth="1" strokeDasharray="2 2" />
        <circle cx="20" cy="20" r="4" fill={color} fillOpacity="0.15" stroke={color} strokeWidth="1.5" />
        <path d="M18 20 L19.5 21.5 L22 19" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M3 20 L7 20" stroke={color} strokeWidth="2" strokeLinecap="round" markerEnd="url(#arrow)" />
        <path d="M33 20 L37 20" stroke={color} strokeWidth="2" strokeLinecap="round" />
        <polygon points="37,20 34,18 34,22" fill={color} />
        <polygon points="3,20 6,18 6,22" fill={color} />
      </svg>
    );
    case 'interactive-table': return (
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
        <rect x="5" y="8" width="30" height="24" rx="3" stroke={color} strokeWidth="1.8" fill={color} fillOpacity="0.04" />
        <rect x="5" y="8" width="30" height="7" rx="3" fill={color} fillOpacity="0.12" stroke={color} strokeWidth="1.8" />
        <path d="M5 15 L35 15" stroke={color} strokeWidth="1.2" />
        <path d="M5 21 L35 21" stroke={color} strokeWidth="0.8" opacity="0.5" />
        <path d="M5 27 L35 27" stroke={color} strokeWidth="0.8" opacity="0.5" />
        <path d="M16 8 L16 32" stroke={color} strokeWidth="0.8" opacity="0.5" />
        <path d="M27 8 L27 32" stroke={color} strokeWidth="0.8" opacity="0.5" />
        <circle cx="31" cy="11.5" r="2.5" fill={color} fillOpacity="0.3" stroke={color} strokeWidth="1" />
        <path d="M30 11.5 L30.8 12.3 L32.5 10.5" stroke="#fff" strokeWidth="1.2" strokeLinecap="round" />
      </svg>
    );
    case 'iwh': return (
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
        <circle cx="20" cy="20" r="14" stroke={color} strokeWidth="1.8" fill={color} fillOpacity="0.04" />
        <circle cx="20" cy="20" r="8" stroke={color} strokeWidth="1.5" fill={color} fillOpacity="0.08" />
        <circle cx="20" cy="20" r="3" fill={color} fillOpacity="0.3" />
        <path d="M20 6 L20 12" stroke={color} strokeWidth="2" strokeLinecap="round" />
        <path d="M20 28 L20 34" stroke={color} strokeWidth="2" strokeLinecap="round" />
        <path d="M6 20 L12 20" stroke={color} strokeWidth="2" strokeLinecap="round" />
        <path d="M28 20 L34 20" stroke={color} strokeWidth="2" strokeLinecap="round" />
        <path d="M10 10 L13.5 13.5" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
        <path d="M26.5 26.5 L30 30" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
        <path d="M30 10 L26.5 13.5" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
        <path d="M13.5 26.5 L10 30" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    );
    case 'cortex': return (
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
        <path d="M20 4 L23 15 L34 12 L25 20 L34 28 L23 25 L20 36 L17 25 L6 28 L15 20 L6 12 L17 15 Z" stroke={color} strokeWidth="1.8" fill={color} fillOpacity="0.08" strokeLinejoin="round" />
        <circle cx="20" cy="20" r="5" fill={color} fillOpacity="0.15" stroke={color} strokeWidth="1.5" />
        <circle cx="20" cy="20" r="2" fill={color} fillOpacity="0.4" />
        <circle cx="20" cy="4" r="2" fill={color} />
        <circle cx="34" cy="12" r="1.5" fill={color} fillOpacity="0.6" />
        <circle cx="34" cy="28" r="1.5" fill={color} fillOpacity="0.6" />
        <circle cx="20" cy="36" r="2" fill={color} />
        <circle cx="6" cy="12" r="1.5" fill={color} fillOpacity="0.6" />
        <circle cx="6" cy="28" r="1.5" fill={color} fillOpacity="0.6" />
      </svg>
    );
    case 'app': return (
      <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
        <rect x="6" y="4" width="28" height="28" rx="4" stroke={color} strokeWidth="1.8" fill={color} fillOpacity="0.04" />
        <rect x="6" y="4" width="28" height="6" rx="4" fill={color} fillOpacity="0.12" stroke={color} strokeWidth="1.8" />
        <circle cx="10" cy="7" r="1.2" fill={color} />
        <circle cx="13.5" cy="7" r="1.2" fill={color} />
        <circle cx="17" cy="7" r="1.2" fill={color} />
        <rect x="9" y="13" width="10" height="7" rx="2" fill={color} fillOpacity="0.1" stroke={color} strokeWidth="1" />
        <rect x="9" y="23" width="22" height="2" rx="1" fill={color} fillOpacity="0.15" />
        <rect x="9" y="27" width="16" height="2" rx="1" fill={color} fillOpacity="0.1" />
        <rect x="22" y="13" width="9" height="3" rx="1.5" fill={color} fillOpacity="0.2" stroke={color} strokeWidth="0.8" />
        <rect x="22" y="18" width="9" height="2" rx="1" fill={color} fillOpacity="0.1" />
        <path d="M17 34 L23 34" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
        <path d="M20 32 L20 35" stroke={color} strokeWidth="1.8" />
      </svg>
    );
    default: return null;
  }
}
