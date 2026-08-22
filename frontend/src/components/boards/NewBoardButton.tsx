import React from 'react';
import { Plus } from 'lucide-react';

interface NewBoardButtonProps {
  onClick: () => void;
}

export const NewBoardButton: React.FC<NewBoardButtonProps> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all text-left text-mint hover:bg-white/5"
    >
      <div className="w-5 h-5 flex items-center justify-center rounded-lg clay-raised">
        <Plus size={12} strokeWidth={3} className="text-mint" />
      </div>
      <span>New Board</span>
    </button>
  );
};
