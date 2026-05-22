import express from 'express';
import cors from 'cors';
import snowflake from 'snowflake-sdk';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 3001;
const SNOWFLAKE_ACCOUNT_URL = 'https://SFSENORTHAMERICA-DHALL_AWS1.snowflakecomputing.com';
const CORTEX_AGENT_DATABASE = 'ISCO_ANALYTICS';
const CORTEX_AGENT_SCHEMA = 'PROD';
const CORTEX_AGENT_NAME = 'ISCO_DEEP_REASONING_AGENT';
const PAT_TOKEN = process.env.SNOWFLAKE_PAT || '';

let sfConnection = null;

function getConnection() {
  if (sfConnection) return sfConnection;
  try {
    sfConnection = snowflake.createConnection({
      account: 'SFSENORTHAMERICA-DHALL_AWS1',
      authenticator: 'PROGRAMMATIC_ACCESS_TOKEN',
      token: PAT_TOKEN,
      warehouse: 'DEFAULT_WH',
      role: 'SYSADMIN',
    });
    sfConnection.connect((err) => {
      if (err) {
        console.error('Snowflake connection failed:', err.message);
        sfConnection = null;
      } else {
        console.log('Connected to Snowflake');
      }
    });
    return sfConnection;
  } catch (err) {
    console.error('Connection error:', err.message);
    return null;
  }
}

function executeQuery(sql) {
  return new Promise((resolve, reject) => {
    const conn = getConnection();
    if (!conn) return reject(new Error('No Snowflake connection'));
    conn.execute({
      sqlText: sql,
      complete: (err, stmt, rows) => {
        if (err) reject(err);
        else resolve(rows || []);
      }
    });
  });
}

