import React from 'react';
import { History, ArrowUpRight, Shirt } from 'lucide-react';
import { CloudStatus } from '../types';

interface NavbarProps {
  cloudStatus: CloudStatus;
  historyCount: number;
  onOpenHistory: () => void;
  onOpenSettings?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  historyCount,
  onOpenHistory,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-xl border-b border-[#E8E8EF] transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand: Pure refined human fashion editorial */}
        <a 
          href="#" 
          aria-label="NUTZ home"
          className="flex items-center gap-3 group focus-visible:ring-2 focus-visible:ring-[#171717] focus-visible:outline-none rounded-xl"
        >
          <div className="w-10 h-10 rounded-xl bg-white border border-[#E8E8EF] flex items-center justify-center p-1.5 shadow-sm group-hover:scale-105 transition-transform duration-300">
            <img 
              src="/nutz_acorn_logo.png" 
              alt="NUTZ" 
              className="w-full h-full object-contain"
            />
          </div>
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

        {/* Center Navigation Links - Editorial Fashion */}
        <nav className="hidden md:flex items-center gap-1 p-1 rounded-full bg-[#F5F4F8] border border-[#E8E8EF]">
          <a
            href="#tryon-workspace"
            className="px-5 py-2 text-xs font-bold text-[#171717] hover:bg-white rounded-full transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#171717] shadow-sm"
          >
            Studio
          </a>
          <a
            href="#curated-wardrobe"
            className="px-5 py-2 text-xs font-semibold text-slate-600 hover:text-[#171717] hover:bg-white/60 rounded-full transition-all duration-200"
          >
            Wardrobe
          </a>
          <a
            href="#how-it-works"
            className="px-5 py-2 text-xs font-semibold text-slate-600 hover:text-[#171717] hover:bg-white/60 rounded-full transition-all duration-200"
          >
            Craft & Fit
          </a>
          <a
            href="#features"
            className="px-5 py-2 text-xs font-semibold text-slate-600 hover:text-[#171717] hover:bg-white/60 rounded-full transition-all duration-200"
          >
            Standards
          </a>
        </nav>

        {/* Right Actions: Clean, Minimal, Non-AI */}
        <div className="flex items-center gap-3">
          {/* Gallery / Past Looks Button */}
          <button
            type="button"
            onClick={onOpenHistory}
            className="px-4 py-2 rounded-xl bg-white hover:bg-[#F5F4F8] border border-[#E8E8EF] text-xs font-bold text-[#171717] transition-all flex items-center gap-2 shadow-sm active:scale-95 cursor-pointer"
            title="View Lookbook"
          >
            <History className="w-3.5 h-3.5 text-slate-700" />
            <span>Lookbook</span>
            {historyCount > 0 && (
              <span className="px-1.5 py-0.5 bg-[#171717] text-white rounded-full text-[10px] font-extrabold">
                {historyCount}
              </span>
            )}
          </button>

          {/* E-Commerce Store Demo Link */}
          <a
            href="/demo"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#171717] hover:bg-[#2B2B36] text-white text-xs font-bold transition-all active:scale-95 shadow-sm"
          >
            <Shirt className="w-3.5 h-3.5 text-white/80" />
            <span>Retail Demo</span>
            <ArrowUpRight className="w-3 h-3 opacity-60" />
          </a>
        </div>
      </div>
    </header>
  );
};
