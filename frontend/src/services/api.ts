import type { APIResponse, Board, Clip, ClipType, GuestSession, User, UserSettings } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private getHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = {
      ...extraHeaders,
    };

    const token = localStorage.getItem('nexus_auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const guestSessionId = localStorage.getItem('nexus_guest_session_id');
    if (guestSessionId) {
      headers['x-guest-session-id'] = guestSessionId;
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const isFormData = options.body instanceof FormData;
    const defaultHeaders = isFormData
      ? this.getHeaders()
      : this.getHeaders({ 'Content-Type': 'application/json' });

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    const data: APIResponse<T> = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.message || 'API request failed');
    }

    return data;
  }

  // Auth
  async register(name: string, email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
    localStorage.setItem('nexus_auth_token', res.data.access_token);
    return res.data;
  }

  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem('nexus_auth_token', res.data.access_token);
    return res.data;
  }

  async getMe(): Promise<User> {
    const res = await this.request<User>('/auth/me');
    return res.data;
  }

  logout(): void {
    localStorage.removeItem('nexus_auth_token');
  }

  // Guest
  async getGuestBoard(): Promise<GuestSession> {
    const res = await this.request<GuestSession>('/guest/board', {
      method: 'POST',
    });
    if (res.data.guest_session_id) {
      localStorage.setItem('nexus_guest_session_id', res.data.guest_session_id);
    }
    return res.data;
  }

  async createGuestClip(payload: {
    type: ClipType;
    title: string;
    content?: string;
    file_url?: string;
    file_name?: string;
    file_size?: number;
    tags?: string[];
  }): Promise<Clip> {
    const res = await this.request<Clip>('/guest/board/clips', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return res.data;
  }

  async continueGuestBoard(boardCode: string): Promise<GuestSession> {
    const res = await this.request<GuestSession>('/guest/continue', {
      method: 'POST',
      body: JSON.stringify({ boardCode }),
    });
    if (res.data.guest_session_id) {
      localStorage.setItem('nexus_guest_session_id', res.data.guest_session_id);
    }
    return res.data;
  }

  async promoteGuestBoard(): Promise<{ board_id: string; board_name: string; moved_clips_count: number }> {
    const res = await this.request<{ board_id: string; board_name: string; moved_clips_count: number }>('/guest/promote', {
      method: 'POST',
    });
    localStorage.removeItem('nexus_guest_session_id');
    return res.data;
  }

  // Boards
  async getBoards(): Promise<Board[]> {
    const res = await this.request<Board[]>('/boards');
    return res.data;
  }

  async createBoard(name: string): Promise<Board> {
    const res = await this.request<Board>('/boards', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
    return res.data;
  }

  async updateBoard(boardId: string, name: string): Promise<Board> {
    const res = await this.request<Board>(`/boards/${boardId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    });
    return res.data;
  }

  async deleteBoard(boardId: string): Promise<void> {
    await this.request<null>(`/boards/${boardId}`, {
      method: 'DELETE',
    });
  }

  // Clips
  async getBoardClips(boardId: string): Promise<{ items: Clip[]; total: number }> {
    const res = await this.request<{ items: Clip[]; total: number }>(`/boards/${boardId}/clips`);
    return res.data;
  }

  async createClip(
    boardId: string,
    payload: {
      type: ClipType;
      title: string;
      content?: string;
      file_url?: string;
      file_name?: string;
      file_size?: number;
      tags?: string[];
      is_pinned?: boolean;
    }
  ): Promise<Clip> {
    const res = await this.request<Clip>(`/boards/${boardId}/clips`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return res.data;
  }

  async updateClip(
    clipId: string,
    payload: { title?: string; content?: string; tags?: string[]; is_pinned?: boolean }
  ): Promise<Clip> {
    const res = await this.request<Clip>(`/clips/${clipId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    return res.data;
  }

  async togglePin(clipId: string): Promise<Clip> {
    const res = await this.request<Clip>(`/clips/${clipId}/pin`, {
      method: 'PATCH',
    });
    return res.data;
  }

  async deleteClip(clipId: string): Promise<void> {
    await this.request<null>(`/clips/${clipId}`, {
      method: 'DELETE',
    });
  }

  // File Upload
  async uploadFile(file: File): Promise<{ file_id: string; file_url: string; file_name: string; file_size: number }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await this.request<{ file_id: string; file_url: string; file_name: string; file_size: number }>('/upload', {
      method: 'POST',
      body: formData,
    });
    return res.data;
  }

  // Search
  async search(query: string, type?: ClipType, boardId?: string): Promise<Clip[]> {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (type) params.append('type', type);
    if (boardId) params.append('board', boardId);
    const res = await this.request<{ items: Clip[]; total: number }>(`/search?${params.toString()}`);
    return res.data.items;
  }

  // Settings
  async getSettings(): Promise<UserSettings> {
    const res = await this.request<UserSettings>('/settings');
    return res.data;
  }

  async updateSettings(payload: Partial<UserSettings>): Promise<UserSettings> {
    const res = await this.request<UserSettings>('/settings', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    return res.data;
  }
}

export const api = new ApiClient();
