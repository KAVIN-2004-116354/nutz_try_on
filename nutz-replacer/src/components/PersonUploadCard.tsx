import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Trash2, CheckCircle2, UserCheck, Camera } from 'lucide-react';
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
    <div className="bg-white rounded-3xl border border-[#E8E8EF] shadow-card p-6 flex flex-col justify-between transition-all duration-300 hover:border-[#171717]/20 hover:shadow-xl">
      <div>
        {/* Header - Clean Human Fashion */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-extrabold text-[#171717]">
                Model & Pose
              </h3>
              {person.previewUrl && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-[#16A34A] border border-emerald-200">
                  <UserCheck className="w-3 h-3" />
                  Locked
                </span>
              )}
            </div>
            <p className="text-[12px] text-slate-500 font-medium mt-0.5">
              Select a studio portrait or upload your photo
            </p>
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

        {/* Studio Models Carousel */}
        <div className="mb-4">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Studio Model Roster
          </span>
          <div className="flex items-center gap-2.5 overflow-x-auto pb-1 no-scrollbar">
            {SAMPLE_PERSONS.map((sample) => {
              const isSelected = person.previewUrl === sample.imageUrl;
              return (
                <motion.button
                  key={sample.id}
                  type="button"
                  whileHover={{ y: -2, scale: 1.02 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={() => selectPreset(sample)}
                  disabled={disabled}
                  className={`group relative flex-shrink-0 flex items-center gap-2.5 p-1.5 pr-3.5 rounded-2xl border transition-colors duration-200 text-left cursor-pointer ${
                    isSelected
                      ? 'bg-[#171717] border-[#171717] text-white shadow-md'
                      : 'bg-[#F9F9FC] border-[#E8E8EF] text-[#171717] hover:border-slate-300 hover:bg-white'
                  }`}
                >
                  <div className="relative w-9 h-9 rounded-xl overflow-hidden border border-black/10 flex-shrink-0 bg-white">
                    <img
                      src={sample.imageUrl}
                      alt={sample.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    {isSelected && (
                      <span className="absolute inset-0 bg-black/30 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4 text-white drop-shadow" />
                      </span>
                    )}
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[11px] font-bold truncate max-w-[85px] leading-tight">
                      {sample.name.split(' ')[0]}
                    </span>
                    <span className={`text-[9px] font-medium ${isSelected ? 'text-slate-300' : 'text-slate-400'}`}>
                      {sample.gender === 'women' ? 'Female' : 'Male'}
                    </span>
                  </div>
                </motion.button>
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
              ? 'border border-[#E8E8EF] bg-[#F8F7F4] group cursor-default'
              : `border-2 border-dashed flex flex-col items-center justify-center p-8 cursor-pointer ${
                  isDragging
                    ? 'border-[#171717] bg-[#F2EFE9] scale-[1.01]'
                    : 'border-neutral-200 hover:border-neutral-400 hover:bg-[#FAF9F6]'
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

              {/* Status Tag */}
              <div className="absolute top-3 left-3 px-3 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-white/40 shadow-sm flex items-center gap-1.5 text-xs font-bold text-[#171717]">
                <span className="w-2 h-2 rounded-full bg-[#16A34A]" />
                <span>Pose & Identity Locked</span>
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
                  <span>Replace Photo</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-[#F5F4F8] text-[#171717] flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-sm border border-[#E8E8EF]">
                <Camera className="w-6 h-6 stroke-[1.8]" />
              </div>
              <p className="text-sm font-extrabold text-[#171717] mb-1">
                Upload your portrait or <span className="underline">browse files</span>
              </p>
              <p className="text-xs text-slate-400 font-medium max-w-xs">
                Front-facing portraits in JPG, PNG, WEBP (up to 20MB)
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
