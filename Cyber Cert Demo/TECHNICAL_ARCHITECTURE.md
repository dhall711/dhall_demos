# Comcast GCS Certificate Compliance Demo — Technical Architecture

## Overview

The Certificate Compliance Demo is an end-to-end Snowflake platform demonstration built for Comcast's GCS Cybersecurity team (Sajit's group). It showcases how Snowflake can serve as the unified platform for certificate lifecycle management — from OLTP workloads via Snowflake Postgres, through near-real-time mirroring and transformation, to AI-powered natural language analytics via Cortex Agent.

The application manages and analyzes **50 million+ X.509 certificates** across IoT devices, streaming infrastructure, gateways, servers, and partner networks.

---

## Tech Stack

| Layer | Technology | Version |
| :---- | :---- | :---- |
| Frontend Framework | Next.js (React) | 14 |
| Language | TypeScript | 5.x |
| Styling | Inline CSS (no Tailwind) | — |
| Icons | Lucide React | 0.344 |
| Markdown Rendering | react-markdown + remark-gfm | 9.0 / 4.0 |
| Deployment | Snowpark Container Services (SPCS) | — |
| Container | Docker (node:20-alpine, standalone) | — |
| Database | Snowflake + Snowflake Postgres | — |
| AI | Cortex Agent (Analyst + Search) | — |

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT BROWSER                                          │
│                 https://mwjfcg-sfsenorthamerica-dhall-aws1.snowflakecomputing.app   │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────┐     │
│  │                         Next.js React Application                           │     │
│  │                                                                             │     │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌─────────┐ ┌───────────┐  │     │
│  │  │ Dashboard  │ │   Agent    │ │  Partners  │ │ Devices │ │ Geography │  │     │
│  │  │ (KPI cards)│ │   Chat     │ │  (table)   │ │ (cards) │ │ (SVG map) │  │     │
│  │  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └────┬────┘ └─────┬─────┘  │     │
│  │        │               │              │             │            │         │     │
│  │  ┌─────┴───────────────┴──────────────┴─────────────┴────────────┘         │     │
│  │  │                                                                          │     │
│  │  │  ┌──────────────────────────────────────────────────────────────────┐   │     │
│  │  │  │                    DrilldownPanel Component                       │   │     │
│  │  │  │  • Click any data element → AI investigation                     │   │     │
│  │  │  │  • ReactMarkdown response with tables                            │   │     │
│  │  │  │  • Drill-down pill buttons for follow-up                          │   │     │
│  │  │  └──────────────────────────────────────────────────────────────────┘   │     │
│  │  │                                                                          │     │
│  │  │  ┌──────────────┐  ┌──────────────┐                                    │     │
│  │  │  │ Investigate  │  │ Architecture │                                    │     │
│  │  │  │(deep reason) │  │ (interactive)│                                    │     │
│  │  │  └──────────────┘  └──────────────┘                                    │     │
│  │  │                                                                          │     │
│  │  └──────────────────────────────────────────────────────────────────────────┘     │
│  │                          │                            │                           │
│  └──────────────────────────┼────────────────────────────┼───────────────────────────┘
│                             │                            │                             │
└─────────────────────────────┼────────────────────────────┼─────────────────────────────┘
                              │ /api/data                   │ /api/chat
                              ▼                            ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                          NEXT.JS API ROUTES (Server-Side)                            │
│                          Running inside SPCS container                               │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────┐     │
│  │  GET /api/data?q=kpis     →  SQL API (Interactive Warehouse)               │     │
│  │  GET /api/data?q=geo      →  SQL API (Standard Warehouse)                  │     │
│  │  GET /api/data?q=partners →  SQL API (Standard Warehouse)                  │     │
│  │                                                                             │     │
│  │  POST /api/chat           →  Cortex Agent REST API                         │     │
│  │       body: { messages }       (orchestrates 3 Analyst + 1 Search tool)    │     │
│  └────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                      │
│  Auth: OAuth token mounted at /snowflake/session/token (SPCS-managed)               │
│  Host: SNOWFLAKE_HOST env var (injected by SPCS)                                    │
│                                                                                      │
└─────────────────────────────┬────────────────────────────┬─────────────────────────────┘
                              │                            │
              ┌───────────────┘                            └───────────────┐
              │                                                            │
              ▼                                                            ▼
