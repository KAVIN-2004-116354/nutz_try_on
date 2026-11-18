import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, ArrowRight, CheckCircle2, User } from 'lucide-react';

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (user: { email: string; name: string }) => void;
}

export const SignInModal: React.FC<SignInModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes('@')) return;

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
      const name = email.split('@')[0];
      const capitalized = name.charAt(0).toUpperCase() + name.slice(1);
      setTimeout(() => {
        onSuccess?.({ email, name: capitalized });
        setIsSubmitted(false);
        setEmail('');
        onClose();
      }, 900);
    }, 600);
  };

  const handleGoogleSignIn = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
      setTimeout(() => {
        onSuccess?.({ email: 'client@atelier.nutz', name: 'Atelier Patron' });
        setIsSubmitted(false);
        onClose();
      }, 700);
    }, 500);
  };

  const handleGuestSignIn = () => {
    onSuccess?.({ email: 'guest@nutz.ai', name: 'Guest Fitting' });
    onClose();
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-[#0A0A0E]/60 backdrop-blur-md"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-md bg-white rounded-3xl border border-[#EAE7E0] shadow-2xl overflow-hidden z-10"
        >
          {/* Close Button */}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close sign in modal"
            className="absolute top-5 right-5 w-8 h-8 rounded-full bg-[#F5F4F8] hover:bg-[#EAE8F2] text-slate-500 hover:text-[#171717] flex items-center justify-center transition-colors cursor-pointer z-10"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="p-8 sm:p-10 text-center">
            {/* Acorn Brand Mark */}
            <div className="w-14 h-14 mx-auto mb-5 rounded-2xl bg-[#F8F7F4] border border-[#EAE7E0] flex items-center justify-center p-2.5 shadow-sm">
              <img
                src="/nutz_acorn_logo.png"
                alt="NUTZ Fitting Room"
                className="w-full h-full object-contain"
              />
            </div>

            {/* Header */}
            <h2 className="text-2xl font-serif text-[#171717] tracking-tight">
              Sign In to NUTZ
            </h2>
            <p className="text-xs text-slate-500 mt-2 max-w-xs mx-auto leading-relaxed">
              Access your personal fittings, curated wardrobe, and high-fidelity tailoring drape history.
            </p>

            {isSubmitted ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="my-8 p-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-center"
              >
                <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-600" />
                <p className="font-bold text-sm text-emerald-950">Welcome to NUTZ Atelier</p>
                <p className="text-xs text-emerald-700 mt-1">Your wardrobe session has been activated.</p>
              </motion.div>
            ) : (
              <div className="mt-8 space-y-4 text-left">
                {/* Google Sign In Button */}
                <button
                  type="button"
                  onClick={handleGoogleSignIn}
                  disabled={isLoading}
                  className="w-full flex items-center justify-center gap-3 px-5 py-3.5 rounded-2xl border border-[#EAE7E0] bg-white hover:bg-[#F9F9FC] text-[#171717] font-bold text-xs shadow-sm hover:border-slate-300 transition-all duration-200 cursor-pointer"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                  <span>Continue with Google</span>
                </button>

                {/* Divider */}
                <div className="flex items-center gap-3 my-4">
                  <div className="flex-1 h-px bg-[#EAE7E0]" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    or with email
                  </span>
                  <div className="flex-1 h-px bg-[#EAE7E0]" />
                </div>

                {/* Email Form */}
                <form onSubmit={handleSubmit} className="space-y-3">
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@fashionatelier.com"
                      required
                      className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading || !email}
                    className="w-full flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    <span>{isLoading ? 'Authenticating...' : 'Sign In with Email'}</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </form>

                {/* Guest Quick Mode */}
                <div className="pt-2 text-center">
                  <button
                    type="button"
                    onClick={handleGuestSignIn}
                    className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 hover:text-[#171717] transition-colors cursor-pointer"
                  >
                    <User className="w-3 h-3" />
                    <span>Continue as Guest Atelier Client</span>
                  </button>
                </div>
              </div>
            )}

            {/* Footer Disclaimer */}
            <p className="text-[10px] text-slate-400 mt-6 leading-relaxed">
              By continuing, you agree to NUTZ Tailoring Terms of Service &amp; Privacy Policy.
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
