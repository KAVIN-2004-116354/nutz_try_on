import React, { useRef, useState } from 'react';
import { Upload, RefreshCw, Trash2, CheckCircle2, Sparkles, Layers, SlidersHorizontal } from 'lucide-react';
import { ImageInputState, SamplePreset } from '../types';
import { SAMPLE_GARMENTS, FLUX_17_CATEGORIES, MACRO_CATEGORIES } from '../presets';

interface GarmentUploadCardProps {
  garment: ImageInputState;
  setGarment: React.Dispatch<React.SetStateAction<ImageInputState>>;
  selectedCategory: string;
  setSelectedCategory: (cat: string) => void;
  disabled?: boolean;
  onError: (msg: string) => void;
}

const SUPPORTED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

export const GarmentUploadCard: React.FC<GarmentUploadCardProps> = ({
  garment,
  setGarment,
  selectedCategory,
  setSelectedCategory,
  disabled = false,
  onError,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [showDetailedCategories, setShowDetailedCategories] = useState(false);

  const processFile = (file: File) => {
    if (!SUPPORTED_FORMATS.includes(file.type)) {
      onError('Unsupported image format. Please upload JPG, JPEG, PNG, or WEBP.');
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      onError('File size exceeds 20MB limit. Please upload a smaller image.');
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      setGarment({
        file,
        previewUrl,
        name: file.name.replace(/\.[^/.]+$/, ''),
        isCustom: true,
        aspectRatio: `${img.naturalWidth}:${img.naturalHeight}`,
        resolution: `${img.naturalWidth} × ${img.naturalHeight}px`,
      });
    };
    img.src = previewUrl;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0];
    if (file) processFile(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  const handleRemove = () => {
    setGarment({
      file: null,
      previewUrl: null,
      name: '',
      isCustom: false,
    });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const selectPreset = (sample: SamplePreset) => {
    if (disabled) return;
    setGarment({
      file: null,
      previewUrl: sample.imageUrl,
      name: sample.name,
      isCustom: false,
      resolution: 'Catalog HD',
    });

    // Auto-align category
    if (sample.id.includes('anarkali')) setSelectedCategory('western_dress');
    else if (sample.id.includes('blazer')) setSelectedCategory('blazer');
    else if (sample.id.includes('shirt')) setSelectedCategory('shirt');
    else if (sample.id.includes('black-tee')) setSelectedCategory('t_shirt');
    else if (sample.id.includes('denim')) setSelectedCategory('shirt');
  };

  return (
    <div className="bg-white rounded-2xl border border-[#E8E8EF] shadow-card p-6 flex flex-col justify-between transition-all hover:border-[#8F77F8]/50">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2.5">
            <span className="w-7 h-7 rounded-lg bg-[#F0EDFD] text-[#5B3DF0] font-bold text-xs flex items-center justify-center border border-[#E8E8EF]">
              02
            </span>
            <h3 className="text-base font-bold text-[#171717]">
              Choose Your Outfit
            </h3>
          </div>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#F0EDFD] text-[#5B3DF0] border border-[#E8E8EF]">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Dual-Panel Reference</span>
          </span>
        </div>

        <p className="text-xs text-slate-600 mb-4 leading-relaxed">
          Upload the clothing item you want the person to wear. Authoritative source for pattern, fabric weave, embroidery, and garment silhouette.
        </p>

        {/* Upload Zone / Active Preview */}
        {!garment.previewUrl ? (
          <div
            tabIndex={disabled ? -1 : 0}
            role="button"
            aria-label="Upload garment reference photo by dragging or browsing"
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !disabled && fileInputRef.current?.click()}
            className={`relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[260px] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 focus-visible:outline-none ${isDragging
              ? 'border-[#5B3DF0] bg-[#F0EDFD]/60'
              : 'border-[#E8E8EF] hover:border-[#5B3DF0] bg-[#F5F4F8] hover:bg-[#F0EDFD]/30'
              }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              disabled={disabled}
              className="hidden"
              aria-label="Select garment reference image from computer"
            />
            <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-subtle flex items-center justify-center text-[#5B3DF0] mb-3 group-hover:scale-110 transition-transform">
              <Upload className="w-6 h-6 stroke-[1.75]" />
            </div>
            <p className="text-sm font-bold text-[#171717] mb-1">
              Drag & drop garment image here, or <span className="text-[#5B3DF0] underline underline-offset-2">browse</span>
            </p>
            <p className="text-xs text-slate-600">
              Supports clear flat-lay or catalog photos in JPG, PNG, WEBP
            </p>
          </div>
        ) : (
          <div className="relative rounded-xl overflow-hidden border border-[#E8E8EF] bg-[#F5F4F8] p-3 flex gap-4 items-center">
            {/* Thumbnail */}
            <div className="relative w-28 h-36 rounded-lg overflow-hidden border border-[#E8E8EF] bg-white flex-shrink-0 shadow-subtle flex items-center justify-center p-1.5">
              <img
                src={garment.previewUrl}
                alt={garment.name}
                className="w-full h-full object-contain"
                loading="lazy"
              />
              <div className="absolute top-1.5 left-1.5 px-1.5 py-0.5 rounded bg-black/60 text-white text-[9px] font-mono">
                Pattern Ref
              </div>
            </div>

            {/* Metadata & Actions */}
            <div className="flex-1 min-w-0 flex flex-col justify-between h-36 py-1">
              <div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#16A34A] mb-1">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Garment Reference Ready</span>
                </div>
                <h4 className="text-sm font-bold text-[#171717] truncate" title={garment.name}>
                  {garment.name || 'Custom Garment Reference'}
                </h4>
                <p className="text-xs text-slate-600 mt-0.5 font-mono">
                  {garment.resolution || 'High Definition'}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-2 border-t border-[#E8E8EF]">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={disabled}
                  aria-label="Replace garment reference photo"
                  className="min-h-[38px] px-3.5 py-1.5 rounded-lg text-xs font-semibold text-[#171717] bg-white hover:bg-gray-50 border border-[#E8E8EF] shadow-subtle flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-1 focus-visible:outline-none"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                  <span>Replace</span>
                </button>
                <button
                  type="button"
                  onClick={handleRemove}
                  disabled={disabled}
                  aria-label="Remove garment reference photo"
                  className="min-h-[38px] px-3.5 py-1.5 rounded-lg text-xs font-semibold text-[#DC2626] bg-white hover:bg-red-50 border border-[#E8E8EF] transition-colors flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#DC2626] focus-visible:ring-offset-1 focus-visible:outline-none"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Remove</span>
                </button>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              disabled={disabled}
              className="hidden"
              aria-label="Select garment reference image from computer"
            />
          </div>
        )}

        {/* Section 6: Intelligent Garment Detection & Category Selection */}
        <div className="mt-5 pt-4 border-t border-[#E8E8EF]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-[#5B3DF0]" />
              <span>Garment Category</span>
            </span>
            <button
              type="button"
              onClick={() => setShowDetailedCategories(!showDetailedCategories)}
              className="text-[11px] font-semibold text-[#5B3DF0] hover:underline flex items-center gap-1 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
            >
              <SlidersHorizontal className="w-3 h-3" />
              <span>{showDetailedCategories ? 'Simple View' : 'All 17 Categories'}</span>
            </button>
          </div>

          {!showDetailedCategories ? (
            /* Macro category pills */
            <div className="grid grid-cols-3 gap-1.5">
              {MACRO_CATEGORIES.map((cat) => {
                const isSelected =
                  (cat === 'Upper Body' && ['shirt', 't_shirt', 'polo_t_shirt', 'blazer', 'hoodie'].includes(selectedCategory)) ||
                  (cat === 'Lower Body' && ['jeans', 'formal_trousers', 'shorts', 'dhoti'].includes(selectedCategory)) ||
                  (cat === 'Traditional Wear' && ['kurta', 'sherwani', 'achkan', 'saree', 'lehenga', 'waistcoat'].includes(selectedCategory)) ||
                  (cat === 'Dress' && selectedCategory === 'western_dress');

                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => {
                      if (cat === 'Upper Body') setSelectedCategory('shirt');
                      else if (cat === 'Lower Body') setSelectedCategory('jeans');
                      else if (cat === 'Traditional Wear') setSelectedCategory('kurta');
                      else if (cat === 'Dress') setSelectedCategory('western_dress');
                      else setSelectedCategory('shirt');
                    }}
                    className={`min-h-[36px] px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all text-center truncate cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${isSelected
                      ? 'bg-[#5B3DF0] text-white border-[#5B3DF0] shadow-subtle'
                      : 'bg-[#F5F4F8] hover:bg-gray-100 text-[#171717] border-[#E8E8EF]'
                      }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          ) : (
            /* Detailed 17 Category Dropdown/Selector */
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              aria-label="Select specific garment category"
              className="w-full text-xs font-semibold text-[#171717] bg-white border border-[#E8E8EF] rounded-xl px-3 py-2.5 focus:ring-2 focus:ring-[#5B3DF0] focus:border-transparent outline-none shadow-subtle cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0]"
            >
              {FLUX_17_CATEGORIES.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.id}. {c.name} ({c.macroCategory})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Quick Sample Presets */}
        <div className="mt-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Or choose a sample outfit:
            </span>
          </div>
          <div className="grid grid-cols-5 gap-2">
            {SAMPLE_GARMENTS.map((sample) => {
              const isSelected = garment.previewUrl === sample.imageUrl;
              return (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => selectPreset(sample)}
                  disabled={disabled}
                  aria-label={`Select sample outfit ${sample.name}`}
                  className={`relative rounded-xl overflow-hidden border p-1 text-left transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-1 focus-visible:outline-none ${isSelected
                    ? 'border-[#5B3DF0] ring-2 ring-[#5B3DF0]/20 bg-[#F0EDFD]/40'
                    : 'border-[#E8E8EF] hover:border-gray-300 bg-white'
                    }`}
                  title={sample.name}
                >
                  <div className="aspect-[3/4] rounded-lg overflow-hidden bg-gray-50 flex items-center justify-center p-1 mb-1">
                    <img
                      src={sample.imageUrl}
                      alt={sample.name}
                      className="w-full h-full object-contain"
                      loading="lazy"
                    />
                  </div>
                  <span className="block text-[10px] font-semibold text-[#171717] truncate text-center">
                    {sample.name.split(' ')[0]}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