┌───────────────────────────────────────┐   ┌───────────────────────────────────────────┐
│        SNOWFLAKE SQL API              │   │           CORTEX AGENT REST API            │
│    /api/v2/statements                 │   │                                           │
│                                       │   │  POST /api/v2/cortex/agent:run            │
│  Warehouse: CERT_COMPLIANCE_IWH       │   │                                           │
│    (Interactive - sub-second KPIs)    │   │  Auth: OAuth (SPCS token)                 │
│                                       │   │  Response: SSE Stream                     │
│  Warehouse: COMCAST_DEMO_WH           │   │                                           │
│    (Standard - geo/partner joins)     │   │  Agent: CERT_COMPLIANCE_AGENT             │
│                                       │   │  Model: auto (orchestration)              │
└───────────────────────────────────────┘   └───────────────────────┬───────────────────┘
                                                                    │
                                              ┌─────────────────────┼─────────────────────┐
                                              │                     │                     │
                                              ▼                     ▼                     ▼
                                    ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐
                                    │  cert_dashboard  │  │  cert_analytics │  │  policy_rules    │
                                    │  (Analyst tool)  │  │  (Analyst tool) │  │  (Analyst tool)  │
                                    │                  │  │                 │  │                  │
                                    │  Interactive Tbl │  │  50M row view   │  │  10 policy rules │
                                    │  via IWH         │  │  via Std WH     │  │  via Std WH      │
                                    └──────────────────┘  └─────────────────┘  └──────────────────┘
                                              │
                                              │           ┌─────────────────────────────────────┐
                                              │           │     compliance_docs_search          │
                                              └──────────►│     (Cortex Search tool)            │
                                                          │     RAG over policy docs            │
                                                          └─────────────────────────────────────┘
```

---

## Data Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA PIPELINE FLOW                                     │
│                                                                                  │
│  ┌──────────────┐    pg_lake     ┌──────────────┐   1-min lag  ┌────────────┐  │
│  │  Snowflake   │───(Iceberg)───►│   Catalog    │─────────────►│Interactive │  │
│  │  Postgres    │    ~30s        │ Integration  │              │   Table    │  │
│  │ CERT_OLTP_DB │                │              │              │ (clustered)│  │
│  └──────────────┘                └──────────────┘              └─────┬──────┘  │
│                                                                      │         │
│  ┌──────────────┐   Snowpipe    ┌──────────────┐                    │         │
│  │   IoT/CDC    │──Streaming───►│    RAW_      │                    │         │
│  │   Sources    │   (5s lag)    │ CERTIFICATE  │                    │         │
│  └──────────────┘               │   _EVENTS    │                    │         │
│                                 └──────┬───────┘                    │         │
│                                        │                            │         │
│                                        ▼                            ▼         │
│                                 ┌──────────────┐           ┌────────────────┐ │
│                                 │DT_CERTS_     │           │CERT_COMPLIANCE │ │
│                                 │CLEANED       │           │    _IWH        │ │
│                                 │(Bronze→Silver)           │ (pre-cached)   │ │
│                                 └──────┬───────┘           └────────────────┘ │
│                                        │                                      │
│                                        ▼                                      │
│                                 ┌──────────────┐                              │
│                                 │DT_CERTS_     │                              │
│                                 │ENRICHED      │                              │
│                                 │(Silver+joins)│                              │
│                                 └──────┬───────┘                              │
│                                        │                                      │
│                                        ▼                                      │
│                                 ┌──────────────┐                              │
│                                 │CERTIFICATES  │─────────────────────────────►│
│                                 │ (50M rows)   │    V_CERTIFICATES_FULL       │
│                                 └──────────────┘    (analytical view)         │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Components

### Component Hierarchy

```
layout.tsx
├── Sidebar                    # Left navigation with icons
│   └── NavItem[]              # Dashboard, Chat, Partners, Devices, Geography, Investigate, Architecture
│
├── page.tsx (Dashboard)       # KPI cards + region/device tables + DrilldownPanel
│   ├── KPI Cards[]            # Click → auto-sends question to agent
│   ├── Region Table           # Click row → region deep-dive
│   ├── Device Table           # Click row → device investigation
│   └── DrilldownPanel         # AI response + drill-down pills
│
├── chat/page.tsx              # Full agent conversation interface
│   ├── Sample Questions       # Suggestion pills
│   ├── MessageList            # User/assistant messages with markdown
│   └── Input Bar              # Text input + send button
│
├── partners/page.tsx          # Partner table with click-to-investigate
│   ├── Partner Table          # Sortable, color-coded compliance
│   └── DrilldownPanel         # Per-partner investigation
│
├── devices/page.tsx           # Device cards with click-to-investigate
│   ├── DeviceCard[]           # Proportional bars, self-signed/expired counts
│   └── DrilldownPanel         # Per-device investigation
│
├── geography/page.tsx         # SVG world map with data center markers
│   ├── WorldMap (SVG)         # Inline country paths from Natural Earth
│   ├── Markers[]              # Positioned by lat/lng, colored by compliance
│   └── DC Detail Panel        # Click marker for data center details
│
├── investigate/page.tsx       # Deep reasoning investigation cards
│   ├── MetricCard[]           # Severity badges, targets, trends
│   ├── Investigation Panel    # AI response with markdown
│   └── Drill-down Pills       # Follow-up question buttons
│
└── architecture/page.tsx      # Interactive architecture diagram
    ├── LayerCard[]            # 6 clickable architecture layers
    ├── FlowArrow[]            # Dashed animated arrows
    └── Detail Panel           # Feature descriptions + doc links
