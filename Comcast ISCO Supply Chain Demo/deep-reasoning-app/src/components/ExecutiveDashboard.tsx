import { useState, useMemo } from 'react';
import { ChevronDown, ChevronRight, X, Brain, Ticket } from 'lucide-react';
import { PanelData, PanelRow, NarrativeResponse } from '../types';

interface Props {
  onOpenComments: (panelType: string, region?: string, value?: number) => void;
}

const REGIONS = ['BELTWAY', 'BIG SOUTH', 'CALIFORNIA', 'CHICAGO', 'FLORIDA', 'HEARTLAND'];

const PANEL_CONFIGS = [
  { type: 'issuance_forecast', title: 'Issuance Forecast Attainment', unit: '%', target: 90, isPositiveGood: true, targetLabel: '>=90%', failLabel: '<90%' },
  { type: 'fill_rates', title: 'Total Fill Rates', unit: '%', target: 90, isPositiveGood: true, targetLabel: '>=90%', failLabel: '<90%' },
  { type: 'cycle_count', title: 'Cycle Count Compliance', unit: '%', target: 96, isPositiveGood: true, targetLabel: '>=96%', failLabel: '<96%' },
  { type: 'bp_issuance', title: 'BP Issuance Frequency', unit: '%', target: 90, isPositiveGood: true, targetLabel: '>=90%', failLabel: '<90%' },
  { type: 'on_time_shipping', title: 'On-Time Shipping (Hub)', unit: '%', target: 98, isPositiveGood: true, targetLabel: '>=98%', failLabel: '<98%' },
  { type: 'critical_items', title: 'Critical Items Inventory Availability', unit: '', target: 21, isPositiveGood: true, targetLabel: '>=21', failLabel: '<21' },
];

function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

function generateSyntheticData(weekIndex: number): Map<string, PanelData> {
  const panels = new Map<string, PanelData>();
  const rand = seededRandom(weekIndex * 12345 + 67890);

  for (const config of PANEL_CONFIGS) {
    const rows: PanelRow[] = REGIONS.map(region => {
      const degradation = weekIndex * 0.5;
      const regionSeed = rand();
      const baseVariance = (regionSeed - 0.5) * 15;

      let value: number;
      if (config.type === 'critical_items') {
        value = 20 + baseVariance - degradation * 0.3;
      } else {
        value = config.target + baseVariance - degradation;
      }

      const trend = Array.from({ length: 4 }, () => {
        const t = value + (rand() - 0.5) * 5;
        return parseFloat(t.toFixed(1));
      });

      let status: PanelRow['status'] = 'on-track';
      if (value < config.target) status = 'critical';

      return {
        region,
        value: parseFloat(value.toFixed(config.type === 'critical_items' ? 2 : 0)),
        target: config.target,
        trend,
        status,
      };
    });

    panels.set(config.type, { type: config.type, title: config.title, rows });
  }

  return panels;
}

function getAvailableWeeks(): { label: string; date: string; shortDate: string }[] {
  const weeks = [];
  const base = new Date('2026-02-16');
  for (let i = 0; i < 8; i++) {
    const d = new Date(base);
    d.setDate(d.getDate() - i * 7);
    const label = `Week of ${d.getMonth() + 1}/${d.getDate()}`;
    const shortDate = `${d.getMonth() + 1}/${d.getDate()}/2026`;
    weeks.push({ label, date: d.toISOString().split('T')[0], shortDate });
  }
  return weeks;
}