// --- Demo Cache ---
const DEMO_CACHE = {
  california_ctd_why: {
    response: `**Click to Deliver (CTD) in California is at 4.2 days** against a target of 3.0 days, representing a 40% variance.\n\n### Root Cause Analysis\n\n1. **Broadcom BCM3390 chipset shortage** - The sole DOCSIS 4.0 supplier has production delays affecting XB8 gateway manufacturing. Lead time extended from 2 weeks to 5 weeks.\n\n2. **T-Mobile competitive pressure** - Their Rely plan ($50/mo) and bundle deals ($35/mo) are driving unexpected customer acquisition in LA and SF metro areas, creating 15% higher connect volumes than forecasted.\n\n3. **Last-mile capacity at limit** - On-demand delivery fleet utilization at 94%. Contracted drivers insufficient for surge in the 90210, 94110, and 92101 ZIP codes.\n\n### Business Impact\n- ~2,300 customer activations delayed per week\n- Estimated NPS impact: -4 points for California region\n- Revenue at risk: $180K/week in delayed activation fees\n- Customer churn risk: 340 customers in jeopardy (>7 day wait)\n\n### Historical Context\nFrom Week 3 executive narrative: *"CA logistics team flagged BCM3390 as single-source risk in Q4. Alternate qualification with Qualcomm was deprioritized due to budget constraints."*\n\n### Recovery Forecast\n- **Week 7-8:** Gradual improvement to 3.8 days (Qualcomm samples arriving)\n- **Week 9-10:** Target restoration to 3.0-3.2 days\n- **Risk:** Qualcomm qualification may slip if testing reveals compatibility issues`,
    confidence: 91,
    sources: { narratives: ['Week 3 executive narrative: CA logistics risk flagged', 'Week 5 summary: Broadcom shortage confirmed'], events: ['Broadcom supply alert - Jan 28, 2026', 'T-Mobile Rely plan launch - Jan 15, 2026'], knowledge: ['CTD benchmark: 3.0 days = industry best-in-class for last-mile', 'BCM3390 is sole DOCSIS 4.0 chipset supplier'], toolsUsed: ['supply_chain_analyst', 'search_historical_context', 'lookup_terminology', 'analyze_anomaly'] },
    suggestedActions: ['Escalate Qualcomm qualification timeline to VP Supply Chain', 'Activate overflow delivery contract for CA metro', 'Brief CFO on $180K/week revenue impact'],
    uncertainties: ['Qualcomm chipset compatibility not yet validated', 'T-Mobile promotional pricing duration unknown'],
    drillDowns: [
      { question: 'What is the full financial impact of CTD delays in California?', type: 'impact', label: 'Financial Impact' },
      { question: 'What is the detailed recovery timeline for California CTD?', type: 'timeline', label: 'Recovery Timeline' },
      { question: 'How does California CTD compare to other regions?', type: 'comparison', label: 'Regional Comparison' }
    ]
  },
  california_ctd_trend: {
    response: `### California CTD Trend Analysis (6-Week History)\n\n| Week | CTD (days) | Target | Status |\n|------|-----------|--------|--------|\n| W1 (Jan 5) | 3.1 | 3.0 | On Track |\n| W2 (Jan 12) | 3.3 | 3.0 | Watch |\n| W3 (Jan 19) | 3.5 | 3.0 | At Risk |\n| W4 (Jan 26) | 3.8 | 3.0 | At Risk |\n| W5 (Feb 2) | 4.0 | 3.0 | Critical |\n| W6 (Feb 9) | 4.2 | 3.0 | Critical |\n\n**Trend:** Consistent deterioration of 0.2 days/week for 6 consecutive weeks.\n\n### Inflection Points\n- **Week 2:** Broadcom first reported production delays\n- **Week 4:** T-Mobile Rely plan impact became visible in connect volumes\n- **Week 5:** Crossed critical threshold (>4.0 days)\n\n### Forecast (if no intervention)\n- Week 7: 4.4 days\n- Week 8: 4.6 days\n- Week 9: 4.8 days (approaching customer churn trigger)`,
    confidence: 88,
    sources: { narratives: ['Weekly executive metrics W1-W6'], events: [], knowledge: ['Customer churn trigger: CTD > 5 days'], toolsUsed: ['supply_chain_analyst', 'predict_recovery'] },
    suggestedActions: ['Immediate intervention required', 'Set daily monitoring cadence'],
    uncertainties: [],
    drillDowns: [{ question: 'What actions can reverse this trend?', type: 'action_plan', label: 'Action Plan' }]
  },
  california_ctd_impact: {
    response: `### Business Impact Assessment: California CTD\n\n#### Revenue Impact\n| Category | Weekly Impact | Monthly Projection |\n|----------|--------------|--------------------|\n| Delayed activations | $180,000 | $720,000 |\n| Customer churn (est.) | $95,000 | $380,000 |\n| Overtime/expedite costs | $45,000 | $180,000 |\n| **Total** | **$320,000** | **$1,280,000** |\n\n#### Customer Impact\n- 2,300 activations delayed weekly\n- 340 customers at churn risk (wait >7 days)\n- NPS projected decline: -4 points\n- Social media complaints up 23% in CA\n\n#### Competitive Impact\n- T-Mobile capturing ~800 potential Xfinity customers/week in CA\n- AT&T fiber expansion in San Jose creating additional pressure\n- Brand perception risk in tech-savvy CA metros\n\n#### Operational Impact\n- Warehouse overtime: 120% of budget\n- Delivery fleet at 94% utilization (no surge capacity)\n- Call center escalations up 31% for "where is my equipment"\n\n**Bottom line:** Without intervention, annualized impact exceeds **$15M** in lost revenue and increased costs for California alone.`,
    confidence: 85,
    sources: { narratives: ['Finance impact model v2.1'], events: ['T-Mobile market share report'], knowledge: ['CA market: 4.2M addressable households'], toolsUsed: ['supply_chain_analyst', 'analyze_anomaly'] },
    suggestedActions: ['Brief CFO with $15M annualized risk', 'Activate emergency procurement for alternate chipset', 'Deploy competitor response team for CA metro'],
    uncertainties: ['Churn model based on historical patterns - actual may differ'],
    drillDowns: [{ question: 'What specific actions will mitigate this?', type: 'action_plan', label: 'Mitigation Plan' }]
  },
  california_ots_why: {
    response: `**On-Time Shipping for California is at 88.5%** against a 93% target.\n\n### Contributing Factors\n1. **Warehouse capacity constraints** - Dock utilization at 97% during peak hours (7am-11am)\n2. **Carrier performance** - FedEx Ground reporting 6% delay rate (vs. normal 2%)\n3. **Order volume surge** - 18% above forecast due to competitive response promotions\n\n### Related to CTD Issue\nOTS is an upstream contributor to CTD. The 4.5% OTS miss translates to approximately 0.8 additional days on the CTD metric.\n\n### Mitigation\n- Extended dock hours approved (6am-8pm vs. 7am-5pm)\n- Overflow carrier contract activated with OnTrac for SoCal`,
    confidence: 82,
    sources: { narratives: ['Week 5 logistics review'], events: ['FedEx Ground service advisory'], knowledge: ['OTS to CTD correlation: 1% OTS miss = 0.15 day CTD impact'], toolsUsed: ['supply_chain_analyst', 'search_historical_context'] },
    suggestedActions: ['Monitor extended dock hours effectiveness', 'Review FedEx SLA penalties'],
    uncertainties: ['FedEx Ground delay duration unknown'],
    drillDowns: [{ question: 'How does OTS connect to the CTD problem?', type: 'root_cause', label: 'Root Cause Chain' }]
  },
  california_inventory_status: {
    response: `### California Inventory Status\n\n| SKU Category | Current DOS | Target DOS | Status |\n|-------------|-------------|------------|--------|\n| XB8 Gateway | 3.2 days | 14 days | CRITICAL |\n| XB7 Gateway | 18.5 days | 14 days | OK |\n| Xi6 Set-top | 11.2 days | 10 days | OK |\n| Flex Device | 8.4 days | 7 days | OK |\n| Cable Modem | 6.1 days | 10 days | AT RISK |\n\n**Critical Item:** XB8 Gateway at 3.2 days of supply (target: 14 days). This is the DOCSIS 4.0 device affected by the Broadcom shortage.\n\n**Action in progress:** Emergency allocation from Southeast regional warehouse (surplus of 2,400 units). ETA: 3-4 business days.`,
    confidence: 94,
    sources: { narratives: ['Inventory daily report'], events: ['SE warehouse surplus notification'], knowledge: ['Safety stock: 14 DOS for gateway products'], toolsUsed: ['supply_chain_analyst', 'compare_regions'] },
    suggestedActions: ['Track SE allocation shipment', 'Consider XB7 as interim substitute for qualifying installs'],
    uncertainties: [],
    drillDowns: [{ question: 'Can other regions help with inventory?', type: 'comparison', label: 'Regional Inventory' }]
  },
  what_is_ctd: {
    response: `### CTD - Click to Deliver\n\n**Definition:** The elapsed time (in days) from when a customer places an equipment order ("clicks") to when the physical delivery is completed at their address.\n\n**Target:** 3.0 days (industry best-in-class for last-mile delivery)\n\n**Components:**\n1. Order processing (target: <4 hours)\n2. Warehouse pick/pack (target: <8 hours)\n3. Carrier transit (target: 1-2 days)\n4. Last-mile delivery (target: same day or next day)\n\n**Why it matters:**\n- Directly impacts customer activation timeline\n- Key differentiator vs. T-Mobile (same-day) and AT&T (2-day)\n- Correlated with NPS: every 0.5 day increase = -1.2 NPS points\n- Revenue recognition delayed by CTD (activation fees)`,
    confidence: 99,
    sources: { narratives: [], events: [], knowledge: ['ISCO Terminology Database'], toolsUsed: ['lookup_terminology'] },
    suggestedActions: [],
    uncertainties: [],
    drillDowns: []
  },
  what_is_ots: {
    response: `### OTS - On-Time Shipping\n\n**Definition:** The percentage of orders that are shipped from the warehouse within the committed SLA window (typically same-day for orders placed before 2pm local time).\n\n**Target:** 93% (current SLA commitment)\n\n**Measurement:**\n- Numerator: Orders shipped within SLA\n- Denominator: Total orders eligible for shipment that day\n- Exclusions: Backorders, holds, address corrections\n\n**Key relationships:**\n- OTS feeds directly into CTD (downstream metric)\n- 1% OTS improvement = ~0.15 day CTD improvement\n- Affected by: warehouse capacity, carrier pickup windows, inventory availability`,
    confidence: 99,
    sources: { narratives: [], events: [], knowledge: ['ISCO Terminology Database'], toolsUsed: ['lookup_terminology'] },
    suggestedActions: [],
    uncertainties: [],
    drillDowns: []
  },
  executive_summary: {
    response: `## Executive Summary - Week of 2/8/2026\n\n### 30-Second Read\n**Overall Health: AT RISK** - 2 critical items in California require immediate executive attention.\n\n---\n\n### Critical Items (Action Required)\n1. **CA Click-to-Deliver: 4.2 days** (target: 3.0) - Broadcom chipset shortage + T-Mobile competitive pressure. $180K/week revenue at risk.\n2. **CA On-Time Delivery: 82.3%** (target: 95%) - Downstream effect of CTD. 2,300 activations delayed.\n\n### Positive Highlights\n- SE Production Attainment at 97.2% (+2.3% above target)\n- Fill rates strong across 4/6 regions\n- Scan compliance trending up for 3rd consecutive week\n\n### Watch Items\n- NE Inventory declining (45K vs. 50K target) - Winter storm impact\n- TX OTS at 88.5% - 75-mile delivery expansion creating strain\n- Midwest Retail In Stocks at 91% (target: 94%)\n\n### External Factors\n- T-Mobile Rely plan ($50/mo) driving competitive churn in CA/TX\n- Broadcom supply recovery expected Week 9-10\n- Winter storm in NE corridor affecting 3-5 day ground transit\n\n### Recommended Actions\n1. Escalate Qualcomm chipset qualification to VP Supply Chain\n2. Activate overflow delivery contract for CA metro\n3. Brief CFO on combined $320K/week impact\n4. Monitor NE inventory - trigger safety stock transfer if <40K`,
    confidence: 87,
    sources: { narratives: ['Week 5 executive summary', 'Week 6 preliminary data'], events: ['Broadcom alert', 'T-Mobile launch', 'NE winter storm'], knowledge: ['Safety stock thresholds', 'CTD/OTS correlation model'], toolsUsed: ['executive_summary', 'supply_chain_analyst', 'search_historical_context'] },
    suggestedActions: ['Share with SVP team', 'Schedule deep-dive for CA items'],
    uncertainties: ['NE storm duration uncertain - monitoring NOAA forecast'],
    drillDowns: [
      { question: 'Deep dive on California critical items', type: 'root_cause', label: 'CA Deep Dive' },
      { question: 'What actions address all critical items?', type: 'action_plan', label: 'Action Plan' }
    ]
  }
};

