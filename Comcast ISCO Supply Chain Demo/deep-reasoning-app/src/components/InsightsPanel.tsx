import { useState } from 'react';
import { FileText, TrendingUp, AlertTriangle, CheckCircle, ExternalLink, ChevronUp, ChevronDown, Download, ArrowRight } from 'lucide-react';

interface ForecastItem {
  metric: string;
  region: string;
  value: string;
  change: string;
  changePositive: boolean;
  ci: string;
  confidence: string;
  risk: 'low' | 'medium' | 'high';
}

const FORECASTS: ForecastItem[] = [
  { metric: 'New Connects', region: 'Texas', value: '2,650', change: '-18.3%', changePositive: false, ci: '[2400, 2900]', confidence: '68%', risk: 'low' },
  { metric: 'On-Time Delivery Rate', region: 'California', value: '84.5%', change: '+10.7%', changePositive: true, ci: '[81.2, 87.8]', confidence: '72%', risk: 'medium' },
  { metric: 'Customer Churn Rate', region: 'California', value: '3.95%', change: '+3.4%', changePositive: false, ci: '[3.7, 4.2]', confidence: '65%', risk: 'high' },
  { metric: 'Click-to-Deliver', region: 'California', value: '3.8 days', change: '-12.1%', changePositive: true, ci: '[3.4, 4.2]', confidence: '61%', risk: 'medium' },
];

interface Correlation {
  from: string;
  fromColor: string;
  to: string;
  toColor: string;
  lag: string;
  strength: 'strong' | 'moderate' | 'weak';
}

const CORRELATIONS: Correlation[] = [
  { from: 'On-Time Delivery Rate', fromColor: 'text-gray-800', to: 'Customer Churn Rate', toColor: 'text-gray-800', lag: '', strength: 'strong' },
  { from: 'On-Time Delivery Rate', fromColor: 'text-gray-800', to: 'Tech Support Call Volume', toColor: 'text-gray-800', lag: '', strength: 'moderate' },
  { from: 'Click-to-Deliver', fromColor: 'text-gray-800', to: 'Customer Satisfaction', toColor: 'text-gray-800', lag: '', strength: 'strong' },
  { from: 'Inventory Levels', fromColor: 'text-gray-800', to: 'On-Time Delivery Rate', toColor: 'text-gray-800', lag: '', strength: 'moderate' },
  { from: 'New Connects Volume', fromColor: 'text-gray-800', to: 'Capacity Utilization', toColor: 'text-gray-800', lag: '', strength: 'moderate' },
];

const CRITICAL_CHAINS = [
  { items: [{ text: 'CA Storm', color: 'bg-orange-100 text-orange-700 border-orange-300' }, { text: 'OTD -18.6%', color: 'text-red-600' }, { text: 'Churn Risk', color: 'text-red-600' }], lag: '2-4 wk lag' },
  { items: [{ text: 'Broadcom Shortage', color: 'bg-orange-100 text-orange-700 border-orange-300' }, { text: 'Inventory -43.8%', color: 'text-red-600' }], lag: '' },
  { items: [{ text: 'Connect Capacity Risk', color: 'text-blue-700' }], lag: '1 wk lag' },
];

