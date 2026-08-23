import React from 'react';
import { useBoard } from '../../contexts/BoardContext';
import { BoardListItem } from '../boards/BoardListItem';
import { NewBoardButton } from '../boards/NewBoardButton';
import { GuestPanel } from '../boards/GuestPanel';

const DOT_COLORS = ['bg-cyan', 'bg-pink', 'bg-violet', 'bg-cyan', 'bg-pink'];

export const Sidebar: React.FC<{ 
  onOpenAuth: () => void;
  onOpenBoardModal: () => void;
}> = ({ onOpenAuth, onOpenBoardModal }) => {
  const { isGuestMode, boards, activeBoardId, setActiveBoardId, guestSession } = useBoard();

  return (
    <aside className="w-[264px] h-screen flex-col hidden lg:flex border-r-[5px] border-ink relative bg-paper">
      {/* Logo Area */}
      <div className="h-24 flex items-center px-6 gap-2">
        <div className="font-display text-[26px] tracking-tight" style={{ transform: 'rotate(-2deg)', display: 'inline-block' }}>
          <span className="bg-pink px-2.5 py-0.5 text-ink inline-block" style={{ border: '3px solid var(--ink)', boxShadow: '4px 4px 0 var(--ink)' }}>NEXUS</span>{' '}
          <span>CLIP</span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4">
        {isGuestMode ? (
          <GuestPanel 
            boardCode={guestSession?.board_code || null}
            onPromoteClick={onOpenAuth}
          />
        ) : (
          <div className="flex flex-col gap-1">
            <div className="text-[11px] font-bold uppercase tracking-widest text-ink px-4 mb-3">
              Your Boards
            </div>
            {boards.map((board, index) => (
              <BoardListItem
                key={board.id}
                id={board.id}
                name={board.name}
                isActive={activeBoardId === board.id}
                colorClass={DOT_COLORS[index % DOT_COLORS.length]}
                onClick={() => setActiveBoardId(board.id)}
              />
            ))}
            <div className="mt-2">
              <NewBoardButton onClick={onOpenBoardModal} />
            </div>
          </div>
        )}
      </div>
      
      {/* Footer Area */}
      <div className="p-6 mb-4">
        {isGuestMode && (
          <div className="text-xs text-ink/50 text-center font-bold">
            nexusclip v1.0 • guest session
          </div>
        )}
      </div>
    </aside>
  );
};
