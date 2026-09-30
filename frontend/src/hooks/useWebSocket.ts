import { useCallback, useEffect, useRef, useState } from 'react';

export type ConnectionState = 'connected' | 'connecting' | 'disconnected';

export interface WebSocketMessage {
  type?: string;
  event?: string;
  data?: unknown;
  [key: string]: unknown;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const MAX_RECONNECT_DELAY = 30_000;
const HEARTBEAT_INTERVAL = 30_000;

const getWebSocketUrl = (boardId: string): string => {
  const baseUrl = API_BASE_URL.replace(/^http/, 'ws').replace(/\/$/, '');
  return `${baseUrl}/ws/boards/${encodeURIComponent(boardId)}`;
};

export function useWebSocket(boardId: string | null = null) {
  const [status, setStatus] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectAttemptRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const connectRef = useRef<() => void>(() => undefined);

  const clearTimers = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    clearTimers();
    socketRef.current?.close();
    socketRef.current = null;
    setStatus('disconnected');
  }, [clearTimers]);

  const connect = useCallback(() => {
    if (!boardId || typeof WebSocket === 'undefined') {
      setStatus('disconnected');
      return;
    }

    shouldReconnectRef.current = true;
    if (socketRef.current?.readyState === WebSocket.OPEN || socketRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    clearTimers();
    setStatus('connecting');
    const socket = new WebSocket(getWebSocketUrl(boardId));
    socketRef.current = socket;

    socket.onopen = () => {
      reconnectAttemptRef.current = 0;
      setStatus('connected');
      heartbeatTimerRef.current = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, HEARTBEAT_INTERVAL);
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        if (message.type !== 'pong') {
          setLastMessage(message);
        }
      } catch {
        // Ignore malformed socket messages so one bad event cannot break sync.
      }
    };

    socket.onclose = () => {
      clearTimers();
      if (socketRef.current === socket) {
        socketRef.current = null;
      }
      if (!shouldReconnectRef.current) {
        setStatus('disconnected');
        return;
      }

      setStatus('disconnected');
      const delay = Math.min(1000 * 2 ** reconnectAttemptRef.current, MAX_RECONNECT_DELAY);
      reconnectAttemptRef.current += 1;
      reconnectTimerRef.current = setTimeout(() => connectRef.current(), delay);
    };

    socket.onerror = () => {
      socket.close();
    };
  }, [boardId, clearTimers]);

  useEffect(() => {
    connectRef.current = connect;
    reconnectAttemptRef.current = 0;
    setLastMessage(null);
    connect();

    return () => {
      shouldReconnectRef.current = false;
      clearTimers();
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [connect, clearTimers]);

  return { status, lastMessage, connect, disconnect };
}
