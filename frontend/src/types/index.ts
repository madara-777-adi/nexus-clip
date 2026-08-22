export type ClipType = 'text' | 'code' | 'markdown' | 'image' | 'file' | 'url';

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  created_at: string;
}

export interface Board {
  id: string;
  name: string;
  is_default: boolean;
  clip_count: number;
  created_at: string;
  updated_at: string;
}

export interface Clip {
  id: string;
  board_id?: string | null;
  type: ClipType;
  title: string;
  content?: string | null;
  file_url?: string | null;
  file_name?: string | null;
  file_size?: number | null;
  tags: string[];
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface GuestSession {
  guest_session_id: string;
  board_code?: string | null;
  expires_at: string;
  clips: Clip[];
}

export interface UserSettings {
  auto_cleanup_days: '7' | '30' | '90' | 'never';
  theme: 'dark' | 'light';
  default_board_id?: string | null;
}

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors?: any[];
}
