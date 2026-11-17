import React from 'react';
import { Sparkles, ShieldCheck, Palette, Layers, Cpu, Eye } from 'lucide-react';

export const FeatureSection: React.FC = () => {
  const features = [
    {
      icon: <Sparkles className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'AI-Powered Virtual Try-On',
      description: 'Powered exclusively by FLUX-DEV-012 on Nutz Cloud for state-of-the-art diffusion try-on synthesis.',
    },
    {
      icon: <Palette className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'Garment Reference Preservation',
      description: 'Dual-panel spatial conditioning preserves all prints, stripes, character motifs, buttons, and embroidery.',
    },
    {
      icon: <ShieldCheck className="w-5 h-5 text-[#16A34A]" />,
      title: 'Identity-Aware Transformation',
      description: 'Strict anatomical boundary guards lock facial identity, skin tone, hair, shoulder width, and pose.',
    },
    {
      icon: <Layers className="w-5 h-5 text-[#5B3DF0]" />,
      title: '17 Universal Clothing Categories',
      description: 'Pre-configured rules for T-Shirts, Shirts, Blazers, Kurta, Sherwani, Anarkali, Jeans, and Western Dresses.',
    },
    {
      icon: <Cpu className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'Dedicated Dual-Panel Latents',
      description: 'Feeds uncompressed garment visual latents directly into diffusion self-attention without prompt contamination.',
    },
    {
      icon: <Eye className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'Interactive Before/After Slider',
      description: 'Side-by-side and draggable split sliders give you complete transparency over the try-on transformation.',
    },
  ];

  return (
    <section id="features" className="py-20 border-b border-[#E8E8EF] bg-[#F5F4F8] scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs font-bold uppercase tracking-wider text-[#5B3DF0] bg-[#F0EDFD] px-3 py-1 rounded-full border border-[#E8E8EF] mb-3 inline-block">
            Engineering Precision
          </span>
          <h2 className="text-3xl font-extrabold text-[#171717] tracking-tight mb-4">
            Built for High-Precision Fashion
          </h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Unlike generic generative tools, Nutz Replacer is specifically architected to satisfy commercial fashion and e-commerce standards.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl border border-[#E8E8EF] p-6 shadow-subtle hover:border-[#8F77F8] hover:shadow-card transition-all"
            >
              <div className="w-10 h-10 rounded-xl bg-[#F0EDFD] flex items-center justify-center mb-4 border border-[#E8E8EF]">
                {feat.icon}
              </div>
              <h3 className="text-base font-bold text-[#171717] mb-2">
                {feat.title}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {feat.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
