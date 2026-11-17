import React from 'react';
import { Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';

interface TryonBridgeProps {
  hasPerson: boolean;
  hasGarment: boolean;
}

export const TryonBridge: React.FC<TryonBridgeProps> = ({ hasPerson, hasGarment }) => {
  const isReady = hasPerson && hasGarment;

  return (
    <div className="flex items-center justify-center my-3 relative">
      <div className={`flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-white border transition-all duration-400 shadow-sm ${
        isReady ? 'border-[#5B3DF0]/40 shadow-glow-sm' : 'border-[#E8E8EF]'
      }`}>
        {/* Person Node */}
        <div className={`flex items-center gap-1.5 text-xs font-bold transition-colors ${
          hasPerson ? 'text-[#16A34A]' : 'text-slate-400'
        }`}>
          {hasPerson ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A]" />
          ) : (
            <span className="w-2 h-2 rounded-full bg-slate-300" />
          )}
          <span>Model Locked</span>
        </div>

        {/* Plus Operator */}
        <div className={`w-6 h-6 rounded-xl flex items-center justify-center font-extrabold text-xs transition-colors ${
          isReady ? 'bg-[#5B3DF0] text-white shadow-sm' : 'bg-[#F0EDFD] text-[#5B3DF0]'
        }`}>
          +
        </div>

        {/* Garment Node */}
        <div className={`flex items-center gap-1.5 text-xs font-bold transition-colors ${
          hasGarment ? 'text-[#16A34A]' : 'text-slate-400'
        }`}>
          {hasGarment ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A]" />
          ) : (
            <span className="w-2 h-2 rounded-full bg-slate-300" />
          )}
          <span>Outfit Locked</span>
        </div>

        {/* Arrow with pulse */}
        <ArrowRight className={`w-3.5 h-3.5 transition-transform ${
          isReady ? 'text-[#5B3DF0] translate-x-0.5' : 'text-slate-300'
        }`} />

        {/* Target Stage */}
        <div className={`flex items-center gap-1 text-xs font-extrabold transition-all ${
          isReady ? 'text-[#5B3DF0] scale-105' : 'text-slate-400'
        }`}>
          <Sparkles className={`w-3.5 h-3.5 ${isReady ? 'animate-spin text-[#5B3DF0]' : ''}`} style={{ animationDuration: '4s' }} />
          <span>Synthesis Ready</span>
        </div>
      </div>
    </div>
  );
};
