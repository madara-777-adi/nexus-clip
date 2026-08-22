import React, { useState } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Topbar } from '../components/layout/Topbar';
import { Dropzone } from '../components/clips/Dropzone';
import { ClipGrid } from '../components/clips/ClipGrid';
import { useBoard } from '../contexts/BoardContext';
import { Settings } from 'lucide-react';
import { AuthModal } from '../components/AuthModal';
import { BoardModal } from '../components/BoardModal';
import { SettingsDrawer } from '../components/SettingsDrawer';


const formatRelativeTime = (isoString?: string) => {
  if (!isoString) return 'never';
  const date = new Date(isoString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

export const BoardPage: React.FC = () => {
  const { boards, activeBoardId, clips, isGuestMode } = useBoard();
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isBoardModalOpen, setIsBoardModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const activeBoard = boards.find(b => b.id === activeBoardId);
  const pinnedCount = clips.filter(c => c.is_pinned).length;

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Fixed Sidebar */}
      <Sidebar 
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenBoardModal={() => setIsBoardModalOpen(true)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative h-screen overflow-hidden">
        <Topbar onOpenAuth={() => setIsAuthOpen(true)} />
        
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 md:p-10 scrollbar-thin">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            
            {/* Board Header */}
            <div className="flex items-start justify-between mb-8">
              <div>
                <h1 className="font-display text-[27px] font-bold text-ink leading-tight">
                  {isGuestMode ? "Guest Board" : (activeBoard?.name || "Loading...")}
                </h1>
                <p className="text-[11px] font-mono text-muted uppercase tracking-widest mt-1">
                  {clips.length} clips · {pinnedCount} pinned · last updated {formatRelativeTime(activeBoard?.updated_at || clips[0]?.created_at)}
                </p>
              </div>
              
              {!isGuestMode && (
                <button
                  onClick={() => setIsSettingsOpen(true)}
                  className="w-10 h-10 rounded-xl clay-raised flex items-center justify-center text-muted hover:text-ink transition-colors"
                >
                  <Settings size={18} />
                </button>
              )}
            </div>

            {/* Main Board Content */}
            <div className="flex-1 flex flex-col">
              <Dropzone />
              <ClipGrid />
            </div>

          </div>
        </main>
      </div>

      {/* Modals & Drawers */}
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
      <BoardModal isOpen={isBoardModalOpen} onClose={() => setIsBoardModalOpen(false)} />
      <SettingsDrawer isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      
      {/* Global Toast */}
      {/* Toast component handles its own state globally or gets it from context (handled inside Toast already ideally, let's just pass from context if needed, but Toast component has it) */}
    </div>
  );
};
