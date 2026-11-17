import React, { useRef, useState } from 'react';
import { Upload, RefreshCw, Trash2, CheckCircle2, ShieldCheck } from 'lucide-react';
import { ImageInputState, SamplePreset } from '../types';
import { SAMPLE_PERSONS } from '../presets';

interface PersonUploadCardProps {
  person: ImageInputState;
  setPerson: React.Dispatch<React.SetStateAction<ImageInputState>>;
  disabled?: boolean;
  onError: (msg: string) => void;
}

const SUPPORTED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

export const PersonUploadCard: React.FC<PersonUploadCardProps> = ({
  person,
  setPerson,
  disabled = false,
  onError,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

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
      setPerson({
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
    setPerson({
      file: null,
      previewUrl: null,
      name: '',
      isCustom: false,
    });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const selectPreset = (sample: SamplePreset) => {
    if (disabled) return;
    setPerson({
      file: null,
      previewUrl: sample.imageUrl,
      name: sample.name,
      isCustom: false,
      resolution: 'Studio Portrait HD',
    });
  };

  return (
    <div className="bg-white rounded-2xl border border-[#E8E8EF] shadow-card p-6 flex flex-col justify-between transition-all hover:border-[#8F77F8]/50">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2.5">
            <span className="w-7 h-7 rounded-lg bg-[#F0EDFD] text-[#5B3DF0] font-bold text-xs flex items-center justify-center border border-[#E8E8EF]">
              01
            </span>
            <h3 className="text-base font-bold text-[#171717]">
              Upload Your Photo
            </h3>
          </div>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#F0EDFD] text-[#5B3DF0] border border-[#E8E8EF]">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Identity Protected</span>
          </span>
        </div>

        <p className="text-xs text-slate-600 mb-4 leading-relaxed">
          Choose a clear photo of the person you want to transform. This image is the authoritative source for face, skin tone, hair, and body proportions.
        </p>

        {/* Upload Zone / Active Preview */}
        {!person.previewUrl ? (
          <div
            tabIndex={disabled ? -1 : 0}
            role="button"
            aria-label="Upload target person photo by dragging or browsing"
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
            className={`relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[260px] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 focus-visible:outline-none ${
              isDragging
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
              aria-label="Select target person photograph from computer"
            />
            <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] shadow-subtle flex items-center justify-center text-[#5B3DF0] mb-3 group-hover:scale-110 transition-transform">
              <Upload className="w-6 h-6 stroke-[1.75]" />
            </div>
            <p className="text-sm font-bold text-[#171717] mb-1">
              Drag & drop your photo here, or <span className="text-[#5B3DF0] underline underline-offset-2">browse</span>
            </p>
            <p className="text-xs text-slate-600">
              Supports high-resolution JPG, PNG, WEBP (up to 20MB)
            </p>
          </div>
        ) : (
          <div className="relative rounded-xl overflow-hidden border border-[#E8E8EF] bg-[#F5F4F8] p-3 flex gap-4 items-center">
            {/* Thumbnail */}
            <div className="relative w-28 h-36 rounded-lg overflow-hidden border border-[#E8E8EF] bg-white flex-shrink-0 shadow-subtle">
              <img
                src={person.previewUrl}
                alt={person.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
              <div className="absolute top-1.5 left-1.5 px-1.5 py-0.5 rounded bg-black/60 text-white text-[9px] font-mono">
                Source
              </div>
            </div>

            {/* Metadata & Actions */}
            <div className="flex-1 min-w-0 flex flex-col justify-between h-36 py-1">
              <div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#16A34A] mb-1">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Target Person Ready</span>
                </div>
                <h4 className="text-sm font-bold text-[#171717] truncate" title={person.name}>
                  {person.name || 'Custom Person Photo'}
                </h4>
                <p className="text-xs text-slate-600 mt-0.5 font-mono">
                  {person.resolution || 'High Definition'}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-2 border-t border-[#E8E8EF]">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={disabled}
                  aria-label="Replace target person photo"
                  className="min-h-[38px] px-3.5 py-1.5 rounded-lg text-xs font-semibold text-[#171717] bg-white hover:bg-gray-50 border border-[#E8E8EF] shadow-subtle flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-1 focus-visible:outline-none"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                  <span>Replace</span>
                </button>
                <button
                  type="button"
                  onClick={handleRemove}
                  disabled={disabled}
                  aria-label="Remove target person photo"
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
              aria-label="Select target person photograph from computer"
            />
          </div>
        )}

        {/* Quick Model Presets */}
        <div className="mt-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Or choose a sample model:
            </span>
          </div>
          <div className="grid grid-cols-5 gap-2">
            {SAMPLE_PERSONS.map((sample) => {
              const isSelected = person.previewUrl === sample.imageUrl;
              return (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => selectPreset(sample)}
                  disabled={disabled}
                  aria-label={`Select sample model ${sample.name}`}
                  className={`relative rounded-xl overflow-hidden border p-1 text-left transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-1 focus-visible:outline-none ${
                    isSelected
                      ? 'border-[#5B3DF0] ring-2 ring-[#5B3DF0]/20 bg-[#F0EDFD]/40'
                      : 'border-[#E8E8EF] hover:border-gray-300 bg-white'
                  }`}
                  title={sample.name}
                >
                  <div className="aspect-[3/4] rounded-lg overflow-hidden bg-gray-100 mb-1">
                    <img
                      src={sample.imageUrl}
                      alt={sample.name}
                      className="w-full h-full object-cover"
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
