import React from 'react';
import { motion } from 'framer-motion';

const FABRICS = [
  'Mulberry Silk',
  'Italian Wool',
  'Japanese Selvedge Denim',
  'Belgian Linen',
  'Royal Velvet',
  'Oxford Pima Cotton',
  'Brocade Weave',
  'Satin Charmeuse',
  'Zardozi Embroidery',
  'Fine Cashmere',
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
        {[...FABRICS, ...FABRICS].map((fabric, idx) => (
          <div key={idx} className="flex items-center gap-8 group">
            <span className="text-xs font-semibold tracking-widest uppercase text-slate-500 hover:text-[#171717] transition-colors cursor-default">
              {fabric}
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#171717]/20 group-hover:bg-[#171717] transition-colors" />
          </div>
        ))}
      </motion.div>
    </div>
  );
};
