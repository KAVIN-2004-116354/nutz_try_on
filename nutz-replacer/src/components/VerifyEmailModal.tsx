import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle2, RefreshCw, Mail, ArrowRight, ShieldCheck } from 'lucide-react';
import { verifyEmail, resendVerification } from '../services/api';

interface VerifyEmailModalProps {
  isOpen: boolean;
  token?: string | null;
  userEmail?: string;
  onClose: () => void;
  onVerified: () => void;
}

export const VerifyEmailModal: React.FC<VerifyEmailModalProps> = ({
  isOpen,
  token,
  userEmail = '',
  onClose,
  onVerified,
}) => {
  const [status, setStatus] = useState<'verifying' | 'success' | 'failed' | 'idle'>(token ? 'verifying' : 'idle');
  const [resendEmail, setResendEmail] = useState(userEmail);
  const [isResending, setIsResending] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && token) {
      setStatus('verifying');
      setFeedbackMessage(null);
      verifyEmail(token)
        .then(() => {
          setStatus('success');
          onVerified();
        })
        .catch((err) => {
          setStatus('failed');
          setFeedbackMessage(err.message || 'Verification link is invalid or has expired.');
        });
    } else if (isOpen && !token) {
      setStatus('idle');
    }
  }, [isOpen, token]);

  if (!isOpen) return null;

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resendEmail) return;

    setIsResending(true);
    setFeedbackMessage(null);

    try {
      const res = await resendVerification(resendEmail.trim());
      setIsResending(false);
      setFeedbackMessage(res.message || 'If this email is registered, a new verification link has been sent.');
    } catch (err: any) {
      setIsResending(false);
      setFeedbackMessage(err.message || 'Failed to resend verification email.');
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
            {/* 1. Verifying in Progress */}
            {status === 'verifying' && (
              <div className="py-8">
                <RefreshCw className="w-10 h-10 text-indigo-600 animate-spin mx-auto mb-4" />
                <h3 className="text-xl font-serif text-[#171717]">Verifying Email...</h3>
                <p className="text-xs text-slate-500 mt-2">
                  Confirming your cryptographic token with NUTZ security authority.
                </p>
              </div>
            )}

            {/* 2. Verification Success */}
            {status === 'success' && (
              <div className="py-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                </div>
                <h2 className="text-2xl font-serif text-[#171717] tracking-tight">
                  Email Verified
                </h2>
                <p className="text-xs text-slate-600 mt-2 max-w-xs mx-auto leading-relaxed">
                  Your email address has been confirmed. Your fitting memory and personal styling atelier are active.
                </p>
                <button
                  type="button"
                  onClick={onClose}
                  className="w-full mt-6 flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all cursor-pointer"
                >
                  <span>Continue to Fitting Studio</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* 3. Verification Failed or Manual Resend */}
            {(status === 'failed' || status === 'idle') && (
              <div className="py-2">
                <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center">
                  <ShieldCheck className="w-7 h-7 text-amber-700" />
                </div>
                <h2 className="text-2xl font-serif text-[#171717] tracking-tight">
                  {status === 'failed' ? 'Verification Expired' : 'Verify Your Email'}
                </h2>
                <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto leading-relaxed">
                  {status === 'failed'
                    ? 'The verification link may have expired or was already used. Enter your email to receive a new link.'
                    : 'Please verify your email address to unlock private wardrobe persistence.'}
                </p>

                {feedbackMessage && (
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-3 rounded-2xl bg-slate-50 border border-slate-200 text-slate-700 text-xs text-left"
                  >
                    {feedbackMessage}
                  </motion.div>
                )}

                <form onSubmit={handleResend} className="mt-5 space-y-3 text-left">
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={resendEmail}
                      onChange={(e) => setResendEmail(e.target.value)}
                      placeholder="Your registered email address"
                      required
                      className="w-full pl-11 pr-4 py-3 rounded-2xl border border-[#EAE7E0] bg-[#FAF9F6] text-xs text-[#171717] placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#171717] focus:bg-white transition-all font-medium"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isResending || !resendEmail}
                    className="w-full flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white font-bold text-xs shadow-md transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isResending ? 'animate-spin' : ''}`} />
                    <span>{isResending ? 'Sending Link...' : 'Resend Verification Email'}</span>
                  </button>
                </form>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
