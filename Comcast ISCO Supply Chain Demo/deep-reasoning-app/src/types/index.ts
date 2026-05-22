export interface Metric {
  id: string;
  metricName: string;
  region: string;
  currentValue: number;
  targetValue: number;
  variancePct: number;
  trend: number;
  status: string;
  anomalySeverity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | null;
  isAnomaly: boolean;
  weekDate: string;
  sparklineData?: number[];
  isPositiveGood?: boolean;
}

export interface Ticket {
  id: string;
  metricId: string;
  metricName: string;
  region: string;
  question: string;
  aiAnalysis: string;
  confidenceScore: number;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  assignedTo: string;
  createdDate: string;
  resolvedDate?: string;
  resolution?: string;
}

export interface DeepReasoningResponse {
  response: string;
  confidence: number;
  sources: {
    narratives: string[];
    events: string[];
    knowledge: string[];
    toolsUsed: string[];
  };
  suggestedActions: string[];
  uncertainties: string[];
  drillDowns: DrillDown[];
  agentMode: boolean;
  cached: boolean;
}

export interface DrillDown {
  question: string;
  type: 'impact' | 'timeline' | 'root_cause' | 'comparison' | 'action_plan';
  label: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  sources?: DeepReasoningResponse['sources'];
  drillDowns?: DrillDown[];
  isStreaming?: boolean;
}

export interface AgentResponse {
  response: string;
  confidence: number;
  sources: DeepReasoningResponse['sources'];
  drillDowns: DrillDown[];
  cached: boolean;
}

export interface TermDefinition {
  term: string;
  definition: string;
  category: string;
}

export interface PanelData {
  type: string;
  title: string;
  rows: PanelRow[];
}

export interface PanelRow {
  region: string;
  value: number;
  target: number;
  trend: number[];
  status: 'on-track' | 'at-risk' | 'critical';
}

export interface NarrativeResponse {
  narrative: string;
  confidence: number;
  context: string;
  recommendations: string[];
}
