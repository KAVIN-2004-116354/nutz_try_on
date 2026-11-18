import React from 'react';
import { Scissors, ShieldCheck, Palette, Layers, Compass, Eye } from 'lucide-react';

export const FeatureSection: React.FC = () => {
  const features = [
    {
      icon: <Scissors className="w-5 h-5 text-[#171717]" />,
      title: 'Photorealistic Drape & Tailoring',
      description: 'True-to-life textile drape modeled to exact model anatomy with natural folds, seams, and fabric tension.',
    },
    {
      icon: <Palette className="w-5 h-5 text-[#171717]" />,
      title: 'Garment Weave Retention',
      description: 'Preserves micro-florals, yarn patterns, checks, buttons, embroidery, and silk sheen with microscopic accuracy.',
    },
    {
      icon: <ShieldCheck className="w-5 h-5 text-[#16A34A]" />,
      title: 'Identity & Complexion Lock',
      description: 'Strict anatomical guards lock facial likeness, skin complexion, hair volume, shoulder slope, and natural posture.',
    },
    {
      icon: <Layers className="w-5 h-5 text-[#171717]" />,
      title: '17 Wardrobe Categories',
      description: 'Dedicated fitting heuristics for Oxford Shirts, Tailored Blazers, Knitwear, Sarees, Kurtas, and Outerwear.',
    },
    {
      icon: <Compass className="w-5 h-5 text-[#171717]" />,
      title: 'Precision Stitch Alignment',
      description: 'Maintains collar geometry, sleeve lengths, and garment hems with couture-level alignment.',
    },
    {
      icon: <Eye className="w-5 h-5 text-[#171717]" />,
      title: 'Interactive Fitting Mirror',
      description: 'Draggable 60fps split slider and HD loupe zoom give you complete transparency over fabric draping.',
    },
  ];

  return (
    <section id="features" className="py-24 border-b border-[#EAE7E0] bg-[#F8F7F4] scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="text-xs font-bold uppercase tracking-wider text-[#171717] bg-[#EFECE6] px-3.5 py-1.5 rounded-full border border-black/5 mb-3 inline-block">
            Atelier Standards
          </span>
          <h2 className="text-3xl sm:text-5xl font-serif text-[#171717] tracking-tight mb-4">
            Master Tailoring &amp; Digital Craft
          </h2>
          <p className="text-sm text-slate-500 leading-relaxed font-normal">
            Designed for digital fitting rooms, luxury lookbooks, and modern fashion houses demanding zero compromise on garment truth.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => (
            <div
              key={idx}
              className="bg-white rounded-3xl border border-[#E8E8EF] p-7 shadow-card hover:border-[#171717]/40 hover:shadow-elevated transition-all duration-400 group hover:-translate-y-1"
            >
              <div className="w-12 h-12 rounded-2xl bg-[#F5F4F8] flex items-center justify-center mb-5 border border-[#E8E8EF] group-hover:scale-110 transition-transform shadow-sm">
                {feat.icon}
              </div>
              <h3 className="text-lg font-extrabold text-[#171717] mb-2 group-hover:text-black transition-colors">
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
