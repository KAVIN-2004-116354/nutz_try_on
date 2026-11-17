import React from 'react';
import { Upload, Shirt, Wand2, ShieldCheck, Sparkles, CheckCircle2 } from 'lucide-react';

export const HowItWorksSection: React.FC = () => {
  return (
    <section id="how-it-works" className="py-24 border-b border-[#E8E8EF] bg-white scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs font-extrabold uppercase tracking-wider text-[#5B3DF0] bg-[#F0EDFD] px-3.5 py-1.5 rounded-full border border-[#5B3DF0]/20 mb-3 inline-block">
            Seamless Architecture
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight mb-4">
            How The Haute-Tech Engine Works
          </h2>
          <p className="text-sm text-slate-500 leading-relaxed font-normal">
            Dual-panel spatial reference conditioning isolates identity from textile design, ensuring facial anatomy and body proportions stay untouched while transferring authentic fabric draping.
          </p>
        </div>

        {/* 3 Step Cards Grid with luxury elevation & animations */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Step 1 */}
          <div className="bg-[#FAF9FD] rounded-3xl border border-[#E8E8EF] p-8 shadow-card flex flex-col justify-between hover:border-[#5B3DF0]/40 hover:shadow-elevated transition-all duration-400 group hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-4xl font-black text-[#5B3DF0]/20 font-mono group-hover:text-[#5B3DF0] transition-colors">
                  01
                </span>
                <div className="w-14 h-14 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm flex items-center justify-center text-[#5B3DF0] group-hover:scale-110 transition-transform">
                  <Upload className="w-6 h-6 stroke-[1.8]" />
                </div>
              </div>
              <h3 className="text-xl font-extrabold text-[#171717] mb-2">
                Model Identity Lock
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                Upload a portrait or editorial photo. 33-point MediaPipe skeletal landmarks preserve facial structure, skin tone, hair, and pose with zero warping.
              </p>
            </div>
            <div className="mt-8 pt-4 border-t border-[#E8E8EF] text-[11px] font-bold text-[#16A34A] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" />
              <span>Identity Truth Locked</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-[#FAF9FD] rounded-3xl border border-[#E8E8EF] p-8 shadow-card flex flex-col justify-between hover:border-[#5B3DF0]/40 hover:shadow-elevated transition-all duration-400 group hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-4xl font-black text-[#5B3DF0]/20 font-mono group-hover:text-[#5B3DF0] transition-colors">
                  02
                </span>
                <div className="w-14 h-14 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm flex items-center justify-center text-[#5B3DF0] group-hover:scale-110 transition-transform">
                  <Shirt className="w-6 h-6 stroke-[1.8]" />
                </div>
              </div>
              <h3 className="text-xl font-extrabold text-[#171717] mb-2">
                Texture Extraction
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                Provide flat-lay, hanger, or catalog apparel. Micro-patterns, embroidery, weave scale, and buttons are encoded into dual-panel latent vectors.
              </p>
            </div>
            <div className="mt-8 pt-4 border-t border-[#E8E8EF] text-[11px] font-bold text-[#5B3DF0] flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              <span>Pixel-Conditioned Reference</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-[#FAF9FD] rounded-3xl border border-[#E8E8EF] p-8 shadow-card flex flex-col justify-between hover:border-[#5B3DF0]/40 hover:shadow-elevated transition-all duration-400 group hover:-translate-y-1">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-4xl font-black text-[#5B3DF0]/20 font-mono group-hover:text-[#5B3DF0] transition-colors">
                  03
                </span>
                <div className="w-14 h-14 rounded-2xl bg-white border border-[#E8E8EF] shadow-sm flex items-center justify-center text-[#5B3DF0] group-hover:scale-110 transition-transform">
                  <Wand2 className="w-6 h-6 stroke-[1.8]" />
                </div>
              </div>
              <h3 className="text-xl font-extrabold text-[#171717] mb-2">
                Diffusion Synthesis
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                FLUX-DEV-012 bidirectional spatial attention synthesizes natural textile folds, realistic tension lines, and studio illumination in 1024×1024 HD.
              </p>
            </div>
            <div className="mt-8 pt-4 border-t border-[#E8E8EF] text-[11px] font-bold text-[#171717] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
              <span>1024×1024 Photorealistic Master</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
