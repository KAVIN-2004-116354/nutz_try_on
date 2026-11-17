import React, { useRef, useState } from 'react';
import { Upload, RefreshCw, Trash2, CheckCircle2, ShieldCheck, UserCheck } from 'lucide-react';
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
    <div className="bg-white rounded-3xl border border-[#E8E8EF] shadow-card p-6 flex flex-col justify-between transition-all duration-400 hover:border-[#5B3DF0]/30 hover:shadow-elevated">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-xl bg-[#F0EDFD] text-[#5B3DF0] font-extrabold text-xs flex items-center justify-center border border-[#5B3DF0]/20 shadow-sm">
              01
            </span>
            <div>
              <h3 className="text-base font-extrabold text-[#171717] flex items-center gap-2">
                <span>Model & Portrait</span>
                {person.previewUrl && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-[#16A34A] border border-emerald-200">
                    <UserCheck className="w-3 h-3" />
                    Locked
                  </span>
                )}
              </h3>
              <p className="text-[12px] text-slate-500 font-medium">
                Identity, facial features and body posture remain 100% intact
              </p>
            </div>
          </div>

          {person.previewUrl && (
            <button
              type="button"
              onClick={handleRemove}
              disabled={disabled}
              className="p-2 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-red-100 transition-all cursor-pointer"
              title="Clear Model"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* 1-Click Studio Models Carousel */}
        <div className="mb-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Quick Studio Models
          </span>
          <div className="flex items-center gap-2.5 overflow-x-auto pb-1 no-scrollbar">
            {SAMPLE_PERSONS.map((sample) => {
              const isSelected = person.previewUrl === sample.imageUrl;
              return (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => selectPreset(sample)}
                  disabled={disabled}
                  className={`group relative flex-shrink-0 flex items-center gap-2 p-1.5 pr-3 rounded-2xl border transition-all duration-300 text-left cursor-pointer ${
                    isSelected
                      ? 'bg-[#F0EDFD] border-[#5B3DF0] shadow-sm ring-2 ring-[#5B3DF0]/20 scale-[1.02]'
                      : 'bg-[#F9F9FC] border-[#E8E8EF] hover:border-slate-300 hover:bg-white'
                  }`}
                >
                  <div className="relative w-9 h-9 rounded-xl overflow-hidden border border-[#E8E8EF] flex-shrink-0">
                    <img
                      src={sample.imageUrl}
                      alt={sample.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    {isSelected && (
                      <span className="absolute inset-0 bg-[#5B3DF0]/20 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4 text-white drop-shadow" />
                      </span>
                    )}
                  </div>
                  <div className="flex flex-col">
                    <span className={`text-[11px] font-bold truncate max-w-[85px] ${
                      isSelected ? 'text-[#5B3DF0]' : 'text-[#171717]'
                    }`}>
                      {sample.name.split(' ')[0]}
                    </span>
                    <span className="text-[9px] text-slate-400 font-medium">
                      {sample.gender === 'women' ? 'Female' : 'Male'}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Upload Dropzone & Interactive Preview */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !person.previewUrl && fileInputRef.current?.click()}
          className={`relative rounded-2xl overflow-hidden transition-all duration-300 ${
            person.previewUrl
              ? 'border border-[#E8E8EF] bg-slate-900 group cursor-default'
              : `border-2 border-dashed flex flex-col items-center justify-center p-8 cursor-pointer ${
                  isDragging
                    ? 'border-[#5B3DF0] bg-[#F0EDFD]/50 scale-[1.01]'
                    : 'border-slate-200 hover:border-[#5B3DF0]/50 hover:bg-[#F9F9FC]'
                }`
          }`}
          style={{ minHeight: person.previewUrl ? '340px' : '220px' }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
            disabled={disabled}
          />

          {person.previewUrl ? (
            <div className="relative w-full h-[340px] flex items-center justify-center overflow-hidden">
              <img
                src={person.previewUrl}
                alt={person.name || 'Model Preview'}
                className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-[1.02]"
              />

              {/* Identity Protection Overlay Tag */}
              <div className="absolute top-3 left-3 px-3 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-white/40 shadow-sm flex items-center gap-1.5 text-xs font-bold text-[#171717]">
                <ShieldCheck className="w-3.5 h-3.5 text-[#16A34A]" />
                <span>Identity Guard Active</span>
              </div>

              {/* Resolution Tag */}
              <div className="absolute top-3 right-3 px-2.5 py-1 rounded-lg bg-black/60 backdrop-blur-md text-[10px] font-mono font-bold text-white">
                {person.resolution || 'HD Portrait'}
              </div>

              {/* Bottom bar with action */}
              <div className="absolute bottom-0 inset-x-0 p-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent flex items-center justify-between opacity-90 group-hover:opacity-100 transition-opacity">
                <span className="text-xs font-semibold text-white truncate max-w-[200px]">
                  {person.name || 'Target Model'}
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  disabled={disabled}
                  className="px-3 py-1.5 rounded-lg bg-white/20 hover:bg-white text-white hover:text-[#171717] text-xs font-bold backdrop-blur-md transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Replace</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-[#F0EDFD] text-[#5B3DF0] flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-sm">
                <Upload className="w-6 h-6 animate-bounce" style={{ animationDuration: '2.5s' }} />
              </div>
              <p className="text-sm font-extrabold text-[#171717] mb-1">
                Drop your photo here or <span className="text-[#5B3DF0] underline">browse</span>
              </p>
              <p className="text-xs text-slate-400 font-medium max-w-xs">
                Supports front-facing portraits in JPG, PNG, WEBP (up to 20MB)
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
