'use client';
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatContext } from '@/context/ChatContext';

type Message = { role: 'user' | 'assistant'; content: string; timestamp: Date };

const SAMPLES = [
  'How many certificates are expiring in the next 30 days?',
  'Which partners have the most non-compliant certificates?',
  'What is our policy for self-signed certificates?',
  'What is the compliance rate by region?',
  'How do I remediate a self-signed certificate?',
  'Show certificates by device type and data center'
];

export default function ChatPage() {
  const { chatMessages: messages, setChatMessages: setMessages } = useChatContext();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  async function send(text: string) {
    if (!text.trim() || loading) return;
    const userMsg: Message = { role: 'user', content: text, timestamp: new Date() };
    setMessages(p => [...p, userMsg]);
    setInput('');
    setLoading(true);
    setStreaming(true);

    const assistantMsg: Message = { role: 'assistant', content: '', timestamp: new Date() };
    setMessages(p => [...p, assistantMsg]);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })), stream: true })
      });

      if (res.headers.get('content-type')?.includes('text/event-stream') && res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buf = '';
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
              if (data.delta) {
                fullText += data.delta;
                setMessages(p => {
                  const updated = [...p];
                  updated[updated.length - 1] = { ...updated[updated.length - 1], content: fullText };
                  return updated;
                });
              }
            } catch {}
          }
        }
      } else {
        const data = await res.json();
        setMessages(p => {
          const updated = [...p];
          updated[updated.length - 1] = { ...updated[updated.length - 1], content: data.text || data.error || 'No response' };
          return updated;
        });
      }
    } catch (e: any) {
      setMessages(p => {
        const updated = [...p];
        updated[updated.length - 1] = { ...updated[updated.length - 1], content: `Error: ${e.message}` };
        return updated;
      });
    } finally {
      setLoading(false);
      setStreaming(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', padding: 24 }}>
      <h1 style={{ fontSize: 18, fontWeight: 700, marginBottom: 4, color: '#111827' }}>Compliance Agent Chat</h1>
      <p style={{ color: '#6b7280', fontSize: 12, marginBottom: 16 }}>Natural language Q&A • Streaming responses • 5 AI tools</p>

      {messages.length === 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          {SAMPLES.map(s => <button key={s} onClick={() => send(s)} style={{ padding: '8px 14px', borderRadius: 20, border: '1px solid #e2e8f0', background: '#fff', color: '#374151', fontSize: 12, cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}>{s}</button>)}
        </div>
      )}

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ maxWidth: '85%', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', background: m.role === 'user' ? '#0066cc' : '#fff', border: m.role === 'user' ? 'none' : '1px solid #e2e8f0', borderRadius: 12, padding: '12px 16px', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', color: m.role === 'user' ? '#fff' : '#1a1a2e' }}>
            <div style={{ fontSize: 10, color: m.role === 'user' ? '#cce5ff' : '#9ca3af', marginBottom: 4 }}>{m.role === 'user' ? 'You' : 'Cortex Agent'} - {m.timestamp.toLocaleTimeString()}</div>
            <div style={{ fontSize: 13, lineHeight: 1.7 }}>
              {m.role === 'assistant' && m.content ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                  table: ({children}) => <div style={{overflowX:'auto',marginTop:8}}><table style={{width:'100%',fontSize:12,borderCollapse:'collapse',border:'1px solid #e2e8f0'}}>{children}</table></div>,
                  th: ({children}) => <th style={{textAlign:'left',padding:'8px 10px',borderBottom:'2px solid #e2e8f0',color:'#374151',background:'#f9fafb',fontWeight:600}}>{children}</th>,
                  td: ({children}) => <td style={{padding:'6px 10px',borderBottom:'1px solid #f3f4f6'}}>{children}</td>
                }}>{m.content}</ReactMarkdown>
              ) : m.content || (streaming && i === messages.length - 1 ? <span style={{ color: '#6b7280' }}>Thinking...</span> : null)}
            </div>
          </div>
        ))}
        {loading && messages[messages.length - 1]?.content === '' && (
          <div style={{ color: '#6b7280', fontSize: 13, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 4, background: '#0066cc', animation: 'pulse 1s infinite' }} />
            Agent is analyzing...
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={e => { e.preventDefault(); send(input); }} style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask about certificate compliance..." disabled={loading} style={{ flex: 1, padding: '12px 16px', borderRadius: 8, border: '1px solid #d1d5db', background: '#fff', color: '#1a1a2e', fontSize: 14 }} />
        <button type="submit" disabled={loading || !input.trim()} style={{ padding: '12px 20px', borderRadius: 8, border: 'none', background: loading || !input.trim() ? '#d1d5db' : '#0066cc', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Send</button>
      </form>
    </div>
  );
}
