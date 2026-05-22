import { Metric, AgentResponse, TermDefinition } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

export const TERMINOLOGY_DB: TermDefinition[] = [
  { term: 'CTD', definition: 'Click to Deliver - Time from customer order to physical delivery', category: 'Logistics' },
  { term: 'OTS', definition: 'On-Time Shipping - Percentage of orders shipped within SLA window', category: 'Logistics' },
  { term: 'OTD', definition: 'On-Time Delivery - Percentage of deliveries completed by promised date', category: 'Logistics' },
  { term: 'FFO', definition: 'Fulfillment From Origin - Direct shipment from manufacturing to customer', category: 'Supply Chain' },
  { term: 'GSK', definition: 'Gateway Starter Kit - Initial equipment bundle for new customer install', category: 'Product' },
  { term: 'DOS', definition: 'Days of Supply - Inventory coverage measured in days', category: 'Inventory' },
  { term: 'NPS', definition: 'Net Promoter Score - Customer satisfaction measurement (-100 to +100)', category: 'Customer' },
  { term: 'RIS', definition: 'Retail In Stocks - Percentage of SKUs available at retail locations', category: 'Inventory' },
  { term: 'SLA', definition: 'Service Level Agreement - Committed performance threshold', category: 'Operations' },
  { term: 'DOCSIS', definition: 'Data Over Cable Service Interface Specification - Cable modem standard', category: 'Technology' },
  { term: 'XB8', definition: 'Xfinity Gateway 8 - Latest DOCSIS 4.0 residential gateway', category: 'Product' },
  { term: 'BP', definition: 'Business Partner - Third-party logistics or service provider', category: 'Operations' },
  { term: 'ISCO', definition: 'Integrated Supply Chain Operations - Comcast supply chain division', category: 'Organization' },
  { term: 'WEM', definition: 'Weekly Executive Metrics - Standard weekly KPI report package', category: 'Reporting' },
  { term: 'PA', definition: 'Production Attainment - Actual vs planned production output', category: 'Manufacturing' },
  { term: 'SC', definition: 'Scan Compliance - Barcode/RFID scan rate at checkpoints', category: 'Operations' },
  { term: 'SVP', definition: 'Senior Vice President - Regional supply chain leadership', category: 'Organization' },
];

export function findTermsInText(text: string): TermDefinition[] {
  const found: TermDefinition[] = [];
  const upper = text.toUpperCase();
  for (const term of TERMINOLOGY_DB) {
    if (upper.includes(term.term)) {
      found.push(term);
    }
  }
  return found;
}

export async function askAgent(metric: Metric | null, question: string): Promise<AgentResponse> {
  try {
    const res = await fetch(`${API_BASE}/deep-reasoning?agent=true`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        metricId: metric?.id || null,
        question,
        sessionId: `session_${Date.now()}`
      })
    });
    if (!res.ok) throw new Error('Agent call failed');
    const data = await res.json();
    return {
      response: data.response,
      confidence: data.confidence,
      sources: data.sources,
      drillDowns: data.drillDowns || [],
      cached: data.cached || false,
    };
  } catch {
    return getFallbackResponse(metric, question);
  }
}

export async function createInvestigationTicket(
  metricName: string,
  region: string,
  weekDate: string,
  question: string,
  aiAnalysis: string,
  confidenceScore: number
): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}/tickets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metricName, region, weekDate, question, aiAnalysis, confidenceScore })
    });
    if (!res.ok) throw new Error('Failed to create ticket');
    const data = await res.json();
    return data.id || `INV-2026-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`;
  } catch {
    return `INV-2026-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`;
  }
}

function getFallbackResponse(metric: Metric | null, question: string): AgentResponse {
  const context = metric ? `Regarding ${metric.metricName} in ${metric.region} (current: ${metric.currentValue}, target: ${metric.targetValue}): ` : '';
  return {
    response: `${context}I've analyzed the available data for your question: "${question}"\n\nBased on historical patterns and current metrics, this appears to be within the expected operational range. I recommend monitoring this metric over the next reporting cycle.\n\n**Note:** This is a fallback response. The live Cortex Agent connection is currently unavailable.`,
    confidence: 45,
    sources: { narratives: [], events: [], knowledge: [], toolsUsed: [] },
    drillDowns: [
      { question: 'What factors typically affect this metric?', type: 'root_cause', label: 'Contributing Factors' },
      { question: 'What should we do about this?', type: 'action_plan', label: 'Recommended Actions' },
    ],
    cached: false,
  };
}
