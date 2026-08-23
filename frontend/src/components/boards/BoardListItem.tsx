import React, { useState, useRef, useEffect } from 'react';
import { Pencil, Trash2, Check, X } from 'lucide-react';
import clsx from 'clsx';
import { useBoards } from '../../hooks/useBoards';

interface BoardListItemProps {
  id: string;
  name: string;
  isActive: boolean;
  colorClass: string;
  onClick: () => void;
}

export const BoardListItem: React.FC<BoardListItemProps> = ({ id, name, isActive, colorClass, onClick }) => {
  const { updateBoard, deleteBoard } = useBoards();
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(name);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isEditing]);

  const handleSaveRename = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!editName.trim() || editName === name) {
      setEditName(name);
      setIsEditing(false);
      return;
    }
    setIsSubmitting(true);
    try {
      await updateBoard(id, editName.trim());
      setIsEditing(false);
    } catch {
      setEditName(name);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${name}" and all its clips?`)) {
      try {
        await deleteBoard(id);
      } catch (err: any) {
        console.error(err);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setEditName(name);
      setIsEditing(false);
    }
  };

  if (isEditing) {
    return (
      <form 
        onSubmit={handleSaveRename}
        className="w-full flex items-center gap-2 px-3 py-2 bg-card"
        style={{ border: '3px solid var(--ink)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={clsx("w-2.5 h-2.5 shrink-0", colorClass)} />
        <input
          ref={inputRef}
          type="text"
          value={editName}
          onChange={(e) => setEditName(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isSubmitting}
          className="w-full bg-transparent text-sm text-ink outline-none px-1 font-body"
        />
        <button
          type="submit"
          disabled={isSubmitting || !editName.trim()}
          className="p-1 hover:text-cyan text-ink transition-colors shrink-0"
          title="Save"
        >
          <Check size={14} />
        </button>
        <button
          type="button"
          onClick={() => {
            setEditName(name);
            setIsEditing(false);
          }}
          className="p-1 hover:text-pink text-ink transition-colors shrink-0"
          title="Cancel"
        >
          <X size={14} />
        </button>
      </form>
    );
  }

  return (
    <div
      onClick={onClick}
      className={clsx(
        "group w-full flex items-center justify-between px-4 py-3 text-sm font-bold transition-all text-left cursor-pointer",
        isActive 
          ? "bg-card text-ink" 
          : "text-ink/70 hover:text-ink bg-transparent hover:bg-card/50"
      )}
      style={isActive ? { border: '3px solid var(--ink)', boxShadow: '4px 4px 0 var(--ink)' } : { border: '3px solid transparent' }}
    >
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <div 
          className={clsx("w-3 h-3 shrink-0", colorClass)}
        />
        <span className="truncate">{name}</span>
      </div>

      <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity ml-2 shrink-0">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsEditing(true);
          }}
          className="p-1 text-ink/60 hover:text-ink transition-colors"
          title="Rename board"
        >
          <Pencil size={13} />
        </button>
        <button
          onClick={handleDelete}
          className="p-1 text-ink/60 hover:text-pink transition-colors"
          title="Delete board"
        >
          <Trash2 size={13} />
        </button>
      </div>
    </div>
  );
};
