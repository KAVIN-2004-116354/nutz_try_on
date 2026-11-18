import React from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';

interface TryonBridgeProps {
  hasPerson: boolean;
  hasGarment: boolean;
}

export const TryonBridge: React.FC<TryonBridgeProps> = ({ hasPerson, hasGarment }) => {
  const isReady = hasPerson && hasGarment;

  return (
    <div className="flex items-center justify-center my-3 relative">
      <div className={`flex items-center gap-3 px-5 py-2.5 rounded-2xl bg-white border transition-all duration-300 shadow-sm ${
        isReady ? 'border-[#171717] shadow-md' : 'border-[#E8E8EF]'
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

        {/* Separator */}
        <div className="text-slate-300 font-medium">+</div>

        {/* Garment Node */}
        <div className={`flex items-center gap-1.5 text-xs font-bold transition-colors ${
          hasGarment ? 'text-[#16A34A]' : 'text-slate-400'
        }`}>
          {hasGarment ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A]" />
          ) : (
            <span className="w-2 h-2 rounded-full bg-slate-300" />
          )}
          <span>Outfit Selected</span>
        </div>

        {/* Arrow */}
        <ArrowRight className={`w-3.5 h-3.5 transition-transform ${
          isReady ? 'text-[#171717] translate-x-0.5' : 'text-slate-300'
        }`} />

        {/* Target Stage */}
        <div className={`text-xs font-extrabold transition-all ${
          isReady ? 'text-[#171717]' : 'text-slate-400'
        }`}>
          <span>Ready to Fit</span>
        </div>
      </div>
    </div>
  );
};
