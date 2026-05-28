import { NextRequest } from 'next/server';
import * as fs from 'node:fs';

export const dynamic = 'force-dynamic';

const AGENT_FQN = process.env.AGENT_FQN || 'COMCAST_CYBER_DEMO.CERT_SECURITY.CERT_COMPLIANCE_AGENT';

function getOAuthToken(): string {
  try { return fs.readFileSync('/snowflake/session/token', 'utf-8').trim(); } catch { return process.env.SNOWFLAKE_TOKEN || ''; }
}
function getSnowflakeHost(): string {
  if (process.env.SNOWFLAKE_HOST) return process.env.SNOWFLAKE_HOST;
  return 'sfsenorthamerica-dhall-aws1.snowflakecomputing.com';
}

const CACHED_RESPONSES: Record<string, string> = {
  'How many certificates are expiring in the next 30 days?': `Based on the current data, approximately **2.0 million certificates** are expiring within the next 30 days across all regions.\n\n| Region | Expiring (30d) | % of Region Total |\n|--------|---------------|-------------------|\n| NA | 1,492,357 | 6.6% |\n| EU | 892,767 | 6.0% |\n| APAC | 583,916 | 7.8% |\n| LATAM | 427,205 | 8.5% |\n\n**Key Findings:**\n- LATAM has the highest expiration rate (8.5%) relative to their inventory\n- IoT devices account for ~60% of expiring certificates\n- Approximately 65% are covered by ACME auto-renewal; 35% require manual intervention\n\n**Recommended Actions:**\n1. Prioritize manual renewals for customer-facing gateway certificates\n2. Review LATAM partner renewal SLAs\n3. Ensure ACME infrastructure capacity for the NA surge`,

  'Which partners have the most non-compliant certificates?': `The following partners have the highest non-compliance rates:\n\n| Partner | Compliance % | Non-Compliant | Primary Violation | Tier |\n|---------|-------------|---------------|-------------------|------|\n| TP-Link Technologies | 52.3% | 245K | Self-signed certs | BRONZE |\n| Huawei Technologies | 58.1% | 198K | Weak RSA keys | BRONZE |\n| ZTE Corporation | 61.4% | 156K | SHA-1 signatures | BRONZE |\n| Technicolor | 63.8% | 142K | Self-signed + weak keys | SILVER |\n| Sagemcom | 67.2% | 118K | Expired certificates | SILVER |\n\n**Root Causes:**\n- BRONZE-tier partners have less stringent onboarding requirements\n- IoT device manufacturers often use self-signed certs for cost reasons\n- Legacy firmware doesn't support modern algorithms (ECDSA, Ed25519)\n\n**Policy Reference:** Per our compliance rules, minimum key size is 2048 bits (RSA) and SHA-1 signatures are prohibited for all new issuances.`,

  'What is our policy for self-signed certificates?': `Per our **Certificate Compliance Policy (CCP-2024-003)**, self-signed certificates are classified as **NON_COMPLIANT** with **HIGH severity**.\n\n**Policy Details:**\n- Self-signed certificates are **prohibited in production environments**\n- Exception: Internal development/test environments (must be tagged as non-production)\n- Grace period: 90 days for migration to CA-issued certificates\n- Escalation: Auto-ticket generated after 60 days of non-compliance\n\n**Current State:**\n- ~1.9M self-signed certificates in inventory\n- Primarily concentrated in IoT devices (67%) and Partner networks (22%)\n- Trending down 5% week-over-week due to ACME auto-enrollment\n\n**Remediation Path:**\n1. Enroll device in ACME auto-renewal (preferred)\n2. Issue certificate from Comcast Internal CA (for internal services)\n3. Purchase from approved CA partner (DigiCert, Let's Encrypt, Sectigo)\n\n**SLA:** All self-signed certificates must be remediated within 90 days of detection.`,

  'What is the compliance rate by region?': `Overall compliance rate is **75.8%** across all regions.\n\n| Region | Total Certs | Compliant | Compliance % | Trend |\n|--------|------------|-----------|-------------|-------|\n| EU | 15.0M | 11.99M | 79.9% | ↑ +1.2% |\n| NA | 22.5M | 17.80M | 79.1% | → stable |\n| APAC | 7.5M | 5.35M | 71.3% | ↑ +0.8% |\n| LATAM | 5.0M | 2.87M | 57.4% | ↓ -0.5% |\n\n**Analysis:**\n- EU leads due to strict GDPR-aligned policies and mature partner ecosystem\n- LATAM lags due to high IoT self-signed rates and fewer ACME-enrolled devices\n- APAC improving from dedicated compliance push in Q1\n\n**Target:** 85% global compliance by end of Q3 2026`,

  'How do I remediate a self-signed certificate?': `**Remediation Steps for Self-Signed Certificates:**\n\n**Option 1: ACME Auto-Enrollment (Recommended)**\n1. Verify device supports ACME protocol (RFC 8555)\n2. Configure device to point to Comcast ACME endpoint\n3. Trigger initial enrollment: device generates CSR → CA issues cert\n4. Auto-renewal kicks in at 30 days before expiry\n\n**Option 2: Manual CA Issuance**\n1. Generate CSR on the device/server\n2. Submit to Comcast Internal CA (for internal) or DigiCert (for partner/external)\n3. Install issued certificate + intermediate chain\n4. Verify chain validity: \`openssl verify -CAfile chain.pem cert.pem\`\n\n**Option 3: Let's Encrypt (External-facing)**\n1. Install certbot or equivalent ACME client\n2. Run: \`certbot certonly --dns-01 -d device.comcast.net\`\n3. Configure auto-renewal cron job\n\n**Validation:**\n- Certificate should show \`Issuer: CN=Comcast IoT Device CA G2\` (or equivalent)\n- Chain depth should be 2-3 (not 1, which indicates self-signed)\n- Key size ≥ 2048 bits (RSA) or ≥ 256 bits (ECDSA)\n\n**Timeline:** Complete remediation within 90 days per CCP-2024-003.`,

  'Show certificates by device type and data center': `Certificate distribution by device type and data center:\n\n| Data Center | IoT | Streaming | Gateway | Server | Partner | Total |\n|-------------|-----|-----------|---------|--------|---------|-------|\n| PHI-DC-01 | 2.1M | 1.8M | 890K | 620K | 410K | 5.8M |\n| CHI-DC-01 | 1.9M | 1.5M | 780K | 550K | 380K | 5.1M |\n| DEN-DC-01 | 1.4M | 1.1M | 620K | 430K | 290K | 3.8M |\n| LON-DC-01 | 1.8M | 1.6M | 750K | 520K | 360K | 5.0M |\n| FRA-DC-01 | 1.6M | 1.4M | 680K | 470K | 330K | 4.5M |\n\n**Key Observations:**\n- IoT devices dominate across all data centers (35-40% of total)\n- Philadelphia (PHI-DC-01) is the largest facility by certificate volume\n- Streaming certificates are concentrated in Tier-1 DCs\n- Partner certificates are evenly distributed across regions`
};

