import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { PersonUploadCard } from './components/PersonUploadCard';
import { GarmentUploadCard } from './components/GarmentUploadCard';
import { TryonBridge } from './components/TryonBridge';
import { ResultStage } from './components/ResultStage';
import { HowItWorksSection } from './components/HowItWorksSection';
import { FeatureSection } from './components/FeatureSection';
import { GenerationHistory } from './components/GenerationHistory';
import { Footer } from './components/Footer';
import { ImageModal } from './components/ImageModal';
import { MobileTryonArtboard } from './components/MobileTryonArtboard';
import { 
  CloudStatus, GenerationStatus, ImageInputState, TryonResult, HistoryItem 
} from './types';
import { getCloudStatus, executeIntelligentTryon } from './services/api';
import { SAMPLE_PERSONS, SAMPLE_GARMENTS } from './presets';
import { AlertCircle, X, Smartphone, Monitor, Columns } from 'lucide-react';

export const App: React.FC = () => {
  // Artboard view mode: dynamically initialized from client viewport width
  const [viewMode, setViewMode] = useState<'side_by_side' | 'mobile_only' | 'desktop_only'>(() => {
    if (typeof window !== 'undefined' && window.innerWidth < 1024) {
      return 'mobile_only';
    }
    return 'side_by_side';
  });

  // Track window resize to ensure responsive view on physical phones
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768 && viewMode === 'side_by_side') {
        setViewMode('mobile_only');
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [viewMode]);

  // Cloud & Gateway Status
  const [cloudStatus, setCloudStatus] = useState<CloudStatus>({
    status: 'online',
    model: 'FLUX-DEV-012',
    provider: 'Nutz Railway Cloud',
    has_key: true,
  });

  // Input states (preloaded with default studio portrait & outfit for immediate review)
  const [person, setPerson] = useState<ImageInputState>({
    file: null,
    previewUrl: SAMPLE_PERSONS[0].imageUrl,
    name: SAMPLE_PERSONS[0].name,
    isCustom: false,
    resolution: 'Studio Portrait HD',
  });

  const [garment, setGarment] = useState<ImageInputState>({
    file: null,
    previewUrl: SAMPLE_GARMENTS[0].imageUrl,
    name: SAMPLE_GARMENTS[0].name,
    isCustom: false,
    resolution: 'Catalog HD',
  });

  const [selectedCategory, setSelectedCategory] = useState<string>('shirt');

  // Track the person and garment used in the most recent generation to detect changes
  const [lastGeneratedPerson, setLastGeneratedPerson] = useState<string | null>(SAMPLE_PERSONS[0].imageUrl);
  const [lastGeneratedGarment, setLastGeneratedGarment] = useState<string | null>(SAMPLE_GARMENTS[0].imageUrl);

  // Selection changed detection
  const selectionChanged = Boolean(
    (person.previewUrl !== lastGeneratedPerson || garment.previewUrl !== lastGeneratedGarment) &&
    person.previewUrl &&
    garment.previewUrl
  );

  // Generation execution state
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>('ready');
  const [currentStage, setCurrentStage] = useState<number>(1);
  const [result, setResult] = useState<TryonResult | null>(null);
  const [elapsedSec, setElapsedSec] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  // Full-screen zoom modal
  const [isZoomOpen, setIsZoomOpen] = useState<boolean>(false);

  // History state
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Initial cloud health check & periodic polling
  useEffect(() => {
    let isMounted = true;
    const fetchStatus = async () => {
      const status = await getCloudStatus();
      if (isMounted) setCloudStatus(status);
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 20000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Timer tracker for generation duration
  useEffect(() => {
    if (generationStatus === 'processing' || generationStatus === 'uploading') {
      const startTime = Date.now();
      timerRef.current = window.setInterval(() => {
        setElapsedSec((Date.now() - startTime) / 1000);
      }, 200);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [generationStatus]);

  const canGenerate = Boolean(
    person.previewUrl &&
    garment.previewUrl &&
    generationStatus !== 'processing' &&
    generationStatus !== 'uploading'
  );

  const handleGenerate = async () => {
    if (!person.previewUrl) {
      setErrorMessage('Please upload or select a target person photograph in Step 01.');
      return;
    }
    if (!garment.previewUrl) {
      setErrorMessage('Please upload or select a clothing reference in Step 02.');
      return;
    }
    if (generationStatus === 'processing' || generationStatus === 'uploading') {
      return;
    }

    setErrorMessage(null);
    setGenerationStatus('uploading');
    setElapsedSec(0);
    setCurrentStage(1);

    try {
      // Stage tracker progression
      const s2 = window.setTimeout(() => {
        setGenerationStatus('processing');
        setCurrentStage(2);
      }, 1200);
      const s3 = window.setTimeout(() => setCurrentStage(3), 3500);
      const s4 = window.setTimeout(() => setCurrentStage(4), 6000);
      const s5 = window.setTimeout(() => setCurrentStage(5), 9000);

      // Execute Virtual Try-on exclusively via FLUX-DEV-012 Dual-Panel Pipeline
      const tryonResponse: TryonResult = await executeIntelligentTryon({
        personImage: person.file || person.previewUrl,
        garmentImage: garment.file || garment.previewUrl,
        category: selectedCategory,
        mode: 'auto',
      });

      clearTimeout(s2);
      clearTimeout(s3);
      clearTimeout(s4);
      clearTimeout(s5);
      setCurrentStage(5);

      setResult(tryonResponse);
      setGenerationStatus('completed');

      // Update generation anchors to clear selectionChanged notice
      setLastGeneratedPerson(person.previewUrl);
      setLastGeneratedGarment(garment.previewUrl);

      // Add to session history
      const resultUrl = tryonResponse.image_data || tryonResponse.result_url;
      const historyItem: HistoryItem = {
        id: `tryon-${Date.now()}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        personThumb: person.previewUrl || '',
        garmentThumb: garment.previewUrl || '',
        resultUrl: resultUrl,
        personName: person.name,
        garmentName: garment.name,
        category: selectedCategory,
        model: 'FLUX-DEV-012',
        latencySec: tryonResponse.latency_seconds || elapsedSec,
        width: tryonResponse.width || 1024,
        height: tryonResponse.height || 1024,
        fileSizeStr: '1.84 MB',
        status: 'completed',
      };
      setHistory((prev) => [historyItem, ...prev]);

    } catch (err: any) {
      console.error('[Nutz Replacer Generation Error]:', err);
      setGenerationStatus('failed');
      setErrorMessage(
        err.message || 'Generation failed on FLUX-DEV-012 server. Please verify cloud link and retry.'
      );
    }
  };

  const handleReset = () => {
    setResult(null);
    setGenerationStatus('ready');
    setElapsedSec(0);
    setCurrentStage(1);
    setErrorMessage(null);
  };

  const handleSelectHistoryLook = (item: HistoryItem) => {
    setResult({
      status: 'success',
      result_url: item.resultUrl,
      image_data: item.resultUrl,
      latency_seconds: item.latencySec,
      inference_time_ms: item.latencySec * 1000,
      model_used: item.model,
      width: item.width,
      height: item.height,
    });
    setGenerationStatus('completed');
    const elem = document.getElementById('tryon-workspace');
    if (elem) elem.scrollIntoView({ behavior: 'smooth' });
  };

  // Render Desktop Studio Content
  const renderDesktopStudio = () => (
    <div className="min-h-screen bg-[#F5F4F8] text-[#171717] font-sans selection:bg-[#F0EDFD] selection:text-[#5B3DF0]">
      {/* 1. Navigation Bar */}
      <Navbar
        cloudStatus={cloudStatus}
        historyCount={history.length}
        onOpenHistory={() => {
          const elem = document.getElementById('gallery');
          if (elem) elem.scrollIntoView({ behavior: 'smooth' });
        }}
      />

      {/* 2. Hero Section */}
      <HeroSection />

      {/* 3. Virtual Try-On Workspace */}
      <section id="tryon-workspace" className="py-16 scroll-mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-[#5B3DF0] bg-[#F0EDFD] px-3 py-1 rounded-full border border-[#E8E8EF] mb-2 inline-block">
                Interactive Workspace
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-[#171717] tracking-tight">
                AI Virtual Try-On Studio
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 mt-1">
                Upload your target person and clothing reference to condition the FLUX-DEV-012 inpainting engine.
              </p>
            </div>

            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#E8E8EF] shadow-subtle text-xs text-slate-600">
              <span className="w-2 h-2 rounded-full bg-[#16A34A]" />
              <span className="font-semibold text-[#171717]">Dual-Panel Spatial Conditioning</span>
            </div>
          </div>

          {errorMessage && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center justify-between shadow-subtle animate-fadeIn">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-[#DC2626] flex-shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                aria-label="Dismiss error notification"
                className="text-red-500 hover:text-red-800 transition p-1 rounded focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:outline-none"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div className="lg:col-span-6 space-y-4">
              <PersonUploadCard
                person={person}
                setPerson={setPerson}
                disabled={generationStatus === 'processing'}
                onError={setErrorMessage}
              />

              <TryonBridge
                hasPerson={Boolean(person.previewUrl)}
                hasGarment={Boolean(garment.previewUrl)}
              />

              <GarmentUploadCard
                garment={garment}
                setGarment={setGarment}
                selectedCategory={selectedCategory}
                setSelectedCategory={setSelectedCategory}
                disabled={generationStatus === 'processing'}
                onError={setErrorMessage}
              />
            </div>

            <div className="lg:col-span-6 sticky top-28">
              <ResultStage
                person={person}
                garment={garment}
                selectedCategory={selectedCategory}
                result={result}
                generationStatus={generationStatus}
                currentStage={currentStage}
                elapsedSec={elapsedSec}
                canGenerate={canGenerate}
                onGenerate={handleGenerate}
                onReset={handleReset}
                onOpenZoom={() => setIsZoomOpen(true)}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 4. How It Works Section */}
      <HowItWorksSection />

      {/* 5. Features Section */}
      <FeatureSection />

      {/* 6. Recent Creations Gallery */}
      <GenerationHistory
        history={history}
        onSelectResult={handleSelectHistoryLook}
        onClearHistory={() => setHistory([])}
      />

      {/* 7. Footer */}
      <Footer />
    </div>
  );

  return (
    <div className="min-h-screen bg-[#EAE8F2] text-[#171717] font-sans antialiased">
      {/* Top Designer Canvas Toolbar */}
      <header className="bg-white/95 backdrop-blur-md border-b border-[#D5D3E5] sticky top-0 z-50 px-4 py-2.5 flex items-center justify-between shadow-subtle">
        <div className="flex items-center">
          <div>
            <span className="font-extrabold text-[15px] text-[#171717] tracking-tight">
              NUTZ REPLACER <span className="text-[#5B3DF0]">CANVAS</span>
            </span>
            <span className="hidden sm:inline-block ml-2 text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#F0EDFD] text-[#5B3DF0] border border-[#5B3DF0]/20">
              Dual Artboard View
            </span>
          </div>
        </div>

        {/* Artboard View Switcher */}
        <div className="flex items-center bg-[#F5F4F8] p-1 rounded-xl border border-[#E8E8EF]">
          <button
            type="button"
            onClick={() => setViewMode('side_by_side')}
            className={`min-h-[36px] px-3.5 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
              viewMode === 'side_by_side'
                ? 'bg-[#5B3DF0] text-white shadow-sm'
                : 'text-slate-600 hover:text-[#171717]'
            }`}
          >
            <Columns className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Side by Side</span>
            <span className="md:hidden">Both</span>
          </button>
          <button
            type="button"
            onClick={() => setViewMode('mobile_only')}
            className={`min-h-[36px] px-3.5 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
              viewMode === 'mobile_only'
                ? 'bg-[#5B3DF0] text-white shadow-sm'
                : 'text-slate-600 hover:text-[#171717]'
            }`}
          >
            <Smartphone className="w-3.5 h-3.5" />
            <span>Mobile (390×844)</span>
          </button>
          <button
            type="button"
            onClick={() => setViewMode('desktop_only')}
            className={`min-h-[36px] px-3.5 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none ${
              viewMode === 'desktop_only'
                ? 'bg-[#5B3DF0] text-white shadow-sm'
                : 'text-slate-600 hover:text-[#171717]'
            }`}
          >
            <Monitor className="w-3.5 h-3.5" />
            <span>Desktop</span>
          </button>
        </div>

        {/* Engine status */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#F5F4F8] border border-[#E8E8EF] text-xs font-bold text-[#171717]">
          <span className="w-2 h-2 rounded-full bg-[#16A34A] animate-pulse" />
          <span>FLUX-DEV-012 Live</span>
        </div>
      </header>

      {/* Main Artboard Canvas Presentation */}
      {viewMode === 'side_by_side' ? (
        <div className="p-4 sm:p-6 lg:p-8 flex flex-col xl:flex-row gap-8 items-start justify-center max-w-[1780px] mx-auto overflow-x-auto">
          {/* LEFT ARTBOARD: Desktop Studio */}
          <div className="flex-1 w-full min-w-0 xl:min-w-[840px] max-w-6xl">
            {/* Artboard Header Label */}
            <div className="flex items-center justify-between mb-3 px-2">
              <div className="flex items-center gap-2">
                <Monitor className="w-4 h-4 text-[#5B3DF0]" />
                <span className="text-xs font-extrabold uppercase tracking-wider text-slate-600">
                  Desktop Artboard (1280 × 900)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-600 bg-white/70 px-2.5 py-0.5 rounded-md border border-[#D5D3E5]">
                Responsive Studio Viewport
              </span>
            </div>

            {/* Desktop Artboard Container */}
            <div className="rounded-[28px] overflow-hidden shadow-2xl border border-[#D5D3E5] bg-white">
              {renderDesktopStudio()}
            </div>
          </div>

          {/* RIGHT ARTBOARD: Mobile Artboard (390 × 844) */}
          <div className="flex-shrink-0 mx-auto xl:mx-0 sticky top-20">
            {/* Artboard Header Label */}
            <div className="flex items-center justify-between mb-3 px-2 w-[390px]">
              <div className="flex items-center gap-2">
                <Smartphone className="w-4 h-4 text-[#5B3DF0]" />
                <span className="text-xs font-extrabold uppercase tracking-wider text-slate-600">
                  Mobile Artboard (390 × 844 px)
                </span>
              </div>
              <span className="text-[11px] font-mono text-[#5B3DF0] bg-[#F0EDFD] px-2.5 py-0.5 rounded-md border border-[#5B3DF0]/30 font-bold">
                iPhone 14 / 15
              </span>
            </div>

            {/* The 390 × 844 Mobile Artboard */}
            <MobileTryonArtboard
              person={person}
              setPerson={setPerson}
              garment={garment}
              setGarment={setGarment}
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              result={result}
              generationStatus={generationStatus}
              canGenerate={canGenerate}
              onGenerate={handleGenerate}
              onOpenZoom={() => setIsZoomOpen(true)}
              selectionChanged={selectionChanged}
            />
          </div>
        </div>
      ) : viewMode === 'mobile_only' ? (
        /* Mobile Artboard Only (Centered) */
        <div className="py-8 px-4 flex flex-col items-center justify-center min-h-[calc(100vh-60px)]">
          <div className="flex items-center justify-between mb-3 px-2 w-[390px]">
            <div className="flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-[#5B3DF0]" />
              <span className="text-xs font-extrabold uppercase tracking-wider text-slate-600">
                Mobile Artboard (390 × 844 px)
              </span>
            </div>
            <span className="text-[11px] font-mono text-[#5B3DF0] bg-[#F0EDFD] px-2.5 py-0.5 rounded-md border border-[#5B3DF0]/30 font-bold">
              390 × 844 Fixed
            </span>
          </div>

          <MobileTryonArtboard
            person={person}
            setPerson={setPerson}
            garment={garment}
            setGarment={setGarment}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            result={result}
            generationStatus={generationStatus}
            canGenerate={canGenerate}
            onGenerate={handleGenerate}
            onOpenZoom={() => setIsZoomOpen(true)}
            selectionChanged={selectionChanged}
          />
        </div>
      ) : (
        /* Desktop Only Full Width */
        <div>
          {renderDesktopStudio()}
        </div>
      )}

      {/* Full-Screen Zoom Modal */}
      <ImageModal
        isOpen={isZoomOpen}
        onClose={() => setIsZoomOpen(false)}
        imageUrl={result?.image_data || result?.result_url || ''}
        title="High-Definition Virtual Try-On Look"
        resolution="1024 × 1024 HD"
        fileSizeStr="1.84 MB"
      />
    </div>
  );
};

export default App;
