'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { TrendingUp, AlertTriangle, Info } from 'lucide-react';
import { useChatContext } from '@/context/ChatContext';
const DrilldownPanel = dynamic(() => import('@/components/DrilldownPanel'), { ssr: false });

const REGION_COLORS: Record<string, string> = { NA: '#0066cc', EU: '#059669', APAC: '#d97706', LATAM: '#7c3aed' };

export default function ForecastPage() {
  const [forecast, setForecast] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { getPageSelection, setPageSelection, clearDrilldown } = useChatContext();
  const selectedRegion = getPageSelection('forecast') as string | null;

  useEffect(() => {
    fetch('/api/data?q=forecast').then(r => r.json()).then(d => { setForecast(d.forecast || []); setHistory(d.history || []); setLoading(false); });
  }, []);

  function handleClose() {
    setPageSelection('forecast', null);
    clearDrilldown('forecast');
  }

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading forecast...</div>;

  const regions = [...new Set(forecast.map(f => f.region))];
  const allDates = [...new Set(forecast.map(f => f.date))].sort();
  const first7Dates = new Set(allDates.slice(0, 7));
  const next7 = forecast.filter(f => first7Dates.has(f.date));
  const totalPredicted7d = next7.reduce((a, f) => a + f.predicted, 0);
  const totalUpper7d = next7.reduce((a, f) => a + f.upper, 0);
  const totalLower7d = next7.reduce((a, f) => a + f.lower, 0);

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Certificate Expiry Forecast</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 8 }}>ML-powered prediction of certificate expiry volumes for capacity planning</p>

      <div style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: 10, padding: '12px 16px', marginBottom: 20, display: 'flex', gap: 10, alignItems: 'flex-start' }}>
        <Info size={16} color="#0066cc" style={{ marginTop: 2, flexShrink: 0 }} />
        <div style={{ fontSize: 12, color: '#1e40af', lineHeight: 1.6 }}>
          <strong>How this works:</strong> A <code style={{ background: '#dbeafe', padding: '1px 4px', borderRadius: 3 }}>SNOWFLAKE.ML.FORECAST</code> model is trained on 90 days of historical expiry data grouped by region. It uses time-series decomposition (trend + seasonality + residuals) to predict the next 14 days of certificate expirations. The confidence interval shows the 95% prediction range.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', gap: 12, marginBottom: 20 }}>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, padding: 16, borderLeft: '4px solid #111827' }}>
          <div style={{ fontSize: 11, color: '#6b7280' }}>7-Day Total (Predicted)</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: '#111827' }}>{fmt(totalPredicted7d)}</div>
          <div style={{ fontSize: 10, color: '#9ca3af' }}>Range: {fmt(totalLower7d)} – {fmt(totalUpper7d)}</div>
        </div>
        {regions.map(r => {
          const regionData = next7.filter(f => f.region === r);
          const regionTotal = regionData.reduce((a, f) => a + f.predicted, 0);
          const regionUpper = regionData.reduce((a, f) => a + f.upper, 0);
          return (
            <div key={r} onClick={() => { if (selectedRegion === r) { handleClose(); } else { setPageSelection('forecast', r); clearDrilldown('forecast'); } }} style={{ background: selectedRegion === r ? '#eff6ff' : '#fff', border: `1px solid ${selectedRegion === r ? '#0066cc' : '#e2e8f0'}`, borderRadius: 10, padding: 16, borderLeft: `4px solid ${REGION_COLORS[r] || '#6b7280'}`, cursor: 'pointer', transition: 'all 0.15s' }}>
              <div style={{ fontSize: 11, color: '#6b7280' }}>{r} (7-day)</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: REGION_COLORS[r] }}>{fmt(regionTotal)}</div>
              <div style={{ fontSize: 10, color: '#9ca3af' }}>Upper bound: {fmt(regionUpper)}</div>
            </div>
          );
        })}
      </div>

      {selectedRegion && (
        <DrilldownPanel
          pageId="forecast"
          title={`Forecast Deep Dive: ${selectedRegion}`}
          question={`What is the predicted certificate expiry volume for the ${selectedRegion} region over the next 14 days? Which partners and device types will have the most expirations? What capacity planning actions should we take for ${selectedRegion}?`}
          onClose={handleClose}
          drilldowns={[
            { label: 'Top Partners Expiring', question: `Which partners in ${selectedRegion} will have the most expiring certificates in the next 7 days?` },
            { label: 'Auto-Renewal Coverage', question: `What percentage of expiring ${selectedRegion} certificates are covered by ACME auto-renewal vs manual?` },
            { label: 'Risk Assessment', question: `Which critical infrastructure certificates in ${selectedRegion} expire soonest?` },
          ]}
        />
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginTop: 20 }}>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 4 }}>14-Day Forecast by Region</h3>
          <p style={{ fontSize: 11, color: '#9ca3af', marginBottom: 12 }}>Daily predicted certificate expirations with 95% confidence interval</p>
          <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
            <thead><tr style={{ background: '#f9fafb' }}><th style={thS}>Date</th>{regions.map(r => <th key={r} style={{...thS, color: REGION_COLORS[r]}}>{r}</th>)}<th style={thS}>Daily Total</th></tr></thead>
            <tbody>
              {[...new Set(forecast.map(f => f.date))].slice(0, 14).map((date, i) => {
                const row = regions.map(r => {
                  const item = forecast.find(f => f.date === date && f.region === r);
                  return item ? { predicted: item.predicted, lower: item.lower, upper: item.upper } : { predicted: 0, lower: 0, upper: 0 };
                });
                const dayTotal = row.reduce((a, b) => a + b.predicted, 0);
                return (
                  <tr key={i} style={{ background: i % 2 === 0 ? '#fff' : '#f9fafb' }}>
                    <td style={tdS}>{String(date).slice(5, 10)}</td>
                    {row.map((v, j) => (
                      <td key={j} style={tdS}>
                        <span style={{ fontWeight: 500 }}>{fmt(v.predicted)}</span>
                        <span style={{ fontSize: 9, color: '#9ca3af', marginLeft: 4 }}>±{fmt(Math.round((v.upper - v.lower) / 2))}</span>
                      </td>
                    ))}
                    <td style={{...tdS, fontWeight: 600, color: dayTotal > 90000 ? '#dc2626' : '#374151'}}>{fmt(dayTotal)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 8 }}>Model Details</h4>
            <div style={{ fontSize: 11, color: '#6b7280', lineHeight: 1.8 }}>
              <div><strong>Algorithm:</strong> Ensemble (Prophet + ARIMA + GBM)</div>
              <div><strong>Training Data:</strong> 90 days historical</div>
              <div><strong>Series:</strong> 4 regions (multi-series)</div>
              <div><strong>Frequency:</strong> Daily</div>
              <div><strong>Confidence:</strong> 95% prediction interval</div>
              <div><strong>Last Trained:</strong> Today</div>
            </div>
          </div>

          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <AlertTriangle size={14} color="#d97706" /> Capacity Alerts
            </h4>
            <div style={{ fontSize: 11, color: '#6b7280', lineHeight: 1.8 }}>
              {regions.map(r => {
                const peak = Math.max(...forecast.filter(f => f.region === r).map(f => f.predicted));
                const isHigh = peak > 25000;
                return (
                  <div key={r} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #f3f4f6' }}>
                    <span style={{ color: REGION_COLORS[r], fontWeight: 500 }}>{r}</span>
                    <span style={{ color: isHigh ? '#dc2626' : '#059669', fontWeight: 500 }}>{fmt(peak)}/day peak {isHigh ? '⚠️' : '✓'}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16 }}>
            <h4 style={{ fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <TrendingUp size={14} color="#0066cc" /> Recommendations
            </h4>
            <div style={{ fontSize: 11, color: '#4b5563', lineHeight: 1.8 }}>
              <div>• Scale ACME renewal capacity for peak days</div>
              <div>• Alert partners with &gt;5K expiring certs</div>
              <div>• Pre-approve bulk renewals for IoT fleet</div>
              <div>• Monitor LATAM manual renewal queue</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const thS: React.CSSProperties = { textAlign: 'left', padding: '8px 12px', borderBottom: '2px solid #e2e8f0', color: '#6b7280', fontWeight: 600, fontSize: 11, textTransform: 'uppercase' };
const tdS: React.CSSProperties = { padding: '8px 12px', borderBottom: '1px solid #f3f4f6', color: '#374151' };
function fmt(n: number) { return n >= 1000000 ? (n/1000000).toFixed(1) + 'M' : n >= 1000 ? (n/1000).toFixed(0) + 'K' : String(n); }
