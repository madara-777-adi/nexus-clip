import React from 'react';
import { FileText, Code2, Type, Image as ImageIcon, File as FileIcon, Link as LinkIcon } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { ClipType } from '../../types';

interface ClipTypeChipProps {
  type: ClipType;
}

const TYPE_CONFIG: Record<ClipType, { icon: LucideIcon; label: string; color: string }> = {
  text: { icon: Type, label: 'TEXT', color: 'text-mint' },
  markdown: { icon: FileText, label: 'MARKDOWN', color: 'text-mint' },
  code: { icon: Code2, label: 'CODE', color: 'text-sky' },
  url: { icon: LinkIcon, label: 'LINK', color: 'text-lav' },
  image: { icon: ImageIcon, label: 'IMAGE', color: 'text-sun' },
  file: { icon: FileIcon, label: 'FILE', color: 'text-coral' },
};

export const ClipTypeChip: React.FC<ClipTypeChipProps> = ({ type }) => {
  const config = TYPE_CONFIG[type] || TYPE_CONFIG.text;
  const Icon = config.icon;

  return (
    <div className="flex items-center gap-3">
      <div className="w-[30px] h-[30px] rounded-[11px] clay-pressed flex items-center justify-center">
        <Icon size={14} strokeWidth={2.5} className={config.color} />
      </div>
      <span className="text-[11px] font-semibold uppercase tracking-widest text-muted">
        {config.label}
      </span>
    </div>
  );
};
