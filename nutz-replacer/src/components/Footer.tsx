import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-[#E8E8EF] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-[#E8E8EF]">
          {/* Brand & Tagline */}
          <div className="flex items-center">
            <div>
              <span className="font-extrabold text-[#171717] text-base tracking-tight font-sans">
                NUTZ <span className="text-[#171717]">FITTING ROOM</span>
              </span>
              <p className="text-xs text-slate-500">
                Bespoke Tailoring. Uncompromised Garment Drape.
              </p>
            </div>
          </div>

          {/* Links */}
          <div className="flex flex-wrap items-center gap-6 text-xs font-semibold text-slate-600">
            <a href="#tryon-workspace" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Fitting Studio
            </a>
            <a href="#how-it-works" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Craft &amp; Process
            </a>
            <a href="#features" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Standards
            </a>
            <a href="#gallery" className="hover:text-black transition-colors focus-visible:ring-2 focus-visible:ring-black focus-visible:outline-none rounded">
              Lookbook
            </a>
          </div>
        </div>

        {/* Copyright */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-600 gap-4">
          <p>© {new Date().getFullYear()} NUTZ Fitting Room. All rights reserved.</p>
          <p className="font-mono text-[11px] text-slate-400">
            Precision Fashion Atelier &amp; Virtual Try-On
          </p>
        </div>
      </div>
    </footer>
  );
};
