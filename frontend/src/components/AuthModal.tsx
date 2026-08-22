import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { login, register } = useAuth();
  const [isLoginTab, setIsLoginTab] = useState(true);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (isLoginTab) {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#030712]/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md clay-raised rounded-[24px] p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 w-8 h-8 rounded-xl clay-raised flex items-center justify-center text-muted hover:text-ink transition-colors"
        >
          <X size={16} />
        </button>

        {/* Tab Headers */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => {
              setIsLoginTab(true);
              setError(null);
            }}
            className={`flex-1 py-3 text-[13px] font-semibold uppercase tracking-widest rounded-xl transition-all ${
              isLoginTab
                ? 'clay-pressed text-mint'
                : 'clay-raised text-muted hover:text-ink'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => {
              setIsLoginTab(false);
              setError(null);
            }}
            className={`flex-1 py-3 text-[13px] font-semibold uppercase tracking-widest rounded-xl transition-all ${
              !isLoginTab
                ? 'clay-pressed text-mint'
                : 'clay-raised text-muted hover:text-ink'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl clay-pressed border border-coral/20 text-coral text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {!isLoginTab && (
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-widest text-muted mb-2">
                Full Name
              </label>
              <input
                type="text"
                required
                placeholder="Jane Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-transparent clay-pressed text-ink px-4 py-3 rounded-xl text-sm focus:outline-none placeholder:text-muted/60"
              />
            </div>
          )}

          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-widest text-muted mb-2">
              Email Address
            </label>
            <input
              type="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-transparent clay-pressed text-ink px-4 py-3 rounded-xl text-sm focus:outline-none placeholder:text-muted/60"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-widest text-muted mb-2">
              Password
            </label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-transparent clay-pressed text-ink px-4 py-3 rounded-xl text-sm focus:outline-none placeholder:text-muted/60"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-4 py-3.5 rounded-xl clay-raised text-mint font-semibold uppercase tracking-widest text-sm hover:brightness-110 transition-all disabled:opacity-50"
          >
            {isSubmitting
              ? 'Processing...'
              : isLoginTab
              ? 'Sign In'
              : 'Create Account'}
          </button>
        </form>
      </div>
    </div>
  );
};
