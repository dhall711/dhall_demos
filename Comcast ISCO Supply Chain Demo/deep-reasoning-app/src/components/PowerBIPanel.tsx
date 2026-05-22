import { useState } from 'react';
import { BarChart3, MessageSquare, ChevronRight, TrendingUp, TrendingDown, FileText, Info } from 'lucide-react';

interface MetricRow {
  region: string;
  value: number;
  trend: number;
  target: number;
  status: 'GREEN' | 'YELLOW' | 'RED';
}

interface QueryTab {
  id: string;
  label: string;
  terms: string[];
  unit: string;
  data: MetricRow[];
}

const QUERY_TABS: QueryTab[] = [
  {
    id: 'gsk_ctd',
    label: 'GSK Click to Deliver',
    terms: ['GSK'],
    unit: 'days',
    data: [
      { region: 'California', value: 4.98, trend: -0.12, target: 4.5, status: 'GREEN' },
      { region: 'Florida', value: 5.23, trend: 0.45, target: 4.5, status: 'YELLOW' },
      { region: 'Texas', value: 4.12, trend: -0.08, target: 4.5, status: 'GREEN' },
      { region: 'Northeast', value: 4.67, trend: 0.15, target: 4.5, status: 'GREEN' },
    ],
  },
  {
    id: 'gsk_ots',
    label: 'GSK On-Time Shipping',
    terms: ['GSK', 'OTS'],
    unit: '%',
    data: [
      { region: 'California', value: 76.3, trend: -18.6, target: 95.0, status: 'RED' },
      { region: 'Florida', value: 94.2, trend: 1.3, target: 95.0, status: 'YELLOW' },
      { region: 'Texas', value: 96.8, trend: 2.1, target: 95.0, status: 'GREEN' },
      { region: 'Northeast', value: 93.5, trend: -0.8, target: 95.0, status: 'YELLOW' },
    ],
  },
  {
    id: 'ffo_scan',
    label: 'FFO Scan Compliance',
    terms: ['FFO'],
    unit: '%',
    data: [
      { region: 'California', value: 88.4, trend: 2.1, target: 92.0, status: 'YELLOW' },
      { region: 'Florida', value: 94.7, trend: 0.3, target: 92.0, status: 'GREEN' },
      { region: 'Texas', value: 96.2, trend: 1.8, target: 92.0, status: 'GREEN' },
      { region: 'Northeast', value: 91.1, trend: -0.5, target: 92.0, status: 'YELLOW' },
    ],
  },
];

