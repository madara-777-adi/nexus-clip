import React from 'react';
import { Plus } from 'lucide-react';

interface NewBoardButtonProps {
  onClick: () => void;
}

export const NewBoardButton: React.FC<NewBoardButtonProps> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-4 py-3 text-sm font-bold transition-all text-left text-pink hover:bg-card/50"
      style={{ border: '3px dashed var(--ink)' }}
    >
      <div className="w-5 h-5 flex items-center justify-center bg-ink text-paper">
        <Plus size={12} strokeWidth={3} />
      </div>
      <span>New Board</span>
    </button>
  );
};
