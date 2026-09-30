import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Board, Clip, ClipType, GuestSession } from '../types';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from './AuthContext';

interface BoardContextType {
  isGuestMode: boolean;
  guestSession: GuestSession | null;
  boards: Board[];
  activeBoardId: string | null;
  setActiveBoardId: (id: string) => void;
  clips: Clip[];
  loading: boolean;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  filterType: ClipType | 'all';
  setFilterType: (type: ClipType | 'all') => void;
  toastMessage: string | null;
  showToast: (msg: string) => void;
  fetchClips: () => Promise<void>;
  fetchBoards: () => Promise<void>;
  createBoard: (name: string) => Promise<Board>;
  updateBoard: (id: string, name: string) => Promise<Board>;
  deleteBoard: (id: string) => Promise<void>;
  createClip: (payload: {
    type: ClipType;
    title: string;
    content?: string;
    file_url?: string;
    file_name?: string;
    file_size?: number;
    tags?: string[];
  }) => Promise<Clip>;
  togglePin: (clipId: string) => Promise<void>;
  deleteClip: (clipId: string) => Promise<void>;
  continueGuestBoard: (boardCode: string) => Promise<void>;
  promoteGuestBoard: () => Promise<void>;
}

const BoardContext = createContext<BoardContextType | undefined>(undefined);

