import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Lock, User, Phone, ArrowRight, CheckCircle2, AlertCircle, Sparkles, KeyRound, ArrowLeft } from 'lucide-react';
import { loginUser, registerUser, forgotPassword } from '../services/api';

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (user: { email: string; name: string; role?: string; id?: string }) => void;
  initialTab?: 'signin' | 'register' | 'forgot';
}

export const SignInModal: React.FC<SignInModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialTab = 'signin',
}) => {
  const [tab, setTab] = useState<'signin' | 'register' | 'forgot'>(initialTab);

  // Sign In fields
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register fields
  const [fullName, setFullName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');

  // Forgot password field
  const [forgotEmail, setForgotEmail] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setTab(initialTab);
    }
  }, [isOpen, initialTab]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Clear feedback when switching tabs
  useEffect(() => {
    setErrorMessage(null);
    setSuccessMessage(null);
  }, [tab]);

  if (!isOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginEmail || !loginPassword) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await loginUser({
        email: loginEmail,
        password: loginPassword,
      });

      setSuccessMessage('Authentication verified. Welcome back to NUTZ Atelier.');
      const user = response.user;
      const displayName = user.full_name || user.name || loginEmail.split('@')[0];

      setTimeout(() => {
        onSuccess?.({
          id: user.id,
          email: user.email,
          name: displayName,
          role: user.role,
        });
        setIsLoading(false);
        setSuccessMessage(null);
        setLoginEmail('');
        setLoginPassword('');
        onClose();
      }, 700);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Invalid email or password. Please try again.');
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !registerEmail || !registerPassword) {
      setErrorMessage('Full name, email, and password are required.');
      return;
    }

    if (registerPassword.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await registerUser({
        full_name: fullName.trim(),
        email: registerEmail.trim(),
        phone: phone.trim() || undefined,
        password: registerPassword,
        role: 'user',
      });

      setSuccessMessage('Account created! A verification link has been sent to your email.');
      const user = response.user;
      const displayName = user.full_name || user.name || registerEmail.split('@')[0];

      setTimeout(() => {
        onSuccess?.({
          id: user.id,
          email: user.email,
          name: displayName,
          role: user.role,
        });
        setIsLoading(false);
        setSuccessMessage(null);
        setFullName('');
        setRegisterEmail('');
        setPhone('');
        setRegisterPassword('');
        onClose();
      }, 900);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Registration failed. Please check your details.');
    }
  };

  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail) {
      setErrorMessage('Please enter your email address.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await forgotPassword(forgotEmail.trim());
      setIsLoading(false);
      setSuccessMessage(res.message || 'If this email is registered, password reset instructions have been sent.');
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Failed to request password reset. Please try again later.');
    }
  };

  const handleGuestSignIn = () => {
    onSuccess?.({ email: 'guest@nutz.ai', name: 'Guest Atelier Client' });
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
            aria-label="Close modal"
            className="absolute top-5 right-5 w-8 h-8 rounded-full bg-[#F5F4F8] hover:bg-[#EAE8F2] text-slate-500 hover:text-[#171717] flex items-center justify-center transition-colors cursor-pointer z-10"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="p-8 sm:p-10 text-center">
            {/* Acorn Brand Mark */}
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-[#F8F7F4] border border-[#EAE7E0] flex items-center justify-center p-2.5 shadow-sm">
              <img
                src="/nutz_acorn_logo.png"
                alt="NUTZ Fitting Room"
                className="w-full h-full object-contain"
              />
            </div>

            {/* Header */}
            <h2 className="text-2xl font-serif text-[#171717] tracking-tight">
              {tab === 'signin' && 'Sign In to NUTZ'}
              {tab === 'register' && 'Create Your NUTZ Account'}
              {tab === 'forgot' && 'Reset Your Password'}
            </h2>
            <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto leading-relaxed">
              {tab === 'signin' && 'Access your personal fittings, curated wardrobe, and try-on history.'}
              {tab === 'register' && 'Join NUTZ Atelier for private session memory and enterprise fitting.'}
              {tab === 'forgot' && 'Enter your registered email to receive a secure, single-use reset link.'}
            </p>

            {/* Tab Selector (for signin & register) */}
            {tab !== 'forgot' ? (
              <div className="flex bg-[#F5F4F8] rounded-2xl p-1 mt-5 border border-[#EAE7E0]">
                <button
                  type="button"
                  onClick={() => setTab('signin')}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                    tab === 'signin'
                      ? 'bg-white text-[#171717] shadow-sm'
                      : 'text-slate-500 hover:text-[#171717]'
                  }`}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => setTab('register')}
                  className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all cursor-pointer ${
                    tab === 'register'
                      ? 'bg-white text-[#171717] shadow-sm'
                      : 'text-slate-500 hover:text-[#171717]'
                  }`}
                >
                  Create Account
                </button>
              </div>
            ) : (
              <div className="mt-4 text-left">
                <button
                  type="button"
                  onClick={() => setTab('signin')}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-[#171717] transition-colors cursor-pointer"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Back to Sign In</span>
                </button>
              </div>
            )}

            {/* Error Banner */}
            {errorMessage && (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-3 rounded-2xl bg-red-50 border border-red-200 text-red-800 text-xs text-left flex items-start gap-2"
              >
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </motion.div>
            )}

            {/* Success Banner */}
            {successMessage && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="my-5 p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-center"
              >
                <CheckCircle2 className="w-7 h-7 mx-auto mb-1.5 text-emerald-600" />
                <p className="font-bold text-xs text-emerald-950">Notice</p>
                <p className="text-xs text-emerald-700 mt-0.5 leading-relaxed">{successMessage}</p>
              </motion.div>
            )}

            {/* FORMS */}
            {!successMessage || tab === 'forgot' ? (
              <div className="mt-5 space-y-4 text-left">
                {/* SIGN IN FORM */}
                {tab === 'signin' && (
                  <form onSubmit={handleLoginSubmit} className="space-y-3">
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        placeholder="name@fashionatelier.com"
                        required
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="password"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        placeholder="Password"
                        required
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <div className="flex justify-end pt-0.5">
                      <button
                        type="button"
                        onClick={() => setTab('forgot')}
                        className="text-[11px] font-semibold text-slate-500 hover:text-[#171717] transition-colors cursor-pointer"
                      >
                        Forgot password?
                      </button>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading || !loginEmail || !loginPassword}
                      className="w-full flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group mt-1"
                    >
                      <span>{isLoading ? 'Verifying Credentials...' : 'Sign In with Email'}</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  </form>
                )}

                {/* REGISTER FORM */}
                {tab === 'register' && (
                  <form onSubmit={handleRegisterSubmit} className="space-y-3">
                    <div className="relative">
                      <User className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Full Name (e.g. Eleanor Vance)"
                        required
                        minLength={2}
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        value={registerEmail}
                        onChange={(e) => setRegisterEmail(e.target.value)}
                        placeholder="Email Address"
                        required
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <div className="relative">
                      <Phone className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="Phone Number (Optional)"
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="password"
                        value={registerPassword}
                        onChange={(e) => setRegisterPassword(e.target.value)}
                        placeholder="Create Password (min. 8 characters)"
                        required
                        minLength={8}
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading || !fullName || !registerEmail || !registerPassword}
                      className="w-full flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group mt-2"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                      <span>{isLoading ? 'Creating Account...' : 'Create Account'}</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  </form>
                )}

                {/* FORGOT PASSWORD FORM */}
                {tab === 'forgot' && (
                  <form onSubmit={handleForgotSubmit} className="space-y-3">
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        value={forgotEmail}
                        onChange={(e) => setForgotEmail(e.target.value)}
                        placeholder="Registered Email Address"
                        required
                        className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading || !forgotEmail}
                      className="w-full flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group"
                    >
                      <KeyRound className="w-3.5 h-3.5 text-indigo-300" />
                      <span>{isLoading ? 'Sending Instructions...' : 'Send Reset Link'}</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  </form>
                )}

                {/* Guest Quick Mode */}
                {tab !== 'forgot' && (
                  <div className="pt-2 text-center border-t border-[#EAE7E0]/60">
                    <button
                      type="button"
                      onClick={handleGuestSignIn}
                      className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 hover:text-[#171717] transition-colors cursor-pointer"
                    >
                      <User className="w-3 h-3" />
                      <span>Continue as Guest Atelier Client</span>
                    </button>
                  </div>
                )}
              </div>
            ) : null}

            {/* Actions / Buttons end */}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
