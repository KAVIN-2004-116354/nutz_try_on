import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Lock, ArrowRight, CheckCircle2, AlertCircle, KeyRound } from 'lucide-react';
import { resetPassword } from '../services/api';

interface ResetPasswordModalProps {
  isOpen: boolean;
  token: string;
  onClose: () => void;
  onSuccess: () => void;
}

export const ResetPasswordModal: React.FC<ResetPasswordModalProps> = ({
  isOpen,
  token,
  onClose,
  onSuccess,
}) => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPassword || !confirmPassword) {
      setErrorMessage('Please fill in both password fields.');
      return;
    }

    if (newPassword.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      await resetPassword(token, newPassword);
      setIsLoading(false);
      setIsSuccess(true);
      setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (err: any) {
      setIsLoading(false);
      setErrorMessage(err.message || 'Password reset failed. The link may have expired or already been used.');
    }
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
            {/* Brand Mark */}
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-[#F8F7F4] border border-[#EAE7E0] flex items-center justify-center p-2.5 shadow-sm">
              <KeyRound className="w-7 h-7 text-[#171717]" />
            </div>

            {/* Header */}
            <h2 className="text-2xl font-serif text-[#171717] tracking-tight">
              Create New Password
            </h2>
            <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto leading-relaxed">
              Please enter and confirm your new secure password. Prior active sessions will be terminated.
            </p>

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

            {/* Success State */}
            {isSuccess ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="my-6 p-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-center"
              >
                <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-600" />
                <p className="font-bold text-sm text-emerald-950">Password Updated</p>
                <p className="text-xs text-emerald-700 mt-1 leading-relaxed">
                  Your password has been changed successfully. Redirecting you to sign in...
                </p>
              </motion.div>
            ) : (
              <form onSubmit={handleSubmit} className="mt-6 space-y-3.5 text-left">
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="New Password (min. 8 characters)"
                    required
                    minLength={8}
                    className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                  />
                </div>

                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm New Password"
                    required
                    minLength={8}
                    className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading || !newPassword || !confirmPassword}
                  className="w-full flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group mt-2"
                >
                  <span>{isLoading ? 'Updating Password...' : 'Reset & Save Password'}</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </form>
            )}

            <p className="text-[10px] text-slate-400 mt-6 leading-relaxed">
              Encrypted using Argon2id with 64MB memory cost protection.
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
