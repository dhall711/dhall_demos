# ISCO Deep Reasoning Agent \- Technical Architecture

## Overview

The ISCO Deep Reasoning Agent is a supply chain intelligence application that combines a React frontend with a Node.js backend, leveraging Snowflake's Cortex AI capabilities for natural language analysis of supply chain metrics.

---

## Tech Stack

| Layer | Technology | Version |
| :---- | :---- | :---- |
| Frontend Framework | React | 18.2 |
| Language | TypeScript | 5.2 |
| Build Tool | Vite | 5.0 |
| Styling | Tailwind CSS | 3.3 |
| Icons | Lucide React | 0.294 |
| Markdown Rendering | react-markdown \+ remark-gfm | 10.1 / 4.0 |
| Backend Runtime | Node.js | 18+ |
| Backend Framework | Express | 5.2 |
| Database Connector | snowflake-sdk | 2.3.4 |

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT BROWSER                                     │
│                              localhost:3000                                     │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           React Application                              │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │   │
│  │  │  Executive   │  │   Anomaly    │  │   Tickets    │  │  Insights   │  │   │
│  │  │  Dashboard   │  │  Dashboard   │  │    Panel     │  │    View     │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │   │
│  │         │                 │                 │                │          │   │
│  │         └─────────────────┴────────┬────────┴────────────────┘          │   │
│  │                                    │                                     │   │
│  │  ┌─────────────────────────────────▼─────────────────────────────────┐  │   │
│  │  │                        ChatInterface                               │  │   │
│  │  │  • Message display with ReactMarkdown                             │  │   │
│  │  │  • Confidence indicators                                          │  │   │
│  │  │  • Drill-down suggestions                                         │  │   │
│  │  │  • Ticket creation                                                │  │   │
│  │  └───────────────────────────────────────────────────────────────────┘  │   │
│  │                                    │                                     │   │
│  │  ┌─────────────────────────────────▼─────────────────────────────────┐  │   │
│  │  │                         Services Layer                             │  │   │
│  │  │                                                                    │  │   │
│  │  │  snowflake.ts              snowflakeAgent.ts                      │  │   │
│  │  │  • getMetrics()            • askAgent()                           │  │   │
│  │  │  • getAnomalies()          • findTermsInText()                    │  │   │
│  │  │  • getTickets()            • createInvestigationTicket()          │  │   │
│  │  │  • getDeepReasoning()      • TERMINOLOGY_DB                       │  │   │
│  │  └───────────────────────────────────────────────────────────────────┘  │   │
│  │                                    │                                     │   │
│  └────────────────────────────────────┼─────────────────────────────────────┘   │
│                                       │                                         │
└───────────────────────────────────────┼─────────────────────────────────────────┘
                                        │ HTTP/REST
                                        ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              EXPRESS BACKEND                                    │
