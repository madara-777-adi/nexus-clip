import { useState, useEffect } from 'react';

type ConnectionState = 'connected' | 'connecting' | 'disconnected';

export function useWebSocket() {
  const [status, setStatus] = useState<ConnectionState>('connecting');

  useEffect(() => {
    // Mock WebSocket connection state
    const timer = setTimeout(() => {
      setStatus('connected');
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  return { status };
}
