import React from 'react';
import { CheckCircle } from 'lucide-react';

interface ToastProps {
  message: string | null;
}

export const Toast: React.FC<ToastProps> = ({ message }) => {
  if (!message) return null;

  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-card text-ink px-5 py-3.5"
      style={{
        border: '4px solid var(--ink)',
        boxShadow: '6px 6px 0 var(--ink)',
        animation: 'fadeIn 0.2s ease-out forwards',
      }}
    >
      <CheckCircle className="w-4 h-4 text-cyan" strokeWidth={2.5} />
      <span className="text-[13px] font-bold tracking-wide">{message}</span>
    </div>
  );
};