│                              localhost:3001                                     │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           API Endpoints                                  │   │
│  │                                                                          │   │
│  │  POST /api/deep-reasoning     ──────────────────────────────────────►   │   │
│  │       ?stream=true|false      Cortex Agent API (SSE streaming)          │   │
│  │       ?agent=true|false       OR Legacy CORTEX.COMPLETE                 │   │
│  │       ?nocache=true           Bypass demo cache                         │   │
│  │                                                                          │   │
│  │  GET  /api/metrics            ──► Snowflake SQL Query                   │   │
│  │  GET  /api/anomalies          ──► Snowflake SQL Query                   │   │
│  │  GET  /api/tickets            ──► Snowflake SQL Query                   │   │
│  │  POST /api/tickets            ──► Snowflake SQL INSERT                  │   │
│  │  GET  /api/knowledge          ──► Snowflake SQL Query                   │   │
│  │  GET  /api/documents          ──► Snowflake SQL Query                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
│  ┌────────────────────────────────────┼─────────────────────────────────────┐   │
│  │                          DEMO CACHE LAYER                                │   │
│  │  Pre-computed responses for California demo path                         │   │
│  │  • california_ctd_why, california_ctd_trend, california_ctd_impact      │   │
│  │  • california_ots_why, california_inventory_status                      │   │
│  │  • what_is_ctd, what_is_ots, executive_summary                          │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                         │
└───────────────────────────────────────┼─────────────────────────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                    ▼                                       ▼
┌───────────────────────────────────┐   ┌───────────────────────────────────────┐
│      SNOWFLAKE SQL QUERIES        │   │         CORTEX AGENT REST API         │
│                                   │   │                                       │
│  Connection: snowflake-sdk        │   │  Endpoint:                            │
│  Auth: PAT Token                  │   │  POST /api/v2/databases/{db}/         │
│                                   │   │       schemas/{schema}/agents/        │
│  Tables:                          │   │       {agent}:run                     │
│  • WEEKLY_EXECUTIVE_METRICS       │   │                                       │
│  • INVESTIGATION_TICKETS          │   │  Auth: PAT + X-Snowflake-             │
│  • BUSINESS_CONTEXT_NARRATIVES    │   │        Authorization-Token-Type       │
│  • EXTERNAL_CONTEXT_EVENTS        │   │                                       │
│  • AGENT_KNOWLEDGE_BASE           │   │  Response: SSE Stream                 │
│  • DOCUMENT_STORE                 │   │  • response.text.delta (streaming)    │
│  • SUPPLY_CHAIN_METRICS           │   │  • response.tool_use (tool calls)     │
│                                   │   │  • response (final content)           │
└───────────────────────────────────┘   └───────────────────────────────────────┘
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                              SNOWFLAKE ACCOUNT                                  │
│                      SFSENORTHAMERICA-DHALL_AWS1                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Database: ISCO_ANALYTICS                                                       │
│  Schema: PROD                                                                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     ISCO_DEEP_REASONING_AGENT                            │   │
│  │                                                                          │   │
│  │  Model: claude-4-sonnet                                                  │   │
│  │                                                                          │   │
│  │  Tools:                                                                  │   │
│  │  ├── supply_chain_analyst   (Cortex Analyst - text-to-SQL)              │   │
│  │  ├── search_historical_context (Cortex Search - RAG)                    │   │
│  │  ├── lookup_terminology     (Cortex Search - definitions)               │   │
│  │  ├── analyze_anomaly        (Custom SQL Function)                       │   │
│  │  ├── predict_recovery       (Custom SQL Function)                       │   │
│  │  ├── compare_regions        (Custom SQL Function)                       │   │
│  │  ├── executive_summary      (Custom SQL Function)                       │   │
│  │  └── CREATE_INVESTIGATION   (Stored Procedure)                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    SUPPLY_CHAIN_SEMANTIC_VIEW                            │   │
│  │                                                                          │   │
│  │  Base Tables:                                                            │   │
│  │  • SUPPLY_CHAIN_METRICS (metrics, executive)                            │   │
│  │  • WEEKLY_EXECUTIVE_METRICS                                             │   │
│  │                                                                          │   │
│  │  Dimensions: REGION, METRIC_NAME, STATUS, ANOMALY_SEVERITY              │   │
│  │  Metrics: AVG_VALUE, AVG_TARGET, AVG_TREND, METRIC_COUNT                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Components

### Component Hierarchy

```
App.tsx
├── SettingsPanel           # Configuration modal
├── DocumentManager         # Knowledge base document viewer
├── Header
│   └── Tab Navigation      # Executive | Anomalies | Tickets | Insights
│
├── ExecutiveDashboard      # Main executive view (activeTab='executive')
│
├── Anomalies View          # (activeTab='dashboard')
│   ├── MetricCard[]        # Anomaly cards with severity indicators
│   └── ChatInterface       # AI conversation panel
│       ├── Message[]       # Chat messages with markdown
│       ├── ConfidenceBadge # AI confidence indicator
│       ├── DrillDownPanel  # Follow-up question suggestions
│       └── SourcesPanel    # Data sources used
│
├── Tickets View            # (activeTab='tickets')
│   ├── TicketsPanel        # List of investigation tickets
│   └── TicketDetail        # Deep analysis panel
│
└── Insights View           # (activeTab='insights')
    ├── ExecutiveSummary    # KPI overview
    ├── MetricCorrelations  # Cross-metric analysis
    └── PredictiveForecast  # Trend predictions
```

### Key Components

#### ChatInterface.tsx

