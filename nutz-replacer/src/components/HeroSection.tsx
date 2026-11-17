import React from 'react';
import { ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';

export const HeroSection: React.FC = () => {
  return (
    <section className="relative overflow-hidden pt-12 pb-14 border-b border-[#E8E8EF] bg-gradient-to-b from-white via-[#F5F4F8] to-[#F5F4F8]">
      {/* Subtle ambient lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[720px] h-[300px] bg-gradient-to-b from-[#F0EDFD] to-transparent rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Top Feature Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-[#E8E8EF] shadow-subtle mb-6">
          <Sparkles className="w-4 h-4 text-[#5B3DF0]" />
          <span className="text-xs font-semibold text-[#171717]">
            Dedicated AI Virtual Try-On Platform
          </span>
          <span className="text-gray-300">•</span>
          <span className="text-xs font-medium text-[#5B3DF0]">
            FLUX-DEV-012 Inpainting
          </span>
        </div>

        {/* Headline - Solid high-contrast typography per Impeccable craft floor */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#171717] tracking-tight leading-[1.15] mb-5">
          Experience Your <span className="text-[#5B3DF0]">Next Look</span>.
        </h1>

        {/* Supporting Description - WCAG AA compliant text-slate-600 (contrast > 5.8:1) */}
        <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed mb-8">
          Upload your photo, choose any outfit, and let AI bring your style to life. 
          Conditioned directly on your clothing reference with strict identity and pose preservation.
        </p>

        {/* CTAs with explicit keyboard focus-visible rings */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 mb-10">
          <a
            href="#tryon-workspace"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-[#5B3DF0] hover:bg-[#4B2EE0] active:bg-[#4D31C7] text-white font-semibold text-sm shadow-premium transition-all hover:scale-[1.01] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 focus-visible:outline-none"
          >
            <span>Start Virtual Try-On</span>
            <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="#how-it-works"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-gray-50 text-[#171717] font-semibold text-sm border border-[#E8E8EF] shadow-subtle transition-all focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 focus-visible:outline-none"
          >
            <span>Explore How It Works</span>
          </a>
        </div>

        {/* Micro-Trust Badges */}
        <div className="flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-xs text-slate-600 pt-4 border-t border-[#E8E8EF]/60">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
            <span className="font-semibold text-[#171717]">Identity & Face Locked</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
            <span className="font-semibold text-[#171717]">Garment Patterns Preserved</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
            <span className="font-semibold text-[#171717]">Photorealistic 1024×1024 HD</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
            <span className="font-semibold text-[#171717]">Pure FLUX Dual-Panel Latents</span>
          </div>
        </div>
      </div>
    </section>
  );
};
