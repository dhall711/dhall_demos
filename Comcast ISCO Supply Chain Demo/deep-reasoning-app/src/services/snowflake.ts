import { Metric, Ticket, DeepReasoningResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

export async function getMetrics(): Promise<Metric[]> {
  try {
    const res = await fetch(`${API_BASE}/metrics`);
    if (!res.ok) throw new Error('Failed to fetch metrics');
    const data = await res.json();
    return data.map(normalizeMetric);
  } catch {
    return getMockMetrics();
  }
}

export async function getAnomalies(): Promise<Metric[]> {
  try {
    const res = await fetch(`${API_BASE}/anomalies`);
    if (!res.ok) throw new Error('Failed to fetch anomalies');
    const data = await res.json();
    return data.map(normalizeMetric);
  } catch {
    return getMockMetrics().filter(m => m.isAnomaly);
  }
}

export async function getTickets(): Promise<Ticket[]> {
  try {
    const res = await fetch(`${API_BASE}/tickets`);
    if (!res.ok) throw new Error('Failed to fetch tickets');
    return await res.json();
  } catch {
    return getMockTickets();
  }
}

export async function createTicket(metricId: string, question: string, aiResponse: string): Promise<Ticket> {
  const res = await fetch(`${API_BASE}/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metricId, question, aiResponse })
  });
  if (!res.ok) throw new Error('Failed to create ticket');
  return await res.json();
}

export async function getDeepReasoning(
  metricId: string,
  question: string,
  options: { stream?: boolean; agent?: boolean; nocache?: boolean; fast?: boolean } = {}
): Promise<DeepReasoningResponse> {
  const params = new URLSearchParams();
  if (options.stream) params.set('stream', 'true');
  if (options.agent !== false) params.set('agent', 'true');
  if (options.nocache) params.set('nocache', 'true');
  if (options.fast) params.set('fast', 'true');

  try {
    const res = await fetch(`${API_BASE}/deep-reasoning?${params}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metricId, question })
    });
    if (!res.ok) throw new Error('Failed to get deep reasoning');
    return await res.json();
  } catch {
    return getMockDeepReasoning(question);
  }
}

function normalizeMetric(raw: Record<string, unknown>): Metric {
  return {
    id: raw.METRIC_ID as string || raw.id as string || '',
    metricName: raw.METRIC_NAME as string || raw.metricName as string || '',
    region: raw.REGION as string || raw.region as string || '',
    currentValue: parseFloat(String(raw.CURRENT_VALUE ?? raw.currentValue ?? 0)),
    targetValue: parseFloat(String(raw.TARGET_VALUE ?? raw.targetValue ?? 0)),
    variancePct: parseFloat(String(raw.VARIANCE_PCT ?? raw.variancePct ?? 0)),
    trend: parseFloat(String(raw.TREND ?? raw.trend ?? 0)),
    status: raw.STATUS as string || raw.status as string || 'normal',
    anomalySeverity: (raw.ANOMALY_SEVERITY ?? raw.anomalySeverity ?? null) as Metric['anomalySeverity'],
    isAnomaly: Boolean(raw.IS_ANOMALY ?? raw.isAnomaly),
    weekDate: raw.WEEK_DATE as string || raw.weekDate as string || '',
    sparklineData: raw.sparklineData as number[] || undefined,
    isPositiveGood: raw.isPositiveGood as boolean | undefined,
  };
}

function getMockMetrics(): Metric[] {
  return [
    { id: 'WEM_2026W06_CA_OTD', metricName: 'On-Time Delivery', region: 'California', currentValue: 82.3, targetValue: 95.0, variancePct: -13.4, trend: -2.1, status: 'critical', anomalySeverity: 'CRITICAL', isAnomaly: true, weekDate: '2026-02-08', sparklineData: [94, 91, 88, 85, 83, 82], isPositiveGood: true },
    { id: 'WEM_2026W06_CA_CTD', metricName: 'Click to Deliver', region: 'California', currentValue: 4.2, targetValue: 3.0, variancePct: 40.0, trend: 0.3, status: 'critical', anomalySeverity: 'CRITICAL', isAnomaly: true, weekDate: '2026-02-08', sparklineData: [3.1, 3.3, 3.5, 3.8, 4.0, 4.2], isPositiveGood: false },
    { id: 'WEM_2026W06_TX_OTS', metricName: 'On-Time Shipping', region: 'Texas', currentValue: 88.5, targetValue: 93.0, variancePct: -4.8, trend: -1.5, status: 'at-risk', anomalySeverity: 'HIGH', isAnomaly: true, weekDate: '2026-02-08', sparklineData: [93, 92, 91, 90, 89, 88], isPositiveGood: true },
    { id: 'WEM_2026W06_NE_INV', metricName: 'Region Inventory', region: 'Northeast', currentValue: 45000, targetValue: 50000, variancePct: -10.0, trend: -500, status: 'at-risk', anomalySeverity: 'HIGH', isAnomaly: true, weekDate: '2026-02-08', sparklineData: [52000, 50000, 48000, 47000, 46000, 45000], isPositiveGood: true },
    { id: 'WEM_2026W06_SE_PA', metricName: 'Production Attainment', region: 'Southeast', currentValue: 97.2, targetValue: 95.0, variancePct: 2.3, trend: 0.5, status: 'on-track', anomalySeverity: null, isAnomaly: false, weekDate: '2026-02-08', sparklineData: [95, 96, 96, 97, 97, 97], isPositiveGood: true },
    { id: 'WEM_2026W06_MW_RIS', metricName: 'Retail In Stocks', region: 'Midwest', currentValue: 91.0, targetValue: 94.0, variancePct: -3.2, trend: -0.8, status: 'at-risk', anomalySeverity: 'MEDIUM', isAnomaly: true, weekDate: '2026-02-08', sparklineData: [94, 93, 93, 92, 91, 91], isPositiveGood: true },
    { id: 'WEM_2026W06_CA_GSK', metricName: 'GSK Click to Deliver', region: 'California', currentValue: 3.8, targetValue: 3.0, variancePct: 26.7, trend: 0.2, status: 'at-risk', anomalySeverity: 'MEDIUM', isAnomaly: true, weekDate: '2026-02-08', sparklineData: [3.0, 3.2, 3.3, 3.5, 3.6, 3.8], isPositiveGood: false },
    { id: 'WEM_2026W06_NW_SC', metricName: 'Scan Compliance', region: 'Northwest', currentValue: 96.5, targetValue: 98.0, variancePct: -1.5, trend: 0.3, status: 'on-track', anomalySeverity: 'LOW', isAnomaly: false, weekDate: '2026-02-08', sparklineData: [95, 95, 96, 96, 96, 97], isPositiveGood: true },
  ];
}

