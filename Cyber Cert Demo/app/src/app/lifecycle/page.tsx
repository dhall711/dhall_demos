'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useChatContext } from '@/context/ChatContext';
const DrilldownPanel = dynamic(() => import('@/components/DrilldownPanel'), { ssr: false });

const STATES = ['ISSUED', 'ACTIVE', 'EXPIRING', 'EXPIRED', 'REVOKED', 'RENEWED'];
const STATE_COLORS: Record<string, string> = { ISSUED: '#0066cc', ACTIVE: '#059669', EXPIRING: '#d97706', EXPIRED: '#dc2626', REVOKED: '#7c3aed', RENEWED: '#0891b2', NONE: '#9ca3af' };

export default function LifecyclePage() {
  const [byState, setByState] = useState<any[]>([]);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { getPageSelection, setPageSelection, clearDrilldown } = useChatContext();
  const selected = getPageSelection('lifecycle') as string | null;

  useEffect(() => {
    fetch('/api/data?q=lifecycle').then(r => r.json()).then(d => { setByState(d.byState || []); setRecent(d.recent || []); setLoading(false); });
  }, []);

  function handleClose() {
    setPageSelection('lifecycle', null);
    clearDrilldown('lifecycle');
  }

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading lifecycle data...</div>;

  const stateTotals: Record<string, number> = {};
  byState.forEach(s => { stateTotals[s.state] = (stateTotals[s.state] || 0) + s.count; });
  const totalEvents = Object.values(stateTotals).reduce((a, b) => a + b, 0);

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Certificate Lifecycle</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>State machine tracking: ISSUED → ACTIVE → EXPIRING → EXPIRED/REVOKED • <span style={{ color: '#0066cc' }}>Click a state to investigate</span></p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        {STATES.map(state => {
          const count = stateTotals[state] || 0;
          const active = selected === state;
          return (
            <div key={state} onClick={() => { setPageSelection('lifecycle', active ? null : state); if (active) clearDrilldown('lifecycle'); }} style={{ background: active ? '#eff6ff' : '#fff', border: `1px solid ${active ? '#0066cc' : '#e2e8f0'}`, borderRadius: 10, padding: '12px 20px', cursor: 'pointer', borderTop: `3px solid ${STATE_COLORS[state]}`, transition: 'all 0.15s', minWidth: 130 }}>
              <div style={{ fontSize: 11, color: '#6b7280', fontWeight: 500 }}>{state}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: STATE_COLORS[state] }}>{fmt(count)}</div>
              <div style={{ fontSize: 10, color: '#9ca3af' }}>{totalEvents > 0 ? ((100 * count / totalEvents).toFixed(1) + '%') : '0%'}</div>
            </div>
          );
        })}
      </div>

      {selected && (
        <DrilldownPanel
          pageId="lifecycle"
          title={`Lifecycle State: ${selected}`}
          question={`Analyze certificates in the ${selected} state. How many are there, what triggered the transition, which device types and partners are most affected, and what actions should be taken?`}
          onClose={handleClose}
          drilldowns={[
            { label: 'By Trigger Type', question: `What triggered certificates to enter the ${selected} state? Show breakdown by trigger type.` },
            { label: 'By Device Type', question: `Which device types have the most certificates in ${selected} state?` },
            { label: 'Transition Timeline', question: `What is the average time certificates spend before transitioning to ${selected}?` },
          ]}
        />
      )}

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginTop: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: '#374151', marginBottom: 12 }}>Recent State Transitions</h3>
        <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb' }}><th style={thS}>Certificate</th><th style={thS}>From</th><th style={thS}>To</th><th style={thS}>Timestamp</th><th style={thS}>Trigger</th></tr></thead>
          <tbody>
            {recent.slice(0, 12).map((r, i) => (
              <tr key={i}>
                <td style={tdS}><code style={{ fontSize: 10, background: '#f8fafc', padding: '2px 6px', borderRadius: 3 }}>{r.certId?.slice(0, 12)}...</code></td>
                <td style={tdS}><span style={{ color: STATE_COLORS[r.from] || '#6b7280', fontWeight: 500, fontSize: 11 }}>{r.from}</span></td>
                <td style={tdS}><span style={{ color: STATE_COLORS[r.to] || '#6b7280', fontWeight: 600, fontSize: 11 }}>→ {r.to}</span></td>
                <td style={tdS}><span style={{ fontSize: 11, color: '#6b7280' }}>{r.ts?.slice(0, 16)}</span></td>
                <td style={tdS}><span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 4, background: '#f0f9ff', color: '#0066cc', border: '1px solid #bfdbfe' }}>{r.trigger}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thS: React.CSSProperties = { textAlign: 'left', padding: '8px 12px', borderBottom: '2px solid #e2e8f0', color: '#6b7280', fontWeight: 600, fontSize: 11, textTransform: 'uppercase' };
const tdS: React.CSSProperties = { padding: '8px 12px', borderBottom: '1px solid #f3f4f6', color: '#374151' };
function fmt(n: number) { return n >= 1000000 ? (n/1000000).toFixed(1) + 'M' : n >= 1000 ? (n/1000).toFixed(0) + 'K' : String(n); }
