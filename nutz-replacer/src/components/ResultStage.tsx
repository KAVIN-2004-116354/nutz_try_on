import React, { useState, useRef, useEffect } from 'react';
import { 
  Sparkles, Download, RefreshCw, RotateCcw, Maximize2, SplitSquareHorizontal, 
  CheckCircle2, Zap
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
  'Mapping 33-point MediaPipe facial & pose landmarks...',
  'Extracting fabric weave, texture & embroidery matrices...',
  'Aligning FLUX-DEV-012 dual-panel spatial reference canvas...',
  'Synthesizing photorealistic textile drape & lighting...',
  'Rendering 1024×1024 master high-resolution look...',
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
  const [zoomLens, setZoomLens] = useState<{ active: boolean; x: number; y: number }>({
    active: false,
    x: 0,
    y: 0,
  });
  const stageContainerRef = useRef<HTMLDivElement>(null);
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
    if (isDragging) {
      const rect = e.currentTarget.getBoundingClientRect();
      handleSliderMove(e.clientX, rect);
    }

    if (!showSlider && isCompleted) {
      const rect = e.currentTarget.getBoundingClientRect();
      setZoomLens({
        active: true,
        x: ((e.clientX - rect.left) / rect.width) * 100,
        y: ((e.clientY - rect.top) / rect.height) * 100,
      });
    }
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
    <div className="bg-white rounded-3xl border border-[#E8E8EF] shadow-elevated p-6 flex flex-col justify-between h-full transition-all duration-400 hover:border-[#5B3DF0]/30">
      {/* Top Action Bar & Primary CTA */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#E8E8EF] mb-5">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-8 h-8 rounded-xl bg-[#F0EDFD] text-[#5B3DF0] font-extrabold text-xs flex items-center justify-center border border-[#5B3DF0]/20 shadow-sm">
                03
              </span>
              <h3 className="text-lg font-extrabold text-[#171717]">
                {isCompleted ? 'Your Custom Look Is Ready!' : 'Photorealistic Try-On Stage'}
              </h3>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              1024×1024 High-Resolution Dual-Panel FLUX Latents
            </p>
          </div>

          {/* Primary CTA: "Generate My Look" with shimmer & glow */}
          <button
            type="button"
            onClick={onGenerate}
            disabled={!canGenerate || isProcessing}
            aria-label={isProcessing ? 'Generating try-on look' : isCompleted ? 'Generate try-on again' : 'Generate virtual try-on look'}
            className={`min-h-[52px] px-8 py-3.5 rounded-2xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2.5 cursor-pointer relative overflow-hidden group ${
              canGenerate && !isProcessing
                ? 'bg-[#5B3DF0] hover:bg-[#4B2EE0] active:scale-[0.98] text-white shadow-elevated shadow-glow-purple hover:scale-[1.02]'
                : 'bg-gray-100 text-gray-400 border border-[#E8E8EF] cursor-not-allowed shadow-none'
            }`}
          >
            {canGenerate && !isProcessing && (
              <span className="absolute inset-0 w-1/2 h-full bg-white/20 skew-x-12 -translate-x-full group-hover:animate-shimmer-slide pointer-events-none" />
            )}

            {isProcessing ? (
              <>
                <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
                <span className="tracking-wide">Synthesizing Look...</span>
              </>
            ) : isCompleted ? (
              <>
                <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                <span>Generate New Variation</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 animate-pulse text-amber-300" />
                <span>Generate Virtual Try-On</span>
              </>
            )}
          </button>
        </div>

        {/* Viewport / Stage Container */}
        <div 
          ref={stageContainerRef}
          className="relative bg-gradient-to-b from-[#FAF9FD] to-[#F5F4F8] border border-[#E8E8EF] rounded-2xl overflow-hidden min-h-[480px] flex items-center justify-center shadow-inner"
        >
          {/* PROCESSING STATE SCREEN WITH SCANLINE LASER ANIMATION */}
          {isProcessing && (
            <div className="absolute inset-0 bg-[#0F0F16]/95 backdrop-blur-md z-30 flex flex-col items-center justify-center p-8 text-center text-white">
              {/* Animated AI Laser Canvas Scan */}
              <div className="relative w-52 h-64 rounded-2xl overflow-hidden border border-white/20 shadow-2xl mb-6 bg-black flex items-center justify-center">
                {person.previewUrl && (
                  <img
                    src={person.previewUrl}
                    alt="Scanning model"
                    className="w-full h-full object-cover opacity-60 scale-105"
                  />
                )}
                {/* Vertical Laser Beam with glowing cyan/violet scanline */}
                <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-[#5B3DF0] to-transparent shadow-[0_0_20px_#5B3DF0] animate-laser" />
                <div className="absolute inset-x-0 h-8 bg-gradient-to-b from-[#5B3DF0]/30 to-transparent animate-laser" />

                {/* Center Pulse Radar */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-16 h-16 rounded-full border border-[#5B3DF0]/50 animate-ping" />
                  <div className="w-8 h-8 rounded-full bg-[#5B3DF0]/40 backdrop-blur-sm flex items-center justify-center">
                    <Zap className="w-4 h-4 text-white fill-current" />
                  </div>
                </div>

                {/* Live elapsed counter pill */}
                <div className="absolute bottom-2.5 px-3 py-1 rounded-full bg-black/80 backdrop-blur-md text-[11px] font-mono font-bold text-white border border-white/10">
                  {Math.round(elapsedSec)}s elapsed
                </div>
              </div>

              <h4 className="text-xl font-extrabold text-white mb-2 tracking-tight">
                Diffusion Inpainting in Progress
              </h4>
              <p className="text-xs text-[#8F77F8] font-bold max-w-sm mb-6 animate-pulse min-h-[20px]">
                {STAGE_LABELS[Math.min(currentStage - 1, STAGE_LABELS.length - 1)]}
              </p>

              {/* Progress Step Bar */}
              <div className="flex items-center gap-1.5 max-w-xs w-full mb-3">
                {STAGE_LABELS.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-2 flex-1 rounded-full transition-all duration-500 ${
                      idx < currentStage
                        ? 'bg-[#5B3DF0] shadow-[0_0_12px_#5B3DF0]'
                        : 'bg-white/15'
                    }`}
                  />
                ))}
              </div>

              <span className="text-[11px] text-slate-400 font-mono tracking-wide">
                FLUX-DEV-012 • 1024×1024 Photorealistic Spatial Attention
              </span>
            </div>
          )}

          {/* COMPLETED RESULT EXPERIENCE */}
          {isCompleted && resultImageUrl ? (
            <div
              className="relative w-full h-[530px] select-none overflow-hidden flex items-center justify-center touch-none group"
              onMouseMove={handleMouseMove}
              onMouseUp={() => setIsDragging(false)}
              onMouseLeave={() => {
                setIsDragging(false);
                setZoomLens((prev) => ({ ...prev, active: false }));
              }}
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
                    className="absolute inset-0 overflow-hidden pointer-events-none transition-none"
                    style={{ width: `${sliderPosition}%` }}
                  >
                    <img
                      src={person.previewUrl}
                      alt="Original Person"
                      className="w-full h-full object-contain"
                      style={{ width: '100%', maxWidth: 'none' }}
                    />
                    <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-md text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider shadow-md border border-white/10">
                      Before (Original Model)
                    </div>
                  </div>

                  <div className="absolute top-4 right-4 bg-[#5B3DF0] text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider shadow-md shadow-glow-sm">
                    After (FLUX Try-On)
                  </div>

                  {/* Vertical Split Line & Draggable Handle with Luminous Thumb */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white shadow-2xl cursor-ew-resize flex items-center justify-center z-20"
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
                    <div className="w-9 h-9 bg-white border-2 border-[#5B3DF0] rounded-full shadow-elevated flex items-center justify-center text-[#5B3DF0] text-xs font-black hover:scale-115 active:scale-95 transition-all select-none">
                      ⟷
                    </div>
                  </div>
                </div>
              ) : (
                /* Full Single Image View with interactive fabric zoom */
                <div className="relative w-full h-full flex items-center justify-center">
                  <img
                    src={resultImageUrl}
                    alt="Virtual Try-On Result"
                    className="w-full h-full object-contain"
                  />

                  {/* Interactive Loupe Zoom Glass */}
                  {zoomLens.active && (
                    <div
                      className="absolute w-44 h-44 rounded-full border-3 border-white shadow-2xl pointer-events-none overflow-hidden hidden md:block"
                      style={{
                        left: `calc(${zoomLens.x}% - 88px)`,
                        top: `calc(${zoomLens.y}% - 88px)`,
                        backgroundImage: `url(${resultImageUrl})`,
                        backgroundPosition: `${zoomLens.x}% ${zoomLens.y}%`,
                        backgroundSize: '350%',
                        boxShadow: '0 0 30px rgba(0,0,0,0.5)',
                      }}
                    />
                  )}
                </div>
              )}

              {/* Top Viewport Controls */}
              <div className="absolute top-4 left-4 flex items-center gap-2 z-20">
                {person.previewUrl && (
                  <button
                    type="button"
                    onClick={() => setShowSlider(!showSlider)}
                    aria-label={showSlider ? 'Exit comparison slider' : 'Compare before and after'}
                    className={`min-h-[38px] px-3.5 py-1.5 rounded-xl text-xs font-bold border shadow-sm transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 ${
                      showSlider
                        ? 'bg-[#5B3DF0] text-white border-[#5B3DF0]'
                        : 'bg-white/95 text-[#171717] border-[#E8E8EF] hover:bg-white'
                    }`}
                  >
                    <SplitSquareHorizontal className="w-3.5 h-3.5" />
                    <span>{showSlider ? 'Single View' : 'Compare Split'}</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={onOpenZoom}
                  aria-label="Open full-screen HD view"
                  className="min-h-[38px] min-w-[38px] p-2 rounded-xl bg-white/95 hover:bg-white text-[#171717] border border-[#E8E8EF] shadow-sm transition-all cursor-pointer flex items-center justify-center active:scale-95"
                  title="Full-Screen HD View"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Floating Bottom Action Strip */}
              <div className="absolute bottom-4 inset-x-4 flex items-center justify-between z-20 pointer-events-none">
                <div className="flex items-center gap-2 pointer-events-auto">
                  <span className="px-3 py-1.5 rounded-xl bg-black/75 backdrop-blur-md text-white text-[11px] font-mono font-bold shadow-md">
                    1024 × 1024 HD
                  </span>
                  <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white/90 backdrop-blur-md text-slate-700 text-[11px] font-bold shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A]" />
                    Photorealistic
                  </span>
                </div>

                <a
                  href={resultImageUrl}
                  download={`nutz_replacer_${Date.now()}.png`}
                  aria-label="Download virtual try-on result in high-resolution PNG"
                  className="pointer-events-auto min-h-[44px] px-5 py-2.5 rounded-2xl bg-white/95 hover:bg-white text-[#171717] font-bold text-xs border border-[#E8E8EF] shadow-elevated flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                >
                  <Download className="w-4 h-4 text-[#5B3DF0]" />
                  <span>Download High-Res</span>
                </a>
              </div>
            </div>
          ) : (
            /* READY / WAITING STATE */
            <div className="flex flex-col items-center justify-center p-8 text-center">
              {person.previewUrl ? (
                <div className="flex flex-col items-center max-w-sm">
                  <div className="relative w-48 h-60 rounded-2xl overflow-hidden border border-[#E8E8EF] bg-white shadow-card mb-4 group hover:scale-[1.02] transition-transform duration-300">
                    <img
                      src={person.previewUrl}
                      alt="Target Person"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex items-end justify-center p-3">
                      <span className="text-[11px] text-white font-bold tracking-wide flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A]" />
                        Model Identity Locked
                      </span>
                    </div>
                  </div>
                  <h4 className="text-base font-extrabold text-[#171717] mb-1">
                    Ready to Generate Try-On
                  </h4>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    {garment.previewUrl
                      ? 'Both images locked. Click "Generate Virtual Try-On" above to synthesize.'
                      : 'Select or upload your garment reference in Step 02.'}
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center max-w-sm text-slate-600">
                  <div className="w-20 h-20 rounded-3xl bg-[#F0EDFD] text-[#5B3DF0] flex items-center justify-center mb-4 border border-[#5B3DF0]/20 shadow-sm animate-float-gentle">
                    <Sparkles className="w-10 h-10 animate-spin" style={{ animationDuration: '8s' }} />
                  </div>
                  <h4 className="text-base font-extrabold text-[#171717] mb-1">
                    Awaiting Studio Selection
                  </h4>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    Choose a model in Step 01 and an outfit in Step 02 to activate the 1024×1024 synthesis canvas.
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
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Applied Transformation:
            </span>
            <button
              type="button"
              onClick={onReset}
              aria-label="Start a new virtual try-on session"
              className="text-xs font-bold text-[#5B3DF0] hover:underline flex items-center gap-1 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Studio</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Person Source */}
            <div className="flex items-center gap-2.5 p-2.5 rounded-2xl bg-[#F9F9FC] border border-[#E8E8EF]">
              <div className="w-11 h-11 rounded-xl overflow-hidden bg-white border border-[#E8E8EF] flex-shrink-0">
                {person.previewUrl && (
                  <img src={person.previewUrl} alt="Person" className="w-full h-full object-cover" />
                )}
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-[#16A34A] uppercase tracking-wider">Identity Model</span>
                <span className="block text-xs font-bold text-[#171717] truncate">{person.name}</span>
              </div>
            </div>

            {/* Garment Reference */}
            <div className="flex items-center gap-2.5 p-2.5 rounded-2xl bg-[#F9F9FC] border border-[#E8E8EF]">
              <div className="w-11 h-11 rounded-xl overflow-hidden bg-white border border-[#E8E8EF] flex-shrink-0 flex items-center justify-center p-0.5">
                {garment.previewUrl && (
                  <img src={garment.previewUrl} alt="Garment" className="w-full h-full object-contain" />
                )}
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-[#5B3DF0] uppercase tracking-wider">Outfit Reference</span>
                <span className="block text-xs font-bold text-[#171717] truncate">{garment.name}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
