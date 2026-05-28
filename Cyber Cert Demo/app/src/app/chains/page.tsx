'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useChatContext } from '@/context/ChatContext';
const DrilldownPanel = dynamic(() => import('@/components/DrilldownPanel'), { ssr: false });

export default function ChainPage() {
  const [chains, setChains] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { getPageSelection, setPageSelection, clearDrilldown } = useChatContext();
  const selected = getPageSelection('chains');

  useEffect(() => {
    fetch('/api/data?q=chains').then(r => r.json()).then(d => { setChains(d.chains || []); setLoading(false); });
  }, []);

  function handleClose() {
    setPageSelection('chains', null);
    clearDrilldown('chains');
  }

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading chain data...</div>;

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Certificate Chain Explorer</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>Trust chain resolution: Leaf → Intermediate CA → Root CA • <span style={{ color: '#0066cc' }}>Click a row to investigate</span></p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 24 }}>
        <Stat label="Total Chains" value={chains.reduce((a, c) => a + c.count, 0)} color="#0066cc" />
        <Stat label="Valid Chains" value={chains.reduce((a, c) => a + c.valid, 0)} color="#059669" />
        <Stat label="Invalid Chains" value={chains.reduce((a, c) => a + (c.count - c.valid), 0)} color="#dc2626" />
      </div>

      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
        <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb' }}>
              <th style={thS}>Intermediate CA</th><th style={thS}>Issuing Org</th><th style={thS}>Root CA</th><th style={thS}>Trust Store</th><th style={thS}>Chains</th><th style={thS}>Valid</th><th style={thS}>Revocation %</th>
            </tr>
          </thead>
          <tbody>
            {chains.map((c, i) => {
              const active = selected?.intermediate === c.intermediate;
              return (
                <tr key={i} onClick={() => setPageSelection('chains', active ? null : c)} style={{ background: active ? '#eff6ff' : i % 2 === 0 ? '#fff' : '#f9fafb', cursor: 'pointer', transition: 'background 0.1s' }} onMouseEnter={e => { if (!active) e.currentTarget.style.background = '#f0f9ff'; }} onMouseLeave={e => { if (!active) e.currentTarget.style.background = i % 2 === 0 ? '#fff' : '#f9fafb'; }}>
                  <td style={tdS}><strong>{c.intermediate}</strong></td>
                  <td style={tdS}>{c.org}</td>
                  <td style={tdS}><span style={{ color: '#7c3aed' }}>{c.rootCa}</span></td>
                  <td style={tdS}><span style={{ fontSize: 10, color: '#6b7280' }}>{c.trustStore}</span></td>
                  <td style={tdS}>{fmt(c.count)}</td>
                  <td style={tdS}><span style={{ color: '#059669' }}>{fmt(c.valid)}</span></td>
                  <td style={tdS}><span style={{ color: c.revocationPct > 1.5 ? '#dc2626' : '#059669' }}>{c.revocationPct}%</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {selected && (
        <DrilldownPanel
          pageId="chains"
          title={`Chain Investigation: ${selected.intermediate}`}
          question={`Tell me about the certificate chain through ${selected.intermediate} (issued by ${selected.org}, root: ${selected.rootCa}). It has ${selected.count} chains with a ${selected.revocationPct}% revocation rate. What certificates use this chain, are there validity issues, and what is the risk?`}
          onClose={handleClose}
          drilldowns={[
            { label: 'Chain Validity Issues', question: `What are the invalid chain issues for ${selected.intermediate}?` },
            { label: 'Affected Devices', question: `Which device types use certificates from ${selected.intermediate}?` },
            { label: 'Revocation Risk', question: `What is the revocation risk for ${selected.intermediate} with ${selected.revocationPct}% rate?` },
          ]}
        />
      )}
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, padding: 16, borderLeft: `4px solid ${color}` }}>
      <div style={{ fontSize: 11, color: '#6b7280' }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color }}>{fmt(value)}</div>
    </div>
  );
}

const thS: React.CSSProperties = { textAlign: 'left', padding: '10px 12px', borderBottom: '2px solid #e2e8f0', color: '#6b7280', fontWeight: 600, fontSize: 11, textTransform: 'uppercase' };
const tdS: React.CSSProperties = { padding: '10px 12px', borderBottom: '1px solid #f3f4f6', color: '#374151' };
function fmt(n: number) { return n >= 1000000 ? (n/1000000).toFixed(1) + 'M' : n >= 1000 ? (n/1000).toFixed(0) + 'K' : String(n); }
