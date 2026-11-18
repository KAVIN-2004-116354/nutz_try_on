import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Download, RefreshCw, RotateCcw, Maximize2, SplitSquareHorizontal, 
  CheckCircle2, ArrowRight, Mail
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
  errorMessage?: string | null;
}

const STAGE_LABELS = [
  'Measuring posture, shoulder span & body contours...',
  'Analyzing textile weave, print scale & fabric drape...',
  'Aligning garment seams and tailoring to model silhouette...',
  'Simulating photorealistic illumination and fabric tension...',
  'Finalizing high-resolution fitting presentation...',
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
  errorMessage,
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
    <div className="bg-white rounded-3xl border border-[#E8E8EF] shadow-card p-6 flex flex-col justify-between h-full transition-all duration-300 hover:border-[#171717]/20 hover:shadow-xl">
      <div>
        {/* Top Action Bar & Primary CTA */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#E8E8EF] mb-5">
          <div>
            <h3 className="text-lg font-extrabold text-[#171717]">
              {isCompleted ? 'Your Custom Fitting Is Ready' : 'Virtual Fitting Mirror'}
            </h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              High-resolution fabric draping & photographic fit
            </p>
          </div>

          {/* Primary CTA Button: Clean, Bold Luxury Fashion */}
          <motion.button
            type="button"
            whileHover={canGenerate && !isProcessing ? { scale: 1.03, y: -1 } : {}}
            whileTap={canGenerate && !isProcessing ? { scale: 0.97 } : {}}
            onClick={onGenerate}
            disabled={!canGenerate || isProcessing}
            aria-label={isProcessing ? 'Draping outfit' : isCompleted ? 'Generate another fitting' : 'Try on outfit'}
            className={`min-h-[50px] px-8 py-3.5 rounded-2xl font-bold text-sm transition-colors duration-200 flex items-center justify-center gap-2.5 cursor-pointer shadow-xl ${
              canGenerate && !isProcessing
                ? 'bg-[#171717] hover:bg-[#2B2B38] text-white hover:shadow-2xl'
                : 'bg-gray-100 text-gray-400 border border-[#E8E8EF] cursor-not-allowed shadow-none'
            }`}
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span className="tracking-wide">Draping Outfit...</span>
              </>
            ) : isCompleted ? (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Try Another Combination</span>
              </>
            ) : generationStatus === 'failed' ? (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Retry Fitting</span>
              </>
            ) : (
              <>
                <span>Try On Outfit</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </motion.button>
        </div>

        {/* Viewport / Mirror Stage Container */}
        <div 
          ref={stageContainerRef}
          className="relative bg-gradient-to-b from-[#FAF9FD] to-[#F5F4F8] border border-[#E8E8EF] rounded-2xl overflow-hidden min-h-[480px] flex items-center justify-center shadow-inner"
        >
          {/* PROCESSING STATE SCREEN - Clean & Sophisticated */}
          {isProcessing && (
            <div className="absolute inset-0 bg-white/95 backdrop-blur-md z-30 flex flex-col items-center justify-center p-8 text-center text-[#171717]">
              {/* Animated Model Scan with elegant hairline */}
              <div className="relative w-48 h-60 rounded-2xl overflow-hidden border border-[#E8E8EF] shadow-lg mb-6 bg-slate-100 flex items-center justify-center">
                {person.previewUrl && (
                  <img
                    src={person.previewUrl}
                    alt="Fitting in progress"
                    className="w-full h-full object-cover opacity-80"
                  />
                )}
                {/* Clean vertical scanline */}
                <div className="absolute inset-x-0 h-0.5 bg-[#171717] shadow-[0_0_12px_rgba(0,0,0,0.5)] animate-laser" />

                {/* Elapsed counter */}
                <div className="absolute bottom-2.5 px-3 py-1 rounded-full bg-black/80 backdrop-blur-md text-[10px] font-mono font-bold text-white">
                  {Math.round(elapsedSec)}s
                </div>
              </div>

              <h4 className="text-xl font-extrabold text-[#171717] mb-2 tracking-tight">
                Tailoring Your Look
              </h4>
              <p className="text-xs text-slate-600 font-semibold max-w-sm mb-6 min-h-[20px]">
                {STAGE_LABELS[Math.min(currentStage - 1, STAGE_LABELS.length - 1)]}
              </p>

              {/* Progress Step Bar */}
              <div className="flex items-center gap-1.5 max-w-xs w-full mb-3">
                {STAGE_LABELS.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                      idx < currentStage
                        ? 'bg-[#171717]'
                        : 'bg-slate-200'
                    }`}
                  />
                ))}
              </div>

              <span className="text-[11px] text-slate-400 font-medium">
                Photographic Fabric Fitting Studio
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
                    <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-md text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider shadow-md">
                      Original
                    </div>
                  </div>

                  <div className="absolute top-4 right-4 bg-[#171717] text-white text-[10px] font-extrabold px-3 py-1 rounded-full uppercase tracking-wider shadow-md">
                    Fitted Look
                  </div>

                  {/* Vertical Split Line & Handle */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white shadow-2xl cursor-ew-resize flex items-center justify-center z-20"
                    style={{ left: `${sliderPosition}%` }}
                    onMouseDown={() => setIsDragging(true)}
                    onTouchStart={() => setIsDragging(true)}
                    role="separator"
                    aria-label="Comparison slider handle"
                    aria-valuenow={Math.round(sliderPosition)}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    tabIndex={0}
                  >
                    <div className="w-8 h-8 bg-white border border-[#E8E8EF] rounded-full shadow-lg flex items-center justify-center text-[#171717] text-xs font-black hover:scale-110 active:scale-95 transition-all select-none">
                      ⟷
                    </div>
                  </div>
                </div>
              ) : (
                /* Full Single Image View */
                <div className="relative w-full h-full flex items-center justify-center">
                  <img
                    src={resultImageUrl}
                    alt="Virtual Try-On Result"
                    className="w-full h-full object-contain"
                  />

                  {/* Interactive Loupe Zoom Glass */}
                  {zoomLens.active && (
                    <div
                      className="absolute w-44 h-44 rounded-full border-2 border-white shadow-2xl pointer-events-none overflow-hidden hidden md:block"
                      style={{
                        left: `calc(${zoomLens.x}% - 88px)`,
                        top: `calc(${zoomLens.y}% - 88px)`,
                        backgroundImage: `url(${resultImageUrl})`,
                        backgroundPosition: `${zoomLens.x}% ${zoomLens.y}%`,
                        backgroundSize: '350%',
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
                    className={`min-h-[36px] px-3.5 py-1.5 rounded-xl text-xs font-bold border shadow-sm transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 ${
                      showSlider
                        ? 'bg-[#171717] text-white border-[#171717]'
                        : 'bg-white/95 text-[#171717] border-[#E8E8EF] hover:bg-white'
                    }`}
                  >
                    <SplitSquareHorizontal className="w-3.5 h-3.5" />
                    <span>{showSlider ? 'Single View' : 'Compare Before/After'}</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={onOpenZoom}
                  className="min-h-[36px] min-w-[36px] p-2 rounded-xl bg-white/95 hover:bg-white text-[#171717] border border-[#E8E8EF] shadow-sm transition-all cursor-pointer flex items-center justify-center active:scale-95"
                  title="Full-Screen High-Resolution"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Floating Bottom Action Strip */}
              <div className="absolute bottom-4 inset-x-4 flex items-center justify-between z-20 pointer-events-none">
                <div className="flex items-center gap-2 pointer-events-auto">
                  <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/90 backdrop-blur-md text-slate-800 text-[11px] font-bold shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A]" />
                    Photographic Quality
                  </span>
                </div>

                <a
                  href={resultImageUrl}
                  download={`nutz_fitting_${Date.now()}.png`}
                  className="pointer-events-auto min-h-[44px] px-5 py-2.5 rounded-2xl bg-white/95 hover:bg-white text-[#171717] font-bold text-xs border border-[#E8E8EF] shadow-lg flex items-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                >
                  <Download className="w-4 h-4 text-[#171717]" />
                  <span>Download Look</span>
                </a>
              </div>
            </div>
          ) : generationStatus === 'failed' ? (
            /* FAILED / RETRY STATE */
            <div className="flex flex-col items-center justify-center p-8 text-center max-w-sm animate-fadeIn">
              <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mb-4 border border-amber-200 shadow-sm">
                {errorMessage && /contact admin|quota/i.test(errorMessage) ? (
                  <Mail className="w-6 h-6 stroke-[1.8]" />
                ) : (
                  <RotateCcw className="w-6 h-6 stroke-[1.8]" />
                )}
              </div>
              <h4 className="text-base font-extrabold text-[#171717] mb-1">
                {errorMessage && /contact admin|quota/i.test(errorMessage)
                  ? 'Quota Limit Reached'
                  : 'Fitting Synthesis Unsuccessful'}
              </h4>
              <p className="text-xs text-slate-500 font-medium leading-relaxed mb-5">
                {errorMessage && /contact admin|quota/i.test(errorMessage)
                  ? 'The cloud generation quota has been exhausted. Please contact admin to recharge or upgrade access.'
                  : (errorMessage || 'The inference pipeline encountered an issue. Please contact admin or retry with different selections.')}
              </p>
              <div className="flex flex-col sm:flex-row items-center gap-2.5 w-full justify-center">
                {errorMessage && /contact admin|quota/i.test(errorMessage) ? (
                  <>
                    <a
                      href="mailto:admin@nutz.ai?subject=Virtual%20Try-On%20Image%20Quota%20Request"
                      className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-[#171717] text-white font-bold text-xs flex items-center justify-center gap-2 hover:bg-[#2B2B38] transition-all shadow-md active:scale-95 cursor-pointer whitespace-nowrap"
                    >
                      <Mail className="w-3.5 h-3.5" />
                      <span>Contact Admin</span>
                    </a>
                    <button
                      type="button"
                      onClick={onGenerate}
                      disabled={!canGenerate}
                      className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs flex items-center justify-center gap-1.5 transition-all active:scale-95 cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Retry</span>
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={onGenerate}
                    disabled={!canGenerate}
                    className="px-6 py-2.5 rounded-xl bg-[#171717] text-white font-bold text-xs flex items-center gap-2 hover:bg-[#2B2B38] transition-all shadow-md active:scale-95 cursor-pointer"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Retry Fitting</span>
                  </button>
                )}
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
                        Model Ready
                      </span>
                    </div>
                  </div>
                  <h4 className="text-base font-extrabold text-[#171717] mb-1">
                    Ready for Virtual Fitting
                  </h4>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    {garment.previewUrl
                      ? 'Both selections ready. Click "Try On Outfit" above to generate.'
                      : 'Choose an outfit in the Wardrobe section to proceed.'}
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center max-w-sm text-slate-600">
                  <div className="w-16 h-16 rounded-2xl bg-[#F5F4F8] text-[#171717] flex items-center justify-center mb-4 border border-[#E8E8EF] shadow-sm">
                    <ArrowRight className="w-6 h-6 stroke-[1.8]" />
                  </div>
                  <h4 className="text-base font-extrabold text-[#171717] mb-1">
                    Awaiting Selection
                  </h4>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    Select a model on the left and choose an outfit to begin your virtual fitting.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Summary Strip */}
      {isCompleted && (
        <div className="mt-5 pt-4 border-t border-[#E8E8EF]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Fitting Details:
            </span>
            <button
              type="button"
              onClick={onReset}
              className="text-xs font-bold text-[#171717] hover:underline flex items-center gap-1.5 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Selection</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center gap-2.5 p-2.5 rounded-2xl bg-[#F9F9FC] border border-[#E8E8EF]">
              <div className="w-11 h-11 rounded-xl overflow-hidden bg-white border border-[#E8E8EF] flex-shrink-0">
                {person.previewUrl && (
                  <img src={person.previewUrl} alt="Person" className="w-full h-full object-cover" />
                )}
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-[#16A34A] uppercase tracking-wider">Model</span>
                <span className="block text-xs font-bold text-[#171717] truncate">{person.name}</span>
              </div>
            </div>

            <div className="flex items-center gap-2.5 p-2.5 rounded-2xl bg-[#F9F9FC] border border-[#E8E8EF]">
              <div className="w-11 h-11 rounded-xl overflow-hidden bg-white border border-[#E8E8EF] flex-shrink-0 flex items-center justify-center p-0.5">
                {garment.previewUrl && (
                  <img src={garment.previewUrl} alt="Garment" className="w-full h-full object-contain" />
                )}
              </div>
              <div className="min-w-0">
                <span className="block text-[10px] font-bold text-[#171717] uppercase tracking-wider">Garment</span>
                <span className="block text-xs font-bold text-[#171717] truncate">{garment.name}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
