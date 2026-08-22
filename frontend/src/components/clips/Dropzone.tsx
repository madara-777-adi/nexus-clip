import React, { useState, useRef } from 'react';
import clsx from 'clsx';
import { useBoard } from '../../contexts/BoardContext';
import { api } from '../../services/api';
import { Paperclip, Send, Code2, FileText, Link as LinkIcon } from 'lucide-react';
import type { ClipType } from '../../types';

export const Dropzone: React.FC = () => {
  const { createClip, showToast } = useBoard();
  const [text, setText] = useState('');
  const [selectedType, setSelectedType] = useState<ClipType>('text');
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-detect type as user types (unless manually chosen)
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setText(val);

    // Basic heuristic for auto-type detection
    const trimmed = val.trim();
    if (/^https?:\/\/[^\s]+$/i.test(trimmed)) {
      setSelectedType('url');
    } else if (
      trimmed.includes('const ') || 
      trimmed.includes('let ') || 
      trimmed.includes('var ') || 
      trimmed.includes('function') || 
      trimmed.includes('def ') || 
      trimmed.includes('class ') ||
      trimmed.includes('import ') ||
      (trimmed.includes('{') && trimmed.includes('}')) ||
      (trimmed.includes('(') && trimmed.includes(');'))
    ) {
      setSelectedType('code');
    } else if (trimmed.startsWith('# ') || trimmed.startsWith('## ') || trimmed.includes('**')) {
      setSelectedType('markdown');
    } else {
      setSelectedType('text');
    }
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    try {
      const uploadRes = await api.uploadFile(file);
      const isImage = file.type.startsWith('image/');
      await createClip({
        type: isImage ? 'image' : 'file',
        title: file.name,
        file_url: uploadRes.file_url,
        file_name: uploadRes.file_name,
        file_size: uploadRes.file_size,
        tags: [isImage ? 'image' : 'file'],
      });
    } catch (err: any) {
      console.error('Upload failed', err);
      showToast('File upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setIsUploading(true);
    try {
      let title = 'Quick Note';
      if (selectedType === 'code') title = 'Code Snippet';
      else if (selectedType === 'url') title = trimmed;
      else if (selectedType === 'markdown') title = trimmed.split('\n')[0].replace(/^#+\s*/, '') || 'Markdown Note';
      else title = trimmed.length > 30 ? trimmed.substring(0, 30) + '...' : trimmed;

      await createClip({
        type: selectedType,
        title,
        content: trimmed,
        tags: [selectedType],
      });

      setText('');
      setSelectedType('text');
      if (textareaRef.current) {
        textareaRef.current.blur();
      }
    } catch (err: any) {
      showToast(err.message || 'Failed to create clip');
    } finally {
      setIsUploading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setIsDragOver(false);
      }}
      onDrop={handleDrop}
      className={clsx(
        "w-full rounded-3xl clay-pressed transition-all duration-200 relative overflow-hidden flex flex-col p-4 mb-8",
        isDragOver && "shadow-[0_0_0_2px_var(--mint),inset_6px_6px_12px_rgba(0,0,0,.5),inset_-5px_-5px_10px_rgba(255,255,255,.03)]",
        isFocused || text.length > 0 ? "min-h-[140px]" : "min-h-[110px]"
      )}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
      />

      {isUploading ? (
        <div className="flex-1 flex flex-col items-center justify-center py-6 gap-3">
          <div className="w-48 h-1.5 rounded-full clay-pressed overflow-hidden relative">
            <div className="absolute top-0 left-0 h-full bg-mint w-1/2 animate-[progress_1s_ease-in-out_infinite]" />
          </div>
          <span className="text-xs font-semibold text-mint uppercase tracking-widest">Processing...</span>
        </div>
      ) : (
        <>
          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Type note, paste code/URL, or drag & drop files here..."
            className="w-full flex-1 bg-transparent text-sm text-ink placeholder:text-muted/60 outline-none resize-none font-mono leading-relaxed"
            rows={isFocused || text.length > 0 ? 3 : 2}
          />

          <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/[0.04]">
            {/* Type selector & attach button */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="p-2 rounded-xl clay-raised text-muted hover:text-ink transition-all text-xs flex items-center gap-1.5"
                title="Upload file"
              >
                <Paperclip size={14} />
                <span className="hidden sm:inline text-[11px] font-semibold uppercase tracking-wider">File</span>
              </button>

              <div className="h-4 w-[1px] bg-white/[0.06] mx-1" />

              <button
                type="button"
                onClick={() => setSelectedType('text')}
                className={clsx(
                  "px-2.5 py-1.5 rounded-xl text-[11px] font-semibold uppercase tracking-wider transition-all flex items-center gap-1",
                  selectedType === 'text' ? "clay-pressed text-sky" : "clay-raised text-muted hover:text-ink"
                )}
              >
                <FileText size={12} />
                <span>Text</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedType('code')}
                className={clsx(
                  "px-2.5 py-1.5 rounded-xl text-[11px] font-semibold uppercase tracking-wider transition-all flex items-center gap-1",
                  selectedType === 'code' ? "clay-pressed text-mint" : "clay-raised text-muted hover:text-ink"
                )}
              >
                <Code2 size={12} />
                <span>Code</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedType('url')}
                className={clsx(
                  "px-2.5 py-1.5 rounded-xl text-[11px] font-semibold uppercase tracking-wider transition-all flex items-center gap-1",
                  selectedType === 'url' ? "clay-pressed text-lav" : "clay-raised text-muted hover:text-ink"
                )}
              >
                <LinkIcon size={12} />
                <span>URL</span>
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline text-[10px] font-mono text-muted/60">
                ⌘+Enter
              </span>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!text.trim()}
                className={clsx(
                  "px-4 py-1.5 rounded-xl text-xs font-semibold uppercase tracking-widest flex items-center gap-1.5 transition-all",
                  text.trim()
                    ? "clay-raised text-mint hover:brightness-110 cursor-pointer"
                    : "opacity-40 text-muted cursor-not-allowed"
                )}
              >
                <Send size={12} />
                <span>Save</span>
              </button>
            </div>
          </div>
        </>
      )}

      <style>{`
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
    </div>
  );
};
