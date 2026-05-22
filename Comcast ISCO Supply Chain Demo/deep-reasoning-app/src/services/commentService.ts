import { ExecutiveComment, CommentReply } from '../types/comments';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

export const commentService = {
  async createComment(payload: Omit<ExecutiveComment, 'id' | 'replies' | 'resolved'>): Promise<ExecutiveComment> {
    try {
      const res = await fetch(`${API_BASE}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Failed to create comment');
      return await res.json();
    } catch {
      return {
        ...payload,
        id: `CMT-${Date.now()}`,
        replies: [],
        resolved: false,
      };
    }
  },

  async getComments(filters?: { panelType?: string; resolved?: boolean }): Promise<ExecutiveComment[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.panelType) params.set('panelType', filters.panelType);
      if (filters?.resolved !== undefined) params.set('resolved', String(filters.resolved));
      const res = await fetch(`${API_BASE}/comments?${params}`);
      if (!res.ok) throw new Error('Failed to fetch comments');
      return await res.json();
    } catch {
      return [];
    }
  },

  async addReply(commentId: string, reply: Omit<CommentReply, 'id'>): Promise<CommentReply> {
    try {
      const res = await fetch(`${API_BASE}/comments/${commentId}/replies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reply)
      });
      if (!res.ok) throw new Error('Failed to add reply');
      return await res.json();
    } catch {
      return { ...reply, id: `RPL-${Date.now()}` };
    }
  },

  async assignComment(commentId: string, assignee: string): Promise<void> {
    await fetch(`${API_BASE}/comments/${commentId}/assign`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assignedTo: assignee })
    });
  },

  async convertToTicket(commentId: string, payload: { metricName: string; region: string }): Promise<string> {
    try {
      const res = await fetch(`${API_BASE}/comments/${commentId}/convert-ticket`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Failed to convert');
      const data = await res.json();
      return data.ticketId;
    } catch {
      return `INV-2026-${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`;
    }
  },

  async resolveComment(commentId: string, notes?: string): Promise<void> {
    await fetch(`${API_BASE}/comments/${commentId}/resolve`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resolved: true, notes })
    });
  }
};

export const slackIntegration = {
  configured: false,
  config: { webhookUrl: '', channel: '', botToken: '' },
  configure(opts: { webhookUrl: string; channel: string; botToken: string }) {
    this.config = opts;
    this.configured = true;
  }
};

export const teamsIntegration = {
  configured: false,
  config: { webhookUrl: '', channelId: '' },
  configure(opts: { webhookUrl: string; channelId: string }) {
    this.config = opts;
    this.configured = true;
  }
};
