'use client';
import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

type Message = { role: 'user' | 'assistant'; content: string; timestamp: Date };

type DrilldownState = {
  response: string;
  question: string;
  selectedKey: string | null;
};

type ChatContextType = {
  chatMessages: Message[];
  setChatMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  getDrilldown: (pageId: string) => DrilldownState;
  setDrilldown: (pageId: string, state: Partial<DrilldownState>) => void;
  clearDrilldown: (pageId: string) => void;
  getPageSelection: (pageId: string) => any;
  setPageSelection: (pageId: string, selection: any) => void;
};

const defaultDrilldown: DrilldownState = { response: '', question: '', selectedKey: null };

const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [drilldowns, setDrilldowns] = useState<Record<string, DrilldownState>>({});
  const [pageSelections, setPageSelections] = useState<Record<string, any>>({});

  const getDrilldown = useCallback((pageId: string): DrilldownState => {
    return drilldowns[pageId] || defaultDrilldown;
  }, [drilldowns]);

  const setDrilldown = useCallback((pageId: string, state: Partial<DrilldownState>) => {
    setDrilldowns(prev => ({
      ...prev,
      [pageId]: { ...(prev[pageId] || defaultDrilldown), ...state }
    }));
  }, []);

  const clearDrilldown = useCallback((pageId: string) => {
    setDrilldowns(prev => {
      const next = { ...prev };
      delete next[pageId];
      return next;
    });
  }, []);

  const getPageSelection = useCallback((pageId: string) => {
    return pageSelections[pageId] ?? null;
  }, [pageSelections]);

  const setPageSelection = useCallback((pageId: string, selection: any) => {
    setPageSelections(prev => ({ ...prev, [pageId]: selection }));
  }, []);

  return (
    <ChatContext.Provider value={{ chatMessages, setChatMessages, getDrilldown, setDrilldown, clearDrilldown, getPageSelection, setPageSelection }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChatContext must be used within ChatProvider');
  return ctx;
}
