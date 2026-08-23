import React, { useEffect, useState } from 'react';
import { Clock, ShieldCheck, X } from 'lucide-react';
import { useBoard } from '../contexts/BoardContext';
import { api } from '../services/api';
import type { UserSettings } from '../types';

interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  const { showToast } = useBoard();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      api
        .getSettings()
        .then((s) => setSettings(s))
        .catch(() => showToast('Failed to load settings'))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  const handleRetentionChange = async (days: '7' | '30' | '90' | 'never') => {
    if (!settings) return;
    try {
      const updated = await api.updateSettings({ auto_cleanup_days: days });
      setSettings(updated);
      showToast(`Retention policy updated to ${days === 'never' ? 'Never' : days + ' days'}`);
    } catch (err: any) {
      showToast(err.message || 'Failed to update retention policy');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-ink/60">
      <div
        className="w-full max-w-md bg-paper h-full p-8 overflow-y-auto relative"
        style={{ borderLeft: '5px solid var(--ink)' }}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-ink bg-card hover:bg-pink hover:text-card transition-colors"
          style={{ border: '3px solid var(--ink)' }}
        >
          <X size={16} />
        </button>

        <h3 className="font-display text-[27px] font-bold text-ink leading-tight mb-8">Settings</h3>

        {loading || !settings ? (
          <div className="flex items-center justify-center py-12">
            <div
              className="w-6 h-6 animate-spin"
              style={{ border: '3px solid var(--ink)', borderTopColor: 'transparent' }}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Auto Cleanup Section */}
            <div
              className="bg-card p-6"
              style={{ border: '4px solid var(--ink)', boxShadow: '6px 6px 0 var(--ink)' }}
            >
              <div className="flex items-center gap-3 mb-3">
                <Clock className="w-5 h-5 text-cyan" />
                <h4 className="text-[14px] font-bold text-ink tracking-wide">
                  Auto Cleanup
                </h4>
              </div>
              <p className="text-xs text-ink/65 mb-6 leading-relaxed">
                Automatically prune unpinned clips older than the selected retention period.
              </p>

              <div className="grid grid-cols-2 gap-3">
                {(['7', '30', '90', 'never'] as const).map((days) => (
                  <button
                    key={days}
                    onClick={() => handleRetentionChange(days)}
                    className={`py-3 text-[12px] font-bold uppercase tracking-widest transition-all ${
                      settings.auto_cleanup_days === days
                        ? 'bg-ink text-paper'
                        : 'bg-card text-ink hover:bg-ink/10'
                    }`}
                    style={{
                      border: '3px solid var(--ink)',
                      boxShadow: settings.auto_cleanup_days === days ? '3px 3px 0 var(--pink)' : 'none',
                    }}
                  >
                    {days === 'never' ? 'Never' : `${days} Days`}
                  </button>
                ))}
              </div>
            </div>

            {/* Privacy Protection Note */}
            <div
              className="bg-paper p-5"
              style={{ border: '3px solid var(--ink)' }}
            >
              <div className="flex items-center gap-2 mb-2">
                <ShieldCheck className="w-4 h-4 text-pink" />
                <h4 className="text-xs font-bold text-pink uppercase tracking-wider">
                  Protected Clips
                </h4>
              </div>
              <p className="text-[11px] text-ink/65 leading-relaxed">
                Pinned clips are permanently protected and will never be automatically deleted by background cleanup jobs.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
