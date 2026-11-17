import React from 'react';
import { Sparkles, ShieldCheck, Palette, Layers, Cpu, Eye } from 'lucide-react';

export const FeatureSection: React.FC = () => {
  const features = [
    {
      icon: <Sparkles className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'AI Photorealistic Try-On',
      description: 'Powered by FLUX-DEV-012 for state-of-the-art diffusion try-on synthesis with zero hallucinated silhouettes.',
    },
    {
      icon: <Palette className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'Garment Weave Retention',
      description: 'Dual-panel spatial conditioning preserves exact prints, micro-florals, checks, buttons, and zardozi embroidery.',
    },
    {
      icon: <ShieldCheck className="w-5 h-5 text-[#16A34A]" />,
      title: 'Identity Boundary Lock',
      description: 'Strict MediaPipe landmark guards lock facial identity, skin tone, hair volume, shoulder angle, and stance.',
    },
    {
      icon: <Layers className="w-5 h-5 text-[#5B3DF0]" />,
      title: '17 Fashion Categories',
      description: 'Specialized pipeline heuristics for T-Shirts, Oxford Shirts, Blazers, Kurtas, Sherwanis, Anarkalis, and Sarees.',
    },
    {
      icon: <Cpu className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'Dual-Panel Latents',
      description: 'Feeds uncompressed garment visual latents directly into diffusion self-attention without prompt drift.',
    },
    {
      icon: <Eye className="w-5 h-5 text-[#5B3DF0]" />,
      title: 'Interactive Split Comparison',
      description: 'Draggable 60fps split slider and HD loupe zoom give you complete transparency over fabric draping.',
    },
  ];

  return (
    <section id="features" className="py-24 border-b border-[#E8E8EF] bg-[#F5F4F8] scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs font-extrabold uppercase tracking-wider text-[#5B3DF0] bg-[#F0EDFD] px-3.5 py-1.5 rounded-full border border-[#5B3DF0]/20 mb-3 inline-block">
            Engineering Precision
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight mb-4">
            Commercial Haute-Tech Standards
          </h2>
          <p className="text-sm text-slate-500 leading-relaxed font-normal">
            Unlike generic text-to-image prompts, Nutz Replacer is architected for commercial fashion lookbooks and digital fitting studios.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="bg-white rounded-3xl border border-[#E8E8EF] p-7 shadow-card hover:border-[#5B3DF0]/40 hover:shadow-elevated transition-all duration-400 group hover:-translate-y-1"
            >
              <div className="w-12 h-12 rounded-2xl bg-[#F0EDFD] flex items-center justify-center mb-5 border border-[#5B3DF0]/20 group-hover:scale-110 transition-transform shadow-sm">
                {feat.icon}
              </div>
              <h3 className="text-lg font-extrabold text-[#171717] mb-2 group-hover:text-[#5B3DF0] transition-colors">
                {feat.title}
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed font-medium">
                {feat.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
