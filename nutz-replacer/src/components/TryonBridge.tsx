import React from 'react';
import { Sparkles } from 'lucide-react';

interface TryonBridgeProps {
  hasPerson: boolean;
  hasGarment: boolean;
}

export const TryonBridge: React.FC<TryonBridgeProps> = ({ hasPerson, hasGarment }) => {
  const isReady = hasPerson && hasGarment;

  return (
    <div className="flex items-center justify-center my-3">
      <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white border border-[#E8E8EF] shadow-subtle">
        <div className={`flex items-center gap-1.5 text-xs font-semibold ${hasPerson ? 'text-[#16A34A]' : 'text-[#737373]'}`}>
          <span className={`w-2 h-2 rounded-full ${hasPerson ? 'bg-[#16A34A]' : 'bg-gray-300'}`} />
          <span>Person (Identity)</span>
        </div>

        <div className="w-6 h-6 rounded-full bg-[#F0EDFD] text-[#5B3DF0] flex items-center justify-center font-bold text-xs border border-[#E8E8EF]">
          +
        </div>

        <div className={`flex items-center gap-1.5 text-xs font-semibold ${hasGarment ? 'text-[#16A34A]' : 'text-[#737373]'}`}>
          <span className={`w-2 h-2 rounded-full ${hasGarment ? 'bg-[#16A34A]' : 'bg-gray-300'}`} />
          <span>Garment (Design)</span>
        </div>

        <div className="text-gray-300">→</div>

        <div className={`flex items-center gap-1 text-xs font-bold ${isReady ? 'text-[#5B3DF0]' : 'text-[#737373]'}`}>
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI Try-On Synthesis</span>
        </div>
      </div>
    </div>
  );
};
