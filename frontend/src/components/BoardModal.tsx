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

        <h3 className="font-display text-[23px] font-bold text-ink mb-6">Create New Board</h3>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-widest text-ink mb-2">
              Board Name
            </label>
            <input
              type="text"
              placeholder="e.g. Project Alpha, Resume Notes..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="neo-input"
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
              disabled={isSubmitting || !name.trim()}
              className="neo-btn text-xs py-3 px-5"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
