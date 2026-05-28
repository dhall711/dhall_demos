'use client';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useState } from 'react';

type Location = { name: string; city: string; lat: number; lng: number; region: string; certs: number; nonCompliant: number; compliancePct: number };

export default function MapView({ locations }: { locations: Location[] }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  if (!mounted) return <div style={{height:'100%',display:'flex',alignItems:'center',justifyContent:'center'}}>Initializing map...</div>;

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer center={[30, 0]} zoom={2} zoomControl={true} scrollWheelZoom={true} style={{ height: '100%', width: '100%', minHeight: 500 }}>
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {locations.map((loc, i) => {
          if (!loc.lat || !loc.lng) return null;
          const radius = Math.max(12, Math.min(35, Math.sqrt(loc.certs / 40000)));
          const color = loc.compliancePct >= 80 ? '#059669' : loc.compliancePct >= 60 ? '#d97706' : '#dc2626';
          return (
            <CircleMarker key={i} center={[loc.lat, loc.lng]} radius={radius} pathOptions={{ color, fillColor: color, fillOpacity: 0.45, weight: 2 }}>
              <Popup>
                <div style={{ fontFamily: 'system-ui', fontSize: 12, minWidth: 200 }}>
                  <strong style={{ fontSize: 14, color: '#111827' }}>{loc.name}</strong><br/>
                  <span style={{ color: '#6b7280' }}>{loc.city} ({loc.region})</span>
                  <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '8px 0' }}/>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
                    <div style={{color:'#6b7280'}}>Certificates:</div><div><strong>{(loc.certs/1000000).toFixed(2)}M</strong></div>
                    <div style={{color:'#6b7280'}}>Compliance:</div><div><strong style={{ color }}>{loc.compliancePct}%</strong></div>
                    <div style={{color:'#6b7280'}}>Non-Compliant:</div><div><strong style={{color:'#dc2626'}}>{(loc.nonCompliant/1000).toFixed(0)}K</strong></div>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