```

### Key Component: DrilldownPanel

Reusable AI investigation component used across Dashboard, Partners, and Devices pages:

```tsx
interface DrilldownProps {
  question: string;        // Auto-sent to Cortex Agent on mount
  title: string;           // Panel header
  onClose: () => void;     // Close handler
  drilldowns?: {           // Follow-up pill buttons
    label: string;
    question: string;
  }[];
}
```

**Behavior:**
1. Mounts → immediately POSTs question to `/api/chat`
2. Shows loading state with pulsing indicator
3. Renders markdown response with formatted tables
4. Displays drill-down pills — clicking sends a new question
5. Pills highlight when active (blue background)

---

## API Routes

### GET /api/data

Dashboard data endpoint querying the Interactive Table via IWH for sub-second responses.

| Parameter | Response |
| :---- | :---- |
| `?q=kpis` | KPI summary + region breakdown + device breakdown |
| `?q=geo` | Data center locations with compliance metrics |
| `?q=partners` | Partner table with compliance rates |

**Warehouse routing:**
- `kpis` → `CERT_COMPLIANCE_IWH` (Interactive Warehouse, sub-second)
- `geo`, `partners` → `COMCAST_DEMO_WH` (Standard, supports JOINs with non-interactive tables)

### POST /api/chat

Cortex Agent endpoint for natural language Q&A.

**Request:**
```json
{
  "messages": [
    { "role": "user", "content": "Which partners have compliance below 60%?" }
  ]
}
```

**Response:**
```json
{
  "text": "Based on the data, the following partners...",
  "sql": "SELECT partner_display_name, ...",
  "sources": [{ "title": "Certificate Compliance Policy", "doc_id": "..." }]
}
```

**Agent REST API call:**
```javascript
POST https://${SNOWFLAKE_HOST}/api/v2/cortex/agent:run
Headers:
  Authorization: Bearer ${SPCS_OAUTH_TOKEN}
  X-Snowflake-Authorization-Token-Type: OAUTH
Body:
  {
    "agent_name": "COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_COMPLIANCE_AGENT",
    "messages": [...],
    "stream": true
  }
