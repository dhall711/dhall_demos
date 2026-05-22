import { useState, useEffect } from 'react';
import { FileText, Search, X, RefreshCw } from 'lucide-react';

interface Document {
  id: string;
  title: string;
  content: string;
  category: string;
  dateAdded: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

export default function DocumentManager({ isOpen, onClose }: Props) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) loadDocuments();
  }, [isOpen]);

  async function loadDocuments() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/documents`);
      if (res.ok) {
        setDocuments(await res.json());
      } else {
        setDocuments(getMockDocuments());
      }
    } catch {
      setDocuments(getMockDocuments());
    } finally {
      setLoading(false);
    }
  }

  const filtered = documents.filter(d =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-semibold text-lg flex items-center gap-2">
            <FileText className="w-5 h-5 text-comcast-blue" /> Knowledge Base
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Search knowledge base..." className="w-full pl-9 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-comcast-blue focus:border-transparent" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-8 text-gray-400">
              <RefreshCw className="w-5 h-5 animate-spin mr-2" /> Loading...
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-8 text-gray-400">No documents found</div>
          ) : (
            filtered.map(doc => (
              <div key={doc.id} className="p-3 border border-gray-200 rounded-lg hover:border-comcast-blue transition">
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-1.5 py-0.5 text-[10px] font-medium bg-gray-100 rounded">{doc.category}</span>
                  <span className="text-xs text-gray-400">{doc.dateAdded}</span>
                </div>
                <h3 className="font-medium text-sm text-gray-900">{doc.title}</h3>
                <p className="text-xs text-gray-600 mt-1 line-clamp-2">{doc.content}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function getMockDocuments(): Document[] {
  return [
    { id: '1', title: 'Week 5 Executive Summary', content: 'California logistics strained due to Broadcom BCM3390 chipset shortage affecting XB8 gateway production.', category: 'Narrative', dateAdded: '2026-02-08' },
    { id: '2', title: 'T-Mobile Competitive Alert', content: 'T-Mobile Rely plan ($50/mo) and bundle pricing ($35) driving unexpected customer acquisition in CA/TX metro areas.', category: 'Market Intel', dateAdded: '2026-02-05' },
    { id: '3', title: 'Texas On-Demand Expansion', content: 'On-demand delivery radius expanded to 75 miles in Texas. Impacting shipping capacity and OTS metrics.', category: 'Operations', dateAdded: '2026-02-03' },
    { id: '4', title: 'Weather Impact - Northeast', content: 'Winter storm affecting Northeast corridor deliveries. Expected 3-5 day delay on ground shipments.', category: 'External', dateAdded: '2026-02-01' },
    { id: '5', title: 'DOCSIS 4.0 Migration Plan', content: 'Broadcom BCM3390 is sole supplier for DOCSIS 4.0 chipset. Alternate qualification in progress with Qualcomm.', category: 'Technology', dateAdded: '2026-01-28' },
  ];
}
