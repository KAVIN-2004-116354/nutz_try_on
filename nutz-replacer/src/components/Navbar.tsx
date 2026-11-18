import React from 'react';
import { motion } from 'framer-motion';
import { History, User, LogOut } from 'lucide-react';
import { CloudStatus } from '../types';

interface NavbarProps {
  cloudStatus: CloudStatus;
  historyCount: number;
  currentPage?: 'home' | 'studio' | 'history';
  onNavigate?: (page: 'home' | 'studio' | 'history') => void;
  onOpenHistory?: () => void;
  onOpenSettings?: () => void;
  onOpenSignIn?: () => void;
  user?: { email: string; name: string } | null;
  onSignOut?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  historyCount,
  currentPage = 'home',
  onNavigate,
  onOpenHistory,
  onOpenSignIn,
  user,
  onSignOut,
}) => {
  const handleTabClick = (tabId: 'studio' | 'history') => {
    if (onNavigate) {
      onNavigate(tabId);
    } else if (tabId === 'history' && onOpenHistory) {
      onOpenHistory();
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-xl border-b border-[#E8E8EF] transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand: Pure refined human fashion editorial with Acorn Logo */}
        <a 
          href="#" 
          onClick={(e) => {
            e.preventDefault();
            onNavigate?.('home');
          }}
          aria-label="NUTZ home"
          className="flex items-center gap-3 group focus-visible:ring-2 focus-visible:ring-[#171717] focus-visible:outline-none rounded-xl cursor-pointer"
        >
          <motion.div 
            whileHover={{ scale: 1.08, rotate: 2 }}
            whileTap={{ scale: 0.94 }}
            className="w-10 h-10 rounded-xl bg-white border border-[#E8E8EF] flex items-center justify-center p-1.5 shadow-sm"
          >
            <img 
              src="/nutz_acorn_logo.png" 
              alt="NUTZ" 
              className="w-full h-full object-contain"
            />
          </motion.div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-[#171717] text-xl tracking-tight font-sans">
                NUTZ
              </span>
              <span className="text-[11px] font-semibold tracking-widest uppercase text-slate-400">
                Fitting Room
              </span>
            </div>
            <span className="text-[11px] font-medium text-slate-500 hidden sm:block tracking-normal">
              High-Fidelity Virtual Dressing Studio
            </span>
          </div>
        </a>

        {/* Center Navigation Links: Merged Studio & LookHistory with Sliding Morph Pill */}
        <nav className="hidden md:flex items-center gap-1 p-1 rounded-full bg-[#F5F4F8] border border-[#E8E8EF] relative shadow-sm">
          {/* Studio Tab */}
          <motion.button
            type="button"
            onClick={() => handleTabClick('studio')}
            whileTap={{ scale: 0.94 }}
            whileHover={{ scale: 1.02 }}
            className={`relative px-5 py-2 text-xs font-bold rounded-full transition-colors duration-200 z-10 select-none cursor-pointer ${
              currentPage === 'studio' ? 'text-[#171717]' : 'text-slate-600 hover:text-[#171717]'
            }`}
          >
            {currentPage === 'studio' && (
              <motion.div
                layoutId="navbar-active-pill"
                transition={{
                  type: 'spring',
                  stiffness: 420,
                  damping: 32,
                }}
                className="absolute inset-0 bg-white rounded-full shadow-sm border border-black/5 -z-10"
              />
            )}
            <span>Studio</span>
          </motion.button>

          {/* LookHistory Tab */}
          <motion.button
            type="button"
            onClick={() => handleTabClick('history')}
            whileTap={{ scale: 0.94 }}
            whileHover={{ scale: 1.02 }}
            className={`relative flex items-center gap-2 px-5 py-2 text-xs font-bold rounded-full transition-colors duration-200 z-10 select-none cursor-pointer ${
              currentPage === 'history' ? 'text-[#171717]' : 'text-slate-600 hover:text-[#171717]'
            }`}
          >
            {currentPage === 'history' && (
              <motion.div
                layoutId="navbar-active-pill"
                transition={{
                  type: 'spring',
                  stiffness: 420,
                  damping: 32,
                }}
                className="absolute inset-0 bg-white rounded-full shadow-sm border border-black/5 -z-10"
              />
            )}
            <History className="w-3.5 h-3.5 text-slate-700" />
            <span>LookHistory</span>
            {historyCount > 0 && (
              <span className="px-1.5 py-0.2 bg-[#171717] text-white rounded-full text-[10px] font-extrabold">
                {historyCount}
              </span>
            )}
          </motion.button>
        </nav>

        {/* Right Actions: Sign In Button */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#FAF9F6] border border-[#E8E8EF]">
                <div className="w-6 h-6 rounded-full bg-[#171717] text-white flex items-center justify-center text-[10px] font-bold">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <span className="text-xs font-bold text-[#171717] max-w-[120px] truncate hidden sm:inline">
                  {user.name}
                </span>
              </div>
              <button
                type="button"
                onClick={onSignOut}
                title="Sign out"
                aria-label="Sign out"
                className="p-2 rounded-full hover:bg-slate-100 text-slate-500 hover:text-red-600 transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <motion.button
              type="button"
              onClick={onOpenSignIn}
              whileHover={{ y: -1, scale: 1.02 }}
              whileTap={{ scale: 0.96 }}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#171717] hover:bg-[#2B2B38] text-white text-xs font-bold transition-all shadow-sm hover:shadow-md cursor-pointer"
            >
              <User className="w-3.5 h-3.5 text-white/90" />
              <span>Sign In</span>
            </motion.button>
          )}
        </div>
      </div>
    </header>
  );
};
