import { useState } from 'react';
import { X, Send, Bold, Italic, List, AtSign, UserPlus, Ticket, Check } from 'lucide-react';
import { ExecutiveComment, CommentReply, TEAM_MEMBERS } from '../types/comments';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  panelType: string;
  region?: string;
  value?: number;
  comments: ExecutiveComment[];
  onAddComment: (comment: Omit<ExecutiveComment, 'id' | 'replies' | 'resolved'>) => void;
  onAddReply: (commentId: string, reply: Omit<CommentReply, 'id'>) => void;
  onAssignComment: (commentId: string, assignee: string) => void;
  onConvertToTicket: (commentId: string) => void;
}

export default function CommentsSidebar({
  isOpen, onClose, panelType, region, value,
  comments, onAddComment, onAddReply, onAssignComment, onConvertToTicket
}: Props) {
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyText, setReplyText] = useState('');
  const [showAssignDropdown, setShowAssignDropdown] = useState<string | null>(null);
  const [filterPanel, setFilterPanel] = useState<string | null>(null);

  if (!isOpen) return null;

  const filteredComments = comments.filter(c => {
    if (filterPanel && c.panelType !== filterPanel) return false;
    return true;
  });

  const handleSubmitComment = () => {
    if (!newComment.trim()) return;
    onAddComment({
      panelType,
      region,
      value,
      text: newComment.trim(),
      author: 'You',
      timestamp: new Date(),
      assignedTo: undefined,
      ticketId: undefined,
    });
    setNewComment('');
  };

  const handleSubmitReply = (commentId: string) => {
    if (!replyText.trim()) return;
    onAddReply(commentId, {
      text: replyText.trim(),
      author: 'You',
      timestamp: new Date(),
    });
    setReplyText('');
    setReplyingTo(null);
  };

  const panelTitle = panelType.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  return (
    <div className="fixed top-0 right-0 h-full w-[380px] bg-white shadow-2xl border-l border-gray-200 z-40 flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="font-semibold text-sm">Questions & Comments</h3>
          <p className="text-xs text-gray-500">
            {region ? `${panelTitle} - ${region} - ${value}` : panelTitle}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
            {comments.length}
          </span>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex gap-1 px-4 py-2 border-b overflow-x-auto">
        <button onClick={() => setFilterPanel(null)} className={`px-2 py-1 text-[10px] rounded whitespace-nowrap ${!filterPanel ? 'bg-comcast-blue text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
          All
        </button>
        {['issuance_forecast', 'fill_rates', 'on_time_shipping'].map(pt => (
          <button key={pt} onClick={() => setFilterPanel(pt)} className={`px-2 py-1 text-[10px] rounded whitespace-nowrap ${filterPanel === pt ? 'bg-comcast-blue text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {pt.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {filteredComments.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">No comments yet. Ask a question below.</div>
        ) : (
          filteredComments.map(comment => (
            <div key={comment.id} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-comcast-blue text-white flex items-center justify-center text-[10px] font-bold">
                    {comment.author.charAt(0)}
                  </div>
                  <div>
                    <span className="text-xs font-medium">{comment.author}</span>
                    <span className="text-[10px] text-gray-400 ml-2">
                      {new Date(comment.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {comment.ticketId && (
                    <span className="px-1.5 py-0.5 text-[9px] font-bold bg-green-100 text-green-700 rounded">
                      {comment.ticketId}
                    </span>
                  )}
                  {comment.assignedTo && (
                    <span className="px-1.5 py-0.5 text-[9px] bg-blue-50 text-blue-700 rounded">
                      @{comment.assignedTo.split(' ')[0]}
                    </span>
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-700 mt-2">{comment.text}</p>
              {comment.region && (
                <p className="text-[10px] text-gray-400 mt-1 italic">
                  Re: {comment.panelType.replace(/_/g, ' ')} - {comment.region}
                </p>
              )}

              {comment.replies.length > 0 && (
                <div className="mt-2 ml-4 space-y-2 border-l-2 border-gray-200 pl-2">
                  {comment.replies.map(reply => (
                    <div key={reply.id} className="text-xs">
                      <span className="font-medium">{reply.author}</span>
                      <span className="text-gray-400 ml-1">{new Date(reply.timestamp).toLocaleDateString()}</span>
                      <p className="text-gray-600 mt-0.5">{reply.text}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-2 flex items-center gap-2 pt-2 border-t border-gray-200">
                <button onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)} className="text-[10px] text-blue-600 hover:text-blue-800">
                  Reply
                </button>
                <div className="relative">
                  <button onClick={() => setShowAssignDropdown(showAssignDropdown === comment.id ? null : comment.id)} className="text-[10px] text-gray-500 hover:text-gray-700 flex items-center gap-0.5">
                    <UserPlus className="w-3 h-3" /> Assign
                  </button>
                  {showAssignDropdown === comment.id && (
                    <div className="absolute left-0 bottom-full mb-1 bg-white border rounded-lg shadow-lg z-10 min-w-[140px]">
                      {TEAM_MEMBERS.map(member => (
                        <button key={member} onClick={() => { onAssignComment(comment.id, member); setShowAssignDropdown(null); }} className="w-full px-3 py-1.5 text-left text-[10px] hover:bg-gray-50">
                          {member}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {!comment.ticketId && (
                  <button onClick={() => onConvertToTicket(comment.id)} className="text-[10px] text-orange-600 hover:text-orange-800 flex items-center gap-0.5">
                    <Ticket className="w-3 h-3" /> Create Ticket
                  </button>
                )}
                {!comment.resolved && (
                  <button className="text-[10px] text-green-600 hover:text-green-800 flex items-center gap-0.5 ml-auto">
                    <Check className="w-3 h-3" /> Resolve
                  </button>
                )}
              </div>

              {replyingTo === comment.id && (
                <div className="mt-2 flex gap-1">
                  <input
                    type="text"
                    value={replyText}
                    onChange={e => setReplyText(e.target.value)}
                    placeholder="@mention or reply..."
                    className="flex-1 px-2 py-1 text-xs border rounded focus:ring-1 focus:ring-comcast-blue"
                    onKeyDown={e => e.key === 'Enter' && handleSubmitReply(comment.id)}
                  />
                  <button onClick={() => handleSubmitReply(comment.id)} className="px-2 py-1 bg-comcast-blue text-white rounded text-xs">
                    <Send className="w-3 h-3" />
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t bg-gray-50">
        <div className="flex gap-1 mb-2">
          <button className="p-1 hover:bg-gray-200 rounded"><Bold className="w-3 h-3 text-gray-500" /></button>
          <button className="p-1 hover:bg-gray-200 rounded"><Italic className="w-3 h-3 text-gray-500" /></button>
          <button className="p-1 hover:bg-gray-200 rounded"><List className="w-3 h-3 text-gray-500" /></button>
          <button className="p-1 hover:bg-gray-200 rounded"><AtSign className="w-3 h-3 text-gray-500" /></button>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={newComment}
            onChange={e => setNewComment(e.target.value)}
            placeholder="Ask a question or add a comment..."
            className="flex-1 px-3 py-2 text-sm border rounded-lg focus:ring-2 focus:ring-comcast-blue"
            onKeyDown={e => e.key === 'Enter' && handleSubmitComment()}
          />
          <button onClick={handleSubmitComment} disabled={!newComment.trim()} className="px-3 py-2 bg-comcast-blue text-white rounded-lg hover:bg-comcast-darkblue disabled:opacity-50 transition">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
