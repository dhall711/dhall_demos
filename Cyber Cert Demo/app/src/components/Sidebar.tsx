'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, MessageSquare, Users, Cpu, Globe2, Search, Workflow, Link2, RefreshCw, TrendingUp, Code2, Presentation } from 'lucide-react';

const NAV = [
  { href: '/intro', label: 'Introduction', icon: Presentation },
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/chat', label: 'Agent Chat', icon: MessageSquare },
  { href: '/chains', label: 'Chain Explorer', icon: Link2 },
  { href: '/lifecycle', label: 'Lifecycle', icon: RefreshCw },
  { href: '/partners', label: 'Partners', icon: Users },
  { href: '/devices', label: 'Devices', icon: Cpu },
  { href: '/geography', label: 'Geography', icon: Globe2 },
  { href: '/forecast', label: 'Forecast', icon: TrendingUp },
  { href: '/investigate', label: 'Investigate', icon: Search },
  { href: '/api-access', label: 'Developer API', icon: Code2 },
  { href: '/architecture', label: 'Architecture', icon: Workflow },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside style={{ width: 220, background: '#ffffff', borderRight: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
      <div style={{ padding: '20px 16px', borderBottom: '1px solid #e2e8f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #29b6f6, #0066cc)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 'bold', color: '#fff' }}>C</div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 13, color: '#1a1a2e' }}>Cert Compliance</div>
            <div style={{ fontSize: 10, color: '#6b7280' }}>Snowflake Cortex</div>
          </div>
        </div>
      </div>
      <nav style={{ flex: 1, padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderRadius: 8, textDecoration: 'none',
              background: active ? '#e8f4fd' : 'transparent',
              color: active ? '#0066cc' : '#4b5563',
              fontSize: 13, fontWeight: active ? 600 : 400,
              transition: 'all 0.15s'
            }}>
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div style={{ padding: '12px 16px', borderTop: '1px solid #e2e8f0', fontSize: 10, color: '#9ca3af' }}>
        50M+ Certificates | Powered by Snowflake
      </div>
    </aside>
  );
}
