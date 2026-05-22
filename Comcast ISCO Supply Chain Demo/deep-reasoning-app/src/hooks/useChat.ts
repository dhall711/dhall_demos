import { useState, useCallback } from 'react';
import { ChatMessage, Metric, DrillDown } from '../types';
import { askAgent } from '../services/snowflakeAgent';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (question: string, metric: Metric | null) => {
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}_user`,
      role: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await askAgent(metric, question);
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources,
        drillDowns: response.drillDowns,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now()}_error`,
        role: 'assistant',
        content: 'I encountered an error while processing your question. Please try again.',
        timestamp: new Date(),
        confidence: 0,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDrillDown = useCallback((drillDown: DrillDown, metric: Metric | null) => {
    sendMessage(drillDown.question, metric);
  }, [sendMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, isLoading, sendMessage, handleDrillDown, clearMessages };
}
