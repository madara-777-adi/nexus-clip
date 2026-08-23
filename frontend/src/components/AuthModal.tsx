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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-4">
      <div
        className="w-full max-w-md bg-card p-8 relative"
        style={{ border: '4px solid var(--ink)', boxShadow: '10px 10px 0 var(--ink)' }}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-ink bg-card hover:bg-pink hover:text-card transition-colors"
          style={{ border: '3px solid var(--ink)' }}
        >
          <X size={16} />
        </button>

        {/* Tab Headers */}
        <div className="flex gap-3 mb-8">
          <button
            onClick={() => {
              setIsLoginTab(true);
              setError(null);
            }}
            className={`flex-1 py-3 text-[13px] font-bold uppercase tracking-widest transition-all ${
              isLoginTab
                ? 'bg-ink text-paper'
                : 'bg-card text-ink hover:bg-ink/10'
            }`}
            style={{ border: '3px solid var(--ink)', boxShadow: isLoginTab ? '3px 3px 0 var(--pink)' : 'none' }}
          >
            Sign In
          </button>
          <button
            onClick={() => {
              setIsLoginTab(false);
              setError(null);
            }}
            className={`flex-1 py-3 text-[13px] font-bold uppercase tracking-widest transition-all ${
              !isLoginTab
                ? 'bg-ink text-paper'
                : 'bg-card text-ink hover:bg-ink/10'
            }`}
            style={{ border: '3px solid var(--ink)', boxShadow: !isLoginTab ? '3px 3px 0 var(--pink)' : 'none' }}
          >
            Register
          </button>
        </div>

        {error && (
          <div
            className="mb-6 p-4 text-pink text-sm font-bold bg-pink/10"
            style={{ border: '3px solid var(--pink)' }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {!isLoginTab && (
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-widest text-ink mb-2">
                Full Name
              </label>
              <input
                type="text"
                required
                placeholder="Jane Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="neo-input"
              />
            </div>
          )}

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-widest text-ink mb-2">
              Email Address
            </label>
            <input
              type="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="neo-input"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-widest text-ink mb-2">
              Password
            </label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="neo-input"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="neo-btn w-full mt-4 py-3.5"
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
