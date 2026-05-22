import { useState, useEffect, useCallback } from 'react';
import { BarChart3, AlertTriangle, Ticket, Lightbulb, Settings, FileText, Brain, MessageSquare, TrendingUp, Calendar, RefreshCw } from 'lucide-react';
import xfinityLogo from './assets/Xfinity_logo.svg';
import { Metric, Ticket as TicketType, ChatMessage } from './types';
import { ExecutiveComment, CommentReply } from './types/comments';
import { getAnomalies, getTickets } from './services/snowflake';
import { useChat } from './hooks/useChat';
import ChatInterface from './components/ChatInterface';
import MetricCard from './components/MetricCard';
import TicketsPanel from './components/TicketsPanel';
import SettingsPanel from './components/SettingsPanel';
import DocumentManager from './components/DocumentManager';
import ExecutiveDashboard from './components/ExecutiveDashboard';
import CommentsSidebar from './components/CommentsSidebar';
import InsightsPanel from './components/InsightsPanel';
import PowerBIPanel from './components/PowerBIPanel';

type TabId = 'executive' | 'dashboard' | 'tickets' | 'insights' | 'powerbi';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('executive');
  const [anomalies, setAnomalies] = useState<Metric[]>([]);
  const [tickets, setTickets] = useState<TicketType[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<Metric | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('claude-4-sonnet');
  const [docsOpen, setDocsOpen] = useState(false);
  const [commentsSidebarOpen, setCommentsSidebarOpen] = useState(false);
  const [activeCommentPanel, setActiveCommentPanel] = useState('');
  const [activeCommentRow, setActiveCommentRow] = useState<{ region?: string; value?: number }>({});
  const [comments, setComments] = useState<ExecutiveComment[]>([
    {
      id: 'CMT-001',
      panelType: 'issuance_forecast',
      region: 'California',
      value: 92.3,
      text: 'Why is California forecast attainment trending down for 3 consecutive weeks?',
      author: 'VOGEL Tom',
      timestamp: new Date('2026-02-07'),
      assignedTo: 'Chen Sarah',
      resolved: false,
      replies: [
        { id: 'RPL-001', text: 'Looking into this - appears related to BCM3390 supply constraints.', author: 'Chen Sarah', timestamp: new Date('2026-02-07') }
      ]
    },
    {
      id: 'CMT-002',
      panelType: 'on_time_shipping',
      region: 'Texas',
      value: 88.5,
      text: 'Is the 75-mile radius expansion causing the OTS drop? Need to understand capacity impact.',
      author: 'Woods Eric',
      timestamp: new Date('2026-02-06'),
      resolved: false,
      replies: []
    },
    {
      id: 'CMT-003',
      panelType: 'fill_rates',
      text: 'Fill rates look strong across all regions this week. Can we document what changed?',
      author: 'Hallen Jodi',
      timestamp: new Date('2026-02-05'),
      resolved: true,
      ticketId: 'INV-2026-0004',
      replies: []
    },
  ]);

  const { messages, isLoading, sendMessage, handleDrillDown, clearMessages } = useChat();

  useEffect(() => {
    async function loadData() {
      const [a, t] = await Promise.all([getAnomalies(), getTickets()]);
      setAnomalies(a);
      setTickets(t);
    }
    loadData();
  }, []);

  const handleMetricSelect = useCallback((metric: Metric) => {
    setSelectedMetric(metric);
    setActiveTab('dashboard');
    sendMessage(`Why did ${metric.metricName} in ${metric.region} change?`, metric);
  }, [sendMessage]);

  const handleSendMessage = useCallback((question: string) => {
    sendMessage(question, selectedMetric);
  }, [sendMessage, selectedMetric]);

  const handleCreateTicket = useCallback((msg: ChatMessage) => {
    if (selectedMetric) {
      const newTicket: TicketType = {
        id: `INV-2026-${String(tickets.length + 1).padStart(4, '0')}`,
        metricId: selectedMetric.id,
        metricName: selectedMetric.metricName,
        region: selectedMetric.region,
        question: messages.find(m => m.role === 'user' && m.timestamp <= msg.timestamp)?.content || '',
        aiAnalysis: msg.content,
        confidenceScore: msg.confidence || 0,
        status: 'OPEN',
        assignedTo: 'Unassigned',
        createdDate: new Date().toISOString().split('T')[0],
      };
      setTickets(prev => [newTicket, ...prev]);
    }
  }, [selectedMetric, tickets, messages]);

  const handleOpenComments = useCallback((panelType: string, region?: string, value?: number) => {
    setActiveCommentPanel(panelType);
    setActiveCommentRow({ region, value });
    setCommentsSidebarOpen(true);
  }, []);

  const handleAddComment = useCallback((comment: Omit<ExecutiveComment, 'id' | 'replies' | 'resolved'>) => {
    const newComment: ExecutiveComment = {
      ...comment,
      id: `CMT-${Date.now()}`,
      replies: [],
      resolved: false,
    };
    setComments(prev => [newComment, ...prev]);
  }, []);

  const handleAddReply = useCallback((commentId: string, reply: Omit<CommentReply, 'id'>) => {
    setComments(prev => prev.map(c =>
      c.id === commentId ? { ...c, replies: [...c.replies, { ...reply, id: `RPL-${Date.now()}` }] } : c
    ));
  }, []);

  const handleAssignComment = useCallback((commentId: string, assignee: string) => {
    setComments(prev => prev.map(c =>
      c.id === commentId ? { ...c, assignedTo: assignee } : c
    ));
  }, []);

  const handleConvertToTicket = useCallback((commentId: string) => {
    const ticketId = `INV-2026-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`;
    setComments(prev => prev.map(c =>
      c.id === commentId ? { ...c, ticketId } : c
    ));
  }, []);

  const tabs = [
    { id: 'executive' as TabId, label: 'Executive View', icon: BarChart3, badge: 'New' },
    { id: 'dashboard' as TabId, label: 'Anomalies', icon: TrendingUp, count: anomalies.filter(a => a.anomalySeverity === 'CRITICAL').length },
    { id: 'tickets' as TabId, label: 'Tickets', icon: Ticket, count: tickets.filter(t => t.status === 'OPEN').length },
    { id: 'insights' as TabId, label: 'Insights', icon: Lightbulb },
    { id: 'powerbi' as TabId, label: 'Power BI', icon: Calendar, badge: 'Phase 2' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-comcast-darkblue sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Brain className="w-6 h-6 text-blue-300" />
            <div>
              <h1 className="text-lg font-bold text-white">ISCO Deep Reasoning Agent</h1>
              <p className="text-xs text-gray-400">Supply Chain Intelligence &bull; Powered by Snowflake Cortex AI</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-300 flex items-center gap-2">
              <Calendar className="w-4 h-4" /> Week of Feb 9, 2026
            </span>
            <button onClick={() => setCommentsSidebarOpen(!commentsSidebarOpen)} className="relative p-2 hover:bg-white/10 rounded-lg" title="Comments">
              <MessageSquare className="w-5 h-5 text-gray-300" />
              {comments.filter(c => !c.resolved).length > 0 && (
                <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[9px] font-bold px-1 py-0.5 rounded-full min-w-[16px] text-center">
                  {comments.filter(c => !c.resolved).length}
                </span>
              )}
            </button>
            <button onClick={() => setSettingsOpen(true)} className="p-2 hover:bg-white/10 rounded-lg" title="Settings">
              <RefreshCw className="w-5 h-5 text-gray-300" />
            </button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t transition ${
                  activeTab === tab.id
                    ? 'bg-white/20 text-white border-b-2 border-white'
                    : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {tab.badge && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-green-500 text-white rounded-full">{tab.badge}</span>
                )}
                {tab.count !== undefined && tab.count > 0 && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-red-500 text-white rounded-full">{tab.count}</span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'executive' && (
          <ExecutiveDashboard onOpenComments={handleOpenComments} />
        )}

        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-orange-500" />
                  Anomalies Requiring Investigation
                </h2>
                <span className="text-sm text-gray-500">{anomalies.filter(m => m.isAnomaly).length} detected</span>
              </div>
              {anomalies.filter(m => m.anomalySeverity === 'CRITICAL').length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2.5 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span className="text-sm text-red-700 font-medium">
                    {anomalies.filter(m => m.anomalySeverity === 'CRITICAL').length} CRITICAL anomaly requires immediate attention
                  </span>
                </div>
              )}
              <div className="space-y-3 max-h-[calc(100vh-250px)] overflow-y-auto pr-1">
                {anomalies
                  .filter(m => m.isAnomaly)
                  .sort((a, b) => {
                    const sev: Record<string, number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
                    return (sev[a.anomalySeverity || 'LOW'] || 3) - (sev[b.anomalySeverity || 'LOW'] || 3);
                  })
                  .map(metric => (
                    <MetricCard key={metric.id} metric={metric} onClick={handleMetricSelect} />
                  ))}
              </div>
            </div>
            <div className="lg:col-span-3 h-[calc(100vh-160px)] sticky top-[140px]">
              <ChatInterface
                messages={messages}
                isLoading={isLoading}
                selectedMetric={selectedMetric}
                onSendMessage={handleSendMessage}
                onDrillDown={dd => handleDrillDown(dd, selectedMetric)}
                onCreateTicket={handleCreateTicket}
              />
            </div>
          </div>
        )}

        {activeTab === 'tickets' && (
          <TicketsPanel tickets={tickets} onSelectTicket={() => {}} />
        )}

        {activeTab === 'insights' && <InsightsPanel />}

        {activeTab === 'powerbi' && <PowerBIPanel />}
      </main>

      <SettingsPanel isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} selectedModel={selectedModel} onModelChange={setSelectedModel} />
      <DocumentManager isOpen={docsOpen} onClose={() => setDocsOpen(false)} />
      <CommentsSidebar
        isOpen={commentsSidebarOpen}
        onClose={() => setCommentsSidebarOpen(false)}
        panelType={activeCommentPanel}
        region={activeCommentRow.region}
        value={activeCommentRow.value}
        comments={comments}
        onAddComment={handleAddComment}
        onAddReply={handleAddReply}
        onAssignComment={handleAssignComment}
        onConvertToTicket={handleConvertToTicket}
      />
    </div>
  );
}
