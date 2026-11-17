import React from 'react';
import { History, Sparkles, Store, Cpu, ArrowUpRight } from 'lucide-react';
import { CloudStatus } from '../types';

interface NavbarProps {
  cloudStatus: CloudStatus;
  historyCount: number;
  onOpenHistory: () => void;
  onOpenSettings?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  cloudStatus,
  historyCount,
  onOpenHistory,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-white/85 backdrop-blur-xl border-b border-[#E8E8EF]/80 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand */}
        <a 
          href="#" 
          aria-label="NUTZ REPLACER home"
          className="flex items-center group focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded-2xl"
        >
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-[#171717] text-lg sm:text-xl tracking-tight font-sans">
                NUTZ <span className="text-[#5B3DF0]">REPLACER</span>
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-[#F0EDFD] text-[#5B3DF0] border border-[#5B3DF0]/20 shadow-sm">
                <Sparkles className="w-2.5 h-2.5 animate-spin text-[#5B3DF0]" style={{ animationDuration: '6s' }} />
                <span>Haute-AI</span>
              </span>
            </div>
            <span className="text-[11px] font-medium text-slate-500 hidden sm:block tracking-wide">
              Your Style. Your Identity. Reimagined.
            </span>
          </div>
        </a>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-1.5 p-1.5 rounded-full bg-[#F5F4F8] border border-[#E8E8EF]">
          <a
            href="#tryon-workspace"
            className="px-4 py-2 text-xs font-bold text-[#171717] hover:text-[#5B3DF0] hover:bg-white rounded-full transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#5B3DF0] shadow-sm"
          >
            Atelier Studio
          </a>
          <a
            href="#how-it-works"
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-[#171717] hover:bg-white/60 rounded-full transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#5B3DF0]"
          >
            How It Works
          </a>
          <a
            href="#features"
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-[#171717] hover:bg-white/60 rounded-full transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#5B3DF0]"
          >
            Capabilities
          </a>
        </nav>

        {/* Right Status & Controls */}
        <div className="flex items-center gap-3">
          {/* FLUX Engine status indicator with luminous pulse */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-[#E8E8EF] text-xs font-semibold text-[#171717] shadow-sm hover:border-[#5B3DF0]/40 transition-colors">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                cloudStatus.status === 'online' ? 'bg-[#16A34A]' : 'bg-amber-400'
              }`} />
              <span className={`relative inline-flex rounded-full h-2 w-2 ${
                cloudStatus.status === 'online' ? 'bg-[#16A34A]' : 'bg-amber-500'
              }`} />
            </span>
            <Cpu className="w-3.5 h-3.5 text-slate-400 hidden sm:inline" />
            <span className="font-mono text-[11px] font-bold text-slate-800">FLUX-DEV-012</span>
          </div>

          {/* Gallery Button */}
          <button
            type="button"
            onClick={onOpenHistory}
            className="relative px-3.5 py-2 rounded-xl bg-white hover:bg-[#F5F4F8] border border-[#E8E8EF] text-xs font-bold text-[#171717] hover:text-[#5B3DF0] transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
            title="View Lookbook Gallery"
          >
            <History className="w-3.5 h-3.5 text-[#5B3DF0]" />
            <span className="hidden sm:inline">Lookbook</span>
            {historyCount > 0 && (
              <span className="ml-0.5 px-1.5 py-0.2 bg-[#5B3DF0] text-white rounded-full text-[10px] font-extrabold animate-pulse">
                {historyCount}
              </span>
            )}
          </button>

          {/* Store Demo Link */}
          <a
            href="/demo"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#F0EDFD] hover:bg-[#E3DCFC] border border-[#5B3DF0]/20 text-xs font-bold text-[#5B3DF0] transition-all active:scale-95 shadow-sm"
          >
            <Store className="w-3.5 h-3.5" />
            <span>Store Demo</span>
            <ArrowUpRight className="w-3 h-3 opacity-60" />
          </a>
        </div>
      </div>
    </header>
  );
};