function Sparkline({ data, target, isPositiveGood }: { data: number[]; target: number; isPositiveGood: boolean }) {
  const width = 60;
  const height = 20;
  const padding = 2;
  const min = Math.min(...data) - 2;
  const max = Math.max(...data) + 2;
  const range = max - min || 1;

  const points = data.map((v, i) => {
    const x = padding + (i / (data.length - 1)) * (width - 2 * padding);
    const y = height - padding - ((v - min) / range) * (height - 2 * padding);
    return `${x},${y}`;
  }).join(' ');

  const lastVal = data[data.length - 1];
  const meetsTarget = isPositiveGood ? lastVal >= target : lastVal <= target;
  const isRising = data[data.length - 1] > data[0];
  const color = meetsTarget ? '#22c55e' : '#ef4444';

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function ExecutiveDashboard({ onOpenComments }: Props) {
  const availableWeeks = useMemo(() => getAvailableWeeks(), []);
  const [selectedWeekIdx, setSelectedWeekIdx] = useState(0);
  const [weekDropdownOpen, setWeekDropdownOpen] = useState(false);
  const [narratorOpen, setNarratorOpen] = useState(false);
  const [narratorContext, setNarratorContext] = useState<{ panelType: string; region: string; value: number } | null>(null);
  const [narratorResponse, setNarratorResponse] = useState<NarrativeResponse | null>(null);
  const [narratorLoading, setNarratorLoading] = useState(false);

  const panelData = useMemo(() => generateSyntheticData(selectedWeekIdx), [selectedWeekIdx]);

  const handleTellMeMore = (panelType: string, region: string, value: number) => {
    setNarratorContext({ panelType, region, value });
    setNarratorOpen(true);
    setNarratorLoading(true);

    const config = PANEL_CONFIGS.find(p => p.type === panelType);
    setTimeout(() => {
      setNarratorResponse({
        narrative: `**${config?.title}** for ${region} is currently at **${value}${config?.unit === '%' ? '%' : ` ${config?.unit}`}** against a target of ${config?.target}${config?.unit === '%' ? '%' : ` ${config?.unit}`}.\n\nBased on historical patterns and the current trajectory, this metric has been ${value >= (config?.target || 0) ? 'performing well' : 'underperforming'} over the past 4 weeks.\n\n**Contributing Factors:**\n- Regional demand fluctuations aligned with seasonal patterns\n- Operational capacity adjustments in progress\n- Third-party logistics performance within expected range\n\n**Recommendation:** ${value >= (config?.target || 0) ? 'Continue monitoring. No immediate action required.' : 'Recommend escalation to regional operations lead for root cause investigation.'}`,
        confidence: Math.floor(65 + Math.random() * 30),
        context: `${config?.title} - ${region}`,
        recommendations: value >= (config?.target || 0)
          ? ['Continue current operational tempo', 'Document best practices for cross-region sharing']
          : ['Escalate to regional ops lead', 'Review contributing supply chain factors', 'Consider creating investigation ticket'],
      });
      setNarratorLoading(false);
    }, 1500);
  };

  const currentWeekShort = availableWeeks[selectedWeekIdx]?.label.replace('Week of ', '');

  return (
    <div className="relative">
      <div className="bg-comcast-darkblue text-white px-6 py-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">EXECUTIVE SUMMARY - 02/16/2026</h2>
            <p className="text-sm text-gray-300 mt-0.5">Materials - Service Week of {currentWeekShort}</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-300 tracking-wider">PRIVATE AND CONFIDENTIAL</span>
            <img src="/src/assets/Xfinity_logo.svg" alt="Xfinity" className="h-5 brightness-0 invert" />
          </div>
        </div>
      </div>

      <div className="bg-green-600 text-white text-center py-2 text-sm font-semibold">
        Core - Service Week of {currentWeekShort}
      </div>

      <div className="grid grid-cols-3 gap-4 mt-4">
        {PANEL_CONFIGS.slice(0, 3).map(config => {
          const panel = panelData.get(config.type);
          if (!panel) return null;
          return <PanelCard key={config.type} config={config} panel={panel} weekDate={availableWeeks[selectedWeekIdx]?.shortDate} onRowClick={handleTellMeMore} />;
        })}
      </div>

      <div className="grid grid-cols-3 gap-4 mt-4">
        {PANEL_CONFIGS.slice(3, 6).map(config => {
          const panel = panelData.get(config.type);
          if (!panel) return null;
          return <PanelCard key={config.type} config={config} panel={panel} weekDate={availableWeeks[selectedWeekIdx]?.shortDate} onRowClick={handleTellMeMore} />;
        })}
      </div>

      <div className="mt-4 flex items-center justify-between px-2">
        <p className="text-xs text-gray-500 flex items-center gap-1">
          <span className="text-base">✨</span> Click any row to ask "Tell Me More?"
        </p>
        <p className="text-xs text-gray-400">
          Powered by <a href="#" className="text-comcast-blue hover:underline">Snowflake Cortex AI</a>
        </p>
      </div>

      {narratorOpen && (
        <div className="fixed top-0 right-0 h-full w-[480px] bg-white shadow-2xl border-l border-gray-200 z-30 flex flex-col">
          <div className="flex items-center justify-between p-4 border-b bg-comcast-darkblue">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-300" />
              <div>
                <h3 className="font-semibold text-sm text-white">AI Narrator</h3>
                <p className="text-xs text-gray-300">{narratorContext?.region} - {PANEL_CONFIGS.find(p => p.type === narratorContext?.panelType)?.title}</p>
              </div>
            </div>
            <button onClick={() => setNarratorOpen(false)} className="p-1 hover:bg-white/10 rounded">
              <X className="w-5 h-5 text-white" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {narratorLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Brain className="w-8 h-8 animate-pulse mb-3" />
                <p className="text-sm">Analyzing metric context...</p>
              </div>
            ) : narratorResponse ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${narratorResponse.confidence >= 80 ? 'bg-green-100 text-green-700' : narratorResponse.confidence >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                    {narratorResponse.confidence}% confidence
                  </span>
                </div>
                <div className="prose prose-sm max-w-none">
                  {narratorResponse.narrative.split('\n').map((line, i) => {
                    if (line.startsWith('**') && line.endsWith('**')) return <p key={i} className="font-bold text-gray-900">{line.replace(/\*\*/g, '')}</p>;
                    if (line.startsWith('- ')) return <li key={i} className="text-gray-700 text-sm ml-4">{line.slice(2)}</li>;
                    return <p key={i} className="text-sm text-gray-700">{line.replace(/\*\*/g, '')}</p>;
                  })}
                </div>
                {narratorResponse.recommendations.length > 0 && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                    <h4 className="text-xs font-semibold text-blue-800 mb-2">Recommendations</h4>
                    <ul className="space-y-1">
                      {narratorResponse.recommendations.map((rec, i) => (
                        <li key={i} className="text-xs text-blue-700 flex items-start gap-1">
                          <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0" /> {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className="p-4 border-t bg-gray-50">
            <button onClick={() => setNarratorOpen(false)} className="w-full py-2 bg-comcast-blue text-white rounded-lg text-sm font-medium hover:bg-comcast-darkblue transition flex items-center justify-center gap-2">
              <Ticket className="w-4 h-4" /> Create Investigation Ticket
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function PanelCard({ config, panel, weekDate, onRowClick }: {
  config: typeof PANEL_CONFIGS[number];
  panel: PanelData;
  weekDate: string;
  onRowClick: (panelType: string, region: string, value: number) => void;
}) {
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
      <div className="flex items-center justify-between px-4 py-2.5 bg-comcast-darkblue">
        <h3 className="text-xs font-semibold text-white">{config.title}</h3>
        {panel.rows.filter(r => r.status === 'critical').length > 0 && (
          <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
            {panel.rows.filter(r => r.status === 'critical').length}
          </span>
        )}
      </div>
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b bg-gray-50">
            <th className="text-left px-4 py-2 font-medium text-gray-600">REGION</th>
            <th className="text-center px-2 py-2 font-medium text-gray-600">4 Week Trend</th>
            <th className="text-right px-4 py-2 font-medium text-gray-600">{weekDate}</th>
          </tr>
        </thead>
        <tbody>
          {panel.rows.map(row => {
            const meetsTarget = row.value >= config.target;
            const valueColor = meetsTarget ? 'text-green-600' : 'text-red-600';
            const trendPct = row.trend.length >= 2
              ? ((row.trend[row.trend.length - 1] - row.trend[0]) / Math.abs(row.trend[0]) * 100).toFixed(2)
              : '0.00';
            const trendPositive = parseFloat(trendPct) >= 0;
            const direction = trendPositive === config.isPositiveGood ? 'Improving' : 'Declining';
            const directionEmoji = direction === 'Improving' ? '📈' : '📉';

            return (
              <tr
                key={row.region}
                className="border-b last:border-0 hover:bg-blue-50/40 cursor-pointer transition relative"
                onClick={() => onRowClick(config.type, row.region, row.value)}
                onMouseEnter={() => setHoveredRow(row.region)}
                onMouseLeave={() => setHoveredRow(null)}
              >
                <td className="px-4 py-2 font-medium text-gray-800">{row.region}</td>
                <td className="px-2 py-2 text-center relative">
                  <Sparkline data={row.trend} target={config.target} isPositiveGood={config.isPositiveGood} />
                  {hoveredRow === row.region && (
                    <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 bg-gray-900 text-white rounded-lg shadow-xl p-3 text-xs pointer-events-none">
                      <div className="font-bold text-sm mb-1">4-Week Trend Analysis</div>
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="text-gray-300">Trend:</span>
                        <span className={trendPositive ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
                          {trendPositive ? '+' : ''}{trendPct}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-gray-300">Direction:</span>
                        <span className="font-medium">{directionEmoji} {direction}</span>
                      </div>
                      <div className="text-gray-400 text-[10px] border-t border-gray-700 pt-1.5 text-center">
                        Click for detailed root cause analysis
                      </div>
                      <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-gray-900"></div>
                    </div>
                  )}
                </td>
                <td className={`px-4 py-2 text-right font-bold ${valueColor}`}>
                  {config.type === 'critical_items' ? row.value.toFixed(2) : `${row.value}%`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div className="px-4 py-1.5 border-t bg-gray-50 flex items-center gap-3 text-[10px] text-gray-500">
        <span className="flex items-center gap-1">
          Target <span className="inline-block w-2 h-2 bg-green-500 rounded-sm"></span> {config.targetLabel}
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-2 h-2 bg-red-500 rounded-sm"></span> {config.failLabel}
        </span>
      </div>
    </div>
  );
}
