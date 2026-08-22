import React from 'react';
import { Copy, Trash2 } from 'lucide-react';
import type { Clip } from '../../types';
import { ClipTypeChip } from './ClipTypeChip';
import { PinButton } from './PinButton';
import { useBoard } from '../../contexts/BoardContext';
import clsx from 'clsx';

interface ClipCardProps {
  clip: Clip;
}

const formatRelativeTime = (isoString: string) => {
  const date = new Date(isoString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

export const ClipCard: React.FC<ClipCardProps> = ({ clip }) => {
  const { showToast, deleteClip } = useBoard();

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (clip.content) {
      navigator.clipboard.writeText(clip.content);
      showToast('Copied to clipboard');
    } else if (clip.file_url) {
      navigator.clipboard.writeText(window.location.origin + clip.file_url);
      showToast('File URL copied');
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this clip?')) {
      try {
        await deleteClip(clip.id);
      } catch (err: any) {
        showToast(err.message || 'Failed to delete clip');
      }
    }
  };

  const renderContent = () => {
    switch (clip.type) {
      case 'code':
        return (
          <div className="mt-4 p-4 rounded-xl clay-pressed overflow-x-auto">
            <pre className="font-mono text-[12px] text-ink leading-relaxed">
              <code>{clip.content}</code>
            </pre>
          </div>
        );
      case 'markdown':
        return (
          <div className="mt-4 p-4 rounded-xl clay-pressed overflow-x-auto max-h-[300px] overflow-y-auto">
            <pre className="font-mono text-[12px] text-ink whitespace-pre-wrap">
              {clip.content}
            </pre>
          </div>
        );
      case 'image':
        return (
          <div className="mt-4 rounded-xl clay-pressed overflow-hidden flex items-center justify-center p-2">
            <img 
              src={clip.file_url || ''} 
              alt={clip.title}
              className="max-h-[300px] object-contain rounded-lg"
              loading="lazy"
            />
          </div>
        );
      case 'url':
        return (
          <div className="mt-4">
            <a 
              href={clip.content || '#'} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-lav hover:underline text-sm break-all font-mono"
            >
              {clip.content}
            </a>
          </div>
        );
      case 'file':
        return null; // File name is shown in the footer
      case 'text':
      default:
        return (
          <div className="mt-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            <p className="text-[14px] text-ink/90 whitespace-pre-wrap leading-[1.55]">
              {clip.content}
            </p>
          </div>
        );
    }
  };

  const isWide = clip.type === 'markdown' || clip.type === 'code';

  return (
    <div 
      className={clsx(
        "group p-[18px] pb-4 rounded-[24px] clay-raised flex flex-col transition-transform duration-150 hover:-translate-y-[3px]",
        isWide && "col-span-1 md:col-span-2"
      )}
    >
      <div className="flex items-center justify-between">
        <ClipTypeChip type={clip.type} />
        <PinButton clipId={clip.id} isPinned={clip.is_pinned} />
      </div>

      {clip.title && clip.type !== 'text' && clip.type !== 'markdown' && clip.type !== 'code' && (
        <h3 className="mt-4 font-semibold text-ink text-sm truncate">{clip.title}</h3>
      )}
      
      {/* For text/markdown/code, the content itself is the primary focus, title is secondary if present */}
      {(clip.type === 'text' || clip.type === 'markdown' || clip.type === 'code') && clip.title && clip.title !== 'Untitled Clip' && (
        <h3 className="mt-4 font-semibold text-ink/80 text-sm truncate">{clip.title}</h3>
      )}

      {renderContent()}

      <div className="mt-auto pt-4 flex items-center justify-between text-[10.5px] font-mono text-muted">
        <div className="flex items-center gap-3 truncate">
          {clip.type === 'file' && (
            <span className="truncate max-w-[120px]" title={clip.file_name || ''}>
              {clip.file_name}
            </span>
          )}
          {clip.type === 'file' && clip.file_size && (
            <span>
              {(clip.file_size / 1024).toFixed(1)} KB
            </span>
          )}
          <span>device-id-stub</span>
        </div>
        
        <div className="flex items-center gap-1.5 shrink-0">
          <span>{formatRelativeTime(clip.created_at)}</span>
          <button 
            onClick={handleCopy}
            className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/5 text-muted hover:text-ink"
            title="Copy to clipboard"
          >
            <Copy size={13} />
          </button>
          <button 
            onClick={handleDelete}
            className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/5 text-muted hover:text-coral"
            title="Delete clip"
          >
            <Trash2 size={13} />
          </button>
        </div>
      </div>
    </div>
  );
};