export const BoardProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const [isGuestMode, setIsGuestMode] = useState<boolean>(!isAuthenticated);
  const [guestSession, setGuestSession] = useState<GuestSession | null>(null);
  const [boards, setBoards] = useState<Board[]>([]);
  const [activeBoardId, setActiveBoardId] = useState<string | null>(null);
  const [clips, setClips] = useState<Clip[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filterType, setFilterType] = useState<ClipType | 'all'>('all');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const { lastMessage } = useWebSocket(isGuestMode ? null : activeBoardId);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const fetchGuestBoard = useCallback(async () => {
    setLoading(true);
    try {
      const session = await api.getGuestBoard();
      setGuestSession(session);
      setClips(session.clips || []);
    } catch (err: any) {
      showToast(err.message || 'Failed to load guest session');
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchBoards = useCallback(async () => {
    setLoading(true);
    try {
      const list = await api.getBoards();
      setBoards(list);
      if (list.length > 0 && !activeBoardId) {
        setActiveBoardId(list[0].id);
      }
    } catch (err: any) {
      showToast(err.message || 'Failed to load boards');
    } finally {
      setLoading(false);
    }
  }, [activeBoardId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchClips = useCallback(async () => {
    if (isGuestMode) {
      setLoading(true);
      try {
        if (searchQuery.trim() || filterType !== 'all') {
          const results = await api.searchGuest(
            searchQuery,
            filterType === 'all' ? undefined : filterType,
          );
          setClips(results);
        } else {
          await fetchGuestBoard();
        }
      } catch (err: any) {
        showToast(err.message || 'Failed to search guest clips');
      } finally {
        setLoading(false);
      }
      return;
    }
    if (!activeBoardId) return;
    setLoading(true);
    try {
      if (searchQuery.trim()) {
        const results = await api.search(
          searchQuery,
          filterType === 'all' ? undefined : filterType,
          activeBoardId
        );
        setClips(results);
      } else {
        const data = await api.getBoardClips(activeBoardId);
        let items = data.items;
        if (filterType !== 'all') {
          items = items.filter((c) => c.type === filterType);
        }
        setClips(items);
      }
    } catch (err: any) {
      showToast(err.message || 'Failed to load clips');
    } finally {
      setLoading(false);
    }
  }, [activeBoardId, isGuestMode, searchQuery, filterType, fetchGuestBoard]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    setIsGuestMode(!isAuthenticated);
    if (isAuthenticated) {
      fetchBoards();
    } else {
      fetchGuestBoard();
    }
  }, [isAuthenticated, user, fetchBoards, fetchGuestBoard]);

  useEffect(() => {
    fetchClips();
  }, [fetchClips]);

  useEffect(() => {
    if (!lastMessage) return;

    const eventType = lastMessage.type || lastMessage.event;
    if (!eventType) return;

    const payload = lastMessage.data;
    const eventData = payload && typeof payload === 'object'
      ? payload as Record<string, unknown>
      : lastMessage;
    const clipValue = eventData.clip ?? lastMessage.clip ?? eventData;
    const clip = clipValue as Partial<Clip>;
    const clipId = typeof eventData.clip_id === 'string'
      ? eventData.clip_id
      : typeof lastMessage.clip_id === 'string'
        ? lastMessage.clip_id
        : clip.id;

    if (eventType === 'CLIP_CREATED' && clip.id) {
      setClips((current) => current.some((item) => item.id === clip.id)
        ? current
        : [...current, clip as Clip]);
    }
    if (eventType === 'CLIP_UPDATED' && clip.id) {
      setClips((current) => current.map((item) => item.id === clip.id ? { ...item, ...clip } : item));
    }
    if (eventType === 'CLIP_DELETED' && clipId) {
      setClips((current) => current.filter((item) => item.id !== clipId));
    }
  }, [lastMessage]);

  const createBoard = async (name: string) => {
    const board = await api.createBoard(name);
    await fetchBoards();
    setActiveBoardId(board.id);
    showToast(`Board "${name}" created.`);
    return board;
  };

  const updateBoard = async (id: string, name: string) => {
    const updated = await api.updateBoard(id, name);
    await fetchBoards();
    showToast(`Board renamed to "${name}".`);
    return updated;
  };

  const deleteBoard = async (id: string) => {
    await api.deleteBoard(id);
    const updated = boards.filter((b) => b.id !== id);
    setBoards(updated);
    if (activeBoardId === id && updated.length > 0) {
      setActiveBoardId(updated[0].id);
    }
    showToast('Board deleted.');
  };

  const createClip = async (payload: {
    type: ClipType;
    title: string;
    content?: string;
    file_url?: string;
    file_name?: string;
    file_size?: number;
    tags?: string[];
  }) => {
    if (isGuestMode) {
      const clip = await api.createGuestClip(payload);
      await fetchGuestBoard();
      showToast('Clip saved to Guest Board.');
      return clip;
    } else {
      if (!activeBoardId) throw new Error('No active board selected.');
      const clip = await api.createClip(activeBoardId, payload);
      await fetchClips();
      await fetchBoards();
      showToast('Clip added.');
      return clip;
    }
  };

  const togglePin = async (clipId: string) => {
    if (isGuestMode) {
      await api.toggleGuestPin(clipId);
      await fetchGuestBoard();
      showToast('Pin state updated.');
    } else {
      await api.togglePin(clipId);
      await fetchClips();
      showToast('Pin state updated.');
    }
  };

  const deleteClip = async (clipId: string) => {
    if (isGuestMode) {
      await api.deleteGuestClip(clipId);
      await fetchGuestBoard();
      showToast('Clip removed.');
    } else {
      await api.deleteClip(clipId);
      await fetchClips();
      showToast('Clip deleted.');
    }
  };

  const continueGuestBoard = async (boardCode: string) => {
    const session = await api.continueGuestBoard(boardCode);
    setGuestSession(session);
    setClips(session.clips || []);
    showToast(`Guest Board ${boardCode} loaded!`);
  };

  const promoteGuestBoard = async () => {
    const res = await api.promoteGuestBoard();
    await fetchBoards();
    setActiveBoardId(res.board_id);
    showToast(`Imported ${res.moved_clips_count} clips to your account!`);
  };

  return (
    <BoardContext.Provider
      value={{
        isGuestMode,
        guestSession,
        boards,
        activeBoardId,
        setActiveBoardId,
        clips,
        loading,
        searchQuery,
        setSearchQuery,
        filterType,
        setFilterType,
        toastMessage,
        showToast,
        fetchClips,
        fetchBoards,
        createBoard,
        updateBoard,
        deleteBoard,
        createClip,
        togglePin,
        deleteClip,
        continueGuestBoard,
        promoteGuestBoard,
      }}
    >
      {children}
    </BoardContext.Provider>
  );
};

export const useBoard = () => {
  const ctx = useContext(BoardContext);
  if (!ctx) throw new Error('useBoard must be used within BoardProvider');
  return ctx;
};
