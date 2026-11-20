import React from 'react';
import { motion } from 'framer-motion';

const BRANDS = [
  'Allen Solly',
  'Louis Philippe',
  'U.S. Polo Assn.',
  'Van Heusen',
  'Peter England',
  'Raymond',
  'Zara',
  "Levi's",
  'Tommy Hilfiger',
  'Calvin Klein',
  'Manyavar',
  'FabIndia',
];

export const LuxuryMarquee: React.FC = () => {
  return (
    <div className="relative w-full py-4 overflow-hidden border-y border-[#EAE7E0] bg-[#FAF9F6]/80 backdrop-blur-sm">
      {/* Side Fade Gradients */}
      <div className="absolute left-0 inset-y-0 w-24 bg-gradient-to-r from-[#FAF9F6] to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 inset-y-0 w-24 bg-gradient-to-l from-[#FAF9F6] to-transparent z-10 pointer-events-none" />

      {/* Infinite Scrolling Track */}
      <motion.div
        animate={{ x: ['0%', '-50%'] }}
        transition={{
          repeat: Infinity,
          ease: 'linear',
          duration: 28,
        }}
        className="flex items-center gap-8 whitespace-nowrap will-change-transform"
      >
        {[...BRANDS, ...BRANDS].map((brand, idx) => (
          <div key={idx} className="flex items-center gap-8 group">
            <span className="text-xs font-semibold tracking-widest uppercase text-slate-500 hover:text-[#171717] transition-colors cursor-default">
              {brand}
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#171717]/20 group-hover:bg-[#171717] transition-colors" />
          </div>
        ))}
      </motion.div>
    </div>
  );
};
