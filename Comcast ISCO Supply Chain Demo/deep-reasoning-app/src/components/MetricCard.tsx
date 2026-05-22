import { TrendingDown, AlertTriangle, ChevronRight } from 'lucide-react';
import { Metric } from '../types';

interface Props {
  metric: Metric;
  onClick: (metric: Metric) => void;
}

function MiniSparkline({ data, isNegative }: { data: number[]; isNegative: boolean }) {
  const width = 60;
  const height = 28;
  const padding = 2;
  const min = Math.min(...data) - 1;
  const max = Math.max(...data) + 1;
  const range = max - min || 1;

  const points = data.map((v, i) => {
    const x = padding + (i / (data.length - 1)) * (width - 2 * padding);
    const y = height - padding - ((v - min) / range) * (height - 2 * padding);
    return `${x},${y}`;
  }).join(' ');

  const color = isNegative ? '#ef4444' : '#22c55e';

  return (
    <svg width={width} height={height}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function MetricCard({ metric, onClick }: Props) {
  const severityBadge: Record<string, string> = {
    CRITICAL: 'bg-red-100 text-red-700 border border-red-200',
    HIGH: 'bg-orange-100 text-orange-700 border border-orange-200',
    MEDIUM: 'bg-yellow-100 text-yellow-700 border border-yellow-200',
    LOW: 'bg-blue-100 text-blue-700 border border-blue-200',
  };

  const cardBorder: Record<string, string> = {
    CRITICAL: 'border-l-red-500',
    HIGH: 'border-l-blue-500',
    MEDIUM: 'border-l-yellow-500',
    LOW: 'border-l-gray-300',
  };

  const isNegative = metric.isPositiveGood ? metric.variancePct < 0 : metric.variancePct > 0;
  const varianceFromTarget = metric.targetValue > 0
    ? ((metric.currentValue - metric.targetValue) / metric.targetValue * 100).toFixed(1)
    : '0';
  const progressPct = metric.targetValue > 0 ? Math.min(100, (metric.currentValue / metric.targetValue) * 100) : 0;

  return (
    <div
      onClick={() => onClick(metric)}
      className={`bg-white rounded-lg border border-gray-200 border-l-4 ${cardBorder[metric.anomalySeverity || 'LOW']} p-4 cursor-pointer hover:shadow-lg transition-shadow`}
    >
      <div className="flex items-start justify-between mb-1">
        <div>
          <p className="text-[11px] text-gray-500 font-medium uppercase tracking-wide">{metric.region}</p>
          <h3 className="font-semibold text-gray-900 text-sm">{metric.metricName}</h3>
        </div>
        {metric.anomalySeverity && (
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold rounded-full ${severityBadge[metric.anomalySeverity]}`}>
            <AlertTriangle className="w-3 h-3" />
            {metric.anomalySeverity}
          </span>
        )}
      </div>

      <div className="flex items-end justify-between mt-3">
        <div>
          <div className="text-3xl font-bold text-gray-900">
            {metric.currentValue.toLocaleString(undefined, { maximumFractionDigits: 1 })}
          </div>
          <div className={`flex items-center gap-1 text-xs font-medium mt-0.5 ${isNegative ? 'text-red-600' : 'text-green-600'}`}>
            <TrendingDown className="w-3 h-3" />
            {metric.variancePct > 0 ? '+' : ''}{metric.variancePct.toFixed(1)}% WoW
          </div>
        </div>
        <div className="text-right">
          <p className="text-[10px] text-gray-400 mb-0.5">6-wk trend</p>
          {metric.sparklineData && (
            <MiniSparkline data={metric.sparklineData} isNegative={isNegative} />
          )}
          <button className="text-[11px] text-comcast-blue font-medium flex items-center gap-0.5 ml-auto mt-1 hover:underline">
            <AlertTriangle className="w-3 h-3" /> Investigate <ChevronRight className="w-3 h-3" />
          </button>
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-gray-100">
        <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
          <span>Target: {metric.targetValue.toLocaleString()}</span>
          <span>{varianceFromTarget}%</span>
        </div>
        <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${isNegative ? 'bg-red-500' : 'bg-green-500'}`}
            style={{ width: `${Math.min(progressPct, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
