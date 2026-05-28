'use client';
import { useState } from 'react';
import { AlertTriangle, Shield, Clock, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatContext } from '@/context/ChatContext';
import SEED_CACHE from '@/data/seedCache';

const METRICS = [
  { id: 'compliance_rate', label: 'Compliance Rate', value: '75.0%', target: '85%', severity: 'HIGH', trend: '-2.1%', icon: Shield, color: '#dc2626', question: 'Why is the overall compliance rate below target? What are the main drivers of non-compliance?', drilldowns: [{ label: 'By Violation Type', question: 'Break down non-compliance by violation type across all regions' }, { label: 'Trend Analysis', question: 'What is the compliance rate trend over time?' }, { label: 'Action Plan', question: 'What are the top 5 actions to improve compliance rate from 75% to 85%?' }] },
  { id: 'expiring_30d', label: 'Expiring (30 days)', value: '2.0M', target: '<500K', severity: 'CRITICAL', trend: '+18%', icon: Clock, color: '#dc2626', question: 'We have 2 million certificates expiring in 30 days. Which device types and partners are most affected? What renewal actions should we prioritize?', drilldowns: [{ label: 'By Partner', question: 'Top 10 partners with most expiring certificates in 30 days' }, { label: 'Auto-Renewal Coverage', question: 'How many expiring certs are covered by ACME vs manual?' }, { label: 'Escalation List', question: 'Which critical infrastructure certs expire in 7 days?' }] },
  { id: 'self_signed', label: 'Self-Signed Certs', value: '1.9M', target: '0', severity: 'HIGH', trend: '-5%', icon: AlertTriangle, color: '#d97706', question: 'Show me the distribution of self-signed certificates by device type and partner. What is the remediation plan per our policies?', drilldowns: [{ label: 'By Device Type', question: 'Which device types have the most self-signed certificates?' }, { label: 'Policy Reference', question: 'What does our compliance policy say about self-signed certificates?' }, { label: 'Migration Path', question: 'What is the recommended CA migration path for self-signed certs?' }] },
  { id: 'sha1_deprecated', label: 'SHA-1 Signatures', value: '~1.6M', target: '0 by Q2', severity: 'MEDIUM', trend: '-12%', icon: Activity, color: '#d97706', question: 'How many certificates still use SHA-1 signatures? What is the deprecation timeline and which device categories are most exposed?', drilldowns: [{ label: 'By Region', question: 'Which regions have the most SHA-1 certificates?' }, { label: 'Deprecation Timeline', question: 'What is the SHA-1 deprecation policy and deadline?' }, { label: 'Replacement Options', question: 'What signature algorithms should replace SHA-1?' }] },
  { id: 'partner_risk', label: 'At-Risk Partners', value: '5', target: '0', severity: 'MEDIUM', trend: 'stable', icon: AlertTriangle, color: '#d97706', question: 'Which partners have compliance rates below 60%? What specific violations do they have and what is the remediation path?', drilldowns: [{ label: 'Partner Details', question: 'List all partners below 60% compliance with their violation types' }, { label: 'SLA Impact', question: 'What SLA penalties apply to non-compliant partners?' }, { label: 'Outreach Plan', question: 'What is the recommended partner outreach plan for compliance remediation?' }] },
];