function getMockTickets(): Ticket[] {
  return [
    { id: 'INV-2026-0001', metricId: 'WEM_2026W06_CA_OTD', metricName: 'On-Time Delivery', region: 'California', question: 'Why is OTD dropping below 85%?', aiAnalysis: 'Multiple factors contributing: weather disruptions in distribution corridor, Broadcom chipset shortage affecting XB8 gateway fulfillment.', confidenceScore: 78, status: 'OPEN', assignedTo: 'Woods Eric', createdDate: '2026-02-08' },
    { id: 'INV-2026-0002', metricId: 'WEM_2026W06_CA_CTD', metricName: 'Click to Deliver', region: 'California', question: 'CTD exceeding 4 days - root cause?', aiAnalysis: 'Last-mile delivery capacity constrained. T-Mobile competitive pressure driving higher connect volumes in CA metro areas.', confidenceScore: 85, status: 'IN_PROGRESS', assignedTo: 'Chen Sarah', createdDate: '2026-02-07' },
    { id: 'INV-2026-0003', metricId: 'WEM_2026W06_TX_OTS', metricName: 'On-Time Shipping', region: 'Texas', question: 'Texas OTS declining - related to expansion?', aiAnalysis: 'On-demand delivery expansion to 75-mile radius straining shipping capacity.', confidenceScore: 91, status: 'RESOLVED', assignedTo: 'VOGEL Tom', createdDate: '2026-02-05', resolvedDate: '2026-02-08', resolution: 'Confirmed: 75-mile radius expansion causing delays. Mitigation plan approved.' },
  ];
}

function getMockDeepReasoning(question: string): DeepReasoningResponse {
  const lower = question.toLowerCase();
  if (lower.includes('california') && lower.includes('ctd')) {
    return {
      response: `**Click to Deliver (CTD) in California is at 4.2 days** against a target of 3.0 days.\n\n### Root Causes\n1. **Broadcom BCM3390 chipset shortage** - DOCSIS 4.0 gateway (XB8) production delayed 3 weeks\n2. **T-Mobile competitive pressure** - Their Rely plan ($50/mo) driving unexpected connect volume in LA/SF metro\n3. **Last-mile capacity** - On-demand delivery fleet at 94% utilization\n\n### Business Impact\n- Estimated 2,300 customer activations delayed this week\n- NPS impact: -4 points projected for CA region\n- Revenue at risk: ~$180K weekly\n\n### Recovery Timeline\nWith current mitigation (alternate supplier qualification + fleet expansion):\n- Week 1-2: Gradual improvement to 3.8 days\n- Week 3-4: Return to target range (3.0-3.2 days)`,
      confidence: 91,
      sources: { narratives: ['Week 5 exec summary: CA logistics strained'], events: ['Broadcom supply alert - Jan 28'], knowledge: ['CTD benchmark: 3.0 days = industry best-in-class'], toolsUsed: ['supply_chain_analyst', 'search_historical_context', 'lookup_terminology'] },
      suggestedActions: ['Escalate to VP Supply Chain', 'Review alternate supplier options'],
      uncertainties: ['Exact chipset delivery timeline from Broadcom unconfirmed'],
      drillDowns: [
        { question: 'What is the financial impact of CTD delays?', type: 'impact', label: 'Impact Analysis' },
        { question: 'When will CTD return to target?', type: 'timeline', label: 'Recovery Timeline' },
        { question: 'How does CA compare to other regions?', type: 'comparison', label: 'Regional Comparison' },
      ],
      agentMode: true,
      cached: false,
    };
  }
  return {
    response: `Based on my analysis of the available data and historical context:\n\n${question}\n\n### Key Findings\nI've reviewed the relevant metrics, historical narratives, and external events. The data suggests this is within normal operational variance, though I recommend monitoring over the next 2 weeks.\n\n### Recommendation\nContinue monitoring. If the trend persists beyond 2 weeks, escalate for investigation.`,
    confidence: 72,
    sources: { narratives: [], events: [], knowledge: [], toolsUsed: ['supply_chain_analyst'] },
    suggestedActions: ['Monitor for 2 weeks', 'Set alert threshold'],
    uncertainties: ['Limited historical data for this specific pattern'],
    drillDowns: [
      { question: 'What are the contributing factors?', type: 'root_cause', label: 'Root Cause' },
      { question: 'What actions should we take?', type: 'action_plan', label: 'Action Plan' },
    ],
    agentMode: true,
    cached: false,
  };
}
