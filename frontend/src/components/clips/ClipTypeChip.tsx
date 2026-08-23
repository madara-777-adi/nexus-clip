import React from 'react';
import { FileText, Code2, Type, Image as ImageIcon, File as FileIcon, Link as LinkIcon } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { ClipType } from '../../types';

interface ClipTypeChipProps {
  type: ClipType;
}

const TYPE_CONFIG: Record<ClipType, { icon: LucideIcon; label: string; bg: string; textColor: string }> = {
  text: { icon: Type, label: 'TEXT', bg: 'var(--cyan)', textColor: 'var(--ink)' },
  markdown: { icon: FileText, label: 'MARKDOWN', bg: 'var(--cyan)', textColor: 'var(--ink)' },
  code: { icon: Code2, label: 'CODE', bg: 'var(--cyan)', textColor: 'var(--ink)' },
  url: { icon: LinkIcon, label: 'LINK', bg: 'var(--pink)', textColor: 'var(--ink)' },
  image: { icon: ImageIcon, label: 'IMAGE', bg: 'var(--violet)', textColor: '#FFFFFF' },
  file: { icon: FileIcon, label: 'FILE', bg: 'var(--pink)', textColor: 'var(--ink)' },
};

export const ClipTypeChip: React.FC<ClipTypeChipProps> = ({ type }) => {
  const config = TYPE_CONFIG[type] || TYPE_CONFIG.text;

  return (
    <span
      className="inline-block text-[11px] font-bold px-2 py-0.5 uppercase tracking-wide"
      style={{
        background: config.bg,
        color: config.textColor,
        border: '2px solid var(--ink)',
      }}
    >
      {config.label}
    </span>
  );
};
