import React from 'react';
import { ArrowRight, Sparkles, ShieldCheck, Palette, Cpu, Zap } from 'lucide-react';

export const HeroSection: React.FC = () => {
  return (
    <section className="relative overflow-hidden pt-14 pb-16 bg-gradient-to-b from-[#FAF9FD] via-[#F5F4F8] to-[#F5F4F8] border-b border-[#E8E8EF]">
      {/* Dynamic Animated Aurora Ambient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[840px] h-[340px] bg-gradient-to-tr from-[#E8E1FD] via-[#F0EDFD] to-[#FAF9FD] rounded-full blur-3xl pointer-events-none -z-10 animate-aurora" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
        {/* Top Feature Pill with smooth pulse */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/90 backdrop-blur-md border border-[#E8E8EF] shadow-sm mb-6 hover:border-[#5B3DF0]/40 transition-all duration-300">
          <Sparkles className="w-4 h-4 text-[#5B3DF0] animate-pulse" />
          <span className="text-xs font-bold text-[#171717] tracking-tight">
            Next-Gen Photorealistic Virtual Try-On
          </span>
          <span className="text-gray-300">•</span>
          <span className="text-xs font-semibold text-[#5B3DF0] flex items-center gap-1">
            <Zap className="w-3 h-3 fill-current" />
            FLUX Dual-Panel Latents
          </span>
        </div>

        {/* Master Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#171717] tracking-tight leading-[1.12] mb-5 max-w-4xl mx-auto">
          Every Garment. Any Model. <br className="hidden sm:inline" />
          <span className="text-[#5B3DF0] relative inline-block">
            Flawlessly Fitted.
            {/* Soft underline accent glow */}
            <span className="absolute left-0 bottom-1 w-full h-1 bg-[#5B3DF0]/20 rounded-full" />
          </span>
        </h1>

        {/* Editorial Subtitle */}
        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed mb-9 font-normal">
          Transfer luxury ethnic silks, tailored streetwear, and runway lookbooks onto any person with 
          100% anatomical identity lock and zero pattern distortion.
        </p>

        {/* Action CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-12">
          <a
            href="#tryon-workspace"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-2xl bg-[#5B3DF0] hover:bg-[#4B2EE0] text-white font-bold text-sm shadow-elevated shadow-glow-purple hover:shadow-glow-purple transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 relative overflow-hidden group"
          >
            {/* Shimmer slide effect on hover */}
            <span className="absolute inset-0 w-1/2 h-full bg-white/20 skew-x-12 -translate-x-full group-hover:animate-shimmer-slide pointer-events-none" />
            <Sparkles className="w-4 h-4" />
            <span>Open Studio Canvas</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </a>

          <a
            href="#how-it-works"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-4 rounded-2xl bg-white hover:bg-[#F9F9FC] text-[#171717] font-bold text-sm border border-[#E8E8EF] shadow-card hover:border-slate-300 transition-all duration-300 hover:scale-[1.01] active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-[#5B3DF0]"
          >
            <span>See The Science</span>
          </a>
        </div>

        {/* Micro-Trust Pillars with elegant micro-cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-4xl mx-auto text-left">
          <div className="p-3.5 rounded-2xl bg-white/80 backdrop-blur-sm border border-[#E8E8EF] shadow-subtle hover:border-[#5B3DF0]/30 transition-all">
            <div className="flex items-center gap-2 text-[#16A34A] mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Identity Lock</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">100% Face & Pose Preserved</p>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/80 backdrop-blur-sm border border-[#E8E8EF] shadow-subtle hover:border-[#5B3DF0]/30 transition-all">
            <div className="flex items-center gap-2 text-[#5B3DF0] mb-1">
              <Palette className="w-4 h-4" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Fabric Fidelity</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">Embroidery & Weave Retention</p>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/80 backdrop-blur-sm border border-[#E8E8EF] shadow-subtle hover:border-[#5B3DF0]/30 transition-all">
            <div className="flex items-center gap-2 text-indigo-600 mb-1">
              <Cpu className="w-4 h-4" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Resolution</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">1024×1024 Studio Master</p>
          </div>

          <div className="p-3.5 rounded-2xl bg-white/80 backdrop-blur-sm border border-[#E8E8EF] shadow-subtle hover:border-[#5B3DF0]/30 transition-all">
            <div className="flex items-center gap-2 text-amber-500 mb-1">
              <Sparkles className="w-4 h-4" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">17 Categories</span>
            </div>
            <p className="text-xs font-bold text-[#171717]">Western, Streetwear & Indian Ethnic</p>
          </div>
        </div>
      </div>
    </section>
  );
};
