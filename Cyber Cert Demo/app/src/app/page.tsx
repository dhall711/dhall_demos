'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useChatContext } from '@/context/ChatContext';
const DrilldownPanel = dynamic(() => import('@/components/DrilldownPanel'), { ssr: false });

type KPI = { label: string; value: string; sub: string; color: string };

const KPI_QUESTIONS: Record<string, { q: string; drilldowns: { label: string; question: string }[] }> = {
  'Total Certificates': { q: 'Give me a summary of our total certificate inventory broken down by region and device type', drilldowns: [{ label: 'By Region', question: 'Show total certificates by region with compliance rates' }, { label: 'By Source System', question: 'How are certificates distributed across source systems?' }, { label: 'Growth Trend', question: 'What is the certificate issuance trend over the past 90 days?' }] },
  'Compliance Rate': { q: 'What are the main drivers of non-compliance across our certificate fleet? Which regions and partners are most affected?', drilldowns: [{ label: 'By Violation Type', question: 'Break down non-compliance by violation type - self-signed, weak key, SHA-1, expired' }, { label: 'Worst Partners', question: 'Which 10 partners have the lowest compliance rates and why?' }, { label: 'Remediation Priority', question: 'What is the prioritized remediation plan for non-compliant certificates?' }] },
  'Expiring (30 days)': { q: 'We have certificates expiring within 30 days. Which device types and partners are most affected? What renewal actions should we prioritize?', drilldowns: [{ label: 'By Partner', question: 'Which partners have the most certificates expiring in 30 days?' }, { label: 'By Device', question: 'Which device types have the most certificates expiring soon?' }, { label: 'Auto-Renewal Status', question: 'How many expiring certificates are covered by ACME auto-renewal vs manual renewal?' }] },
  'Non-Compliant': { q: 'Break down all non-compliant certificates by violation type, region, and partner. What is the severity distribution?', drilldowns: [{ label: 'Critical Violations', question: 'Which non-compliant certificates have CRITICAL severity policy violations?' }, { label: 'By Region', question: 'Show non-compliant certificate counts by region with violation types' }, { label: 'Policy Rules', question: 'What compliance rules are being violated and what are their severity levels?' }] },
  'Expired': { q: 'Show me expired certificates - which regions and device types are most affected? What is the risk exposure?', drilldowns: [{ label: 'By Age', question: 'How long have expired certificates been expired? Show distribution by weeks/months' }, { label: 'By Partner', question: 'Which partners have the most expired certificates?' }, { label: 'Impact Assessment', question: 'What is the security risk of expired certificates by device type?' }] },
  'Self-Signed': { q: 'Show the distribution of self-signed certificates by device type and partner. What is the remediation plan per our policies?', drilldowns: [{ label: 'By Device Type', question: 'Which device types have the highest self-signed certificate rates?' }, { label: 'Policy Guidance', question: 'What does our compliance policy say about self-signed certificates and their remediation?' }, { label: 'Migration Plan', question: 'What is the migration path from self-signed to CA-issued certificates?' }] },
};

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [byRegion, setByRegion] = useState<any[]>([]);
  const [byDevice, setByDevice] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { getPageSelection, setPageSelection, clearDrilldown } = useChatContext();
  const selected = getPageSelection('dashboard') as { type: string; title: string; question: string; drilldowns: { label: string; question: string }[] } | null;

  useEffect(() => {
    fetch('/api/data?q=kpis').then(r => r.json()).then(d => { setKpis(d.kpis || []); setByRegion(d.byRegion || []); setByDevice(d.byDevice || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  function selectKPI(k: KPI) {
    const cfg = KPI_QUESTIONS[k.label] || { q: `Tell me more about ${k.label}`, drilldowns: [] };
    setPageSelection('dashboard', { type: 'kpi', title: `Investigation: ${k.label}`, question: cfg.q, drilldowns: cfg.drilldowns });
  }

  function selectRegion(r: any) {
    setPageSelection('dashboard', { type: 'region', title: `Region Deep Dive: ${r.region}`, question: `Deep dive into the ${r.region} region certificate compliance. What is driving their ${r.compliance_pct}% compliance rate? Which partners and device types are most problematic in ${r.region}?`, drilldowns: [{ label: 'Top Violations', question: `What are the top compliance violations in ${r.region}?` }, { label: 'Partners at Risk', question: `Which partners in ${r.region} have compliance below 70%?` }, { label: 'Remediation Plan', question: `What is the remediation priority for ${r.region} region?` }] });
  }

  function selectDevice(d: any) {
    setPageSelection('dashboard', { type: 'device', title: `Device Analysis: ${d.device_type}`, question: `Analyze ${d.device_type} device certificates - what compliance issues exist? Show self-signed rates, expiry risks, and partner distribution for ${d.device_type} devices.`, drilldowns: [{ label: 'By Partner', question: `Which partners issue the most ${d.device_type} certificates and what are their compliance rates?` }, { label: 'By Region', question: `How are ${d.device_type} certificates distributed across regions?` }, { label: 'Security Risks', question: `What are the key security risks for ${d.device_type} certificates?` }] });
  }

  function handleClose() {
    setPageSelection('dashboard', null);
    clearDrilldown('dashboard');
  }

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading dashboard...</div>;

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Certificate Compliance Dashboard</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>Real-time compliance posture across 50M+ certificates • <span style={{ color: '#0066cc' }}>Click any element for AI investigation</span></p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 16 }}>
        {kpis.map((k, i) => {
          const active = selected?.type === 'kpi' && selected.title.includes(k.label);
          return (
            <div key={i} onClick={() => selectKPI(k)} style={{ background: active ? '#eff6ff' : '#fff', border: `1px solid ${active ? '#0066cc' : '#e2e8f0'}`, borderRadius: 12, padding: 20, borderLeft: `4px solid ${k.color}`, boxShadow: active ? '0 2px 8px rgba(0,102,204,0.1)' : '0 1px 3px rgba(0,0,0,0.04)', cursor: 'pointer', transition: 'all 0.15s' }}>
              <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 8, fontWeight: 500 }}>{k.label}</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: k.color }}>{k.value}</div>
              <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 4 }}>{k.sub}</div>
            </div>
          );
        })}
      </div>

      {selected && <DrilldownPanel pageId="dashboard" question={selected.question} title={selected.title} onClose={handleClose} drilldowns={selected.drilldowns} key={selected.question} />}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 24 }}>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <h3 style={{ fontSize: 14, marginBottom: 12, color: '#374151', fontWeight: 600 }}>By Region <span style={{ fontSize: 10, color: '#9ca3af', fontWeight: 400 }}>• click row to investigate</span></h3>
          <table style={{ width: '100%', fontSize: 12 }}>
            <thead><tr><th style={thS}>Region</th><th style={thS}>Total</th><th style={thS}>Compliant %</th><th style={thS}>Non-Compliant</th></tr></thead>
            <tbody>{byRegion.map((r, i) => (
              <tr key={i} onClick={() => selectRegion(r)} style={{ cursor: 'pointer', transition: 'background 0.1s' }} onMouseEnter={e => (e.currentTarget.style.background = '#f0f9ff')} onMouseLeave={e => (e.currentTarget.style.background = '')}>
                <td style={tdS}><strong>{r.region}</strong></td><td style={tdS}>{fmt(r.total)}</td><td style={{...tdS, color: r.compliance_pct >= 80 ? '#059669' : '#dc2626', fontWeight: 600}}>{r.compliance_pct}%</td><td style={tdS}>{fmt(r.non_compliant)}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <h3 style={{ fontSize: 14, marginBottom: 12, color: '#374151', fontWeight: 600 }}>By Device Type <span style={{ fontSize: 10, color: '#9ca3af', fontWeight: 400 }}>• click row to investigate</span></h3>
          <table style={{ width: '100%', fontSize: 12 }}>
            <thead><tr><th style={thS}>Device</th><th style={thS}>Total</th><th style={thS}>Self-Signed</th><th style={thS}>Expired</th></tr></thead>
            <tbody>{byDevice.map((r, i) => (
              <tr key={i} onClick={() => selectDevice(r)} style={{ cursor: 'pointer', transition: 'background 0.1s' }} onMouseEnter={e => (e.currentTarget.style.background = '#f0f9ff')} onMouseLeave={e => (e.currentTarget.style.background = '')}>
                <td style={tdS}><strong>{r.device_type}</strong></td><td style={tdS}>{fmt(r.total)}</td><td style={tdS}>{fmt(r.self_signed)}</td><td style={tdS}>{fmt(r.expired)}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const thS: React.CSSProperties = { textAlign: 'left', padding: '8px 10px', borderBottom: '1px solid #e2e8f0', color: '#6b7280', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px' };
const tdS: React.CSSProperties = { padding: '8px 10px', borderBottom: '1px solid #f3f4f6', color: '#374151' };
function fmt(n: number) { return n >= 1000000 ? (n/1000000).toFixed(1) + 'M' : n >= 1000 ? (n/1000).toFixed(0) + 'K' : String(n); }
