import React from 'react';
import { Upload, Shirt, Wand2, ShieldCheck, Sparkles } from 'lucide-react';

export const HowItWorksSection: React.FC = () => {
  return (
    <section id="how-it-works" className="py-20 border-b border-[#E8E8EF] bg-white scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs font-bold uppercase tracking-wider text-[#5B3DF0] bg-[#F0EDFD] px-3 py-1 rounded-full border border-[#E8E8EF] mb-3 inline-block">
            Simple 3-Step Process
          </span>
          <h2 className="text-3xl font-extrabold text-[#171717] tracking-tight mb-4">
            How Nutz Replacer Works
          </h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Our dual-panel conditioning pipeline separates identity from clothing design, ensuring your face and body anatomy remain unchanged while new outfits drape naturally.
          </p>
        </div>

        {/* 3 Step Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Step 1 */}
          <div className="bg-[#F5F4F8] rounded-2xl border border-[#E8E8EF] p-8 shadow-card flex flex-col justify-between hover:border-[#8F77F8] transition-all group">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-3xl font-extrabold text-[#5B3DF0]/30 font-mono group-hover:text-[#5B3DF0] transition-colors">
                  01
                </span>
                <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-subtle flex items-center justify-center text-[#5B3DF0] group-hover:scale-110 transition-transform">
                  <Upload className="w-6 h-6 stroke-[1.75]" />
                </div>
              </div>
              <h3 className="text-lg font-bold text-[#171717] mb-2">
                Upload Your Photo
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Provide a portrait or full-length photograph. The model preserves your face, skin tone, natural hairstyle, pose, and body anatomy with zero artificial deformation.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-[#E8E8EF] text-[11px] font-semibold text-[#16A34A] flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Identity Source of Truth</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-[#F5F4F8] rounded-2xl border border-[#E8E8EF] p-8 shadow-card flex flex-col justify-between hover:border-[#8F77F8] transition-all group">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-3xl font-extrabold text-[#5B3DF0]/30 font-mono group-hover:text-[#5B3DF0] transition-colors">
                  02
                </span>
                <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-subtle flex items-center justify-center text-[#5B3DF0] group-hover:scale-110 transition-transform">
                  <Shirt className="w-6 h-6 stroke-[1.75]" />
                </div>
              </div>
              <h3 className="text-lg font-bold text-[#171717] mb-2">
                Select Your Outfit
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Upload any flat-lay clothing photo or catalog item. All original printed patterns, geometric motifs, fabric weaves, and embroidery are faithfully captured as visual latents.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-[#E8E8EF] text-[11px] font-semibold text-[#5B3DF0] flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Garment Design Reference</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-[#F5F4F8] rounded-2xl border border-[#E8E8EF] p-8 shadow-card flex flex-col justify-between hover:border-[#8F77F8] transition-all group">
            <div>
              <div className="flex items-center justify-between mb-6">
                <span className="text-3xl font-extrabold text-[#5B3DF0]/30 font-mono group-hover:text-[#5B3DF0] transition-colors">
                  03
                </span>
                <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-subtle flex items-center justify-center text-[#5B3DF0] group-hover:scale-110 transition-transform">
                  <Wand2 className="w-6 h-6 stroke-[1.75]" />
                </div>
              </div>
              <h3 className="text-lg font-bold text-[#171717] mb-2">
                Generate Your New Look
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Click "Generate My Look". FLUX-DEV-012 spatial attention synthesizes natural fabric folds, dynamic lighting, and seamless garment draping onto your body in 1024×1024 HD.
              </p>
            </div>
            <div className="mt-6 pt-4 border-t border-[#E8E8EF] text-[11px] font-semibold text-[#171717] flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#16A34A]" />
              <span>Instant Download & Slider View</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
