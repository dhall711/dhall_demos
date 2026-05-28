import type { Metadata } from 'next';
import Sidebar from '@/components/Sidebar';
import ClientProviders from '@/components/ClientProviders';

export const metadata: Metadata = {
  title: 'Cert Compliance Platform | Snowflake Cortex',
  description: 'AI-powered certificate compliance analytics over 50M+ records'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>{`
          * { box-sizing: border-box; }
          body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8f9fb; color: #1a1a2e; }
          a { color: #0066cc; text-decoration: none; }
          ::selection { background: #0066cc22; }
          ::-webkit-scrollbar { width: 6px; }
          ::-webkit-scrollbar-track { background: #f0f0f0; }
          ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
          @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
          @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
          button:hover { filter: brightness(0.95); }
          input:focus { border-color: #0066cc !important; outline: none; }
          p { margin: 0 0 8px 0; }
          table { border-spacing: 0; }
          pre { margin: 0; white-space: pre-wrap; word-break: break-all; }
        `}</style>
      </head>
      <body>
        <ClientProviders>
          <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
            <Sidebar />
            <main style={{ flex: 1, overflow: 'auto', background: '#f8f9fb' }}>{children}</main>
          </div>
        </ClientProviders>
      </body>
    </html>
  );
}
