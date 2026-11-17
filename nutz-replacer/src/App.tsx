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
import { 
  CloudStatus, GenerationStatus, ImageInputState, TryonResult, HistoryItem 
} from './types';
import { getCloudStatus, executeIntelligentTryon } from './services/api';
import { SAMPLE_PERSONS, SAMPLE_GARMENTS } from './presets';
import { triggerCelebration } from './services/confetti';
import { AlertCircle, X, Layers } from 'lucide-react';
import gsap from 'gsap';

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

  // Full-screen zoom modal
  const [isZoomOpen, setIsZoomOpen] = useState<boolean>(false);

  // History state
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Workspace ref for GSAP entrance
  const workspaceRef = useRef<HTMLDivElement>(null);

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

  // GSAP animation on workspace mount
  useEffect(() => {
    if (workspaceRef.current) {
      gsap.from(workspaceRef.current.querySelectorAll('.studio-card'), {
        y: 30,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: 'power3.out',
        delay: 0.2,
      });
    }
  }, []);

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
    if (!canGenerate || generationStatus === 'processing') return;

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
      setErrorMessage(
        err.message || 'Generation failed. Please try another combination or retry.'
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

  return (
    <div className="min-h-screen bg-[#F5F4F8] text-[#171717] font-sans antialiased selection:bg-[#EAE8F2] selection:text-[#171717]">
      {/* 1. Global Navigation Bar */}
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
                  <button
                    key={look.id}
                    type="button"
                    onClick={() => handleApplyCuratedLook(look)}
                    disabled={generationStatus === 'processing'}
                    className="group flex-shrink-0 flex items-center gap-2.5 p-1.5 pr-3.5 rounded-2xl border border-[#E8E8EF] hover:border-[#171717] bg-[#F9F9FC] hover:bg-white transition-all duration-300 cursor-pointer active:scale-95 shadow-sm"
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
                  </button>
                ))}
              </div>
            </div>
          </div>

          {errorMessage && (
            <div className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center justify-between shadow-sm animate-fadeIn">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-[#DC2626] flex-shrink-0" />
                <span className="font-semibold">{errorMessage}</span>
              </div>
              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                aria-label="Dismiss error notification"
                className="text-red-500 hover:text-red-800 transition p-1 rounded-lg cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Main Studio Canvas Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Column: Inputs */}
            <div className="lg:col-span-6 space-y-4">
              <div className="studio-card">
                <PersonUploadCard
                  person={person}
                  setPerson={setPerson}
                  disabled={generationStatus === 'processing'}
                  onError={setErrorMessage}
                />
              </div>

              <div className="studio-card">
                <TryonBridge
                  hasPerson={Boolean(person.previewUrl)}
                  hasGarment={Boolean(garment.previewUrl)}
                />
              </div>

              <div className="studio-card">
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
            <div className="lg:col-span-6 sticky top-28 studio-card">
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

      {/* 7. Footer */}
      <Footer />

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
