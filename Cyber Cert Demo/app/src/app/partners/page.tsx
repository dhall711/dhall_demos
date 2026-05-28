'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useChatContext } from '@/context/ChatContext';
const DrilldownPanel = dynamic(() => import('@/components/DrilldownPanel'), { ssr: false });

export default function PartnersPage() {
  const [partners, setPartners] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { getPageSelection, setPageSelection, clearDrilldown } = useChatContext();
  const selected = getPageSelection('partners');

  useEffect(() => {
    fetch('/api/data?q=partners').then(r => r.json()).then(d => { setPartners(d.partners || []); setLoading(false); });
  }, []);

  function handleClose() {
    setPageSelection('partners', null);
    clearDrilldown('partners');
  }

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading partners...</div>;

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Partner Compliance</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>Certificate compliance by technology partner • <span style={{ color: '#0066cc' }}>Click a row for AI investigation</span></p>

      <div style={{ display: 'flex', gap: 16 }}>
        <div style={{ flex: selected ? '0 0 55%' : '1 1 100%', background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.04)', transition: 'flex 0.2s' }}>
          <div style={{ maxHeight: selected ? 'calc(100vh - 180px)' : 'none', overflowY: 'auto' }}>
            <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f9fafb', position: 'sticky', top: 0, zIndex: 1 }}>
                  <th style={thS}>Partner</th><th style={thS}>Industry</th><th style={thS}>Tier</th><th style={thS}>Certs</th><th style={thS}>Compliance</th><th style={thS}>Risk</th>
                </tr>
              </thead>
              <tbody>
                {partners.map((p, i) => {
                  const active = selected?.partner === p.partner;
                  return (
                    <tr key={i} onClick={() => { if (active) { handleClose(); } else { setPageSelection('partners', p); clearDrilldown('partners'); } }} style={{ background: active ? '#eff6ff' : i % 2 === 0 ? '#fff' : '#f9fafb', cursor: 'pointer', transition: 'background 0.1s', borderLeft: active ? '3px solid #0066cc' : '3px solid transparent' }} onMouseEnter={e => { if (!active) e.currentTarget.style.background = '#f0f9ff'; }} onMouseLeave={e => { if (!active) e.currentTarget.style.background = i % 2 === 0 ? '#fff' : '#f9fafb'; }}>
                      <td style={tdS}><strong style={{ color: '#111827' }}>{p.partner}</strong></td>
                      <td style={tdS}><span style={{ color: '#6b7280', fontSize: 11 }}>{p.industry || '-'}</span></td>
                      <td style={tdS}><span style={{ padding: '2px 6px', borderRadius: 4, fontSize: 10, fontWeight: 600, background: p.tier === 'GOLD' ? '#fef3c7' : p.tier === 'SILVER' ? '#f3f4f6' : '#fed7aa', color: p.tier === 'GOLD' ? '#92400e' : p.tier === 'SILVER' ? '#374151' : '#9a3412' }}>{p.tier}</span></td>
                      <td style={tdS}>{fmt(p.total)}</td>
                      <td style={tdS}><span style={{ fontWeight: 600, color: p.compliancePct >= 80 ? '#059669' : p.compliancePct >= 60 ? '#d97706' : '#dc2626' }}>{p.compliancePct}%</span></td>
                      <td style={tdS}><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 5, background: p.compliancePct >= 80 ? '#059669' : p.compliancePct >= 60 ? '#d97706' : '#dc2626' }} /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {selected && (
          <div style={{ flex: '0 0 43%', maxHeight: 'calc(100vh - 180px)', overflowY: 'auto' }}>
            <DrilldownPanel
              pageId="partners"
              title={`${selected.partner}`}
              question={`Tell me about ${selected.partner}'s certificate compliance. They have ${fmt(selected.total)} total certificates at ${selected.compliancePct}% compliance with ${fmt(selected.nonCompliant)} non-compliant and ${fmt(selected.selfSigned)} self-signed. What specific violations do they have, which device types are affected, and what is the remediation priority?`}
              onClose={handleClose}
              drilldowns={[
                { label: 'Violation Types', question: `What types of compliance violations does ${selected.partner} have?` },
                { label: 'By Device', question: `How are ${selected.partner}'s certificates distributed across device types?` },
                { label: 'By Region', question: `Which regions have ${selected.partner}'s non-compliant certificates?` },
                { label: 'Remediation', question: `What is the recommended remediation plan for ${selected.partner}?` },
              ]}
            />
          </div>
        )}
      </div>
    </div>
  );
}

const thS: React.CSSProperties = { textAlign: 'left', padding: '10px 12px', borderBottom: '2px solid #e2e8f0', color: '#6b7280', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px' };
const tdS: React.CSSProperties = { padding: '10px 12px', borderBottom: '1px solid #f3f4f6', color: '#374151' };
function fmt(n: number) { return n >= 1000000 ? (n/1000000).toFixed(1) + 'M' : n >= 1000 ? (n/1000).toFixed(0) + 'K' : String(n); }
