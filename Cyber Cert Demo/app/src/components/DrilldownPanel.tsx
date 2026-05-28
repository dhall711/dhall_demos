'use client';
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, Loader2, Zap } from 'lucide-react';
import { useChatContext } from '@/context/ChatContext';
import SEED_CACHE from '@/data/seedCache';

interface DrilldownProps {
  pageId: string;
  question: string;
  title: string;
  onClose: () => void;
  drilldowns?: { label: string; question: string }[];
  cacheKey?: string;
}

export default function DrilldownPanel({ pageId, question, title, onClose, drilldowns = [], cacheKey }: DrilldownProps) {
  const { getDrilldown, setDrilldown } = useChatContext();
  const persisted = getDrilldown(pageId);

  const seedKey = cacheKey || `${pageId}:${title.replace(/^(Investigation|Chain Investigation|Device Investigation|Lifecycle State|Forecast Deep Dive|Region Deep Dive|Device Analysis): ?/, '')}`;
  const seedResponse = SEED_CACHE[seedKey];

  const initialResponse = persisted.response || seedResponse || '';
  const hasInstantResponse = !!initialResponse;

  const [response, setResponseLocal] = useState(initialResponse);
  const [loading, setLoading] = useState(!hasInstantResponse);
  const [activeQ, setActiveQ] = useState(persisted.question || question);
  const [elapsed, setElapsed] = useState(0);
  const [fromCache, setFromCache] = useState(!!seedResponse && !persisted.response);
  const abortRef = useRef<AbortController | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const initialized = useRef(false);
  const prefetchedRef = useRef<Record<string, string>>({});

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    if (persisted.response && persisted.question === question) {
      setResponseLocal(persisted.response);
      setActiveQ(persisted.question);
      setLoading(false);
    } else if (seedResponse) {
      setResponseLocal(seedResponse);
      setLoading(false);
      setFromCache(true);
      setDrilldown(pageId, { response: seedResponse, question, selectedKey: pageId });
      prefetchDrilldowns();
    } else {
      ask(question);
    }
    return () => { abortRef.current?.abort(); if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  function prefetchDrilldowns() {
    drilldowns.forEach(dd => {
      const ddSeedKey = `${pageId}:${dd.label}`;
      if (SEED_CACHE[ddSeedKey]) {
        prefetchedRef.current[dd.question] = SEED_CACHE[ddSeedKey];
        return;
      }
      fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [{ role: 'user', content: dd.question }], stream: false })
      }).then(r => r.json()).then(data => {
        if (data.text) prefetchedRef.current[dd.question] = data.text;
      }).catch(() => {});
    });
  }

  async function ask(q: string) {
    if (prefetchedRef.current[q]) {
      const cached = prefetchedRef.current[q];
      setActiveQ(q);
      setResponseLocal(cached);
      setLoading(false);
      setFromCache(false);
      setDrilldown(pageId, { response: cached, question: q, selectedKey: pageId });
      return;
    }

    const ddSeedKey = `${pageId}:${q.split(' ')[0]}`;
    for (const key of Object.keys(SEED_CACHE)) {
      if (key.startsWith(pageId) && q.toLowerCase().includes(key.split(':')[1]?.toLowerCase() || '___')) {
        setActiveQ(q);
        setResponseLocal(SEED_CACHE[key]);
        setLoading(false);
        setFromCache(true);
        setDrilldown(pageId, { response: SEED_CACHE[key], question: q, selectedKey: pageId });
        return;
      }
    }

    setActiveQ(q);
    setLoading(true);
    setResponseLocal('');
    setFromCache(false);
    setElapsed(0);
    abortRef.current?.abort();
    if (timerRef.current) clearInterval(timerRef.current);
    const controller = new AbortController();
    abortRef.current = controller;

    timerRef.current = setInterval(() => setElapsed(e => e + 1), 1000);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [{ role: 'user', content: q }], stream: true }),
        signal: controller.signal
      });

      const contentType = res.headers.get('content-type') || '';
      if (contentType.includes('text/event-stream') && res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buf = '';
        let gotContent = false;
        let fullText = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });
          const lines = buf.split('\n');
          buf = lines.pop() || '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try {
              const data = JSON.parse(line.slice(6));
              if (data.delta) { if (!gotContent) { setLoading(false); gotContent = true; } fullText += data.delta; setResponseLocal(fullText); }
              if (data.text) { if (!gotContent) { setLoading(false); gotContent = true; } fullText += data.text; setResponseLocal(fullText); }
            } catch {}
          }
        }
        if (!gotContent) { fullText = 'No results returned. The agent may not have found matching data for this query.'; setResponseLocal(fullText); }
        setLoading(false);
        setDrilldown(pageId, { response: fullText, question: q, selectedKey: pageId });
      } else {
        const text = await res.text();
        let parsed = '';
        try {
          const data = JSON.parse(text);
          parsed = data.text || data.error || 'No response';
        } catch { parsed = text || 'No response'; }
        setResponseLocal(parsed);
        setLoading(false);
        setDrilldown(pageId, { response: parsed, question: q, selectedKey: pageId });
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        const errMsg = `Error: ${e.message}`;
        setResponseLocal(errMsg);
        setDrilldown(pageId, { response: errMsg, question: q, selectedKey: pageId });
      }
      setLoading(false);
    } finally {
      if (timerRef.current) clearInterval(timerRef.current);
    }
  }

  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginTop: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', animation: 'fadeIn 0.2s ease', position: 'relative' }}>
      <button onClick={onClose} style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 4 }}><X size={16} /></button>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ fontSize: 13, color: '#0066cc', fontWeight: 600, marginBottom: 4 }}>{title}</div>
        {fromCache && <span style={{ fontSize: 9, color: '#059669', background: '#ecfdf5', padding: '2px 6px', borderRadius: 4, fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 3 }}><Zap size={9} />Instant</span>}
      </div>
      <div style={{ fontSize: 11, color: '#9ca3af', marginBottom: 12 }}>{activeQ}</div>

      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: '12px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: '#374151', fontSize: 13 }}>
            <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} color="#0066cc" />
            <span>Cortex Agent is analyzing your question...</span>
          </div>
          <div style={{ fontSize: 11, color: '#9ca3af' }}>
            {elapsed < 5 && 'Planning tool selection...'}
            {elapsed >= 5 && elapsed < 12 && 'Executing SQL query across 50M certificates...'}
            {elapsed >= 12 && elapsed < 20 && 'Processing results and generating insights...'}
            {elapsed >= 20 && elapsed < 30 && 'Synthesizing response (large dataset)...'}
            {elapsed >= 30 && 'Still working — complex queries may take up to 45 seconds...'}
          </div>
          <div style={{ marginTop: 4, height: 3, borderRadius: 2, background: '#f3f4f6', overflow: 'hidden' }}>
            <div style={{ height: 3, borderRadius: 2, background: '#0066cc', width: `${Math.min(95, elapsed * 3)}%`, transition: 'width 1s linear' }} />
          </div>
          <div style={{ fontSize: 10, color: '#d1d5db' }}>{elapsed}s elapsed</div>
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
          {drilldowns.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 16, paddingTop: 12, borderTop: '1px solid #f3f4f6' }}>
              <span style={{ fontSize: 10, color: '#9ca3af', alignSelf: 'center' }}>Drill deeper:</span>
              {drilldowns.map((dd, i) => (
                <button key={i} onClick={() => ask(dd.question)} style={{ padding: '5px 14px', borderRadius: 20, border: '1px solid #bfdbfe', background: activeQ === dd.question ? '#dbeafe' : '#f0f9ff', color: '#0066cc', fontSize: 11, cursor: 'pointer', fontWeight: 500, transition: 'all 0.15s' }}>{dd.label}</button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
