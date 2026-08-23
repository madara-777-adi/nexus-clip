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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-4">
      <div
        className="w-full max-w-md bg-card p-8 relative"
        style={{ border: '4px solid var(--ink)', boxShadow: '10px 10px 0 var(--ink)' }}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-ink bg-card hover:bg-pink hover:text-card transition-colors"
          style={{ border: '3px solid var(--ink)' }}
        >
          <X size={16} />
        </button>

        <div className="flex items-center gap-4 mb-6">
          <div
            className="w-12 h-12 flex items-center justify-center text-cyan bg-ink"
          >
            <KeyRound size={20} strokeWidth={2.5} />
          </div>
          <div>
            <h3 className="font-display text-[23px] font-bold text-ink leading-tight">
              Continue Board
            </h3>
            <p className="text-[11px] font-bold text-ink/65 uppercase tracking-widest mt-1">
              Enter 6-character code
            </p>
          </div>
        </div>

        {error && (
          <div
            className="mb-6 p-4 text-pink text-sm font-bold bg-pink/10"
            style={{ border: '3px solid var(--pink)' }}
          >
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
              className="neo-input font-display tracking-widest text-center text-lg uppercase"
              style={{ padding: '16px' }}
              autoFocus
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="neo-btn-secondary text-xs py-3 px-5"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !boardCode.trim()}
              className="neo-btn text-xs py-3 px-5"
            >
              Sync
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
