import React from 'react';
import { SearchInput } from '../ui/SearchInput';
import { LiveSyncBadge } from '../ui/LiveSyncBadge';
import { useAuth } from '../../contexts/AuthContext';
import { User, LogOut } from 'lucide-react';

export const Topbar: React.FC<{ onOpenAuth: () => void }> = ({ onOpenAuth }) => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="h-16 px-6 flex items-center justify-between z-10 w-full relative border-b-[5px] border-ink bg-paper">
      <div className="flex-1 max-w-md">
        <SearchInput />
      </div>
      <div className="flex items-center gap-4">
        <LiveSyncBadge />
        
        {isAuthenticated ? (
          <div className="flex items-center gap-3">
            <span className="text-sm font-bold font-body text-ink">{user?.full_name}</span>
            <button
              onClick={logout}
              className="p-2 border-3 border-ink bg-card text-ink hover:bg-pink hover:text-card transition-colors"
              style={{ border: '3px solid var(--ink)' }}
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="neo-btn text-xs py-2 px-4"
          >
            <User size={16} />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
};
