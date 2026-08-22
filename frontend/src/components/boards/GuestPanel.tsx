import React from 'react';

interface GuestPanelProps {
  boardCode: string | null;
  onPromoteClick: () => void;
}

export const GuestPanel: React.FC<GuestPanelProps> = ({ boardCode, onPromoteClick }) => {
  return (
    <div className="clay-raised rounded-3xl p-5 mx-4 flex flex-col gap-4">
      <div>
        <div className="text-[11px] font-semibold uppercase tracking-widest text-muted mb-2">
          Guest Board Code
        </div>
        {boardCode ? (
          <div className="font-mono text-2xl font-semibold text-sun">
            {boardCode}
          </div>
        ) : (
          <div className="font-mono text-sm text-muted/70 italic">
            Appears after first clip
          </div>
        )}
      </div>
      
      <p className="text-xs text-muted leading-relaxed">
        This temporary board expires in 24 hours. Use this code on other devices to access it.
      </p>

      <button
        onClick={onPromoteClick}
        className="mt-2 w-full py-2.5 rounded-xl clay-pressed text-xs font-semibold text-mint hover:text-white transition-colors"
      >
        Sign up to keep this board
      </button>
    </div>
  );
};
