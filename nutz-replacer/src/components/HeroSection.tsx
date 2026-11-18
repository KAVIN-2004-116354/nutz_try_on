import React, { useEffect, useRef } from 'react';
import { ArrowRight, ShieldCheck, CheckCircle2, ChevronDown } from 'lucide-react';
import gsap from 'gsap';

export const HeroSection: React.FC = () => {
  const heroRef = useRef<HTMLDivElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  const subtextRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const pillarsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      tl.from(headlineRef.current, {
        y: 40,
        opacity: 0,
        duration: 1,
        delay: 0.1,
      })
      .from(subtextRef.current, {
        y: 25,
        opacity: 0,
        duration: 0.8,
      }, '-=0.6')
      .from(ctaRef.current, {
        y: 20,
        opacity: 0,
        duration: 0.7,
      }, '-=0.5')
      .from(pillarsRef.current ? Array.from(pillarsRef.current.children) : [], {
        y: 20,
        opacity: 0,
        stagger: 0.1,
        duration: 0.8,
      }, '-=0.4');
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section ref={heroRef} className="relative overflow-hidden pt-20 pb-24 bg-gradient-to-b from-[#FDFCFB] via-[#F8F7F4] to-[#F3EFEA] border-b border-[#EAE7E0]">
      {/* Soft warm ambient atelier lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[850px] h-[350px] bg-gradient-to-b from-[#F7F2E8]/70 via-[#EFE7D8]/30 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        {/* Master Headline: High-fashion editorial typography */}
        <h1 
          ref={headlineRef} 
          className="text-5xl sm:text-7xl lg:text-8xl font-serif text-[#171717] tracking-tight leading-[1.05] mb-6 max-w-4xl mx-auto font-normal"
        >
          See Yourself in Any Outfit. <br className="hidden sm:inline" />
          <span className="font-sans font-extrabold italic text-[#171717]">Flawlessly Fitted.</span>
        </h1>

        {/* Editorial Subtitle */}
        <p 
          ref={subtextRef} 
          className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed mb-10 font-normal"
        >
          Upload your portrait and preview how bespoke tailoring, luxury ethnic silks, and modern streetwear drape over your body with authentic photographic realism.
        </p>

        {/* Action CTAs with smooth GSAP button physics */}
        <div ref={ctaRef} className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
          <a
            href="#tryon-workspace"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-2xl bg-[#171717] hover:bg-[#2A2A38] text-white font-bold text-sm shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] group cursor-pointer"
          >
            <span>Enter Fitting Studio</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </a>

          <a
            href="#curated-wardrobe"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-4 rounded-2xl bg-white hover:bg-[#F9F9FC] text-[#171717] font-bold text-sm border border-[#E8E8EF] shadow-sm hover:border-slate-300 transition-all duration-300 hover:scale-[1.01] active:scale-[0.98]"
          >
            <span>Explore Wardrobe</span>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </a>
        </div>

        {/* Real Fashion Standards (No AI buzzwords) */}
        <div ref={pillarsRef} className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-4xl mx-auto text-left">
          <div className="p-4 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm hover:border-[#171717]/20 transition-all">
            <div className="flex items-center gap-2 text-[#16A34A] mb-1.5">
              <ShieldCheck className="w-4 h-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Identity Lock</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">100% Face & Pose Preserved</p>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm hover:border-[#171717]/20 transition-all">
            <div className="flex items-center gap-2 text-[#5B3DF0] mb-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Fabric Truth</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">True Weave & Embroidery</p>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm hover:border-[#171717]/20 transition-all">
            <div className="flex items-center gap-2 text-indigo-600 mb-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Natural Drape</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">Photographic Tension Lines</p>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm hover:border-[#171717]/20 transition-all">
            <div className="flex items-center gap-2 text-slate-700 mb-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Silhouettes</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">17 Dedicated Apparel Cuts</p>
          </div>
        </div>
      </div>
    </section>
  );
};
