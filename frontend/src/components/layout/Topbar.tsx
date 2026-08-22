import React from 'react';
import { SearchInput } from '../ui/SearchInput';
import { LiveSyncBadge } from '../ui/LiveSyncBadge';
import { useAuth } from '../../contexts/AuthContext';
import { User, LogOut } from 'lucide-react';

export const Topbar: React.FC<{ onOpenAuth: () => void }> = ({ onOpenAuth }) => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="h-16 px-6 flex items-center justify-between z-10 w-full relative">
      <div className="flex-1 max-w-md">
        <SearchInput />
      </div>
      <div className="flex items-center gap-4">
        <LiveSyncBadge />
        
        {isAuthenticated ? (
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium">{user?.full_name}</span>
            <button
              onClick={logout}
              className="p-2 rounded-xl clay-raised text-muted hover:text-ink transition-colors"
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="flex items-center gap-2 px-4 py-2 rounded-xl clay-raised text-sm font-medium hover:text-mint transition-colors"
          >
            <User size={16} />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
};
