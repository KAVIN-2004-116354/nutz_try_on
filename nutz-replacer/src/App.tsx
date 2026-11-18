import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { LuxuryMarquee } from './components/ui/LuxuryMarquee';
import { PersonUploadCard } from './components/PersonUploadCard';
import { GarmentUploadCard } from './components/GarmentUploadCard';
import { TryonBridge } from './components/TryonBridge';
import { ResultStage } from './components/ResultStage';
import { HowItWorksSection } from './components/HowItWorksSection';
import { FeatureSection } from './components/FeatureSection';
import { GenerationHistory } from './components/GenerationHistory';
import { Footer } from './components/Footer';
import { ImageModal } from './components/ImageModal';
import { 
  CloudStatus, GenerationStatus, ImageInputState, TryonResult, HistoryItem 
} from './types';
import { getCloudStatus, executeIntelligentTryon } from './services/api';
import { SAMPLE_PERSONS, SAMPLE_GARMENTS } from './presets';
import { triggerCelebration } from './services/confetti';
import { AlertCircle, X, Layers, ArrowLeft, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const CURATED_LOOKS = [
  {
    id: 'look-mint',
    title: 'Mint Riviera Shirt',
    tag: 'Casual Micro-Print',
    person: SAMPLE_PERSONS[0],
    garment: SAMPLE_GARMENTS[0],
    category: 'shirt',
    thumb: '/studio/assets/sample_emerald_shirt.jpg',
  },
  {
    id: 'look-anarkali',
    title: 'Royal Emerald Anarkali',
    tag: 'Haute Ethnic Silk',
    person: SAMPLE_PERSONS[3],
    garment: SAMPLE_GARMENTS[3],
    category: 'western_dress',
    thumb: '/studio/assets/sample_anarkali_dress.jpg',
  },
  {
    id: 'look-blazer',
    title: 'Milano Navy Blazer',
    tag: 'Bespoke Tailoring',
    person: SAMPLE_PERSONS[1],
    garment: SAMPLE_GARMENTS[1],
    category: 'blazer',
    thumb: '/studio/assets/sample_navy_blazer.jpg',
  },
  {
    id: 'look-denim',
    title: 'Vintage Trucker Denim',
    tag: 'Streetwear Icon',
    person: SAMPLE_PERSONS[2],
    garment: SAMPLE_GARMENTS[4],
    category: 'shirt',
    thumb: '/studio/assets/sample_denim_jacket.jpg',
  },
  {
    id: 'look-black-tee',
    title: 'Obsidian Minimalist Tee',
    tag: 'Modern Classic',
    person: SAMPLE_PERSONS[4],
    garment: SAMPLE_GARMENTS[2],
    category: 't_shirt',
    thumb: '/studio/assets/sample_black_tshirt.jpg',
  },
];

export const App: React.FC = () => {
  // Cloud & Gateway Status
  const [cloudStatus, setCloudStatus] = useState<CloudStatus>({
    status: 'online',
    model: 'Atelier-Engine v2.4',
    provider: 'Nutz Atelier Cloud',
    has_key: true,
  });

  // Input states preloaded with default studio portrait & outfit
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

  // Generation execution state
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>('ready');
  const [currentStage, setCurrentStage] = useState<number>(1);
  const [result, setResult] = useState<TryonResult | null>(null);
  const [elapsedSec, setElapsedSec] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);
  const isGeneratingRef = useRef<boolean>(false);

  // Full-screen zoom modal
  const [isZoomOpen, setIsZoomOpen] = useState<boolean>(false);

  // History state
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Workspace ref
  const workspaceRef = useRef<HTMLDivElement>(null);

  // Current view page: 'home' (front page) vs 'studio' (fitting room + craft + standards) vs 'history'
  const [currentPage, setCurrentPage] = useState<'home' | 'studio' | 'history'>('home');

  // Synchronize URL hash with current view
  useEffect(() => {
    const syncHash = () => {
      const hash = window.location.hash;
      if (
        hash === '#studio' ||
        hash === '#tryon-workspace' ||
        hash === '#curated-wardrobe' ||
        hash === '#how-it-works' ||
        hash === '#features'
      ) {
        setCurrentPage('studio');
      } else if (hash === '#history' || hash === '#gallery') {
        setCurrentPage('history');
      } else {
        setCurrentPage('home');
      }
    };
    syncHash();
    window.addEventListener('hashchange', syncHash);
    return () => window.removeEventListener('hashchange', syncHash);
  }, []);

  const handleNavigate = (page: 'home' | 'studio' | 'history', sectionId?: string) => {
    setCurrentPage(page);
    if (page === 'home') {
      window.location.hash = '';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (page === 'studio') {
      window.location.hash = sectionId ? `#${sectionId}` : '#studio';
      if (sectionId) {
        setTimeout(() => {
          const el = document.getElementById(sectionId);
          if (el) el.scrollIntoView({ behavior: 'smooth' });
        }, 80);
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } else if (page === 'history') {
      window.location.hash = '#history';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Initial cloud health check
  useEffect(() => {
    let isMounted = true;
    const fetchStatus = async () => {
      const status = await getCloudStatus();
      if (isMounted) setCloudStatus(status);
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
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
      }, 100);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [generationStatus]);

  // Stage progress simulator
  useEffect(() => {
    if (generationStatus === 'processing') {
      const stageTimer1 = setTimeout(() => setCurrentStage(2), 2500);
      const stageTimer2 = setTimeout(() => setCurrentStage(3), 5500);
      const stageTimer3 = setTimeout(() => setCurrentStage(4), 9500);
      const stageTimer4 = setTimeout(() => setCurrentStage(5), 14000);
      return () => {
        clearTimeout(stageTimer1);
        clearTimeout(stageTimer2);
        clearTimeout(stageTimer3);
        clearTimeout(stageTimer4);
      };
    } else if (generationStatus === 'ready') {
      setCurrentStage(1);
    }
  }, [generationStatus]);

  const canGenerate = Boolean(person.previewUrl && garment.previewUrl);

  const handleApplyCuratedLook = (look: typeof CURATED_LOOKS[0]) => {
    if (generationStatus === 'processing') return;
    setPerson({
      file: null,
      previewUrl: look.person.imageUrl,
      name: look.person.name,
      isCustom: false,
      resolution: 'Studio Portrait HD',
    });
    setGarment({
      file: null,
      previewUrl: look.garment.imageUrl,
      name: look.garment.name,
      isCustom: false,
      resolution: 'Catalog HD',
    });
    setSelectedCategory(look.category);
  };

  const handleGenerate = async () => {
    if (!canGenerate || isGeneratingRef.current || generationStatus === 'processing' || generationStatus === 'uploading') return;

    isGeneratingRef.current = true;
    setGenerationStatus('processing');
    setCurrentStage(1);
    setElapsedSec(0);
    setErrorMessage(null);

    try {
      const res = await executeIntelligentTryon({
        personImage: person.file || person.previewUrl!,
        garmentImage: garment.file || garment.previewUrl!,
        category: selectedCategory,
        mode: 'auto',
        seed: Math.floor(Math.random() * 900000) + 100000,
      });

      setResult(res);
      setGenerationStatus('completed');

      // Trigger high-end celebration particle burst
      triggerCelebration();

      // Add to gallery history
      if (res.image_data || res.result_url) {
        const newItem: HistoryItem = {
          id: `look_${Date.now()}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          personThumb: person.previewUrl || '',
          garmentThumb: garment.previewUrl || '',
          personName: person.name || 'Studio Portrait',
          garmentName: garment.name || 'Outfit Reference',
          category: selectedCategory,
          resultUrl: res.image_data || res.result_url!,
          latencySec: res.latency_seconds || 16.8,
          model: res.model_used || 'Atelier-Engine v2.4',
          width: res.width || 1024,
          height: res.height || 1024,
          fileSizeStr: '1.84 MB',
          status: 'completed',
        };
        setHistory((prev) => [newItem, ...prev.slice(0, 19)]);
      }
    } catch (err: any) {
      console.error('[Nutz Replacer Generation Error]:', err);
      setGenerationStatus('failed');
      const raw = String(err?.message || '');
      if (/quota|429|insufficient_quota/i.test(raw)) {
        setErrorMessage('Generation quota reached. Please contact admin.');
      } else if (/contact admin/i.test(raw)) {
        setErrorMessage(raw);
      } else if (raw.includes('{') || raw.includes('error:') || raw.includes('failed:')) {
        setErrorMessage('Generation could not be completed. Please contact admin.');
      } else {
        setErrorMessage(raw || 'Generation failed. Please contact admin or retry.');
      }
    } finally {
      isGeneratingRef.current = false;
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
    handleNavigate('studio', 'tryon-workspace');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F4F8] text-[#171717] font-sans antialiased selection:bg-[#EAE8F2] selection:text-[#171717]">
      {/* 1. Global Navigation Bar */}
      <Navbar
        cloudStatus={cloudStatus}
        historyCount={history.length}
        currentPage={currentPage}
        onNavigate={handleNavigate}
        onOpenHistory={() => handleNavigate('history')}
      />

      {/* PAGE 1: Front Page Landing (Hero + Marquee + Footer only) */}
      {currentPage === 'home' && (
        <main className="flex-1 flex flex-col justify-between animate-fadeIn">
          <div>
            <HeroSection
              onEnterStudio={() => handleNavigate('studio', 'tryon-workspace')}
              onExploreWardrobe={() => handleNavigate('studio', 'curated-wardrobe')}
            />

            {/* Sera UI Infinite Fashion Craft Marquee */}
            <LuxuryMarquee />
          </div>

          {/* Centered Brand Editorial Footer */}
          <Footer onNavigate={handleNavigate} />
        </main>
      )}

      {/* PAGE 2: Fitting Studio Workspace (The Fitting Room, Process, Standards, LookHistory) */}
      {currentPage === 'studio' && (
        <main className="flex-1 animate-fadeIn">
          {/* Top Breadcrumb Navigation */}
          <div className="bg-[#FAF9F6] border-b border-[#EAE7E0] py-3.5 px-4 sm:px-8">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <button
                type="button"
                onClick={() => handleNavigate('home')}
                className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-[#171717] transition-colors cursor-pointer group"
              >
                <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
                <span>Back to Overview</span>
              </button>
              <div className="flex items-center gap-2 text-[11px] font-semibold text-slate-400">
                <button
                  type="button"
                  onClick={() => handleNavigate('home')}
                  className="hover:text-[#171717] transition-colors cursor-pointer"
                >
                  Front Page
                </button>
                <span>/</span>
                <span className="text-[#171717] font-bold">Fitting Studio</span>
              </div>
            </div>
          </div>

          {/* 3. Virtual Try-On Studio Workspace */}
          <section id="tryon-workspace" className="py-16 scroll-mt-20">
            <div ref={workspaceRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {/* Workspace Header & Curated Quick Looks */}
              <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-10">
                <div>
                  <h2 className="text-3xl sm:text-5xl font-serif text-[#171717] tracking-tight">
                    The Fitting Room
                  </h2>
                  <p className="text-sm text-slate-500 mt-2 max-w-xl font-normal">
                    Select a model portrait on the left and choose an outfit to preview how luxury tailoring and fabric weave drape onto your posture.
                  </p>
                </div>

                {/* Curated Showcase Wardrobe Rack */}
                <div id="curated-wardrobe" className="p-3.5 rounded-3xl bg-white border border-[#E8E8EF] shadow-card">
                  <div className="flex items-center gap-2 mb-2 text-xs font-bold text-[#171717]">
                    <Layers className="w-3.5 h-3.5 text-slate-700" />
                    <span>Curated Wardrobe:</span>
                  </div>
                  <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
                    {CURATED_LOOKS.map((look) => (
                      <motion.button
                        key={look.id}
                        type="button"
                        whileHover={{ y: -2, scale: 1.03 }}
                        whileTap={{ scale: 0.96 }}
                        onClick={() => handleApplyCuratedLook(look)}
                        disabled={generationStatus === 'processing'}
                        className="group flex-shrink-0 flex items-center gap-2.5 p-1.5 pr-3.5 rounded-2xl border border-[#E8E8EF] hover:border-[#171717] bg-[#F9F9FC] hover:bg-white transition-colors duration-200 cursor-pointer shadow-sm"
                      >
                        <img
                          src={look.thumb}
                          alt={look.title}
                          className="w-8 h-8 rounded-xl object-cover group-hover:scale-105 transition-transform"
                        />
                        <div className="text-left">
                          <span className="block text-[11px] font-bold text-[#171717] leading-tight">
                            {look.title}
                          </span>
                          <span className="block text-[9px] text-slate-400 font-medium">
                            {look.tag}
                          </span>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </div>
              </div>

              {errorMessage && (
                <div className="mb-6 p-4 rounded-2xl bg-amber-50/95 border border-amber-200/90 text-amber-900 text-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-sm animate-fadeIn">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0 text-amber-700">
                      <AlertCircle className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900">{errorMessage}</div>
                      {/contact admin|quota/i.test(errorMessage) && (
                        <div className="text-xs text-slate-500 mt-0.5">
                          The cloud generation quota has been exhausted. Please contact system admin for quota renewal.
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 self-end sm:self-center">
                    {/contact admin|quota/i.test(errorMessage) && (
                      <a
                        href="mailto:admin@nutz.ai?subject=Virtual%20Try-On%20Image%20Quota%20Request"
                        className="px-3.5 py-1.5 rounded-xl bg-[#171717] hover:bg-[#2B2B38] text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer whitespace-nowrap"
                      >
                        <span>Contact Admin</span>
                      </a>
                    )}
                    <button
                      type="button"
                      onClick={() => setErrorMessage(null)}
                      aria-label="Dismiss error notification"
                      className="text-slate-400 hover:text-slate-700 transition p-1.5 rounded-lg cursor-pointer"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              {/* Main Studio Canvas Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Column: Inputs */}
                <div className="lg:col-span-6 space-y-4">
                  <div>
                    <PersonUploadCard
                      person={person}
                      setPerson={setPerson}
                      disabled={generationStatus === 'processing'}
                      onError={setErrorMessage}
                    />
                  </div>

                  <div>
                    <TryonBridge
                      hasPerson={Boolean(person.previewUrl)}
                      hasGarment={Boolean(garment.previewUrl)}
                    />
                  </div>

                  <div>
                    <GarmentUploadCard
                      garment={garment}
                      setGarment={setGarment}
                      selectedCategory={selectedCategory}
                      setSelectedCategory={setSelectedCategory}
                      disabled={generationStatus === 'processing'}
                      onError={setErrorMessage}
                    />
                  </div>
                </div>

                {/* Right Column: Mirror Canvas */}
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
                    errorMessage={errorMessage}
                  />
                </div>
              </div>
            </div>
          </section>

          {/* 4. Craft & Fit Process Section */}
          <HowItWorksSection />

          {/* 5. Production Standards Section */}
          <FeatureSection />

          {/* 6. Recent Lookbook Gallery */}
          <GenerationHistory
            history={history}
            onSelectResult={handleSelectHistoryLook}
            onClearHistory={() => setHistory([])}
          />

          {/* Footer */}
          <Footer onNavigate={handleNavigate} />
        </main>
      )}

      {/* PAGE 3: LookHistory Dedicated View */}
      {currentPage === 'history' && (
        <main className="flex-1 animate-fadeIn py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6 flex items-center justify-between">
            <button
              type="button"
              onClick={() => handleNavigate('home')}
              className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-[#171717] transition-colors cursor-pointer group"
            >
              <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-1 transition-transform" />
              <span>Back to Overview</span>
            </button>
            <button
              type="button"
              onClick={() => handleNavigate('studio')}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-[#171717] hover:bg-[#2B2B38] text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
            >
              <span>Open Fitting Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Generation History Gallery */}
          <GenerationHistory
            history={history}
            onSelectResult={handleSelectHistoryLook}
            onClearHistory={() => setHistory([])}
          />

          <Footer onNavigate={handleNavigate} />
        </main>
      )}

      {/* Full-Screen HD Zoom Modal */}
      <ImageModal
        isOpen={isZoomOpen}
        onClose={() => setIsZoomOpen(false)}
        imageUrl={result?.image_data || result?.result_url || ''}
        title="High-Definition Garment Drape & Fitting Preview"
        resolution="High-Resolution HD"
        fileSizeStr="1.84 MB"
      />
    </div>
  );
};

export default App;
