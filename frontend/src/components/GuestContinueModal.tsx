import React, { useState } from 'react';
import { KeyRound, X } from 'lucide-react';
import { useBoard } from '../contexts/BoardContext';

interface GuestContinueModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GuestContinueModal: React.FC<GuestContinueModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { continueGuestBoard } = useBoard();
  const [boardCode, setBoardCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!boardCode.trim()) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await continueGuestBoard(boardCode.trim());
      setBoardCode('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Board code not found or expired.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#030712]/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md clay-raised rounded-[24px] p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 w-8 h-8 rounded-xl clay-raised flex items-center justify-center text-muted hover:text-ink transition-colors"
        >
          <X size={16} />
        </button>

        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-[14px] clay-pressed flex items-center justify-center text-mint">
            <KeyRound size={20} strokeWidth={2.5} />
          </div>
          <div>
            <h3 className="font-display text-[23px] font-bold text-ink leading-tight">
              Continue Board
            </h3>
            <p className="text-[11px] font-semibold text-muted uppercase tracking-widest mt-1">
              Enter 6-character code
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl clay-pressed border border-coral/20 text-coral text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <input
              type="text"
              placeholder="NEXUS-XXXX"
              value={boardCode}
              onChange={(e) => setBoardCode(e.target.value.toUpperCase())}
              className="w-full bg-transparent clay-pressed text-ink font-mono tracking-widest text-center px-4 py-4 rounded-xl text-lg focus:outline-none placeholder:text-muted/40 uppercase"
              autoFocus
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-3 clay-pressed text-muted text-xs font-semibold uppercase tracking-widest rounded-xl hover:text-ink transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !boardCode.trim()}
              className="px-5 py-3 clay-raised text-mint text-xs font-semibold uppercase tracking-widest rounded-xl hover:brightness-110 transition-all disabled:opacity-50"
            >
              Sync
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