export async function POST(req: NextRequest) {
  const body = await req.json();
  const userMessage = body.messages?.[body.messages.length - 1]?.content || '';
  const stream = body.stream !== false;

  if (CACHED_RESPONSES[userMessage]) {
    const cached = CACHED_RESPONSES[userMessage];
    if (stream) {
      return new Response(
        new ReadableStream({
          start(controller) {
            const words = cached.split(' ');
            let i = 0;
            const interval = setInterval(() => {
              if (i < words.length) {
                const chunk = (i === 0 ? '' : ' ') + words[i];
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ delta: chunk })}\n\n`));
                i++;
              } else {
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ done: true })}\n\n`));
                controller.close();
                clearInterval(interval);
              }
            }, 15);
          }
        }),
        { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' } }
      );
    }
    return Response.json({ text: cached });
  }

  const messages = (body.messages || []).map((m: any) => ({
    role: m.role,
    content: [{ type: 'text', text: m.content }]
  }));

  const token = getOAuthToken();
  const host = getSnowflakeHost();
  const [db, schema, name] = AGENT_FQN.split('.');
  const url = `https://${host}/api/v2/databases/${db}/schemas/${schema}/agents/${name}:run`;

  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': stream ? 'text/event-stream' : 'application/json',
        'X-Snowflake-Authorization-Token-Type': 'OAUTH'
      },
      body: JSON.stringify({ messages, stream })
    });

    if (!resp.ok) {
      const errText = await resp.text();
      return Response.json({ error: `Agent API ${resp.status}: ${errText.substring(0, 500)}` }, { status: 500 });
    }

    if (stream && resp.body) {
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();

      return new Response(
        new ReadableStream({
          async start(controller) {
            let currentEvent = '';
            let buffer = '';
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                  if (line.startsWith('event: ')) {
                    currentEvent = line.slice(7).trim();
                    continue;
                  }
                  if (!line.startsWith('data: ')) continue;
                  if (currentEvent.includes('thinking')) continue;

                  const dataStr = line.slice(6);
                  if (dataStr === '[DONE]') continue;

                  try {
                    const data = JSON.parse(dataStr);
                    if (currentEvent === 'response.text.delta' && data.text) {
                      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ delta: data.text })}\n\n`));
                    } else if (currentEvent === 'response' && data.content) {
                      const text = data.content.find((c: any) => c.type === 'text')?.text;
                      if (text) {
                        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ delta: text })}\n\n`));
                      }
                    } else if (currentEvent === 'done') {
                      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ done: true })}\n\n`));
                    }
                  } catch {}
                }
              }
              controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ done: true })}\n\n`));
              controller.close();
            } catch (e) {
              controller.close();
            }
          }
        }),
        { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' } }
      );
    }

    const text = await resp.text();
    let parsed: any;
    try { parsed = JSON.parse(text); } catch { parsed = { raw: text }; }
    return Response.json(extractResponse(parsed));
  } catch (e: any) {
    return Response.json({ error: `Fetch failed: ${e.message}` }, { status: 500 });
  }
}

function extractResponse(payload: any): any {
  let textParts: string[] = [];
  let sql: string | undefined;
  let sources: any[] = [];
  const walk = (obj: any) => {
    if (!obj) return;
    if (Array.isArray(obj)) { obj.forEach(walk); return; }
    if (typeof obj !== 'object') return;
    if (obj.type === 'text' && obj.text) textParts.push(obj.text);
    if (obj.type === 'tool_results' && obj.tool_results) walk(obj.tool_results);
    if (obj.statement) sql = obj.statement;
    if (obj.sql) sql = obj.sql;
    if (obj.searchResults) sources.push(...obj.searchResults.map((s: any) => ({ title: s.title || s.doc_id, doc_id: s.doc_id })));
    Object.values(obj).forEach(walk);
  };
  walk(payload);
  return { text: textParts.join('\n').trim() || 'No response.', sql, sources: sources.length ? sources : undefined };
}
