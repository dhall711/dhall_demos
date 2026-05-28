'use client';
import { useEffect, useState } from 'react';
import { WORLD_PATHS } from './worldpaths';

type Location = { name: string; city: string; lat: number; lng: number; region: string; certs: number; nonCompliant: number; compliancePct: number };

export default function GeographyPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selected, setSelected] = useState<Location | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/data?q=geo').then(r => r.json()).then(d => { setLocations(d.locations || []); setLoading(false); });
  }, []);

  if (loading) return <div style={{ padding: 40, color: '#6b7280' }}>Loading geography data...</div>;

  return (
    <div style={{ padding: 24, animation: 'fadeIn 0.3s ease' }}>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Geographic Distribution</h1>
      <p style={{ color: '#6b7280', fontSize: 13, marginBottom: 20 }}>Certificate density and compliance by data center. Circle size = volume, color = compliance.</p>

      <div style={{ display: 'flex', gap: 20 }}>
        <div style={{ flex: 1, background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <svg viewBox="-180 -90 360 180" style={{ width: '100%', height: 'auto', minHeight: 420 }} preserveAspectRatio="xMidYMid meet">
            <rect x="-180" y="-90" width="360" height="180" fill="#f8fafc" />
            <path d={WORLD_PATHS} fill="#e2e8f0" stroke="#cbd5e1" strokeWidth="0.2" fillRule="evenodd" />
            {locations.filter(l => l.lat && l.lng).map((loc, i) => {
              const x = loc.lng;
              const y = -loc.lat;
              const r = Math.max(2.5, Math.min(8, Math.sqrt(loc.certs / 300000)));
              const color = loc.compliancePct >= 80 ? '#059669' : loc.compliancePct >= 60 ? '#d97706' : '#dc2626';
              const isSelected = selected?.name === loc.name;
              return (
                <g key={i} onClick={() => setSelected(loc)} style={{ cursor: 'pointer' }}>
                  {isSelected && <circle cx={x} cy={y} r={r + 2} fill="none" stroke={color} strokeWidth="1" strokeDasharray="2,1" />}
                  <circle cx={x} cy={y} r={r} fill={color} fillOpacity={0.6} stroke={color} strokeWidth={isSelected ? 1.2 : 0.6} />
                  <title>{loc.name} - {loc.city} ({loc.compliancePct}%)</title>
                </g>
              );
            })}
          </svg>
          <div style={{ display: 'flex', gap: 20, marginTop: 10, justifyContent: 'center', fontSize: 11, color: '#6b7280' }}>
            <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 5, background: '#059669', marginRight: 4, verticalAlign: 'middle' }} />80%+ Compliant</span>
            <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 5, background: '#d97706', marginRight: 4, verticalAlign: 'middle' }} />60-80%</span>
            <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 5, background: '#dc2626', marginRight: 4, verticalAlign: 'middle' }} />&lt;60%</span>
          </div>
        </div>

        <div style={{ width: 300, display: 'flex', flexDirection: 'column', gap: 12 }}>
          {selected ? (
            <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#111827', marginBottom: 4 }}>{selected.name}</h3>
              <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>{selected.city} ({selected.region})</p>
              <Stat label="Total Certificates" value={fmt(selected.certs)} />
              <Stat label="Compliance Rate" value={`${selected.compliancePct}%`} color={selected.compliancePct >= 80 ? '#059669' : selected.compliancePct >= 60 ? '#d97706' : '#dc2626'} />
              <Stat label="Non-Compliant" value={fmt(selected.nonCompliant)} color="#dc2626" />
              <div style={{ marginTop: 12, height: 8, borderRadius: 4, background: '#f3f4f6', overflow: 'hidden' }}>
                <div style={{ height: 8, borderRadius: 4, background: selected.compliancePct >= 80 ? '#059669' : selected.compliancePct >= 60 ? '#d97706' : '#dc2626', width: `${selected.compliancePct}%`, transition: 'width 0.3s' }} />
              </div>
            </div>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, textAlign: 'center', color: '#9ca3af', fontSize: 13 }}>
              Click a data center marker to view details
            </div>
          )}

          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.04)', flex: 1 }}>
            <h4 style={{ fontSize: 11, color: '#6b7280', fontWeight: 600, marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Data Centers by Volume</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {locations.filter(l => l.lat && l.lng).sort((a, b) => b.certs - a.certs).map((loc, i) => {
                const color = loc.compliancePct >= 80 ? '#059669' : loc.compliancePct >= 60 ? '#d97706' : '#dc2626';
                return (
                  <div key={i} onClick={() => setSelected(loc)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 10px', borderRadius: 6, cursor: 'pointer', background: selected?.name === loc.name ? '#eff6ff' : 'transparent', fontSize: 12, transition: 'background 0.1s' }}>
                    <div>
                      <span style={{ color: '#374151', fontWeight: 500 }}>{loc.city}</span>
                      <span style={{ color: '#9ca3af', marginLeft: 6 }}>{loc.region}</span>
                    </div>
                    <span style={{ fontWeight: 600, color }}>{loc.compliancePct}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f3f4f6' }}>
      <span style={{ fontSize: 12, color: '#6b7280' }}>{label}</span>
      <span style={{ fontSize: 14, fontWeight: 700, color: color || '#111827' }}>{value}</span>
    </div>
  );
}

function fmt(n: number) { return n >= 1000000 ? (n / 1000000).toFixed(2) + 'M' : n >= 1000 ? (n / 1000).toFixed(0) + 'K' : String(n); }
