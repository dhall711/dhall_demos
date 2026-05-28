'use client';
import Link from 'next/link';
import { ArrowRight, CheckCircle2, Lightbulb, Target, Zap, Shield, Database, Brain, Globe2, Code2 } from 'lucide-react';

const HEARD = [
  { icon: Brain, text: 'AI/RAG chat-with-data for leadership — cert expiry, non-compliance, real-time analytics without writing SQL', color: '#d97706' },
  { icon: Database, text: 'OLTP + OLAP together — compare transactional vs. analytical on a single platform, eliminate data movement', color: '#0066cc' },
  { icon: Zap, text: 'Streaming data ingestion + transformation + enrichment — replace Kinesis → custom ETL with managed pipelines', color: '#059669' },
  { icon: Code2, text: 'API & MCP access to AI capabilities — not just a UI, engineers need programmatic access from services', color: '#7c3aed' },
  { icon: Globe2, text: 'Data residency control — European customers require cert data stays within EU boundaries', color: '#dc2626' },
];

const SOLUTION_TECH = [
  { label: 'Snowflake Postgres', desc: 'OLTP certificate management with full PostgreSQL compatibility', color: '#7c3aed' },
  { label: 'pg_lake → Iceberg', desc: 'Zero-infrastructure CDC mirroring with ~30-second lag', color: '#0066cc' },
  { label: 'Dynamic Tables', desc: 'Declarative medallion pipeline (bronze → silver → gold)', color: '#059669' },
  { label: 'Interactive Table + IWH', desc: 'Sub-100ms KPI queries on pre-aggregated 50M rows', color: '#0891b2' },
  { label: 'Cortex Agent (5 tools)', desc: 'AI orchestrator: 3 Analyst SVs + 1 Search + chain resolution', color: '#d97706' },
  { label: 'SPCS React App', desc: 'Full-stack Next.js with OAuth, streaming AI, public endpoint', color: '#dc2626' },
];



export default function IntroPage() {
  return (
    <div style={{ padding: 32, maxWidth: 1100, margin: '0 auto', animation: 'fadeIn 0.3s ease' }}>
      <div style={{ background: 'linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0066cc 100%)', borderRadius: 16, padding: '48px 40px', marginBottom: 32, color: '#fff', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -100, right: -80, width: 400, height: 400, background: 'radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%)', borderRadius: '50%' }} />
        <div style={{ fontSize: 11, color: '#93c5fd', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8 }}>Comcast GCS Cybersecurity</div>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 12, letterSpacing: -0.5 }}>Certificate Compliance Platform</h1>
        <p style={{ fontSize: 16, opacity: 0.85, maxWidth: 650, lineHeight: 1.7 }}>
          A unified Snowflake solution for managing, analyzing, and securing 50M+ X.509 certificates — from OLTP operations to AI-powered compliance analytics.
        </p>
        <div style={{ display: 'flex', gap: 10, marginTop: 24, flexWrap: 'wrap' }}>
          {['50M+ Certificates', 'Sub-100ms Queries', '5-Tool AI Agent', 'Postgres OLTP', 'Zero-ETL CDC'].map(b => (
            <span key={b} style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 500 }}>{b}</span>
          ))}
        </div>
      </div>

      <section style={{ marginBottom: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: '#fff7ed', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Target size={18} color="#d97706" /></div>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>Here's What We Heard</h2>
        </div>
        <p style={{ fontSize: 14, color: '#6b7280', marginBottom: 20, lineHeight: 1.7 }}>
          From our discovery call — your team manages over 1 billion certificates issued to IoT devices, streaming boxes, gateways, and partner infrastructure. The data lives across Postgres (Aurora/RDS), DynamoDB, and Kinesis streams. Complex joins make compliance insights very difficult today. Here's what you need:
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {HEARD.map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 14, background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: '16px 20px', borderLeft: `4px solid ${item.color}`, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
                <Icon size={18} color={item.color} style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontSize: 14, color: '#374151', lineHeight: 1.6 }}>{item.text}</span>
              </div>
            );
          })}
        </div>
      </section>

      <section style={{ marginBottom: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Lightbulb size={18} color="#059669" /></div>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>Our Solution</h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#111827', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}><Shield size={16} color="#0066cc" /> Business Value</h3>
            <ul style={{ listStyle: 'none', padding: 0, fontSize: 13, color: '#374151', lineHeight: 2 }}>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}><CheckCircle2 size={14} color="#059669" style={{ marginTop: 4, flexShrink: 0 }} /> Replace 4-5 disparate tools with one unified platform</li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}><CheckCircle2 size={14} color="#059669" style={{ marginTop: 4, flexShrink: 0 }} /> Leadership gets instant answers without filing engineering tickets</li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}><CheckCircle2 size={14} color="#059669" style={{ marginTop: 4, flexShrink: 0 }} /> Engineers retain full API/programmatic access to all AI capabilities</li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}><CheckCircle2 size={14} color="#059669" style={{ marginTop: 4, flexShrink: 0 }} /> Sub-second compliance dashboards without pre-aggregation engineering</li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}><CheckCircle2 size={14} color="#059669" style={{ marginTop: 4, flexShrink: 0 }} /> Real-time pipeline (5s–30s latency) replaces batch ETL jobs</li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}><CheckCircle2 size={14} color="#059669" style={{ marginTop: 4, flexShrink: 0 }} /> Data residency controls via Snowflake regional deployments</li>
            </ul>
          </div>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#111827', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}><Zap size={16} color="#d97706" /> Technical Architecture</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {SOLUTION_TECH.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13 }}>
                  <div style={{ width: 8, height: 8, borderRadius: 4, background: s.color, flexShrink: 0 }} />
                  <span style={{ fontWeight: 600, color: '#111827', minWidth: 140 }}>{s.label}</span>
                  <span style={{ color: '#6b7280' }}>{s.desc}</span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 16, padding: '10px 14px', background: '#f8fafc', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: 11, color: '#6b7280', lineHeight: 1.6 }}>
                <strong style={{ color: '#374151' }}>Key differentiator:</strong> All components run inside Snowflake — no external compute, no S3 buckets, no IAM roles, no separate vector DB. One platform, one security perimeter, one governance model.
              </div>
            </div>
          </div>
        </div>
      </section>



      <div style={{ textAlign: 'center', padding: '24px 0' }}>
        <Link href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: '#0066cc', color: '#fff', padding: '12px 28px', borderRadius: 8, fontSize: 14, fontWeight: 600, textDecoration: 'none', boxShadow: '0 2px 8px rgba(0,102,204,0.3)' }}>
          Launch Demo Dashboard <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  );
}
