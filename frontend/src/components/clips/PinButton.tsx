import React from 'react';
import { Pin } from 'lucide-react';
import clsx from 'clsx';
import { useBoard } from '../../contexts/BoardContext';

interface PinButtonProps {
  clipId: string;
  isPinned: boolean;
}

export const PinButton: React.FC<PinButtonProps> = ({ clipId, isPinned }) => {
  const { togglePin } = useBoard();

  const handleToggle = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await togglePin(clipId);
    } catch (error) {
      console.error("Failed to toggle pin", error);
    }
  };

  return (
    <button
      onClick={handleToggle}
      aria-label={isPinned ? 'Unpin clip' : 'Pin clip'}
      className={clsx(
        "w-[28px] h-[28px] flex items-center justify-center transition-all duration-150",
        isPinned ? "bg-pink text-card" : "bg-card text-ink hover:bg-ink/10"
      )}
      style={{ border: '2px solid var(--ink)' }}
    >
      <Pin
        size={14}
        className={clsx(
          "transition-colors duration-150",
          isPinned ? "fill-card" : ""
        )}
      />
    </button>
  );
};
