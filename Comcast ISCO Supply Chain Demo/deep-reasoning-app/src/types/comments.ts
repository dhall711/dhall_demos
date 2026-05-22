export interface ExecutiveComment {
  id: string;
  panelType: string;
  region?: string;
  value?: number;
  text: string;
  author: string;
  timestamp: Date;
  assignedTo?: string;
  ticketId?: string;
  resolved: boolean;
  replies: CommentReply[];
}

export interface CommentReply {
  id: string;
  text: string;
  author: string;
  timestamp: Date;
}

export const TEAM_MEMBERS = [
  'VOGEL Tom',
  'Hallen Jodi',
  'Woods Eric',
  'Chen Sarah',
  'Martinez Ana',
] as const;

export type TeamMember = typeof TEAM_MEMBERS[number];
