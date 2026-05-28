'use client';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function APIPage() {
  const [input, setInput] = useState('How many certificates are expiring this week?');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  async function tryAPI() {
    setLoading(true); setResponse('');
    try {
      const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: [{ role: 'user', content: input }], stream: false }) });
      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));
    } catch (e: any) { setResponse(`Error: ${e.message}`); }
    finally { setLoading(false); }
  }

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Developer API</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>Programmatic access to the Certificate Compliance Agent via REST API, Python SDK, and MCP</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <CodeBlock title="cURL — Agent REST API" lang="bash" code={`curl -X POST "https://\${SNOWFLAKE_HOST}/api/v2/cortex/agent:run" \\
  -H "Authorization: Bearer \${TOKEN}" \\
  -H "Content-Type: application/json" \\
  -H "X-Snowflake-Authorization-Token-Type: OAUTH" \\
  -d '{
    "agent_name": "COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_COMPLIANCE_AGENT",
    "messages": [{
      "role": "user",
      "content": [{"type": "text", "text": "How many certs expire this week?"}]
    }],
    "stream": true
  }'`} />

        <CodeBlock title="Python — Snowflake Connector" lang="python" code={`import snowflake.connector
import os

conn = snowflake.connector.connect(
    connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME")
)

# Query Interactive Table via IWH (sub-second)
cur = conn.cursor()
cur.execute("""
    USE WAREHOUSE CERT_COMPLIANCE_IWH;
    SELECT region, compliance_status, SUM(cert_count)
    FROM CERT_COMPLIANCE_INTERACTIVE
    GROUP BY 1, 2 ORDER BY 3 DESC
""")
for row in cur:
    print(f"{row[0]} | {row[1]} | {row[2]:,}")`} />

        <CodeBlock title="SQL API — Direct Queries" lang="bash" code={`# Execute SQL via REST API (used by this app's dashboard)
curl -X POST "https://\${HOST}/api/v2/statements" \\
  -H "Authorization: Bearer \${TOKEN}" \\
  -H "X-Snowflake-Authorization-Token-Type: OAUTH" \\
  -d '{
    "statement": "SELECT region, SUM(cert_count) FROM CERT_COMPLIANCE_INTERACTIVE GROUP BY 1",
    "warehouse": "CERT_COMPLIANCE_IWH",
    "database": "COMCAST_CYBER_DEMO",
    "schema": "CERT_SECURITY"
  }'`} />

        <CodeBlock title="MCP — Model Context Protocol" lang="json" code={`// MCP Server Configuration (connect from Claude, Cortex Code, etc.)
{
  "mcpServers": {
    "comcast-cert-agent": {
      "type": "snowflake-agent",
      "account": "SFSENORTHAMERICA-DHALL_AWS1",
      "agent": "COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_COMPLIANCE_AGENT",
      "description": "Certificate compliance AI agent with 5 tools",
      "tools": [
        "cert_dashboard (fast KPIs via IWH)",
        "cert_analytics (50M row drill-down)",
        "policy_rules (compliance definitions)",
        "cert_chains (trust chain resolution)",
        "compliance_docs_search (policy RAG)"
      ]
    }
  }
}`} />
      </div>

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 12 }}>Try the Agent API</h3>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
          <input value={input} onChange={e => setInput(e.target.value)} style={{ flex: 1, padding: '10px 14px', borderRadius: 8, border: '1px solid #d1d5db', fontSize: 13 }} />
          <button onClick={tryAPI} disabled={loading} style={{ padding: '10px 20px', borderRadius: 8, border: 'none', background: '#0066cc', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: 13 }}>{loading ? 'Calling...' : 'Send'}</button>
        </div>
        {response && (
          <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: 16, borderRadius: 8, fontSize: 11, maxHeight: 400, overflow: 'auto', whiteSpace: 'pre-wrap' }}>{response}</pre>
        )}
      </div>
    </div>
  );
}

function CodeBlock({ title, lang, code }: { title: string; lang: string; code: string }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
      <div style={{ padding: '10px 14px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#374151' }}>{title}</span>
        <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 4, background: '#e0f2fe', color: '#0066cc' }}>{lang}</span>
      </div>
      <pre style={{ padding: 14, fontSize: 11, color: '#1e293b', overflow: 'auto', maxHeight: 260, margin: 0, background: '#fafbfc', lineHeight: 1.6 }}>{code}</pre>
    </div>
  );
}
