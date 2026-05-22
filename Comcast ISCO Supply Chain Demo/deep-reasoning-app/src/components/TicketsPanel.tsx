import { CheckCircle, Clock, ChevronRight, User, AlertCircle, Brain } from 'lucide-react';
import { Ticket } from '../types';

interface Props {
  tickets: Ticket[];
  onSelectTicket: (ticket: Ticket) => void;
}

const KNOWLEDGE_STEPS = [
  { num: 1, color: 'bg-comcast-blue', title: 'AI Analysis', desc: 'Agent searches historical narratives, external events, and knowledge base to provide initial reasoning.' },
  { num: 2, color: 'bg-yellow-500', title: 'Human Verification', desc: "Domain experts validate, correct, or enhance the AI's analysis with institutional knowledge." },
  { num: 3, color: 'bg-green-500', title: 'Knowledge Capture', desc: 'Verified insights are stored in the knowledge base, making the agent smarter over time.' },
  { num: 4, color: 'bg-purple-500', title: 'Institutionalized Learning', desc: 'Future similar patterns are recognized automatically, reducing investigation time.' },
];

export default function TicketsPanel({ tickets, onSelectTicket }: Props) {
  const statusConfig: Record<string, { border: string; badge: string; badgeBg: string; icon: JSX.Element }> = {
    OPEN: { border: 'border-l-red-500', badge: 'OPEN', badgeBg: 'bg-red-100 text-red-700', icon: <AlertCircle className="w-3.5 h-3.5" /> },
    IN_PROGRESS: { border: 'border-l-yellow-500', badge: 'IN PROGRESS', badgeBg: 'bg-yellow-100 text-yellow-700', icon: <Clock className="w-3.5 h-3.5" /> },
    RESOLVED: { border: 'border-l-green-500', badge: 'RESOLVED', badgeBg: 'bg-green-100 text-green-700', icon: <CheckCircle className="w-3.5 h-3.5" /> },
    CLOSED: { border: 'border-l-gray-400', badge: 'CLOSED', badgeBg: 'bg-gray-100 text-gray-600', icon: <CheckCircle className="w-3.5 h-3.5" /> },
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Brain className="w-5 h-5 text-comcast-blue" />
              Investigation Tickets
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">Track questions, capture knowledge, close the loop</p>
          </div>
          <div className="divide-y divide-gray-100">
            {tickets.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <AlertCircle className="w-10 h-10 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No tickets yet</p>
              </div>
            ) : (
              tickets.map(ticket => {
                const cfg = statusConfig[ticket.status] || statusConfig.OPEN;
                return (
                  <div
                    key={ticket.id}
                    onClick={() => onSelectTicket(ticket)}
                    className={`px-5 py-4 border-l-4 ${cfg.border} cursor-pointer hover:bg-gray-50 transition`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold rounded-full ${cfg.badgeBg}`}>
                        {cfg.icon} {cfg.badge}
                      </span>
                      <span className="text-xs text-gray-400">{formatDate(ticket.createdDate)}</span>
                    </div>
                    <p className="text-sm text-gray-900 font-medium leading-snug">{ticket.question}</p>
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <User className="w-3 h-3" /> {ticket.assignedTo?.split(' ')[0] || 'Unassigned'}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {ticket.confidenceScore}%
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {ticket.status === 'RESOLVED' && (
                          <span className="text-[10px] text-green-600 font-medium flex items-center gap-0.5">
                            <CheckCircle className="w-3 h-3" /> Knowledge saved
                          </span>
                        )}
                        <ChevronRight className="w-4 h-4 text-gray-300" />
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      <div className="lg:col-span-3">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-6">Knowledge Capture Workflow</h3>
          <div className="space-y-6">
            {KNOWLEDGE_STEPS.map(step => (
              <div key={step.num} className="flex items-start gap-4">
                <div className={`w-9 h-9 rounded-full ${step.color} text-white flex items-center justify-center font-bold text-sm flex-shrink-0`}>
                  {step.num}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 text-sm">{step.title}</h4>
                  <p className="text-sm text-gray-600 mt-0.5">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return dateStr;
  }
}
