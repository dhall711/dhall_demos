'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useChatContext } from '@/context/ChatContext';
const DrilldownPanel = dynamic(() => import('@/components/DrilldownPanel'), { ssr: false });

export default function DevicesPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { getPageSelection, setPageSelection, clearDrilldown } = useChatContext();
  const selected = getPageSelection('devices');

  useEffect(() => {
    fetch('/api/data?q=kpis').then(r => r.json()).then(d => { setData(d.byDevice || []); setLoading(false); });
  }, []);

  function handleClose() {
    setPageSelection('devices', null);
    clearDrilldown('devices');
  }

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading devices...</div>;

  const colors: Record<string, string> = { IoT: '#0066cc', Streaming: '#7c3aed', Gateway: '#059669', Server: '#d97706', Partner: '#dc2626' };
  const total = data.reduce((a, d) => a + d.total, 0);

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Device Type Analysis</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>Certificate distribution and compliance by device category • <span style={{ color: '#0066cc' }}>Click a card to investigate</span></p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 16 }}>
        {data.map((d, i) => {
          const active = selected?.device_type === d.device_type;
          return (
            <div key={i} onClick={() => { if (active) { handleClose(); } else { setPageSelection('devices', d); clearDrilldown('devices'); } }} style={{ background: active ? '#eff6ff' : '#fff', border: `1px solid ${active ? '#0066cc' : '#e2e8f0'}`, borderRadius: 12, padding: 20, borderTop: `3px solid ${colors[d.device_type] || '#0066cc'}`, boxShadow: active ? '0 2px 8px rgba(0,102,204,0.1)' : '0 1px 3px rgba(0,0,0,0.04)', cursor: 'pointer', transition: 'all 0.15s' }}>
              <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 500 }}>{d.device_type}</div>
              <div style={{ fontSize: 26, fontWeight: 700, color: colors[d.device_type] || '#0066cc', margin: '4px 0' }}>{fmt(d.total)}</div>
              <div style={{ fontSize: 11, color: '#9ca3af' }}>{(100 * d.total / total).toFixed(1)}% of total inventory</div>
              <div style={{ marginTop: 10, height: 6, borderRadius: 3, background: '#f3f4f6' }}>
                <div style={{ height: 6, borderRadius: 3, background: colors[d.device_type], width: `${100 * d.total / total}%`, transition: 'width 0.5s' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 10, fontSize: 11, color: '#6b7280' }}>
                <span>Self-signed: <strong style={{ color: '#d97706' }}>{fmt(d.self_signed)}</strong></span>
                <span>Expired: <strong style={{ color: '#dc2626' }}>{fmt(d.expired)}</strong></span>
              </div>
            </div>
          );
        })}
      </div>

      {selected && (
        <DrilldownPanel
          pageId="devices"
          title={`Device Investigation: ${selected.device_type}`}
          question={`Analyze ${selected.device_type} device certificates in detail. They have ${fmt(selected.total)} total, ${fmt(selected.self_signed)} self-signed, and ${fmt(selected.expired)} expired. What are the compliance issues, which partners issue the most ${selected.device_type} certs, and what are the key risks?`}
          onClose={handleClose}
          drilldowns={[
            { label: 'By Partner', question: `Which partners issue ${selected.device_type} certificates and what are their compliance rates?` },
            { label: 'By Region', question: `How are ${selected.device_type} certificates distributed across regions?` },
            { label: 'Self-Signed Analysis', question: `Why are there ${fmt(selected.self_signed)} self-signed ${selected.device_type} certificates? What policy applies?` },
            { label: 'Security Risks', question: `What are the security risks of ${selected.device_type} certificates with weak keys or deprecated algorithms?` },
          ]}
        />
      )}
    </div>
  );
}

function fmt(n: number) { return n >= 1000000 ? (n/1000000).toFixed(1) + 'M' : n >= 1000 ? (n/1000).toFixed(0) + 'K' : String(n); }
