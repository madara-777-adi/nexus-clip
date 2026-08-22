import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useBoard } from '../contexts/BoardContext';

interface BoardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BoardModal: React.FC<BoardModalProps> = ({ isOpen, onClose }) => {
  const { createBoard } = useBoard();
  const [name, setName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      await createBoard(name.trim());
      setName('');
      onClose();
    } catch (err: any) {
      alert(err.message || 'Failed to create board');
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

        <h3 className="font-display text-[23px] font-bold text-ink mb-6">Create New Board</h3>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-widest text-muted mb-2">
              Board Name
            </label>
            <input
              type="text"
              placeholder="e.g. Project Alpha, Resume Notes..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-transparent clay-pressed text-ink px-4 py-3 rounded-xl text-sm focus:outline-none placeholder:text-muted/60"
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
              disabled={isSubmitting || !name.trim()}
              className="px-5 py-3 clay-raised text-mint text-xs font-semibold uppercase tracking-widest rounded-xl hover:brightness-110 transition-all disabled:opacity-50"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
