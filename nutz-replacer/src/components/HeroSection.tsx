import React from 'react';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { WordCycle } from './ui/WordCycle';
import { RadiantGrid } from './ui/RadiantGrid';
import { MagneticButton } from './ui/MagneticButton';

interface HeroSectionProps {
  onEnterStudio?: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onEnterStudio,
}) => {
  return (
    <section className="relative overflow-hidden pt-24 pb-16 bg-gradient-to-b from-[#FDFCFB] via-[#F8F7F4] to-[#F3EFEA] border-b border-[#EAE7E0]">
      {/* Sera UI Interactive Radiant Grid & Ambient Lighting */}
      <RadiantGrid />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
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

        {/* Action CTA with Sera UI Magnetic Spring Physics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="flex items-center justify-center"
        >
          <MagneticButton onClick={onEnterStudio} href={!onEnterStudio ? "#tryon-workspace" : undefined}>
            <div className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-9 py-4 rounded-2xl bg-[#171717] hover:bg-[#2A2A38] text-white font-bold text-sm shadow-xl hover:shadow-2xl transition-all duration-300 group cursor-pointer">
              <span>Enter Fitting Studio</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </MagneticButton>
        </motion.div>
      </div>
    </section>
  );
};
