import React from 'react';
import { useBoard } from '../../contexts/BoardContext';
import { ClipCard } from './ClipCard';
import type { ClipType } from '../../types';

export const ClipGrid: React.FC = () => {
  const { clips, loading, filterType, setFilterType, searchQuery } = useBoard();

  const FILTER_TABS: { id: ClipType | 'all'; label: string }[] = [
    { id: 'all', label: 'All' },
    { id: 'text', label: 'Text' },
    { id: 'code', label: 'Code' },
    { id: 'url', label: 'URLs' },
    { id: 'image', label: 'Images' },
    { id: 'file', label: 'Files' },
  ];

  if (loading) {
    return (
      <div className="mt-12 flex justify-center">
        <div
          className="w-6 h-6 animate-spin"
          style={{
            border: '3px solid var(--ink)',
            borderTopColor: 'transparent',
          }}
        />
      </div>
    );
  }

  // Sort: Pinned first, then by created_at desc
  const sortedClips = [...clips].sort((a, b) => {
    if (a.is_pinned === b.is_pinned) {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    }
    return a.is_pinned ? -1 : 1;
  });

  return (
    <div className="mt-8 flex flex-col gap-6">
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {FILTER_TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterType(tab.id)}
            className={`px-4 py-1.5 text-xs font-bold uppercase tracking-wider transition-all whitespace-nowrap ${
              filterType === tab.id
                ? 'bg-ink text-paper'
                : 'bg-card text-ink hover:bg-ink hover:text-paper'
            }`}
            style={{
              border: '3px solid var(--ink)',
              boxShadow: filterType === tab.id ? '3px 3px 0 var(--pink)' : 'none',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {sortedClips.length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center text-center">
          <div
            className="w-16 h-16 flex items-center justify-center mb-4 bg-card"
            style={{ border: '4px solid var(--ink)', boxShadow: '6px 6px 0 var(--ink)' }}
          >
            <span className="text-2xl">📭</span>
          </div>
          <h3 className="text-lg font-display text-ink mb-2">No clips found</h3>
          <p className="text-ink/65 text-sm max-w-sm">
            {searchQuery 
              ? `No results match "${searchQuery}"`
              : "Nothing here yet. Paste, drop, or upload to start this board."}
          </p>
        </div>
      ) : (
        <div className="clip-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(230px, 1fr))', gap: '26px' }}>
          {sortedClips.map(clip => (
            <ClipCard key={clip.id} clip={clip} />
          ))}
        </div>
      )}
    </div>
  );
};
