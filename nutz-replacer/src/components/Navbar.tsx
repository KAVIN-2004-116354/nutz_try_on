import React from 'react';
import { Zap, History, Settings } from 'lucide-react';
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
  onOpenSettings,
}) => {
  return (
    <header className="bg-white/95 backdrop-blur-md border-b border-[#E8E8EF] sticky top-0 z-40 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand */}
        <a 
          href="#" 
          aria-label="NUTZ REPLACER home"
          className="flex items-center group focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded-xl"
        >
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-[#171717] text-lg tracking-tight font-sans">
                NUTZ <span className="text-[#5B3DF0]">REPLACER</span>
              </span>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-[#F0EDFD] text-[#5B3DF0] border border-[#E8E8EF]">
                AI Fashion
              </span>
            </div>
            <span className="text-[11px] font-medium text-slate-600 hidden sm:block">
              Your Style. Your Identity. Reimagined.
            </span>
          </div>
        </a>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          <a
            href="#tryon-workspace"
            className="text-sm font-semibold text-[#171717] hover:text-[#5B3DF0] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
          >
            Virtual Try-On
          </a>
          <a
            href="#how-it-works"
            className="text-sm font-medium text-slate-600 hover:text-[#171717] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
          >
            How It Works
          </a>
          <a
            href="#features"
            className="text-sm font-medium text-slate-600 hover:text-[#171717] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
          >
            Features
          </a>
          <button
            type="button"
            onClick={onOpenHistory}
            className="text-sm font-medium text-slate-600 hover:text-[#5B3DF0] transition-colors flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
          >
            <History className="w-4 h-4" />
            <span>Gallery</span>
            {historyCount > 0 && (
              <span className="px-1.5 py-0.2 bg-[#F0EDFD] text-[#5B3DF0] rounded-full text-[10px] font-bold">
                {historyCount}
              </span>
            )}
          </button>
        </nav>

        {/* Right Status & Controls */}
        <div className="flex items-center gap-3">
          {/* FLUX Engine status indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#F5F4F8] border border-[#E8E8EF] text-xs font-semibold text-[#171717] shadow-subtle">
            <span
              className={`w-2 h-2 rounded-full ${
                cloudStatus.status === 'online' ? 'bg-[#16A34A] animate-pulse' : 'bg-amber-500'
              }`}
            />
            <span className="hidden lg:inline text-slate-600 font-normal">Engine:</span>
            <span className="text-[#171717] font-mono text-[11px]">FLUX-DEV-012</span>
          </div>

          {/* Credits / Status Pill */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#F0EDFD] text-[#5B3DF0] text-xs font-bold border border-[#8F77F8]/30">
            <Zap className="w-3.5 h-3.5 fill-[#5B3DF0]" />
            <span>Pro Studio</span>
          </div>

          {/* Settings Trigger if provided */}
          {onOpenSettings && (
            <button
              type="button"
              onClick={onOpenSettings}
              className="p-2 rounded-xl text-slate-600 hover:text-[#171717] hover:bg-[#F5F4F8] border border-[#E8E8EF] transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
              title="Studio Settings"
              aria-label="Studio Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
