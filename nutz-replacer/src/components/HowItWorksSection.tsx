import React from 'react';
import { Camera, Shirt, CheckCircle2, ShieldCheck, Eye } from 'lucide-react';

export const HowItWorksSection: React.FC = () => {
  return (
    <section id="how-it-works" className="py-24 border-b border-[#EAE7E0] bg-white scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 block">
            Craft &amp; Tailoring
          </span>
          <h2 className="text-3xl sm:text-5xl font-serif text-[#171717] tracking-tight mb-4">
            The Precision Fitting Process
          </h2>
          <p className="text-sm text-slate-500 leading-relaxed font-normal">
            Every fitting preserves your unique body proportions, facial identity, and posture while accurately simulating how real fabrics fold, tension, and drape.
          </p>
        </div>

        {/* 3 Step Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Step 1 */}
          <div className="bg-[#FAF9F6] rounded-3xl border border-[#EAE7E0] p-8 shadow-card flex flex-col justify-between hover:border-[#171717]/20 hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-sm font-bold uppercase tracking-widest text-slate-400">
                  Step 01
                </span>
                <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm flex items-center justify-center text-[#171717] group-hover:scale-105 transition-transform">
                  <Camera className="w-5 h-5 stroke-[1.8]" />
                </div>
              </div>
              <h3 className="text-xl font-extrabold text-[#171717] mb-2">
                Model & Posture Lock
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                Upload your portrait or full-length photo. Facial geometry, natural hair, skin tone, and body posture are strictly locked as the ground truth.
              </p>
            </div>
            <div className="mt-8 pt-4 border-t border-[#E8E8EF] text-[11px] font-bold text-[#16A34A] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" />
              <span>Anatomical Truth Preserved</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-[#FAF9F6] rounded-3xl border border-[#EAE7E0] p-8 shadow-card flex flex-col justify-between hover:border-[#171717]/20 hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-sm font-bold uppercase tracking-widest text-slate-400">
                  Step 02
                </span>
                <div className="w-12 h-12 rounded-2xl bg-white border border-[#EAE7E0] shadow-sm flex items-center justify-center text-[#171717] group-hover:scale-105 transition-transform">
                  <Shirt className="w-5 h-5 stroke-[1.8]" />
                </div>
              </div>
              <h3 className="text-xl font-extrabold text-[#171717] mb-2">
                Textile Weave &amp; Pattern
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                Choose or upload clothing references. All printed micro-patterns, embroidery textures, buttons, and collar structures are faithfully retained.
              </p>
            </div>
            <div className="mt-8 pt-4 border-t border-[#EAE7E0] text-[11px] font-bold text-[#171717] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
              <span>Fabric Truth Captured</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-[#FAF9F6] rounded-3xl border border-[#EAE7E0] p-8 shadow-card flex flex-col justify-between hover:border-[#171717]/20 hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-sm font-bold uppercase tracking-widest text-slate-400">
                  Step 03
                </span>
                <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm flex items-center justify-center text-[#171717] group-hover:scale-105 transition-transform">
                  <Eye className="w-5 h-5 stroke-[1.8]" />
                </div>
              </div>
              <h3 className="text-xl font-extrabold text-[#171717] mb-2">
                Photographic Drape
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                The outfit is fitted to your posture with natural fabric tension, realistic shadow draping, and crisp high-definition photographic resolution.
              </p>
            </div>
            <div className="mt-8 pt-4 border-t border-[#E8E8EF] text-[11px] font-bold text-[#171717] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
              <span>Interactive Slider Inspection</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