```

---

## Cortex Agent Configuration

### Agent: CERT_COMPLIANCE_AGENT

```
Database: COMCAST_CYBER_DEMO
Schema:   CERT_SECURITY
Model:    auto (orchestration)
```

### Tool Selection Logic (Orchestration Instructions)

| Question Type | Tool Selected | Warehouse | Response Time |
| :---- | :---- | :---- | :---- |
| Summary KPIs, totals by region/device/partner | `cert_dashboard` | CERT_COMPLIANCE_IWH | <1s |
| Detailed drill-downs, cert lookups, expiry analysis | `cert_analytics` | COMCAST_DEMO_WH | 2-5s |
| Compliance rules, severity levels, allowed algorithms | `policy_rules` | COMCAST_DEMO_WH | <1s |
| Policy documents, remediation procedures | `compliance_docs_search` | N/A (Search) | <2s |

### Tools

| Tool | Type | Backing Object | Description |
| :---- | :---- | :---- | :---- |
| `cert_dashboard` | Cortex Analyst | CERT_DASHBOARD_SV | Pre-aggregated Interactive Table metrics |
| `cert_analytics` | Cortex Analyst | CERT_COMPLIANCE_SV | Full 50M certificate inventory (18 dimensions, 11 metrics) |
| `policy_rules` | Cortex Analyst | CERT_POLICY_RULES_SV | Compliance policy rule definitions |
| `compliance_docs_search` | Cortex Search | CERT_COMPLIANCE_SEARCH | RAG over compliance documents |

### Semantic Views

**CERT_COMPLIANCE_SV** (primary analytics)
- Table: V_CERTIFICATES_FULL (50M rows)
- Dimensions: cert_id, compliance_status, device_type, region, partner_display_name, partner_industry, partner_tier, dc_name, dc_city, key_algorithm, signature_algorithm, issuer_cn, subject_cn, source_system, is_self_signed, compliance_violation, key_size
- Metrics: total_certificates, compliant_count, non_compliant_count, expired_count, expiring_30_days, self_signed_count, weak_key_count, sha1_count, avg_key_size, avg_validity_days, avg_days_to_expiry

**CERT_DASHBOARD_SV** (fast aggregates via IWH)
- Table: CERT_COMPLIANCE_INTERACTIVE (21K pre-aggregated rows)
- Dimensions: region, device_type, partner_name, partner_display_name, key_algorithm, compliance_status
- Metrics: total_certs, self_signed_total, compliant_certs, non_compliant_certs, expired_certs, expiring_certs, compliance_rate

**CERT_POLICY_RULES_SV** (policy reference)
- Table: COMPLIANCE_RULES (10 rules)
- Dimensions: rule_id, rule_name, description, allowed_algorithms, severity
- Metrics: min_key_size, max_validity_days, total_rules

---

## Snowflake Objects

### Databases & Schemas

| Object | Purpose |
| :---- | :---- |
| `COMCAST_CYBER_DEMO.CERT_SECURITY` | Primary schema for all demo objects |
| `CERT_OLTP_DB` (Postgres) | OLTP transactional instance |

### Tables

| Table | Rows | Description |
| :---- | :---- | :---- |
| `CERTIFICATES` | 50,000,000 | Core certificate fact table (X.509 attributes) |
| `PARTNERS` | 50 | Partner dimension (DigiCert, Akamai, Arris, etc.) |
| `DATA_CENTERS` | 15 | Data center dimension with lat/lng coordinates |
| `COMPLIANCE_DOCUMENTS` | 10 | Policy documents for Cortex Search RAG |
| `COMPLIANCE_RULES` | 10 | Policy rules (min key size, allowed algorithms) |
| `RAW_CERTIFICATE_EVENTS` | 8,000 | Simulated streaming ingest events |
| `POSTGRES_CDC_EVENTS` | 1,000 | Simulated CDC events from Postgres |

### Dynamic Tables (Medallion Architecture)

| Table | Layer | Target Lag | Description |
| :---- | :---- | :---- | :---- |
| `DT_CERTS_CLEANED` | Bronze→Silver | 5 min | SCD Type 1 dedup, schema flattening |
| `DT_CERTS_ENRICHED` | Silver | 5 min | JOIN to PARTNERS, base compliance flags |
| `DT_COMPLIANCE_DASHBOARD` | Gold | 5 min | Aggregations by region/partner/device |

### Interactive Table

| Table | Cluster By | Target Lag | Rows |
| :---- | :---- | :---- | :---- |
| `CERT_COMPLIANCE_INTERACTIVE` | (region, compliance_status) | 1 minute | ~21,000 |

### Views

| View | Description |
| :---- | :---- |
| `V_CERTIFICATES_FULL` | Analytical view joining CERTIFICATES + PARTNERS + DATA_CENTERS with compliance logic |

### Warehouses

| Warehouse | Type | Size | Purpose |
| :---- | :---- | :---- | :---- |
| `COMCAST_DEMO_WH` | Standard | LARGE | Refresh, analytical queries, geo/partner JOINs |
| `CERT_COMPLIANCE_IWH` | Interactive | XSMALL | Sub-second dashboard KPIs (5s timeout, fallback to COMCAST_DEMO_WH) |

### Compute Pools

| Pool | Instance | Services |
| :---- | :---- | :---- |
| `COMCAST_CERT_APP_POOL` | CPU_X64_XS | CERT_CHAT_SERVICE |

### Integrations

| Integration | Type | Purpose |
| :---- | :---- | :---- |
| `CERT_POSTGRES_CATALOG` | Catalog (SNOWFLAKE_POSTGRES) | pg_lake Shared Iceberg mirror from CERT_OLTP_DB |

### Services

| Service | Image | Endpoint |
| :---- | :---- | :---- |
| `CERT_CHAT_SERVICE` | cert-chat:v3 | mwjfcg-sfsenorthamerica-dhall-aws1.snowflakecomputing.app |

---

## Authentication & Security

### SPCS OAuth (Production)

The application runs inside SPCS and uses the platform-mounted OAuth token:

```typescript
// Token auto-mounted by SPCS runtime
const token = fs.readFileSync('/snowflake/session/token', 'utf-8').trim();

