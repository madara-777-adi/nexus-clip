import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';

export const LiveSyncBadge: React.FC = () => {
  const { status } = useWebSocket();

  if (status === 'connecting') {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full clay-raised text-xs font-semibold uppercase tracking-wider text-muted">
        <div className="w-2 h-2 rounded-full bg-muted"></div>
        Connecting...
      </div>
    );
  }

  if (status === 'disconnected') {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full clay-raised text-xs font-semibold uppercase tracking-wider text-coral">
        <div className="w-2 h-2 rounded-full bg-coral"></div>
        Reconnecting...
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full clay-raised text-xs font-semibold uppercase tracking-wider text-muted">
      <div className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-mint opacity-75 duration-[1800ms]"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-mint"></span>
      </div>
      Synced
    </div>
  );
};
