import React from 'react';
import { useBoard } from '../../contexts/BoardContext';
import { BoardListItem } from '../boards/BoardListItem';
import { NewBoardButton } from '../boards/NewBoardButton';
import { GuestPanel } from '../boards/GuestPanel';

const DOT_COLORS = ['bg-mint', 'bg-sky', 'bg-sun', 'bg-lav', 'bg-coral'];

export const Sidebar: React.FC<{ 
  onOpenAuth: () => void;
  onOpenBoardModal: () => void;
}> = ({ onOpenAuth, onOpenBoardModal }) => {
  const { isGuestMode, boards, activeBoardId, setActiveBoardId, guestSession } = useBoard();

  return (
    <aside className="w-[264px] h-screen flex-col hidden lg:flex border-r border-clay-hi/20 relative">
      {/* Logo Area */}
      <div className="h-24 flex items-center px-6 gap-4">
        <div className="w-[34px] h-[34px] rounded-[14px] clay-raised flex items-center justify-center">
          <div className="w-3 h-3 rounded-full bg-mint shadow-[0_0_8px_var(--mint)]" />
        </div>
        <div className="font-display text-[23px] font-bold tracking-wide">
          nexus<span className="text-mint">clip</span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4 scrollbar-thin">
        {isGuestMode ? (
          <GuestPanel 
            boardCode={guestSession?.board_code || null}
            onPromoteClick={onOpenAuth}
          />
        ) : (
          <div className="flex flex-col gap-1">
            <div className="text-[11px] font-semibold uppercase tracking-widest text-muted px-4 mb-3">
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
          <div className="text-xs text-muted/50 text-center">
            nexusclip v1.0 • guest session
          </div>
        )}
      </div>
    </aside>
  );
};
