'use client';
import { ChatProvider } from '@/context/ChatContext';

export default function ClientProviders({ children }: { children: React.ReactNode }) {
  return <ChatProvider>{children}</ChatProvider>;
}