export default function PowerBIPanel() {
  const [activeQuery, setActiveQuery] = useState(QUERY_TABS[0].id);
  const [narration, setNarration] = useState<string | null>(null);
  const [narrationLoading, setNarrationLoading] = useState(false);

  const currentTab = QUERY_TABS.find(t => t.id === activeQuery)!;

  const statusBadge = (status: 'GREEN' | 'YELLOW' | 'RED') => {
    const styles = {
      GREEN: 'bg-green-500 text-white',
      YELLOW: 'bg-yellow-400 text-white',
      RED: 'bg-red-500 text-white',
    };
    return <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${styles[status]}`}>{status}</span>;
  };

  const rowBorder = (status: 'GREEN' | 'YELLOW' | 'RED') => {
    const styles = { GREEN: 'border-green-200 bg-green-50/30', YELLOW: 'border-yellow-200 bg-yellow-50/30', RED: 'border-red-200 bg-red-50/30' };
    return styles[status];
  };

  const handleTellMeMore = (region: string) => {
    setNarrationLoading(true);
    setNarration(null);
    setTimeout(() => {
      setNarrationLoading(false);
      setNarration(
        `**${currentTab.label} — ${region}**\n\n` +
        `The current value of ${currentTab.data.find(d => d.region === region)?.value} ${currentTab.unit} ` +
        `is ${currentTab.data.find(d => d.region === region)!.value <= currentTab.data[0].target ? 'within' : 'above'} ` +
        `the target of ${currentTab.data[0].target} ${currentTab.unit}.\n\n` +
        `Week-over-week trend shows a ${Math.abs(currentTab.data.find(d => d.region === region)!.trend)} ${currentTab.unit} ` +
        `${currentTab.data.find(d => d.region === region)!.trend < 0 ? 'improvement' : 'increase'}.\n\n` +
        `This metric is sourced from the Power BI semantic model and narrated by the Cortex Agent for contextual understanding.`
      );
    }, 1500);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
      {/* Left Panel - Metrics */}
      <div className="lg:col-span-3">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5 text-comcast-blue" />
              <h2 className="text-lg font-bold text-gray-900">Power BI Dashboard View</h2>
            </div>
            <span className="text-xs text-blue-600 border border-blue-200 rounded px-2 py-0.5 font-medium">Pre-formed Queries</span>
          </div>

          {/* Query Tabs */}
          <div className="px-6 pt-4 flex gap-2 flex-wrap">
            {QUERY_TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => { setActiveQuery(tab.id); setNarration(null); }}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
                  activeQuery === tab.id
                    ? 'bg-comcast-blue text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Terms Referenced */}
          <div className="mx-6 mt-4 p-3 bg-gray-50 rounded-lg border border-gray-100">
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <Info className="w-3.5 h-3.5" />
              <span className="font-medium">Industry Terms Referenced</span>
            </div>
            <div className="flex gap-2 mt-1.5">
              {currentTab.terms.map(term => (
                <span key={term} className="text-xs bg-white border border-gray-200 rounded px-2 py-0.5 text-gray-600">ⓘ {term}</span>
              ))}
            </div>
          </div>

          {/* Metric Rows */}
          <div className="p-6 space-y-4">
            {currentTab.data.map(row => (
              <div key={row.region} className={`border rounded-lg p-4 flex items-center justify-between ${rowBorder(row.status)}`}>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{row.region}</span>
                    {statusBadge(row.status)}
                  </div>
                  <div className="flex items-baseline gap-3">
                    <span className="text-3xl font-bold text-gray-900">{row.value}</span>
                    <span className={`text-sm font-medium flex items-center gap-0.5 ${row.trend < 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {row.trend < 0 ? <TrendingDown className="w-3.5 h-3.5" /> : <TrendingUp className="w-3.5 h-3.5" />}
                      {row.trend > 0 ? '+' : ''}{row.trend} WoW
                    </span>
                    <span className="text-sm text-gray-400">Target: {row.target} {currentTab.unit}</span>
                  </div>
                </div>
                <button
                  onClick={() => handleTellMeMore(row.region)}
                  className="bg-comcast-blue hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition"
                >
                  <MessageSquare className="w-4 h-4" />
                  Tell Me More
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Footer Note */}
          <div className="px-6 pb-4 flex items-start gap-2 text-xs text-gray-400">
            <Info className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
            <p>Data sourced from Power BI semantic model via pre-formed SQL queries • LLM provides narration only, not query generation</p>
          </div>
        </div>
      </div>

      {/* Right Panel - AI Narration */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 sticky top-6 min-h-[400px] flex items-center justify-center">
          {narrationLoading ? (
            <div className="text-center">
              <div className="animate-spin w-8 h-8 border-2 border-comcast-blue border-t-transparent rounded-full mx-auto mb-3"></div>
              <p className="text-sm text-gray-500">Generating AI narration...</p>
            </div>
          ) : narration ? (
            <div className="w-full">
              <div className="prose prose-sm max-w-none">
                {narration.split('\n\n').map((para, i) => (
                  <p key={i} className="text-sm text-gray-700 mb-3">
                    {para.startsWith('**') ? (
                      <strong className="text-gray-900">{para.replace(/\*\*/g, '')}</strong>
                    ) : para}
                  </p>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center">
              <FileText className="w-12 h-12 text-gray-200 mx-auto mb-3" />
              <p className="text-sm text-gray-400">Select a metric and click "Tell Me More" to see AI-powered narration</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