Primary AI interaction component that:

- Renders chat messages with **ReactMarkdown** \+ **remark-gfm**  
- Displays confidence badges with tooltips  
- Shows drill-down recommendations for follow-up questions  
- Provides ticket creation for low-confidence responses

#### MetricCard.tsx

Displays anomaly metrics with:

- Severity indicator (CRITICAL/HIGH/MEDIUM/LOW)  
- Current value vs target comparison  
- Week-over-week trend sparkline  
- Click handler for deep analysis

---

## Services Layer

### snowflake.ts \- Data Access Service

```ts
const API_BASE = 'http://localhost:3001/api';

// Fetch anomalies requiring investigation
export async function getAnomalies(): Promise<Metric[]>

// Fetch all metrics for analysis
export async function getMetrics(): Promise<Metric[]>

// Fetch investigation tickets
export async function getTickets(): Promise<Ticket[]>

// Create new investigation ticket
export async function createTicket(
  metricId: string, 
  question: string, 
  aiResponse: string
): Promise<Ticket>

// Call deep reasoning API (Cortex Agent)
export async function getDeepReasoning(
  metricId: string, 
  question: string
): Promise<DeepReasoningResponse>
```

### snowflakeAgent.ts \- Agent Interaction Service

```ts
// Main agent interaction function
export async function askAgent(
  metric: Metric | null,
  question: string
): Promise<AgentResponse>

// Extract ISCO terminology from text
export function findTermsInText(text: string): TermDefinition[]

// Create investigation ticket via API
export async function createInvestigationTicket(
  metricName: string,
  region: string,
  weekDate: string,
  question: string,
  aiAnalysis: string,
  confidenceScore: number
): Promise<string>
```

---

## Backend API Endpoints

### POST /api/deep-reasoning

Primary endpoint for AI-powered analysis.

**Query Parameters:** | Parameter | Type | Default | Description | |-----------|------|---------|-------------| | `stream` | boolean | false | Enable SSE streaming response | | `agent` | boolean | true | Use Cortex Agent (false \= legacy CORTEX.COMPLETE) | | `nocache` | boolean | false | Bypass demo cache | | `fast` | boolean | false | Use lighter model (llama3.1-8b) |

**Request Body:**

```json
{
  "metricId": "WEM_2026W06_CA_OTD",
  "question": "Why is On-Time Delivery dropping?",
  "sessionId": "optional-session-id"
}
```

**Response:**

```json
{
  "response": "**On-Time Shipping in California is at 82.3%**...",
  "confidence": 91,
  "sources": {
    "narratives": [],
    "events": [],
    "knowledge": [],
    "toolsUsed": ["supply_chain_analyst", "cortex_search"]
  },
  "suggestedActions": ["Review the analysis", "Create ticket if needed"],
  "uncertainties": [],
  "drillDowns": [],
  "agentMode": true,
  "cached": false
}
```

### GET /api/metrics

Retrieves all supply chain metrics from `SUPPLY_CHAIN_METRICS` table.

### GET /api/anomalies

Retrieves metrics flagged as anomalies from `WEEKLY_EXECUTIVE_METRICS` where `IS_ANOMALY = TRUE`.

### GET /api/tickets

Retrieves investigation tickets from `INVESTIGATION_TICKETS` table.

### POST /api/tickets

Creates new investigation ticket in `INVESTIGATION_TICKETS` table.

---

## Cortex Agent Integration

### Agent Configuration

```javascript
const SNOWFLAKE_ACCOUNT_URL = 'https://SFSENORTHAMERICA-DHALL_AWS1.snowflakecomputing.com';
const CORTEX_AGENT_DATABASE = 'ISCO_ANALYTICS';
const CORTEX_AGENT_SCHEMA = 'PROD';
const CORTEX_AGENT_NAME = 'ISCO_DEEP_REASONING_AGENT';
```

### API Call Structure

