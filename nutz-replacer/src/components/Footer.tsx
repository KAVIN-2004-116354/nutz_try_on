import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-[#E8E8EF] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-[#E8E8EF]">
          {/* Logo & Tagline */}
          <div className="flex items-center gap-3.5">
            <div className="h-9 px-2 py-1 rounded-xl bg-[#171717] flex items-center justify-center border border-black/10">
              <img
                src="/nutz_logo_white.png"
                alt="NUTZ Logo"
                className="h-5 w-auto object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/nutz_logo.jpg';
                }}
              />
            </div>
            <div>
              <span className="font-extrabold text-[#171717] text-base tracking-tight font-sans">
                NUTZ <span className="text-[#5B3DF0]">REPLACER</span>
              </span>
              <p className="text-xs text-slate-600">
                Your Style. Your Identity. Reimagined.
              </p>
            </div>
          </div>

          {/* Links */}
          <div className="flex flex-wrap items-center gap-6 text-xs font-semibold text-slate-600">
            <a href="#tryon-workspace" className="hover:text-[#5B3DF0] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded">
              Virtual Try-On
            </a>
            <a href="#how-it-works" className="hover:text-[#5B3DF0] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded">
              How It Works
            </a>
            <a href="#features" className="hover:text-[#5B3DF0] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded">
              Features
            </a>
            <a href="#" className="hover:text-[#5B3DF0] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-[#5B3DF0] transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded">
              Contact
            </a>
          </div>
        </div>

        {/* Copyright */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-600 gap-4">
          <p>© {new Date().getFullYear()} NUTZ REPLACER. All rights reserved.</p>
          <p className="font-mono text-[11px]">
            Powered by FLUX-DEV-012 Cloud Inference
          </p>
        </div>
      </div>
    </footer>
  );
};
