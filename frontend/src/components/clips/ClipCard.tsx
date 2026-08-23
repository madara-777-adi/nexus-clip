import React from 'react';
import { Copy, Trash2 } from 'lucide-react';
import type { Clip } from '../../types';
import { ClipTypeChip } from './ClipTypeChip';
import { PinButton } from './PinButton';
import { useBoard } from '../../contexts/BoardContext';
import { resolveFileUrl } from '../../services/api';
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

/** Map clip types to the sample's CSS class equivalents for border-top accent */
const typeToAccentBorder = (type: string): string => {
  switch (type) {
    case 'text':
    case 'markdown':
    case 'code':
      return 'var(--cyan)';
    case 'url':
      return 'var(--pink)';
    case 'image':
    case 'file':
      return 'var(--violet)';
    default:
      return 'var(--cyan)';
  }
};

export const ClipCard: React.FC<ClipCardProps> = ({ clip }) => {
  const { showToast, deleteClip } = useBoard();

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (clip.content) {
      navigator.clipboard.writeText(clip.content);
      showToast('Copied to clipboard');
    } else if (clip.file_url) {
      navigator.clipboard.writeText(resolveFileUrl(clip.file_url));
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
          <div className="mt-4 p-4 overflow-x-auto bg-ink/5" style={{ border: '2px solid var(--ink)' }}>
            <pre className="font-mono text-[12px] text-ink leading-relaxed">
              <code>{clip.content}</code>
            </pre>
          </div>
        );
      case 'markdown':
        return (
          <div className="mt-4 p-4 overflow-x-auto max-h-[300px] overflow-y-auto bg-ink/5" style={{ border: '2px solid var(--ink)' }}>
            <pre className="font-mono text-[12px] text-ink whitespace-pre-wrap">
              {clip.content}
            </pre>
          </div>
        );
      case 'image':
        return (
          <div className="mt-4 overflow-hidden flex items-center justify-center">
            <img 
              src={clip.file_url ? resolveFileUrl(clip.file_url) : ''} 
              alt={clip.title}
              className="max-h-[300px] w-full object-contain"
              style={{ border: '3px solid var(--ink)' }}
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
              className="text-pink hover:underline text-sm break-all font-mono font-bold"
              style={{ borderBottom: '2px solid var(--pink)' }}
            >
              {clip.content}
            </a>
          </div>
        );
      case 'file':
        return clip.file_url ? (
          <div className="mt-4">
            <a
              href={resolveFileUrl(clip.file_url)}
              download={clip.file_name || true}
              target="_blank"
              rel="noopener noreferrer"
              className="text-violet hover:underline text-sm break-all font-mono font-bold"
              style={{ borderBottom: '2px solid var(--violet)' }}
            >
              Download {clip.file_name || 'file'}
            </a>
          </div>
        ) : null; // File name is also shown in the footer
      case 'text':
      default:
        return (
          <div className="mt-4 max-h-[300px] overflow-y-auto pr-2">
            <p className="text-[14px] text-ink whitespace-pre-wrap leading-[1.5]">
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
        "group neo-card p-4 flex flex-col relative",
        isWide && "col-span-1 md:col-span-2"
      )}
      style={{
        borderTopColor: typeToAccentBorder(clip.type),
        borderTopWidth: '6px',
      }}
    >
      <div className="flex items-center justify-between">
        <ClipTypeChip type={clip.type} />
        <PinButton clipId={clip.id} isPinned={clip.is_pinned} />
      </div>

      {clip.title && clip.type !== 'text' && clip.type !== 'markdown' && clip.type !== 'code' && (
        <h3 className="mt-4 font-bold text-ink text-sm truncate">{clip.title}</h3>
      )}
      
      {/* For text/markdown/code, the content itself is the primary focus, title is secondary if present */}
      {(clip.type === 'text' || clip.type === 'markdown' || clip.type === 'code') && clip.title && clip.title !== 'Untitled Clip' && (
        <h3 className="mt-4 font-bold text-ink/80 text-sm truncate">{clip.title}</h3>
      )}

      {renderContent()}

      <div className="mt-auto pt-4 flex items-center justify-between text-[11px] font-mono text-ink/65">
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
            className="p-1.5 opacity-0 group-hover:opacity-100 transition-opacity text-ink/50 hover:text-ink"
            style={{ border: '2px solid transparent' }}
            title="Copy to clipboard"
          >
            <Copy size={13} />
          </button>
          <button 
            onClick={handleDelete}
            className="p-1.5 opacity-0 group-hover:opacity-100 transition-opacity text-ink/50 hover:text-pink"
            style={{ border: '2px solid transparent' }}
            title="Delete clip"
          >
            <Trash2 size={13} />
          </button>
        </div>
      </div>
    </div>
  );
};