```javascript
async function runCortexAgentDirect(question, metricContext) {
  const enhancedQuestion = metricContext 
    ? `Regarding ${metricContext.metricName} in ${metricContext.region} 
       (current: ${metricContext.currentValue}, target: ${metricContext.targetValue}, 
       variance: ${metricContext.variancePct}%): ${question}`
    : question;
  
  const response = await fetch(
    `${SNOWFLAKE_ACCOUNT_URL}/api/v2/databases/${CORTEX_AGENT_DATABASE}/schemas/${CORTEX_AGENT_SCHEMA}/agents/${CORTEX_AGENT_NAME}:run`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${PAT_TOKEN}`,
        'X-Snowflake-Authorization-Token-Type': 'PROGRAMMATIC_ACCESS_TOKEN'
      },
      body: JSON.stringify({
        messages: [{
          role: 'user',
          content: [{ type: 'text', text: enhancedQuestion }]
        }]
      })
    }
  );
  
  return response;
}
```

### SSE Response Parsing

The Cortex Agent returns Server-Sent Events (SSE) with multiple event types:

```javascript
// Event types from Cortex Agent
event: response.status        // Status updates (planning, executing_tools)
event: response.thinking.delta // Internal reasoning (filtered out)
event: response.text.delta    // Streaming text output
event: response.tool_use      // Tool invocations
event: response.tool_result   // Tool results
event: response              // Final complete response
event: done                  // Stream complete
```

**Parsing Logic:**

```javascript
const reader = agentResponse.body.getReader();
let currentEventType = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  // Parse SSE format
  for (const line of lines) {
    if (line.startsWith('event: ')) {
      currentEventType = line.slice(7).trim();
      continue;
    }
    
    // Skip thinking events
    if (currentEventType.includes('thinking')) continue;
    
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      
      // Capture streaming text
      if (currentEventType === 'response.text.delta' && data.text) {
        fullResponse += data.text;
      }
      
      // Capture tool usage
      if (currentEventType === 'response.tool_use' && data.name) {
        toolsUsed.push(data.name);
      }
      
      // Final response
      if (currentEventType === 'response' && data.content) {
        fullResponse = data.content.find(c => c.type === 'text')?.text;
      }
    }
  }
}
```

---

## Data Flow Diagrams

### User Question Flow

```
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌───────────────┐
│   User   │───►│ ChatInterface│───►│  useChat    │───►│ snowflakeAgent│
│  Types   │    │   .tsx       │    │   Hook      │    │    .ts        │
│ Question │    │              │    │             │    │               │
└──────────┘    └──────────────┘    └─────────────┘    └───────┬───────┘
                                                               │
                                                               ▼
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌───────────────┐
│  Display │◄───│ ChatInterface│◄───│  useChat    │◄───│   Backend     │
│ Response │    │ (Markdown)   │    │  (setState) │    │   Response    │
└──────────┘    └──────────────┘    └─────────────┘    └───────┬───────┘
                                                               │
                                          ┌────────────────────┴────────────────────┐
                                          │                                         │
                                          ▼                                         ▼
                                   ┌─────────────┐                          ┌─────────────┐
                                   │ Demo Cache  │                          │Cortex Agent │
                                   │   (fast)    │                          │   (live)    │
                                   └─────────────┘                          └──────┬──────┘
                                                                                   │
                                                                    ┌──────────────┼──────────────┐
                                                                    │              │              │
                                                                    ▼              ▼              ▼
                                                              ┌──────────┐  ┌──────────┐  ┌──────────┐
                                                              │ Cortex   │  │ Cortex   │  │ Custom   │
                                                              │ Analyst  │  │ Search   │  │Functions │
                                                              │(text2SQL)│  │  (RAG)   │  │          │
                                                              └──────────┘  └──────────┘  └──────────┘
```

### Metric Selection Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  MetricCard  │────►│   App.tsx    │────►│ ChatInterface│
│   onClick    │     │handleMetric  │     │  displays    │
│              │     │   Select     │     │   context    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  sendMessage │
                    │  (auto-ask)  │
                    │              │
                    │ "Why did     │
                    │ {metric}     │
                    │ change?"     │
                    └──────────────┘
```

---

## Demo Cache System

For faster demo experiences, California-related queries are pre-cached:

### Cache Keys and Triggers

