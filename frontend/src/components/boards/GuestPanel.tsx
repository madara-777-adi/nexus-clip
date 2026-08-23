import React from 'react';

interface GuestPanelProps {
  boardCode: string | null;
  onPromoteClick: () => void;
}

export const GuestPanel: React.FC<GuestPanelProps> = ({ boardCode, onPromoteClick }) => {
  return (
    <div
      className="bg-violet p-4 flex flex-col gap-4 text-card mx-0"
      style={{
        border: '4px solid var(--ink)',
        boxShadow: '8px 8px 0 var(--ink)',
        transform: 'rotate(-0.6deg)',
      }}
    >
      <div className="text-[12px] font-bold text-card/80">
        Board code — hop devices, no login needed
      </div>
      <div className="flex items-center gap-3 flex-wrap">
        {boardCode ? (
          <div
            className="font-display text-[20px] text-cyan tracking-widest bg-ink px-3.5 py-1.5 inline-block"
          >
            {boardCode}
          </div>
        ) : (
          <div className="font-mono text-sm text-card/70 italic">
            Appears after first clip
          </div>
        )}
        <div
          className="text-[12px] font-bold bg-paper text-ink px-2 py-0.5 inline-block"
          style={{ border: '3px solid var(--ink)' }}
        >
          GUEST MODE
        </div>
      </div>
      
      <p className="text-xs text-card/80 leading-relaxed">
        This temporary board expires in 24 hours. Use this code on other devices to access it.
      </p>

      <button
        onClick={onPromoteClick}
        className="neo-btn w-full text-xs py-2.5 mt-1"
      >
        Sign up to keep this board
      </button>
    </div>
  );
};
