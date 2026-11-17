import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Check, Shield } from 'lucide-react';

export const IdentityGuidancePanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="glass-card rounded-2xl p-4 shadow-card hover:border-purple-500/30 transition-all duration-300 h-full flex flex-col justify-center">
      <div 
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-600 to-amber-500 text-white flex items-center justify-center shadow-sm">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <span className="font-bold text-white block font-mono text-xs uppercase tracking-wide flex items-center gap-1.5">
              Identity Guard
              <span className="text-[10px] px-1.5 py-0.2 rounded font-sans font-medium text-emerald-300 bg-emerald-500/10 border border-emerald-500/20">
                100% Protected
              </span>
            </span>
            <span className="text-[11px] text-slate-400 font-sans">
              Face, skin tone, hair &amp; pose locked
            </span>
          </div>
        </div>

        <button 
          type="button" 
          className="text-slate-400 hover:text-white transition-colors p-1"
          aria-label="Toggle details"
        >
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isOpen && (
        <div className="mt-3.5 pt-3.5 border-t border-white/10 text-[11px] space-y-2 text-slate-300 animate-fadeIn">
          <p className="font-medium text-slate-200">
            MediaPipe landmark shields strictly protect identity during FLUX synthesis:
          </p>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 pl-0.5">
            <li className="flex items-center gap-1.5 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span><strong>Face &amp; Eyes:</strong> Strict Identity Mask</span>
            </li>
            <li className="flex items-center gap-1.5 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span><strong>Skin Tone &amp; Hair:</strong> True-to-Life Lock</span>
            </li>
            <li className="flex items-center gap-1.5 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span><strong>Anatomy &amp; Hands:</strong> Namaste/Pose Guard</span>
            </li>
            <li className="flex items-center gap-1.5 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span><strong>Natural Drape:</strong> Realistic Seams &amp; Folds</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};
