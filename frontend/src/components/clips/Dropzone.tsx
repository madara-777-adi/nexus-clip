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
        "w-full transition-all duration-200 relative overflow-hidden flex flex-col p-5 mb-8",
        isDragOver && "bg-cyan/10",
        isFocused || text.length > 0 ? "min-h-[140px]" : "min-h-[110px]"
      )}
      style={{
        border: '4px dashed var(--ink)',
        background: isDragOver
          ? undefined
          : 'repeating-linear-gradient(135deg, var(--card), var(--card) 12px, #f4f4f4 12px, #f4f4f4 24px)',
      }}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
      />

      {isUploading ? (
        <div className="flex-1 flex flex-col items-center justify-center py-6 gap-3">
          <div className="w-48 h-2 overflow-hidden relative bg-card" style={{ border: '2px solid var(--ink)' }}>
            <div
              className="absolute top-0 left-0 h-full bg-cyan w-1/2"
              style={{ animation: 'progress 1s ease-in-out infinite' }}
            />
          </div>
          <span className="text-xs font-bold text-ink uppercase tracking-widest">Processing...</span>
        </div>
      ) : (
        <>
          {/* Header label */}
          {!isFocused && text.length === 0 && (
            <div className="text-center font-display text-[18px] text-ink mb-3">
              DRAG A FILE HERE, OR PASTE WITH ⌘V
            </div>
          )}

          <textarea
            ref={textareaRef}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Type note, paste code/URL, or drag & drop files here..."
            className="w-full flex-1 bg-transparent text-sm text-ink placeholder:text-ink/35 outline-none resize-none font-mono leading-relaxed"
            rows={isFocused || text.length > 0 ? 3 : 2}
          />

          <div className="flex items-center justify-between mt-3 pt-3" style={{ borderTop: '2px solid var(--ink)' }}>
            {/* Type selector & attach button */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="py-1.5 px-2.5 text-ink text-xs flex items-center gap-1.5 font-bold transition-all hover:bg-ink hover:text-paper"
                style={{ border: '2px solid var(--ink)' }}
                title="Upload file"
              >
                <Paperclip size={14} />
                <span className="hidden sm:inline text-[11px] font-bold uppercase tracking-wider">File</span>
              </button>

              <div className="h-5 w-[2px] bg-ink mx-1" />

              <button
                type="button"
                onClick={() => setSelectedType('text')}
                className={clsx(
                  "px-2.5 py-1.5 text-[11px] font-bold uppercase tracking-wider transition-all flex items-center gap-1",
                  selectedType === 'text' ? "bg-cyan text-ink" : "bg-card text-ink hover:bg-ink/10"
                )}
                style={{ border: '2px solid var(--ink)' }}
              >
                <FileText size={12} />
                <span>Text</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedType('code')}
                className={clsx(
                  "px-2.5 py-1.5 text-[11px] font-bold uppercase tracking-wider transition-all flex items-center gap-1",
                  selectedType === 'code' ? "bg-cyan text-ink" : "bg-card text-ink hover:bg-ink/10"
                )}
                style={{ border: '2px solid var(--ink)' }}
              >
                <Code2 size={12} />
                <span>Code</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedType('url')}
                className={clsx(
                  "px-2.5 py-1.5 text-[11px] font-bold uppercase tracking-wider transition-all flex items-center gap-1",
                  selectedType === 'url' ? "bg-pink text-ink" : "bg-card text-ink hover:bg-ink/10"
                )}
                style={{ border: '2px solid var(--ink)' }}
              >
                <LinkIcon size={12} />
                <span>URL</span>
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <span className="hidden sm:inline text-[10px] font-mono text-ink/50 font-bold">
                ⌘+Enter
              </span>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!text.trim()}
                className={clsx(
                  "neo-btn text-xs py-1.5 px-4",
                  !text.trim() && "opacity-40 cursor-not-allowed"
                )}
              >
                <Send size={12} />
                <span>Save</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
