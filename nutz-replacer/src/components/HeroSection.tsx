import React, { useState, useEffect } from 'react';
import { ArrowRight, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { WordCycle } from './ui/WordCycle';
import { RadiantGrid } from './ui/RadiantGrid';
import { MagneticButton } from './ui/MagneticButton';

interface HeroSectionProps {
  onEnterStudio?: () => void;
  activeTab?: 'studio' | 'history';
  onTabChange?: (tab: 'studio' | 'history') => void;
  animTrigger?: number;
}

const PREVIEW_OUTFITS = [
  {
    id: 'blazer',
    title: 'Milano Navy Blazer',
    tag: 'Bespoke Tailoring',
    fabric: 'Super 130s Italian Wool',
    fitScore: '99.8%',
    modelName: 'Kabir (Clean Studio Pose)',
    personImg: '/studio/assets/sample_men_clean.jpg',
    garmentImg: '/studio/assets/sample_navy_blazer.jpg',
    resultImg: '/studio/assets/sample_navy_blazer.jpg',
  },
  {
    id: 'anarkali',
    title: 'Royal Emerald Anarkali',
    tag: 'Haute Ethnic Silk',
    fabric: 'Chanderi Handloom Silk',
    fitScore: '99.4%',
    modelName: 'Ananya (Editorial Model)',
    personImg: '/studio/assets/sample_person_female.jpg',
    garmentImg: '/studio/assets/sample_anarkali_dress.jpg',
    resultImg: '/studio/assets/sample_ethnic_anarkali_model.jpg',
  },
  {
    id: 'shirt',
    title: 'Mint Riviera Shirt',
    tag: 'Casual Micro-Print',
    fabric: '100% Breathable Linen Cotton',
    fitScore: '99.6%',
    modelName: 'Dev (Studio Portrait)',
    personImg: '/studio/assets/sample_person_1.jpg',
    garmentImg: '/studio/assets/sample_emerald_shirt.jpg',
    resultImg: '/studio/assets/sample_emerald_shirt.jpg',
  },
];

const PREVIEW_HISTORY = [
  {
    id: 'hist-1',
    title: 'Royal Emerald Silk Anarkali',
    client: 'Ananya',
    tag: 'Haute Ethnic Silk',
    timeAgo: '12m ago',
    img: '/studio/assets/sample_ethnic_anarkali_model.jpg',
    specs: 'Chanderi Handloom • 1024×1024 HD',
  },
  {
    id: 'hist-2',
    title: 'Milano Navy Fitted Blazer',
    client: 'Kabir',
    tag: 'Bespoke Tailoring',
    timeAgo: '34m ago',
    img: '/studio/assets/sample_navy_blazer.jpg',
    specs: 'Italian Wool • 1024×1024 HD',
  },
  {
    id: 'hist-3',
    title: 'Pastel Mint Riviera Shirt',
    client: 'Dev',
    tag: 'Casual Linen Print',
    timeAgo: '1h ago',
    img: '/studio/assets/sample_emerald_shirt.jpg',
    specs: 'Micro-Print • 1024×1024 HD',
  },
];

export const HeroSection: React.FC<HeroSectionProps> = ({
  onEnterStudio,
  activeTab = 'studio',
  animTrigger = 0,
}) => {
  const [selectedOutfit, setSelectedOutfit] = useState(PREVIEW_OUTFITS[0]);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    setIsScanning(true);
    const timer = setTimeout(() => setIsScanning(false), 850);
    return () => clearTimeout(timer);
  }, [selectedOutfit.id, activeTab, animTrigger]);

  return (
    <section className="relative overflow-hidden pt-20 pb-20 bg-gradient-to-b from-[#FDFCFB] via-[#F8F7F4] to-[#F3EFEA] border-b border-[#EAE7E0]">
      {/* Sera UI Interactive Radiant Grid & Ambient Lighting */}
      <RadiantGrid />

      {/* Dynamic Animated Shockwave Ring emanating from top on capsule click */}
      <AnimatePresence>
        <motion.div
          key={`hero-shockwave-${animTrigger}-${activeTab}`}
          initial={{ scale: 0.1, opacity: 0.8, y: -40 }}
          animate={{ scale: 2.8, opacity: 0, y: 0 }}
          transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
          className="absolute top-0 left-1/2 -translate-x-1/2 w-80 h-80 rounded-full border border-[#171717]/20 bg-gradient-to-b from-[#171717]/10 via-[#171717]/3 to-transparent pointer-events-none -z-5"
        />
      </AnimatePresence>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        {/* Master Headline with Sera UI Kinetic WordCycle */}
        <motion.h1
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-4xl sm:text-6xl lg:text-7xl font-serif text-[#171717] tracking-tight leading-[1.08] mb-5 max-w-4xl mx-auto font-normal"
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
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed mb-8 font-normal"
        >
          Upload your portrait and preview how bespoke tailoring, luxury ethnic silks, and modern streetwear drape over your body with authentic photographic realism.
        </motion.p>

        {/* Action CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="flex items-center justify-center mb-12"
        >
          <MagneticButton onClick={onEnterStudio} href={!onEnterStudio ? "#tryon-workspace" : undefined}>
            <div className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-3.5 rounded-2xl bg-[#171717] hover:bg-[#2A2A38] text-white font-bold text-xs uppercase tracking-wider shadow-xl hover:shadow-2xl transition-all duration-300 group cursor-pointer">
              <span>Enter Fitting Studio</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </MagneticButton>
        </motion.div>

        {/* ANIMATED HERO SHOWCASE: Reacts to clicking Studio or LookHistory */}
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {activeTab === 'studio' ? (
              /* TAB 1: STUDIO INTERACTIVE DRESSING STAGE ANIMATION */
              <motion.div
                key={`hero-studio-stage-${animTrigger}`}
                initial={{ opacity: 0, y: 24, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.98 }}
                transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                className="bg-white/90 backdrop-blur-xl border border-[#EAE7E0] rounded-3xl p-5 sm:p-8 shadow-2xl relative overflow-hidden text-left"
              >
                {/* Showcase Header with live outfit selector pills */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#EAE7E0]">
                  <div>
                    <h3 className="text-sm font-extrabold text-[#171717]">
                      Live Studio Simulation
                    </h3>
                    <p className="text-[11px] text-slate-500 font-medium">
                      Instant garment drape &amp; posture synthesis
                    </p>
                  </div>

                  {/* Quick-Select Outfits in Hero */}
                  <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
                    {PREVIEW_OUTFITS.map((outfit) => {
                      const isSel = selectedOutfit.id === outfit.id;
                      return (
                        <button
                          key={outfit.id}
                          type="button"
                          onClick={() => setSelectedOutfit(outfit)}
                          className={`flex-shrink-0 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                            isSel
                              ? 'bg-[#171717] text-white shadow-md'
                              : 'bg-[#FAF9F6] text-slate-600 hover:text-[#171717] hover:bg-[#F2EFE8] border border-[#EAE7E0]'
                          }`}
                        >
                          {isSel && <Check className="w-3 h-3 text-emerald-400" />}
                          <span>{outfit.title}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Main Visual Dressing Stage */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
                  {/* Left: Input Portrait + Garment Pill */}
                  <div className="md:col-span-5 space-y-3">
                    <div className="relative rounded-2xl overflow-hidden border border-[#EAE7E0] bg-[#FAF9F6] shadow-inner aspect-[3/4] max-h-[340px] flex items-center justify-center">
                      <img
                        src={selectedOutfit.personImg}
                        alt={selectedOutfit.modelName}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute bottom-3 left-3 right-3 p-2.5 rounded-xl bg-white/95 backdrop-blur-md border border-[#EAE7E0] shadow-md flex items-center justify-between">
                        <div>
                          <span className="block text-[11px] font-extrabold text-[#171717]">
                            {selectedOutfit.modelName}
                          </span>
                          <span className="block text-[9px] text-slate-500 font-medium">
                            Neutral Studio Light
                          </span>
                        </div>
                        <span className="px-2 py-0.5 rounded-md bg-[#171717]/5 text-[#171717] text-[10px] font-bold">
                          Client
                        </span>
                      </div>
                    </div>

                    {/* Garment Reference Card */}
                    <div className="p-3 rounded-2xl bg-[#FAF9F6] border border-[#EAE7E0] flex items-center gap-3">
                      <img
                        src={selectedOutfit.garmentImg}
                        alt={selectedOutfit.title}
                        className="w-10 h-10 rounded-xl object-cover border border-[#EAE7E0]"
                      />
                      <div className="flex-1">
                        <span className="block text-xs font-bold text-[#171717]">
                          {selectedOutfit.title}
                        </span>
                        <span className="block text-[10px] text-slate-500 font-medium">
                          {selectedOutfit.fabric}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Middle Arrow / Bridge */}
                  <div className="hidden md:flex md:col-span-2 flex-col items-center justify-center">
                    <div className="w-10 h-10 rounded-full bg-[#171717] text-white flex items-center justify-center shadow-lg">
                      <ArrowRight className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400 mt-2">
                      Drape
                    </span>
                  </div>

                  {/* Right: Photorealistic Result with Animated Laser Scan Beam */}
                  <div className="md:col-span-5">
                    <div className="relative rounded-2xl overflow-hidden border-2 border-[#171717]/10 bg-[#FAF9F6] shadow-xl aspect-[3/4] max-h-[340px] flex items-center justify-center group">
                      <img
                        src={selectedOutfit.resultImg}
                        alt={selectedOutfit.title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                      />

                      {/* Animated Laser Drape Scan Beam */}
                      {isScanning && (
                        <motion.div
                          initial={{ top: '-10%' }}
                          animate={{ top: '110%' }}
                          transition={{ duration: 0.85, ease: 'easeInOut' }}
                          className="absolute left-0 right-0 h-16 bg-gradient-to-b from-transparent via-amber-400/35 to-transparent border-b-2 border-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.6)] pointer-events-none z-20"
                        />
                      )}

                      {/* Bottom Info Banner */}
                      <div className="absolute bottom-3 left-3 right-3 p-3 rounded-xl bg-white/95 backdrop-blur-md border border-[#EAE7E0] shadow-md z-10 flex items-center justify-between">
                        <div>
                          <span className="block text-xs font-extrabold text-[#171717]">
                            {selectedOutfit.title}
                          </span>
                          <span className="block text-[10px] text-slate-500 font-medium">
                            {selectedOutfit.tag} • Authentic Weave
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={onEnterStudio}
                          className="px-3 py-1.5 rounded-lg bg-[#171717] hover:bg-[#2B2B38] text-white text-[10px] font-bold transition-colors cursor-pointer"
                        >
                          Try On
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Footer Bar inside Card */}
                <div className="mt-6 pt-4 border-t border-[#EAE7E0] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-4 text-slate-500 text-[11px] font-medium">
                    <span className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      Zero Garment Crease Distortion
                    </span>
                    <span className="hidden sm:inline">•</span>
                    <span className="hidden sm:inline">100% Posture Preservation</span>
                  </div>

                  <button
                    type="button"
                    onClick={onEnterStudio}
                    className="inline-flex items-center gap-2 font-bold text-[#171717] hover:underline cursor-pointer group"
                  >
                    <span>Launch Full Fitting Room Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </motion.div>
            ) : (
              /* TAB 2: LOOKHISTORY 3D GALLERY CASCADE ANIMATION */
              <motion.div
                key={`hero-history-stage-${animTrigger}`}
                initial={{ opacity: 0, y: 24, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.98 }}
                transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                className="bg-white/90 backdrop-blur-xl border border-[#EAE7E0] rounded-3xl p-5 sm:p-8 shadow-2xl relative overflow-hidden text-left"
              >
                {/* Header */}
                <div className="flex items-center justify-between pb-6 border-b border-[#EAE7E0]">
                  <div>
                    <h3 className="text-sm font-extrabold text-[#171717]">
                      LookHistory Recent Atelier Gallery
                    </h3>
                    <p className="text-[11px] text-slate-500 font-medium">
                      Recent bespoke fitting transformations
                    </p>
                  </div>

                  <span className="px-3 py-1 rounded-full bg-[#171717]/5 text-[#171717] text-xs font-bold">
                    3 Looks Logged
                  </span>
                </div>

                {/* 3D Staggered Cards Fan */}
                <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-5">
                  {PREVIEW_HISTORY.map((item, idx) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1, duration: 0.4 }}
                      whileHover={{ y: -4, scale: 1.02 }}
                      className="group bg-[#FAF9F6] border border-[#EAE7E0] hover:border-[#171717] rounded-2xl overflow-hidden shadow-sm transition-all duration-300 flex flex-col justify-between"
                    >
                      <div className="relative aspect-[3/4] overflow-hidden bg-white">
                        <img
                          src={item.img}
                          alt={item.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-full bg-black/70 backdrop-blur-md text-white text-[10px] font-bold">
                          {item.timeAgo}
                        </div>
                      </div>

                      <div className="p-4">
                        <span className="inline-block px-2 py-0.5 rounded bg-white border border-[#EAE7E0] text-[10px] font-bold text-slate-700 mb-1.5">
                          {item.tag}
                        </span>
                        <h4 className="text-xs font-extrabold text-[#171717] line-clamp-1">
                          {item.title}
                        </h4>
                        <p className="text-[10px] text-slate-500 mt-0.5">
                          Client: {item.client} • {item.specs}
                        </p>

                        <button
                          type="button"
                          onClick={onEnterStudio}
                          className="mt-3 w-full py-2 rounded-xl bg-white hover:bg-[#171717] hover:text-white border border-[#EAE7E0] text-[#171717] text-xs font-bold transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5"
                        >
                          <span>Open in Studio</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Footer Bar */}
                <div className="mt-6 pt-4 border-t border-[#EAE7E0] flex items-center justify-between text-xs">
                  <span className="text-slate-500 text-[11px] font-medium">
                    High-Definition 1024×1024 Render Archive
                  </span>
                  <button
                    type="button"
                    onClick={onEnterStudio}
                    className="inline-flex items-center gap-2 font-bold text-[#171717] hover:underline cursor-pointer group"
                  >
                    <span>Create New Look in Studio</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};
