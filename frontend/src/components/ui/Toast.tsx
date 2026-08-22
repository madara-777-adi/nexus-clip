import React from 'react';
import { CheckCircle } from 'lucide-react';

interface ToastProps {
  message: string | null;
}

export const Toast: React.FC<ToastProps> = ({ message }) => {
  if (!message) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 clay-raised text-ink px-5 py-3.5 rounded-2xl animate-[fadeIn_0.2s_ease-out_forwards]">
      <div className="w-5 h-5 rounded-[7px] clay-pressed flex items-center justify-center">
        <CheckCircle className="w-3.5 h-3.5 text-mint" strokeWidth={2.5} />
      </div>
      <span className="text-[13px] font-medium tracking-wide">{message}</span>
    </div>
  );
};
