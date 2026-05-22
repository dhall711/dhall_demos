import { useState, useRef, useEffect } from 'react';
import { Send, Brain, CheckCircle, AlertTriangle, BookOpen, Ticket, ExternalLink, Link2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage, Metric, DrillDown } from '../types';
import { findTermsInText } from '../services/snowflakeAgent';

interface Props {
  messages: ChatMessage[];
  isLoading: boolean;
  selectedMetric: Metric | null;
  onSendMessage: (question: string) => void;
  onDrillDown: (drillDown: DrillDown) => void;
  onCreateTicket: (message: ChatMessage) => void;
}

export default function ChatInterface({ messages, isLoading, selectedMetric, onSendMessage, onDrillDown, onCreateTicket }: Props) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const getConfidenceStyle = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getDrillDownStyle = (type: string) => {
    switch (type) {
      case 'impact': return 'bg-comcast-blue text-white';
      case 'timeline': return 'bg-gray-600 text-white';
      case 'root_cause': return 'bg-green-600 text-white';
      case 'comparison': return 'bg-purple-600 text-white';
      case 'action_plan': return 'bg-orange-600 text-white';
      default: return 'bg-gray-200 text-gray-700';
    }
  };

  const getDrillDownIcon = (type: string) => {
    switch (type) {
      case 'impact': return <Link2 className="w-3 h-3" />;
      case 'root_cause': return <span className="text-xs">⚡</span>;
      case 'comparison': return <span className="text-xs">📊</span>;
      default: return <ExternalLink className="w-3 h-3" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-4 py-3 bg-comcast-darkblue flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-300" />
          <div>
            <h3 className="font-semibold text-sm text-white">Deep Reasoning Agent</h3>
            {selectedMetric && (
              <p className="text-xs text-gray-300">Analyzing: {selectedMetric.metricName} - {selectedMetric.region}</p>
            )}
          </div>
        </div>
        {selectedMetric?.isAnomaly && (
          <span className="px-2 py-1 text-[10px] font-bold bg-red-500 text-white rounded-full">
            Anomaly Detected
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium">ISCO Deep Reasoning Agent</p>
            <p className="text-sm mt-1">Ask about supply chain metrics, anomalies, or trends</p>
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              {['Why is California CTD rising?', 'What is OTS?', 'Executive summary'].map(q => (
                <button key={q} onClick={() => onSendMessage(q)} className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition">
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <div key={msg.id}>
            {msg.role === 'user' ? (
              <div className="flex justify-end">
                <div className="max-w-[80%] bg-comcast-blue text-white rounded-lg rounded-br-sm px-4 py-2">
                  <p className="text-sm">{msg.content}</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="prose prose-sm max-w-none text-gray-800">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>

                {msg.confidence !== undefined && (
                  <div className="flex items-center gap-4 py-2 border-t border-gray-100">
                    <span className={`inline-flex items-center gap-1 text-xs font-medium ${getConfidenceStyle(msg.confidence)}`}>
                      <CheckCircle className="w-3.5 h-3.5" />
                      {msg.confidence >= 80 ? 'High' : msg.confidence >= 60 ? 'Medium' : 'Low'} Confidence ({msg.confidence}%)
                    </span>
                    {msg.drillDowns && msg.drillDowns.length > 0 && (
                      <span className="text-xs text-gray-500">{msg.drillDowns.length} action(s) suggested</span>
                    )}
                  </div>
                )}

                {msg.sources && msg.sources.toolsUsed.length > 0 && (
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <ExternalLink className="w-3 h-3" />
                    {msg.sources.narratives.length + msg.sources.events.length + msg.sources.knowledge.length + msg.sources.toolsUsed.length} source(s) referenced ▶
                  </div>
                )}

                {msg.drillDowns && msg.drillDowns.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Brain className="w-3 h-3" /> Continue investigating:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {msg.drillDowns.map((dd, i) => (
                        <button
                          key={i}
                          onClick={() => onDrillDown(dd)}
                          className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-full transition hover:opacity-90 ${getDrillDownStyle(dd.type)}`}
                        >
                          {getDrillDownIcon(dd.type)} {dd.label}
                        </button>
                      ))}
                    </div>
                    <button className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1 mt-1">
                      <span className="text-sm">🕐</span> Compare to last month
                    </button>
                    {msg.confidence !== undefined && msg.confidence < 80 && (
                      <button onClick={() => onCreateTicket(msg)} className="text-xs text-comcast-blue hover:underline flex items-center gap-1">
                        <Ticket className="w-3 h-3" /> Create Investigation Ticket
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm py-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-comcast-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-comcast-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-comcast-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            Deep reasoning in progress...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={selectedMetric ? `Ask about ${selectedMetric.metricName}...` : 'Ask about supply chain metrics...'}
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-comcast-blue focus:border-transparent"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()} className="px-4 py-2.5 bg-comcast-blue text-white rounded-lg hover:bg-comcast-darkblue disabled:opacity-50 disabled:cursor-not-allowed transition">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
