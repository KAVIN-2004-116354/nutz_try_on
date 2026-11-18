import React from 'react';
import { ArrowRight, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { WordCycle } from './ui/WordCycle';
import { RadiantGrid } from './ui/RadiantGrid';
import { ShimmerBadge } from './ui/ShimmerBadge';
import { MagneticButton } from './ui/MagneticButton';

export const HeroSection: React.FC = () => {
  return (
    <section className="relative overflow-hidden pt-20 pb-16 bg-gradient-to-b from-[#FDFCFB] via-[#F8F7F4] to-[#F3EFEA] border-b border-[#EAE7E0]">
      {/* Sera UI Interactive Radiant Grid & Ambient Lighting */}
      <RadiantGrid />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        {/* Sera UI Shimmer Border Beam Badge */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="flex justify-center mb-7"
        >
          <ShimmerBadge>
            <span className="w-2 h-2 rounded-full bg-[#16A34A] animate-pulse" />
            <span className="tracking-wider uppercase text-[10px] text-slate-500 font-bold">
              Atelier Fitting Room
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-[11px] text-[#171717] font-semibold">
              Live Drape Simulation
            </span>
          </ShimmerBadge>
        </motion.div>

        {/* Master Headline with Sera UI Kinetic WordCycle */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-5xl sm:text-7xl lg:text-8xl font-serif text-[#171717] tracking-tight leading-[1.06] mb-6 max-w-4xl mx-auto font-normal"
        >
          See Yourself in Any Outfit. <br className="hidden sm:inline" />
          <WordCycle
            words={[
              'Flawlessly Fitted.',
              'Couture Tailored.',
              'Perfect Silhouette.',
              'Bespoke Precision.',
            ]}
            className="font-sans font-extrabold italic text-[#171717]"
          />
        </motion.h1>

        {/* Editorial Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed mb-10 font-normal"
        >
          Upload your portrait and preview how bespoke tailoring, luxury ethnic silks, and modern streetwear drape over your body with authentic photographic realism.
        </motion.p>

        {/* Action CTAs with Sera UI Magnetic Spring Physics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <MagneticButton href="#tryon-workspace">
            <div className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-2xl bg-[#171717] hover:bg-[#2A2A38] text-white font-bold text-sm shadow-xl hover:shadow-2xl transition-all duration-300 group">
              <span>Enter Fitting Studio</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </MagneticButton>

          <MagneticButton href="#curated-wardrobe">
            <div className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-4 rounded-2xl bg-white hover:bg-[#F9F9FC] text-[#171717] font-bold text-sm border border-[#EAE7E0] shadow-sm hover:border-slate-300 transition-all duration-300">
              <span>Explore Wardrobe</span>
              <ChevronDown className="w-4 h-4 text-slate-400 group-hover:translate-y-0.5 transition-transform" />
            </div>
          </MagneticButton>
        </motion.div>
      </div>
    </section>
  );
};