export default function InsightsPanel() {
  const [summaryOpen, setSummaryOpen] = useState(true);
  const [correlationsOpen, setCorrelationsOpen] = useState(true);
  const [forecastOpen, setForecastOpen] = useState(true);

  const riskBadge = (risk: 'low' | 'medium' | 'high') => {
    const styles = {
      low: 'bg-green-100 text-green-700',
      medium: 'bg-yellow-100 text-yellow-700',
      high: 'bg-red-100 text-red-700',
    };
    return <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${styles[risk]}`}>{risk} risk</span>;
  };

  const strengthBadge = (s: 'strong' | 'moderate' | 'weak') => {
    const styles = {
      strong: 'bg-green-100 text-green-700',
      moderate: 'bg-yellow-100 text-yellow-700',
      weak: 'bg-gray-100 text-gray-500',
    };
    return <span className={`text-[10px] font-medium px-2 py-0.5 rounded ${styles[s]}`}>{s}</span>;
  };

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div
          className="bg-comcast-darkblue px-5 py-3 flex items-center justify-between cursor-pointer"
          onClick={() => setSummaryOpen(!summaryOpen)}
        >
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-white" />
            <h2 className="text-white font-bold text-sm">Executive Summary</h2>
            <span className="bg-white/20 text-white text-[10px] font-medium px-2 py-0.5 rounded-full">30-second read</span>
          </div>
          <div className="flex items-center gap-2">
            <Download className="w-4 h-4 text-white/70 hover:text-white cursor-pointer" />
            {summaryOpen ? <ChevronUp className="w-4 h-4 text-white" /> : <ChevronDown className="w-4 h-4 text-white" />}
          </div>
        </div>
        {summaryOpen && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs text-gray-500">📅 Week of February 9, 2026</p>
              <p className="text-xs text-gray-400 italic">AI-Generated • Click items to investigate</p>
            </div>

            {/* Critical Items */}
            <div className="mb-5">
              <h3 className="text-xs font-bold text-red-600 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                Critical Items Requiring Immediate Attention
              </h3>
              <div className="space-y-2">
                <div className="bg-red-50 border border-red-100 rounded-lg px-4 py-2.5 flex items-start gap-2 cursor-pointer hover:bg-red-100 transition">
                  <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-800">California OTD dropped to 76.3% (-18.6% WoW) due to AR4 atmospheric river storm. I-5 closed 3 days. Air freight surge: $847K incremental.</p>
                </div>
              </div>
            </div>

            {/* Positive Highlights */}
            <div className="mb-5">
              <h3 className="text-xs font-bold text-green-600 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                Positive Highlights
              </h3>
              <div className="space-y-2">
                <div className="bg-green-50 border border-green-100 rounded-lg px-4 py-2.5 flex items-start gap-2 cursor-pointer hover:bg-green-100 transition">
                  <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-800">Texas new connects +50.5% to 3,245 driven by Bringg same-day expansion (91% TX coverage) and Super Bowl marketing. 60% sustainable, 40% event-driven.</p>
                </div>
                <div className="bg-green-50 border border-green-100 rounded-lg px-4 py-2.5 flex items-start gap-2 cursor-pointer hover:bg-green-100 transition">
                  <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-gray-800">Texas same-day delivery at 58.7% (+42.5% WoW) - exceeding 45% target. Bringg driver utilization healthy at 87%.</p>
                </div>
              </div>
            </div>

            {/* Watch Items */}
            <div className="mb-5">
              <h3 className="text-xs font-bold text-yellow-600 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
                Watch Items
              </h3>
              <div className="space-y-2">
                <div className="bg-yellow-50 border border-yellow-100 rounded-lg px-4 py-2.5 flex items-start gap-2 cursor-pointer hover:bg-yellow-100 transition">
                  <span className="text-base mt-0.5">↗️</span>
                  <p className="text-sm text-gray-800">California churn elevated to 3.82% - T-Mobile "Switch & Save" at $35/mo impacting price-sensitive segment. 68% cite price as reason.</p>
                </div>
              </div>
            </div>

            {/* Key External Factors */}
            <div className="mb-5">
              <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">Key External Factors</h3>
              <ul className="space-y-1 text-sm text-gray-700 ml-1">
                <li className="flex items-start gap-2"><span className="text-gray-400">•</span> AR4 atmospheric river caused widespread Central Valley flooding</li>
                <li className="flex items-start gap-2"><span className="text-gray-400">•</span> T-Mobile added 127K CA home internet subs in January</li>
              </ul>
            </div>

            {/* Recommended Actions */}
            <div>
              <h3 className="text-xs font-bold text-blue-600 uppercase tracking-wide mb-2">Recommended Actions</h3>
              <ol className="space-y-1 text-sm text-gray-700 list-decimal list-inside">
                <li>Continue air freight protocol through Feb 14</li>
                <li>Launch competitive retention offer for at-risk segments</li>
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Two Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cross-Metric Correlations */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div
            className="bg-comcast-darkblue px-5 py-3 flex items-center justify-between cursor-pointer"
            onClick={() => setCorrelationsOpen(!correlationsOpen)}
          >
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              <h2 className="text-white font-bold text-sm">Cross-Metric Correlations</h2>
              <span className="bg-blue-500 text-white text-[10px] font-medium px-2 py-0.5 rounded-full">7 relationships</span>
            </div>
            {correlationsOpen ? <ChevronUp className="w-4 h-4 text-white" /> : <ChevronDown className="w-4 h-4 text-white" />}
          </div>
          {correlationsOpen && (
            <div className="p-5">
              <p className="text-xs text-gray-400 mb-4 flex items-center gap-1">
                <span className="w-3.5 h-3.5 rounded-full border border-gray-300 flex items-center justify-center text-[8px]">i</span>
                Click any correlation to see how metrics affect each other
              </p>

              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wide mb-3">Current Week Critical Chain</h4>
              <div className="space-y-3 mb-6">
                {CRITICAL_CHAINS.map((chain, ci) => (
                  <div key={ci} className="flex items-center gap-2 flex-wrap">
                    {chain.items.map((item, ii) => (
                      <span key={ii} className="flex items-center gap-2">
                        {ii > 0 && <ArrowRight className="w-3 h-3 text-gray-400" />}
                        <span className={`text-xs font-medium px-2.5 py-1 rounded border ${item.color}`}>{item.text}</span>
                      </span>
                    ))}
                    {chain.lag && <span className="text-[10px] text-gray-400 ml-1">({chain.lag})</span>}
                  </div>
                ))}
              </div>

              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wide mb-3">All Relationships</h4>
              <div className="space-y-2.5">
                {CORRELATIONS.map((corr, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs cursor-pointer hover:bg-gray-50 rounded p-1.5 -mx-1.5 transition">
                    <span className="font-medium text-gray-700">{corr.from}</span>
                    <span className="text-red-500 text-[10px] font-medium px-1.5 py-0.5 bg-red-50 rounded">Causes</span>
                    <ArrowRight className="w-3 h-3 text-gray-400" />
                    <span className="text-gray-700">{corr.to}</span>
                    <span className="ml-auto">{strengthBadge(corr.strength)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Next Week Forecast */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div
            className="bg-comcast-darkblue px-5 py-3 flex items-center justify-between cursor-pointer"
            onClick={() => setForecastOpen(!forecastOpen)}
          >
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-white" />
              <h2 className="text-white font-bold text-sm">Next Week Forecast</h2>
              <span className="bg-red-500 text-white text-[10px] font-medium px-2 py-0.5 rounded-full">1 high risk</span>
            </div>
            {forecastOpen ? <ChevronUp className="w-4 h-4 text-white" /> : <ChevronDown className="w-4 h-4 text-white" />}
          </div>
          {forecastOpen && (
            <div className="p-5">
              <p className="text-xs text-gray-400 mb-4 flex items-center gap-1">
                <span className="w-3.5 h-3.5 rounded-full border border-gray-300 flex items-center justify-center text-[8px]">i</span>
                AI predictions based on historical patterns, external factors, and current trends
              </p>
              <div className="space-y-5">
                {FORECASTS.map((f, i) => (
                  <div key={i} className="cursor-pointer hover:bg-gray-50 rounded-lg p-3 -mx-3 transition">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <TrendingUp className={`w-4 h-4 ${f.changePositive ? 'text-green-500' : 'text-red-500'}`} />
                        <span className="text-sm font-medium text-gray-800">{f.metric}</span>
                        <span className="text-xs text-gray-400">{f.region}</span>
                      </div>
                      {riskBadge(f.risk)}
                    </div>
                    <div className="flex items-baseline gap-3 ml-6">
                      <span className="text-xl font-bold text-gray-900">{f.value}</span>
                      <span className={`text-sm font-medium ${f.changePositive ? 'text-green-600' : 'text-red-600'}`}>({f.change})</span>
                      <span className="text-xs text-gray-400">CI: {f.ci}</span>
                      <span className="text-xs text-blue-500 font-medium">{f.confidence} confidence</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
