import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';

export const LiveSyncBadge: React.FC = () => {
  const { status } = useWebSocket();

  if (status === 'connecting') {
    return (
      <div
        className="flex items-center gap-2 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-ink bg-card"
        style={{ border: '3px solid var(--ink)' }}
      >
        <div className="w-2 h-2 bg-ink/40"></div>
        Connecting...
      </div>
    );
  }

  if (status === 'disconnected') {
    return (
      <div
        className="flex items-center gap-2 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-pink bg-card"
        style={{ border: '3px solid var(--ink)' }}
      >
        <div className="w-2 h-2 bg-pink"></div>
        Reconnecting...
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-2 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-ink bg-card"
      style={{ border: '3px solid var(--ink)' }}
    >
      <div className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full bg-cyan opacity-75 duration-[1800ms]"></span>
        <span className="relative inline-flex h-2 w-2 bg-cyan"></span>
      </div>
      Synced
    </div>
  );
};