| Cache Key | Trigger Patterns |
| :---- | :---- |
| `california_ctd_why` | California \+ CTD \+ (why, cause, drop, issue) |
| `california_ctd_trend` | California \+ CTD \+ (trend, week, history, forecast) |
| `california_ctd_impact` | California \+ CTD \+ (impact, cost, effect, business) |
| `california_ots_why` | California \+ (OTS, shipping) |
| `california_inventory_status` | California \+ (inventory, stock, DOS) |
| `what_is_ctd` | "what is CTD", "what's CTD" |
| `what_is_ots` | "what is OTS", "what's OTS" |
| `executive_summary` | summary, overview, status, executive |

### Cache Bypass

Add `?nocache=true` to force live agent call:

```
POST /api/deep-reasoning?nocache=true
```

---

## Authentication

### Snowflake SQL Connection

```javascript
const connection = snowflake.createConnection({
  account: 'SFSENORTHAMERICA-DHALL_AWS1',
  authenticator: 'PROGRAMMATIC_ACCESS_TOKEN',
  token: process.env.SNOWFLAKE_PAT,
  warehouse: 'DEFAULT_WH',
  role: 'SYSADMIN'
});
```

### Cortex Agent API

```javascript
headers: {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${PAT_TOKEN}`,
  'X-Snowflake-Authorization-Token-Type': 'PROGRAMMATIC_ACCESS_TOKEN'
}
```

---

## Running the Application

### Development Mode

```shell
# Start both frontend and backend
npm run dev:all

# Or separately:
npm run server  # Backend on :3001
npm run dev     # Frontend on :3000
```

### Environment Variables

| Variable | Description |
| :---- | :---- |
| `SNOWFLAKE_PAT` | Programmatic Access Token |
| `SNOWFLAKE_CONNECTION_NAME` | Named connection (default: dhall\_demo) |
| `VITE_API_URL` | Backend API URL (default: [http://localhost:3001/api](http://localhost:3001/api)) |

---

## Key Files Reference

| File | Purpose |
| :---- | :---- |
| `src/App.tsx` | Main application, state management, routing |
| `src/components/ChatInterface.tsx` | AI chat UI with markdown rendering |
| `src/components/ExecutiveDashboard.tsx` | Executive KPI dashboard |
| `src/components/MetricCard.tsx` | Anomaly metric display cards |
| `src/services/snowflake.ts` | Backend API client |
| `src/services/snowflakeAgent.ts` | Agent interaction \+ terminology |
| `src/hooks/useChat.ts` | Chat state management hook |
| `src/types/index.ts` | TypeScript type definitions |
| `server/index.js` | Express backend \+ Cortex Agent integration |

---

## Snowflake Objects

### Tables

| Table | Description |
| :---- | :---- |
| `WEEKLY_EXECUTIVE_METRICS` | Weekly KPIs with anomaly detection |
| `SUPPLY_CHAIN_METRICS` | Core supply chain metrics |
| `INVESTIGATION_TICKETS` | AI-generated investigation tickets |
| `BUSINESS_CONTEXT_NARRATIVES` | Historical context from leadership |
| `EXTERNAL_CONTEXT_EVENTS` | External events affecting metrics |
| `AGENT_KNOWLEDGE_BASE` | Learned institutional knowledge |
| `DOCUMENT_STORE` | Knowledge base documents |

### Agent Tools

| Tool | Type | Purpose |
| :---- | :---- | :---- |
| `supply_chain_analyst` | Cortex Analyst | Natural language to SQL |
| `search_historical_context` | Cortex Search | RAG over historical docs |
| `lookup_terminology` | Cortex Search | ISCO acronym definitions |
| `analyze_anomaly` | SQL Function | Anomaly root cause analysis |
| `predict_recovery` | SQL Function | Recovery timeline forecast |
| `compare_regions` | SQL Function | Cross-regional benchmarking |
| `executive_summary` | SQL Function | Overall health summary |
| `CREATE_INVESTIGATION` | Procedure | Create investigation ticket |

---

## Version History

| Version | Date | Changes |
| :---- | :---- | :---- |
| 1.0.0 | 2026-02-25 | Initial release with CORTEX.COMPLETE |
| 2.0.0 | 2026-02-25 | Migrated to Cortex Agent REST API |
| 2.1.0 | 2026-02-25 | Added demo cache for California path |