export default function InvestigatePage() {
  const { getPageSelection, setPageSelection, getDrilldown, setDrilldown, clearDrilldown } = useChatContext();
  const selected = getPageSelection('investigate') as string | null;
  const persisted = getDrilldown('investigate');
  const [response, setResponse] = useState(persisted.response || '');
  const [loading, setLoading] = useState(false);
  const [activeQuestion, setActiveQuestion] = useState(persisted.question || '');

  async function investigate(question: string, metricId?: string) {
    if (metricId) setPageSelection('investigate', metricId);
    setActiveQuestion(question);

    const seedKey = `investigate:${metricId || selected}`;
    if (SEED_CACHE[seedKey] && !response) {
      setResponse(SEED_CACHE[seedKey]);
      setDrilldown('investigate', { response: SEED_CACHE[seedKey], question, selectedKey: metricId || selected });
      return;
    }

    setResponse('');
    setLoading(true);
    try {
      const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: [{ role: 'user', content: question }], stream: false }) });
      const data = await res.json();
      const text = data.text || data.error || 'No response';
      setResponse(text);
      setDrilldown('investigate', { response: text, question, selectedKey: metricId || selected });
    } catch (e: any) {
      const errMsg = `Error: ${e.message}`;
      setResponse(errMsg);
      setDrilldown('investigate', { response: errMsg, question, selectedKey: metricId || selected });
    }
    finally { setLoading(false); }
  }

  const selectedMetric = METRICS.find(m => m.id === selected);

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Compliance Investigation</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 24 }}>Click a metric card to launch an AI-powered root cause investigation</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 12, marginBottom: 24 }}>
        {METRICS.map(m => {
          const Icon = m.icon;
          const active = selected === m.id;
          return (
            <div key={m.id} onClick={() => investigate(m.question, m.id)} style={{
              background: active ? '#eff6ff' : '#fff', border: `1px solid ${active ? '#0066cc' : '#e2e8f0'}`,
              borderLeft: `4px solid ${m.color}`, borderRadius: 10, padding: 16, cursor: 'pointer', transition: 'all 0.2s', boxShadow: active ? '0 2px 8px rgba(0,102,204,0.1)' : '0 1px 3px rgba(0,0,0,0.04)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <Icon size={16} color={m.color} />
                <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, fontWeight: 600, background: m.severity === 'CRITICAL' ? '#fef2f2' : m.severity === 'HIGH' ? '#fff7ed' : '#fefce8', color: m.color }}>{m.severity}</span>
              </div>
              <div style={{ fontSize: 11, color: '#6b7280', fontWeight: 500 }}>{m.label}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: m.color, margin: '4px 0' }}>{m.value}</div>
              <div style={{ fontSize: 10, color: '#9ca3af' }}>Target: {m.target} | WoW: {m.trend}</div>
            </div>
          );
        })}
      </div>

      {(loading || response) && (
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <div style={{ fontSize: 14, color: '#0066cc', fontWeight: 600, marginBottom: 4 }}>
            Investigation: {selectedMetric?.label}
          </div>
          <div style={{ fontSize: 11, color: '#9ca3af', marginBottom: 12 }}>{activeQuestion}</div>
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#6b7280', fontSize: 13 }}>
              <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 4, background: '#0066cc', animation: 'pulse 1s infinite' }} />
              Analyzing data across 50M certificates...
            </div>
          ) : (
            <>
              <div style={{ fontSize: 13, lineHeight: 1.8, color: '#374151' }}>
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                  table: ({children}) => <div style={{overflowX:'auto',marginTop:8}}><table style={{width:'100%',fontSize:12,borderCollapse:'collapse',border:'1px solid #e2e8f0'}}>{children}</table></div>,
                  th: ({children}) => <th style={{textAlign:'left',padding:'8px 10px',borderBottom:'2px solid #e2e8f0',color:'#374151',background:'#f9fafb',fontWeight:600}}>{children}</th>,
                  td: ({children}) => <td style={{padding:'6px 10px',borderBottom:'1px solid #f3f4f6'}}>{children}</td>
                }}>{response}</ReactMarkdown>
              </div>
              {selectedMetric && selectedMetric.drilldowns.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 16, paddingTop: 12, borderTop: '1px solid #f3f4f6' }}>
                  <span style={{ fontSize: 10, color: '#9ca3af', alignSelf: 'center' }}>Drill deeper:</span>
                  {selectedMetric.drilldowns.map((dd, i) => (
                    <button key={i} onClick={() => investigate(dd.question)} style={{ padding: '5px 14px', borderRadius: 20, border: '1px solid #bfdbfe', background: activeQuestion === dd.question ? '#dbeafe' : '#f0f9ff', color: '#0066cc', fontSize: 11, cursor: 'pointer', fontWeight: 500, transition: 'all 0.15s' }}>{dd.label}</button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