// Host injected as env var by SPCS
const host = process.env.SNOWFLAKE_HOST;

// All API calls use OAuth
headers: {
  'Authorization': `Bearer ${token}`,
  'X-Snowflake-Authorization-Token-Type': 'OAUTH'
}
```

### Public Endpoint Access

The SPCS service endpoint requires Snowflake authentication. Users must be logged into the Snowflake account to access the app URL.

---

## Deployment

### Docker Build (Multi-Stage)

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install --no-audit --no-fund

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

**Critical:** `ENV HOSTNAME=0.0.0.0` is required — Next.js standalone binds to localhost by default, which is unreachable inside SPCS.

### Build & Deploy Commands

```bash
# Build for linux/amd64
docker build --platform linux/amd64 --no-cache -t sfsenorthamerica-dhall-aws1.registry.snowflakecomputing.com/comcast_cyber_demo/cert_security/app_repo/cert-chat:v3 .

# Login to Snowflake registry
snow spcs image-registry login

# Push
docker push sfsenorthamerica-dhall-aws1.registry.snowflakecomputing.com/comcast_cyber_demo/cert_security/app_repo/cert-chat:v3

# Deploy (Snowflake SQL)
CREATE SERVICE COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_CHAT_SERVICE
  IN COMPUTE POOL COMCAST_CERT_APP_POOL
  FROM SPECIFICATION $$ ... $$
  MIN_INSTANCES = 1 MAX_INSTANCES = 1;
```

---

## Key Design Decisions

| Decision | Rationale |
| :---- | :---- |
| Next.js standalone (not Streamlit) | Full control over UI, supports SPCS deployment, multi-page SPA |
| Inline SVG map (not Leaflet) | SPCS CSP blocks external tile servers and CDN scripts |
| Interactive Table + IWH for dashboard | Sub-second KPIs on pre-aggregated 50M rows without scanning full table |
| 3 Semantic Views (not 1) | Intelligent routing: fast aggregates via IWH, full detail via standard WH, policy rules separate |
| pg_lake Shared Iceberg | Zero-infra CDC from Postgres (~30s lag, no Openflow, no S3 bucket) |
| DrilldownPanel component | Reusable click-to-investigate pattern across all pages |
| Light mode theme | Better visibility for remote demo presentations |
| Real partner names | Credibility with customer (DigiCert, Akamai, Arris vs Partner_001) |

---

## Demo Flow Script (5/29 Meeting)

1. **Dashboard** — Show real-time KPIs powered by Interactive Warehouse (<100ms)
2. **Click a KPI** — Demonstrate AI investigation with drill-down pills
3. **Chat** — Ask natural language questions across all 3 semantic views
4. **Partners** — Click a partner row to investigate their compliance posture
5. **Geography** — Show global data center distribution and regional compliance
6. **Investigate** — Deep reasoning cards for root cause analysis
7. **Architecture** — Click each layer to explain the technology and link to docs

---

## Version History

| Version | Date | Changes |
| :---- | :---- | :---- |
| 1.0.0 | 2026-05-21 | Initial deployment: dashboard, chat, basic pages |
| 1.1.0 | 2026-05-21 | Added geography (SVG map), investigation, architecture pages |
| 1.2.0 | 2026-05-21 | Light mode, realistic partner names, data variance fix |
| 2.0.0 | 2026-05-22 | Postgres Mirroring (pg_lake), Interactive Table + IWH, 3 Semantic Views |
| 2.1.0 | 2026-05-22 | Interactive dashboards with DrilldownPanel, click-to-investigate pattern |
| 2.2.0 | 2026-05-22 | Interactive architecture page with documentation links |