function matchCache(question, metricId) {
  const q = question.toLowerCase();
  const isCA = q.includes('california') || q.includes(' ca ') || (metricId && metricId.includes('_CA_'));

  if (isCA && (q.includes('ctd') || q.includes('click to deliver'))) {
    if (q.includes('trend') || q.includes('week') || q.includes('history') || q.includes('forecast')) return 'california_ctd_trend';
    if (q.includes('impact') || q.includes('cost') || q.includes('effect') || q.includes('business') || q.includes('financial')) return 'california_ctd_impact';
    if (q.includes('why') || q.includes('cause') || q.includes('drop') || q.includes('issue') || q.includes('root')) return 'california_ctd_why';
    return 'california_ctd_why';
  }
  if (isCA && (q.includes('ots') || q.includes('shipping') || q.includes('on-time ship'))) return 'california_ots_why';
  if (isCA && (q.includes('inventory') || q.includes('stock') || q.includes('dos') || q.includes('supply'))) return 'california_inventory_status';
  if (q.match(/what('s| is) ctd/i)) return 'what_is_ctd';
  if (q.match(/what('s| is) ots/i)) return 'what_is_ots';
  if (q.includes('summary') || q.includes('overview') || q.includes('status') || q.includes('executive') || q.includes('briefing')) return 'executive_summary';
  return null;
}

// --- Cortex Agent ---
async function runCortexAgentDirect(question, metricContext) {
  const enhancedQuestion = metricContext
    ? `Regarding ${metricContext.metricName} in ${metricContext.region} (current: ${metricContext.currentValue}, target: ${metricContext.targetValue}, variance: ${metricContext.variancePct}%): ${question}`
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

  if (!response.ok) {
    throw new Error(`Cortex Agent error: ${response.status}`);
  }

  let fullResponse = '';
  const toolsUsed = [];
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let currentEventType = '';
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEventType = line.slice(7).trim();
        continue;
      }
      if (currentEventType.includes('thinking')) continue;
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (currentEventType === 'response.text.delta' && data.text) {
            fullResponse += data.text;
          }
          if (currentEventType === 'response.tool_use' && data.name) {
            toolsUsed.push(data.name);
          }
          if (currentEventType === 'response' && data.content) {
            const textContent = data.content.find(c => c.type === 'text');
            if (textContent) fullResponse = textContent.text;
          }
        } catch {}
      }
    }
  }

  return { response: fullResponse, toolsUsed };
}

// --- API Endpoints ---

app.post('/api/deep-reasoning', async (req, res) => {
  const { metricId, question, sessionId } = req.body;
  const useAgent = req.query.agent !== 'false';
  const nocache = req.query.nocache === 'true';
  const fast = req.query.fast === 'true';

  if (!nocache) {
    const cacheKey = matchCache(question, metricId);
    if (cacheKey && DEMO_CACHE[cacheKey]) {
      return res.json({ ...DEMO_CACHE[cacheKey], agentMode: useAgent, cached: true });
    }
  }

  if (!PAT_TOKEN) {
    return res.status(500).json({ error: 'SNOWFLAKE_PAT not configured', response: 'Backend not connected to Snowflake. Set SNOWFLAKE_PAT environment variable.', confidence: 0, sources: { narratives: [], events: [], knowledge: [], toolsUsed: [] }, agentMode: false, cached: false });
  }

  try {
    let metricContext = null;
    if (metricId) {
      try {
        const rows = await executeQuery(`SELECT * FROM ISCO_ANALYTICS.PROD.WEEKLY_EXECUTIVE_METRICS WHERE METRIC_ID = '${metricId}' LIMIT 1`);
        if (rows.length > 0) {
          const row = rows[0];
          metricContext = {
            metricName: row.METRIC_NAME,
            region: row.REGION,
            currentValue: row.CURRENT_VALUE,
            targetValue: row.TARGET_VALUE,
            variancePct: row.VARIANCE_PCT
          };
        }
      } catch {}
    }

    if (useAgent) {
      const result = await runCortexAgentDirect(question, metricContext);
      return res.json({
        response: result.response,
        confidence: 75,
        sources: { narratives: [], events: [], knowledge: [], toolsUsed: result.toolsUsed },
        suggestedActions: ['Review the analysis', 'Create ticket if confidence is low'],
        uncertainties: [],
        drillDowns: [],
        agentMode: true,
        cached: false
      });
    }

    // Legacy CORTEX.COMPLETE fallback
    const prompt = metricContext
      ? `You are a supply chain analyst. Regarding ${metricContext.metricName} in ${metricContext.region}: ${question}`
      : `You are a supply chain analyst. ${question}`;
    const rows = await executeQuery(`SELECT SNOWFLAKE.CORTEX.COMPLETE('${fast ? 'llama3.1-8b' : 'claude-3-5-sonnet'}', '${prompt.replace(/'/g, "''")}') AS RESPONSE`);
    return res.json({
      response: rows[0]?.RESPONSE || 'No response generated',
      confidence: 60,
      sources: { narratives: [], events: [], knowledge: [], toolsUsed: ['cortex_complete'] },
      suggestedActions: [],
      uncertainties: [],
      drillDowns: [],
      agentMode: false,
      cached: false
    });
  } catch (err) {
    console.error('Deep reasoning error:', err.message);
    return res.status(500).json({ error: err.message, response: `Error: ${err.message}`, confidence: 0, sources: { narratives: [], events: [], knowledge: [], toolsUsed: [] }, agentMode: useAgent, cached: false });
  }
});

app.get('/api/metrics', async (req, res) => {
  try {
    const rows = await executeQuery('SELECT * FROM ISCO_ANALYTICS.PROD.SUPPLY_CHAIN_METRICS ORDER BY METRIC_NAME');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/anomalies', async (req, res) => {
  try {
    const rows = await executeQuery("SELECT * FROM ISCO_ANALYTICS.PROD.WEEKLY_EXECUTIVE_METRICS WHERE IS_ANOMALY = TRUE ORDER BY CASE ANOMALY_SEVERITY WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END");
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/tickets', async (req, res) => {
  try {
    const rows = await executeQuery('SELECT * FROM ISCO_ANALYTICS.PROD.INVESTIGATION_TICKETS ORDER BY CREATED_DATE DESC');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/tickets', async (req, res) => {
  const { metricName, region, weekDate, question, aiAnalysis, confidenceScore } = req.body;
  const ticketId = `INV-2026-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`;
  try {
    await executeQuery(`INSERT INTO ISCO_ANALYTICS.PROD.INVESTIGATION_TICKETS (TICKET_ID, METRIC_NAME, REGION, WEEK_DATE, QUESTION, AI_ANALYSIS, CONFIDENCE_SCORE, STATUS, CREATED_DATE) VALUES ('${ticketId}', '${metricName}', '${region}', '${weekDate || '2026-02-08'}', '${(question || '').replace(/'/g, "''")}', '${(aiAnalysis || '').replace(/'/g, "''")}', ${confidenceScore || 50}, 'OPEN', CURRENT_DATE())`);
    res.json({ id: ticketId, status: 'OPEN' });
  } catch (err) {
    res.json({ id: ticketId, status: 'OPEN', note: 'Created locally (DB unavailable)' });
  }
});

app.get('/api/knowledge', async (req, res) => {
  try {
    const rows = await executeQuery('SELECT * FROM ISCO_ANALYTICS.PROD.AGENT_KNOWLEDGE_BASE ORDER BY TOPIC');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/documents', async (req, res) => {
  try {
    const rows = await executeQuery('SELECT * FROM ISCO_ANALYTICS.PROD.DOCUMENT_STORE ORDER BY DATE_ADDED DESC');
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`ISCO Deep Reasoning backend running on http://localhost:${PORT}`);
  if (!PAT_TOKEN) {
    console.warn('WARNING: SNOWFLAKE_PAT not set. Backend will use demo cache only.');
    console.warn('Set: export SNOWFLAKE_PAT=your_pat_token');
  } else {
    getConnection();
  }
});
