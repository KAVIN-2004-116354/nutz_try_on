import React, { useState, useRef, useEffect } from 'react';
import { 
  Download, RefreshCw, Trash2, ChevronDown, ChevronUp, 
  Menu, X, Check, Sparkles, Layers 
} from 'lucide-react';
import { ImageInputState, TryonResult, GenerationStatus, SamplePreset } from '../types';
import { SAMPLE_PERSONS, SAMPLE_GARMENTS, FLUX_17_CATEGORIES } from '../presets';

interface MobileTryonArtboardProps {
  person: ImageInputState;
  setPerson: React.Dispatch<React.SetStateAction<ImageInputState>>;
  garment: ImageInputState;
  setGarment: React.Dispatch<React.SetStateAction<ImageInputState>>;
  selectedCategory: string;
  setSelectedCategory: (cat: string) => void;
  result: TryonResult | null;
  generationStatus: GenerationStatus;
  canGenerate: boolean;
  onGenerate: () => void;
  onOpenZoom?: () => void;
  selectionChanged: boolean;
  onSelectionChangedDismiss?: () => void;
}

export const MobileTryonArtboard: React.FC<MobileTryonArtboardProps> = ({
  person,
  setPerson,
  garment,
  setGarment,
  selectedCategory,
  setSelectedCategory,
  result,
  generationStatus,
  canGenerate,
  onGenerate,
  selectionChanged,
}) => {
  // Slider state
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState<boolean>(false);
  const [accordionOpen, setAccordionOpen] = useState<boolean>(false);
  const rafRef = useRef<number | null>(null);

  // Hidden file inputs
  const personFileInputRef = useRef<HTMLInputElement>(null);
  const garmentFileInputRef = useRef<HTMLInputElement>(null);

  const handleSliderChange = (newVal: number) => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      setSliderPosition(newVal);
    });
  };

  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  // Detected category label helper
  const getDetectedCategoryLabel = () => {
    const matched = FLUX_17_CATEGORIES.find((c) => c.key === selectedCategory);
    if (matched) {
      return `${matched.name}, ${matched.macroCategory.toLowerCase()}`;
    }
    return 'Blazer, upper body';
  };

  const handlePersonFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setPerson({
        file,
        previewUrl,
        name: file.name.replace(/\.[^/.]+$/, ''),
        isCustom: true,
        resolution: 'Custom Photo',
      });
    }
  };

  const handleGarmentFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setGarment({
        file,
        previewUrl,
        name: file.name.replace(/\.[^/.]+$/, ''),
        isCustom: true,
        resolution: 'Custom Garment',
      });
    }
  };

  const selectPersonPreset = (preset: SamplePreset) => {
    setPerson({
      file: null,
      previewUrl: preset.imageUrl,
      name: preset.name,
      isCustom: false,
      resolution: 'Studio HD',
    });
  };

  const selectGarmentPreset = (preset: SamplePreset) => {
    setGarment({
      file: null,
      previewUrl: preset.imageUrl,
      name: preset.name,
      isCustom: false,
      resolution: 'Catalog HD',
    });
    // Auto-update category
    if (preset.id.includes('blazer')) setSelectedCategory('blazer');
    else if (preset.id.includes('shirt')) setSelectedCategory('shirt');
    else if (preset.id.includes('black-tee')) setSelectedCategory('t_shirt');
    else if (preset.id.includes('anarkali')) setSelectedCategory('western_dress');
    else if (preset.id.includes('denim')) setSelectedCategory('shirt');
  };

  const isGenerating = generationStatus === 'processing' || generationStatus === 'uploading';
  const resultImageUrl = result?.image_data || result?.result_url || (person.previewUrl ? '/studio/assets/studio_demo/demo_tryon_result.jpg' : null);

  return (
    <div className="w-[390px] h-[844px] bg-[#F5F4F8] text-[#171717] font-sans flex flex-col overflow-hidden relative shadow-2xl rounded-[40px] border-[8px] border-[#171717] select-none">
      {/* iOS Status Bar Notch Mockup */}
      <div className="h-10 bg-transparent flex items-center justify-between px-6 pt-1 flex-shrink-0 z-40">
        <span className="text-[14px] font-bold tracking-tight text-[#171717]">9:41</span>
        <div className="w-20 h-4 bg-black rounded-full" />
        <div className="flex items-center gap-1.5 text-[#171717]">
          <span className="text-[12px] font-bold">5G</span>
          <div className="w-5 h-2.5 border border-[#171717] rounded-xs p-0.5 flex items-center">
            <div className="w-3 h-full bg-[#171717] rounded-2xs" />
          </div>
        </div>
      </div>

      {/* 1. Compact Header */}
      <header className="h-14 bg-white/95 backdrop-blur-md border-b border-[#E8E8EF] flex items-center justify-between px-4 flex-shrink-0 z-30">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#171717] flex items-center justify-center p-1">
            <img
              src="/nutz_logo_white.png"
              alt="Nutz Logo"
              className="w-full h-full object-contain"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/nutz_logo.jpg';
              }}
            />
          </div>
          <span className="text-[17px] font-extrabold tracking-tight text-[#171717]">
            Nutz Replacer
          </span>
        </div>

        {/* 44x44px Tappable Menu Button */}
        <button
          type="button"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-xl hover:bg-[#F5F4F8] active:bg-gray-200 transition-colors cursor-pointer text-[#171717] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
          aria-label="Navigation Menu"
        >
          {isMenuOpen ? <X className="w-5 h-5 stroke-[2.2]" /> : <Menu className="w-5 h-5 stroke-[2.2]" />}
        </button>
      </header>

      {/* Slide-in Mobile Menu */}
      {isMenuOpen && (
        <div className="absolute inset-x-0 top-24 bg-white/98 backdrop-blur-lg border-b border-[#E8E8EF] z-40 p-5 shadow-xl animate-fadeIn">
          <nav className="flex flex-col gap-2">
            <button
              onClick={() => setIsMenuOpen(false)}
              className="min-h-[44px] flex items-center px-4 rounded-xl font-bold text-[15px] bg-[#F0EDFD] text-[#5B3DF0] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
            >
              Virtual Try-On Studio
            </button>
            <button
              onClick={() => setIsMenuOpen(false)}
              className="min-h-[44px] flex items-center px-4 rounded-xl font-semibold text-[15px] text-[#171717] hover:bg-[#F5F4F8] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
            >
              How It Works
            </button>
            <button
              onClick={() => setIsMenuOpen(false)}
              className="min-h-[44px] flex items-center px-4 rounded-xl font-semibold text-[15px] text-[#171717] hover:bg-[#F5F4F8] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
            >
              Features & Quality
            </button>
          </nav>
        </div>
      )}

      {/* Scrollable Mobile Body (No Horizontal Scroll, 16px Side Margins) */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4 space-y-4 no-scrollbar">
        {/* 2. Title & 3-Step Bar */}
        <div className="pt-1">
          <h1 className="text-[22px] font-extrabold text-[#171717] tracking-tight leading-tight">
            Virtual try-on
          </h1>
          <p className="text-[14px] text-slate-600 mt-0.5 leading-normal">
            Select a photo and outfit to see your transformation.
          </p>

          {/* 3-Step Bar as single row of small circles with active step labeled */}
          <div className="flex items-center justify-between pt-3 pb-1">
            {/* Step 1: Photo */}
            <div className="flex items-center gap-1.5">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${
                person.previewUrl ? 'bg-[#5B3DF0] text-white' : 'bg-[#E8E8EF] text-slate-600'
              }`}>
                {person.previewUrl ? <Check className="w-3 h-3 stroke-[3]" /> : '1'}
              </div>
              <span className={`text-[13px] font-bold ${!resultImageUrl ? 'text-[#5B3DF0]' : 'text-[#171717]'}`}>
                Photo
              </span>
            </div>

            <div className="flex-1 h-[2px] bg-[#E8E8EF] mx-2" />

            {/* Step 2: Outfit */}
            <div className="flex items-center gap-1.5">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${
                garment.previewUrl ? 'bg-[#5B3DF0] text-white' : 'bg-[#E8E8EF] text-slate-600'
              }`}>
                {garment.previewUrl ? <Check className="w-3 h-3 stroke-[3]" /> : '2'}
              </div>
              <span className={`text-[13px] font-bold ${!resultImageUrl && person.previewUrl ? 'text-[#5B3DF0]' : 'text-[#171717]'}`}>
                Outfit
              </span>
            </div>

            <div className="flex-1 h-[2px] bg-[#E8E8EF] mx-2" />

            {/* Step 3: Result */}
            <div className="flex items-center gap-1.5">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${
                resultImageUrl ? 'bg-[#5B3DF0] text-white' : 'bg-[#E8E8EF] text-slate-600'
              }`}>
                3
              </div>
              <span className={`text-[13px] font-bold ${resultImageUrl ? 'text-[#5B3DF0]' : 'text-slate-600'}`}>
                Result
              </span>
            </div>
          </div>
        </div>

        {/* 3. Result First: "Your new look" Card */}
        <section className="bg-white rounded-[20px] p-4 shadow-subtle border border-[#E8E8EF]">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-[16px] font-bold text-[#171717]">
              Your new look
            </h2>
            <span className="text-[13px] font-bold text-[#5B3DF0] bg-[#F0EDFD] px-2.5 py-0.5 rounded-full border border-[#5B3DF0]/20">
              HD 1024px
            </span>
          </div>

          {/* Full Width (3:4) Image with Draggable Before/After Slider Handle */}
          <div className="w-full aspect-[3/4] rounded-[16px] overflow-hidden relative select-none bg-[#F5F4F8] border border-[#E8E8EF]">
            {resultImageUrl ? (
              <div className="relative w-full h-full">
                {/* Result (After) Image */}
                <img
                  src={resultImageUrl}
                  alt="Your new look"
                  className="w-full h-full object-cover pointer-events-none"
                />

                {/* Original (Before) Image clamped to sliderPosition */}
                {person.previewUrl && (
                  <div
                    className="absolute inset-0 overflow-hidden pointer-events-none"
                    style={{ width: `${sliderPosition}%` }}
                  >
                    <img
                      src={person.previewUrl}
                      alt="Original photo"
                      className="w-full h-full object-cover"
                      style={{ width: '358px', maxWidth: 'none' }}
                    />
                    <div className="absolute top-2.5 left-2.5 bg-black/70 text-white text-[13px] font-bold px-2 py-0.5 rounded-md">
                      Before
                    </div>
                  </div>
                )}

                <div className="absolute top-2.5 right-2.5 bg-[#5B3DF0] text-white text-[13px] font-bold px-2 py-0.5 rounded-md shadow-sm">
                  After
                </div>

                {/* Slider Handle On Image */}
                <div
                  className="absolute top-0 bottom-0 w-[2px] bg-white shadow-md z-20 pointer-events-none flex items-center justify-center"
                  style={{ left: `${sliderPosition}%` }}
                >
                  <div className="w-8 h-8 rounded-full bg-white shadow-lg border border-[#E8E8EF] flex items-center justify-center text-[#5B3DF0] text-[13px] font-bold">
                    ⟷
                  </div>
                </div>
              </div>
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-center p-6 text-slate-600">
                <Sparkles className="w-8 h-8 text-[#5B3DF0] mb-2" />
                <p className="text-[14px] font-bold text-[#171717]">Ready for generation</p>
                <p className="text-[13px] mt-1">Tap generate below to render your new look</p>
              </div>
            )}
          </div>

          {/* 44px Tall Touch Area Range Slider Below the Image */}
          <div className="h-[44px] flex items-center justify-between gap-3 px-1 mt-2">
            <span className="text-[13px] font-bold text-slate-600 min-w-[44px]">
              Before
            </span>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPosition}
              onChange={(e) => handleSliderChange(Number(e.target.value))}
              aria-label="Before and after comparison slider"
              className="slider-range flex-1 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
            />
            <span className="text-[13px] font-bold text-[#5B3DF0] min-w-[44px] text-right">
              After
            </span>
          </div>

          {/* Full-width Outlined Download PNG Button (Min 44px Touch Target) */}
          {resultImageUrl && (
            <a
              href={resultImageUrl}
              download={`nutz_tryon_${Date.now()}.png`}
              aria-label="Download virtual try-on result in high-resolution PNG"
              className="w-full min-h-[44px] rounded-xl border-2 border-[#5B3DF0] text-[#5B3DF0] hover:bg-[#5B3DF0]/5 active:bg-[#5B3DF0]/10 font-bold text-[14px] flex items-center justify-center gap-2 mt-2 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
            >
              <Download className="w-4 h-4 stroke-[2.2]" />
              <span>Download PNG</span>
            </a>
          )}
        </section>

        {/* 4. Photo Card */}
        <section className="bg-white rounded-[20px] p-4 shadow-subtle border border-[#E8E8EF]">
          <h2 className="text-[16px] font-bold text-[#171717] mb-3">
            Photo
          </h2>

          {/* 72 × 92 Thumbnail & Details Row */}
          <div className="flex items-center gap-3.5">
            <div className="w-[72px] h-[92px] rounded-xl overflow-hidden border border-[#E8E8EF] bg-[#F5F4F8] flex-shrink-0">
              {person.previewUrl ? (
                <img
                  src={person.previewUrl}
                  alt={person.name}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-xs font-bold text-slate-600">
                  No Photo
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="text-[15px] font-bold text-[#171717] truncate">
                {person.name || 'Sample Model'}
              </h3>
              <p className="text-[13px] text-slate-600 mt-0.5">
                Target identity & pose
              </p>

              {/* 44x44px Minimum Tappable Action Buttons */}
              <div className="flex items-center gap-2 mt-2.5">
                <button
                  type="button"
                  onClick={() => personFileInputRef.current?.click()}
                  aria-label="Replace target model photo"
                  className="min-h-[44px] px-3.5 py-2 rounded-xl bg-[#F5F4F8] hover:bg-gray-200 active:bg-gray-300 text-[#171717] font-bold text-[13px] border border-[#E8E8EF] flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                  <span>Replace</span>
                </button>
                <button
                  type="button"
                  onClick={() => setPerson({ file: null, previewUrl: null, name: '', isCustom: false })}
                  aria-label="Remove target model photo"
                  className="min-h-[44px] px-3.5 py-2 rounded-xl bg-white hover:bg-red-50 active:bg-red-100 text-[#DC2626] font-bold text-[13px] border border-[#E8E8EF] flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#DC2626] focus-visible:outline-none"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Remove</span>
                </button>
              </div>
            </div>

            <input
              ref={personFileInputRef}
              type="file"
              accept="image/*"
              onChange={handlePersonFile}
              className="hidden"
              aria-label="Upload target person photograph from device"
            />
          </div>

          {/* Horizontally Scrolling Row of 64px Tiles with Snap Scrolling */}
          <div className="pt-3.5 mt-3.5 border-t border-[#E8E8EF]">
            <span className="text-[13px] font-bold text-slate-600 block mb-2">
              Sample models
            </span>
            <div className="flex items-center gap-2.5 overflow-x-auto snap-x snap-mandatory no-scrollbar pb-1">
              {SAMPLE_PERSONS.map((sample) => {
                const isSelected = person.previewUrl === sample.imageUrl;
                return (
                  <button
                    key={sample.id}
                    type="button"
                    onClick={() => selectPersonPreset(sample)}
                    aria-label={`Select sample model ${sample.name}`}
                    className={`w-[64px] h-[64px] rounded-[14px] flex-shrink-0 snap-start overflow-hidden border-2 transition-all p-0.5 cursor-pointer min-h-[44px] min-w-[44px] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
                      isSelected
                        ? 'border-[#5B3DF0] ring-2 ring-[#5B3DF0]/25'
                        : 'border-[#E8E8EF] hover:border-gray-300'
                    }`}
                    title={sample.name}
                  >
                    <img
                      src={sample.imageUrl}
                      alt={sample.name}
                      className="w-full h-full object-cover rounded-[10px]"
                      loading="lazy"
                    />
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* 5. Outfit Card */}
        <section className="bg-white rounded-[20px] p-4 shadow-subtle border border-[#E8E8EF]">
          <h2 className="text-[16px] font-bold text-[#171717] mb-3">
            Outfit
          </h2>

          {/* 72 × 92 Thumbnail & Details Row */}
          <div className="flex items-center gap-3.5">
            <div className="w-[72px] h-[92px] rounded-xl overflow-hidden border border-[#E8E8EF] bg-[#F5F4F8] p-1 flex items-center justify-center flex-shrink-0">
              {garment.previewUrl ? (
                <img
                  src={garment.previewUrl}
                  alt={garment.name}
                  className="w-full h-full object-contain"
                  loading="lazy"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-xs font-bold text-slate-600">
                  No Outfit
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="text-[15px] font-bold text-[#171717] truncate">
                {garment.name || 'Sample Outfit'}
              </h3>
              <p className="text-[13px] text-slate-600 mt-0.5">
                Garment design & pattern
              </p>

              {/* 44x44px Minimum Tappable Action Buttons */}
              <div className="flex items-center gap-2 mt-2.5">
                <button
                  type="button"
                  onClick={() => garmentFileInputRef.current?.click()}
                  aria-label="Replace garment reference photo"
                  className="min-h-[44px] px-3.5 py-2 rounded-xl bg-[#F5F4F8] hover:bg-gray-200 active:bg-gray-300 text-[#171717] font-bold text-[13px] border border-[#E8E8EF] flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                  <span>Replace</span>
                </button>
                <button
                  type="button"
                  onClick={() => setGarment({ file: null, previewUrl: null, name: '', isCustom: false })}
                  aria-label="Remove garment reference photo"
                  className="min-h-[44px] px-3.5 py-2 rounded-xl bg-white hover:bg-red-50 active:bg-red-100 text-[#DC2626] font-bold text-[13px] border border-[#E8E8EF] flex items-center gap-1.5 transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-[#DC2626] focus-visible:outline-none"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Remove</span>
                </button>
              </div>
            </div>

            <input
              ref={garmentFileInputRef}
              type="file"
              accept="image/*"
              onChange={handleGarmentFile}
              className="hidden"
              aria-label="Upload clothing reference photograph from device"
            />
          </div>

          {/* "Detected: Blazer, upper body" Row with a 44x44px Change Link */}
          <div className="flex items-center justify-between py-2 px-3.5 bg-[#F5F4F8] rounded-xl my-3 text-[13px] text-[#171717] border border-[#E8E8EF]">
            <div className="flex items-center gap-1.5 truncate">
              <span className="text-slate-600">Detected:</span>
              <span className="font-bold text-[#171717] truncate">
                {getDetectedCategoryLabel()}
              </span>
            </div>
            <button
              type="button"
              onClick={() => setIsCategoryModalOpen(true)}
              aria-label="Change garment category"
              className="min-h-[44px] min-w-[44px] flex items-center justify-end text-[#5B3DF0] hover:text-[#4B2EE0] font-bold text-[13px] cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
            >
              Change
            </button>
          </div>

          {/* Horizontally Scrolling Row of 64px Garment Tiles with Snap Scrolling */}
          <div className="pt-2 border-t border-[#E8E8EF]">
            <span className="text-[13px] font-bold text-slate-600 block mb-2">
              Sample garments
            </span>
            <div className="flex items-center gap-2.5 overflow-x-auto snap-x snap-mandatory no-scrollbar pb-1">
              {SAMPLE_GARMENTS.map((sample) => {
                const isSelected = garment.previewUrl === sample.imageUrl;
                return (
                  <button
                    key={sample.id}
                    type="button"
                    onClick={() => selectGarmentPreset(sample)}
                    aria-label={`Select sample outfit ${sample.name}`}
                    className={`w-[64px] h-[64px] rounded-[14px] flex-shrink-0 snap-start overflow-hidden border-2 bg-white p-1 transition-all flex items-center justify-center cursor-pointer min-h-[44px] min-w-[44px] focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
                      isSelected
                        ? 'border-[#5B3DF0] ring-2 ring-[#5B3DF0]/25'
                        : 'border-[#E8E8EF] hover:border-gray-300'
                    }`}
                    title={sample.name}
                  >
                    <img
                      src={sample.imageUrl}
                      alt={sample.name}
                      className="w-full h-full object-contain"
                      loading="lazy"
                    />
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* 7. Collapsible "How it works" Accordion / Stacked Cards */}
        <section className="bg-white rounded-[20px] p-4 shadow-subtle border border-[#E8E8EF]">
          <button
            type="button"
            onClick={() => setAccordionOpen(!accordionOpen)}
            className="w-full min-h-[44px] flex items-center justify-between text-left cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded-xl"
            aria-expanded={accordionOpen}
            aria-label="Toggle how it works explanation"
          >
            <div>
              <h2 className="text-[16px] font-bold text-[#171717]">
                How it works
              </h2>
              <p className="text-[13px] text-slate-600">
                3 simple steps to your virtual look
              </p>
            </div>
            <div className="min-w-[44px] min-h-[44px] flex items-center justify-end text-[#5B3DF0]">
              {accordionOpen ? <ChevronUp className="w-5 h-5 stroke-[2.5]" /> : <ChevronDown className="w-5 h-5 stroke-[2.5]" />}
            </div>
          </button>

          {accordionOpen && (
            <div className="pt-3 space-y-2.5 border-t border-[#E8E8EF] mt-2 animate-fadeIn">
              <div className="p-3 bg-[#F5F4F8] rounded-[16px] border border-[#E8E8EF]">
                <span className="text-[13px] font-bold text-[#5B3DF0]">01. Upload photo</span>
                <p className="text-[13px] text-slate-600 mt-0.5 leading-snug">
                  Locks face, skin tone, hair, and body proportions as identity source of truth.
                </p>
              </div>

              <div className="p-3 bg-[#F5F4F8] rounded-[16px] border border-[#E8E8EF]">
                <span className="text-[13px] font-bold text-[#5B3DF0]">02. Choose outfit</span>
                <p className="text-[13px] text-slate-600 mt-0.5 leading-snug">
                  Extracts printed graphics, fabric weave, and color patterns into visual latents.
                </p>
              </div>

              <div className="p-3 bg-[#F5F4F8] rounded-[16px] border border-[#E8E8EF]">
                <span className="text-[13px] font-bold text-[#5B3DF0]">03. Generate look</span>
                <p className="text-[13px] text-slate-600 mt-0.5 leading-snug">
                  FLUX-DEV-012 dual-panel diffusion synthesizes the garment with photorealistic drape.
                </p>
              </div>
            </div>
          )}
        </section>

        {/* Safe margin bottom to prevent sticky bar overlap */}
        <div className="h-20" />
      </main>

      {/* 6. Sticky Bottom Bar with 56px Tall Button and Safe-Area Inset */}
      <footer className="sticky bottom-0 z-30 bg-white/95 backdrop-blur-md border-t border-[#E8E8EF] px-4 pt-2.5 pb-[max(16px,env(safe-area-inset-bottom))] shadow-lg flex-shrink-0">
        {/* Selection Changed Notice Badge */}
        {selectionChanged && !isGenerating && (
          <div className="mb-2 px-3 py-1.5 rounded-xl bg-[#F0EDFD] border border-[#5B3DF0]/30 text-[#5B3DF0] text-[13px] font-bold flex items-center justify-center gap-1.5 animate-fadeIn">
            <span className="w-2 h-2 rounded-full bg-[#5B3DF0] animate-pulse" />
            <span>Selection changed • Tap to generate new look</span>
          </div>
        )}

        {/* 56px Tall Primary Action Button */}
        <button
          type="button"
          onClick={onGenerate}
          disabled={!canGenerate || isGenerating}
          aria-label={isGenerating ? 'Generating look' : selectionChanged ? 'Generate new look' : resultImageUrl ? 'Generate again' : 'Generate look'}
          className={`w-full h-[56px] rounded-xl font-bold text-[16px] transition-all flex items-center justify-center gap-2 shadow-premium cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 focus-visible:outline-none ${
            canGenerate && !isGenerating
              ? 'bg-[#5B3DF0] hover:bg-[#4B2EE0] active:scale-[0.99] text-white'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
          }`}
        >
          {isGenerating ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Generating look...</span>
            </>
          ) : selectionChanged ? (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Generate new look</span>
            </>
          ) : resultImageUrl ? (
            <>
              <RefreshCw className="w-5 h-5" />
              <span>Generate again</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Generate look</span>
            </>
          )}
        </button>

        {/* iOS Home Indicator Bar Mockup */}
        <div className="w-32 h-1 bg-[#171717]/30 rounded-full mx-auto mt-3" />
      </footer>

      {/* Category Selection Modal Sheet */}
      {isCategoryModalOpen && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-xs z-50 flex flex-col justify-end animate-fadeIn">
          <div className="bg-white rounded-t-[28px] p-5 max-h-[70vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#E8E8EF]">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#5B3DF0]" />
                <h3 className="text-[16px] font-bold text-[#171717]">Select Garment Category</h3>
              </div>
              <button
                type="button"
                onClick={() => setIsCategoryModalOpen(false)}
                aria-label="Close category selection modal"
                className="min-w-[44px] min-h-[44px] flex items-center justify-center text-slate-600 focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded-xl"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto py-3 space-y-1.5 no-scrollbar flex-1">
              {FLUX_17_CATEGORIES.map((cat) => {
                const isSelected = selectedCategory === cat.key;
                return (
                  <button
                    key={cat.key}
                    type="button"
                    onClick={() => {
                      setSelectedCategory(cat.key);
                      setIsCategoryModalOpen(false);
                    }}
                    className={`w-full min-h-[44px] px-3.5 py-2.5 rounded-xl text-left text-[14px] flex items-center justify-between transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
                      isSelected
                        ? 'bg-[#F0EDFD] text-[#5B3DF0] font-bold'
                        : 'hover:bg-[#F5F4F8] text-[#171717] font-medium'
                    }`}
                  >
                    <span>{cat.name} ({cat.macroCategory})</span>
                    {isSelected && <Check className="w-4 h-4 text-[#5B3DF0] stroke-[3]" />}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
