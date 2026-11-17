import React, { useState, useRef, useEffect } from 'react';
import { 
  Sparkles, Download, RefreshCw, RotateCcw, Maximize2, SplitSquareHorizontal 
} from 'lucide-react';
import { TryonResult, ImageInputState, GenerationStatus } from '../types';

interface ResultStageProps {
  person: ImageInputState;
  garment: ImageInputState;
  selectedCategory?: string;
  result: TryonResult | null;
  generationStatus: GenerationStatus;
  currentStage: number;
  elapsedSec: number;
  canGenerate: boolean;
  onGenerate: () => void;
  onReset: () => void;
  onOpenZoom: () => void;
}

const STAGE_LABELS = [
  'Preparing your images & pose landmarks...',
  'Analyzing garment patterns & fabric structure...',
  'Conditioning FLUX-DEV-012 dual-panel visual latents...',
  'Synthesizing photorealistic fabric folds & fit...',
  'Finalizing high-resolution virtual try-on...',
];

export const ResultStage: React.FC<ResultStageProps> = ({
  person,
  garment,
  result,
  generationStatus,
  currentStage,
  elapsedSec,
  canGenerate,
  onGenerate,
  onReset,
  onOpenZoom,
}) => {
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [showSlider, setShowSlider] = useState<boolean>(true);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const rafRef = useRef<number | null>(null);

  const isProcessing = generationStatus === 'processing' || generationStatus === 'uploading';
  const isCompleted = generationStatus === 'completed' && Boolean(result);

  const handleSliderMove = (clientX: number, rect: DOMRect) => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      setSliderPosition((x / rect.width) * 100);
    });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    handleSliderMove(e.clientX, rect);
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    handleSliderMove(e.touches[0].clientX, rect);
  };

  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  const resultImageUrl = result?.image_data || result?.result_url || null;

  return (
    <div className="bg-white rounded-2xl border border-[#E8E8EF] shadow-card p-6 flex flex-col justify-between h-full transition-all">
      {/* Top Action Bar & Primary CTA */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#E8E8EF] mb-5">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#5B3DF0] flex items-center gap-1.5 mb-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Step 03</span>
            </span>
            <h3 className="text-lg font-extrabold text-[#171717]">
              {isCompleted ? 'Your New Look Is Ready!' : 'Virtual Try-On Stage'}
            </h3>
          </div>

          {/* Primary CTA: "Generate My Look" */}
          <button
            type="button"
            onClick={onGenerate}
            disabled={!canGenerate || isProcessing}
            aria-label={isProcessing ? 'Generating try-on look' : isCompleted ? 'Generate try-on again' : 'Generate virtual try-on look'}
            className={`min-h-[48px] px-7 py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 shadow-premium cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:ring-offset-2 focus-visible:outline-none ${
              canGenerate && !isProcessing
                ? 'bg-[#5B3DF0] hover:bg-[#4B2EE0] active:bg-[#4D31C7] text-white hover:scale-[1.01]'
                : 'bg-gray-100 text-gray-400 border border-[#E8E8EF] cursor-not-allowed shadow-none'
            }`}
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Processing Look...</span>
              </>
            ) : isCompleted ? (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Generate Again</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate My Look</span>
              </>
            )}
          </button>
        </div>

        {/* Viewport / Stage Container */}
        <div className="relative bg-[#F5F4F8] border border-[#E8E8EF] rounded-xl overflow-hidden min-h-[460px] flex items-center justify-center">
          {/* PROCESSING STATE SCREEN */}
          {isProcessing && (
            <div className="absolute inset-0 bg-white/95 backdrop-blur-xs z-30 flex flex-col items-center justify-center p-8 text-center animate-fadeIn">
              {/* Spinner */}
              <div className="relative mb-6">
                <div className="w-16 h-16 rounded-full border-4 border-[#F0EDFD] border-t-[#5B3DF0] animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center text-xs font-mono font-bold text-[#5B3DF0]">
                  {Math.round(elapsedSec)}s
                </div>
              </div>

              <h4 className="text-lg font-extrabold text-[#171717] mb-2">
                Creating Your New Look...
              </h4>
              <p className="text-xs text-[#5B3DF0] font-semibold max-w-sm mb-6 animate-pulse">
                {STAGE_LABELS[Math.min(currentStage - 1, STAGE_LABELS.length - 1)]}
              </p>

              {/* Progress Step Pills */}
              <div className="flex items-center gap-1.5 max-w-xs w-full">
                {STAGE_LABELS.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                      idx < currentStage ? 'bg-[#5B3DF0]' : 'bg-[#E8E8EF]'
                    }`}
                  />
                ))}
              </div>

              <span className="text-[11px] text-slate-600 mt-4 font-mono">
                Conditioning FLUX-DEV-012 with Dual-Panel Reference
              </span>
            </div>
          )}

          {/* COMPLETED RESULT EXPERIENCE */}
          {isCompleted && resultImageUrl ? (
            <div
              className="relative w-full h-[520px] select-none overflow-hidden flex items-center justify-center touch-none"
              onMouseMove={handleMouseMove}
              onMouseUp={() => setIsDragging(false)}
              onMouseLeave={() => setIsDragging(false)}
              onTouchMove={handleTouchMove}
              onTouchEnd={() => setIsDragging(false)}
              onTouchCancel={() => setIsDragging(false)}
            >
              {showSlider && person.previewUrl ? (
                /* Draggable Before/After Comparison Split Slider */
                <div className="relative w-full h-full">
                  {/* Generated Result (After) */}
                  <img
                    src={resultImageUrl}
                    alt="Virtual Try-On Result"
                    className="w-full h-full object-contain pointer-events-none"
                  />

                  {/* Original Person (Before) clamped to slider percentage */}
                  <div
                    className="absolute inset-0 overflow-hidden pointer-events-none"
                    style={{ width: `${sliderPosition}%` }}
                  >
                    <img
                      src={person.previewUrl}
                      alt="Original Person"
                      className="w-full h-full object-contain"
                      style={{ width: '100%', maxWidth: 'none' }}
                    />
                    <div className="absolute top-3 left-3 bg-black/70 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider shadow">
                      Before (Original)
                    </div>
                  </div>

                  <div className="absolute top-3 right-3 bg-[#5B3DF0] text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider shadow">
                    After (Try-On)
                  </div>

                  {/* Vertical Split Line & Draggable Handle */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg cursor-ew-resize flex items-center justify-center z-20"
                    style={{ left: `${sliderPosition}%` }}
                    onMouseDown={() => setIsDragging(true)}
                    onTouchStart={() => setIsDragging(true)}
                    role="separator"
                    aria-label="Before and after split slider handle"
                    aria-valuenow={Math.round(sliderPosition)}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'ArrowLeft') {
                        setSliderPosition((prev) => Math.max(0, prev - 5));
                      } else if (e.key === 'ArrowRight') {
                        setSliderPosition((prev) => Math.min(100, prev + 5));
                      }
                    }}
                  >
                    <div className="w-8 h-8 bg-white border border-[#E8E8EF] rounded-full shadow-md flex items-center justify-center text-[#5B3DF0] text-xs font-bold hover:scale-110 active:scale-95 transition-transform select-none">
                      ⟷
                    </div>
                  </div>
                </div>
              ) : (
                /* Full Single Image View */
                <img
                  src={resultImageUrl}
                  alt="Virtual Try-On Result"
                  className="w-full h-full object-contain"
                />
              )}

              {/* Top Viewport Controls */}
              <div className="absolute top-3 left-3 flex items-center gap-2 z-20">
                {person.previewUrl && (
                  <button
                    type="button"
                    onClick={() => setShowSlider(!showSlider)}
                    aria-label={showSlider ? 'Exit comparison slider' : 'Compare before and after'}
                    className={`min-h-[36px] px-3 py-1.5 rounded-lg text-xs font-semibold border shadow-subtle transition flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
                      showSlider
                        ? 'bg-[#5B3DF0] text-white border-[#5B3DF0]'
                        : 'bg-white/95 text-[#171717] border-[#E8E8EF] hover:bg-white'
                    }`}
                  >
                    <SplitSquareHorizontal className="w-3.5 h-3.5" />
                    <span>{showSlider ? 'Exit Slider' : 'Compare Before/After'}</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={onOpenZoom}
                  aria-label="Open full-screen HD view"
                  className="min-h-[36px] min-w-[36px] p-2 rounded-lg bg-white/95 hover:bg-white text-[#171717] border border-[#E8E8EF] shadow-subtle transition cursor-pointer flex items-center justify-center focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
                  title="Full-Screen HD View"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Floating Bottom Action Strip */}
              <div className="absolute bottom-4 inset-x-4 flex items-center justify-between z-20 pointer-events-none">
                <div className="flex items-center gap-2 pointer-events-auto">
                  <span className="px-2.5 py-1 rounded-lg bg-black/60 backdrop-blur-xs text-white text-[11px] font-mono">
                    1024 × 1024 HD
                  </span>
                </div>

                <a
                  href={resultImageUrl}
                  download={`nutz_replacer_${Date.now()}.png`}
                  aria-label="Download virtual try-on result in high-resolution PNG"
                  className="pointer-events-auto min-h-[44px] px-4 py-2 rounded-xl bg-white/95 hover:bg-white text-[#171717] font-bold text-xs border border-[#E8E8EF] shadow-md flex items-center gap-2 transition hover:scale-[1.02] cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
                >
                  <Download className="w-4 h-4 text-[#5B3DF0]" />
                  <span>Download PNG</span>
                </a>
              </div>
            </div>
          ) : (
            /* READY / WAITING STATE */
            <div className="flex flex-col items-center justify-center p-8 text-center">
              {person.previewUrl ? (
                <div className="flex flex-col items-center max-w-sm">
                  <div className="relative w-44 h-56 rounded-xl overflow-hidden border border-[#E8E8EF] bg-white shadow-subtle mb-4">
                    <img
                      src={person.previewUrl}
                      alt="Target Person"
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent flex items-end justify-center p-2.5">
                      <span className="text-[11px] text-white font-semibold">
                        Target Person Selected
                      </span>
                    </div>
                  </div>
                  <h4 className="text-sm font-bold text-[#171717] mb-1">
                    Ready to Transform Look
                  </h4>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    {garment.previewUrl
                      ? 'Both images uploaded. Click "Generate My Look" to synthesize your try-on.'
                      : 'Please choose or upload a clothing reference in Step 02.'}
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center max-w-sm text-slate-600">
                  <div className="w-16 h-16 rounded-2xl bg-[#F0EDFD] text-[#5B3DF0] flex items-center justify-center mb-3 border border-[#E8E8EF]">
                    <Sparkles className="w-8 h-8" />
                  </div>
                  <h4 className="text-sm font-bold text-[#171717] mb-1">
                    Awaiting Input Images
                  </h4>
                  <p className="text-xs text-slate-600">
                    Upload a person photo and clothing reference on the left to activate the try-on synthesis engine.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Comparison Cards */}
      {isCompleted && (
        <div className="mt-5 pt-4 border-t border-[#E8E8EF]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
              Source Transformation Summary:
            </span>
            <button
              type="button"
              onClick={onReset}
              aria-label="Start a new virtual try-on session"
              className="text-xs font-semibold text-[#5B3DF0] hover:underline flex items-center gap-1 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none rounded"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Start New Try-On</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Person Source */}
            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-[#F5F4F8] border border-[#E8E8EF]">
              <div className="w-10 h-10 rounded-lg overflow-hidden bg-white border border-[#E8E8EF] flex-shrink-0">
                {person.previewUrl && (
                  <img src={person.previewUrl} alt="Person" className="w-full h-full object-cover" loading="lazy" />
                )}
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-[#16A34A] uppercase">Identity Source</span>
                <span className="block text-xs font-semibold text-[#171717] truncate">{person.name}</span>
              </div>
            </div>

            {/* Garment Reference */}
            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-[#F5F4F8] border border-[#E8E8EF]">
              <div className="w-10 h-10 rounded-lg overflow-hidden bg-white border border-[#E8E8EF] flex-shrink-0 flex items-center justify-center p-0.5">
                {garment.previewUrl && (
                  <img src={garment.previewUrl} alt="Garment" className="w-full h-full object-contain" loading="lazy" />
                )}
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-[#5B3DF0] uppercase">Pattern Reference</span>
                <span className="block text-xs font-semibold text-[#171717] truncate">{garment.name}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
