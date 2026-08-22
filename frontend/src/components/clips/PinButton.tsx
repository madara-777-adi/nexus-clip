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
        "w-[30px] h-[30px] rounded-[11px] flex items-center justify-center transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mint focus-visible:ring-offset-2 focus-visible:ring-offset-[#2B2E3D]",
        isPinned ? "clay-pressed" : "clay-raised hover:brightness-110"
      )}
    >
      <Pin
        size={14}
        className={clsx(
          "transition-colors duration-150",
          isPinned ? "text-coral fill-coral" : "text-muted"
        )}
      />
    </button>
  );
};
